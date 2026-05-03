#!/usr/bin/env python3
"""ZLab OTF — Monitor de control en tiempo real.

Uso:
    python dashboard.py           # http://localhost:7474
    python dashboard.py --open    # abre el navegador automáticamente
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string, request, send_file
from target_seeds import build_address_seed, write_seed_file

_HERE            = Path(__file__).resolve().parent
_REPO_ROOT       = _HERE.parent
_SRC_DIR         = _HERE / "src"
_RUNS_DIR        = _HERE / "run-registry"
_STORE_DIR       = _HERE / "artifact-store"
_OUTPUT_DIR      = _HERE / "output"
_SOURCE_REFRESH_STATUS = _HERE / "source_refresh_status.json"
_SOURCE_REFRESH_PID    = _HERE / "source_refresh.pid"
_LAUNCH_LOG_DIR  = Path("/tmp/zlab_runtime_launch_logs")
_MOTOR_CONTRACT  = _REPO_ROOT / "governanza" / "automation-base" / "motor_dependencies.json"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
try:
    from runtime_orchestrator.adapters import build_registry
    from runtime_orchestrator.adapters.motor_028 import (
        PRIMARY_SOURCE_CONTRACT,
        _EXTENDED_SOURCE_REGISTRY,
    )
    from runtime_orchestrator.asset_contracts import (
        derive_subject_definition,
        derive_target_definition,
    )
    from runtime_orchestrator.output_taxonomy import canonicalize_output_mode
    from runtime_orchestrator.run_registry import load_run_manifest
except Exception:
    build_registry = None
    PRIMARY_SOURCE_CONTRACT = []
    _EXTENDED_SOURCE_REGISTRY = []
    derive_subject_definition = None
    derive_target_definition = None
    canonicalize_output_mode = lambda value: str(value or "").strip()
    load_run_manifest = None

app = Flask(__name__)


@app.after_request
def _disable_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# ── Motores críticos de análisis / reporte ───────────────────────────────────
_FOCUS_MOTORS = {
    "motor_013": "Activación de casos de inferencia",
    "motor_014": "Decision Core / inferencia",
    "motor_015": "Composición de bloques de salida",
    "motor_016": "Ensamble del paquete de reporte",
    "motor_018": "Generación de charts",
    "motor_019": "Escritura LLM",
}

_PRIMARY_FALLBACK_CONTRACT = [
    {
        "source_type": "sec_edgar_submissions",
        "locator_tpl": "https://data.sec.gov/submissions/CIK{cik}.json",
        "discovery_reason": "CIK found in pipeline.subject.cik",
    },
    {
        "source_type": "sec_edgar_xbrl_facts",
        "locator_tpl": "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
        "discovery_reason": "XBRL structured financials from SEC EDGAR",
    },
    {
        "source_type": "nyc_open_data_property",
        "locator_tpl": "https://data.cityofnewyork.us/resource/yjxr-fw8i.json?parid={bbl}&$limit=5",
        "discovery_reason": "NYC DOF property assessment record for subject asset",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _contract_adapter_map() -> dict[str, str]:
    if build_registry is None:
        return {}
    try:
        registry = build_registry()
    except Exception:
        return {}
    adapters: dict[str, str] = {}
    for mid, _ in _motor_contract_list():
        adapter = registry.get(mid)
        adapters[mid] = type(adapter).__name__ if adapter is not None else ""
    return adapters


_CONTRACT_ADAPTERS: dict[str, str] = {}

def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _load_run(run_id: str) -> dict:
    path = _RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return {}
    if load_run_manifest is not None:
        return load_run_manifest(path)
    return _load_json(path)


def _runs_for_pipeline(pipeline_id: str) -> list[dict[str, Any]]:
    if not _RUNS_DIR.exists():
        return []
    matches: list[dict[str, Any]] = []
    for path in _RUNS_DIR.glob("*.json"):
        data = load_run_manifest(path) if load_run_manifest is not None else _load_json(path)
        if data.get("pipeline_id") == pipeline_id:
            data["_mtime"] = path.stat().st_mtime
            matches.append(data)
    matches.sort(key=lambda item: item.get("_mtime", 0.0), reverse=True)
    return matches


def _tail_text(path: Path, max_chars: int = 2000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    return text[-max_chars:]


def _canonicalize_report_type_trace(trace: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(trace or {})
    for key in (
        "early_report_type_gate",
        "maturity_refined_report_type",
        "final_published_report_type",
        "leading_primary_structural_output_mode",
        "default_structural_output_mode",
    ):
        if key in normalized:
            normalized[key] = canonicalize_output_mode(normalized.get(key, ""))
    normalized["secondary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("secondary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    normalized["blocked_secondary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("blocked_secondary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    normalized["eligible_primary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("eligible_primary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    normalized["non_promotable_primary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("non_promotable_primary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    return normalized


def _canonicalize_ingestion_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload or {})
    classification = dict(normalized.get("classification", {}) or {})
    if classification:
        classification["recommended_report_type_internal"] = classification.get(
            "recommended_report_type_internal",
            classification.get("recommended_report_type", ""),
        )
        classification["recommended_report_type"] = canonicalize_output_mode(
            classification.get("recommended_report_type", "")
        )
        classification["report_identity_state_internal"] = classification.get(
            "report_identity_state_internal",
            classification.get("report_identity_state", ""),
        )
        classification["report_identity_state"] = canonicalize_output_mode(
            classification.get("report_identity_state", "")
        )
        classification["report_type_trace"] = _canonicalize_report_type_trace(
            dict(classification.get("report_type_trace", {}) or {})
        )
        normalized["classification"] = classification
    return normalized


def _pipeline_alias_stem(pipeline_id: str) -> str:
    slug = (pipeline_id or "").strip().lower()
    if not slug:
        return ""
    parts = slug.split("-")
    if len(parts) >= 2 and len(parts[-1]) == 4 and parts[-1].isdigit():
        return "-".join(parts[:-1]).strip()
    return slug


def _matches_input_alias(path: Path, pipeline_id: str) -> bool:
    alias = _pipeline_alias_stem(pipeline_id)
    if not alias:
        return False
    stem = path.stem[:-7] if path.stem.endswith("_inputs") else path.stem
    if stem.lower() == alias:
        return True
    pipeline = _load_json(path)
    if not pipeline:
        return False
    target_definition = derive_target_definition(pipeline) if derive_target_definition is not None else {}
    candidates = {
        str(target_definition.get("target_id", "")).strip().lower(),
        str(target_definition.get("target_slug", "")).strip().lower(),
        str(target_definition.get("target_identifier", "")).strip().lower(),
        str(target_definition.get("target_name", "")).strip().lower(),
        str(pipeline.get("case_id", "")).strip().lower(),
    }
    return alias in {c for c in candidates if c}


def _resolve_inputs_file(pipeline_id: str, inputs_file: str) -> str:
    if inputs_file:
        candidate = Path(inputs_file)
        if candidate.exists():
            return str(candidate)
        relative = (_HERE / inputs_file).resolve()
        if relative.exists():
            return str(relative)
    slug = (pipeline_id or "").strip().lower()
    candidates: list[Path] = []
    if slug:
        candidates.append(_HERE / "inputs" / f"{slug}_inputs.json")
        prefix = slug.split("-", 1)[0].strip()
        if prefix and prefix != slug:
            candidates.append(_HERE / "inputs" / f"{prefix}_inputs.json")
    for guessed in candidates:
        if guessed.exists():
            return str(guessed)
    inputs_dir = _HERE / "inputs"
    if inputs_dir.exists():
        for path in sorted(inputs_dir.glob("*_inputs.json")):
            if _matches_input_alias(path, pipeline_id):
                return str(path)
    return inputs_file


def _load_inputs_for_run(run_d: dict[str, Any]) -> dict[str, Any]:
    pipeline_id = str(run_d.get("pipeline_id", "")).strip()
    candidate = _resolve_inputs_file(pipeline_id, "")
    if candidate and Path(candidate).exists():
        return _load_json(Path(candidate))
    return {}


def _artifact_path_for_motor_result(motor_id: str, motor_result: dict[str, Any]) -> Path | None:
    cached_from = motor_result.get("cached_from", "")
    if cached_from:
        p = Path(cached_from)
        return p if p.exists() else None
    inputs_hash = motor_result.get("inputs_hash", "")
    if inputs_hash:
        p = _STORE_DIR / motor_id / f"{inputs_hash}.json"
        return p if p.exists() else None
    return None


def _motor_contract_map() -> dict[str, dict[str, Any]]:
    data = _load_json(_MOTOR_CONTRACT)
    motors = data.get("motors", {})
    return motors if isinstance(motors, dict) else {}


def _motor_contract_list() -> list[tuple[str, dict[str, Any]]]:
    motors = _motor_contract_map()
    return [(mid, motors[mid]) for mid in sorted(motors)]


if not _CONTRACT_ADAPTERS:
    _CONTRACT_ADAPTERS = _contract_adapter_map()


def _load_motor_output(run_d: dict, motor_id: str) -> dict:
    motor = run_d.get("motor_results", {}).get(motor_id, {})
    artifact_path = _artifact_path_for_motor_result(motor_id, motor)
    if artifact_path is None:
        return {}
    art = _load_json(artifact_path)
    return art.get("output", art)


def _expected_motor_count() -> int:
    contract = _motor_contract_list()
    return len(contract) if contract else 34


def _is_full_framework_run(run_d: dict[str, Any]) -> bool:
    if not run_d:
        return False
    if "motor_results" in run_d:
        return len(run_d.get("motor_results", {})) >= _expected_motor_count()
    counts = run_d.get("motor_counts", {})
    return int(counts.get("total", 0)) >= _expected_motor_count()


def _display_status(status: str, *, pdf_available: bool) -> str:
    if status == "not_started":
        return "not_started"
    if status == "completed_with_stubs":
        return "completed_partial"
    if status == "partial":
        return "partial"
    if status == "completed" and not pdf_available:
        return "completed_no_pdf"
    return status


def _duration(run_d: dict) -> float | None:
    try:
        s = datetime.fromisoformat(run_d["started_at"].replace("Z", "+00:00"))
        e = datetime.fromisoformat(run_d["completed_at"].replace("Z", "+00:00"))
        return round((e - s).total_seconds(), 1)
    except Exception:
        return None


def _case_title_from_run(run_d: dict) -> str:
    fp = _load_motor_output(run_d, "motor_012").get("facility_prior", {})
    t = fp.get("case_title") or fp.get("case_id")
    if t:
        return t
    return run_d.get("pipeline_id", "")


def _company_info(run_d: dict) -> dict:
    """Lee owner / issuer context desde motor_028."""
    out = _load_motor_output(run_d, "motor_028")
    if not out:
        return {}
    ed  = out.get("enriched_data", {})
    return {
        "name":     ed.get("company_name", ""),
        "ticker":   ed.get("ticker", ""),
        "sic":      ed.get("sic_description", ""),
        "state":    ed.get("state_of_incorporation", ""),
        "gaps":     out.get("coverage_gaps", []),
        "status":   out.get("discovery_status", ""),
    }


def _target_code(subject_kind: str = "", target_type: str = "", pipeline_id: str = "") -> str:
    kind = str(subject_kind or "").strip().lower()
    if kind == "address_candidate":
        return "ADDR"
    if kind == "site_candidate":
        return "SITE"
    if kind == "asset_candidate":
        return "ASET"
    if kind == "asset":
        return "ASST"
    if kind == "issuer":
        return "ISSR"
    typ = str(target_type or "").strip().lower()
    if typ:
        words = [w for w in typ.replace("-", " ").split() if w]
        if len(words) >= 2:
            code = "".join(word[0] for word in words[:4]).upper()
            if len(code) >= 3:
                return code[:4]
        compact = "".join(ch for ch in typ if ch.isalpha()).upper()
        if compact:
            return compact[:4]
    if pipeline_id:
        return pipeline_id.split("-", 1)[0][:4].upper()
    return "TGT"


def _fallback_target_from_pipeline(pipeline: dict[str, Any], *, pipeline_id: str = "", inputs_file: str = "") -> dict[str, Any]:
    target_definition = derive_target_definition(pipeline) if derive_target_definition is not None else (pipeline.get("target_definition_contract", {}) if isinstance(pipeline.get("target_definition_contract", {}), dict) else {})
    subject_definition = derive_subject_definition(pipeline) if derive_subject_definition is not None else (pipeline.get("subject_definition_contract", {}) if isinstance(pipeline.get("subject_definition_contract", {}), dict) else {})
    target_label = (
        target_definition.get("address_raw")
        or subject_definition.get("declared_asset_name")
        or target_definition.get("target_name")
        or pipeline.get("case_title")
        or pipeline_id
        or "Unnamed target"
    )
    owner_name = (
        target_definition.get("owner_entity")
        or subject_definition.get("owner_context_optional")
        or ""
    )
    target_type = target_definition.get("target_type", "")
    target_id = target_definition.get("target_id", "")
    target_slug = target_definition.get("target_slug", "")
    subject_kind = subject_definition.get("subject_kind", "")
    return {
        "label": str(target_label).strip(),
        "address": str(target_definition.get("address_raw", "")).strip(),
        "target_type": str(target_type).strip(),
        "target_id": str(target_id).strip(),
        "target_slug": str(target_slug).strip(),
        "subject_kind": str(subject_kind).strip(),
        "owner_name": str(owner_name).strip(),
        "ticker": str((pipeline.get("facility_inputs", {}) or {}).get("input_03_sector", {}).get("owner_ticker", "")).strip() if isinstance((pipeline.get("facility_inputs", {}) or {}).get("input_03_sector", {}), dict) else "",
        "target_code": _target_code(subject_kind, target_type, pipeline_id),
        "pipeline_id": pipeline_id,
        "inputs_file": inputs_file,
    }


def _target_info(run_d: dict) -> dict:
    pipeline = _load_inputs_for_run(run_d)
    runtime_target = run_d.get("target_definition", {}) or {}
    runtime_subject = run_d.get("subject_definition", {}) or {}
    fallback = _fallback_target_from_pipeline(
        pipeline,
        pipeline_id=run_d.get("pipeline_id", ""),
        inputs_file=_resolve_inputs_file(run_d.get("pipeline_id", ""), ""),
    )
    if not runtime_target and not runtime_subject:
        return fallback
    label = (
        runtime_target.get("address_raw")
        or runtime_subject.get("declared_asset_name")
        or runtime_target.get("target_name")
        or fallback.get("label")
        or run_d.get("pipeline_id", "")
    )
    owner_name = (
        runtime_target.get("owner_entity")
        or runtime_subject.get("owner_context_optional")
        or fallback.get("owner_name", "")
    )
    return {
        "label": str(label).strip(),
        "address": str(runtime_target.get("address_raw", "") or fallback.get("address", "")).strip(),
        "target_type": str(runtime_target.get("target_type", "") or fallback.get("target_type", "")).strip(),
        "target_id": str(runtime_target.get("target_id", "") or fallback.get("target_id", "")).strip(),
        "target_slug": str(runtime_target.get("target_slug", "") or fallback.get("target_slug", "")).strip(),
        "subject_kind": str(runtime_subject.get("subject_kind", "") or runtime_target.get("subject_kind", "") or fallback.get("subject_kind", "")).strip(),
        "owner_name": str(owner_name).strip(),
        "ticker": str(fallback.get("ticker", "")).strip(),
        "target_code": str(fallback.get("target_code", "")).strip() or _target_code(
            runtime_subject.get("subject_kind", "") or runtime_target.get("subject_kind", ""),
            runtime_target.get("target_type", "") or fallback.get("target_type", ""),
            run_d.get("pipeline_id", ""),
        ),
        "pipeline_id": run_d.get("pipeline_id", ""),
        "inputs_file": fallback.get("inputs_file", ""),
    }


def _target_seed_records() -> list[dict[str, Any]]:
    inputs_dir = _HERE / "inputs"
    if not inputs_dir.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(inputs_dir.glob("*_inputs.json")):
        pipeline = _load_json(path)
        stem = path.stem[:-7] if path.stem.endswith("_inputs") else path.stem
        target = _fallback_target_from_pipeline(
            pipeline,
            pipeline_id=f"{stem}-{datetime.now().year}",
            inputs_file=str(path),
        )
        target_id = str(target.get("target_id", "")).strip() or stem
        pipeline_id = f"{target_id}-{datetime.now().year}"
        legacy_pipeline_id = f"{stem}-{datetime.now().year}"
        pipeline_aliases = []
        if legacy_pipeline_id != pipeline_id:
            pipeline_aliases.append(legacy_pipeline_id)
        subject_kind = target.get("subject_kind", "")
        owner_name = target.get("owner_name", "")
        context_parts = [p for p in [target.get("target_type", ""), subject_kind, owner_name] if p]
        records.append({
            "pipeline_id": pipeline_id,
            "pipeline_aliases": pipeline_aliases,
            "inputs_file": str(path),
            "has_inputs": True,
            "target_label": target.get("label", stem),
            "target_address": target.get("address", ""),
            "target_type": target.get("target_type", ""),
            "target_id": target_id,
            "target_slug": target.get("target_slug", ""),
            "subject_kind": subject_kind,
            "owner_name": owner_name,
            "ticker": target.get("ticker", stem.upper()),
            "target_code": target.get("target_code", _target_code(subject_kind, target.get("target_type", ""), pipeline_id)),
            "context_line": " · ".join(context_parts),
        })
    return records


def _target_seed_lookup(pipeline_id: str) -> dict[str, Any]:
    if not pipeline_id:
        return {}
    for seed in _target_seed_records():
        aliases = [seed.get("pipeline_id", ""), *seed.get("pipeline_aliases", [])]
        if pipeline_id in aliases:
            return seed
    return {}


def _target_from_seed_record(seed: dict[str, Any]) -> dict[str, Any]:
    if not seed:
        return {}
    return {
        "label": str(seed.get("target_label") or seed.get("name") or seed.get("pipeline_id") or "Unnamed target").strip(),
        "address": str(seed.get("target_address", "")).strip(),
        "target_type": str(seed.get("target_type", "")).strip(),
        "target_id": str(seed.get("target_id", "")).strip(),
        "target_slug": str(seed.get("target_slug", "")).strip(),
        "subject_kind": str(seed.get("subject_kind", "")).strip(),
        "owner_name": str(seed.get("owner_name", "")).strip(),
        "ticker": str(seed.get("ticker", "")).strip(),
        "target_code": str(seed.get("target_code", "")).strip(),
        "pipeline_id": str(seed.get("pipeline_id", "")).strip(),
        "inputs_file": str(seed.get("inputs_file", "")).strip(),
    }


def _focus_activity(run_d: dict, motors: list[dict[str, Any]]) -> list[dict]:
    motor_map = {m["motor_id"]: m for m in motors}
    result = []
    for mid, label in _FOCUS_MOTORS.items():
        m       = motor_map.get(mid, {})
        status  = m.get("status", "pending")
        snippet = ""
        # Intentar extraer un snippet del bloque narrativo
        if status in ("completed", "cached"):
            out = _load_motor_output(run_d, mid)
            blocks = out.get("output_blocks", [])
            if blocks and isinstance(blocks[0], dict):
                paras = blocks[0].get("content_paragraphs", [])
                if paras:
                    snippet = paras[0][:180]
        result.append({
            "motor_id":    mid,
            "label":       label,
            "status":      status,
            "duration_ms": m.get("duration_ms"),
            "snippet":     snippet,
            "error":       m.get("error"),
            "name":        m.get("motor_name", ""),
        })
    return result


def _source_contract() -> list[dict[str, Any]]:
    primary = PRIMARY_SOURCE_CONTRACT or _PRIMARY_FALLBACK_CONTRACT
    contract: list[dict[str, Any]] = []
    for spec in primary:
        contract.append({
            "source_type": spec.get("source_type", ""),
            "locator_tpl": spec.get("locator_tpl", ""),
            "discovery_reason": spec.get("discovery_reason", ""),
            "attempt_kind": spec.get("attempt_kind", "primary"),
            "source_scope": _source_scope(spec.get("source_type", "")),
        })
    for spec in _EXTENDED_SOURCE_REGISTRY:
        contract.append({
            "source_type": spec.get("source_type", ""),
            "locator_tpl": spec.get("locator_tpl", ""),
            "discovery_reason": spec.get("discovery_reason", ""),
            "attempt_kind": "extended",
            "source_scope": _source_scope(spec.get("source_type", "")),
        })
    return contract


def _source_label(source_type: str) -> str:
    labels = {
        "census_geocoder_validation": "Census geocoder validation",
        "ashrae_climate_zone_lookup": "ASHRAE climate zone lookup",
        "asset_energy_behavior_reference": "Asset energy behavior reference",
        "city_benchmarking_boston": "Boston building benchmarking reference",
        "sec_edgar_submissions": "SEC EDGAR submissions",
        "sec_edgar_xbrl_facts": "SEC EDGAR XBRL facts",
        "nyc_open_data_property": "NYC DOF property assessment",
        "nyc_ll84_energy_benchmarking": "NYC LL84 benchmarking",
        "nyc_pluto_property": "NYC PLUTO property",
        "nyc_dob_permits": "NYC DOB permits",
        "nyc_acris_mortgage_records": "NYC ACRIS mortgage records",
        "sec_edgar_efts_fulltext": "SEC EDGAR full-text search",
        "sec_edgar_8k_events": "SEC EDGAR 8-K events",
        "sec_10k_full_text_extraction": "SEC 10-K full-text extraction",
        "esrt_ir_html_scrape": "Issuer-specific IR page (ESRT only)",
        "esrt_10k_html_extraction": "Issuer-specific 10-K extraction (ESRT only)",
        "eia_commercial_electricity_rates": "EIA electricity rates",
        "epa_energy_star_benchmarks": "EPA Energy Star benchmarks",
    }
    if source_type in labels:
        return labels[source_type]
    return source_type.replace("_", " ")


def _source_family(source_type: str) -> str:
    if source_type.startswith("sec_") or source_type.startswith("esrt_"):
        return "issuer_context"
    if source_type.startswith("census_") or source_type.startswith("parcel_"):
        return "asset_identity"
    if source_type.startswith("ashrae_") or source_type.startswith("noaa_"):
        return "climate_context"
    if source_type.startswith("city_benchmarking_") or source_type.startswith("asset_energy_behavior_"):
        return "asset_energy_context"
    if source_type.startswith("nyc_") or source_type.startswith("city_"):
        return "city_property"
    if source_type.startswith("epa_") or source_type.startswith("eia_") or source_type.startswith("noaa_"):
        return "energy_environment"
    if source_type.startswith("web_search_"):
        return "web_search"
    if source_type.startswith("census_") or source_type.startswith("bls_") or source_type.startswith("fred_"):
        return "economic_context"
    return "other"


def _source_scope(source_type: str) -> str:
    if source_type.startswith("esrt_"):
        return "issuer_specific"
    if source_type.startswith("census_") or source_type.startswith("parcel_"):
        return "asset_identity_level"
    if source_type.startswith("ashrae_") or source_type.startswith("noaa_"):
        return "asset_environment_level"
    if source_type.startswith("asset_energy_behavior_") or source_type.startswith("city_benchmarking_"):
        return "asset_benchmark_level"
    if source_type.startswith("nyc_"):
        return "asset_jurisdiction_specific"
    if source_type.startswith("sec_"):
        return "entity_level"
    if source_type.startswith("web_search_"):
        return "market_signal"
    if source_type.startswith(("eia_", "epa_", "noaa_")):
        return "energy_environment_context"
    if source_type.startswith(("census_", "bls_", "fred_", "fhfa_", "hud_")):
        return "macro_context"
    return "extended_context"


def _gap_to_source_type(gap: dict[str, Any]) -> str:
    mapping = {
        "company_submissions": "sec_edgar_submissions",
        "financial_metrics": "sec_edgar_xbrl_facts",
        "property_assessment": "nyc_open_data_property",
    }
    return mapping.get(gap.get("gap_type", ""), gap.get("gap_type", ""))


def _fallback_source_activity(m28_out: dict) -> dict[str, Any]:
    contract = _source_contract()
    attempts: dict[str, dict[str, Any]] = {
        item["source_type"]: {
            "source_type": item["source_type"],
            "label": _source_label(item["source_type"]),
            "locator": item.get("locator_tpl", ""),
            "status": "untracked",
            "attempt_kind": item.get("attempt_kind", ""),
            "source_scope": item.get("source_scope", _source_scope(item["source_type"])),
            "family": _source_family(item["source_type"]),
            "discovery_reason": item.get("discovery_reason", ""),
            "detail": "Este run no registró el intento por fuente; solo dejó éxitos / errores parciales.",
            "matched_terms": [],
            "error": "",
        }
        for item in contract
        if item.get("source_type")
    }
    for candidate in m28_out.get("discovery_candidates", []):
        source_type = candidate.get("source_type", "")
        if not source_type:
            continue
        attempts[source_type] = {
            "source_type": source_type,
            "label": _source_label(source_type),
            "locator": candidate.get("locator", ""),
            "status": "found",
            "attempt_kind": attempts.get(source_type, {}).get("attempt_kind", ""),
            "source_scope": attempts.get(source_type, {}).get("source_scope", _source_scope(source_type)),
            "family": _source_family(source_type),
            "discovery_reason": candidate.get("discovery_reason", ""),
            "detail": "",
            "matched_terms": candidate.get("matched_terms", []),
            "error": "",
        }
    primary_rejections = {
        "src_001": "sec_edgar_submissions",
        "src_002": "sec_edgar_xbrl_facts",
        "src_003": "nyc_open_data_property",
        "src_003_nyc_property": "nyc_open_data_property",
    }
    for rejection in m28_out.get("discovery_rejections", []):
        source_type = primary_rejections.get(rejection.get("source_id", ""), "")
        if not source_type:
            continue
        attempts[source_type] = {
            "source_type": source_type,
            "label": _source_label(source_type),
            "locator": rejection.get("locator", ""),
            "status": "failed",
            "attempt_kind": attempts.get(source_type, {}).get("attempt_kind", "primary"),
            "source_scope": attempts.get(source_type, {}).get("source_scope", _source_scope(source_type)),
            "family": _source_family(source_type),
            "discovery_reason": attempts.get(source_type, {}).get("discovery_reason", ""),
            "detail": "",
            "matched_terms": [],
            "error": rejection.get("reason_detail", ""),
        }
    for gap in m28_out.get("coverage_gaps", []):
        source_type = _gap_to_source_type(gap)
        if not source_type or source_type not in attempts:
            continue
        if attempts[source_type]["status"] == "untracked":
            attempts[source_type]["status"] = "failed"
            attempts[source_type]["error"] = gap.get("detail", "") or ", ".join(gap.get("scope_terms", []))
    ordered = sorted(attempts.values(), key=lambda item: (item["status"] != "found", item["label"]))
    summary = {
        "contract_total": len(contract),
        "applicable_contract_total": len(contract),
        "attempted": len([a for a in ordered if a["status"] != "untracked"]),
        "applicable_attempted": len([a for a in ordered if a["status"] in ("found", "no_data", "failed")]),
        "found": len([a for a in ordered if a["status"] == "found"]),
        "admitted": len(m28_out.get("discovery_candidates", [])),
        "no_data": len([a for a in ordered if a["status"] == "no_data"]),
        "failed": len([a for a in ordered if a["status"] == "failed"]),
        "context_missing": 0,
        "not_applicable": 0,
        "untracked": len([a for a in ordered if a["status"] == "untracked"]),
        "tracking_complete": False,
        "applicable_tracking_complete": False,
        "candidates": len(m28_out.get("discovery_candidates", [])),
        "rejections": len(m28_out.get("discovery_rejections", [])),
        "coverage_gaps": len(m28_out.get("coverage_gaps", [])),
    }
    return {
        "summary": summary,
        "attempts": ordered,
        "note": "Este artifact no registró intentos por fuente. El dashboard expone el contrato de fuentes y marca qué quedó realmente trazado.",
    }


def _research_activity(run_d: dict) -> dict[str, Any]:
    out = _load_motor_output(run_d, "motor_028")
    if not out:
        return {"summary": {}, "attempts": [], "note": "motor_028 no dejó artifact para este run."}
    attempts = out.get("discovery_attempts", [])
    if attempts:
        normalized = []
        for attempt in attempts:
            source_type = attempt.get("source_type", "")
            normalized.append({
                **attempt,
                "label": _source_label(source_type),
                "family": _source_family(source_type),
                "source_scope": attempt.get("source_scope", _source_scope(source_type)),
            })
        summary = out.get("discovery_summary", {}).copy()
        summary.setdefault("contract_total", len(_source_contract()))
        summary.setdefault("applicable_contract_total", summary.get("contract_total", 0) - summary.get("not_applicable", 0))
        summary.setdefault("untracked", max(summary.get("contract_total", 0) - summary.get("attempted", 0), 0))
        summary.setdefault("applicable_attempted", summary.get("found", 0) + summary.get("no_data", 0) + summary.get("failed", 0) + summary.get("context_missing", 0))
        summary.setdefault("admitted", summary.get("candidates", 0))
        summary.setdefault("context_missing", 0)
        summary.setdefault("not_applicable", 0)
        summary.setdefault("applicable_tracking_complete", summary.get("applicable_attempted", 0) == summary.get("applicable_contract_total", 0))
        return {
            "summary": summary,
            "attempts": sorted(normalized, key=lambda item: (item.get("status") != "found", item.get("label", ""))),
            "note": "",
        }
    return _fallback_source_activity(out)


def _ingestion_activity(run_d: dict) -> dict[str, Any]:
    m28 = _load_motor_output(run_d, "motor_028")
    m12 = _load_motor_output(run_d, "motor_012")
    m14 = _load_motor_output(run_d, "motor_014")
    m35 = _load_motor_output(run_d, "motor_035")
    if not m28 and not m12 and not m14 and not m35:
        return {
            "available": False,
            "classification": {},
            "summary": {},
            "blocking_fields": [],
            "missing_evidence": [],
        }

    source_register = list((m28 or {}).get("source_register", []) or [])
    asset_field_register = list((m12 or {}).get("asset_field_register", []) or [])
    missing_evidence_register = list((m14 or {}).get("missing_evidence_register", []) or (m12 or {}).get("missing_evidence_register", []) or [])
    accepted_count = len([row for row in source_register if row.get("accepted")])
    rejected_count = len([row for row in source_register if not row.get("accepted")])
    scope_counts: dict[str, int] = {}
    for row in source_register:
        scope = str(row.get("scope", "")).strip() or "UNKNOWN_SCOPE"
        scope_counts[scope] = scope_counts.get(scope, 0) + 1
    blocking_fields = [
        {
            "field": row.get("field", ""),
            "admissibility": row.get("admissibility", ""),
            "scope": row.get("scope", ""),
            "notes": row.get("notes", ""),
        }
        for row in asset_field_register
        if row.get("status") == "BLOCKING_FIELD"
    ]
    classification = {
        "target_type": run_d.get("target_type_classification", ""),
        "classification_confidence": run_d.get("classification_confidence", ""),
        "asset_identity_status": run_d.get("asset_identity_status", ""),
        "target_admissibility_state": run_d.get("target_admissibility_state", ""),
        "technical_substrate_readiness": run_d.get("technical_substrate_readiness", ""),
        "recommended_report_type_internal": run_d.get("recommended_report_type", ""),
        "recommended_report_type": run_d.get("recommended_report_type", ""),
        "report_identity_state_internal": run_d.get("report_identity_state", ""),
        "report_identity_state": run_d.get("report_identity_state", ""),
        "report_type_trace": dict(run_d.get("report_type_trace", {}) or {}),
        "phase_self_evaluation_summary": dict(run_d.get("phase_self_evaluation_summary", {}) or {}),
        "ingestion_contract_status": run_d.get("ingestion_contract_status", ""),
        "subject_gate_passed": bool(run_d.get("subject_gate_passed", False)),
    }
    ingestion_learning_summary = dict(run_d.get("ingestion_learning_summary", {}) or {})
    case_delta_summary = dict(run_d.get("case_delta_summary", {}) or {})
    source_yield_memory_summary = dict(run_d.get("source_yield_memory_summary", {}) or {})
    next_ingestion_priority_update = dict(run_d.get("next_ingestion_priority_update", {}) or {})
    routing_plan = dict((m35 or {}).get("source_routing_plan", {}) or (m28 or {}).get("source_routing_plan", {}) or {})
    routing_plan_compliance = dict((m28 or {}).get("routing_plan_compliance", {}) or {})
    jurisdiction_resolution = dict((m35 or {}).get("jurisdiction_resolution", {}) or {})
    critical_field_contract = list((m35 or {}).get("critical_field_contract", []) or [])
    return {
        "available": True,
        "classification": classification,
        "summary": {
            "sources_total": len(source_register),
            "sources_accepted": accepted_count,
            "sources_rejected": rejected_count,
            "asset_fields_total": len(asset_field_register),
            "blocking_fields_total": len(blocking_fields),
            "missing_evidence_total": len(missing_evidence_register),
            "scope_counts": scope_counts,
        },
        "learning": {
            "summary": ingestion_learning_summary,
            "case_delta_summary": case_delta_summary,
            "source_yield_memory_summary": source_yield_memory_summary,
            "next_ingestion_priority_update": next_ingestion_priority_update,
        },
        "jurisdiction_resolution": jurisdiction_resolution,
        "routing_plan": {
            "mandatory_sources": list(routing_plan.get("mandatory_sources", []) or []),
            "high_priority_sources": list(routing_plan.get("high_priority_sources", []) or []),
            "optional_sources": list(routing_plan.get("optional_sources", []) or []),
            "disallowed_substitutions": list(routing_plan.get("disallowed_substitutions", []) or []),
            "routing_notes": list(routing_plan.get("routing_notes", []) or []),
        },
        "routing_plan_compliance": routing_plan_compliance,
        "critical_field_contract": critical_field_contract[:12],
        "blocking_fields": blocking_fields[:8],
        "missing_evidence": [
            {
                "missing_field": row.get("missing_field", ""),
                "minimum_evidence_needed": row.get("minimum_evidence_needed", ""),
                "suggested_source": row.get("suggested_source", ""),
            }
            for row in missing_evidence_register[:8]
        ],
    }


def _chart_activity(run_d: dict) -> dict[str, Any]:
    motor = run_d.get("motor_results", {}).get("motor_018", {})
    out = _load_motor_output(run_d, "motor_018")
    if not motor:
        return {"status": "missing", "total_charts": 0, "assets": [], "errors": []}
    assets = out.get("chart_assets", []) if out else []
    errors = out.get("chart_errors", []) if out else []
    return {
        "status": motor.get("status", "missing"),
        "adapter_class": motor.get("adapter_class", ""),
        "total_charts": out.get("total_charts", len(assets)) if out else 0,
        "assets": [
            {
                "asset_id": asset.get("asset_id", ""),
                "title": asset.get("title", asset.get("asset_id", "")),
                "description": asset.get("description", ""),
                "section_hint": asset.get("section_hint", ""),
            }
            for asset in assets
        ],
        "errors": errors,
    }


def _all_runs() -> list[dict]:
    if not _RUNS_DIR.exists():
        return []
    runs = []
    # Ordenar por fecha de modificación real (más reciente primero)
    for p in sorted(_RUNS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:50]:
        d  = load_run_manifest(p) if load_run_manifest is not None else _load_json(p)
        mr = d.get("motor_results", {})
        runs.append({
            "run_id":      d.get("run_id", p.stem),
            "pipeline_id": d.get("pipeline_id", ""),
            "status":      d.get("status", "unknown"),
            "started_at":  d.get("started_at", ""),
            "completed_at": d.get("completed_at", ""),
            "duration_s":  _duration(d),
            "case_title":  _case_title_from_run(d),
            "mtime":       p.stat().st_mtime,
            "motor_counts": {
                "total":     len(mr),
                "completed": sum(1 for v in mr.values() if v.get("status") == "completed"),
                "cached":    sum(1 for v in mr.values() if v.get("status") == "cached"),
                "stub":      sum(1 for v in mr.values() if v.get("status") == "stub"),
                "failed":    sum(1 for v in mr.values() if v.get("status") == "failed"),
                "running":   sum(1 for v in mr.values() if v.get("status") == "running"),
            },
            "is_full_framework_run": len(mr) >= _expected_motor_count(),
        })
    return runs


def _select_active_run(
    runs: list[dict[str, Any]],
    *,
    requested_run_id: str = "",
    requested_pipeline_id: str = "",
) -> dict[str, Any] | None:
    if requested_run_id:
        exact = next((r for r in runs if r["run_id"] == requested_run_id), None)
        if exact is not None:
            return exact
    full_runs = [r for r in runs if r.get("is_full_framework_run")]
    if requested_pipeline_id:
        pipeline_runs = [r for r in full_runs if r.get("pipeline_id") == requested_pipeline_id]
        if not pipeline_runs:
            return None
        running = next((r for r in pipeline_runs if r.get("status") == "running"), None)
        return running or pipeline_runs[0]
    running = next((r for r in full_runs if r["status"] == "running"), None)
    full = next((r for r in full_runs if r["motor_counts"]["total"] >= 30), None)
    return running or full or (runs[0] if runs else None)


def _legacy_truth_state(motor_result: dict[str, Any], is_placeholder_contract: bool) -> str:
    raw_status = motor_result.get("status", "missing")
    if raw_status == "cached":
        if motor_result.get("output_state") == "stub" or is_placeholder_contract:
            return "cached_stub"
        return "cached_real"
    if raw_status == "completed":
        if is_placeholder_contract or motor_result.get("output_state") == "stub":
            return "completed_stub"
        return "completed_real"
    return raw_status


def _run_detail(run_id: str) -> dict:
    d = _load_run(run_id)
    if not d:
        return {}
    mr = d.get("motor_results", {})
    motors = []
    status_counts = {
        "pending": 0,
        "completed": 0,
        "cached": 0,
        "stub": 0,
        "cached_stub": 0,
        "completed_stub": 0,
        "failed": 0,
        "running": 0,
        "skipped": 0,
        "missing": 0,
        "pending_real": 0,
        "completed_real": 0,
        "cached_real": 0,
        "failed_real": 0,
        "running_real": 0,
        "missing_real": 0,
    }
    placeholder_contract = 0
    implemented_contract = 0
    for mid, spec in _motor_contract_list():
        r = mr.get(mid, {})
        contract_adapter = _CONTRACT_ADAPTERS.get(mid, "")
        is_placeholder_contract = contract_adapter == "StubMotorAdapter"
        raw_status = r.get("status", "missing")
        truth_state = r.get("truth_state") or _legacy_truth_state(r, is_placeholder_contract)
        status = truth_state or raw_status
        if is_placeholder_contract:
            placeholder_contract += 1
        else:
            implemented_contract += 1
        if status not in status_counts:
            status_counts["missing"] += 1
        else:
            status_counts[status] += 1
        if not is_placeholder_contract:
            if status in ("running", "failed", "pending", "missing"):
                real_key = f"{status}_real"
                if real_key in status_counts:
                    status_counts[real_key] += 1
                else:
                    status_counts["missing_real"] += 1
        motors.append({
            "motor_id": mid,
            "motor_name": spec.get("name", ""),
            "status": status,
            "raw_status": raw_status,
            "truth_state": truth_state,
            "duration_ms": r.get("duration_ms"),
            "adapter_class": r.get("adapter_class", ""),
            "contract_adapter_class": contract_adapter,
            "implementation_state": r.get("implementation_state") or ("placeholder" if is_placeholder_contract else "implemented"),
            "output_state": r.get("output_state", ""),
            "error": r.get("error"),
            "cached_from": str(_artifact_path_for_motor_result(mid, r) or ""),
            "is_stub": r.get("adapter_class", "") == "StubMotorAdapter" or is_placeholder_contract,
            "is_placeholder_contract": is_placeholder_contract,
        })
    return {
        "run_id":       d.get("run_id"),
        "pipeline_id":  d.get("pipeline_id"),
        "status":       d.get("status"),
        "started_at":   d.get("started_at"),
        "completed_at": d.get("completed_at"),
        "duration_s":   _duration(d),
        "case_title":   _case_title_from_run(d),
        "error":        d.get("error"),
        "motors":       motors,
        "summary":      d.get("summary", {}),
        "motor_overview": {
            **status_counts,
            "total_expected": len(motors),
            "implemented_contract": implemented_contract,
            "placeholder_contract": placeholder_contract,
        },
    }


def _audit_failures(run_id: str) -> dict:
    d = _load_run(run_id)
    if not d:
        return {"available": False, "failures": []}
    mr = d.get("motor_results", {})
    m24 = mr.get("motor_024", {})
    out = _load_motor_output(d, "motor_024")
    if not m24 or not out:
        # Fallback: motores con status failed
        failed = [
            {"type": "Motor fallido", "motor": mid, "message": r.get("error", ""), "severity": "error"}
            for mid, r in mr.items() if r.get("status") == "failed"
        ]
        return {"available": bool(failed), "failures": failed}
    if out.get("__stub__"):
        return {"available": False, "failures": []}
    failures = []
    for exc in out.get("exception_register", []):
        failures.append({
            "type":     exc.get("event_type", "Error"),
            "motor":    exc.get("motor_id", ""),
            "message":  exc.get("description", exc.get("outcome", "")),
            "severity": exc.get("severity", "error"),
        })
    for ev in out.get("governance_event_log", []):
        if ev.get("severity") in ("error", "critical"):
            failures.append({
                "type":     ev.get("event_type", "Error"),
                "motor":    ev.get("motor_id", ""),
                "message":  ev.get("description", ""),
                "severity": ev.get("severity"),
            })
    health = out.get("pipeline_health_summary", {})
    return {
        "available": True,
        "failures":  failures,
        "health":    health,
    }


def _latest_pdf() -> dict | None:
    search = [_OUTPUT_DIR, Path.home() / "ZLab_Reports"]
    pdfs   = []
    for base in search:
        if not base.exists():
            continue
        for p in base.rglob("*.pdf"):
            try:
                pdfs.append((p.stat().st_mtime, p))
            except Exception:
                pass
    if not pdfs:
        return None
    _, p = max(pdfs)
    stat = p.stat()
    return {
        "path":     str(p),
        "name":     p.name,
        "size_kb":  round(stat.st_size / 1024, 1),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "mtime":    stat.st_mtime,
    }


def _pdf_metadata(path_str: str) -> dict | None:
    if not path_str:
        return None
    p = Path(path_str)
    if not p.exists():
        return None
    stat = p.stat()
    return {
        "path": str(p),
        "name": p.name,
        "size_kb": round(stat.st_size / 1024, 1),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "mtime": stat.st_mtime,
    }


def _pdf_variants_for_run(run_d: dict) -> dict[str, dict]:
    if not run_d:
        return {}
    variants: dict[str, dict] = {}
    for motor_id, key in (
        ("motor_027", "pdf_output_paths"),
        ("motor_027", "pdf_source_paths"),
        ("motor_017", "pdf_paths"),
    ):
        out = _load_motor_output(run_d, motor_id)
        raw = out.get(key, {})
        if not isinstance(raw, dict):
            continue
        for language, path_str in raw.items():
            meta = _pdf_metadata(path_str)
            if meta is not None:
                variants[str(language)] = meta
        if variants:
            return variants
    single = None
    for motor_id, key in (
        ("motor_027", "pdf_output_path"),
        ("motor_027", "pdf_source_path"),
        ("motor_017", "pdf_path"),
    ):
        out = _load_motor_output(run_d, motor_id)
        single = _pdf_metadata(out.get(key, ""))
        if single is not None:
            break
    return {"en": single} if single is not None else {}


def _pdf_for_run(run_d: dict, *, allow_global_fallback: bool = False) -> dict | None:
    if not run_d:
        return _latest_pdf() if allow_global_fallback else None
    variants = _pdf_variants_for_run(run_d)
    if variants:
        return variants.get("en") or next(iter(variants.values()))
    for motor_id, key in (
        ("motor_027", "pdf_output_path"),
        ("motor_027", "pdf_source_path"),
        ("motor_017", "pdf_path"),
    ):
        out = _load_motor_output(run_d, motor_id)
        meta = _pdf_metadata(out.get(key, ""))
        if meta is not None:
            return meta
    return _latest_pdf() if allow_global_fallback else None


def _source_refresh_status() -> dict:
    pid_running = False
    if _SOURCE_REFRESH_PID.exists():
        try:
            import os as _os
            _os.kill(int(_SOURCE_REFRESH_PID.read_text().strip()), 0)
            pid_running = True
        except Exception:
            pass
    if not _SOURCE_REFRESH_STATUS.exists():
        return {
            "enabled": False,
            "running": False,
            "mode": "manual_only",
            "companies": [],
            "log": [],
            "total_sweeps": 0,
            "message": "Refresco automático desactivado. El análisis solo corre al pulsar Analizar.",
        }
    try:
        d = json.loads(_SOURCE_REFRESH_STATUS.read_text())
        d["enabled"] = False
        d["running"] = False
        d["mode"] = "manual_only"
        d["message"] = "Refresco automático desactivado. El análisis solo corre al pulsar Analizar."
        return d
    except Exception:
        return {
            "enabled": False,
            "running": False,
            "mode": "manual_only",
            "companies": [],
            "log": [],
            "total_sweeps": 0,
            "message": "Refresco automático desactivado. El análisis solo corre al pulsar Analizar.",
        }


# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/live")
def api_live():
    """Endpoint principal: todo lo necesario para el dashboard en una llamada."""
    runs = _all_runs()
    requested_run_id = (request.args.get("run_id") or "").strip()
    requested_pipeline_id = (request.args.get("pipeline_id") or "").strip()
    requested_seed = _target_seed_lookup(requested_pipeline_id)
    if not runs:
        if requested_seed:
            return jsonify({
                "has_run": False,
                "pipeline_id": requested_pipeline_id,
                "display_status": "not_started",
                "target": _target_from_seed_record(requested_seed),
                "case_title": requested_seed.get("target_label", requested_pipeline_id),
            })
        return jsonify({
            "has_run": False,
            "pipeline_id": requested_pipeline_id,
        })

    active = _select_active_run(
        runs,
        requested_run_id=requested_run_id,
        requested_pipeline_id=requested_pipeline_id,
    )
    if active is None:
        if requested_seed:
            return jsonify({
                "has_run": False,
                "pipeline_id": requested_pipeline_id,
                "display_status": "not_started",
                "target": _target_from_seed_record(requested_seed),
                "case_title": requested_seed.get("target_label", requested_pipeline_id),
                "all_runs": runs[:8],
            })
        return jsonify({
            "has_run": False,
            "pipeline_id": requested_pipeline_id,
            "all_runs": runs[:8],
        })
    run_id  = active["run_id"]
    raw_run = _load_run(run_id)
    detail = _run_detail(run_id)
    motors = detail.get("motors", [])

    company  = _company_info(raw_run)
    target   = _target_info(raw_run)
    research = _research_activity(raw_run)
    ingestion = _canonicalize_ingestion_payload(_ingestion_activity(raw_run))
    focus    = _focus_activity(raw_run, motors)
    charts   = _chart_activity(raw_run)
    audit    = _audit_failures(run_id)
    pdf      = _pdf_for_run(
        raw_run,
        allow_global_fallback=not requested_run_id and not requested_pipeline_id,
    )
    pdf_variants = _pdf_variants_for_run(raw_run)
    display_status = _display_status(active["status"], pdf_available=pdf is not None)
    return jsonify({
        "has_run":     True,
        "run_id":      run_id,
        "status":      active["status"],
        "display_status": display_status,
        "case_title":  detail.get("case_title") or active.get("pipeline_id", ""),
        "pipeline_id": active.get("pipeline_id", ""),
        "started_at":  detail.get("started_at", ""),
        "duration_s":  detail.get("duration_s"),
        "error":       detail.get("error"),
        "summary":     detail.get("summary", {}),
        "report_type_trace": _canonicalize_report_type_trace(dict(raw_run.get("report_type_trace", {}) or {})),
        "phase_self_evaluation_summary": raw_run.get("phase_self_evaluation_summary", {}),
        "previous_run_id": raw_run.get("previous_run_id"),
        "case_delta_summary": raw_run.get("case_delta_summary", {}),
        "source_yield_memory_summary": raw_run.get("source_yield_memory_summary", {}),
        "next_ingestion_priority_update": raw_run.get("next_ingestion_priority_update", {}),
        "ingestion_learning_summary": raw_run.get("ingestion_learning_summary", {}),
        "motor_overview": detail.get("motor_overview", {}),
        "motors":      motors,
        "target":      target,
        "company":     company,
        "research":    research,
        "ingestion":   ingestion,
        "focus":       focus,
        "charts":      charts,
        "audit":       audit,
        "pdf":         pdf,
        "pdf_variants": pdf_variants,
        "requested_pipeline_id": requested_pipeline_id,
        "all_runs":    runs[:8],
    })


@app.route("/api/latest-pdf")
def api_latest_pdf():
    pdf = _latest_pdf()
    if not pdf:
        return jsonify({"available": False})
    return jsonify({"available": True, **pdf})


@app.route("/api/serve-pdf/<path:pdf_path>")
def api_serve_pdf(pdf_path: str):
    full = Path("/" + pdf_path)
    if not full.exists() or full.suffix.lower() != ".pdf":
        return jsonify({"error": "no encontrado"}), 404
    return send_file(str(full), mimetype="application/pdf")


@app.route("/api/open-pdf/<path:pdf_path>")
def api_open_pdf(pdf_path: str):
    full = "/" + pdf_path
    if Path(full).exists():
        subprocess.Popen(["open", full])
        return jsonify({"ok": True})
    return jsonify({"ok": False})


@app.route("/api/start-run", methods=["POST"])
def api_start_run():
    data        = request.get_json() or {}
    pipeline_id = (data.get("pipeline_id") or "default").strip()
    inputs_file = _resolve_inputs_file(pipeline_id, (data.get("inputs_file") or "").strip())
    no_cache    = bool(data.get("no_cache", True))

    existing_runs = _runs_for_pipeline(pipeline_id)
    running_existing = next((r for r in existing_runs if r.get("status") == "running"), None)
    if running_existing is not None:
        return jsonify({
            "ok": True,
            "already_running": True,
            "pipeline_id": pipeline_id,
            "inputs_file": inputs_file,
            "no_cache": no_cache,
            "run_id": running_existing.get("run_id", ""),
            "message": "Ya existe un run activo para este target.",
        })

    cmd = [sys.executable, str(_HERE / "cli.py"), "run", f"--pipeline-id={pipeline_id}"]
    if inputs_file and Path(inputs_file).exists():
        cmd += [f"--inputs={inputs_file}"]
    if no_cache:
        cmd += ["--no-cache"]
    try:
        _LAUNCH_LOG_DIR.mkdir(parents=True, exist_ok=True)
        launch_started_at = time.time()
        known_run_ids = {r.get("run_id", "") for r in _runs_for_pipeline(pipeline_id)}
        log_path = _LAUNCH_LOG_DIR / f"{pipeline_id}_{int(launch_started_at)}.log"
        log_handle = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            cmd,
            cwd=str(_HERE),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        log_handle.close()

        observed_run_id = ""
        deadline = time.time() + 5.0
        while time.time() < deadline:
            new_runs = [
                r for r in _runs_for_pipeline(pipeline_id)
                if r.get("run_id", "") not in known_run_ids
            ]
            if new_runs:
                observed_run_id = new_runs[0].get("run_id", "")
                break
            if proc.poll() is not None:
                break
            time.sleep(0.15)

        if not observed_run_id and proc.poll() is not None:
            return jsonify({
                "ok": False,
                "error": "El proceso terminó antes de registrar el run.",
                "pipeline_id": pipeline_id,
                "inputs_file": inputs_file,
                "launch_log": str(log_path),
                "log_tail": _tail_text(log_path),
                "returncode": proc.returncode,
            }), 500

        if not observed_run_id:
            return jsonify({
                "ok": False,
                "error": "No apareció un run nuevo en el registro dentro del tiempo esperado.",
                "pipeline_id": pipeline_id,
                "inputs_file": inputs_file,
                "launch_log": str(log_path),
                "log_tail": _tail_text(log_path),
                "pid": proc.pid,
            }), 500

        return jsonify({
            "ok": True,
            "pid": proc.pid,
            "pipeline_id": pipeline_id,
            "inputs_file": inputs_file,
            "no_cache": no_cache,
            "run_id": observed_run_id,
            "launch_log": str(log_path),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/create-target", methods=["POST"])
def api_create_target():
    data = request.get_json() or {}
    address = str(data.get("address") or "").strip()
    if not address:
        return jsonify({"ok": False, "error": "Address is required."}), 400
    target_type = str(data.get("target_type") or "commercial_building").strip() or "commercial_building"
    pipeline = build_address_seed(
        address_raw=address,
        target_type=target_type,
        owner_name=str(data.get("owner_name") or "").strip(),
        owner_ticker=str(data.get("owner_ticker") or "").strip(),
        owner_cik=str(data.get("owner_cik") or "").strip(),
        sector=str(data.get("sector") or "").strip(),
        sic=str(data.get("sic") or "").strip(),
        decision_intent=str(data.get("decision_intent") or "target_identification_required").strip(),
        report_intent="decision_admissibility_brief",
    )
    path = write_seed_file(_HERE / "inputs", pipeline, stem_hint=str(data.get("stem") or "").strip())
    target_definition = pipeline.get("target_definition_contract", {})
    year = str(pipeline.get("case_id", "")).split("-")[-1]
    pipeline_id = f"{target_definition.get('target_id', 'target')}-{year}"
    return jsonify({
        "ok": True,
        "pipeline_id": pipeline_id,
        "inputs_file": str(path),
        "target_id": target_definition.get("target_id", ""),
        "target_type": target_definition.get("target_type", ""),
        "target_label": target_definition.get("target_label", address),
    })
@app.route("/api/targets")
@app.route("/api/companies")
def api_targets():
    """Lista de target seeds físicos con su último run."""
    seeds = _target_seed_records()
    if not seeds:
        return jsonify([])
    runs = _all_runs()
    # Indexar runs por pipeline_id
    run_by_pid: dict = {}
    for r in runs:
        if not r.get("is_full_framework_run"):
            continue
        pid = r.get("pipeline_id", "")
        if pid not in run_by_pid:
            run_by_pid[pid] = r
    result = []
    for seed in seeds:
        pid_key = seed.get("pipeline_id", "")
        aliases = [pid_key, *seed.get("pipeline_aliases", [])]
        run = next((run_by_pid.get(alias) for alias in aliases if run_by_pid.get(alias)), None)
        inp_file = Path(seed.get("inputs_file", ""))
        run_pdf = _pdf_for_run(_load_run(run.get("run_id", "")), allow_global_fallback=False) if run else None
        last_run_status = run.get("status") if run else None
        result.append({
            "ticker":      seed.get("ticker", ""),
            "name":        seed.get("target_label", pid_key),
            "target_label": seed.get("target_label", pid_key),
            "target_address": seed.get("target_address", ""),
            "target_type": seed.get("target_type", ""),
            "target_id": seed.get("target_id", ""),
            "target_slug": seed.get("target_slug", ""),
            "subject_kind": seed.get("subject_kind", ""),
            "owner_name": seed.get("owner_name", ""),
            "target_code": seed.get("target_code", ""),
            "sector":      seed.get("context_line", ""),
            "has_inputs":  inp_file.exists(),
            "last_run":    last_run_status,
            "last_run_display_status": _display_status(last_run_status or "unknown", pdf_available=run_pdf is not None) if run else "not_started",
            "last_run_report_ready": bool(run_pdf),
            "last_run_id": run.get("run_id") if run else None,
            "pipeline_id": pid_key,
            "pipeline_aliases": seed.get("pipeline_aliases", []),
            "inputs_file": str(inp_file) if inp_file.exists() else "",
        })
    return jsonify(result)


@app.route("/api/financials/<run_id>")
def api_financials(run_id: str):
    """Compat: devuelve research + charts en vez de la vista financiera vieja."""
    raw_run = _load_run(run_id)
    company = _company_info(raw_run)
    return jsonify({
        "company": company,
        "research": _research_activity(raw_run),
        "charts": _chart_activity(raw_run),
    })


@app.route("/api/source-refresh")
def api_source_refresh():
    return jsonify(_source_refresh_status())


@app.route("/api/source-refresh/control", methods=["POST"])
def api_source_refresh_control():
    return jsonify({
        "ok": False,
        "enabled": False,
        "mode": "manual_only",
        "error": "El refresco automático está desactivado. El análisis solo se ejecuta manualmente por target.",
    }), 403


# ── HTML ──────────────────────────────────────────────────────────────────────

_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZLab — Monitor</title>
<style>
:root{
  --bg:#f7f7f8;--surface:#fff;--border:#e4e4e7;--text:#18181b;--text2:#3f3f46;
  --muted:#71717a;--faint:#a1a1aa;--accent:#2563eb;--green:#16a34a;
  --red:#dc2626;--amber:#b45309;
  --blue-bg:#eff6ff;--green-bg:#f0fdf4;--red-bg:#fef2f2;--amber-bg:#fffbeb;
  --blue-bd:#bfdbfe;--green-bd:#bbf7d0;--red-bd:#fecaca;--amber-bd:#fde68a;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;font-size:13px;line-height:1.5;}

/* ── Header ── */
#hdr{position:sticky;top:0;z-index:20;height:48px;padding:0 16px;
  background:rgba(255,255,255,.94);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;}
.logo{font-size:14px;font-weight:700;letter-spacing:-.3px;}
.logo-sub{font-size:12px;color:var(--muted);font-weight:400;}
#hdr-right{display:flex;align-items:center;gap:8px;}
.pill{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;
  font-size:11px;font-weight:500;border:1px solid var(--border);background:var(--surface);color:var(--muted);}
.pill .dot{width:6px;height:6px;border-radius:50%;background:var(--faint);}
.pill.running{border-color:var(--blue-bd);color:var(--accent);background:var(--blue-bg);}
.pill.running .dot{background:var(--accent);animation:blink 1.4s infinite;}
.pill.done{border-color:var(--green-bd);color:var(--green);background:var(--green-bg);}
.pill.done .dot{background:var(--green);}
.pill.warn{border-color:var(--amber-bd);color:var(--amber);background:var(--amber-bg);}
.pill.warn .dot{background:var(--amber);}
.pill.fail{border-color:var(--red-bd);color:var(--red);background:var(--red-bg);}
.pill.fail .dot{background:var(--red);}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}

/* ── Layout ── */
#body{display:flex;height:calc(100vh - 48px);overflow:hidden;}

/* Sidebar targets */
#sidebar{width:240px;flex-shrink:0;border-right:1px solid var(--border);
  background:var(--surface);display:flex;flex-direction:column;overflow:hidden;}
#sb-hdr{padding:12px 14px;border-bottom:1px solid var(--border);flex-shrink:0;}
#sb-hdr .sb-title{font-size:10.5px;font-weight:700;text-transform:uppercase;
  letter-spacing:.07em;color:var(--muted);margin-bottom:8px;}
#sb-search{width:100%;padding:6px 10px;border:1px solid var(--border);border-radius:7px;
  font-size:12px;background:var(--bg);color:var(--text);outline:none;}
#sb-search:focus{border-color:var(--accent);}
#sb-list{flex:1;overflow-y:auto;}
.sb-item{padding:9px 14px;border-bottom:1px solid #f4f4f5;cursor:pointer;
  transition:background .1s;display:flex;align-items:center;gap:8px;}
.sb-item:hover{background:var(--bg);}
.sb-item.active{background:var(--blue-bg);border-left:3px solid var(--accent);}
.sb-code{font-size:10px;font-weight:700;color:var(--muted);width:38px;flex-shrink:0;
  letter-spacing:.08em;text-transform:uppercase;}
.sb-info{flex:1;min-width:0;}
.sb-name{font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.sb-sector{font-size:10px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.sb-meta{font-size:10px;color:var(--faint);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;}
.sb-status{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.ss-done{background:var(--green);}
.ss-partial{background:var(--amber);}
.ss-failed{background:var(--red);}
.ss-pending{background:var(--faint);}
.ss-running{background:var(--accent);animation:blink 1s infinite;}
#sb-footer{padding:10px 14px;border-top:1px solid var(--border);flex-shrink:0;}

/* Main content */
#main{flex:1;min-width:0;display:flex;flex-direction:column;overflow:hidden;}

/* Hero target */
#hero{padding:18px 20px 14px;border-bottom:1px solid var(--border);
  background:var(--surface);display:flex;align-items:flex-start;
  justify-content:space-between;gap:16px;flex-shrink:0;}
#hero-left{flex:1;min-width:0;}
#hero-tag{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;
  color:var(--faint);margin-bottom:4px;}
#hero-name{font-size:32px;font-weight:800;letter-spacing:-1px;line-height:1.1;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
#hero-sub{font-size:13px;color:var(--muted);margin-top:5px;}
#hero-badge{margin-top:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
#hero-right{display:flex;gap:8px;align-items:flex-start;flex-shrink:0;}
#btn-run{padding:11px 22px;background:var(--text);color:#fff;border:none;
  border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;}
#btn-run:hover{opacity:.84;}
#btn-run:disabled{opacity:.4;cursor:not-allowed;}
.e-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;
  border-radius:20px;font-size:11px;font-weight:600;}
.eb-running{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);}
.eb-done{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
.eb-failed{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}
.eb-stub{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.eb-failed{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}
.eb-warn{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.eb-idle{background:#f4f4f5;color:var(--muted);border:1px solid var(--border);}

/* Content area */
#content{flex:1;overflow-y:auto;padding:18px 20px;display:flex;flex-direction:column;gap:14px;}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px;}
.card-title{font-size:10.5px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);margin-bottom:12px;}
.card-hdr{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px;}
.card-sub{font-size:11px;color:var(--muted);}

.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-bottom:14px;}
.stat-card{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px 12px;}
.stat-val{font-size:18px;font-weight:800;letter-spacing:-.03em;}
.stat-lbl{font-size:10.5px;color:var(--muted);margin-top:2px;text-transform:uppercase;letter-spacing:.05em;}

/* Motores */
.prog-track{height:5px;background:#f0f0f0;border-radius:3px;overflow:hidden;margin-bottom:10px;}
.prog-fill{height:100%;border-radius:3px;transition:width .6s;}
.prog-fill.s-running{background:linear-gradient(90deg,var(--accent),#60a5fa);animation:shimmer 2s infinite;}
.prog-fill.s-done{background:var(--green);}
.prog-fill.s-partial{background:var(--amber);}
.prog-fill.s-failed{background:var(--red);}
.prog-fill.s-failed{background:var(--red);}
@keyframes shimmer{0%,100%{opacity:1}50%{opacity:.7}}
.prog-row{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:6px;}
.motor-dots{display:flex;flex-wrap:wrap;gap:4px;}
.mdot{width:26px;height:26px;border-radius:6px;display:flex;align-items:center;
  justify-content:center;font-size:8.5px;font-weight:700;cursor:default;
  transition:transform .12s;position:relative;user-select:none;}
.mdot:hover{transform:scale(1.4);z-index:10;}
.mdot::after{content:attr(data-tip);position:absolute;bottom:115%;left:50%;
  transform:translateX(-50%);background:var(--text);color:#fff;white-space:nowrap;
  font-size:10px;padding:3px 8px;border-radius:5px;opacity:0;pointer-events:none;transition:opacity .12s;}
.mdot:hover::after{opacity:1;}
.md-completed{background:#dcfce7;color:#15803d;}
.md-cached{background:#dbeafe;color:#1d4ed8;}
.md-stub{background:#fef9c3;color:#a16207;}
.md-failed{background:#fee2e2;color:var(--red);}
.md-running{background:#dbeafe;color:var(--accent);animation:blink 1s infinite;}
.md-missing{background:#f4f4f5;color:var(--faint);}
.md-unknown{background:#f4f4f5;color:var(--faint);}

/* Fuentes */
.sources-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px;}
.src-item{display:flex;align-items:flex-start;gap:8px;padding:9px 11px;
  border-radius:7px;background:#fafafa;border:1px solid var(--border);}
.src-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:3px;}
.sd-found{background:var(--green);}
.sd-ok{background:var(--green);}
.sd-no_data{background:var(--amber);}
.sd-untracked{background:var(--faint);}
.sd-enriched{background:var(--accent);}
.sd-proposed{background:var(--faint);}
.sd-failed{background:var(--red);}
.src-body{flex:1;min-width:0;}
.src-name{font-size:12px;font-weight:600;}
.src-val{font-size:11px;color:var(--muted);margin-top:1px;}
.src-meta{font-size:10.5px;color:var(--faint);margin-top:2px;line-height:1.4;}

.chart-list{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.chart-item{padding:10px 12px;border-radius:8px;background:#fafafa;border:1px solid var(--border);}
.chart-name{font-size:12px;font-weight:700;}
.chart-meta{font-size:10.5px;color:var(--muted);margin-top:2px;line-height:1.4;}

/* Auditoría */
.audit-ok{display:flex;align-items:center;gap:10px;padding:12px 14px;
  background:var(--green-bg);border:1px solid var(--green-bd);border-radius:8px;
  font-size:13px;font-weight:500;color:var(--green);}
.audit-fail{padding:11px 14px;border-radius:8px;margin-bottom:8px;border-left:3px solid;}
.af-error{border-color:var(--red);background:var(--red-bg);}
.af-warning{border-color:var(--amber);background:var(--amber-bg);}
.af-type{font-size:10.5px;font-weight:700;text-transform:uppercase;margin-bottom:3px;}
.af-error .af-type{color:var(--red);}
.af-warning .af-type{color:var(--amber);}
.af-msg{font-size:12px;color:var(--text2);}

/* LLM */
.llm-note{font-size:12px;color:var(--accent);background:var(--blue-bg);
  border:1px solid var(--blue-bd);border-radius:7px;padding:9px 12px;margin-bottom:10px;}
.llm-table{width:100%;border-collapse:collapse;}
.llm-table tr{border-bottom:1px solid #f4f4f5;}
.llm-table tr:last-child{border-bottom:none;}
.llm-table td{padding:8px 6px;vertical-align:top;}
.lt-num{font-size:10px;font-family:monospace;color:var(--faint);width:36px;padding-top:10px;}
.lt-label{font-size:12.5px;font-weight:600;}
.lt-snippet{font-size:11px;color:var(--muted);margin-top:2px;line-height:1.5;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.lt-status{text-align:right;padding-top:8px;}
.st-badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700;white-space:nowrap;}
.st-completed{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
.st-completed_real{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
.st-cached{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);}
.st-cached_real{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);}
.st-running{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);animation:blink 1s infinite;}
.st-stub{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.st-cached_stub,.st-completed_stub{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.st-failed{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}
.st-pending,.st-missing,.st-skipped{background:#f4f4f5;color:var(--faint);border:1px solid var(--border);}

/* PDF panel */
#right{width:38%;max-width:520px;min-width:240px;border-left:1px solid var(--border);
  background:var(--surface);display:flex;flex-direction:column;flex-shrink:0;}
#pdf-hdr{padding:12px 16px;border-bottom:1px solid var(--border);flex-shrink:0;
  display:flex;align-items:center;justify-content:space-between;}
.pdf-title{font-size:12.5px;font-weight:600;}
.pdf-sub{font-size:11px;color:var(--muted);margin-top:1px;}
.pdf-empty{font-size:13px;font-weight:600;color:var(--muted);}
.pdf-actions{display:flex;align-items:center;gap:8px;}
.lang-sel{display:none;align-items:center;gap:4px;padding:3px;background:#f4f4f5;border:1px solid var(--border);border-radius:8px;}
.lang-btn{border:none;background:transparent;color:var(--muted);padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;cursor:pointer;}
.lang-btn.active{background:var(--surface);color:var(--text);box-shadow:0 1px 2px rgba(0,0,0,.06);}
.lang-btn:hover{color:var(--text);}
.btn-ext{font-size:11px;padding:5px 11px;border:1px solid var(--border);
  border-radius:6px;background:var(--surface);color:var(--text2);cursor:pointer;}
.btn-ext:hover{background:#f4f4f5;}
#pdf-frame{flex:1;border:none;background:#e8e8e8;}
#pdf-ph{flex:1;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:10px;padding:30px;text-align:center;color:var(--faint);}
.ph-icon{font-size:36px;}
.ph-title{font-size:14px;font-weight:600;color:var(--muted);}
.ph-sub{font-size:12px;line-height:1.6;}

/* Modal */
#modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.3);backdrop-filter:blur(4px);
  z-index:50;display:none;align-items:center;justify-content:center;}
#modal-bg.open{display:flex;}
#modal{background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:24px;width:420px;max-width:95vw;box-shadow:0 20px 60px rgba(0,0,0,.12);}
.modal-title{font-size:16px;font-weight:700;margin-bottom:4px;}
.modal-sub{font-size:12px;color:var(--muted);margin-bottom:18px;}
.field{margin-bottom:13px;}
.field label{display:block;font-size:12px;font-weight:600;margin-bottom:5px;}
.field .hint{font-size:11px;color:var(--muted);margin-top:3px;}
.field input[type=text]{width:100%;padding:8px 10px;background:var(--bg);
  border:1px solid var(--border);border-radius:7px;font-size:13px;color:var(--text);outline:none;}
.field input[type=text]:focus{border-color:var(--accent);}
.field-check{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:12px;}
.field-check input{accent-color:var(--accent);}
.modal-btns{display:flex;gap:8px;margin-top:18px;}
.modal-ok{flex:1;padding:9px 0;background:var(--text);color:#fff;border:none;
  border-radius:7px;font-size:13px;font-weight:600;cursor:pointer;}
.modal-ok:hover{opacity:.85;}
.modal-ok:disabled{opacity:.4;cursor:not-allowed;}
.modal-cancel{padding:9px 16px;border:1px solid var(--border);border-radius:7px;
  background:var(--surface);font-size:13px;cursor:pointer;color:var(--text2);}
.modal-cancel:hover{background:#f4f4f5;}
#modal-msg{font-size:12px;padding:8px 12px;border-radius:7px;margin-top:10px;display:none;}
#modal-msg.ok{display:block;background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
#modal-msg.err{display:block;background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}

.empty{font-size:12px;color:var(--faint);padding:6px 0;}
.na-note{font-size:12px;color:var(--faint);text-align:center;padding:12px;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
</style>
</head>
<body>

<!-- Header -->
<div id="hdr">
  <div style="display:flex;align-items:center;gap:12px;">
    <span class="logo">ZLab <span class="logo-sub">Monitor</span></span>
    <div class="pill" id="status-pill"><span class="dot"></span><span id="status-txt">Cargando…</span></div>
  </div>
  <div id="hdr-right">
    <button class="btn-ext" onclick="openCreateModal()" style="font-weight:600">+ Registrar target</button>
  </div>
</div>

<div id="body">

<!-- Sidebar: lista de activos / targets -->
<div id="sidebar">
  <div id="sb-hdr">
    <div class="sb-title">Targets registrados</div>
    <input id="sb-search" type="text" placeholder="Buscar activo o dirección…" oninput="filterTargets(this.value)">
  </div>
  <div id="sb-list"><div style="padding:14px;color:var(--faint);font-size:12px">Cargando…</div></div>
  <div id="sb-footer">
    <button onclick="openCreateModal()" style="width:100%;padding:7px;background:var(--text);color:#fff;border:none;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;">+ Registrar target</button>
  </div>
</div>

<!-- Main -->
<div id="main">

  <!-- Hero: target principal -->
  <div id="hero">
    <div id="hero-left">
      <div id="hero-tag">Target seleccionado</div>
      <div id="hero-name">—</div>
      <div id="hero-sub"></div>
      <div id="hero-badge"></div>
    </div>
    <div id="hero-right">
      <button id="btn-run" onclick="correr()">▶ Iniciar investigación</button>
    </div>
  </div>

  <!-- Contenido -->
  <div id="content">

    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Investigación de fuentes por activo · motor_028</span>
        <span id="src-count" class="card-sub"></span>
      </div>
      <div class="stats-grid" id="research-stats"></div>
      <div class="llm-note" id="research-note" style="display:none;margin-bottom:12px"></div>
      <div class="sources-grid" id="sources-grid">
        <div class="empty">Sin datos aún — corre el framework para consultar las fuentes</div>
      </div>
    </div>

    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Admisibilidad de ingestión · motores 007 / 012 / 014</span>
        <span id="ingestion-count" class="card-sub"></span>
      </div>
      <div class="stats-grid" id="ingestion-stats"></div>
      <div class="llm-note" id="ingestion-classification" style="margin-bottom:12px"></div>
      <div class="llm-note" id="ingestion-learning" style="margin-bottom:12px"></div>
      <div class="sources-grid" id="ingestion-fields">
        <div class="empty">Sin registros de admisibilidad todavía</div>
      </div>
      <div class="chart-list" id="ingestion-evidence" style="margin-top:12px">
        <div class="empty">Sin evidencia mínima registrada todavía</div>
      </div>
      <div class="chart-list" id="ingestion-priorities" style="margin-top:12px">
        <div class="empty">Sin prioridades de siguiente ingesta todavía</div>
      </div>
    </div>

    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Motor de charts · motor_018</span>
        <span id="chart-count" class="card-sub"></span>
      </div>
      <div class="stats-grid" id="chart-stats"></div>
      <div class="chart-list" id="chart-list">
        <div class="empty">Sin datos del motor de charts todavía</div>
      </div>
    </div>

    <!-- Motores -->
    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Estado de los motores</span>
        <span id="motor-counts" class="card-sub"></span>
      </div>
      <div class="prog-row"><span id="prog-lbl">—</span><span id="prog-pct" style="font-weight:700">—</span></div>
      <div class="prog-track"><div class="prog-fill" id="prog-fill" style="width:0%"></div></div>
      <div class="motor-dots" id="motor-dots"></div>
    </div>

    <!-- LLM -->
    <div class="card">
      <div class="card-hdr"><span class="card-title">Motores críticos de análisis y reporte</span></div>
      <div class="llm-note" id="llm-note">Esta tabla ya no pretende describir “la IA” en abstracto. Resume los motores que más afectan análisis, charts y ensamblado del reporte.</div>
      <table class="llm-table" id="llm-table"></table>
    </div>

    <!-- Auditoría -->
    <div class="card">
      <div class="card-hdr"><span class="card-title">Auditoría — fallos detectados</span></div>
      <div id="audit-body"><div class="empty">Sin datos</div></div>
    </div>

  </div>
</div>

<!-- Panel derecho: PDF -->
<div id="right">
  <div id="pdf-hdr">
    <div>
      <div class="pdf-empty" id="pdf-title">Reporte generado</div>
      <div class="pdf-sub" id="pdf-sub">La investigación se inicia manualmente</div>
    </div>
    <div class="pdf-actions">
      <div class="lang-sel" id="pdf-lang-sel">
        <button class="lang-btn active" id="pdf-lang-en" onclick="selectPdfLanguage('en')">EN</button>
        <button class="lang-btn" id="pdf-lang-es" onclick="selectPdfLanguage('es')">ES</button>
      </div>
      <button class="btn-ext" id="btn-ext" onclick="openPdfExt()" style="display:none">Abrir ↗</button>
    </div>
  </div>
  <iframe id="pdf-frame" style="display:none;flex:1;border:none;"></iframe>
  <div id="pdf-ph">
    <div class="ph-icon">📄</div>
    <div class="ph-title">Sin reporte aún</div>
    <div class="ph-sub">El PDF aparecerá aquí<br>cuando inicies una investigación y termine el run.</div>
  </div>
</div>

</div><!-- #body -->

<!-- Modal -->
<div id="modal-bg" onclick="onBgClick(event)">
  <div id="modal">
    <div class="modal-title" id="modal-title">Registrar target</div>
    <div class="modal-sub" id="modal-sub">Crea el target primero. La investigación se lanza solo si tú lo indicas.</div>
    <div class="field">
      <label>Dirección del activo <span style="color:var(--muted);font-weight:400">(opcional si ya seleccionaste un target)</span></label>
      <input type="text" id="f-address" placeholder="ej. 5900 HIGHWAY 225, DEER PARK, TX, 77536">
      <div class="hint" id="modal-address-hint">Si rellenas esta dirección, el sistema registra un target nuevo. La investigación solo correrá si activas la opción de ejecutar inmediatamente.</div>
    </div>
    <div class="field">
      <label>Tipo de activo</label>
      <input type="text" id="f-target-type" list="target-type-options" placeholder="ej. oil_gas_downstream_facility">
      <datalist id="target-type-options">
        <option value="commercial_building">
        <option value="data_center">
        <option value="warehouse_distribution">
        <option value="industrial_plant">
        <option value="manufacturing_facility">
        <option value="food_processing_facility">
        <option value="cold_chain_facility">
        <option value="infrastructure_node">
        <option value="oil_gas_upstream_site">
        <option value="oil_gas_midstream_facility">
        <option value="oil_gas_downstream_facility">
      </datalist>
    </div>
    <div class="field">
      <label>Owner context <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
      <input type="text" id="f-owner-name" placeholder="Nombre del owner o operador si ya lo sabes">
    </div>
    <div class="field">
      <label>Ticker owner <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
      <input type="text" id="f-owner-ticker" placeholder="ej. PLD, BXP, NEE">
    </div>
    <div class="field">
      <label>ID del análisis</label>
      <input type="text" id="f-pid" placeholder="ej. esrt-2026">
    </div>
    <div class="field">
      <label>Archivo de entradas <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
      <input type="text" id="f-inputs" placeholder="Ruta al .json — se auto-completa si seleccionas un activo">
      <div class="hint">Deja vacío para usar las entradas del target seleccionado.</div>
    </div>
    <div class="field">
      <label class="field-check">
        <input type="checkbox" id="f-auto-run">
        Iniciar investigación inmediatamente después de guardar el target
      </label>
    </div>
    <div class="field">
      <label class="field-check">
        <input type="checkbox" id="f-nocache">
        Re-ejecutar todos los motores (sin caché)
      </label>
    </div>
    <div id="modal-msg"></div>
    <div class="modal-btns">
      <button class="modal-cancel" onclick="closeModal()">Cancelar</button>
      <button class="modal-ok" id="btn-launch" onclick="launchRun()">▶ Ejecutar ahora</button>
    </div>
  </div>
</div>

<script>
const ESTADO={completed:'Completado',completed_real:'Completado',completed_with_stubs:'Completado (parcial)',
  completed_partial:'Completado parcial',completed_no_pdf:'Completado sin PDF',partial:'Parcial',
  cached:'En caché',cached_real:'En caché',cached_stub:'Caché de stub',completed_stub:'Completado como stub',
  failed:'Fallido',running:'Ejecutando',stub:'Placeholder',skipped:'No corrido',missing:'Sin correr',
  not_started:'No investigado',unknown:'Desconocido'};
const FOCUS_COUNT=6;

let liveData=null, selectedRunId=null, selectedPipelineId=null, selectedInputsFile='', allTargets=[], lastPdfMtime=null, currentPdfPath=null, selectedTarget=null, currentPdfVariants={}, currentPdfLanguage='en', modalIntent='create';

async function init(){
  await Promise.all([refresh(), loadTargets()]);
  document.getElementById('f-address').addEventListener('input', updateLaunchButtonLabel);
  document.getElementById('f-auto-run').addEventListener('change', updateLaunchButtonLabel);
  setInterval(refresh,4000);
  setInterval(loadTargets,15000);
}

async function refresh(){
  try{
    let url='/api/live';
    if(selectedPipelineId)url=`/api/live?pipeline_id=${encodeURIComponent(selectedPipelineId)}`;
    else if(selectedRunId)url=`/api/live?run_id=${encodeURIComponent(selectedRunId)}`;
    const d=await fj(url); liveData=d;
    if(!selectedPipelineId&&d.pipeline_id)selectedPipelineId=d.pipeline_id;
    renderPill(d); renderHero(d); renderResearch(d); renderIngestion(d); renderChartEngine(d); renderMotores(d); renderLLM(d); renderAuditoria(d);
    renderPdf(d.pdf,pdfPlaceholderFor(d),d.pdf_variants||{});
  }catch(e){console.warn(e);}
}

async function fj(u){return(await fetch(u)).json();}

function displayState(d){return d.display_status||d.status||'unknown';}

function pdfPlaceholderFor(d){
  const s=displayState(d);
  if(!d.has_run){
    if((d.target&&d.target.label)||selectedTarget?.name||selectedPipelineId){
      return 'Target registrado sin investigación. Iníciala manualmente cuando quieras.';
    }
    return 'Sin reporte aún';
  }
  if(s==='running')return `Ejecutando ${selectedTarget?.name||d.target?.label||d.pipeline_id||'análisis'}… el PDF aparecerá al finalizar este run.`;
  if(s==='completed_partial')return 'El framework terminó de forma parcial: hay placeholders contractuales activos y no debe leerse como cierre total.';
  if(s==='partial')return 'El framework terminó sin un entregable final íntegro. Revisa renderizado, exportación y trazabilidad del PDF.';
  if(s==='completed_no_pdf')return 'El análisis terminó pero no dejó un PDF renderizable. Revisa motor_016 y motor_017.';
  if(s==='failed')return 'El análisis falló antes de generar un PDF.';
  return 'Sin reporte aún';
}

// ── Pill ──────────────────────────────────────────────────────
function renderPill(d){
  const pill=document.getElementById('status-pill');
  const txt=document.getElementById('status-txt');
  if(!d.has_run){
    pill.className='pill';
    txt.textContent=((d.target&&d.target.label)||selectedTarget?.name||selectedPipelineId)?'No investigado':'Sin análisis';
    return;
  }
  const s=displayState(d);
  if(s==='running'){pill.className='pill running';txt.textContent='Ejecutando';}
  else if(s==='completed'){pill.className='pill done';txt.textContent='Completado';}
  else if(s==='completed_partial'||s==='completed_no_pdf'||s==='partial'){pill.className='pill warn';txt.textContent=ESTADO[s]||s;}
  else if(s==='failed'){pill.className='pill fail';txt.textContent='Fallido';}
  else{pill.className='pill';txt.textContent=ESTADO[s]||s;}
}

// ── Hero ──────────────────────────────────────────────────────
function renderHero(d){
  const tg=d.target||{};
  const co=d.company||{};
  const selectedName=selectedTarget?.name||'';
  const name=tg.label||selectedName||(d.has_run?(d.case_title||d.pipeline_id||''):'');
  document.getElementById('hero-name').textContent=name||'Sin activo seleccionado';
  const heroAddress=tg.address||selectedTarget?.target_address||'';
  const heroType=tg.target_type||selectedTarget?.target_type||'';
  const heroOwner=tg.owner_name||co.name||selectedTarget?.owner_name||'';
  document.getElementById('hero-sub').textContent=[heroAddress,heroType,heroOwner].filter(Boolean).join(' · ');
  const badge=document.getElementById('hero-badge');
  const btn=document.getElementById('btn-run');
  const samePipeline=!selectedPipelineId||selectedPipelineId===d.pipeline_id;
  if(d.has_run&&samePipeline){
    const s=displayState(d);
    let cls='eb-idle';
    if(s==='running')cls='eb-running';
    else if(s==='completed')cls='eb-done';
    else if(s==='completed_partial'||s==='completed_no_pdf'||s==='partial')cls='eb-warn';
    else if(s==='failed')cls='eb-failed';
    const dur=d.duration_s?(d.duration_s>60?`${Math.floor(d.duration_s/60)}m ${Math.round(d.duration_s%60)}s`:`${d.duration_s}s`):'';
    badge.innerHTML=`<span class="e-badge ${cls}">${ESTADO[s]||s}</span>${dur?`<span style="font-size:12px;color:var(--faint)">${dur}</span>`:''}`;
    if(s==='running'){btn.textContent='⏳ Ejecutando…';btn.disabled=true;}
    else{btn.innerHTML='▶ Iniciar investigación';btn.disabled=false;}
  }else{
    if(name||selectedPipelineId){
      badge.innerHTML='<span class="e-badge eb-idle">No investigado</span><span style="font-size:12px;color:var(--faint)">La investigación se lanza manualmente</span>';
    }else{
      badge.innerHTML='';
    }
    btn.innerHTML='▶ Iniciar investigación';btn.disabled=false;
  }
}

// ── Investigación de fuentes ───────────────────────────────────
function statCard(value,label){
  return `<div class="stat-card"><div class="stat-val">${esc(value)}</div><div class="stat-lbl">${esc(label)}</div></div>`;
}

function sourceStatusLabel(status){
  const map={
    found:'Con datos',
    no_data:'Sin datos',
    failed:'Falló',
    context_missing:'Contexto insuficiente',
    not_applicable:'No aplicable',
    untracked:'Sin rastro',
    proposed:'Propuesto'
  };
  return map[status]||status;
}

function sourceScopeLabel(scope){
  const map={
    entity_level:'entity-level',
    issuer_specific:'issuer-specific',
    asset_jurisdiction_specific:'asset/jurisdiction-specific',
    market_signal:'market-signal',
    energy_environment_context:'energy/environment',
    macro_context:'macro-context',
    extended_context:'extended-context'
  };
  return map[scope]||scope||'';
}

function renderResearch(d){
  const research=d.research||{};
  const summary=research.summary||{};
  const attempts=research.attempts||[];
  const grid=document.getElementById('sources-grid');
  const cnt=document.getElementById('src-count');
  const stats=document.getElementById('research-stats');
  const note=document.getElementById('research-note');
  cnt.textContent=summary.contract_total?`${summary.applicable_contract_total??summary.contract_total}/${summary.contract_total} fuentes aplicables/contractuales`:'';
  stats.innerHTML=[
    statCard(summary.contract_total??'—','Contrato'),
    statCard(summary.applicable_contract_total??'—','Aplicables'),
    statCard(summary.attempted??'—','Intentos trazados'),
    statCard(summary.found??'—','Con datos'),
    statCard(summary.admitted??'—','Admitidas'),
    statCard(summary.no_data??'—','Sin datos'),
    statCard(summary.failed??'—','Fallidas'),
    statCard(summary.context_missing??'—','Contexto insuficiente'),
    statCard(summary.not_applicable??'—','No aplicables'),
    statCard(summary.untracked??'—','Sin rastro'),
  ].join('');
  if(research.note){
    note.style.display='block';
    note.textContent=research.note;
  }else{
    note.style.display='none';
    note.textContent='';
  }
  if(!attempts.length){
    grid.innerHTML='<div class="empty">Sin fuentes consultadas aún. Ejecuta el framework.</div>';return;
  }
  const dc=s=>(s==='found'||s==='ok'||s==='enriched'||s==='accepted')
    ?'sd-found'
    :(s==='failed')
      ?'sd-failed'
      :(s==='no_data')
        ?'sd-no_data'
        :'sd-untracked';
  grid.innerHTML=attempts.map(s=>`
    <div class="src-item">
      <span class="src-dot ${dc(s.status)}"></span>
      <div class="src-body">
        <div class="src-name">${esc(s.label||s.source_type||'Fuente')}</div>
        <div class="src-val">${esc(sourceStatusLabel(s.status))}${s.family?` · ${esc(s.family)}`:''}${s.source_scope?` · ${esc(sourceScopeLabel(s.source_scope))}`:''}${s.lifecycle_stage?` · ${esc(s.lifecycle_stage)}`:''}</div>
        ${s.locator?`<div class="src-meta">${esc(s.locator)}</div>`:''}
        ${s.discovery_reason?`<div class="src-meta">${esc(s.discovery_reason)}</div>`:''}
        ${(s.error||s.detail)?`<div class="src-meta">${esc(s.error||s.detail)}</div>`:''}
      </div>
    </div>`).join('');
}

function renderIngestion(d){
  const ing=d.ingestion||{};
  const summary=ing.summary||{};
  const cls=ing.classification||{};
  const learning=ing.learning||{};
  const learningSummary=learning.summary||{};
  const caseDelta=learning.case_delta_summary||{};
  const yieldSummary=learning.source_yield_memory_summary||{};
  const nextUpdate=learning.next_ingestion_priority_update||{};
  const stats=document.getElementById('ingestion-stats');
  const info=document.getElementById('ingestion-classification');
  const learn=document.getElementById('ingestion-learning');
  const fields=document.getElementById('ingestion-fields');
  const evidence=document.getElementById('ingestion-evidence');
  const priorities=document.getElementById('ingestion-priorities');
  const cnt=document.getElementById('ingestion-count');
  const reportTrace=cls.report_type_trace||{};
  const selfEval=cls.phase_self_evaluation_summary||{};
  if(!ing.available){
    cnt.textContent='';
    stats.innerHTML='';
    info.textContent='Sin registros de ingestión todavía.';
    learn.textContent='Sin memoria de aprendizaje todavía.';
    fields.innerHTML='<div class="empty">Sin campos bloqueantes registrados</div>';
    evidence.innerHTML='<div class="empty">Sin evidencia mínima registrada</div>';
    priorities.innerHTML='<div class="empty">Sin prioridades de siguiente ingesta</div>';
    return;
  }
  cnt.textContent=`${summary.sources_accepted||0}/${summary.sources_total||0} fuentes aceptadas · ${summary.blocking_fields_total||0} campos bloqueantes`;
  stats.innerHTML=[
    statCard(cls.target_type||'—','Target type'),
    statCard(cls.recommended_report_type||'—','Reporte recomendado'),
    statCard(reportTrace.final_published_report_type||cls.report_identity_state||'—','Reporte final'),
    statCard(summary.sources_accepted??'—','Fuentes aceptadas'),
    statCard(summary.sources_rejected??'—','Fuentes rechazadas'),
    statCard(summary.blocking_fields_total??'—','Campos bloqueantes'),
    statCard(summary.missing_evidence_total??'—','Evidencia faltante'),
    statCard(learningSummary.net_progress_state||'—','Delta'),
    statCard(learningSummary.priority_count??'—','Próx. ingesta'),
  ].join('');
  const scopeBits=Object.entries(summary.scope_counts||{}).map(([k,v])=>`${k}: ${v}`).join(' · ');
  info.textContent=[
    `Clasificación: ${cls.target_type||'—'} (${cls.classification_confidence||'—'})`,
    `Admisibilidad: ${cls.target_admissibility_state||'—'}`,
    `Readiness: ${cls.technical_substrate_readiness||'—'}`,
    reportTrace.early_report_type_gate?`Trace: ${reportTrace.early_report_type_gate} → ${reportTrace.final_published_report_type||cls.report_identity_state||'—'}`:'',
    selfEval.overall_result?`Autoeval: ${selfEval.overall_result} (${selfEval.resolved||0}/${selfEval.total_phases||0} resolved)`:'',
    `Ingestion status: ${cls.ingestion_contract_status||'—'}`,
    scopeBits?`Scopes: ${scopeBits}`:''
  ].filter(Boolean).join(' | ');
  learn.textContent=[
    learningSummary.previous_run_id?`Run previo: ${learningSummary.previous_run_id}`:'Primera corrida con memoria inter-ingesta.',
    learningSummary.net_progress_state?`Delta: ${learningSummary.net_progress_state}`:'',
    `Fuentes productivas: ${yieldSummary.productive_source_count??0}/${yieldSummary.sources_evaluated??0}`,
    nextUpdate.top_priority_action?`Acción top: ${nextUpdate.top_priority_action}`:'',
    (caseDelta.progress_signals||[]).length?`Señales+: ${(caseDelta.progress_signals||[]).slice(0,3).join(', ')}`:'',
    (caseDelta.regression_signals||[]).length?`Señales-: ${(caseDelta.regression_signals||[]).slice(0,3).join(', ')}`:''
  ].filter(Boolean).join(' | ');
  const blocking=ing.blocking_fields||[];
  if(!blocking.length){
    fields.innerHTML='<div class="empty">Sin campos bloqueantes registrados</div>';
  }else{
    fields.innerHTML=blocking.map(row=>`
      <div class="src-item">
        <span class="src-dot sd-failed"></span>
        <div class="src-body">
          <div class="src-name">${esc(row.field||'Field')}</div>
          <div class="src-val">${esc(row.admissibility||'')} · ${esc(row.scope||'')}</div>
          ${row.notes?`<div class="src-meta">${esc(row.notes)}</div>`:''}
        </div>
      </div>`).join('');
  }
  const missing=ing.missing_evidence||[];
  if(!missing.length){
    evidence.innerHTML='<div class="empty">Sin evidencia mínima registrada</div>';
  }else{
    evidence.innerHTML=missing.map(row=>`
      <div class="chart-item">
        <div class="chart-name">${esc(row.missing_field||'Campo faltante')}</div>
        ${row.minimum_evidence_needed?`<div class="chart-meta">${esc(row.minimum_evidence_needed)}</div>`:''}
        ${row.suggested_source?`<div class="chart-meta">Fuente sugerida: ${esc(row.suggested_source)}</div>`:''}
      </div>`).join('');
  }
  const priorityRows=nextUpdate.priorities||[];
  if(!priorityRows.length){
    priorities.innerHTML='<div class="empty">Sin prioridades de siguiente ingesta</div>';
  }else{
    priorities.innerHTML=priorityRows.slice(0,5).map(row=>`
      <div class="chart-item">
        <div class="chart-name">${esc(row.priority_rank||'')} · ${esc(row.action_type||'Acción')}</div>
        ${row.target?`<div class="chart-meta">${esc(row.target)}</div>`:''}
        ${row.reason?`<div class="chart-meta">${esc(row.reason)}</div>`:''}
        ${row.expected_unlock?`<div class="chart-meta">Desbloquea: ${esc(row.expected_unlock)}</div>`:''}
        ${row.basis?`<div class="chart-meta">Base: ${esc(row.basis)}</div>`:''}
      </div>`).join('');
  }
}

function renderChartEngine(d){
  const charts=d.charts||{};
  const assets=charts.assets||[];
  const errors=charts.errors||[];
  document.getElementById('chart-count').textContent=`${charts.total_charts||0} charts · ${errors.length||0} errores`;
  document.getElementById('chart-stats').innerHTML=[
    statCard(ESTADO[charts.status]||charts.status||'Sin correr','Estado'),
    statCard(charts.total_charts||0,'Charts'),
    statCard(errors.length||0,'Errores'),
    statCard(charts.adapter_class||'—','Adapter'),
  ].join('');
  const list=document.getElementById('chart-list');
  if(!assets.length&&!errors.length){
    list.innerHTML='<div class="empty">motor_018 no dejó charts trazables en este run.</div>';
    return;
  }
  list.innerHTML=[
    ...assets.map(asset=>`
      <div class="chart-item">
        <div class="chart-name">${esc(asset.title||asset.asset_id||'Chart')}</div>
        ${asset.section_hint?`<div class="chart-meta">${esc(asset.section_hint)}</div>`:''}
        ${asset.description?`<div class="chart-meta">${esc(asset.description)}</div>`:''}
      </div>`),
    ...errors.map(err=>`
      <div class="chart-item">
        <div class="chart-name">Error</div>
        <div class="chart-meta">${esc(typeof err==='string'?err:JSON.stringify(err))}</div>
      </div>`),
  ].join('');
}

// ── Motores ────────────────────────────────────────────────────
function renderMotores(d){
  const motors=d.motors||[];
  const ov=d.motor_overview||{};
  const total=ov.total_expected||motors.length||34;
  const implemented=ov.implemented_contract||Math.max(total-(ov.placeholder_contract||0),0);
  const healthy=(ov.completed_real||0)+(ov.cached_real||0);
  const active=healthy+(ov.running_real||0)+(ov.failed_real||0);
  const pct=implemented?Math.round(active/implemented*100):0;
  const s=displayState(d);
  document.getElementById('prog-lbl').textContent=`${healthy} motores reales listos · ${(ov.running_real||0)} corriendo · ${(ov.pending_real||0)} pendientes · ${(ov.placeholder_contract||0)} placeholder contractuales · ${(ov.failed_real||0)} reales fallidos`;
  document.getElementById('prog-pct').textContent=`${pct}%`;
  document.getElementById('motor-counts').textContent=total?`${total} motores contractuales · ${implemented} implementados · ${(ov.placeholder_contract||0)} placeholder`:'';
  const fill=document.getElementById('prog-fill');
  fill.style.width=pct+'%';
  fill.className='prog-fill '+(s==='running'?'s-running':s==='completed_partial'||s==='completed_no_pdf'||s==='partial'?'s-partial':((ov.failed||0)>0||s==='failed')?'s-failed':'s-done');
  const dotsEl=document.getElementById('motor-dots');
  if(!motors.length){dotsEl.innerHTML='<div class="empty">Sin datos — corre el framework</div>';return;}
  dotsEl.innerHTML=motors.map(m=>{
    const num=m.motor_id.replace('motor_','');
    const st=m.status||'unknown';
    const dur=m.duration_ms!=null?(m.duration_ms<1000?Math.round(m.duration_ms)+'ms':(m.duration_ms/1000).toFixed(1)+'s'):(st==='cached'?'caché':'');
    const stub=m.is_stub?' · placeholder':'';
    const name=m.motor_name?` · ${m.motor_name}`:'';
    const adapter=m.adapter_class?` · ${m.adapter_class}`:'';
    return`<div class="mdot md-${st}" data-tip="M-${num}${name} · ${ESTADO[st]||st}${dur?' · '+dur:''}${stub}${adapter}">${num}</div>`;
  }).join('');
}

// ── Motores críticos ───────────────────────────────────────────
function renderLLM(d){
  const motors=d.motors||[];
  const total=motors.length||34;
  document.getElementById('llm-note').textContent=
    `Aquí se muestran ${FOCUS_COUNT} motores críticos para inferencia, charts y paquete de reporte. El panel completo del framework queda arriba; esta tabla resume solo la parte más sensible del pipeline.`;
  const llm=d.focus||[];
  const tbl=document.getElementById('llm-table');
  if(!llm.length){tbl.innerHTML='<tr><td class="empty">Sin datos aún</td></tr>';return;}
  const stLbl={completed:'Listo',cached:'En caché',running:'Ejecutando',stub:'Placeholder',failed:'Error',pending:'En espera',missing:'Sin correr'};
  tbl.innerHTML=llm.map(m=>{
    const st=m.status||'pending';
    const dur=m.duration_ms!=null?(m.duration_ms<1000?Math.round(m.duration_ms)+'ms':(m.duration_ms/1000).toFixed(1)+'s'):'';
    const snip=m.snippet?esc(m.snippet)+'…':'';
    return`<tr>
      <td class="lt-num">${m.motor_id.replace('motor_','M-')}</td>
      <td><div class="lt-label">${esc(m.label)}</div>${m.name?`<div class="lt-snippet">${esc(m.name)}</div>`:''}${snip?`<div class="lt-snippet">${snip}</div>`:''}</td>
      <td class="lt-status"><span class="st-badge st-${st}">${stLbl[st]||st}${dur?' · '+dur:''}</span></td>
    </tr>`;
  }).join('');
}

// ── Auditoría ──────────────────────────────────────────────────
function renderAuditoria(d){
  const el=document.getElementById('audit-body');
  const audit=d.audit||{};
  const fails=audit.failures||[];
  if(!d.has_run){el.innerHTML='<div class="empty">Sin análisis activo</div>';return;}
  if(!audit.available&&!fails.length){
    el.innerHTML='<div class="na-note">La auditoría aparecerá al finalizar el análisis (requiere motor_024).</div>';return;
  }
  if(!fails.length){el.innerHTML='<div class="audit-ok">✓ Sin fallos de auditoría detectados</div>';return;}
  el.innerHTML=fails.map(f=>`
    <div class="audit-fail ${f.severity==='warning'?'af-warning':'af-error'}">
      <div class="af-type">${esc(f.type)}</div>
      <div class="af-msg">${esc(f.message)}${f.motor?` <span style="color:var(--faint)">(${esc(f.motor)})</span>`:''}</div>
    </div>`).join('');
}

// ── Targets sidebar ───────────────────────────────────────────
async function loadTargets(){
  try{
    const data=await fj('/api/targets');
    allTargets=data;
    if(selectedPipelineId){
      selectedTarget=data.find(c=>c.pipeline_id===selectedPipelineId)||selectedTarget;
    }else if(liveData?.pipeline_id){
      selectedTarget=data.find(c=>c.pipeline_id===liveData.pipeline_id)||selectedTarget;
    }
    renderTargetList(data,'');
  }catch(e){}
}

function filterTargets(q){renderTargetList(allTargets,q);}

function renderTargetList(data,q){
  const el=document.getElementById('sb-list');
  const filtered=q?data.filter(c=>
    c.name.toLowerCase().includes(q.toLowerCase())||
    (c.target_address||'').toLowerCase().includes(q.toLowerCase())||
    (c.ticker||'').toLowerCase().includes(q.toLowerCase())||
    (c.owner_name||'').toLowerCase().includes(q.toLowerCase())||
    (c.sector||'').toLowerCase().includes(q.toLowerCase())
  ):data;
  if(!filtered.length){
    el.innerHTML='<div style="padding:14px;color:var(--faint);font-size:12px">Sin resultados</div>';return;
  }
  el.innerHTML=filtered.map(c=>{
    const active=selectedPipelineId===c.pipeline_id?'active':'';
    const ds=c.last_run_display_status||c.last_run||'unknown';
    const running=ds==='running';
    const done=ds==='completed';
    const partial=ds==='completed_partial'||ds==='completed_no_pdf'||ds==='partial';
    const failed=ds==='failed';
    const dotCls=running?'ss-running':done?'ss-done':partial?'ss-partial':failed?'ss-failed':'ss-pending';
    return`<div class="sb-item ${active}" onclick="selectTarget('${esc(c.pipeline_id)}','${esc(c.inputs_file||'')}','${esc(c.last_run_id||'')}')">
      <span class="sb-code">${esc(c.target_code||'TGT')}</span>
      <div class="sb-info">
        <div class="sb-name">${esc(c.target_label||c.name)}</div>
        <div class="sb-sector">${esc(c.target_address||c.sector||'')}</div>
        <div class="sb-meta">${esc(c.sector||'')}</div>
      </div>
      <span class="sb-status ${dotCls}" title="${esc(ESTADO[ds]||ds||'Sin analizar')}"></span>
    </div>`;
  }).join('');
}

function selectTarget(pipelineId,inputsFile,runId){
  selectedTarget=allTargets.find(c=>c.pipeline_id===pipelineId)||{pipeline_id:pipelineId,name:pipelineId};
  selectedPipelineId=pipelineId||null;
  selectedInputsFile=inputsFile||'';
  selectedRunId=null;
  document.getElementById('f-pid').value=pipelineId;
  document.getElementById('f-inputs').value=inputsFile;
  document.getElementById('f-nocache').checked=true;
  renderPdf(null, `Target ${selectedTarget?.name||pipelineId} seleccionado. La investigación sigue manual hasta que inicies un run.`, {});
  renderTargetList(allTargets,document.getElementById('sb-search').value||'');
  refresh();
}

// ── PDF ────────────────────────────────────────────────────────
function activePdfVariant(pdf, variants){
  const keys=Object.keys(variants||{});
  if(!keys.length)return pdf||null;
  if(currentPdfLanguage&&variants[currentPdfLanguage])return variants[currentPdfLanguage];
  if(variants.en)return variants.en;
  return variants[keys[0]];
}

function renderPdfLanguageSelector(variants){
  const sel=document.getElementById('pdf-lang-sel');
  const en=document.getElementById('pdf-lang-en');
  const es=document.getElementById('pdf-lang-es');
  const keys=Object.keys(variants||{});
  const hasEn=!!variants?.en;
  const hasEs=!!variants?.es;
  sel.style.display=keys.length>1?'inline-flex':'none';
  en.style.display=hasEn?'inline-block':'none';
  es.style.display=hasEs?'inline-block':'none';
  en.classList.toggle('active', currentPdfLanguage==='en');
  es.classList.toggle('active', currentPdfLanguage==='es');
}

function renderPdf(pdf, placeholderText='Sin reporte aún', variants={}){
  const frame=document.getElementById('pdf-frame');
  const ph=document.getElementById('pdf-ph');
  const ext=document.getElementById('btn-ext');
  currentPdfVariants=variants||{};
  if(currentPdfLanguage && !currentPdfVariants[currentPdfLanguage]){
    currentPdfLanguage=currentPdfVariants.en?'en':(Object.keys(currentPdfVariants)[0]||'en');
  }
  renderPdfLanguageSelector(currentPdfVariants);
  const activePdf=activePdfVariant(pdf,currentPdfVariants);
  if(!activePdf){
    currentPdfPath=null;
    lastPdfMtime=null;
    frame.removeAttribute('src');
    frame.style.display='none';
    ph.style.display='flex';
    ext.style.display='none';
    document.getElementById('pdf-title').textContent='Reporte generado';
    document.getElementById('pdf-title').className='pdf-empty';
    document.getElementById('pdf-sub').textContent=placeholderText;
    return;
  }
  if(activePdf.mtime===lastPdfMtime&&activePdf.path===currentPdfPath)return;
  lastPdfMtime=activePdf.mtime; currentPdfPath=activePdf.path;
  const label=currentPdfLanguage==='es'?'ES':'EN';
  document.getElementById('pdf-title').textContent=activePdf.name;
  document.getElementById('pdf-title').className='pdf-title';
  document.getElementById('pdf-sub').textContent=`${label} · ${activePdf.size_kb} KB · ${activePdf.modified}`;
  frame.src=`/api/serve-pdf/${activePdf.path.replace(/^\//,'')}`;
  frame.style.display='block'; frame.style.flex='1';
  ph.style.display='none'; ext.style.display='inline-block';
}
function selectPdfLanguage(language){
  if(!currentPdfVariants || !currentPdfVariants[language])return;
  currentPdfLanguage=language;
  lastPdfMtime=null;
  renderPdf(liveData?.pdf||null,pdfPlaceholderFor(liveData||{}),currentPdfVariants);
}
function openPdfExt(){if(currentPdfPath)fetch('/api/open-pdf/'+currentPdfPath.replace(/^\//,''));}

// ── Modal ──────────────────────────────────────────────────────
function correr(){openModal('run');}
function openCreateModal(){openModal('create');}
function updateLaunchButtonLabel(){
  const hasAddress=!!document.getElementById('f-address').value.trim();
  const autoRun=document.getElementById('f-auto-run').checked;
  const btn=document.getElementById('btn-launch');
  const hasRunnableTarget=!!(document.getElementById('f-pid').value.trim()||selectedPipelineId);
  if(hasAddress){
    btn.disabled=false;
    btn.textContent=autoRun?'Guardar y ejecutar':'Guardar target';
    return;
  }
  if(modalIntent==='create'){
    btn.textContent='Guardar target';
    btn.disabled=true;
    return;
  }
  btn.disabled=!hasRunnableTarget;
  btn.textContent='▶ Ejecutar ahora';
}
function applyModalIntent(intent){
  const runIntent=intent==='run';
  document.getElementById('modal-title').textContent=runIntent?'Iniciar investigación':'Registrar target';
  document.getElementById('modal-sub').textContent=runIntent
    ?'Lanza manualmente la investigación para el target seleccionado o crea uno nuevo y ejecútalo si así lo indicas.'
    :'Crea el target primero. La investigación se lanza solo si tú lo indicas.';
  document.getElementById('modal-address-hint').textContent=runIntent
    ?'Si rellenas esta dirección, el sistema registra un target nuevo antes de iniciar la investigación.'
    :'Si rellenas esta dirección, el sistema registra un target nuevo. No investigará nada hasta que tú lo decidas.';
}
function openModal(intent='create'){
  modalIntent=intent;
  document.getElementById('modal-bg').classList.add('open');
  document.getElementById('modal-msg').className='';
  document.getElementById('modal-msg').textContent='';
  document.getElementById('btn-launch').disabled=false;
  document.getElementById('f-address').value='';
  document.getElementById('f-nocache').checked=true;
  applyModalIntent(intent);
  if(intent==='run'){
    document.getElementById('f-auto-run').checked=true;
    document.getElementById('f-target-type').value=selectedTarget?.target_type||document.getElementById('f-target-type').value||'';
    document.getElementById('f-owner-name').value=selectedTarget?.owner_name||document.getElementById('f-owner-name').value||'';
    document.getElementById('f-pid').value=selectedPipelineId||liveData?.pipeline_id||'';
    document.getElementById('f-inputs').value=selectedInputsFile||'';
  }else{
    document.getElementById('f-auto-run').checked=false;
    document.getElementById('f-pid').value='';
    document.getElementById('f-inputs').value='';
  }
  updateLaunchButtonLabel();
}
function closeModal(){document.getElementById('modal-bg').classList.remove('open');}
function onBgClick(e){if(e.target.id==='modal-bg')closeModal();}

async function launchRun(){
  const btn=document.getElementById('btn-launch');
  const msgEl=document.getElementById('modal-msg');
  let pid=document.getElementById('f-pid').value.trim()||selectedPipelineId||'';
  let inp=document.getElementById('f-inputs').value.trim()||selectedInputsFile||'';
  const address=document.getElementById('f-address').value.trim();
  const targetType=(document.getElementById('f-target-type').value.trim()||'commercial_building');
  const ownerName=document.getElementById('f-owner-name').value.trim();
  const ownerTicker=document.getElementById('f-owner-ticker').value.trim();
  const autoRun=document.getElementById('f-auto-run').checked;
  const nc=document.getElementById('f-nocache').checked;
  btn.disabled=true;btn.textContent='Lanzando…';msgEl.className='';
  try{
    if(address){
      const createRes=await fetch('/api/create-target',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({address:address,target_type:targetType,owner_name:ownerName,owner_ticker:ownerTicker})});
      const created=await createRes.json();
      if(!created.ok){
        msgEl.className='err';
        msgEl.textContent=`Error: ${created.error||'No se pudo crear el target.'}`;
        btn.disabled=false;btn.textContent='▶ Ejecutar ahora';
        return;
      }
      pid=created.pipeline_id||pid;
      inp=created.inputs_file||inp;
      selectedPipelineId=pid;
      selectedRunId=null;
      selectedInputsFile=inp;
      document.getElementById('f-pid').value=pid;
      document.getElementById('f-inputs').value=inp;
      await loadTargets();
      selectedTarget=allTargets.find(c=>c.pipeline_id===pid)||selectedTarget||{name:created.target_label||pid,pipeline_id:pid};
      if(!autoRun){
        renderPdf(null, `Target ${selectedTarget?.name||pid} registrado. La investigación no se ha iniciado todavía.`, {});
        msgEl.className='ok';
        msgEl.textContent=`"${pid}" registrado. La investigación sigue manual; iníciala cuando quieras.`;
        setTimeout(()=>{closeModal();refresh();loadTargets();},1200);
        btn.disabled=false;
        updateLaunchButtonLabel();
        return;
      }
    }else if(!pid){
      msgEl.className='err';
      msgEl.textContent='Selecciona un target existente o registra una dirección nueva antes de investigar.';
      btn.disabled=false;
      updateLaunchButtonLabel();
      return;
    }
    const res=await fetch('/api/start-run',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({pipeline_id:pid,inputs_file:inp,no_cache:nc})});
    const data=await res.json();
    if(data.ok){
      selectedPipelineId=pid;
      selectedRunId=data.run_id||null;
      selectedInputsFile=data.inputs_file||inp;
      if(allTargets.length){
        selectedTarget=allTargets.find(c=>c.pipeline_id===pid)||selectedTarget;
      }
      const runMsg=data.already_running
        ? `Ya había un análisis corriendo para ${selectedTarget?.name||pid}. Se sigue ese run en vivo.`
        : `Ejecutando ${selectedTarget?.name||pid}… el PDF aparecerá al finalizar este run.`;
      renderPdf(null, runMsg, {});
      msgEl.className='ok';
      msgEl.textContent=data.already_running
        ? `"${pid}" ya estaba corriendo. El monitor quedó atado a ese run.`
        : `"${pid}" iniciado. El análisis aparecerá en el monitor en segundos.`;
      setTimeout(()=>{closeModal();refresh();loadTargets();},2000);
    }else{msgEl.className='err';msgEl.textContent=`Error: ${data.error||'No se pudo iniciar.'}`;}
  }catch(e){msgEl.className='err';msgEl.textContent=`Error: ${e.message}`;}
  btn.disabled=false;updateLaunchButtonLabel();
}

function esc(s){
  if(!s)return'';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

init();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(_HTML)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ZLab OTF — Monitor")
    parser.add_argument("--port", type=int, default=7474)
    parser.add_argument("--open", action="store_true", dest="auto_open")
    args = parser.parse_args()

    os.chdir(_HERE)
    if args.auto_open:
        def _open():
            time.sleep(1.2)
            subprocess.Popen(["open", f"http://localhost:{args.port}"])
        threading.Thread(target=_open, daemon=True).start()

    print(f"ZLab OTF Monitor → http://localhost:{args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
