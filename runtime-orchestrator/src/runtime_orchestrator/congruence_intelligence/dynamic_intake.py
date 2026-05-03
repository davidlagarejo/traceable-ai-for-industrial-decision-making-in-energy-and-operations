from __future__ import annotations

from typing import Any

from .schemas import text

_UNRESOLVED_PACK_STATES = {
    "requested_but_absent",
    "public_context_only",
    "uploaded_but_unparsed",
    "parsed_but_weak",
    "partially_evidenced",
}

_PRIORITY_SCORE = {
    "critical": 100,
    "high": 75,
    "medium": 50,
    "low": 25,
}

_DEFAULT_QUESTION_CAP = 8

_COMPARISON_BLOCKER_NEEDS = {
    "logistics_warehouse": {
        "warehouse_subtype_classification",
        "dock_and_service_intensity",
        "refrigeration_presence",
        "operator_boundary_and_control",
        "utility_territory_and_tariff_context",
    },
    "cold_chain": {
        "cold_chain_confirmation",
    },
    "industrial_manufacturing": {
        "process_and_permit_profile",
        "thermal_system_and_utility_mix",
        "throughput_proxy_and_schedule",
    },
}

_LOSS_PATTERN_NEEDS = {
    "warehouse_subtype_classification": ["asset_family_misclassification"],
    "dock_and_service_intensity": ["dock_infiltration", "schedule_waste"],
    "refrigeration_presence": ["refrigeration_load"],
    "operator_boundary_and_control": ["control_boundary_value_leakage"],
    "mhe_charging_and_mechanical_clues": ["mhe_charging_peak_demand", "rooftop_hvac_degradation"],
    "utility_territory_and_tariff_context": ["tariff_exposure_hidden"],
    "cold_chain_confirmation": ["refrigeration_load", "door_infiltration"],
    "process_and_permit_profile": ["maintenance_downtime_exposure", "process_heat_waste"],
    "thermal_system_and_utility_mix": ["compressed_air_waste", "thermal_system_loss", "power_factor_penalty"],
    "throughput_proxy_and_schedule": ["throughput_normalization_block", "idle_equipment"],
}

_QUESTION_METADATA: dict[str, dict[str, Any]] = {
    "warehouse_subtype_and_cold_chain_status": {
        "blocked_claims_if_missing": ["generic_warehouse_eui_claim", "peer_superiority_claim"],
        "comparison_requirements_unlocked": ["asset_subtype_or_temperature_regime"],
        "loss_pattern_tags": ["asset_family_misclassification", "refrigeration_load"],
        "consequence_tags": ["comparison"],
        "financial_exposure_tags": ["wrong_peer_valuation"],
    },
    "warehouse_dock_cycles_and_operating_hours": {
        "blocked_claims_if_missing": ["generic_warehouse_eui_claim", "peer_superiority_claim"],
        "comparison_requirements_unlocked": ["dock_density_and_service_intensity"],
        "loss_pattern_tags": ["dock_infiltration", "schedule_waste"],
        "consequence_tags": ["comparison"],
        "financial_exposure_tags": ["wrong_underwriting_premium"],
    },
    "warehouse_mhe_charging_profile": {
        "blocked_claims_if_missing": ["demand_charge_claim", "tariff_exposure_claim"],
        "comparison_requirements_unlocked": ["control_boundary_and_tariff"],
        "loss_pattern_tags": ["mhe_charging_peak_demand"],
        "consequence_tags": ["tariff"],
        "financial_exposure_tags": ["demand_charge_exposure_hidden"],
    },
    "warehouse_control_boundary": {
        "blocked_claims_if_missing": ["owner_capturable_roi_claim", "retrofit_capture_claim"],
        "comparison_requirements_unlocked": ["control_boundary_and_tariff"],
        "loss_pattern_tags": ["control_boundary_value_leakage"],
        "consequence_tags": ["control_boundary"],
        "financial_exposure_tags": ["tenant_operator_value_leakage"],
    },
    "warehouse_hvac_mechanical_context": {
        "blocked_claims_if_missing": ["mechanical_loss_claim"],
        "comparison_requirements_unlocked": [],
        "loss_pattern_tags": ["rooftop_hvac_degradation", "dock_infiltration"],
        "consequence_tags": ["loss_pattern"],
        "financial_exposure_tags": ["wrong_retrofit_sequencing"],
    },
    "cold_chain_temperature_regime": {
        "blocked_claims_if_missing": ["peer_superiority_claim", "cold_chain_claim"],
        "comparison_requirements_unlocked": ["asset_subtype_or_temperature_regime"],
        "loss_pattern_tags": ["refrigeration_load", "door_infiltration"],
        "consequence_tags": ["comparison", "loss_pattern"],
        "financial_exposure_tags": ["wrong_peer_valuation"],
    },
    "manufacturing_process_and_thermal_lane": {
        "blocked_claims_if_missing": ["process_energy_claim", "thermal_lane_claim"],
        "comparison_requirements_unlocked": ["process_type_and_thermal_lane"],
        "loss_pattern_tags": ["process_heat_waste", "thermal_system_loss"],
        "consequence_tags": ["comparison", "loss_pattern"],
        "financial_exposure_tags": ["wrong_retrofit_sequencing"],
    },
    "manufacturing_compressed_air_use": {
        "blocked_claims_if_missing": ["compressed_air_savings_claim"],
        "comparison_requirements_unlocked": ["support_system_stack"],
        "loss_pattern_tags": ["compressed_air_waste"],
        "consequence_tags": ["loss_pattern"],
        "financial_exposure_tags": ["operational_savings_not_capturable"],
    },
    "manufacturing_throughput_and_product_mix": {
        "blocked_claims_if_missing": ["peer_superiority_claim", "throughput_normalized_claim"],
        "comparison_requirements_unlocked": ["throughput_product_mix_and_schedule"],
        "loss_pattern_tags": ["throughput_normalization_block", "idle_equipment"],
        "consequence_tags": ["comparison"],
        "financial_exposure_tags": ["wrong_underwriting_premium"],
    },
    "manufacturing_maintenance_ownership": {
        "blocked_claims_if_missing": ["maintenance_maturity_claim", "downtime_economics_claim"],
        "comparison_requirements_unlocked": [],
        "loss_pattern_tags": ["maintenance_downtime_exposure"],
        "consequence_tags": ["control_boundary", "loss_pattern"],
        "financial_exposure_tags": ["maintenance_downtime_exposure"],
    },
    "utility_bill_history": {
        "blocked_claims_if_missing": ["cost_driver_claim", "roi_claim"],
        "comparison_requirements_unlocked": [],
        "loss_pattern_tags": ["tariff_exposure_hidden"],
        "consequence_tags": ["tariff"],
        "financial_exposure_tags": ["operational_savings_not_capturable"],
    },
    "utility_tariff_or_rate_class": {
        "blocked_claims_if_missing": ["tariff_exposure_claim"],
        "comparison_requirements_unlocked": ["control_boundary_and_tariff"],
        "loss_pattern_tags": ["tariff_exposure_hidden"],
        "consequence_tags": ["tariff"],
        "financial_exposure_tags": ["demand_charge_exposure_hidden"],
    },
    "metering_and_boundary_map": {
        "blocked_claims_if_missing": ["asset_level_cost_attribution_claim", "owner_capturable_roi_claim"],
        "comparison_requirements_unlocked": ["control_boundary_and_tariff"],
        "loss_pattern_tags": ["control_boundary_value_leakage"],
        "consequence_tags": ["control_boundary"],
        "financial_exposure_tags": ["under_instrumentation_risk"],
    },
}

