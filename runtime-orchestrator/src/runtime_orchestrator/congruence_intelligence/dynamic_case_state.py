from __future__ import annotations

from typing import Any


_FAMILY_BY_TARGET_TYPE = {
    "commercial_building": "commercial_building",
    "multifamily_building": "commercial_building",
    "data_center": "commercial_building",
    "warehouse_distribution": "logistics_warehouse",
    "cold_chain_facility": "cold_chain",
    "manufacturing_facility": "industrial_manufacturing",
    "food_processing_facility": "industrial_manufacturing",
    "industrial_plant": "industrial_manufacturing",
    "thermal_process_site": "thermal_process_site",
    "infrastructure_node": "infrastructure_node",
    "utility_heavy_site": "utility_heavy_site",
    "oil_gas_upstream_site": "utility_heavy_site",
    "oil_gas_midstream_facility": "utility_heavy_site",
    "oil_gas_downstream_facility": "utility_heavy_site",
}

_SUCCESS_STATUSES = {"found"}
_FAILURE_STATUSES = {"failed", "no_data", "time_budget_exhausted"}

_OPERATOR_BOUNDARY_KEYWORDS = ("operator", "tenant", "lease", "boundary")
_SCHEDULE_KEYWORDS = ("schedule", "shift", "throughput", "operating hours")
_CONTROL_BOUNDARY_KEYWORDS = ("meter", "lease", "boundary", "control")
_UTILITY_CONTEXT_KEYWORDS = ("utility", "tariff", "demand", "rate")

_OPERATOR_BOUNDARY_SOURCE_FAMILIES = {
    "operator_input_record",
    "lease_matrix_record",
    "schedule_record",
}
_SCHEDULE_SOURCE_FAMILIES = {
    "schedule_record",
    "operator_input_record",
}
_CONTROL_BOUNDARY_SOURCE_FAMILIES = {
    "lease_matrix_record",
    "submetering_record",
    "meter_interval_record",
    "operator_input_record",
}
_UTILITY_CONTEXT_SOURCE_FAMILIES = {
    "utility_bill_record",
    "utility_tariff_record",
    "utility_service_record",
}

_WAREHOUSE_COMPARISON_BLOCKERS = {
    "warehouse_subtype_classification",
    "dock_and_service_intensity",
    "refrigeration_presence",
    "operator_boundary_and_control",
    "utility_territory_and_tariff_context",
}

