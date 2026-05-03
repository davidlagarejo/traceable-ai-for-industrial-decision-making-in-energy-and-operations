from __future__ import annotations

from typing import Any

from .asset_type_router import route_for_asset_type
from .critical_fields import default_evidence_gating_plan
from .jurisdiction_resolver import resolve_us_jurisdiction
from .report_switching import derive_report_type_switch
from .schemas import (
    AssetType,
    CriticalFieldStatus,
    EvidenceGatingPlan,
    ReportTypeSwitchRecommendation,
    TargetClassification,
    TargetClassificationResult,
)
from .source_registry import build_source_routing_plan
from .target_taxonomy import make_target_classification_result, normalize_asset_type, normalize_target_classification


_FIELD_CLUSTER_MAP = {
    "address_confirmed": "location_cluster",
    "size_or_gfa": "geometry_size_cluster",
    "use_or_occupancy": "use_program_cluster",
    "year_built": "vintage_structure_cluster",
    "energy_baseline_or_proxy": "fuel_energy_cluster",
    "fuel_type": "fuel_energy_cluster",
    "system_presence": "systems_cluster",
    "regulatory_applicability": "regulatory_cluster",
    "benchmarking_or_local_energy_disclosure": "benchmark_mapping_cluster",
    "hvac_or_controls_clue": "systems_cluster",
    "unit_or_use_mix": "use_program_cluster",
    "process_anchor": "use_program_cluster",
    "environmental_or_permit_anchor": "regulatory_cluster",
    "throughput_or_load_driver": "operating_regime_cluster",
    "dock_or_throughput_anchor": "operating_regime_cluster",
    "refrigeration_yes_no": "systems_cluster",
    "critical_load_anchor": "fuel_energy_cluster",
    "cooling_or_redundancy_clue": "systems_cluster",
    "utility_tariff_or_power_context": "fuel_energy_cluster",
}


_JURISDICTION_CITY_MAP = {
    "US-NY-NYC": ("NY", "New York"),
    "US-CA-SF": ("CA", "San Francisco"),
    "US-CA-LA": ("CA", "Los Angeles"),
    "US-CA-BERKELEY": ("CA", "Berkeley"),
    "US-CA-SANJOSE": ("CA", "San Jose"),
    "US-TX-HOUSTON": ("TX", "Houston"),
}


def _normalize_decision_intent(value: str | None) -> str:
    text = str(value or "").strip().lower()
    if text in {"asset_screening", "target_identification", "classification"}:
        return "target_identification"
    if "acquisition" in text or "underwriting" in text:
        return "acquisition_underwriting"
    if "retrofit" in text or "capex" in text:
        return "retrofit_capex"
    if "compliance" in text:
        return "compliance_investment"
    if "process" in text:
        return "process_change"
    if "refinanc" in text:
        return "refinancing"
    return "target_identification"


def _resolve_state_city(
    target_definition: dict[str, Any],
    subject_definition: dict[str, Any],
) -> tuple[str | None, str | None]:
    scopes = target_definition.get("jurisdiction_scope", [])
    if isinstance(scopes, list):
        for scope in scopes:
            if scope in _JURISDICTION_CITY_MAP:
                return _JURISDICTION_CITY_MAP[scope]
    address = str(
        target_definition.get("address_raw")
        or subject_definition.get("address_raw")
        or ""
    ).strip()
    if address:
        parts = [part.strip() for part in address.split(",") if part.strip()]
        if len(parts) >= 3 and parts[-1].replace("-", "").isdigit():
            state = parts[-2].upper()
            city = parts[-3].title()
            return state, city
        if len(parts) >= 2:
            state_tokens = parts[-1].replace(".", " ").split()
            if state_tokens:
                state = state_tokens[0].upper()
                city = parts[-2].title()
                return state, city
    return None, None


def _target_class_with_asset_override(
    base_target_class: str | TargetClassification,
    asset_type: AssetType | str | None,
) -> TargetClassification:
    normalized = normalize_target_classification(base_target_class)
    normalized_asset_type = normalize_asset_type(asset_type)
    if normalized == TargetClassification.OPERATING_ASSET and normalized_asset_type == AssetType.INDUSTRIAL_FACILITY:
        return TargetClassification.INDUSTRIAL_FACILITY
    if normalized == TargetClassification.OPERATING_ASSET and normalized_asset_type == AssetType.DATA_CENTER:
        return TargetClassification.DATA_CENTER
    return normalized


def build_target_classification_from_upstream(
    *,
    target_definition: dict[str, Any],
    target_classification_object: dict[str, Any],
    subject_gate_passed: bool,
    reason_fallback: str = "",
) -> TargetClassificationResult:
    asset_type = normalize_asset_type(target_definition.get("target_type"))
    target_class = _target_class_with_asset_override(
        target_classification_object.get("target_type"),
        asset_type,
    )
    return make_target_classification_result(
        target_class,
        classification_confidence=str(target_classification_object.get("classification_confidence") or "low"),
        asset_identity_confirmed=bool(subject_gate_passed),
        reason=str(target_classification_object.get("reason") or reason_fallback or "").strip(),
    )