_QUESTION_LIBRARY: dict[str, list[dict[str, Any]]] = {
    "logistics_warehouse": [
        {
            "question_id": "warehouse_subtype_and_cold_chain_status",
            "need_ids": ["warehouse_subtype_classification", "refrigeration_presence"],
            "pack_names": ["throughput_schedule_pack"],
            "priority": "critical",
            "required_from": "operator / facility manager / asset manager",
            "intake_question": (
                "Is the facility dry-only, cold-chain, mixed-temperature, fulfillment, cross-dock, "
                "or storage-focused?"
            ),
            "why_needed": (
                "Subtype changes the asset family, the fair comparison basis, and which loss patterns are even plausible."
            ),
            "hypothesis_it_discriminates": (
                "generic warehouse intensity problem vs subtype-driven operational load"
            ),
            "rival_hypotheses": [
                "This is a dry warehouse with service-level complexity.",
                "This is cold-chain or mixed-temperature and area-based comparison is invalid.",
            ],
            "claim_impact_if_missing": (
                "No generic warehouse EUI or peer claim until dry/cold-chain status is bounded."
            ),
        },
        {
            "question_id": "warehouse_dock_cycles_and_operating_hours",
            "need_ids": ["dock_and_service_intensity"],
            "pack_names": ["throughput_schedule_pack"],
            "priority": "critical",
            "required_from": "operator / facility manager",
            "intake_question": (
                "How many active dock doors are there, what are typical dock cycles, and what are the operating hours / shifts by day?"
            ),
            "why_needed": (
                "Dock intensity and operating windows often explain why area-based energy benchmarks punish high-service logistics nodes."
            ),
            "hypothesis_it_discriminates": (
                "service-level intensity denominator problem vs controllable building-waste problem"
            ),
            "rival_hypotheses": [
                "Energy intensity is driven by dock throughput and service windows.",
                "Energy intensity is driven by controllable HVAC / lighting waste.",
            ],
            "claim_impact_if_missing": (
                "No fair peer set or EUI interpretation until dock intensity and schedule are bounded."
            ),
        },
        {
            "question_id": "warehouse_mhe_charging_profile",
            "need_ids": ["mhe_charging_and_mechanical_clues", "utility_territory_and_tariff_context"],
            "pack_names": ["utility_bill_pack", "utility_tariff_pack", "throughput_schedule_pack"],
            "priority": "critical",
            "required_from": "operator / facility manager / energy manager",
            "intake_question": (
                "Do material-handling vehicles charge on-site? If yes, how many, with what charger types, and during what charging windows?"
            ),
            "why_needed": (
                "Charging windows can drive peak demand and make the cost problem tariff orchestration, not annual efficiency."
            ),
            "hypothesis_it_discriminates": (
                "demand-charge orchestration problem vs generic energy inefficiency problem"
            ),
            "rival_hypotheses": [
                "Demand cost is being driven by charging peaks.",
                "High cost is driven by annual consumption or HVAC / lighting inefficiency.",
            ],
            "claim_impact_if_missing": (
                "No demand-charge or tariff-exposure framing should harden until charging behavior is known."
            ),
        },
        {
            "question_id": "warehouse_control_boundary",
            "need_ids": ["operator_boundary_and_control"],
            "pack_names": ["lease_responsibility_pack", "metering_boundary_pack"],
            "priority": "critical",
            "required_from": "owner / operator / asset manager",
            "intake_question": (
                "Who controls docks, charging schedules, HVAC schedules, and who pays utility / CAPEX across the site?"
            ),
            "why_needed": (
                "A broken owner-operator boundary can make savings uncapturable even when the physical problem is real."
            ),
            "hypothesis_it_discriminates": (
                "owner-capturable efficiency opportunity vs control-boundary value leakage"
            ),
            "rival_hypotheses": [
                "The owner can capture the value of an energy intervention.",
                "The operator controls the dominant drivers and value leaks across the boundary.",
            ],
            "claim_impact_if_missing": (
                "No owner-capturable retrofit or ROI claim until the control boundary is evidenced."
            ),
        },
        {
            "question_id": "warehouse_hvac_mechanical_context",
            "need_ids": ["mhe_charging_and_mechanical_clues"],
            "pack_names": ["equipment_inventory_pack"],
            "priority": "high",
            "required_from": "facility engineer / maintenance manager",
            "intake_question": (
                "What HVAC, rooftop, ventilation, or conditioned-storage systems serve the facility, and which zones do they cover?"
            ),
            "why_needed": (
                "Mechanical context determines whether the dominant variable is logistics-envelope interaction or generic HVAC degradation."
            ),
            "hypothesis_it_discriminates": (
                "logistics-interface thermal loss vs equipment-efficiency problem"
            ),
            "rival_hypotheses": [
                "Loss is dominated by dock / air exchange interaction.",
                "Loss is dominated by poorly performing HVAC or rooftop equipment.",
            ],
            "claim_impact_if_missing": (
                "No mechanical-loss story should harden until conditioning topology is bounded."
            ),
        },
    ],
    "cold_chain": [
        {
            "question_id": "cold_chain_temperature_regime",
            "need_ids": ["cold_chain_confirmation"],
            "pack_names": ["throughput_schedule_pack", "equipment_inventory_pack"],
            "priority": "critical",
            "required_from": "operator / cold-storage manager",
            "intake_question": (
                "What temperature bands, refrigerated zones, and door-traffic regimes define the facility?"
            ),
            "why_needed": (
                "Temperature regime determines valid peers, refrigeration duty, and whether door losses dominate."
            ),
            "hypothesis_it_discriminates": (
                "refrigeration-duty problem vs generic warehouse comparison frame"
            ),
            "rival_hypotheses": [
                "The dominant driver is refrigeration and cold-chain duty.",
                "The facility behaves like a generic warehouse.",
            ],
            "claim_impact_if_missing": (
                "No warehouse-like peer claim until cold-chain regime is bounded."
            ),
        },
    ],
    "industrial_manufacturing": [
        {
            "question_id": "manufacturing_process_and_thermal_lane",
            "need_ids": ["process_and_permit_profile", "thermal_system_and_utility_mix"],
            "pack_names": ["equipment_inventory_pack", "permit_detail_pack"],
            "priority": "critical",
            "required_from": "plant manager / process engineer / EHS lead",
            "intake_question": (
                "What are the primary process lines, and which boilers, furnaces, steam, chilled-water, or other thermal systems serve them?"
            ),
            "why_needed": (
                "Thermal duty and process lane determine whether the benchmark frame is physically coherent."
            ),
            "hypothesis_it_discriminates": (
                "structural process load vs support-system waste"
            ),
            "rival_hypotheses": [
                "Energy intensity is dominated by the process and thermal duty itself.",
                "Energy intensity is dominated by avoidable support-system or thermal losses.",
            ],
            "claim_impact_if_missing": (
                "No process-energy interpretation until the dominant thermal lane is bounded."
            ),
        },
        {
            "question_id": "manufacturing_compressed_air_use",
            "need_ids": ["thermal_system_and_utility_mix"],
            "pack_names": ["equipment_inventory_pack"],
            "priority": "critical",
            "required_from": "maintenance manager / process engineer",
            "intake_question": (
                "Is compressed air used for cooling, cleaning, agitation, actuation, packaging, or production tooling? Where is it used in the process?"
            ),
            "why_needed": (
                "Inappropriate compressed-air use can dominate waste and completely change the intervention logic."
            ),
            "hypothesis_it_discriminates": (
                "support-system compressed-air waste vs legitimate process load"
            ),
            "rival_hypotheses": [
                "Compressed air is a major avoidable support-system waste source.",
                "Compressed air use is structurally tied to the production process.",
            ],
            "claim_impact_if_missing": (
                "No compressed-air savings logic should harden without use-case evidence."
            ),
        },
        {
            "question_id": "manufacturing_throughput_and_product_mix",
            "need_ids": ["throughput_proxy_and_schedule"],
            "pack_names": ["throughput_schedule_pack"],
            "priority": "critical",
            "required_from": "plant manager / production planner",
            "intake_question": (
                "What are throughput by shift, duty cycle, and product mix for the main process lines?"
            ),
            "why_needed": (
                "Manufacturing comparability fails without throughput and product-mix normalization."
            ),
            "hypothesis_it_discriminates": (
                "throughput-normalized intensity problem vs false per-area or per-site comparison"
            ),
            "rival_hypotheses": [
                "The site is energy-intensive because throughput or product mix is heavy.",
                "The site is energy-intensive because utilities and support systems are wasteful.",
            ],
            "claim_impact_if_missing": (
                "No peer or superiority claim until throughput and product mix are bounded."
            ),
        },
        {
            "question_id": "manufacturing_maintenance_ownership",
            "need_ids": ["process_and_permit_profile"],
            "pack_names": ["maintenance_proof_pack", "cmms_or_workorder_pack"],
            "priority": "high",
            "required_from": "maintenance manager / plant manager",
            "intake_question": (
                "Who owns maintenance for critical utilities and process lines, and where do PM logs, work orders, and downtime records live?"
            ),
            "why_needed": (
                "Reactive maintenance can dominate economics, but the framework needs ownership and proof before making that claim."
            ),
            "hypothesis_it_discriminates": (
                "maintenance-driven downtime exposure vs pure efficiency problem"
            ),
            "rival_hypotheses": [
                "Downtime and maintenance reality dominate the business case.",
                "The issue is primarily energy waste with stable maintenance maturity.",
            ],
            "claim_impact_if_missing": (
                "No maintenance-maturity or downtime-economics claim until ownership and proof paths are known."
            ),
        },
    ],
}

