from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .autodraft_rule_derivation import derive_autodraft_rule_from_pattern_spec
from .extractor import build_extraction_seed_from_manifest

try:
    import pdfplumber
except Exception:  # pragma: no cover - bounded fallback when optional dependency is unavailable
    pdfplumber = None


_AUTO_PATTERN_RULES: dict[str, dict[str, Any]] = {
    "warehouse_mhe_charging_demand_peak": {
        "required_groups": [
            ["warehouse", "logistics", "distribution center", "fulfillment center"],
            ["forklift", "mhe", "material handling", "pallet jack", "lift truck"],
            ["charging", "charger", "battery swap", "battery charging"],
        ],
        "optional_terms": ["demand charge", "peak demand", "tariff", "load profile"],
    },
    "warehouse_dock_infiltration_loss": {
        "required_groups": [
            ["warehouse", "logistics", "distribution center", "fulfillment center"],
            ["dock", "dock door", "loading dock", "trailer door", "cross dock"],
        ],
        "optional_terms": ["infiltration", "air exchange", "conditioned space", "refrigerated"],
    },
    "cold_chain_status_unknown": {
        "required_groups": [["cold chain", "cold storage", "refrigerated", "temperature-controlled"]],
        "optional_terms": ["freezer", "chilled", "refrigeration"],
    },
    "value_boundary_leakage_owner_operator": {
        "required_groups": [["owner", "operator", "tenant", "landlord", "lease", "split incentive"]],
        "optional_terms": ["meter boundary", "capex responsibility", "utility payment", "responsibility matrix"],
    },
    "demand_charge_exposure_unknown": {
        "required_groups": [["demand charge", "peak demand", "tariff", "utility bill", "rate schedule"]],
        "optional_terms": ["kW", "interval data", "billing demand"],
    },
    "fair_comparison_invalid_area_metric": {
        "required_groups": [["eui", "energy use intensity", "per square foot", "per sq ft", "benchmark"]],
        "optional_terms": ["denominator", "normalization", "peer comparison"],
    },
    "benchmark_denominator_error": {
        "required_groups": [["benchmark", "eui", "per square foot", "per sq ft", "denominator"]],
        "optional_terms": ["comparison", "normalization", "peer set"],
    },
    "reactive_power_exposure": {
        "required_groups": [["power factor", "reactive power", "kvar", "harmonics"]],
        "optional_terms": ["capacitor bank", "power quality", "nonlinear load"],
    },
    "compressed_air_leak_plausibility": {
        "required_groups": [["compressed air", "air leak", "air compressor", "compressor room"]],
        "optional_terms": ["leak survey", "end use", "demand reduction"],
    },
    "maintenance_maturity_not_evidenced": {
        "required_groups": [["maintenance", "preventive maintenance", "pm program", "reliability"]],
        "optional_terms": ["downtime", "work order", "asset care", "maintenance maturity"],
    },
    "procurement_vs_maintenance_conflict": {
        "required_groups": [["procurement", "lifecycle cost", "maintenance", "spare parts"]],
        "optional_terms": ["opex", "replacement cycle", "lowest bid"],
    },
    "digital_twin_prematurity": {
        "required_groups": [["digital twin", "simulation", "modeling", "digital model"]],
        "optional_terms": ["dominant variable", "boundary", "model scope"],
    },
    "sensor_prematurity": {
        "required_groups": [["sensor", "submeter", "metering", "instrumentation"]],
        "optional_terms": ["dominant variable", "measurement plan", "hypothesis"],
    },
    "high_bay_lighting_waste": {
        "required_groups": [["high bay", "lighting", "warehouse lighting", "fixture"]],
        "optional_terms": ["occupancy sensor", "burn hours", "led retrofit"],
    },
    "hvac_schedule_drift": {
        "required_groups": [["hvac", "schedule", "setback", "controls"]],
        "optional_terms": ["bms", "building automation", "operating hours"],
    },
    "steam_trap_failure_plausibility": {
        "required_groups": [["steam trap", "steam system", "condensate"]],
        "optional_terms": ["blow-through", "trap survey", "steam loss"],
    },
    "boiler_degradation_plausibility": {
        "required_groups": [["boiler", "combustion", "stack loss"]],
        "optional_terms": ["blowdown", "boiler efficiency", "tune-up"],
    },
    "chiller_degradation_plausibility": {
        "required_groups": [["chiller", "cooling plant", "condenser", "evaporator"]],
        "optional_terms": ["approach temperature", "fouling", "coefficient of performance"],
    },
    "tenant_operator_boundary_unresolved": {
        "required_groups": [["tenant", "operator", "landlord", "lease"]],
        "optional_terms": ["responsibility", "utility payment", "meter"],
    },
    "compliance_vs_control_mismatch": {
        "required_groups": [["compliance", "permit", "control", "operations"]],
        "optional_terms": ["responsibility", "governance", "control boundary"],
    },
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _slug(value: Any) -> str:
    text = _text(value).lower()
    chars: list[str] = []
    previous_dash = False
    for ch in text:
        safe = ch if ch.isalnum() else "-"
        if safe == "-":
            if previous_dash:
                continue
            previous_dash = True
        else:
            previous_dash = False
        chars.append(safe)
    return "".join(chars).strip("-")


def _normalize_search_text(*parts: Any) -> str:
    rows = [_text(part).lower() for part in parts if _text(part)]
    return "\n".join(rows)


def _extract_excerpt(search_text: str, matched_terms: list[str], *, span: int = 220) -> str:
    for term in matched_terms:
        needle = _text(term).lower()
        if not needle:
            continue
        index = search_text.find(needle)
        if index >= 0:
            start = max(0, index - span // 2)
            end = min(len(search_text), index + len(needle) + span // 2)
            return search_text[start:end].strip()
    return _text(search_text[:span])


def _build_structured_prior_candidates(
    *,
    search_text: str,
    document_slug: str,
    source_locator_prefix: str,
    registry_bundle: Mapping[str, Any] | None,
) -> dict[str, Any]:
    registry = dict(registry_bundle or {})
    matched_patterns: list[dict[str, Any]] = []
    for pattern_spec in list(registry.get("patterns", []) or []):
        pattern_id = _text(pattern_spec.get("id"))
        # V5 P9: hand-authored rule first; fall back to deterministic
        # derivation from the pattern_spec's own trigger_conditions when
        # no hand-authored rule exists. This unlocks the 10 registry
        # patterns (cold-chain S4 + manufacturing) that previously had
        # no autodraft rule and would skip in V5 P3 smoke tests.
        rule = _AUTO_PATTERN_RULES.get(pattern_id)
        if rule is None:
            rule = derive_autodraft_rule_from_pattern_spec(pattern_spec)
        if not rule or not search_text:
            continue
        evaluation = _evaluate_pattern_rule(search_text, rule)
        if not evaluation:
            continue
        matched_patterns.append(
            {
                "pattern_id": pattern_id,
                "pattern_spec": dict(pattern_spec),
                "matched_terms": list(evaluation.get("matched_terms", []) or []),
                "score": int(evaluation.get("score", 0) or 0),
            }
        )
    matched_patterns.sort(key=lambda row: (-int(row.get("score", 0)), _text(row.get("pattern_id"))))

    knowledge_atoms: list[dict[str, Any]] = []
    pattern_candidates: list[dict[str, Any]] = []
    pattern_candidate_ids_by_pattern_id: dict[str, str] = {}

    for row in matched_patterns:
        pattern_id = _text(row.get("pattern_id"))
        pattern_spec = dict(row.get("pattern_spec", {}) or {})
        matched_terms = list(row.get("matched_terms", []) or [])
        atom_id = f"atom::{document_slug}::{pattern_id}"
        candidate_id = f"pattern_candidate::{document_slug}::{pattern_id}"
        source_locator = f"{source_locator_prefix}::{pattern_id}"
        excerpt = _extract_excerpt(search_text, matched_terms)
        knowledge_atoms.append(
            _build_atom_from_pattern(
                pattern_spec=pattern_spec,
                atom_id=atom_id,
                supporting_excerpt=excerpt,
                source_locator=source_locator,
            )
        )
        pattern_candidates.append(
            _build_pattern_candidate_from_pattern(
                pattern_spec=pattern_spec,
                candidate_id=candidate_id,
                atom_id=atom_id,
                source_locator=source_locator,
            )
        )
        pattern_candidate_ids_by_pattern_id[pattern_id] = candidate_id

    combination_candidates: list[dict[str, Any]] = []
    active_pattern_ids = set(pattern_candidate_ids_by_pattern_id)
    for combination_spec in list(registry.get("combinations", []) or []):
        required_pattern_ids = [_text(item) for item in list(combination_spec.get("pattern_ids", []) or []) if _text(item)]
        if not required_pattern_ids or not set(required_pattern_ids).issubset(active_pattern_ids):
            continue
        combination_id = _text(combination_spec.get("id"))
        candidate_id = f"combination_candidate::{document_slug}::{combination_id}"
        source_locator = f"{source_locator_prefix}::{combination_id}"
        combination_candidates.append(
            _build_combination_candidate_from_spec(
                combination_spec=combination_spec,
                candidate_id=candidate_id,
                derived_pattern_candidate_ids=[pattern_candidate_ids_by_pattern_id[item] for item in required_pattern_ids],
                source_locator=source_locator,
            )
        )
    return {
        "knowledge_atoms": knowledge_atoms,
        "pattern_candidate_records": pattern_candidates,
        "combination_candidate_records": combination_candidates,
        "matched_pattern_ids": [_text(row.get("pattern_id")) for row in matched_patterns],
        "matched_combination_ids": [
            _text(row.get("matched_registry_combination_id"))
            for row in combination_candidates
        ],
    }


def build_structured_prior_candidates_from_text(
    *,
    document_slug: str,
    title: str = "",
    abstract: str = "",
    keywords: list[str] | None = None,
    notes: str = "",
    supplemental_text: str = "",
    source_locator_prefix: str,
    registry_bundle: Mapping[str, Any] | None,
) -> dict[str, Any]:
    search_text = _normalize_search_text(
        title,
        abstract,
        "\n".join([_text(item) for item in list(keywords or []) if _text(item)]),
        notes,
        supplemental_text,
    )
    return _build_structured_prior_candidates(
        search_text=search_text,
        document_slug=_slug(document_slug) or "licensed-paper",
        source_locator_prefix=source_locator_prefix,
        registry_bundle=registry_bundle,
    )


def extract_bounded_pdf_text(
    *,
    artifact_path: str,
    max_pages: int = 8,
    max_chars: int = 24000,
) -> dict[str, Any]:
    artifact = Path(str(artifact_path)).expanduser()
    if pdfplumber is None:
        return {
            "status": "pdfplumber_unavailable",
            "visible_text": "",
            "page_count_scanned": 0,
            "char_count": 0,
            "error": "",
        }
    try:
        pages: list[str] = []
        scanned = 0
        with pdfplumber.open(str(artifact)) as pdf:
            for page in list(pdf.pages[: max(1, max_pages)]):
                scanned += 1
                page_text = _text(page.extract_text())
                if page_text:
                    pages.append(page_text)
                joined = "\n\n".join(pages)
                if len(joined) >= max_chars:
                    break
        visible_text = "\n\n".join(pages)[:max_chars]
        return {
            "status": "success" if visible_text else "empty_text",
            "visible_text": visible_text,
            "page_count_scanned": scanned,
            "char_count": len(visible_text),
            "error": "",
        }
    except Exception as exc:  # pragma: no cover - runtime-dependent PDF parser failures
        return {
            "status": "error",
            "visible_text": "",
            "page_count_scanned": 0,
            "char_count": 0,
            "error": _text(exc),
        }


def _evaluate_pattern_rule(search_text: str, rule: Mapping[str, Any]) -> dict[str, Any] | None:
    matched_terms: list[str] = []
    for group in list(rule.get("required_groups", []) or []):
        group_hit = ""
        for term in list(group or []):
            text = _text(term).lower()
            if text and text in search_text:
                group_hit = text
                break
        if not group_hit:
            return None
        matched_terms.append(group_hit)
    optional_hits: list[str] = []
    for term in list(rule.get("optional_terms", []) or []):
        text = _text(term).lower()
        if text and text in search_text and text not in matched_terms and text not in optional_hits:
            optional_hits.append(text)
    return {
        "matched_terms": matched_terms + optional_hits,
        "score": len(matched_terms) * 10 + len(optional_hits),
    }


def _build_atom_from_pattern(
    *,
    pattern_spec: Mapping[str, Any],
    atom_id: str,
    supporting_excerpt: str,
    source_locator: str,
) -> dict[str, Any]:
    knowledge_types = list(pattern_spec.get("knowledge_type", []) or [])
    return {
        "id": atom_id,
        "knowledge_type": _text(knowledge_types[0]) or "PROCESS_LOGIC",
        "statement": _text(pattern_spec.get("physical_basis")) or _text(pattern_spec.get("hypothesis")),
        "asset_types": list(pattern_spec.get("asset_types", []) or []),
        "applicable_industries": list(pattern_spec.get("applicable_industries", []) or []),
        "applicable_contexts": list(pattern_spec.get("applicable_contexts", []) or []),
        "anti_triggers": list(pattern_spec.get("anti_triggers", []) or []),
        "falsification_conditions": list(pattern_spec.get("falsification_conditions", []) or []),
        "minimum_evidence": (
            list(pattern_spec.get("minimum_evidence_to_activate", []) or [])
            or list(pattern_spec.get("evidence_required", []) or [])
        ),
        "financial_mechanism": _text(pattern_spec.get("financial_mechanism")),
        "supporting_excerpt": supporting_excerpt,
        "source_locator": source_locator,
        "confidence_ceiling": _text(pattern_spec.get("confidence_ceiling")) or "L2",
    }


def _build_pattern_candidate_from_pattern(
    *,
    pattern_spec: Mapping[str, Any],
    candidate_id: str,
    atom_id: str,
    source_locator: str,
) -> dict[str, Any]:
    return {
        "id": candidate_id,
        "matched_registry_pattern_id": _text(pattern_spec.get("id")),
        "derived_from_atom_ids": [atom_id],
        "name": _text(pattern_spec.get("name")),
        "knowledge_types": list(pattern_spec.get("knowledge_type", []) or []),
        "asset_types": list(pattern_spec.get("asset_types", []) or []),
        "applicable_contexts": list(pattern_spec.get("applicable_contexts", []) or []),
        "hypothesis": _text(pattern_spec.get("hypothesis")),
        "minimum_evidence": (
            list(pattern_spec.get("minimum_evidence_to_activate", []) or [])
            or list(pattern_spec.get("evidence_required", []) or [])
        ),
        "anti_triggers": list(pattern_spec.get("anti_triggers", []) or []),
        "falsification_conditions": list(pattern_spec.get("falsification_conditions", []) or []),
        "financial_mechanism": _text(pattern_spec.get("financial_mechanism")),
        "source_locator": source_locator,
        "confidence_ceiling": _text(pattern_spec.get("confidence_ceiling")) or "L2",
    }


def _build_combination_candidate_from_spec(
    *,
    combination_spec: Mapping[str, Any],
    candidate_id: str,
    derived_pattern_candidate_ids: list[str],
    source_locator: str,
) -> dict[str, Any]:
    return {
        "id": candidate_id,
        "matched_registry_combination_id": _text(combination_spec.get("id")),
        "derived_from_pattern_candidate_ids": derived_pattern_candidate_ids,
        "name": _text(combination_spec.get("name")),
        "combined_hypothesis": _text(combination_spec.get("combined_hypothesis")),
        "minimum_evidence": list(combination_spec.get("minimum_evidence", []) or []),
        "financial_exposure": list(combination_spec.get("financial_exposure", []) or []),
        "prohibited_claims": list(combination_spec.get("prohibited_claims", []) or []),
        "source_locator": source_locator,
        "confidence_ceiling": _text(combination_spec.get("confidence_ceiling")) or "L2",
    }


def build_local_pdf_auto_draft_extraction_payload(
    *,
    artifact_path: str,
    metadata: Mapping[str, Any] | None,
    research_document_manifest: Mapping[str, Any],
    registry_bundle: Mapping[str, Any] | None,
    source_basis_id: str = "licensed_research_public_technical_priors",
    retrieval_purpose: str = "pattern_seed_discovery",
) -> dict[str, Any]:
    artifact = Path(str(artifact_path)).expanduser()
    metadata_payload = dict(metadata or {})
    manifest = dict(research_document_manifest or {})
    seed = build_extraction_seed_from_manifest(
        research_document_manifest=manifest,
        source_basis_id=source_basis_id,
        retrieval_purpose=retrieval_purpose,
    )
    pdf_text_result = extract_bounded_pdf_text(artifact_path=str(artifact))
    search_text = _normalize_search_text(
        manifest.get("title"),
        metadata_payload.get("title"),
        metadata_payload.get("abstract"),
        metadata_payload.get("notes"),
        pdf_text_result.get("visible_text"),
    )

    document_slug = _slug(manifest.get("title") or artifact.stem) or "licensed-paper"
    candidate_bundle = build_structured_prior_candidates_from_text(
        document_slug=document_slug,
        title=_text(metadata_payload.get("title")) or _text(manifest.get("title")),
        abstract=_text(metadata_payload.get("abstract")),
        notes=_text(metadata_payload.get("notes")),
        supplemental_text=_text(pdf_text_result.get("visible_text")),
        source_locator_prefix=f"local_pdf_autodraft::{artifact.name}",
        registry_bundle=registry_bundle,
    )

    payload = dict(seed)
    payload.update(
        {
            "id": f"extract::local_autodraft::{document_slug}",
            "provider_key": _text(metadata_payload.get("provider_key")) or seed.get("provider_key") or "manual_local",
            "document_title": _text(metadata_payload.get("title")) or _text(manifest.get("title")) or artifact.stem,
            "document_ref": artifact.name,
            "review_status": "auto_draft",
            "notes": (
                "Auto-draft generated from licensed PDF text and metadata. "
                "Keep all extracted knowledge at L2 until a human reviews or edits the draft."
            ),
            "knowledge_atoms": list(candidate_bundle.get("knowledge_atoms", []) or []),
            "pattern_candidate_records": list(candidate_bundle.get("pattern_candidate_records", []) or []),
            "combination_candidate_records": list(candidate_bundle.get("combination_candidate_records", []) or []),
            "autodraft_summary": {
                "pdf_text_status": _text(pdf_text_result.get("status")) or "unknown",
                "pdf_text_char_count": int(pdf_text_result.get("char_count", 0) or 0),
                "pdf_pages_scanned": int(pdf_text_result.get("page_count_scanned", 0) or 0),
                "matched_pattern_ids": list(candidate_bundle.get("matched_pattern_ids", []) or []),
                "matched_combination_ids": list(candidate_bundle.get("matched_combination_ids", []) or []),
            },
        }
    )
    return payload
