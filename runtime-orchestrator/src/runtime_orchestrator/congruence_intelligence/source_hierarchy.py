from __future__ import annotations

from typing import Any

from .schemas import dedupe, list_text, text

SOURCE_HIERARCHY = {
    "geospatial_public_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_public_record",
        "default_used_for": ["asset identity", "geometry", "site boundary context"],
        "allowed_inference_class": ["PUBLIC_RECORD", "asset_identity_support"],
        "prohibited_inference_class": ["local_performance_diagnosis", "savings_claim", "retrofit_economics"],
    },
    "property_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_public_record",
        "default_used_for": ["ownership support", "parcel / tax identity", "asset-level legal context"],
        "allowed_inference_class": ["PUBLIC_RECORD", "asset_identity_support"],
        "prohibited_inference_class": ["local_operational_truth", "owner_capturable_savings_claim"],
    },
    "benchmarking_disclosure_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_disclosure_record",
        "default_used_for": ["benchmarking context", "compliance screening", "screening-level performance context"],
        "allowed_inference_class": ["PUBLIC_RECORD", "bounded_screening_context"],
        "prohibited_inference_class": ["local_waste_diagnosis", "owner_capturable_roi"],
    },
    "regulatory_coverage_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_regulatory_record",
        "default_used_for": ["regulatory applicability", "permit context", "jurisdictional constraint"],
        "allowed_inference_class": ["PUBLIC_RECORD", "regulatory_context_support"],
        "prohibited_inference_class": ["proof_of_current_operation", "compliance_closure"],
    },
    "permit_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_regulatory_record",
        "default_used_for": ["permit-to-physics signals", "regulated process clues", "system change history"],
        "allowed_inference_class": ["PUBLIC_RECORD", "permit_signal"],
        "prohibited_inference_class": ["proof_of_current_operation", "local_equipment_condition"],
    },
    "climate_normals_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_public_record",
        "default_used_for": ["climate context", "weather normalization", "degree-day framing"],
        "allowed_inference_class": ["PUBLIC_RECORD", "climate_context_support"],
        "prohibited_inference_class": ["local_schedule_truth", "local_system_fault_diagnosis"],
    },
    "issuer_financial_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_disclosure_record",
        "default_used_for": ["issuer context", "entity-level financial framing", "capital context"],
        "allowed_inference_class": ["PUBLIC_RECORD", "entity_level_financial_context"],
        "prohibited_inference_class": ["asset_level_unit_economics", "local_operating_margin_truth"],
    },
    "utility_tariff_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "official_tariff_record",
        "default_used_for": ["tariff structure", "demand / reactive exposure framing", "rate logic"],
        "allowed_inference_class": ["PUBLIC_RECORD", "tariff_context_support"],
        "prohibited_inference_class": ["site_specific_bill_truth", "local_charge_realization_without_bill"],
    },
    "technical_sourcebook_record": {
        "source_tier": "tier_1_authoritative_public",
        "source_class": "authoritative_technical_guidance",
        "default_used_for": ["asset-family process understanding", "loss pattern context", "measurement strategy context"],
        "allowed_inference_class": ["STRUCTURAL_PATTERN", "ARCHETYPAL_PRIOR"],
        "prohibited_inference_class": ["local_diagnosis", "local_savings_claim"],
    },
    "utility_bill_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_operational_financial_record",
        "default_used_for": ["local charge reality", "demand and tariff realization", "bounded economics"],
        "allowed_inference_class": ["OBSERVED_FACT", "local_cost_existence"],
        "prohibited_inference_class": ["subsystem_causality_without_metering", "savings_claim_without_binding"],
    },
    "utility_tariff_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_operational_financial_record",
        "default_used_for": ["site rate logic", "demand / PF exposure context", "measurement prioritization"],
        "allowed_inference_class": ["OBSERVED_FACT", "tariff_realization_context"],
        "prohibited_inference_class": ["local_loss_diagnosis_without_binding"],
    },
    "equipment_inventory_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_operational_record",
        "default_used_for": ["dominant equipment classes", "process boundary clues", "maintenance and measurement scoping"],
        "allowed_inference_class": ["OBSERVED_FACT", "bounded_equipment_context"],
        "prohibited_inference_class": ["local_performance_condition_without_testing"],
    },
    "schedule_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_operational_record",
        "default_used_for": ["operating hours", "shift logic", "service-level rhythm"],
        "allowed_inference_class": ["OBSERVED_FACT", "bounded_schedule_context"],
        "prohibited_inference_class": ["actual_load_causality_without_measurement"],
    },
    "submetering_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_metering_record",
        "default_used_for": ["boundary visibility", "local load partitioning", "measurement path selection"],
        "allowed_inference_class": ["OBSERVED_FACT", "bounded_boundary_context"],
        "prohibited_inference_class": ["savings_closure_without_operational_binding"],
    },
    "meter_interval_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_metering_record",
        "default_used_for": ["time-based demand behavior", "load timing", "measurement discrimination"],
        "allowed_inference_class": ["OBSERVED_FACT", "bounded_interval_context"],
        "prohibited_inference_class": ["subsystem_attribution_without_mapping"],
    },
    "lease_matrix_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_contractual_record",
        "default_used_for": ["control boundary", "responsibility matrix", "owner vs operator economics"],
        "allowed_inference_class": ["OBSERVED_FACT", "bounded_control_boundary"],
        "prohibited_inference_class": ["tenant_behavior_truth_without_operational_evidence"],
    },
    "maintenance_contract_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_maintenance_record",
        "default_used_for": ["maintenance program existence", "service coverage", "discipline context"],
        "allowed_inference_class": ["OBSERVED_FACT", "maintenance_program_support"],
        "prohibited_inference_class": ["maintenance_quality_closure_without_logs"],
    },
    "maintenance_log_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_maintenance_record",
        "default_used_for": ["work history", "repeat failure evidence", "downtime context"],
        "allowed_inference_class": ["OBSERVED_FACT", "maintenance_history_support"],
        "prohibited_inference_class": ["asset_condition_closure_without inspection"],
    },
    "cmms_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_maintenance_record",
        "default_used_for": ["workorder patterns", "maintenance maturity", "failure recurrence context"],
        "allowed_inference_class": ["OBSERVED_FACT", "cmms_pattern_support"],
        "prohibited_inference_class": ["future_reliability_closure_without_trend"],
    },
    "bms_trend_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "local_controls_record",
        "default_used_for": ["controls visibility", "schedule enforcement", "plant sequencing evidence"],
        "allowed_inference_class": ["OBSERVED_FACT", "bounded_controls_context"],
        "prohibited_inference_class": ["root_cause_finality_without_cross-binding"],
    },
    "operator_input_record": {
        "source_tier": "tier_local_operator_evidence",
        "source_class": "structured_operator_declared_record",
        "default_used_for": ["operator-declared local context", "service-level framing", "boundary explanation"],
        "allowed_inference_class": ["OBSERVED_FACT", "declared_local_context"],
        "prohibited_inference_class": ["unverified_local_superiority_claim", "direct_savings_claim_without_measurement"],
    },
    "industry_guidance_record": {
        "source_tier": "tier_2_sectoral_guidance",
        "source_class": "sectoral_guidance",
        "default_used_for": ["subsystem expectations", "maintenance and operating norms", "sector process context"],
        "allowed_inference_class": ["STRUCTURAL_PATTERN", "WEAK_SIGNAL"],
        "prohibited_inference_class": ["local_superiority_claim", "local_operational_truth"],
    },
    "vendor_implementation_record": {
        "source_tier": "tier_3_vendor_or_secondary",
        "source_class": "vendor_or_secondary",
        "default_used_for": ["implementation options", "hardware communications options", "integration patterns"],
        "allowed_inference_class": ["implementation_option", "communication_path_option"],
        "prohibited_inference_class": ["local_dominant_loss_diagnosis", "comparability_truth", "local_economics"],
    },
}