_GENERIC_PACK_FALLBACKS: list[dict[str, Any]] = [
    {
        "question_id": "utility_bill_history",
        "pack_names": ["utility_bill_pack"],
        "priority": "high",
        "required_from": "owner / accounting / operator",
        "intake_question": "Please provide 12 months of utility bills, including any demand-charge pages or interval summaries.",
        "why_needed": "Bills are the minimum anchor for cost-driver and tariff interpretation.",
        "hypothesis_it_discriminates": "annual-consumption problem vs tariff / demand-structure problem",
        "rival_hypotheses": [
            "Total annual consumption is the main cost driver.",
            "Demand, tariff design, or operating windows dominate the cost story.",
        ],
        "claim_impact_if_missing": "Cost-driver claims remain screening-only until bills are available.",
    },
    {
        "question_id": "utility_tariff_or_rate_class",
        "pack_names": ["utility_tariff_pack"],
        "priority": "high",
        "required_from": "owner / accounting / operator",
        "intake_question": "What utility tariff or rate class applies to the site, and can you provide the tariff sheet or bill page showing it?",
        "why_needed": "Without tariff identity, the framework cannot distinguish efficiency from tariff-structure exposure.",
        "hypothesis_it_discriminates": "tariff orchestration problem vs pure equipment-efficiency problem",
        "rival_hypotheses": [
            "Tariff design and demand windows dominate cost exposure.",
            "Cost exposure is explained by annual energy use alone.",
        ],
        "claim_impact_if_missing": "Tariff-exposure claims remain conditional until rate class is confirmed.",
    },
    {
        "question_id": "metering_and_boundary_map",
        "pack_names": ["metering_boundary_pack"],
        "priority": "high",
        "required_from": "owner / operator / energy manager",
        "intake_question": "What meters, submeters, and cost boundaries exist, and which spaces or systems do they actually cover?",
        "why_needed": "Metering boundary determines whether measured energy can be attributed to the asset and decision-maker in scope.",
        "hypothesis_it_discriminates": "owner-capturable signal vs mixed-boundary data contamination",
        "rival_hypotheses": [
            "The available utility data maps cleanly to the asset and decision boundary.",
            "The data mixes spaces, tenants, or utilities in a way that invalidates interpretation.",
        ],
        "claim_impact_if_missing": "No asset-level cost or savings attribution should harden until metering boundary is mapped.",
    },
]


