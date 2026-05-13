"""Adapter for motor_019 — LLM Writing Engine.

Uses Codex CLI to write bounded professional prose for the
governed asset brief produced by the framework. All output is strictly
conditioned on the analytical objects produced by upstream motors —
no external knowledge injected.

Context sources (all from pipeline):
  motor_014 — inference_records, conflict_register, tension_records,
               opportunity_candidates, validation_queue, next_best_questions
  motor_012 — facility_prior (system_asset_hypotheses, regulatory_flag_bundle,
               benchmark_bundle, operational_tension_hypotheses)
  motor_028 — enriched_data.financials (SEC EDGAR live data)
  __pipeline__ — facility_inputs (raw inputs as declared by the operator)

Epistemic law: The LLM is a professional writer, not an analyst. It may
reformulate, clarify, and explain — it may NOT introduce new claims, facts,
or conclusions beyond what the context objects contain.

Frame law: This is an operational assessment, not a transaction assessment.
The organizing axis is what the building IS and what it CANNOT DO YET.
Financial data is subordinated context. The LLM must never frame
analysis as due diligence, underwriting, or acquisition assessment.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
import urllib.error
from hashlib import sha256
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..narrator_validator import check_orphan_claims, summarize_orphan_findings
from .base import BaseMotorAdapter

_CODEX_CLI = os.environ.get("ZLAB_CODEX_CLI", "codex")
_MODEL      = os.environ.get("ZLAB_CODEX_MODEL", "").strip()
_TIMEOUT    = 180
_SECTION_TIMEOUT = int(os.environ.get("ZLAB_LLM_SECTION_TIMEOUT_SECONDS", "45"))
_TOTAL_WRITE_BUDGET_SECONDS = int(
    os.environ.get("ZLAB_LLM_WRITING_BUDGET_SECONDS", "240")
)
_MAX_TOKENS = 700
_LLM_SECTION_ALLOWLIST = {
    "s01_exec_narrative",
    "s02_blocking_conflict",
    "s04_validation_narrative",
    "s06_tensions_narrative",
    "s09_systems_energy_narrative",
    "s08_opportunities_narrative",
}
_CODEX_WORKDIR = Path(__file__).resolve().parents[3]
_CODEX_REASONING_EFFORT = os.environ.get("ZLAB_CODEX_REASONING_EFFORT", "low").strip()

_SYSTEM = (
    "You are a controlled report writer for the ZLab framework. "
    "You are not an analyst and you are not a decision authority. "
    "You only translate structured upstream objects into clear prose.\n"
    "STRICT RULES — follow without exception:\n"
    "1. Use ONLY the section_packet provided. If a fact, number, or claim is not in the packet, do not mention it.\n"
    "2. Write in simple but strong language. Short paragraphs. One idea per paragraph. No academic tone. No hype.\n"
    "3. The report is operational and epistemic. It is never acquisition, underwriting, due diligence, or investment advice.\n"
    "4. Epistemic proportionality is mandatory. Use language such as 'suggests', 'is compatible with', "
    "'warrants validation', 'cannot yet be confirmed', 'remains bounded'.\n"
    "5. Never invent new claims, new numbers, new entities, or new conclusions.\n"
    "6. Do not close uncertainty. Do not imply verification-grade certainty from decision-grade inputs.\n"
    "7. If the packet references a chart, write so the prose helps the reader understand what the chart clarifies.\n"
    "8. Always preserve semantic equivalence between English and Spanish. Spanish should not add or remove claims.\n"
    "9. Never write meta-instructions such as 'the chart should', 'the prose should', or 'use in text'. "
    "Write directly about the evidence, uncertainty, and decision consequence.\n"
)

_FORBIDDEN_PHRASES = (
    "acquisition",
    "underwriting",
    "due diligence",
    "institutional buyer",
    "purchase",
    "buy",
    "deal",
    "going concern valuation",
    "fully compliant",
    "verified diagnosis",
)
_HARD_CLOSURE_PHRASES = (
    "proves",
    "confirms",
    "guarantees",
    "demonstrates definitively",
    "without doubt",
    "is compliant",
    "will save",
    "will deliver",
)
_INSTRUCTION_LEAKAGE_PHRASES = (
    "the chart should",
    "the prose should",
    "use in text",
)
_COMMON_SAFE_NUMBERS = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}
_NUMERIC_TOKEN_RE = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")

_BUILDING_TYPES = {
    "commercial_building",
    "multifamily_building",
    "hospital",
    "hotel",
    "data_center",
    "campus",
}
_LOGISTICS_TYPES = {"warehouse_distribution"}
_MANUFACTURING_TYPES = {
    "industrial_plant",
    "manufacturing_facility",
    "food_processing_facility",
    "cold_chain_facility",
}
_INFRASTRUCTURE_TYPES = {"infrastructure_node"}
_OIL_GAS_TYPES = {
    "oil_gas_upstream_site",
    "oil_gas_midstream_facility",
    "oil_gas_downstream_facility",
}


def _call_codex(prompt: str, ctx: dict, timeout: int = _SECTION_TIMEOUT) -> tuple[str | None, str | None]:
    ctx_str = json.dumps(ctx, ensure_ascii=False, default=str)
    full = f"{_SYSTEM}\n\nCONTEXT:\n{ctx_str}\n\nTASK:\n{prompt}"
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="zlab-codex-", suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name
        cmd = [
            _CODEX_CLI,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--output-last-message",
            tmp_path,
            "--color",
            "never",
            "-C",
            str(_CODEX_WORKDIR),
            "-",
        ]
        if _MODEL:
            cmd[6:6] = ["--model", _MODEL]
        if _CODEX_REASONING_EFFORT:
            cmd[6:6] = ["-c", f"model_reasoning_effort={_CODEX_REASONING_EFFORT}"]
        proc = subprocess.run(
            cmd,
            input=full,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=str(_CODEX_WORKDIR),
        )
        text = ""
        if tmp_path and Path(tmp_path).exists():
            text = Path(tmp_path).read_text(encoding="utf-8", errors="replace").strip()
        if proc.returncode != 0 and not text:
            detail = (proc.stderr or proc.stdout or "").strip()
            detail = " ".join(detail.split())[:240]
            return None, f"codex_exit:{proc.returncode}:{detail}" if detail else f"codex_exit:{proc.returncode}"
        return (text if text else None), None
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception as exc:
        return None, exc.__class__.__name__
    finally:
        if tmp_path:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass


def _fmt(v) -> str:
    if v is None:
        return "N/A"
    if isinstance(v, (int, float)):
        if abs(v) >= 1e9:
            return f"${v/1e9:.2f}B"
        if abs(v) >= 1e6:
            return f"${v/1e6:.1f}M"
        return f"{v:.4f}"
    return str(v)


def _codex_up() -> bool:
    return shutil.which(_CODEX_CLI) is not None


def _shorten(value: Any, limit: int = 180) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str) if isinstance(value, (dict, list)) else str(value)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _context_snapshot(ctx: dict[str, Any], limit: int = 8) -> list[dict[str, str]]:
    snapshot: list[dict[str, str]] = []
    for key, value in ctx.items():
        if value in ("", None, [], {}):
            continue
        snapshot.append({
            "label": key.replace("_", " ").title(),
            "value": _shorten(value),
        })
        if len(snapshot) >= limit:
            break
    return snapshot


def _claim_permission_snapshot(
    register: list[dict[str, Any]],
    names: list[str],
    *,
    limit: int = 6,
) -> list[dict[str, Any]]:
    wanted = set(names)
    rows: list[dict[str, Any]] = []
    for row in register:
        claim_name = str(row.get("claim_name", "")).strip()
        if claim_name not in wanted:
            continue
        rows.append({
            "claim_name": claim_name,
            "current_permission": row.get("current_permission", ""),
            "reason_if_blocked": row.get("reason_if_blocked", ""),
            "upgrade_path": (row.get("upgrade_path", []) or [])[:4],
        })
        if len(rows) >= limit:
            break
    return rows


def _decision_permission_snapshot(
    register: list[dict[str, Any]],
    names: list[str],
    *,
    limit: int = 6,
) -> list[dict[str, Any]]:
    wanted = set(names)
    rows: list[dict[str, Any]] = []
    for row in register:
        decision_name = str(row.get("decision_name", "")).strip()
        if decision_name not in wanted:
            continue
        rows.append({
            "decision_name": decision_name,
            "admissibility_state": row.get("admissibility_state", ""),
            "current_variable_bottleneck": row.get("current_variable_bottleneck", ""),
            "allowed_action": row.get("allowed_action", ""),
            "evidence_needed": (row.get("evidence_needed", []) or [])[:4],
        })
        if len(rows) >= limit:
            break
    return rows


def _variable_maturity_snapshot(
    register: list[dict[str, Any]],
    names: list[str],
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    wanted = set(names)
    rows: list[dict[str, Any]] = []
    for row in register:
        variable_name = str(row.get("variable_name", "")).strip()
        if variable_name not in wanted:
            continue
        rows.append({
            "variable_name": variable_name,
            "maturity_level": row.get("maturity_level", ""),
            "source_scope": row.get("source_scope", ""),
            "authority_score": row.get("authority_score", ""),
            "uncertainty_reason": row.get("uncertainty_reason", ""),
        })
        if len(rows) >= limit:
            break
    return rows


def _blocked_claim_names(register: list[dict[str, Any]], *, limit: int = 8) -> list[str]:
    names: list[str] = []
    for row in register:
        if str(row.get("current_permission", "")).strip() != "prohibited":
            continue
        claim_name = str(row.get("claim_name", "")).strip()
        if claim_name:
            names.append(claim_name)
        if len(names) >= limit:
            break
    return names


def _section_contract(section_id: str) -> dict[str, Any]:
    defaults = {
        "allowed_claim_classes": ["explanation", "bounded synthesis", "validation framing"],
        "forbidden_claims": [
            "new quantitative claims",
            "compliance closure",
            "bankability closure",
            "verified diagnosis",
        ],
        "chart_role": "Use the chart to reduce reading burden and surface the core analytical point quickly.",
    }
    overrides = {
        "s01_exec_narrative": {
            "allowed_claim_classes": ["decision state summary", "blocking condition summary", "validation ordering"],
            "chart_role": "Use the visuals to show the reader what matters first in the report.",
        },
        "s03_financial_narrative": {
            "allowed_claim_classes": ["bounded financial context", "readiness posture", "scope limitation"],
            "forbidden_claims": defaults["forbidden_claims"] + ["asset-level ROI", "payback", "IRR", "NPV", "DSCR"],
            "chart_role": "Use the visual to clarify scale and ambiguity, not to imply bankability.",
        },
        "s09_systems_energy_narrative": {
            "allowed_claim_classes": ["systems explanation", "normative exposure explanation", "validation need"],
            "chart_role": "Use the visual to make compliance posture or energy exposure easier to read.",
        },
        "s04_validation_narrative": {
            "allowed_claim_classes": ["validation ordering", "information value framing"],
            "chart_role": "Use the visual to clarify sequencing and urgency.",
        },
        "s06_tensions_narrative": {
            "allowed_claim_classes": ["tension explanation", "operational consequence", "uncertainty framing"],
            "chart_role": "Use the visual to clarify concentration or tension structure, not to decorate the section.",
        },
    }
    merged = dict(defaults)
    merged.update(overrides.get(section_id, {}))
    return merged


def _target_family(target_type: str) -> str:
    target_type = (target_type or "").strip().lower()
    if target_type in _LOGISTICS_TYPES:
        return "logistics"
    if target_type in _MANUFACTURING_TYPES:
        return "manufacturing"
    if target_type in _INFRASTRUCTURE_TYPES:
        return "infrastructure"
    if target_type in _OIL_GAS_TYPES:
        return "oil_gas"
    return "building"


def _operational_identity_instruction(target_type: str) -> str:
    family = _target_family(target_type)
    if family == "logistics":
        return (
            "Use logistics vocabulary: dock operations, throughput windows, occupancy zones, refrigeration if present, "
            "and control boundaries. Do not describe the asset as a generic office building."
        )
    if family == "manufacturing":
        return (
            "Use plant vocabulary: process lines, thermal duty, refrigeration, compressed air, sanitation or maintenance cycles, "
            "and operator control boundaries. Do not describe the asset as a tenant-led building."
        )
    if family == "infrastructure":
        return (
            "Use network and reliability vocabulary: topology, duty, conversion equipment, redundancy, service boundary, "
            "and outage tolerance. Do not describe the asset as a multi-tenant building."
        )
    if family == "oil_gas":
        return (
            "Use process-duty vocabulary: throughput, compression, pumping, fired systems, steam, flare or vent basis, "
            "and operating-unit boundaries. Do not describe the asset as a generic building."
        )
    return (
        "Use building systems vocabulary: use mix, occupancy, HVAC, controls, and tenant or owner control boundary."
    )


def _systems_normative_instruction(target_type: str) -> str:
    family = _target_family(target_type)
    if family == "logistics":
        return (
            "Frame the systems boundary around dock operations, refrigeration if present, lighting, controls, and occupancy / throughput dependence. "
            "Explain whether local benchmarking or compliance exposure remains only screening-grade."
        )
    if family == "manufacturing":
        return (
            "Frame the systems boundary around process lines, motors, compressed air, refrigeration, thermal duty, sanitation, and controls. "
            "Explain what remains archetypal versus confirmed, and how permit or emissions posture stays screening-grade."
        )
    if family == "infrastructure":
        return (
            "Frame the systems boundary around topology, conversion equipment, controls, redundancy, and service duty. "
            "Explain what remains archetypal versus confirmed, and how environmental or reporting posture stays screening-grade."
        )
    if family == "oil_gas":
        return (
            "Frame the systems boundary around process units, rotating equipment, steam, flare, compression or pumping, and operating duty. "
            "Explain what remains archetypal versus confirmed, and how permit, emissions, or transition posture stays screening-grade."
        )
    return (
        "Frame the systems boundary around building systems, benchmark context, and bounded regulatory exposure."
    )


def _build_section_packet(
    *,
    section_id: str,
    title: str,
    audience: str,
    prompt: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    contract = _section_contract(section_id)
    packet_key = f"{section_id}:{json.dumps(ctx, sort_keys=True, default=str)}"
    return {
        "packet_id": "sp:" + sha256(packet_key.encode()).hexdigest()[:10],
        "section_id": section_id,
        "title": title,
        "audience": audience,
        "writing_task": prompt,
        "style_contract": {
            "tone": "executive_technical",
            "language": "simple_but_strong",
            "max_words": 110,
            "paragraph_style": "short",
            "output_languages": ["en", "es"],
        },
        "allowed_claim_classes": contract["allowed_claim_classes"],
        "forbidden_claims": contract["forbidden_claims"],
        "chart_role": contract["chart_role"],
        "context_snapshot": _context_snapshot(ctx),
        "source_facts": ctx,
    }


def _normalized_numeric_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for match in _NUMERIC_TOKEN_RE.findall(text or ""):
        token = str(match).replace(",", "").strip()
        if token:
            tokens.add(token)
    return tokens


def _lint_text(packet: dict[str, Any], text: str) -> dict[str, Any]:
    violations: list[str] = []
    lowered = text.lower()
    allowed_context_text = json.dumps(packet.get("source_facts", {}), ensure_ascii=False, default=str).lower()
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in lowered and phrase not in allowed_context_text:
            violations.append(f"forbidden_phrase:{phrase}")
    for phrase in _HARD_CLOSURE_PHRASES:
        if phrase in lowered:
            violations.append(f"closure_phrase:{phrase}")
    for phrase in _INSTRUCTION_LEAKAGE_PHRASES:
        if phrase in lowered:
            violations.append(f"instruction_leakage:{phrase}")
    if len(text.split()) > packet.get("style_contract", {}).get("max_words", 260):
        violations.append("too_verbose")
    allowed_tokens = _normalized_numeric_tokens(json.dumps(packet.get("source_facts", {}), ensure_ascii=False, default=str))
    rendered_tokens = _normalized_numeric_tokens(text)
    unsupported_tokens = sorted(
        token for token in rendered_tokens
        if token not in allowed_tokens and token not in _COMMON_SAFE_NUMBERS
    )
    if unsupported_tokens:
        violations.append("unsupported_numeric_tokens:" + ",".join(unsupported_tokens[:6]))

    # V5 P7: orphan-claim detection. Each sentence whose significant
    # tokens share NO overlap with source_facts is flagged as a candidate
    # hallucination. This is the Phase 0 "the LLM doesn't invent"
    # enforcement at sentence granularity.
    orphan_findings = check_orphan_claims(
        packet.get("source_facts", {}),
        text,
        allow_list=[
            str(packet.get("target_type", "")),
            str(packet.get("asset_family", "")),
            str(packet.get("case_id", "")),
        ],
    )
    if orphan_findings:
        summary = summarize_orphan_findings(orphan_findings)
        if summary:
            violations.append(summary)
    return {
        "status": "failed" if violations else "passed",
        "violations": violations,
        # Surface the structured findings so downstream audit (motor_017
        # render gate, dashboard) can inspect each orphan in detail.
        "orphan_claim_findings": orphan_findings,
    }


def _trim_to_word_limit(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text.strip()
    clipped = " ".join(words[:limit]).strip()
    sentence_end = max(clipped.rfind(". "), clipped.rfind("! "), clipped.rfind("? "))
    if sentence_end > int(limit * 0.45):
        return clipped[: sentence_end + 1].strip()
    return clipped.rstrip(" ,;:") + "."


def _title_es(title: str) -> str:
    translations = {
        "Framework Context & Executive Brief": "Contexto del Framework y Resumen Ejecutivo",
        "Blocking Conflict": "Conflicto Bloqueante",
        "Validation Architecture": "Arquitectura de Validación",
        "Financial Context": "Contexto Financiero",
        "Tension Map": "Mapa de Tensiones",
        "Operational Identity": "Identidad Operacional",
        "Conditional Decision Space": "Espacio de Decisión Condicional",
        "Priority Questions": "Preguntas Prioritarias",
    }
    return translations.get(title, title)


def _render_fallback(packet: dict[str, Any]) -> dict[str, str]:
    snapshot = packet.get("context_snapshot", [])
    facts = [f"{item.get('label')}: {item.get('value')}" for item in snapshot[:5]]
    title_en = packet.get("title", "Section")
    title_es = _title_es(title_en)
    intro_en = (
        f"{title_en}. "
        "This section remains bounded by the current evidence state and should be read as decision-grade only."
    )
    if facts:
        intro_en += " " + " ".join(facts[:2]) + "."
    follow_up_en = (
        "What matters now is validation, not closure. "
        + " ".join(facts[2:5])
        if len(facts) > 2
        else "What matters now is validation, not closure."
    )
    chart_note = packet.get("chart_role", "")
    if chart_note:
        follow_up_en += f" {chart_note}"
    intro_es = (
        f"{title_es}. "
        "Esta sección sigue acotada por el estado actual de evidencia y debe leerse solo como decision-grade."
    )
    if facts:
        intro_es += " " + " ".join(facts[:2]) + "."
    follow_up_es = (
        "Lo importante ahora es validar, no cerrar. " + " ".join(facts[2:5])
        if len(facts) > 2
        else "Lo importante ahora es validar, no cerrar."
    )
    if chart_note:
        follow_up_es += " Use el gráfico para aclarar el punto central, no para endurecer el claim."
    return {
        "en": intro_en.strip() + "\n\n" + follow_up_en.strip(),
        "es": intro_es.strip() + "\n\n" + follow_up_es.strip(),
    }


def _render_structured_summary(packet: dict[str, Any]) -> dict[str, str]:
    snapshot = packet.get("context_snapshot", [])
    title_en = packet.get("title", "Section")
    title_es = _title_es(title_en)
    lines_en = [
        f"{title_en}.",
        "This section is rendered as a structured summary because the report reserves LLM prose for the highest-value narrative sections.",
    ]
    lines_es = [
        f"{title_es}.",
        "Esta sección se presenta como resumen estructurado porque el reporte reserva la prosa LLM para las narrativas de mayor valor.",
    ]
    if snapshot:
        lines_en.append("Current support points:")
        lines_es.append("Puntos de soporte actuales:")
        for item in snapshot[:4]:
            line = f"- {item.get('label')}: {item.get('value')}"
            lines_en.append(line)
            lines_es.append(line)
    lines_en.append("Interpretation remains bounded by the current evidence state.")
    lines_es.append("La interpretación sigue acotada por el estado actual de evidencia.")
    return {
        "en": "\n".join(lines_en),
        "es": "\n".join(lines_es),
    }


def _extract_json_candidate(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned).strip()
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    return match.group(0).strip() if match else cleaned


def _parse_bilingual_response(text: str) -> tuple[dict[str, str] | None, str | None]:
    candidate = _extract_json_candidate(text)
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        return None, "invalid_json"
    if not isinstance(payload, dict):
        return None, "invalid_shape"
    en = payload.get("en") or payload.get("english")
    es = payload.get("es") or payload.get("spanish")
    if not isinstance(en, str) or not en.strip():
        return None, "missing_en"
    if not isinstance(es, str) or not es.strip():
        return None, "missing_es"
    return {"en": en.strip(), "es": es.strip()}, None


class Motor019Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_019"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_014", "motor_012", "motor_028", "motor_033", "motor_034", "motor_001"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m14      = inputs.get("motor_014", {})
        m12      = inputs.get("motor_012", {})
        m33      = inputs.get("motor_033", {})
        m28      = inputs.get("motor_028", {})
        m34      = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        m01      = inputs.get("motor_001", {})
        pipeline = inputs.get("__pipeline__", {})
        produced_at = datetime.now(timezone.utc).isoformat()
        writing_started_at_monotonic = time.monotonic()

        # ── motor_014: inference objects ──────────────────────────────────────
        inf_records  = m14.get("inference_records", [])
        conflict_reg = m14.get("conflict_register", [])
        tension_recs = m14.get("tension_records", [])
        opp_cands    = m14.get("opportunity_candidates", [])
        val_queue    = m14.get("validation_queue", [])
        nbq          = m14.get("next_best_questions", [])
        comp_reading = m14.get("composite_reading", {})
        decision_front_register = m14.get("decision_front_register", [])
        minimum_evidence_unlock_map = m14.get("minimum_evidence_unlock_map", [])
        scenario_space = m14.get("scenario_space", [])
        asset_context_readiness_summary = m14.get("asset_context_readiness_summary", {})
        information_deficit_score = m14.get("information_deficit_score")
        claim_permission_register = list(m14.get("claim_permission_register", m34.get("claim_permission_register", [])) or [])
        decision_permission_register = list(m14.get("decision_permission_register", m34.get("decision_permission_register", [])) or [])
        variable_maturity_register = list(m14.get("variable_maturity_register", m34.get("variable_maturity_register", [])) or [])
        claim_permission_summary = m14.get("claim_permission_summary", {}) if isinstance(m14.get("claim_permission_summary", {}), dict) else {}
        variable_bottleneck_register = list(m14.get("variable_bottleneck_register", []) or [])
        report_readiness_register = dict(m14.get("report_readiness_register", m34.get("report_readiness_register", {})) or {})
        maturity_summary = dict(m34.get("maturity_summary", {}) or {})

        # ── motor_012: facility_prior ─────────────────────────────────────────
        fp = m12.get("facility_prior", {})
        sys_hypotheses   = fp.get("system_asset_hypotheses", [])
        op_tensions      = fp.get("operational_tension_hypotheses", [])
        reg_flags        = fp.get("regulatory_flag_bundle", {})
        compliance_case  = fp.get("compliance_applicability_case", m12.get("compliance_applicability_case", {}))
        bench            = fp.get("benchmark_bundle", {})
        vintage          = fp.get("vintage", {})
        prior_assump     = fp.get("prior_assumptions_pack", [])
        uncertainty      = fp.get("uncertainty_markers", [])

        # ── motor_028: live SEC financial data + web search results ──────────
        enriched   = m28.get("enriched_data", {})
        financials = enriched.get("financials", {})
        company    = enriched.get("company_name", enriched.get("subject", {}).get("name", ""))
        ticker     = enriched.get("ticker", "")
        ext_sources = enriched.get("extended_sources", {})
        ws_ll97         = ext_sources.get("ws_ll97_compliance", {}) or {}
        ws_energy       = ext_sources.get("ws_energy_benchmarking", {}) or {}
        ws_occupancy    = ext_sources.get("ws_occupancy_leasing", {}) or {}
        ws_capex        = ext_sources.get("ws_capex_sustainability", {}) or {}
        ws_debt         = ext_sources.get("ws_debt_leverage", {}) or {}
        ws_tenants      = ext_sources.get("ws_anchor_tenant_news", {}) or {}

        # ── motor_033: TAD Preliminary (VoI-ordered validation plan) ─────────
        tad_prelim   = m33.get("tad_preliminary", {})
        tad_actions  = tad_prelim.get("tad_action_plan", [])
        tad_frontier = tad_prelim.get("decision_frontier", "")
        tad_deficit  = tad_prelim.get("information_deficit_score", None)
        tad_blocking = tad_prelim.get("blocking_resolution_paths", [])

        # ── pipeline inputs (raw operator declarations) ───────────────────────
        fi      = pipeline.get("facility_inputs", {})
        fac     = fi.get("input_02_facility_type", {})
        size    = fi.get("input_05_size", {})
        vintage_fi = fi.get("input_06_vintage", {})
        tenants = fi.get("input_04_primary_use", {})
        systems = fi.get("input_09_known_systems", {})
        concern = fi.get("input_10_main_concern", {})
        subject_definition = m01.get("subject_definition", {})
        target_definition = fp.get("target_definition", {}) if isinstance(fp.get("target_definition", {}), dict) else {}
        target_type = str(target_definition.get("target_type", "")).strip().lower()
        asset_context_readiness = fp.get("asset_context_readiness", "asset_context_insufficient")
        blocked_report_mode = (
            asset_context_readiness in {"issuer_context_only", "location_only", "asset_context_insufficient"}
            or information_deficit_score in {"HIGH", "CRITICAL"}
            or subject_definition.get("subject_kind") in {"issuer", "address_candidate", "site_candidate"}
        )
        operational_identity_instruction = _operational_identity_instruction(target_type)
        systems_normative_instruction = _systems_normative_instruction(target_type)
        blocked_claims = _blocked_claim_names(claim_permission_register)

        written: list[dict] = []
        errors:  list[dict] = []
        budget_exhausted = False
        skipped_sections_due_budget = 0
        section_packets: list[dict[str, Any]] = []
        lint_failures = 0
        fallback_sections = 0

        structured_summary_sections = 0

        if not _codex_up():
            return {
                "written_sections": [],
                "section_packets": [],
                "codex_available": False,
                "llm_errors": [{"error": "Codex CLI not reachable"}],
                "total_sections_written": 0,
                "llm_governance_summary": {
                    "sections_attempted": 0,
                    "sections_rendered": 0,
                    "lint_failures": 0,
                    "fallback_sections": 0,
                    "structured_summary_sections": 0,
                "budget_exhausted": False,
                "unresolved_breaches": 0,
            },
                "produced_at": produced_at,
                "model_used": _MODEL or "codex-cli-default",
            }

        def add(section_id: str, title: str, audience: str, prompt: str, ctx: dict):
            nonlocal budget_exhausted, skipped_sections_due_budget, lint_failures, fallback_sections, structured_summary_sections
            packet = _build_section_packet(
                section_id=section_id,
                title=title,
                audience=audience,
                prompt=prompt,
                ctx=ctx,
            )
            section_packets.append(packet)
            if section_id not in _LLM_SECTION_ALLOWLIST:
                structured_summary_sections += 1
                structured_text = _render_structured_summary(packet)
                written.append({
                    "section_id": section_id,
                    "title": title,
                    "audience": audience,
                    "text": structured_text["en"],
                    "text_en": structured_text["en"],
                    "text_es": structured_text["es"],
                    "context_sources": list(ctx.keys()),
                    "render_mode": "structured_summary",
                    "lint_status": "passed",
                    "lint_violations": [],
                    "section_packet": packet,
                })
                return
            elapsed_seconds = time.monotonic() - writing_started_at_monotonic
            if elapsed_seconds >= _TOTAL_WRITE_BUDGET_SECONDS:
                budget_exhausted = True
                skipped_sections_due_budget += 1
                fallback_sections += 1
                errors.append({
                    "section": section_id,
                    "error": "writing_budget_exhausted",
                    "detail": (
                        "Writing budget exhausted before this section could be generated "
                        f"({elapsed_seconds:.1f}s/{_TOTAL_WRITE_BUDGET_SECONDS}s)."
                    ),
                })
                fallback_text = _render_fallback(packet)
                lint_result = {"status": "passed", "violations": ["fallback_budget_exhausted"]}
                written.append({
                    "section_id": section_id,
                    "title": title,
                    "audience": audience,
                    "text": fallback_text["en"],
                    "text_en": fallback_text["en"],
                    "text_es": fallback_text["es"],
                    "context_sources": list(ctx.keys()),
                    "render_mode": "fallback",
                    "lint_status": lint_result["status"],
                    "lint_violations": lint_result["violations"],
                    "section_packet": packet,
                })
                return
            llm_prompt = (
                "Write the section defined by the section_packet. "
                "Obey its writing_task, allowed_claim_classes, forbidden_claims, and style_contract. "
                "Use only source_facts. If uncertainty remains, state it directly. "
                "Return strict JSON only with this exact schema: "
                "{\"en\":\"...\",\"es\":\"...\"}. "
                "Both values must carry the same meaning. "
                "Use two short paragraphs maximum per language."
            )
            text, llm_error = _call_codex(llm_prompt, {"section_packet": packet}, timeout=_SECTION_TIMEOUT)
            if text:
                bilingual_text, parse_error = _parse_bilingual_response(text)
                if parse_error:
                    fallback_sections += 1
                    errors.append({
                        "section": section_id,
                        "error": "llm_parse_failed",
                        "detail": parse_error,
                    })
                    fallback_text = _render_fallback(packet)
                    written.append({
                        "section_id": section_id,
                        "title": title,
                        "audience": audience,
                        "text": fallback_text["en"],
                        "text_en": fallback_text["en"],
                        "text_es": fallback_text["es"],
                        "context_sources": list(ctx.keys()),
                        "render_mode": "fallback_llm_parse_error",
                        "lint_status": "passed",
                        "lint_violations": [f"fallback:{parse_error}"],
                        "section_packet": packet,
                    })
                    return
                assert bilingual_text is not None
                text_en = _trim_to_word_limit(
                    bilingual_text["en"],
                    packet.get("style_contract", {}).get("max_words", 110),
                )
                text_es = _trim_to_word_limit(
                    bilingual_text["es"],
                    packet.get("style_contract", {}).get("max_words", 110),
                )
                lint_en = _lint_text(packet, text_en)
                lint_es = _lint_text(packet, text_es)
                lint_violations = [f"en:{v}" for v in lint_en["violations"]] + [
                    f"es:{v}" for v in lint_es["violations"]
                ]
                render_mode = "llm"
                final_text_en = text_en
                final_text_es = text_es
                if lint_en["status"] != "passed" or lint_es["status"] != "passed":
                    lint_failures += 1
                    fallback_sections += 1
                    render_mode = "fallback_after_lint"
                    fallback_text = _render_fallback(packet)
                    final_text_en = fallback_text["en"]
                    final_text_es = fallback_text["es"]
                    errors.append({
                        "section": section_id,
                        "error": "llm_lint_failed",
                        "detail": ",".join(lint_violations),
                    })
                written.append({
                    "section_id": section_id,
                    "title": title,
                    "audience": audience,
                    "text": final_text_en,
                    "text_en": final_text_en,
                    "text_es": final_text_es,
                    "context_sources": list(ctx.keys()),
                    "render_mode": render_mode,
                    "lint_status": "passed" if not lint_violations or render_mode == "llm" else "failed",
                    "lint_violations": lint_violations,
                    "section_packet": packet,
                })
            else:
                fallback_sections += 1
                errors.append({"section": section_id, "error": llm_error or "empty_response"})
                fallback_text = _render_fallback(packet)
                written.append({
                    "section_id": section_id,
                    "title": title,
                    "audience": audience,
                    "text": fallback_text["en"],
                    "text_en": fallback_text["en"],
                    "text_es": fallback_text["es"],
                    "context_sources": list(ctx.keys()),
                    "render_mode": "fallback_llm_unavailable",
                    "lint_status": "passed",
                    "lint_violations": [f"fallback:{llm_error or 'empty_response'}"],
                    "section_packet": packet,
                })

        # ── S0: Operational Identity (C2) ────────────────────────────────────
        if not blocked_report_mode:
            add(
                "s00_operational_identity",
                "Operational Identity",
                "technical",
                (
                    "Write a precise operational identity profile (2-3 paragraphs) for this asset. "
                    "This is not a marketing description — it is a systems characterization. "
                    "(1) State what the asset IS operationally: its physical classification, "
                    "functional programme, and the nature of its operational dependency on "
                    "multiple use streams — name each use stream and its structural role in "
                    "the building's operational continuity; "
                    "(2) Characterize the operational complexity: the landmark constraint, "
                    "the multi-system interdependencies, the public-access dimension "
                    "(observatory, retail), and how these create non-standard operational risk; "
                    "(3) State what is factually confirmed versus what is structurally inferred "
                    "about this asset's operational state. "
                    f"{operational_identity_instruction} "
                    "Write with the precision of a technical operator or systems engineer. "
                    "No valuation language, no transaction framing."
                ),
                {
                    "address":            fi.get("input_01_location", {}).get("address", ""),
                    "asset_type":         fac.get("primary_classification", ""),
                    "primary_uses":       {
                        "use_1": tenants.get("use_1", ""),
                        "use_1_pct": tenants.get("use_1_approx_pct"),
                        "use_2": tenants.get("use_2", ""),
                        "use_2_pct": tenants.get("use_2_approx_pct"),
                        "use_3": tenants.get("use_3", ""),
                        "use_3_pct": tenants.get("use_3_approx_pct"),
                    },
                    "gfa_sqft":          size.get("GFA_sqft", ""),
                    "rentable_sqft":     size.get("rentable_office_sqft_approx", ""),
                    "floors":            size.get("total_floors", ""),
                    "year_built":        vintage_fi.get("year_built", ""),
                    "vintage_category":  vintage_fi.get("vintage_category", ""),
                    "landmark_status":   reg_flags.get("landmark_status", ""),
                    "leed_status":       reg_flags.get("LEED_Gold_ll97_equivalence", ""),
                    "owner_entity":      company,
                    "owner_ticker":      ticker,
                    "known_systems":     systems,
                },
            )

        # ── S1: Decision State & Epistemic Brief ──────────────────────────────
        top_cases = sorted(inf_records, key=lambda x: x.get("validation_urgency_score", 0), reverse=True)
        blocking  = conflict_reg[0] if conflict_reg else {}
        finance_readiness_state = (
            "screening_only"
            if not financials or financials.get("revenues_annual") is None
            else "hold_for_overstatement_risk"
            if blocking.get("conflict_statement")
            else "bounded_decision_grade"
        )
        cost_basis_state = (
            "public_search_only"
            if ws_capex.get("numeric_extracts") or ws_capex.get("results")
            else "unavailable"
        )
        add(
            "s01_exec_narrative",
            "Executive Decision-Admissibility Brief" if blocked_report_mode else "Decision State & Epistemic Brief",
            "executive",
            (
                "Write a concise executive brief for a decision-maker audience. "
                "The frame is operational assessment under uncertainty — never transaction framing. "
                "State clearly whether this asset is decision-ready or still blocked. "
                "Explain the main dangerous assumption the reader must avoid, the primary blocking condition, "
                "and the minimum evidence path that should happen next. "
                "Use direct language and make the reader feel that stopping early is a strength, not a system failure."
            )
            if blocked_report_mode
            else
            (
                "Write a concise decision state brief (3-4 paragraphs) for a "
                "decision-maker audience. The frame is operational assessment — not transaction. "
                "Cover: "
                "(1) what asset is being assessed and what the framework characterizes as its "
                "current operational and epistemic state; "
                "(2) the overall analytical finding — what the system determined about the "
                "state of knowledge and what remains unresolved; "
                "(3) the key blocking epistemic conflict and why it prevents decision advancement; "
                "(4) what must be validated next, and in what order, to advance the epistemic state. "
                "Be direct. The document is not about a transaction — it is about what we know, "
                "what we do not know, and what must be confirmed before any decision is warranted."
            ),
            {
                "asset_name":              fi.get("input_01_location", {}).get("address", ""),
                "asset_type":              fac.get("primary_classification", ""),
                "owner_entity":            company,
                "owner_ticker":            ticker,
                "subject_kind":            subject_definition.get("subject_kind", ""),
                "asset_context_readiness": asset_context_readiness,
                "information_deficit_score": information_deficit_score,
                "total_inference_cases":   len(inf_records),
                "blocking_conflicts":      len(conflict_reg),
                "open_tensions":           len(tension_recs),
                "conditional_opportunities": len(opp_cands),
                "decision_state":          comp_reading.get("decision_state", ""),
                "blocking_case": {
                    "id":                blocking.get("inference_case_id", blocking.get("case_id", "")),
                    "name":              blocking.get("conflict_name", blocking.get("case_name", "")),
                    "statement":         blocking.get("conflict_statement", "")[:500],
                    "validation_needed": blocking.get("validation_requirement", "")[:300],
                },
                "decision_front_register": decision_front_register[:4],
                "minimum_evidence_unlock_map": minimum_evidence_unlock_map[:4],
                "claim_permission_summary": claim_permission_summary,
                "report_readiness_reason": report_readiness_register.get("reason", ""),
                "report_type_allowed": report_readiness_register.get("report_type_allowed", []),
                "report_type_prohibited": report_readiness_register.get("report_type_prohibited", []),
                "key_variable_bottlenecks": list(maturity_summary.get("key_bottlenecks", []) or []),
                "decision_permission_snapshot": _decision_permission_snapshot(
                    decision_permission_register,
                    [
                        "asset_identity_confirmation",
                        "seller_or_operator_evidence_request",
                        "retrofit_capex",
                        "acquisition_underwriting_with_energy_upside",
                    ],
                ),
                "blocked_claims": blocked_claims,
                "top_3_urgency_cases": [
                    {
                        "id":      r.get("case_id", ""),
                        "name":    r.get("case_name", ""),
                        "urgency": r.get("validation_urgency_score"),
                    }
                    for r in top_cases[:3]
                ],
            },
        )

        # ── S2: Financial Context (subordinated) ──────────────────────────────
        rev_series = financials.get("revenues_series", [])
        add(
            "s03_financial_narrative",
            "Financial Exposure Under Uncertainty" if blocked_report_mode else "Financial Context — Subordinated Scope",
            "technical",
            (
                "Write 2 short paragraphs on financial exposure under uncertainty. "
                "This section is appendix-grade and subordinated. "
                "Lead with scope limits, current readiness, and what financial claims remain prohibited. "
                "Then explain the downside of using consolidated issuer data as if it were asset evidence. "
                "Do not lead with metrics and do not make the case sound bankable."
            )
            if blocked_report_mode
            else
            (
                "Write 3 substantive paragraphs on the financial context of this asset. "
                "This section is SUBORDINATED — financial data provides scale and exposure "
                "context, it does not govern the operational assessment. "
                "Cover: "
                "(1) what financial data was obtained, from which authoritative source, "
                "and what its scope limitations are — specifically that figures are "
                "consolidated at the entity level, not asset-specific; "
                "(2) the current financial readiness posture — what the framework can "
                "and cannot say yet, including explicit prohibition on asset-level return, "
                "payback, IRR, NPV, DSCR, or bankability claims; "
                "(3) the key financial metrics and what they reveal about the "
                "asset's financial scale, structure, and operational health signals; "
                "(3) the critical data quality conflict — the material discrepancy between "
                "the reported debt figure and other sources — and why it creates an "
                "epistemic block on any leverage-dependent analysis. "
                "Do not lead with financial metrics. Lead with scope, readiness, and limitations."
            ),
            {
                "data_source":          financials.get("data_quality_note", ""),
                "filing_date":          financials.get("filing_date", ""),
                "finance_readiness_state": finance_readiness_state,
                "scope_boundary":       "consolidated_entity_level_only",
                "baseline_dependency":  "asset_specific_baseline_unavailable",
                "tariff_basis_state":   "unavailable",
                "cost_basis_state":     cost_basis_state,
                "bankability_posture":  "not_bankable_in_current_state",
                "inadmissible_metrics": ["asset_NOI", "payback", "IRR", "NPV", "DSCR", "bankability"],
                "financial_claim_permissions": _claim_permission_snapshot(
                    claim_permission_register,
                    [
                        "roi_directional_claim",
                        "roi_range_claim",
                        "roi_scenario_claim",
                    ],
                ),
                "financial_variable_maturity": _variable_maturity_snapshot(
                    variable_maturity_register,
                    [
                        "GFA",
                        "utility_bills",
                        "tariff_class",
                        "CAPEX",
                        "owner_control_boundary",
                    ],
                ),
                "revenues_annual":      _fmt(financials.get("revenues_annual")),
                "revenues_series":      [
                    {"period": r.get("end", ""), "value": _fmt(r.get("val"))}
                    for r in (rev_series if isinstance(rev_series, list) else [])[-6:]
                ],
                "total_debt_reported":  _fmt(financials.get("total_debt")),
                "total_assets":         _fmt(financials.get("total_assets")),
                "net_income":           _fmt(financials.get("net_income_annual")),
                "operating_income":     _fmt(financials.get("operating_income")),
                "epistemic_block":      blocking.get("conflict_statement", ""),
                "data_quality_note":    financials.get("data_quality_note", ""),
                "scope_note":           "Financial data is at the consolidated entity level — not asset-specific. Cannot be attributed to this property without segment disclosure.",
                "report_readiness_reason": report_readiness_register.get("reason", ""),
            },
        )

        # ── S3: Blocking Conflict Deep Dive ──────────────────────────────────
        if conflict_reg:
            c = conflict_reg[0]
            add(
                "s02_blocking_conflict",
                f"Blocking Conflict: {c.get('inference_case_id', c.get('case_id',''))} — "
                f"{c.get('conflict_name', c.get('case_name', ''))}",
                "technical",
                (
                    "Write a detailed analytical section (3-4 paragraphs) on this "
                    "blocking epistemic conflict. Cover: "
                    "(1) the precise nature of the discrepancy described in the conflict_statement — "
                    "what the two incompatible data signals are and why they cannot be reconciled; "
                    "(2) the mechanism by which this conflict blocks epistemic advancement — "
                    "what analysis becomes structurally impossible while this conflict remains open; "
                    "(3) the inference logic and what it implies about the underlying operational "
                    "or financial structure of the asset; "
                    "(4) exactly what evidence must be obtained, from which sources, to resolve "
                    "this conflict and restore the ability to advance the assessment. "
                    "Use precise technical language and explain each concept clearly."
                ),
                {
                    "case_id":                   c.get("inference_case_id", c.get("case_id", "")),
                    "case_name":                 c.get("conflict_name", c.get("case_name", "")),
                    "conflict_statement":        c.get("conflict_statement", ""),
                    "blocking_status":           c.get("blocking_status", ""),
                    "plausibility_score":        c.get("plausibility_score"),
                    "decision_relevance_score":  c.get("decision_relevance_score"),
                    "validation_urgency_score":  c.get("validation_urgency_score"),
                    "validation_requirement":    c.get("validation_requirement", ""),
                    "reported_debt_sec_xbrl":    _fmt(financials.get("total_debt")),
                    "total_assets":              _fmt(financials.get("total_assets")),
                },
            )

        # ── S4: Per-case analysis for top inference cases ─────────────────────
        if not blocked_report_mode:
            priority_cases = sorted(
                inf_records, key=lambda x: x.get("validation_urgency_score", 0), reverse=True
            )[:4]
            for rec in priority_cases:
                cid  = rec.get("case_id", "")
                add(
                    f"s03_case_{cid.lower()}",
                    f"{cid}: {rec.get('case_name', '')}",
                    "technical",
                    (
                        f"Write a thorough analytical section (2-3 paragraphs) for inference "
                        f"case {cid}. Cover: "
                        "(1) the analytical finding — what the framework determined and why "
                        "it is epistemically plausible given the available evidence and domain logic; "
                        "(2) the operational consequence — what this case implies about the "
                        "asset's operational state, normative exposure, or decision prerequisites; "
                        "(3) what validation is required and what it would confirm or rule out. "
                        "Be specific. Cite the conditional statement logic directly. "
                        "Frame consequences in terms of operational and epistemic impact, "
                        "not financial transaction impact."
                    ),
                    {
                        "case_id":                  cid,
                        "case_name":                rec.get("case_name", ""),
                        "claim_family":             rec.get("claim_family", ""),
                        "conditional_statement":    rec.get("conditional_statement", ""),
                        "inference_logic":          rec.get("inference_logic", ""),
                        "dependency_assumptions":   rec.get("dependency_assumptions", []),
                        "plausibility_score":       rec.get("plausibility_score"),
                        "decision_relevance_score": rec.get("decision_relevance_score"),
                        "validation_urgency_score": rec.get("validation_urgency_score"),
                        "validation_requirement":   rec.get("validation_requirement", ""),
                    },
                )

        # ── S5: Operational Systems and Energy Profile ────────────────────────
        add(
            "s09_systems_energy_narrative",
            "Regulatory / Normative Screening" if blocked_report_mode else "Operational Systems Profile and Normative Exposure",
            "technical",
            (
                "Write 2-3 paragraphs on bounded regulatory and systems screening. "
                "State clearly what rule family appears relevant, what trigger fields are still missing, "
                "and why current posture remains screening-grade only. "
                "Then explain the systems boundary problem: what is merely archetypal or inferred, what is not yet confirmed, "
                "and why this prevents stronger compliance or retrofit claims. "
                f"{systems_normative_instruction}"
            )
            if blocked_report_mode
            else
            (
                "Write 3-4 paragraphs covering the operational systems and "
                "energy-normative profile of this asset. "
                "THIS IS THE GOVERNING SECTION — systems and normative exposure are the "
                "central analytical axis of this report, not a subordinated risk factor. "
                "(1) Characterize each key system family using the system_hypotheses — state what is known, "
                "what is plausible, and what is structurally unknown; explain integration "
                "risks and operational dependencies between systems; "
                "(2) Explain the energy benchmark context: what the benchmark source is, "
                "what its methodological limitations are, and what it suggests about the "
                "asset's likely energy profile relative to the sector; "
                "(3) Explain the primary regulatory and compliance exposure with full technical depth: "
                "what the governing rule family appears to be, what makes it applicable or plausibly "
                "applicable, what trigger fields and thresholds are present or still missing, and "
                "what cannot yet be asserted from public data alone; "
                "if the primary regulation is LL97, then also explain what the 2024-2029 and "
                "2030-2034 thresholds mean at this asset's scale, why LEED Gold does not equal "
                "LL97 compliance, and why any penalty logic remains screening-grade until official disclosure; "
                "(4) What specific operational validation actions are required on systems "
                "and energy before the decision state can advance. "
                f"{systems_normative_instruction} "
                "Write with the authority of a technical systems engineer, not a financial analyst."
            ),
            {
                "target_type": target_type,
                "system_hypotheses":       sys_hypotheses,
                "benchmark": {
                    "source":                  bench.get("benchmark_source", ""),
                    "type":                    bench.get("benchmark_type", ""),
                    "office_median_EUI":       bench.get("office_sector_median_EUI_kBtu_sqft", ""),
                    "nyc_adjusted_EUI":        bench.get("NYC_adjusted_EUI_estimate_kBtu_sqft", ""),
                    "leed_gold_eui_reduction": bench.get("LEED_Gold_expected_EUI_reduction_pct", ""),
                    "limitation":              bench.get("benchmark_limitation", ""),
                },
                "ll97": {
                    "applicability":           reg_flags.get("LL97_applicability", ""),
                    "gfa_sqft":                reg_flags.get("LL97_GFA_sqft", ""),
                    "limit_2024_2029":         reg_flags.get("LL97_2024_2029_limit_tCO2e_sqft", ""),
                    "limit_2030_2034":         reg_flags.get("LL97_2030_2034_limit_tCO2e_sqft", ""),
                    "penalty_per_tCO2e_usd":   reg_flags.get("LL97_penalty_per_tCO2e_usd", ""),
                    "leed_equivalence_note":   reg_flags.get("LEED_Gold_ll97_equivalence", ""),
                    "determination_status":    reg_flags.get("compliance_determination_status", ""),
                    "landmark_constraint":     reg_flags.get("landmark_retrofit_constraint", ""),
                },
                "regulatory_claim_permissions": _claim_permission_snapshot(
                    claim_permission_register,
                    [
                        "compliance_screening_claim",
                        "compliance_closure_claim",
                        "ll97_penalty_screening_claim",
                        "energy_savings_claim",
                    ],
                ),
                "regulatory_variable_maturity": _variable_maturity_snapshot(
                    variable_maturity_register,
                    [
                        "jurisdiction",
                        "applicable_rule_family",
                        "regulated_floor_area",
                        "emissions",
                        "compliance_filing",
                        "HVAC_type",
                        "utility_bills",
                    ],
                ),
                "compliance_applicability_case": compliance_case,
                "known_systems_declared":  systems,
                "ll97_inference_case":     next(
                    (r.get("conditional_statement", "") for r in inf_records
                     if r.get("case_id") == "IC-03"), ""
                ),
	                "live_web_intelligence": {
	                    "ll97_search_snippets":    [r.get("snippet", "") for r in ws_ll97.get("results", [])[:3]],
	                    "ll97_numeric_extracts":   ws_ll97.get("numeric_extracts", []),
	                    "eui_search_snippets":     [r.get("snippet", "") for r in ws_energy.get("results", [])[:3]],
	                    "eui_numeric_extracts":    ws_energy.get("numeric_extracts", []),
	                    "capex_search_snippets":   [r.get("snippet", "") for r in ws_capex.get("results", [])[:3]],
	                    "capex_numeric_extracts":  ws_capex.get("numeric_extracts", []),
	                    "data_provenance":         "Live web search results — treat as unverified intelligence requiring validation",
	                },
	                "report_readiness_reason": report_readiness_register.get("reason", ""),
	            },
	        )

        # ── S6: CapEx and Building Age ────────────────────────────────────────
        capex_case = next(
            (r for r in inf_records if r.get("case_id") == "IC-05"), {}
        )
        if capex_case and not blocked_report_mode:
            add(
                "s09_capex_narrative",
                "Capital Requirements and Building Age Risk",
                "technical",
                (
                    "Write 2-3 paragraphs on the capital requirement risk profile of "
                    "this asset given its age and system profile. "
                    "(1) What the framework's inference on capital requirements states "
                    "and its logical basis — what physical and operational factors drive it; "
                    "(2) How landmark status structurally constrains the capital expenditure "
                    "pathway — what options are eliminated and what options remain; "
                    "(3) What validation is required to quantify the capital reserve gap "
                    "and what it would reveal about the operational readiness of the asset. "
                    "Be specific about what is confirmed vs. what is plausible. "
                    "Frame in terms of operational capacity, not financial return."
                ),
                {
                    "year_built":          vintage_fi.get("year_built", ""),
                    "years_old":           vintage_fi.get("years_old", ""),
                    "major_renovations":   vintage_fi.get("major_renovations_known", []),
                    "vintage_category":    vintage_fi.get("vintage_category", ""),
                    "structural_note":     vintage_fi.get("structural_note", ""),
                    "elevator_count":      systems.get("elevators", {}).get("count", ""),
                    "elevator_status":     systems.get("elevators", {}).get("status", ""),
                    "hvac_note":           systems.get("HVAC", {}).get("note", ""),
                    "landmark_status":     reg_flags.get("landmark_status", ""),
                    "landmark_constraint": reg_flags.get("landmark_retrofit_constraint", ""),
                    "capex_inference_case": {
                        "conditional_statement":  capex_case.get("conditional_statement", ""),
                        "inference_logic":        capex_case.get("inference_logic", ""),
                        "validation_requirement": capex_case.get("validation_requirement", ""),
                        "plausibility_score":     capex_case.get("plausibility_score"),
                    },
                    "vintage_tension": next(
                        (t.get("description", "") for t in op_tensions
                         if t.get("tension_type") == "vintage_capex_vs_reserve_adequacy"), ""
                    ),
                },
            )

        # ── S7: Tensions ─────────────────────────────────────────────────────
        if op_tensions or (blocked_report_mode and scenario_space):
            add(
                "s06_tensions_narrative",
                "Scenario Space Under Current Uncertainty" if blocked_report_mode else "Material Tensions and Structural Risk Factors",
                "technical",
                (
                    "Write 2 short paragraphs that explain the current scenario space. "
                    "Do not assign numeric probabilities. "
                    "Explain which scenario is currently dominant, which alternatives remain plausible, "
                    "and which specific evidence would discriminate between them. "
                    "Do not mention charts, prose, or the report itself."
                )
                if blocked_report_mode
                else
                (
                    "Write 2-3 paragraphs on the material structural tensions in this analysis. "
                    "For each tension: explain the conflicting operational or epistemic factors, "
                    "why they create irresolvable analytical tension at this stage, and what the "
                    "consequence is for the epistemic state of the assessment. "
                    "Be especially thorough on tenant concentration risk: what the operational "
                    "concentration means for revenue structure, what the binary event scenario "
                    "implies for the asset's operational continuity, and why this must be "
                    "resolved before the assessment can advance. "
                    "Frame all consequences in operational terms first, financial terms second."
                ),
                {
                    "scenario_space": scenario_space[:4],
                    "claim_permission_summary": claim_permission_summary,
                    "variable_bottleneck_register": variable_bottleneck_register[:4],
                    "operational_tensions": [
                        {
                            "id":          t.get("tension_id", ""),
                            "type":        t.get("tension_type", ""),
                            "description": t.get("description", "")[:400],
                        }
                        for t in op_tensions[:5]
                    ],
                    "inference_tensions": [
                        {
                            "id":        r.get("case_id", ""),
                            "name":      r.get("case_name", ""),
                            "statement": r.get("conditional_statement", "")[:300],
                        }
                        for r in tension_recs[:4]
                    ],
                    "tenant_data": {
                        "major_tenants":  tenants.get("major_tenants_known", []),
                        "anchor_tenant":  tenants.get("anchor_tenant", ""),
                        "anchor_sqft":    tenants.get("anchor_tenant_approx_sqft", ""),
                        "total_rentable": size.get("rentable_office_sqft_approx", ""),
                    },
                    "live_web_intelligence": {
                        "occupancy_snippets":     [r.get("snippet", "") for r in ws_occupancy.get("results", [])[:3]],
                        "occupancy_numerics":     ws_occupancy.get("numeric_extracts", []),
                        "tenant_news_snippets":   [r.get("snippet", "") for r in ws_tenants.get("results", [])[:3]],
                        "tenant_news_numerics":   ws_tenants.get("numeric_extracts", []),
                        "data_provenance":        "Live web search — unverified intelligence, treat with epistemic caution",
                    },
                },
            )

        # ── S8: Validation Architecture ───────────────────────────────────────
        vq_top = sorted(val_queue, key=lambda x: x.get("urgency_score", 0), reverse=True)[:6]
        add(
            "s04_validation_narrative",
            "Minimum Evidence Pack" if blocked_report_mode else "Validation Architecture",
            "technical",
            (
                "Write 2 short paragraphs introducing the minimum evidence pack. "
                "Explain that the immediate decision is what evidence to request first, not what capital to commit. "
                "Make clear that each evidence item unlocks a specific blocked reading or decision front."
            )
            if blocked_report_mode
            else
            (
                "Write a detailed validation architecture section (3 paragraphs + structured list). "
                "Open with the epistemic philosophy of this framework: it identifies what must be "
                "confirmed before the decision state can advance — not what is assumed to be true. "
                "Then: the critical validation path — which validations are prerequisite to all others "
                "and why their order matters. "
                "Then: a prioritized list of the top validation actions with: "
                "what to obtain, from which source, what epistemic block it resolves. "
                "Do not frame this as a checklist for a transaction. "
                "Frame it as the epistemic path from current state to decision-ready state."
            ),
            {
                "decision_state":          comp_reading.get("decision_state", ""),
                "total_open_validations":  len(val_queue),
                "minimum_evidence_unlock_map": minimum_evidence_unlock_map[:6],
                "decision_front_register": decision_front_register[:4],
                "blocking_item": {
                    "id":     blocking.get("inference_case_id", ""),
                    "name":   blocking.get("conflict_name", ""),
                    "status": blocking.get("blocking_status", ""),
                },
                "top_validations": [
                    {
                        "case_id":   v.get("case_id", ""),
                        "case_name": v.get("case_name", ""),
                        "urgency":   v.get("urgency_label", ""),
                        "action":    v.get("validation_requirement", "")[:250],
                    }
                    for v in vq_top
                ],
                "tad_preliminary": {
                    "information_deficit_score": tad_deficit,
                    "decision_frontier":         tad_frontier[:400] if tad_frontier else "",
                    "top_voi_actions": [
                        {
                            "rank":          a.get("rank"),
                            "case_id":       a.get("case_id", ""),
                            "voi_score":     a.get("voi_score"),
                            "effort_tier":   a.get("effort_tier", ""),
                            "decision_unlock": a.get("decision_unlock", "")[:200],
                        }
                        for a in tad_actions[:5]
                    ],
                    "blocking_resolution_paths": [
                        {
                            "conflict_id":      p.get("conflict_id", ""),
                            "minimum_evidence": p.get("minimum_evidence", "")[:200],
                        }
                        for p in tad_blocking[:2]
                    ],
                    "note": "VoI scores rank validation actions by information value: urgency × relevance × epistemic gap.",
                },
                "report_readiness_reason": report_readiness_register.get("reason", ""),
                "decision_permission_snapshot": _decision_permission_snapshot(
                    decision_permission_register,
                    [
                        "asset_identity_confirmation",
                        "seller_or_operator_evidence_request",
                        "retrofit_capex",
                        "compliance_investment",
                    ],
                ),
                "variable_bottleneck_register": variable_bottleneck_register[:6],
            },
        )

        # ── S9: Priority Questions ────────────────────────────────────────────
        if nbq and not blocked_report_mode:
            add(
                "s11_questions_narrative",
                "Priority Questions for the Decision Team",
                "executive",
                (
                    "Write a section framing the priority questions the decision team "
                    "must answer before the epistemic state of this assessment can advance. "
                    "Write as if briefing a technical decision committee — not a transaction committee: "
                    "explain why each question matters to the operational assessment, "
                    "what answering it would resolve or eliminate, "
                    "and what the epistemic consequence is if it cannot be answered. "
                    "Structure as numbered questions with explanatory prose. "
                    "The questions are about what must be known — not about whether to proceed."
                ),
                {
                    "questions": nbq[:8],
                    "framework_note": (
                        "These questions derive from activated inference cases. "
                        "Answering them transforms cases from 'plausible hypothesis' to either "
                        "'confirmed finding' or 'hypothesis eliminated'. "
                        "Until they are answered, the assessment remains in a partial epistemic state."
                    ),
                },
            )

        # ── S10: Conditional Decision Space ──────────────────────────────────
        if opp_cands or (blocked_report_mode and decision_front_register):
            add(
                "s08_opportunities_narrative",
                "TAD — Decision-Admissibility Layer" if blocked_report_mode else "Conditional Decision Space",
                "technical",
                (
                    "Write 2 short paragraphs closing the report with decision admissibility. "
                    "State what can be done now, what must be validated first, what should be deferred, "
                    "and what remains no-go. The reader should leave with a clear action posture, not with optimism."
                )
                if blocked_report_mode
                else
                (
                    "Write 2 paragraphs on the conditional decision space identified by the framework. "
                    "For each item: explain the operational or structural condition that must be "
                    "confirmed for this scenario to become actionable, "
                    "what epistemic prerequisite must be resolved first, "
                    "and what the scenario implies for operational strategy. "
                    "Maintain strict epistemic proportionality — these are conditional possibilities, "
                    "not forecasts or recommendations. "
                    "Lead with conditions, not with outcomes."
                ),
                {
                    "decision_front_register": decision_front_register[:6],
                    "decision_front_actions": tad_prelim.get("decision_front_actions", [])[:6],
                    "recommended_posture": tad_prelim.get("recommended_posture", ""),
                    "decision_permission_snapshot": _decision_permission_snapshot(
                        decision_permission_register,
                        [
                            "asset_identity_confirmation",
                            "seller_or_operator_evidence_request",
                            "retrofit_capex",
                            "acquisition_underwriting_with_energy_upside",
                            "compliance_investment",
                            "process_redesign",
                        ],
                    ),
                    "claim_permission_summary": claim_permission_summary,
                    "report_readiness_reason": report_readiness_register.get("reason", ""),
                    "conditional_scenarios": [
                        {
                            "id":         o.get("opportunity_id", ""),
                            "name":       o.get("opportunity_name", ""),
                            "statement":  o.get("opportunity_statement", o.get("conditional_statement", ""))[:350],
                            "conditions": o.get("conditions_required", o.get("dependency_assumptions", [])),
                        }
                        for o in opp_cands[:3]
                    ],
                    "epistemic_prerequisite": {
                        "id":   blocking.get("inference_case_id", ""),
                        "name": blocking.get("conflict_name", ""),
                        "note": "This blocking epistemic conflict must be resolved before any conditional scenario can be assessed",
                    },
                },
            )

        total_elapsed_seconds = time.monotonic() - writing_started_at_monotonic
        return {
            "written_sections":        written,
            "section_packets":         section_packets,
            "codex_available":         True,
            "llm_errors":              errors,
            "total_sections_written":  len(written),
            "llm_governance_summary": {
                "sections_attempted": len(section_packets),
                "sections_rendered": len(written),
                "lint_failures": lint_failures,
                "fallback_sections": fallback_sections,
                "structured_summary_sections": structured_summary_sections,
                "budget_exhausted": budget_exhausted,
                "unresolved_breaches": 0,
                "report_readiness_reason": report_readiness_register.get("reason", ""),
                "blocked_claim_count": len(blocked_claims),
            },
            "writing_runtime_profile": {
                "total_elapsed_seconds": round(total_elapsed_seconds, 3),
                "total_budget_seconds": _TOTAL_WRITE_BUDGET_SECONDS,
                "section_timeout_seconds": _SECTION_TIMEOUT,
                "budget_exhausted": budget_exhausted,
                "skipped_sections_due_budget": skipped_sections_due_budget,
            },
            "model_used":              _MODEL or "codex-cli-default",
            "produced_at":             produced_at,
        }