_TIER_PRECEDENCE = {
    "tier_1_authoritative_public": 80,
    "tier_local_operator_evidence": 85,
    "tier_2_sectoral_guidance": 40,
    "tier_3_vendor_or_secondary": 20,
}

_AUTHORITY_PRECEDENCE = {
    "high": 20,
    "medium": 10,
    "low": 0,
    "declared_input": -25,
    "field_verified": 30,
}


def source_policy(source_family: str) -> dict[str, Any]:
    family = text(source_family)
    if family in SOURCE_HIERARCHY:
        return dict(SOURCE_HIERARCHY[family])
    return {
        "source_tier": "tier_2_sectoral_guidance",
        "source_class": "uncategorized_external_source",
        "default_used_for": ["bounded context only"],
        "allowed_inference_class": ["WEAK_SIGNAL"],
        "prohibited_inference_class": ["local_diagnosis", "strong_financial_claim"],
    }


def source_precedence_policy(source_row: dict[str, Any]) -> dict[str, Any]:
    family = text(source_row.get("source_family"))
    authority_score = text(source_row.get("authority_score")).lower()
    policy = source_policy(family)
    tier = text(policy.get("source_tier"))
    score = _TIER_PRECEDENCE.get(tier, 30) + _AUTHORITY_PRECEDENCE.get(authority_score, 0)
    haystack = " ".join(
        text(source_row.get(key)).lower()
        for key in ("source_id", "title", "url", "notes")
    )
    if any(token in haystack for token in ("brochure", "listing", "marketing", "flyer", "property page")):
        score -= 25
    if any(token in haystack for token in ("assessor", "parcel", "permit", "utility bill", "lease", "tariff", "cmms")):
        score += 10
    return {
        "source_family": family,
        "source_tier": tier,
        "authority_score": authority_score or "unknown",
        "precedence_score": score,
        "precedence_basis": (
            f"{tier} + authority={authority_score or 'unknown'}"
            + (" - marketing/listing penalty" if any(token in haystack for token in ("brochure", "listing", "marketing", "flyer", "property page")) else "")
            + (" + official/local-record bonus" if any(token in haystack for token in ("assessor", "parcel", "permit", "utility bill", "lease", "tariff", "cmms")) else "")
        ),
    }