def _priority_score(priority: str) -> int:
    return _PRIORITY_SCORE.get(text(priority).lower(), 0)


def _budget_state(operational_intake_pack: dict[str, Any]) -> str:
    for row in list(operational_intake_pack.get("search_budget_register", []) or []):
        if text(row.get("budget_scope")) == "total_public_discovery":
            return text(row.get("budget_state")) or "bounded"
    return "bounded"


def _pack_state_map(operational_intake_pack: dict[str, Any]) -> dict[str, str]:
    rows = list(operational_intake_pack.get("diligence_pack_register", []) or [])
    return {
        text(row.get("pack_name")): text(row.get("current_state"))
        for row in rows
        if text(row.get("pack_name"))
    }


def _need_map(discovery_need_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("need_id")): row
        for row in list(discovery_need_register or [])
        if text(row.get("need_id"))
    }


def _stop_map(stop_condition_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("path_id")): row
        for row in list(stop_condition_register or [])
        if text(row.get("path_id"))
    }


def _question_metadata(spec: dict[str, Any]) -> dict[str, Any]:
    question_id = text(spec.get("question_id"))
    metadata = dict(_QUESTION_METADATA.get(question_id, {}) or {})
    if "supports_hypotheses" not in metadata:
        metadata["supports_hypotheses"] = [text(item) for item in list(spec.get("rival_hypotheses", []) or []) if text(item)]
    if "falsifies_hypotheses" not in metadata:
        metadata["falsifies_hypotheses"] = []
    metadata.setdefault("blocked_claims_if_missing", [])
    metadata.setdefault("comparison_requirements_unlocked", [])
    metadata.setdefault("loss_pattern_tags", [])
    metadata.setdefault("consequence_tags", [])
    metadata.setdefault("financial_exposure_tags", [])
    return metadata