_MANUFACTURING_COMPARISON_BLOCKERS = {
    "process_and_permit_profile",
    "thermal_system_and_utility_mix",
    "throughput_proxy_and_schedule",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _unique(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        label = _text(value)
        if not label or label in seen:
            continue
        seen.add(label)
        ordered.append(label)
    return ordered


def _asset_family(target_definition: dict[str, Any]) -> str:
    return _FAMILY_BY_TARGET_TYPE.get(_text(target_definition.get("target_type")), "commercial_building")


def _budget_state(search_budget_register: list[dict[str, Any]]) -> str:
    for row in _as_list(search_budget_register):
        if _text(_as_dict(row).get("budget_scope")) == "total_public_discovery":
            return _text(_as_dict(row).get("budget_state")) or "bounded"
    return "bounded"


def _family_counts(attempts: list[dict[str, Any]], statuses: set[str]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in _as_list(attempts):
        payload = _as_dict(row)
        if _text(payload.get("status")) not in statuses:
            continue
        source_family = _text(payload.get("source_family"))
        if not source_family:
            continue
        counts[source_family] = counts.get(source_family, 0) + 1
    return [
        {"source_family": source_family, "count": counts[source_family]}
        for source_family in sorted(counts, key=lambda item: (-counts[item], item))
    ]


def _requestable_blob(requestable_evidence_items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in _as_list(requestable_evidence_items):
        payload = _as_dict(row)
        parts.extend(
            [
                _text(payload.get("evidence_item")),
                _text(payload.get("why_needed")),
                _text(payload.get("source")),
            ]
        )
    return " ".join(part.lower() for part in parts if part)


def _infer_state(
    *,
    requestable_blob: str,
    success_families: set[str],
    keywords: tuple[str, ...],
    relevant_source_families: set[str],
) -> str:
    if success_families.intersection(relevant_source_families):
        return "partially_evidenced"
    if any(keyword in requestable_blob for keyword in keywords):
        return "not_yet_evidenced"
    return "not_primary"


def _progress_signals(runtime_context: dict[str, Any]) -> list[str]:
    case_delta_summary = _as_dict(runtime_context.get("case_delta_summary"))
    if case_delta_summary:
        signals = _unique(_as_list(case_delta_summary.get("progress_signals")))
        if signals:
            return signals
    previous_run_summary = _as_dict(runtime_context.get("previous_run_summary"))
    previous_case_delta = _as_dict(previous_run_summary.get("case_delta_summary"))
    return _unique(_as_list(previous_case_delta.get("progress_signals")))


def _pressure_rows(summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _as_list(summary):
        payload = _as_dict(row)
        source_family = _text(payload.get("source_family"))
        if not source_family:
            continue
        count = int(payload.get("count", 0) or 0)
        rows.append(
            {
                "source_family": source_family,
                "count": count,
                "pressure_score": min(count * 10, 30),
            }
        )
    return rows


def _contains_any(blob: str, *tokens: str) -> bool:
    return any(token in blob for token in tokens if token)


def _active_case_pressure(
    *,
    asset_family: str,
    requestable_blob: str,
    gap_types: list[str],
    operator_boundary_state: str,
    schedule_state: str,
    control_boundary_state: str,
    utility_context_state: str,
) -> dict[str, list[str]]:
    active_rival_hypotheses: list[str] = []
    active_comparison_blockers: list[str] = []
    active_loss_pattern_candidates: list[str] = []
    active_financial_exposure_candidates: list[str] = []
    active_contradiction_targets: list[str] = []

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        if (
            "asset_energy_behavior_reference" in gap_types
            or "asset_primary_anchor_missing" in gap_types
            or _contains_any(requestable_blob, "cold", "refrigerat", "temperature-controlled", "freezer")
        ):
            active_rival_hypotheses.append("warehouse_subtype_temperature_regime")
            active_comparison_blockers.extend(["warehouse_subtype_classification", "refrigeration_presence"])
            active_loss_pattern_candidates.extend(["asset_family_misclassification", "refrigeration_load"])
            active_financial_exposure_candidates.append("wrong_peer_valuation")
            active_contradiction_targets.append("subtype_vs_generic_benchmark")
        if (
            schedule_state in {"not_yet_evidenced", "partially_evidenced"}
            or _contains_any(requestable_blob, "dock", "throughput", "shift", "operating hours", "service")
        ):
            active_rival_hypotheses.append("warehouse_service_intensity_denominator")
            active_comparison_blockers.append("dock_and_service_intensity")
            active_loss_pattern_candidates.extend(["dock_infiltration", "schedule_waste"])
            active_financial_exposure_candidates.append("wrong_underwriting_premium")
            active_contradiction_targets.append("service_intensity_vs_building_waste")
        if (
            utility_context_state in {"not_yet_evidenced", "partially_evidenced"}
            or _contains_any(requestable_blob, "tariff", "demand", "utility", "charging", "battery", "forklift")
        ):
            active_rival_hypotheses.append("warehouse_tariff_orchestration")
            active_comparison_blockers.append("utility_territory_and_tariff_context")
            active_loss_pattern_candidates.extend(["tariff_exposure_hidden", "mhe_charging_peak_demand"])
            active_financial_exposure_candidates.append("demand_charge_exposure_hidden")
            active_contradiction_targets.append("tariff_vs_efficiency")
        if (
            "asset_context_readiness" in gap_types
            or _contains_any(requestable_blob, "tenant", "lease", "boundary", "meter", "responsibility", "control")
            or (
                control_boundary_state in {"not_yet_evidenced", "partially_evidenced"}
                and _contains_any(requestable_blob, "tenant", "lease", "boundary", "meter", "responsibility")
            )
        ):
            active_rival_hypotheses.append("warehouse_control_boundary_value_leakage")
            active_comparison_blockers.append("operator_boundary_and_control")
            active_loss_pattern_candidates.append("control_boundary_value_leakage")
            active_financial_exposure_candidates.append("tenant_operator_value_leakage")
            active_contradiction_targets.append("control_boundary_vs_owner_capture")
        if _contains_any(requestable_blob, "hvac", "roof", "rtu", "mechanical", "ventilation"):
            active_rival_hypotheses.append("warehouse_mechanical_topology")
            active_loss_pattern_candidates.extend(["rooftop_hvac_degradation", "dock_infiltration"])
            active_financial_exposure_candidates.append("wrong_retrofit_sequencing")
            active_contradiction_targets.append("mechanical_vs_logistics_interface")

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        if (
            "asset_energy_behavior_reference" in gap_types
            or _contains_any(requestable_blob, "process", "thermal", "boiler", "furnace", "steam", "permit")
        ):
            active_rival_hypotheses.append("manufacturing_process_thermal_lane")
            active_comparison_blockers.extend(["process_and_permit_profile", "thermal_system_and_utility_mix"])
            active_loss_pattern_candidates.extend(["process_heat_waste", "thermal_system_loss"])
            active_financial_exposure_candidates.append("wrong_retrofit_sequencing")
            active_contradiction_targets.append("process_load_vs_support_waste")
        if _contains_any(requestable_blob, "compressed air", "compressor", "pressure", "pneumatic"):
            active_rival_hypotheses.append("manufacturing_compressed_air_support_waste")
            active_loss_pattern_candidates.append("compressed_air_waste")
            active_financial_exposure_candidates.append("operational_savings_not_capturable")
            active_contradiction_targets.append("support_system_vs_process_load")
        if (
            schedule_state in {"not_yet_evidenced", "partially_evidenced"}
            or _contains_any(requestable_blob, "throughput", "shift", "product mix", "capacity", "duty cycle")
        ):
            active_rival_hypotheses.append("manufacturing_throughput_normalization")
            active_comparison_blockers.append("throughput_proxy_and_schedule")
            active_loss_pattern_candidates.extend(["throughput_normalization_block", "idle_equipment"])
            active_financial_exposure_candidates.append("wrong_underwriting_premium")
            active_contradiction_targets.append("throughput_vs_support_system_intensity")
        if _contains_any(requestable_blob, "maintenance", "pm", "work order", "cmms", "downtime"):
            active_rival_hypotheses.append("manufacturing_maintenance_downtime")
            active_loss_pattern_candidates.append("maintenance_downtime_exposure")
            active_financial_exposure_candidates.append("maintenance_downtime_exposure")
            active_contradiction_targets.append("maintenance_reality_vs_efficiency_story")

    return {
        "active_rival_hypotheses": _unique(active_rival_hypotheses),
        "active_comparison_blockers": _unique(active_comparison_blockers),
        "active_loss_pattern_candidates": _unique(active_loss_pattern_candidates),
        "active_financial_exposure_candidates": _unique(active_financial_exposure_candidates),
        "active_contradiction_targets": _unique(active_contradiction_targets),
    }


def build_discovery_case_state(
    *,
    target_definition: dict[str, Any],
    routing_output: dict[str, Any],
    coverage_gaps: list[dict[str, Any]],
    requestable_evidence_items: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    search_budget_register: list[dict[str, Any]],
    case_fingerprint: str,
    asset_context_readiness: dict[str, Any] | None = None,
    runtime_context: dict[str, Any] | None = None,
    routing_plan_compliance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime_context = _as_dict(runtime_context)
    routing_output = _as_dict(routing_output)
    target_definition = _as_dict(target_definition)
    asset_context_readiness = _as_dict(asset_context_readiness)
    routing_plan_compliance = _as_dict(routing_plan_compliance)

    requestable_blob = _requestable_blob(requestable_evidence_items)
    success_summary = _family_counts(attempts, _SUCCESS_STATUSES)
    failure_summary = _family_counts(attempts, _FAILURE_STATUSES)
    success_families = {_text(row.get("source_family")) for row in success_summary}
    target_classification_result = _as_dict(routing_output.get("target_classification_result"))
    technical_scraping_allowed = bool(
        target_classification_result.get("technical_scraping_allowed", routing_output.get("routing_ready"))
    )
    gap_types = _unique([_text(_as_dict(row).get("gap_type")) for row in _as_list(coverage_gaps)])
    gap_severities = {
        _text(_as_dict(row).get("gap_type")): _text(_as_dict(row).get("severity")) or "unknown"
        for row in _as_list(coverage_gaps)
        if _text(_as_dict(row).get("gap_type"))
    }
    asset_context_state = _text(asset_context_readiness.get("state")) or "unknown"
    mandatory_source_gaps = _unique(
        _as_list(routing_plan_compliance.get("mandatory_sources_missing_from_executor"))
        or _as_list(_as_dict(runtime_context.get("case_delta_summary")).get("current_snapshot", {}).get("mandatory_source_gaps"))
    )
    active_regulatory_triggers = _unique(
        _as_list(routing_output.get("regulatory_stack"))
        + _as_list(target_definition.get("jurisdiction_scope"))
    )
    source_yield_memory = _as_dict(_as_dict(runtime_context.get("source_yield_memory_summary")).get("by_source_family"))
    source_acquisition_yield_memory = _as_dict(
        _as_dict(runtime_context.get("source_yield_memory_summary")).get("source_acquisition_yield_memory")
    )

    if not technical_scraping_allowed:
        identity_state = "routing_blocked"
    elif "asset_primary_anchor_missing" in gap_types or "asset_geocode_match" in gap_types:
        identity_state = "public_anchor_missing"
    elif asset_context_state and asset_context_state != "asset_localized":
        identity_state = asset_context_state
    else:
        identity_state = "public_anchor_seeded"

    asset_family = _asset_family(target_definition)
    operator_boundary_state = _infer_state(
        requestable_blob=requestable_blob,
        success_families=success_families,
        keywords=_OPERATOR_BOUNDARY_KEYWORDS,
        relevant_source_families=_OPERATOR_BOUNDARY_SOURCE_FAMILIES,
    )
    schedule_state = _infer_state(
        requestable_blob=requestable_blob,
        success_families=success_families,
        keywords=_SCHEDULE_KEYWORDS,
        relevant_source_families=_SCHEDULE_SOURCE_FAMILIES,
    )
    control_boundary_state = _infer_state(
        requestable_blob=requestable_blob,
        success_families=success_families,
        keywords=_CONTROL_BOUNDARY_KEYWORDS,
        relevant_source_families=_CONTROL_BOUNDARY_SOURCE_FAMILIES,
    )
    utility_context_state = _infer_state(
        requestable_blob=requestable_blob,
        success_families=success_families,
        keywords=_UTILITY_CONTEXT_KEYWORDS,
        relevant_source_families=_UTILITY_CONTEXT_SOURCE_FAMILIES,
    )
    case_pressure = _active_case_pressure(
        asset_family=asset_family,
        requestable_blob=requestable_blob,
        gap_types=gap_types,
        operator_boundary_state=operator_boundary_state,
        schedule_state=schedule_state,
        control_boundary_state=control_boundary_state,
        utility_context_state=utility_context_state,
    )

    return {
        "case_fingerprint": case_fingerprint,
        "asset_fingerprint": _text(target_definition.get("target_id"))
        or _text(target_definition.get("target_identifier"))
        or case_fingerprint,
        "target_identifier": _text(target_definition.get("target_identifier")),
        "target_type": _text(target_definition.get("target_type")),
        "asset_family": asset_family,
        "jurisdiction_scope": _unique(_as_list(target_definition.get("jurisdiction_scope"))),
        "industry_context": {
            "decision_intent": _text(target_definition.get("decision_intent")),
            "report_intent": _text(target_definition.get("report_intent")),
            "owner_entity": _text(target_definition.get("owner_entity")),
            "operator_entity": _text(target_definition.get("operator_entity")),
        },
        "technical_scraping_allowed": technical_scraping_allowed,
        "route_report_type_allowed": _text(routing_output.get("report_type_allowed")),
        "coverage_gap_types": gap_types,
        "coverage_gap_severities": gap_severities,
        "requestable_evidence_items": [dict(row) for row in _as_list(requestable_evidence_items)],
        "active_regulatory_triggers": active_regulatory_triggers,
        "source_family_failures": [_text(row.get("source_family")) for row in failure_summary],
        "source_family_successes": [_text(row.get("source_family")) for row in success_summary],
        "source_family_failure_summary": failure_summary,
        "source_family_success_summary": success_summary,
        "source_family_failure_pressure": _pressure_rows(failure_summary),
        "source_family_success_pressure": _pressure_rows(success_summary),
        "source_family_yield_memory": source_yield_memory,
        "source_acquisition_yield_memory": source_acquisition_yield_memory,
        "browser_success_failure_summary": _as_dict(
            _as_dict(runtime_context.get("source_yield_memory_summary")).get("browser_success_failure_summary")
        ),
        "static_success_failure_summary": _as_dict(
            _as_dict(runtime_context.get("source_yield_memory_summary")).get("static_success_failure_summary")
        ),
        "browser_justified_source_families": _unique(
            _as_list(source_acquisition_yield_memory.get("browser_justified_source_families"))
        ),
        "browser_waste_source_families": _unique(
            _as_list(source_acquisition_yield_memory.get("browser_waste_source_families"))
        ),
        "mandatory_source_gaps": mandatory_source_gaps,
        "budget_state": _budget_state(search_budget_register),
        "identity_state": identity_state,
        "asset_context_state": asset_context_state,
        "operator_boundary_state": operator_boundary_state,
        "schedule_state": schedule_state,
        "control_boundary_state": control_boundary_state,
        "utility_context_state": utility_context_state,
        "active_rival_hypotheses": list(case_pressure.get("active_rival_hypotheses", []) or []),
        "dominant_hypothesis_ids": list(case_pressure.get("active_rival_hypotheses", []) or [])[:2],
        "active_comparison_blockers": list(case_pressure.get("active_comparison_blockers", []) or []),
        "active_loss_pattern_candidates": list(case_pressure.get("active_loss_pattern_candidates", []) or []),
        "active_financial_exposure_candidates": list(case_pressure.get("active_financial_exposure_candidates", []) or []),
        "active_contradiction_targets": list(case_pressure.get("active_contradiction_targets", []) or []),
        "previous_run_progress_signals": _progress_signals(runtime_context),
    }