def build_critical_field_contract(
    *,
    asset_type: AssetType | str | None,
    observable_clusters: dict[str, Any],
    subject_gate_passed: bool,
) -> tuple[list[CriticalFieldStatus], int]:
    gating_plan = default_evidence_gating_plan(asset_type)
    rows: list[CriticalFieldStatus] = []
    missing_count = 0

    for requirement in gating_plan.critical_fields:
        cluster_name = _FIELD_CLUSTER_MAP.get(requirement.field_name, "")
        cluster = observable_clusters.get(cluster_name, {}) if isinstance(observable_clusters, dict) else {}
        populated = bool(cluster.get("populated"))
        if requirement.field_name == "address_confirmed":
            populated = bool(subject_gate_passed) or populated

        current_status = "observed" if populated else "missing"
        notes = str(cluster.get("note", "")).strip() if isinstance(cluster, dict) else ""
        if requirement.blocking_if_missing and not populated:
            missing_count += 1

        rows.append(
            CriticalFieldStatus(
                field_name=requirement.field_name,
                required=requirement.blocking_if_missing,
                current_status=current_status,
                rationale=requirement.rationale,
                minimum_source_layer=requirement.minimum_source_layer,
                prohibited_substitutions=list(requirement.prohibited_substitutions),
                notes=notes,
            )
        )

    return rows, missing_count


def build_routing_bundle(
    *,
    target_definition: dict[str, Any],
    subject_definition: dict[str, Any],
    target_classification_object: dict[str, Any],
    subject_gate_passed: bool,
    technical_substrate_readiness: str,
    observable_clusters: dict[str, Any],
    upstream_recommended_report_type: str | None = None,
    upstream_prohibited_report_types: list[str] | None = None,
) -> dict[str, Any]:
    asset_type = normalize_asset_type(target_definition.get("target_type"))
    target_classification_result = build_target_classification_from_upstream(
        target_definition=target_definition,
        target_classification_object=target_classification_object,
        subject_gate_passed=subject_gate_passed,
        reason_fallback="Routing requires stronger asset identity and jurisdiction grounding.",
    )
    state, city = _resolve_state_city(target_definition, subject_definition)
    jurisdiction_resolution = resolve_us_jurisdiction(
        state=state,
        city=city,
        asset_type=asset_type,
    )
    asset_type_route = route_for_asset_type(asset_type)
    decision_type = _normalize_decision_intent(target_definition.get("decision_intent"))
    source_routing_plan = build_source_routing_plan(
        jurisdiction_resolution,
        asset_type,
        decision_type,
    )
    evidence_gating_plan = default_evidence_gating_plan(asset_type)
    critical_field_contract, missing_critical_fields = build_critical_field_contract(
        asset_type=asset_type,
        observable_clusters=observable_clusters,
        subject_gate_passed=subject_gate_passed,
    )
    report_type_switch_recommendation = derive_report_type_switch(
        target_type=target_classification_result.target_type,
        technical_scraping_allowed=target_classification_result.technical_scraping_allowed,
        technical_substrate_readiness=technical_substrate_readiness,
        missing_critical_fields=missing_critical_fields,
        gating_plan=evidence_gating_plan,
        upstream_recommended_report_type=upstream_recommended_report_type,
        upstream_prohibited_report_types=upstream_prohibited_report_types,
        reason=target_classification_result.reason,
    )
    source_routing_plan_dict = source_routing_plan.to_dict()
    if not target_classification_result.technical_scraping_allowed:
        source_routing_plan_dict["mandatory_sources"] = []
        source_routing_plan_dict["high_priority_sources"] = []
        source_routing_plan_dict["optional_sources"] = []
        source_routing_plan_dict.setdefault("routing_notes", []).append(
            "Technical discovery suppressed because target classification does not admit an asset-level route yet."
        )
    return {
        "target_classification_result": target_classification_result.to_dict(),
        "jurisdiction_resolution": jurisdiction_resolution.to_dict(),
        "asset_type_route": asset_type_route.to_dict() if asset_type_route else {},
        "source_routing_plan": source_routing_plan_dict,
        "critical_field_contract": [row.to_dict() for row in critical_field_contract],
        "critical_field_summary": {
            "total_critical_fields": len(critical_field_contract),
            "missing_critical_fields": missing_critical_fields,
            "max_missing_before_block": evidence_gating_plan.max_missing_critical_fields,
        },
        "evidence_gating_plan": evidence_gating_plan.to_dict(),
        "report_type_switch_recommendation": report_type_switch_recommendation.to_dict(),
        "routing_eligibility": {
            "technical_scraping_allowed": target_classification_result.technical_scraping_allowed,
            "decision_type": decision_type,
            "technical_substrate_readiness": technical_substrate_readiness,
        },
    }