def build_congruence_case_state(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    discovery_need_register: list[dict[str, Any]],
    target_definition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    asset_family = text(asset_family_research_profile.get("asset_family")) or "commercial_building"
    active_need_ids = [text(row.get("need_id")) for row in list(discovery_need_register or []) if text(row.get("need_id"))]
    unresolved_pack_names = [
        pack_name
        for pack_name, state in _pack_state_map(operational_intake_pack or {}).items()
        if state in _UNRESOLVED_PACK_STATES
    ]
    comparison_blockers = [
        need_id
        for need_id in active_need_ids
        if need_id in _COMPARISON_BLOCKER_NEEDS.get(asset_family, set())
    ]
    active_loss_pattern_tags: list[str] = []
    for need_id in active_need_ids:
        for tag in _LOSS_PATTERN_NEEDS.get(need_id, []):
            if tag not in active_loss_pattern_tags:
                active_loss_pattern_tags.append(tag)
    tariff_exposure_active = bool(operational_intake_pack.get("tariff_exposure_register")) or (
        "utility_territory_and_tariff_context" in active_need_ids
        or any(pack_name in unresolved_pack_names for pack_name in {"utility_bill_pack", "utility_tariff_pack"})
    )
    control_boundary_active = bool(operational_intake_pack.get("control_boundary_evidence_register")) or (
        "operator_boundary_and_control" in active_need_ids
        or any(pack_name in unresolved_pack_names for pack_name in {"lease_responsibility_pack", "metering_boundary_pack"})
    )
    maintenance_reality_active = bool(operational_intake_pack.get("maintenance_proof_evidence_register")) or (
        "maintenance_proof_pack" in unresolved_pack_names
        or "cmms_or_workorder_pack" in unresolved_pack_names
    )
    financial_exposure_priority: list[str] = []
    if tariff_exposure_active:
        financial_exposure_priority.append("demand_charge_exposure_hidden")
    if control_boundary_active:
        financial_exposure_priority.append("tenant_operator_value_leakage")
    if maintenance_reality_active:
        financial_exposure_priority.append("maintenance_downtime_exposure")
    if comparison_blockers:
        financial_exposure_priority.extend(["wrong_peer_valuation", "wrong_underwriting_premium"])
    financial_exposure_priority = [tag for idx, tag in enumerate(financial_exposure_priority) if tag and tag not in financial_exposure_priority[:idx]]
    return {
        "asset_family": asset_family,
        "active_need_ids": active_need_ids,
        "comparison_blockers": comparison_blockers,
        "active_loss_pattern_tags": active_loss_pattern_tags,
        "unresolved_pack_names": unresolved_pack_names,
        "tariff_exposure_active": tariff_exposure_active,
        "control_boundary_active": control_boundary_active,
        "maintenance_reality_active": maintenance_reality_active,
        "financial_exposure_priority": financial_exposure_priority,
        "search_budget_state": _budget_state(operational_intake_pack or {}),
        "decision_intent": text((target_definition or {}).get("decision_intent")),
        "report_intent": text((target_definition or {}).get("report_intent")),
    }


def _spec_triggered(
    *,
    spec: dict[str, Any],
    needs_by_id: dict[str, dict[str, Any]],
    pack_states: dict[str, str],
) -> bool:
    need_ids = [text(value) for value in list(spec.get("need_ids", []) or []) if text(value)]
    pack_names = [text(value) for value in list(spec.get("pack_names", []) or []) if text(value)]

    need_hit = any(need_id in needs_by_id for need_id in need_ids) if need_ids else False
    pack_hit = any(pack_states.get(pack_name) in _UNRESOLVED_PACK_STATES for pack_name in pack_names)
    return need_hit or pack_hit


def _build_trigger_text(
    *,
    spec: dict[str, Any],
    needs_by_id: dict[str, dict[str, Any]],
    pack_states: dict[str, str],
) -> str:
    parts: list[str] = []
    for need_id in list(spec.get("need_ids", []) or []):
        row = needs_by_id.get(text(need_id))
        if row:
            parts.append(text(row.get("discovery_need")) or text(need_id))
    for pack_name in list(spec.get("pack_names", []) or []):
        state = pack_states.get(text(pack_name))
        if state in _UNRESOLVED_PACK_STATES:
            parts.append(f"{text(pack_name)} is {state}")
    return "; ".join(part for part in parts if part)


def _build_public_search_context(
    *,
    spec: dict[str, Any],
    needs_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    context: list[str] = []
    for need_id in list(spec.get("need_ids", []) or []):
        row = needs_by_id.get(text(need_id))
        if not row:
            continue
        for family in list(row.get("search_families_to_explore", []) or []):
            label = text(family)
            if label and label not in context:
                context.append(label)
    return context


def _build_escalation_condition(
    *,
    spec: dict[str, Any],
    stop_by_path: dict[str, dict[str, Any]],
) -> str:
    escalations: list[str] = []
    for path_id in list(spec.get("need_ids", []) or []) + list(spec.get("pack_names", []) or []):
        row = stop_by_path.get(text(path_id))
        escalation = text(row.get("escalation_condition")) if row else ""
        if escalation and escalation not in escalations:
            escalations.append(escalation)
    return " ".join(escalations)


def _governed_question_library(asset_family: str) -> list[dict[str, Any]]:
    return list(_QUESTION_LIBRARY.get(asset_family, []) or []) + list(_GENERIC_PACK_FALLBACKS)


def build_decision_context_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    discovery_need_register: list[dict[str, Any]],
    congruence_case_state: dict[str, Any] | None = None,
    target_definition: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    congruence_case_state = (
        dict(congruence_case_state)
        if isinstance(congruence_case_state, dict)
        else build_congruence_case_state(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            target_definition=target_definition,
        )
    )
    asset_family = text(asset_family_research_profile.get("asset_family")) or "commercial_building"
    register: list[dict[str, Any]] = []

    def add_row(
        *,
        context_type: str,
        context_value: str,
        context_state: str,
        source_basis: str,
        why_it_matters: str,
    ) -> None:
        value = text(context_value)
        if not value:
            return
        register.append(
            {
                "asset_family": asset_family,
                "context_type": context_type,
                "context_value": value,
                "context_state": context_state,
                "source_basis": source_basis,
                "why_it_matters": why_it_matters,
            }
        )

    add_row(
        context_type="decision_intent",
        context_value=text(congruence_case_state.get("decision_intent")) or text((target_definition or {}).get("decision_intent")),
        context_state="declared",
        source_basis="target_definition",
        why_it_matters="Decision intent should shape which questions discriminate value, risk, and action admissibility.",
    )
    add_row(
        context_type="report_intent",
        context_value=text(congruence_case_state.get("report_intent")) or text((target_definition or {}).get("report_intent")),
        context_state="declared",
        source_basis="target_definition",
        why_it_matters="Report intent should constrain how much unresolved ambiguity can survive into the final output mode.",
    )
    add_row(
        context_type="search_budget_state",
        context_value=text(congruence_case_state.get("search_budget_state")) or "bounded",
        context_state="derived",
        source_basis="search_budget_register",
        why_it_matters="Search budget state determines whether the next move is more public search, intake escalation, or claim downgrade.",
    )

    for blocker in list(congruence_case_state.get("comparison_blockers", []) or []):
        add_row(
            context_type="comparison_blocker",
            context_value=text(blocker),
            context_state="active",
            source_basis="congruence_case_state",
            why_it_matters="Comparison blockers should directly pressure which questions are synthesized before any peer claim is allowed.",
        )
    for hypothesis_id in list(congruence_case_state.get("dominant_hypothesis_ids", []) or []):
        add_row(
            context_type="dominant_hypothesis",
            context_value=text(hypothesis_id),
            context_state="active",
            source_basis="hypothesis_backbone",
            why_it_matters="Dominant hypotheses should bias intake toward the minimum evidence that can discriminate the leading rival frames.",
        )
    for tag in list(congruence_case_state.get("active_loss_pattern_tags", []) or []):
        add_row(
            context_type="loss_pattern",
            context_value=text(tag),
            context_state="active",
            source_basis="congruence_case_state",
            why_it_matters="Active loss-pattern plausibility should shape which operator questions are worth asking next.",
        )
    for tag in list(congruence_case_state.get("financial_exposure_priority", []) or []):
        add_row(
            context_type="financial_exposure",
            context_value=text(tag),
            context_state="active",
            source_basis="congruence_case_state",
            why_it_matters="Financial exposure priority helps separate economically material questions from generic completeness questions.",
        )
    for pack_name in list(congruence_case_state.get("unresolved_pack_names", []) or []):
        add_row(
            context_type="unresolved_pack",
            context_value=text(pack_name),
            context_state="unresolved",
            source_basis="operational_intake_pack",
            why_it_matters="Unresolved packs indicate which evidence lanes remain materially incomplete and should still drive questions.",
        )

    return register


def _question_candidate_row(
    *,
    asset_family: str,
    spec: dict[str, Any],
    needs_by_id: dict[str, dict[str, Any]],
    pack_states: dict[str, str],
    stop_by_path: dict[str, dict[str, Any]],
    congruence_case_state: dict[str, Any],
) -> dict[str, Any]:
    priority = text(spec.get("priority")).lower() or "medium"
    metadata = _question_metadata(spec)
    priority_score = _priority_score(priority)
    dominant_hypothesis_labels = {
        text(item)
        for item in list(congruence_case_state.get("dominant_hypothesis_labels", []) or [])
        if text(item)
    }
    dominant_hypothesis_ids = [
        text(item)
        for item in list(congruence_case_state.get("dominant_hypothesis_ids", []) or [])
        if text(item)
    ]
    supports_hits = [
        label
        for label in list(metadata.get("supports_hypotheses", []) or [])
        if text(label) in dominant_hypothesis_labels
    ]
    falsifies_hits = [
        label
        for label in list(metadata.get("falsifies_hypotheses", []) or [])
        if text(label) in dominant_hypothesis_labels
    ]
    rival_hits = [
        label
        for label in list(spec.get("rival_hypotheses", []) or [])
        if text(label) in dominant_hypothesis_labels
    ]
    comparison_hits = [
        requirement
        for requirement in list(metadata.get("comparison_requirements_unlocked", []) or [])
        if requirement and congruence_case_state.get("comparison_blockers")
    ]
    loss_pattern_hits = [
        tag
        for tag in list(metadata.get("loss_pattern_tags", []) or [])
        if tag in list(congruence_case_state.get("active_loss_pattern_tags", []) or [])
    ]
    financial_hits = [
        tag
        for tag in list(metadata.get("financial_exposure_tags", []) or [])
        if tag in list(congruence_case_state.get("financial_exposure_priority", []) or [])
    ]
    question_score_components = {
        "priority_base": priority_score,
        "hypothesis_discrimination_value": min(len(list(spec.get("rival_hypotheses", []) or [])) * 10, 20),
        "claim_blocking_value": min(len(list(metadata.get("blocked_claims_if_missing", []) or [])) * 8, 24),
        "comparison_unlock_value": min(len(comparison_hits) * 16, 32),
        "loss_pattern_falsification_value": min(len(loss_pattern_hits) * 12, 24),
        "tariff_consequence_value": (
            18
            if congruence_case_state.get("tariff_exposure_active")
            and "tariff" in list(metadata.get("consequence_tags", []) or [])
            else 0
        ),
        "control_boundary_consequence_value": (
            18
            if congruence_case_state.get("control_boundary_active")
            and "control_boundary" in list(metadata.get("consequence_tags", []) or [])
            else 0
        ),
        "financial_exposure_consequence_value": min(len(financial_hits) * 12, 24),
        "dominant_hypothesis_alignment_value": min(
            len(supports_hits) * 12 + len(falsifies_hits) * 10 + len(rival_hits) * 8,
            24,
        ),
        "public_search_exhaustion_value": (
            8
            if congruence_case_state.get("search_budget_state") == "exhausted"
            and (
                list(spec.get("need_ids", []) or [])
                or list(spec.get("pack_names", []) or [])
            )
            else 0
        ),
    }
    activation_reasons: list[str] = []
    if question_score_components["comparison_unlock_value"] > 0:
        activation_reasons.extend(f"comparison_blocker:{value}" for value in list(congruence_case_state.get("comparison_blockers", []) or [])[:2])
    if question_score_components["loss_pattern_falsification_value"] > 0:
        activation_reasons.extend(f"loss_pattern:{value}" for value in loss_pattern_hits[:2])
    if question_score_components["tariff_consequence_value"] > 0:
        activation_reasons.append("tariff_exposure_priority")
    if question_score_components["control_boundary_consequence_value"] > 0:
        activation_reasons.append("control_boundary_priority")
    if question_score_components["financial_exposure_consequence_value"] > 0:
        activation_reasons.extend(f"financial_exposure:{value}" for value in financial_hits[:2])
    if question_score_components["dominant_hypothesis_alignment_value"] > 0:
        activation_reasons.extend(f"dominant_hypothesis:{value}" for value in dominant_hypothesis_ids[:2])
    if question_score_components["public_search_exhaustion_value"] > 0:
        activation_reasons.append("public_search_exhausted")
    question_score = sum(int(value) for value in question_score_components.values())
    decision_context_keys: list[str] = []
    decision_intent = text(congruence_case_state.get("decision_intent"))
    report_intent = text(congruence_case_state.get("report_intent"))
    budget_state = text(congruence_case_state.get("search_budget_state"))
    if decision_intent:
        decision_context_keys.append(f"decision_intent:{decision_intent}")
    if report_intent:
        decision_context_keys.append(f"report_intent:{report_intent}")
    if budget_state:
        decision_context_keys.append(f"search_budget_state:{budget_state}")
    decision_context_keys.extend(
        f"comparison_blocker:{value}" for value in list(congruence_case_state.get("comparison_blockers", []) or [])[:2]
    )
    decision_context_keys.extend(f"loss_pattern:{value}" for value in loss_pattern_hits[:2])
    decision_context_keys.extend(f"financial_exposure:{value}" for value in financial_hits[:2])
    decision_context_keys.extend(f"dominant_hypothesis:{value}" for value in dominant_hypothesis_ids[:2])
    for pack_name in list(spec.get("pack_names", []) or []):
        state = pack_states.get(text(pack_name))
        if state in _UNRESOLVED_PACK_STATES:
            decision_context_keys.append(f"unresolved_pack:{text(pack_name)}")
    candidate_trigger_basis: list[str] = []
    candidate_trigger_basis.extend(
        f"need:{value}" for value in list(spec.get("need_ids", []) or []) if value in needs_by_id
    )
    candidate_trigger_basis.extend(
        f"pack:{text(pack_name)}:{pack_states.get(text(pack_name), '')}"
        for pack_name in list(spec.get("pack_names", []) or [])
        if pack_states.get(text(pack_name)) in _UNRESOLVED_PACK_STATES
    )
    return {
        "question_id": text(spec.get("question_id")),
        "asset_family": asset_family,
        "candidate_origin": "state_native_synthesis",
        "candidate_status": "triggered",
        "candidate_trigger_basis": candidate_trigger_basis,
        "decision_context_keys": decision_context_keys,
        "trigger": _build_trigger_text(
            spec=spec,
            needs_by_id=needs_by_id,
            pack_states=pack_states,
        ),
        "priority": priority,
        "priority_score": priority_score,
        "question_score": question_score,
        "question_score_components": question_score_components,
        "activation_reasons": activation_reasons,
        "linked_need_ids": [text(item) for item in list(spec.get("need_ids", []) or []) if text(item)],
        "linked_pack_names": [text(item) for item in list(spec.get("pack_names", []) or []) if text(item)],
        "public_search_context": _build_public_search_context(
            spec=spec,
            needs_by_id=needs_by_id,
        ),
        "escalation_condition": _build_escalation_condition(
            spec=spec,
            stop_by_path=stop_by_path,
        ),
        "normalization_required": True,
    }


def build_question_candidate_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    discovery_need_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
    congruence_case_state: dict[str, Any],
    decision_context_register: list[dict[str, Any]] | None = None,
    target_definition: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(congruence_case_state, dict):
        congruence_case_state = build_congruence_case_state(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            target_definition=target_definition,
        )
    decision_context_register = (
        list(decision_context_register or [])
        if isinstance(decision_context_register, list)
        else build_decision_context_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            congruence_case_state=congruence_case_state,
            target_definition=target_definition,
        )
    )
    asset_family = text(asset_family_research_profile.get("asset_family")) or "commercial_building"
    needs_by_id = _need_map(discovery_need_register)
    pack_states = _pack_state_map(operational_intake_pack or {})
    stop_by_path = _stop_map(stop_condition_register)

    question_register: list[dict[str, Any]] = []
    seen: set[str] = set()
    library = _governed_question_library(asset_family)
    active_context_keys = {
        f"{text(row.get('context_type'))}:{text(row.get('context_value'))}"
        for row in list(decision_context_register or [])
        if text(row.get("context_type")) and text(row.get("context_value"))
    }

    for spec in library:
        question_id = text(spec.get("question_id"))
        if not question_id or question_id in seen:
            continue
        if not _spec_triggered(
            spec=spec,
            needs_by_id=needs_by_id,
            pack_states=pack_states,
        ):
            continue
        seen.add(question_id)
        row = _question_candidate_row(
            asset_family=asset_family,
            spec=spec,
            needs_by_id=needs_by_id,
            pack_states=pack_states,
            stop_by_path=stop_by_path,
            congruence_case_state=congruence_case_state,
        )
        row["candidate_context_overlap_count"] = len(
            [value for value in list(row.get("decision_context_keys", []) or []) if value in active_context_keys]
        )
        question_register.append(row)

    question_register.sort(
        key=lambda row: (-int(row.get("question_score", 0) or 0), -int(row.get("priority_score", 0) or 0), text(row.get("question_id")))
    )
    return question_register


def build_question_normalization_register(
    *,
    asset_family_research_profile: dict[str, Any],
    question_candidate_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family")) or "commercial_building"
    library_by_id = {
        text(row.get("question_id")): dict(row)
        for row in _governed_question_library(asset_family)
        if text(row.get("question_id"))
    }
    normalization_register: list[dict[str, Any]] = []
    for candidate in list(question_candidate_register or []):
        question_id = text(candidate.get("question_id"))
        if not question_id:
            continue
        spec = library_by_id.get(question_id, {})
        metadata = _question_metadata(spec)
        normalization_register.append(
            {
                "question_id": question_id,
                "normalization_basis": "governed_question_library",
                "normalization_status": "normalized" if spec else "missing_governed_spec",
                "normalized_intake_question": text(spec.get("intake_question")),
                "normalized_required_from": text(spec.get("required_from")),
                "normalized_priority": text(spec.get("priority")).lower() or "medium",
                "why_needed": text(spec.get("why_needed")),
                "hypothesis_it_discriminates": text(spec.get("hypothesis_it_discriminates")),
                "rival_hypotheses": [
                    text(item)
                    for item in list(spec.get("rival_hypotheses", []) or [])
                    if text(item)
                ],
                "claim_impact_if_missing": text(spec.get("claim_impact_if_missing")),
                "blocked_claims_if_missing": [
                    text(item)
                    for item in list(metadata.get("blocked_claims_if_missing", []) or [])
                    if text(item)
                ],
                "supports_hypotheses": [
                    text(item)
                    for item in list(metadata.get("supports_hypotheses", []) or [])
                    if text(item)
                ],
                "falsifies_hypotheses": [
                    text(item)
                    for item in list(metadata.get("falsifies_hypotheses", []) or [])
                    if text(item)
                ],
                "comparison_requirements_unlocked": [
                    text(item)
                    for item in list(metadata.get("comparison_requirements_unlocked", []) or [])
                    if text(item)
                ],
            }
        )
    return normalization_register


def _materialize_dynamic_intake_question_register(
    *,
    question_candidate_register: list[dict[str, Any]],
    question_normalization_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalization_by_id = {
        text(row.get("question_id")): dict(row)
        for row in list(question_normalization_register or [])
        if text(row.get("question_id"))
    }
    question_register: list[dict[str, Any]] = []
    for candidate in list(question_candidate_register or []):
        question_id = text(candidate.get("question_id"))
        if not question_id:
            continue
        normalized = normalization_by_id.get(question_id, {})
        question_register.append(
            {
                "question_id": question_id,
                "asset_family": text(candidate.get("asset_family")),
                "intake_question": text(normalized.get("normalized_intake_question")),
                "trigger": text(candidate.get("trigger")),
                "why_needed": text(normalized.get("why_needed")),
                "hypothesis_it_discriminates": text(normalized.get("hypothesis_it_discriminates")),
                "rival_hypotheses": [
                    text(item)
                    for item in list(normalized.get("rival_hypotheses", []) or [])
                    if text(item)
                ],
                "required_from": text(normalized.get("normalized_required_from")),
                "priority": text(candidate.get("priority")) or text(normalized.get("normalized_priority")),
                "priority_score": int(candidate.get("priority_score", 0) or 0),
                "question_score": int(candidate.get("question_score", 0) or 0),
                "question_score_components": dict(candidate.get("question_score_components", {}) or {}),
                "activation_reasons": [
                    text(item)
                    for item in list(candidate.get("activation_reasons", []) or [])
                    if text(item)
                ],
                "linked_need_ids": [
                    text(item)
                    for item in list(candidate.get("linked_need_ids", []) or [])
                    if text(item)
                ],
                "linked_pack_names": [
                    text(item)
                    for item in list(candidate.get("linked_pack_names", []) or [])
                    if text(item)
                ],
                "public_search_context": [
                    text(item)
                    for item in list(candidate.get("public_search_context", []) or [])
                    if text(item)
                ],
                "escalation_condition": text(candidate.get("escalation_condition")),
                "claim_impact_if_missing": text(normalized.get("claim_impact_if_missing")),
                "blocked_claims_if_missing": [
                    text(item)
                    for item in list(normalized.get("blocked_claims_if_missing", []) or [])
                    if text(item)
                ],
                "supports_hypotheses": [
                    text(item)
                    for item in list(normalized.get("supports_hypotheses", []) or [])
                    if text(item)
                ],
                "falsifies_hypotheses": [
                    text(item)
                    for item in list(normalized.get("falsifies_hypotheses", []) or [])
                    if text(item)
                ],
                "comparison_requirements_unlocked": [
                    text(item)
                    for item in list(normalized.get("comparison_requirements_unlocked", []) or [])
                    if text(item)
                ],
            }
        )
    return question_register


def build_dynamic_intake_question_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    discovery_need_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
    congruence_case_state: dict[str, Any] | None = None,
    target_definition: dict[str, Any] | None = None,
    question_cap: int = _DEFAULT_QUESTION_CAP,
) -> list[dict[str, Any]]:
    congruence_case_state = (
        dict(congruence_case_state)
        if isinstance(congruence_case_state, dict)
        else build_congruence_case_state(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            target_definition=target_definition,
        )
    )
    decision_context_register = build_decision_context_register(
        asset_family_research_profile=asset_family_research_profile,
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        congruence_case_state=congruence_case_state,
        target_definition=target_definition,
    )
    candidates = build_question_candidate_register(
        asset_family_research_profile=asset_family_research_profile,
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        stop_condition_register=stop_condition_register,
        congruence_case_state=congruence_case_state,
        decision_context_register=decision_context_register,
        target_definition=target_definition,
    )
    normalization_register = build_question_normalization_register(
        asset_family_research_profile=asset_family_research_profile,
        question_candidate_register=candidates,
    )
    materialized_rows = _materialize_dynamic_intake_question_register(
        question_candidate_register=candidates,
        question_normalization_register=normalization_register,
    )
    selected = [dict(row) for row in materialized_rows[:question_cap]]
    dropped = materialized_rows[question_cap:]
    for row in selected:
        row["truncation_reason"] = "top_question_cap_applied" if dropped else ""
        row["questions_dropped_due_to_cap"] = len(dropped)
    return selected


def build_truncated_question_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    discovery_need_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
    congruence_case_state: dict[str, Any] | None = None,
    target_definition: dict[str, Any] | None = None,
    question_cap: int = _DEFAULT_QUESTION_CAP,
) -> list[dict[str, Any]]:
    congruence_case_state = (
        dict(congruence_case_state)
        if isinstance(congruence_case_state, dict)
        else build_congruence_case_state(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            target_definition=target_definition,
        )
    )
    decision_context_register = build_decision_context_register(
        asset_family_research_profile=asset_family_research_profile,
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        congruence_case_state=congruence_case_state,
        target_definition=target_definition,
    )
    candidates = build_question_candidate_register(
        asset_family_research_profile=asset_family_research_profile,
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        stop_condition_register=stop_condition_register,
        congruence_case_state=congruence_case_state,
        decision_context_register=decision_context_register,
        target_definition=target_definition,
    )
    normalization_register = build_question_normalization_register(
        asset_family_research_profile=asset_family_research_profile,
        question_candidate_register=candidates,
    )
    materialized_rows = _materialize_dynamic_intake_question_register(
        question_candidate_register=candidates,
        question_normalization_register=normalization_register,
    )
    dropped_rows: list[dict[str, Any]] = []
    for row in materialized_rows[question_cap:]:
        dropped_rows.append(
            {
                **dict(row),
                "drop_reason": "question_cap_exceeded",
            }
        )
    return dropped_rows


def build_required_from_register(
    *,
    dynamic_intake_question_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "question_id": text(row.get("question_id")),
            "required_from": text(row.get("required_from")),
            "priority": text(row.get("priority")),
            "claim_impact_if_missing": text(row.get("claim_impact_if_missing")),
        }
        for row in list(dynamic_intake_question_register or [])
        if text(row.get("question_id"))
    ]


def build_intake_priority_register(
    *,
    dynamic_intake_question_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "question_id": text(row.get("question_id")),
            "priority": text(row.get("priority")),
            "priority_score": int(row.get("priority_score", 0) or 0),
            "question_score": int(row.get("question_score", 0) or 0),
            "question_score_components": dict(row.get("question_score_components", {}) or {}),
            "hypothesis_it_discriminates": text(row.get("hypothesis_it_discriminates")),
        }
        for row in list(dynamic_intake_question_register or [])
        if text(row.get("question_id"))
    ]