def build_authoritative_source_trace_register(
    *,
    asset_family_research_profile: dict[str, Any],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    selected_families = list(asset_family_research_profile.get("authoritative_source_families", []) or [])
    for family in selected_families:
        policy = source_policy(family)
        rows.append(
            {
                "source_family": text(family),
                "source_tier": text(policy.get("source_tier")),
                "source_class": text(policy.get("source_class")),
                "url_or_reference": "",
                "used_for": list(policy.get("default_used_for", []) or []),
                "allowed_inference_class": list(policy.get("allowed_inference_class", []) or []),
                "prohibited_inference_class": list(policy.get("prohibited_inference_class", []) or []),
                "trace_state": "research_route_selected",
            }
        )

    for source in list(source_register or []):
        family = text(source.get("source_family"))
        if not family:
            continue
        policy = source_policy(family)
        rows.append(
            {
                "source_family": family,
                "source_tier": text(policy.get("source_tier")),
                "source_class": text(policy.get("source_class")),
                "url_or_reference": text(source.get("url")) or text(source.get("source_id")) or text(source.get("title")),
                "used_for": dedupe(
                    list_text(source.get("used_for"))
                    + list(policy.get("default_used_for", []) or [])
                ),
                "allowed_inference_class": list(policy.get("allowed_inference_class", []) or []),
                "prohibited_inference_class": list(policy.get("prohibited_inference_class", []) or []),
                "trace_state": "case_source_observed",
            }
        )
    return rows


def _research_source_policy(source_family: str) -> dict[str, Any]:
    family = text(source_family)
    policy = dict(source_policy(family))
    if family == "utility_tariff_record":
        policy["source_tier"] = "tier_1_authoritative_public"
        policy["source_class"] = "official_tariff_record"
        policy["allowed_inference_class"] = ["PUBLIC_RECORD", "tariff_context_support"]
        policy["prohibited_inference_class"] = ["site_specific_bill_truth", "local_charge_realization_without_bill"]
    return policy


def build_authoritative_source_acquisition_trace(
    *,
    asset_family_research_dossier: dict[str, Any],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    observed_by_family: dict[str, list[dict[str, Any]]] = {}
    for source in list(source_register or []):
        family = text(source.get("source_family"))
        if not family:
            continue
        observed_by_family.setdefault(family, []).append(dict(source))

    rows: list[dict[str, Any]] = []
    for family in list(asset_family_research_dossier.get("authoritative_source_families", []) or []):
        policy = _research_source_policy(family)
        observed = observed_by_family.get(text(family), [])
        rows.append(
            {
                "asset_family": text(asset_family_research_dossier.get("asset_family")),
                "source_family": text(family),
                "source_tier": text(policy.get("source_tier")),
                "source_class": text(policy.get("source_class")),
                "coverage_state": "observed_in_case" if observed else "selected_unobserved_in_case",
                "case_source_observed_count": len(observed),
                "case_source_refs": dedupe(
                    [
                        text(source.get("source_id")) or text(source.get("title"))
                        for source in observed
                    ]
                ),
                "allowed_inference_class": list(policy.get("allowed_inference_class", []) or []),
                "prohibited_inference_class": list(policy.get("prohibited_inference_class", []) or []),
                "research_library_version": text(asset_family_research_dossier.get("research_library_version")),
            }
        )
    return rows


def build_family_source_gap_register(
    *,
    authoritative_source_acquisition_trace: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(authoritative_source_acquisition_trace or []):
        if text(row.get("coverage_state")) == "observed_in_case":
            continue
        rows.append(
            {
                "asset_family": text(row.get("asset_family")),
                "source_family": text(row.get("source_family")),
                "gap_code": "selected_authoritative_source_not_yet_observed_in_case",
                "why": f"`{text(row.get('source_family'))}` is part of the family dossier but is not yet observed in the current case evidence.",
                "research_library_version": text(row.get("research_library_version")),
            }
        )
    return rows


def derive_family_source_refresh_state(
    *,
    authoritative_source_acquisition_trace: list[dict[str, Any]],
) -> str:
    rows = list(authoritative_source_acquisition_trace or [])
    if not rows:
        return "no_family_source_selection"
    observed = sum(1 for row in rows if text(row.get("coverage_state")) == "observed_in_case")
    if observed == len(rows):
        return "case_source_coverage_complete"
    if observed > 0:
        return "case_source_coverage_partial"
    return "case_source_coverage_not_started"
