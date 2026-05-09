from __future__ import annotations

from typing import Any

from runtime_orchestrator.output_taxonomy import canonicalize_output_mode


SKILL_PATTERN_NAME_TO_ID = {
    "forklift_charging_and_demand_spike_plausible": "warehouse_mhe_charging_demand_peak",
    "dock_infiltration_and_door_discipline_plausible": "warehouse_dock_infiltration_loss",
    "compressed_air_leakage_or_pressure_overuse_plausible": "compressed_air_leak_plausibility",
    "poor_lubrication_or_reactive_maintenance_plausible": "maintenance_maturity_not_evidenced",
    "schedule_and_after_hours_waste_plausible": "hvac_schedule_drift",
    "missing_control_boundary_visibility": "tenant_operator_boundary_unresolved",
}

SKILL_POWER_QUALITY_HYPOTHESIS_TO_ID = {
    "power_quality_and_reactive_exposure_plausible": "reactive_power_exposure",
}

SKILL_INVALID_COMPARISON_TO_ID = {
    "warehouse_area_only_comparison": "fair_comparison_invalid_area_metric",
    "area_based_energy_intensity_comparison": "benchmark_denominator_error",
}

SKILL_COMPARISON_FAMILY_DEFAULTS = {
    "logistics_warehouse": "fair_comparison_invalid_area_metric",
    "cold_chain": "fair_comparison_invalid_area_metric",
}

SKILL_MEASUREMENT_HYPOTHESIS_TO_PATTERN_IDS = {
    "process_or_support_system_load_dominates_cost": ["process_load_vs_waste"],
    "maintenance_reality_changes_the_economic_story": ["maintenance_hidden_value_driver"],
}

ALLOWED_PATTERN_ACTIVATION_STATES = {
    "not_applicable",
    "candidate",
    "weakly_activated",
    "structurally_plausible",
    "asset_supported",
    "verified",
    "falsified",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _normalize_label(value: Any) -> str:
    text_value = _text(value).lower()
    if not text_value:
        return ""
    chars: list[str] = []
    for ch in text_value:
        chars.append(ch if ch.isalnum() else " ")
    return " ".join("".join(chars).split())


def build_active_skill_pattern_state(
    *,
    motor_049_output: dict[str, Any] | None = None,
    motor_051_output: dict[str, Any] | None = None,
    motor_052_output: dict[str, Any] | None = None,
    motor_053_output: dict[str, Any] | None = None,
) -> tuple[list[str], list[dict[str, Any]], list[str]]:
    m49 = dict(motor_049_output or {})
    m51 = dict(motor_051_output or {})
    m52 = dict(motor_052_output or {})
    m53 = dict(motor_053_output or {})
    fair_profile = dict(m51.get("fair_comparison_profile", {}) or {})
    asset_family = (
        _text(fair_profile.get("asset_family"))
        or _text((m49.get("asset_family_research_profile", {}) or {}).get("asset_family"))
        or _text((m49.get("asset_family_research_profile", {}) or {}).get("target_type_hint"))
    )

    active_pattern_ids: list[str] = []
    active_pattern_sources: list[dict[str, Any]] = []
    anti_trigger_signals: list[str] = []

    def _append_pattern(
        pattern_id: str,
        *,
        evidence_state: str = "",
        source_register: str = "",
        matched_key: str = "",
        why_activated: str = "",
    ) -> None:
        pid = _text(pattern_id)
        if not pid or pid in active_pattern_ids:
            return
        active_pattern_ids.append(pid)
        active_pattern_sources.append(
            {
                "pattern_id": pid,
                "evidence_state": _text(evidence_state),
                "source_register": _text(source_register),
                "matched_key": _text(matched_key),
                "why_activated": _text(why_activated),
            }
        )

    for row in list(m52.get("activated_pattern_register", []) or []):
        matched_key = _text(row.get("pattern_name"))
        pattern_id = SKILL_PATTERN_NAME_TO_ID.get(matched_key)
        if pattern_id:
            _append_pattern(
                pattern_id,
                evidence_state=_text(row.get("evidence_state")),
                source_register="motor_052.activated_pattern_register",
                matched_key=matched_key,
                why_activated=f"Legacy activated pattern `{matched_key}` is already active in motor_052.",
            )

    for row in list(m52.get("power_quality_hypothesis_register", []) or []):
        matched_key = _text(row.get("hypothesis_name"))
        pattern_id = SKILL_POWER_QUALITY_HYPOTHESIS_TO_ID.get(matched_key)
        if pattern_id:
            _append_pattern(
                pattern_id,
                evidence_state=_text(row.get("evidence_state")),
                source_register="motor_052.power_quality_hypothesis_register",
                matched_key=matched_key,
                why_activated=f"Power-quality hypothesis `{matched_key}` is already active in motor_052.",
            )

    if list(m53.get("value_leakage_register", []) or []):
        _append_pattern(
            "value_boundary_leakage_owner_operator",
            evidence_state="CONDITIONAL_HYPOTHESIS",
            source_register="motor_053.value_leakage_register",
            matched_key="tenant_operator_value_leakage",
            why_activated="Value leakage is already visible in motor_053, so control-boundary leakage remains structurally plausible.",
        )

    invalid_rows = list(m51.get("invalid_comparison_risk_register", []) or [])
    for row in invalid_rows:
        matched_key = _text(row.get("risk_name"))
        pattern_id = SKILL_INVALID_COMPARISON_TO_ID.get(matched_key)
        if pattern_id:
            _append_pattern(
                pattern_id,
                evidence_state=_text(row.get("risk_level")),
                source_register="motor_051.invalid_comparison_risk_register",
                matched_key=matched_key,
                why_activated=f"Invalid comparison risk `{matched_key}` is active in motor_051.",
            )

    comparison_not_yet_valid_rows = list(m51.get("comparison_not_yet_valid_register", []) or [])
    if not invalid_rows and comparison_not_yet_valid_rows:
        fallback_pattern_id = SKILL_COMPARISON_FAMILY_DEFAULTS.get(asset_family)
        if fallback_pattern_id:
            _append_pattern(
                fallback_pattern_id,
                evidence_state="comparison_not_yet_valid",
                source_register="motor_051.comparison_not_yet_valid_register",
                matched_key=asset_family,
                why_activated=f"Comparison remains invalid for `{asset_family}` until normalization evidence is available.",
            )
    if asset_family == "logistics_warehouse" and comparison_not_yet_valid_rows:
        _append_pattern(
            "cold_chain_status_unknown",
            evidence_state="comparison_not_yet_valid",
            source_register="motor_051.comparison_not_yet_valid_register",
            matched_key="dry_vs_cold_chain_unresolved",
            why_activated="Warehouse comparison remains invalid until dry versus cold-chain status is discriminated.",
        )

    measurement_strategy_rows = list(m52.get("measurement_strategy_register", []) or [])
    for row in measurement_strategy_rows:
        hypothesis_name = _text(row.get("hypothesis"))
        for pattern_id in list(SKILL_MEASUREMENT_HYPOTHESIS_TO_PATTERN_IDS.get(hypothesis_name, []) or []):
            _append_pattern(
                pattern_id,
                evidence_state="WEAK_SIGNAL",
                source_register="motor_052.measurement_strategy_register",
                matched_key=hypothesis_name,
                why_activated=f"Measurement strategy `{hypothesis_name}` is active and points to `{pattern_id}` as a rival hypothesis.",
            )

    hardware_minimality_rows = list(m52.get("hardware_minimality_register", []) or [])
    if measurement_strategy_rows:
        _append_pattern(
            "digital_twin_prematurity",
            evidence_state="WEAK_SIGNAL",
            source_register="motor_052.measurement_strategy_register",
            matched_key="dominant_variables_unresolved",
            why_activated="Measurement strategy remains open because dominant variables are not yet discriminated, so a digital twin remains premature.",
        )
    if asset_family == "industrial_manufacturing" and hardware_minimality_rows:
        _append_pattern(
            "sensor_prematurity",
            evidence_state="WEAK_SIGNAL",
            source_register="motor_052.hardware_minimality_register",
            matched_key="hardware_minimality",
            why_activated="Hardware minimality remains active for manufacturing, so broad sensing stays premature before hypothesis discrimination.",
        )

    if "warehouse_mhe_charging_demand_peak" in active_pattern_ids:
        _append_pattern(
            "demand_charge_exposure_unknown",
            evidence_state="CONDITIONAL_HYPOTHESIS",
            source_register="motor_052.activated_pattern_register",
            matched_key="forklift_charging_and_demand_spike_plausible",
            why_activated="MHE charging remains active, so demand-charge exposure stays structurally plausible until tariff evidence arrives.",
        )

    if asset_family == "industrial_manufacturing" and "maintenance_maturity_not_evidenced" in active_pattern_ids:
        _append_pattern(
            "procurement_vs_lifecycle_cost",
            evidence_state="WEAK_SIGNAL",
            source_register="motor_052.measurement_strategy_register",
            matched_key="maintenance_reality_changes_the_economic_story",
            why_activated="Maintenance reality is unresolved, so procurement-versus-lifecycle logic remains under-discriminated.",
        )

    comparable_rows = [
        row
        for row in list(m51.get("comparison_validity_register", []) or [])
        if bool(row.get("comparable"))
    ]
    if comparable_rows and not invalid_rows and not list(m51.get("comparison_not_yet_valid_register", []) or []):
        anti_trigger_signals.append("fair peer set already normalized")

    return active_pattern_ids, active_pattern_sources, anti_trigger_signals


def _infer_pattern_activation_state(
    *,
    source_register: str,
    evidence_state: str,
) -> str:
    register_label = _normalize_label(source_register)
    evidence_label = _normalize_label(evidence_state)
    if evidence_label in {"verified", "field verified", "independent verified", "l4"}:
        return "verified"
    if evidence_label in {"observed", "confirmed asset level", "asset specific public", "operator evidence", "l3"}:
        return "asset_supported"
    if register_label.endswith("measurement strategy register") or register_label.endswith("hardware minimality register"):
        return "weakly_activated"
    if evidence_label in {"conditional hypothesis", "comparison not yet valid", "critical", "high"}:
        return "structurally_plausible"
    if register_label.endswith("activated pattern register") or register_label.endswith("power quality hypothesis register"):
        return "structurally_plausible"
    if register_label.endswith("invalid comparison risk register") or register_label.endswith("comparison not yet valid register"):
        return "structurally_plausible"
    if register_label.endswith("value leakage register"):
        return "structurally_plausible"
    if evidence_label in {"weak signal", "l1"}:
        return "weakly_activated"
    return "candidate"


def build_registry_pattern_activation_register(
    *,
    registry_bundle: dict[str, Any],
    active_pattern_sources: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    patterns_by_id = dict((registry_bundle or {}).get("patterns_by_id", {}) or {})
    rows: list[dict[str, Any]] = []
    for source_row in list(active_pattern_sources or []):
        pattern_id = _text(source_row.get("pattern_id"))
        if not pattern_id:
            continue
        spec = dict(patterns_by_id.get(pattern_id, {}) or {})
        if not spec:
            continue
        rows.append(
            {
                "pattern_id": pattern_id,
                "pattern_name": _text(spec.get("name")),
                "knowledge_type": list(spec.get("knowledge_type", []) or []),
                "asset_types": list(spec.get("asset_types", []) or []),
                "activation_state": _infer_pattern_activation_state(
                    source_register=_text(source_row.get("source_register")),
                    evidence_state=_text(source_row.get("evidence_state")),
                ),
                "evidence_state": _text(source_row.get("evidence_state")),
                "evidence_state_ceiling": _text(spec.get("confidence_ceiling")),
                "source_register": _text(source_row.get("source_register")),
                "matched_key": _text(source_row.get("matched_key")),
                "why_activated": _text(source_row.get("why_activated"))
                or f"Registry pattern `{pattern_id}` was activated from `{_text(source_row.get('source_register'))}`.",
                "what_would_falsify": "; ".join(list(spec.get("falsification_conditions", []) or [])),
                "minimum_evidence_to_activate": list(spec.get("minimum_evidence_to_activate", []) or []),
                "minimum_evidence_to_confirm": list(spec.get("minimum_evidence_to_confirm", []) or []),
                "falsification_conditions": list(spec.get("falsification_conditions", []) or []),
                "rival_hypotheses": list(spec.get("rival_hypotheses", []) or []),
                "allowed_claim_language": _text(spec.get("allowed_claim_language")),
                "prohibited_claim_language": _text(spec.get("prohibited_claim_language")),
                "source_basis": list(spec.get("source_basis", []) or []),
            }
        )
    return rows


def build_pattern_authority_state(
    *,
    legacy_pattern_register: list[dict[str, Any]] | None,
    skill_pattern_activation_register: list[dict[str, Any]] | None,
    skill_active_pattern_ids: list[str] | None = None,
) -> dict[str, Any]:
    legacy_rows = list(legacy_pattern_register or [])
    skill_rows = list(skill_pattern_activation_register or [])
    required_pattern_ids = {_text(item) for item in list(skill_active_pattern_ids or []) if _text(item)}
    promoted = bool(skill_rows) and (
        not required_pattern_ids
        or required_pattern_ids.issubset(
            {_text(row.get("pattern_id")) for row in skill_rows if _text(row.get("pattern_id"))}
        )
    )
    return {
        "pattern_authority_state": "skill_primary" if promoted else "legacy_primary_skill_shadow",
        "coverage_state": "promoted" if promoted else "shadow_ready" if skill_rows else "missing",
        "required_pattern_ids": sorted(required_pattern_ids),
        "legacy_pattern_count": len(legacy_rows),
        "skill_pattern_count": len(skill_rows),
    }


_FINANCIAL_EXPOSURE_CATEGORY_MAP = {
    "capex_misallocated": "CAPEX misallocation risk",
    "wrong_peer_valuation": "wrong peer valuation",
    "tariff_exposure_hidden": "tariff exposure",
    "demand_charge_exposure": "hidden demand charge exposure",
    "operational_savings_not_capturable": "savings capture risk",
    "tenant_operator_value_leakage": "boundary leakage",
    "maintenance_downtime_exposure": "maintenance downtime exposure",
    "compliance_exposure_misunderstood": "compliance exposure ambiguity",
    "over_modeling_cost": "over-modeling cost",
    "under_instrumentation_risk": "instrumentation waste",
    "wrong_retrofit_sequencing": "wrong retrofit sequencing",
}


def build_registry_financial_exposure_register(
    *,
    financial_exposure_type_register: list[dict[str, Any]] | None,
    source_register: str = "motor_053.financial_exposure_type_register",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(financial_exposure_type_register or []):
        exposure_type = _text(row.get("financial_exposure_type")).lower()
        if not exposure_type:
            continue
        rows.append(
            {
                "financial_exposure_type": _text(row.get("financial_exposure_type")),
                "governed_exposure_category": _FINANCIAL_EXPOSURE_CATEGORY_MAP.get(
                    exposure_type,
                    _text(row.get("financial_exposure_type")).replace("_", " "),
                ),
                "trigger": _text(row.get("trigger")),
                "why_it_matters": _text(row.get("why_it_matters")),
                "evidence_needed": list(row.get("evidence_needed", []) or []),
                "tad_consequence": _text(row.get("tad_consequence")),
                "evidence_state_ceiling": "L2",
                "source_register": _text(source_register),
            }
        )
    return rows


def _split_tad_actions(value: Any) -> list[str]:
    text_value = _text(value)
    if not text_value:
        return []
    return [_text(part) for part in text_value.split("+") if _text(part)]


def _canonical_tad_action(value: Any) -> str:
    return _text(value).replace(" ", "_").upper()


def _format_label(value: Any) -> str:
    return " ".join(_text(value).replace("_", " ").split())


def _list_text(value: Any) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        return [_text(item) for item in value if _text(item)]
    text_value = _text(value)
    return [text_value] if text_value else []


def build_registry_tad_action_register(
    *,
    combination_review_register: list[dict[str, Any]] | None,
    skill_pattern_activation_register: list[dict[str, Any]] | None = None,
    skill_financial_exposure_register: list[dict[str, Any]] | None = None,
    measurement_strategy_register: list[dict[str, Any]] | None = None,
    claim_impact_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_actions: set[str] = set()

    def _push(
        *,
        strategic_action: str,
        status: str,
        trigger: str,
        why: str,
        evidence_needed: list[str],
        prohibited_action: str,
        source_register: str,
        source_combination_id: str = "",
        validator_state: str = "not_run",
    ) -> None:
        action_id = _canonical_tad_action(strategic_action)
        if not action_id or action_id in seen_actions:
            return
        seen_actions.add(action_id)
        rows.append(
            {
                "strategic_action": action_id,
                "status": _text(status),
                "trigger": _text(trigger),
                "why": _text(why),
                "evidence_needed": list(evidence_needed or []),
                "prohibited_action": _text(prohibited_action),
                "source_register": _text(source_register),
                "source_combination_id": _text(source_combination_id),
                "validator_state": _text(validator_state) or "not_run",
            }
        )

    for review_row in list(combination_review_register or []):
        for action in _split_tad_actions(review_row.get("tad_action")):
            _push(
                strategic_action=action,
                status="NEEDS REVIEW",
                trigger=_text(review_row.get("combination_id")),
                why=_text(review_row.get("combined_hypothesis")),
                evidence_needed=list(review_row.get("minimum_evidence", []) or []),
                prohibited_action=", ".join(
                    [_text(item) for item in list(review_row.get("prohibited_claims", []) or []) if _text(item)]
                ),
                source_register="zlab_skill.combination_review_register",
                source_combination_id=_text(review_row.get("combination_id")),
                validator_state=_text(review_row.get("validator_state")) or "not_run",
            )

    for row in list(skill_pattern_activation_register or []):
        pattern_id = _text(row.get("pattern_id"))
        if not pattern_id:
            continue
        _push(
            strategic_action="VALIDATE_LOSS_PATTERN",
            status="ACT NOW",
            trigger=pattern_id,
            why=f"Registry-first pattern {pattern_id} remains bounded and needs falsification before diagnosis.",
            evidence_needed=list(row.get("minimum_evidence_to_activate", []) or []),
            prohibited_action=_text(row.get("prohibited_claim_language")),
            source_register=_text(row.get("source_register")) or "motor_052.skill_pattern_activation_register",
            validator_state="passed",
        )

    for row in list(skill_financial_exposure_register or []):
        category = _normalize_label(row.get("governed_exposure_category"))
        if category in {"tariff exposure", "hidden demand charge exposure"}:
            _push(
                strategic_action="VALIDATE_TARIFF_EXPOSURE",
                status="ACT NOW",
                trigger=_text(row.get("financial_exposure_type")),
                why=_text(row.get("why_it_matters")),
                evidence_needed=list(row.get("evidence_needed", []) or []),
                prohibited_action=_text(row.get("tad_consequence")),
                source_register=_text(row.get("source_register")) or "motor_053.skill_financial_exposure_register",
                validator_state="passed",
            )
        if category == "boundary leakage":
            _push(
                strategic_action="VALIDATE_CONTROL_BOUNDARY",
                status="ACT NOW",
                trigger=_text(row.get("financial_exposure_type")),
                why=_text(row.get("why_it_matters")),
                evidence_needed=list(row.get("evidence_needed", []) or []),
                prohibited_action=_text(row.get("tad_consequence")),
                source_register=_text(row.get("source_register")) or "motor_053.skill_financial_exposure_register",
                validator_state="passed",
            )
        if category == "wrong peer valuation":
            _push(
                strategic_action="BUILD_FAIR_PEER_SET",
                status="ACT NOW",
                trigger=_text(row.get("financial_exposure_type")),
                why=_text(row.get("why_it_matters")),
                evidence_needed=list(row.get("evidence_needed", []) or []),
                prohibited_action=_text(row.get("tad_consequence")),
                source_register=_text(row.get("source_register")) or "motor_053.skill_financial_exposure_register",
                validator_state="passed",
            )
        if category == "over modeling cost":
            _push(
                strategic_action="DO_NOT_MODEL_YET",
                status="DO NOT MODEL YET",
                trigger=_text(row.get("financial_exposure_type")),
                why=_text(row.get("why_it_matters")),
                evidence_needed=list(row.get("evidence_needed", []) or []),
                prohibited_action=_text(row.get("tad_consequence")) or "Do not model yet.",
                source_register=_text(row.get("source_register")) or "motor_053.skill_financial_exposure_register",
                validator_state="passed",
            )
        if category in {"capex misallocation risk", "wrong retrofit sequencing"}:
            _push(
                strategic_action="DO_NOT_INVEST_YET",
                status="DO NOT INVEST YET",
                trigger=_text(row.get("financial_exposure_type")),
                why=_text(row.get("why_it_matters")),
                evidence_needed=list(row.get("evidence_needed", []) or []),
                prohibited_action=_text(row.get("tad_consequence")) or "Do not invest yet.",
                source_register=_text(row.get("source_register")) or "motor_053.skill_financial_exposure_register",
                validator_state="passed",
            )

    for row in list(measurement_strategy_register or []):
        _push(
            strategic_action="DO_NOT_SENSOR_YET",
            status="DO NOT SENSOR YET",
            trigger=_text(row.get("hypothesis")),
            why=_text(row.get("why")),
            evidence_needed=[_text(row.get("minimum_measurement"))] if _text(row.get("minimum_measurement")) else [],
            prohibited_action=_text(row.get("hardware_trigger")) or "Do not deploy broad sensing before hypothesis discrimination.",
            source_register="motor_052.measurement_strategy_register",
            validator_state="passed",
        )
        break

    for row in list(claim_impact_register or []):
        _push(
            strategic_action="PROHIBIT_CLAIM",
            status="PROHIBIT CLAIM",
            trigger=_text(row.get("hypothesis_it_discriminates")),
            why=_text(row.get("claim_impact")),
            evidence_needed=list(row.get("evidence_needed", []) or []),
            prohibited_action="Do not promote the blocked claim before the discriminating evidence arrives.",
            source_register="motor_049.claim_impact_register",
            validator_state="passed",
        )
        break

    return rows


def build_registry_gold_nugget_register(
    *,
    registry_bundle: dict[str, Any],
    combination_review_register: list[dict[str, Any]] | None,
    skill_pattern_activation_register: list[dict[str, Any]] | None = None,
    skill_financial_exposure_register: list[dict[str, Any]] | None = None,
    tad_action_register: list[dict[str, Any]] | None = None,
    asset_family_research_profile: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    patterns_by_id = dict((registry_bundle or {}).get("patterns_by_id", {}) or {})
    skill_pattern_activation_register = list(skill_pattern_activation_register or [])
    skill_financial_exposure_register = list(skill_financial_exposure_register or [])
    tad_action_register = list(tad_action_register or [])
    combination_review_register = list(combination_review_register or [])
    asset_profile = dict(asset_family_research_profile or {})
    asset_family = _text(asset_profile.get("asset_family")) or _text(asset_profile.get("target_type_hint"))

    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()
    active_pattern_ids = {
        _text(row.get("pattern_id"))
        for row in skill_pattern_activation_register
        if _text(row.get("pattern_id"))
    }
    governed_exposure_categories = {
        _normalize_label(row.get("governed_exposure_category") or row.get("financial_exposure_type"))
        for row in skill_financial_exposure_register
        if _normalize_label(row.get("governed_exposure_category") or row.get("financial_exposure_type"))
    }

    def _find_tad_row(*action_ids: str) -> dict[str, Any]:
        normalized = {
            _canonical_tad_action(action_id)
            for action_id in action_ids
            if _canonical_tad_action(action_id)
        }
        for row in tad_action_register:
            if _canonical_tad_action(row.get("strategic_action")) in normalized:
                return dict(row)
        return {}

    def _push(
        *,
        nugget_id: str,
        gold_nugget: str,
        why_it_matters: str,
        evidence_state: str,
        what_to_do_next: str,
        minimum_evidence: list[str],
        linked_financial_exposure: str = "",
        linked_comparison_failure: str = "",
        linked_loss_pattern: str = "",
        linked_dependency: str = "",
        tad_action: str = "",
        source_combination_id: str = "",
        source_pattern_id: str = "",
        nugget_theme: str = "",
        validator_state: str = "passed",
    ) -> None:
        nugget_key = _text(nugget_id)
        nugget_text = _text(gold_nugget)
        if not nugget_key or not nugget_text or nugget_key in seen_ids or nugget_text in seen_texts:
            return
        seen_ids.add(nugget_key)
        seen_texts.add(nugget_text)
        rows.append(
            {
                "nugget_id": nugget_key,
                "gold_nugget": nugget_text,
                "why_it_matters": _text(why_it_matters),
                "evidence_state": _text(evidence_state) or "L2",
                "what_to_do_next": _text(what_to_do_next),
                "minimum_evidence": _list_text(minimum_evidence),
                "linked_financial_exposure": _text(linked_financial_exposure),
                "linked_comparison_failure": _text(linked_comparison_failure),
                "linked_loss_pattern": _text(linked_loss_pattern),
                "linked_dependency": _text(linked_dependency),
                "tad_action": _text(tad_action),
                "source_combination_id": _text(source_combination_id),
                "source_pattern_id": _text(source_pattern_id),
                "nugget_theme": _text(nugget_theme),
                "validator_state": _text(validator_state) or "passed",
            }
        )

    def _push_pattern(
        pattern_id: str,
        *,
        nugget_theme: str,
        preferred_actions: list[str],
        linked_financial_exposure: str = "",
        linked_comparison_failure: str = "",
    ) -> None:
        spec = dict(patterns_by_id.get(pattern_id, {}) or {})
        if not spec:
            return
        example_outputs = _list_text(spec.get("example_outputs"))
        if not example_outputs:
            return
        action_row = _find_tad_row(*preferred_actions, *_list_text(spec.get("tad_actions")))
        minimum_evidence = _list_text(action_row.get("evidence_needed")) or _list_text(spec.get("evidence_required"))
        _push(
            nugget_id=f"pattern_{pattern_id}",
            gold_nugget=example_outputs[0],
            why_it_matters=_text(spec.get("financial_mechanism")) or _text(spec.get("operational_basis")),
            evidence_state=_text(spec.get("confidence_ceiling")) or "L2",
            what_to_do_next=_text(action_row.get("why")) or _text(action_row.get("prohibited_action")) or _text(spec.get("allowed_claim_language")),
            minimum_evidence=minimum_evidence,
            linked_financial_exposure=linked_financial_exposure or ", ".join(_list_text(spec.get("financial_exposure_if_true"))[:2]),
            linked_comparison_failure=linked_comparison_failure,
            linked_loss_pattern=_text(spec.get("name")) if "LOSS_PATTERN" in list(spec.get("knowledge_type", []) or []) else "",
            linked_dependency=_text(spec.get("hypothesis")),
            tad_action=_text(action_row.get("strategic_action")) or _text(preferred_actions[0] if preferred_actions else ""),
            source_pattern_id=pattern_id,
            nugget_theme=nugget_theme,
            validator_state="passed",
        )

    first_combination = {}
    for review_row in combination_review_register:
        combination_id = _text(review_row.get("combination_id"))
        if not combination_id:
            continue
        if _normalize_label(review_row.get("validator_state")) == "blocked":
            continue
        if _normalize_label(review_row.get("decision")) == "rejected for use":
            continue
        first_combination = dict(review_row)
        break

    if asset_family == "industrial_manufacturing" and "process_load_vs_waste" in active_pattern_ids:
        _push_pattern(
            "process_load_vs_waste",
            nugget_theme="process_dominance",
            preferred_actions=["REQUEST_MINIMUM_EVIDENCE", "DO_NOT_INVEST_YET"],
            linked_financial_exposure="CAPEX misallocation risk, wrong dominant-variable selection",
        )

    if (
        "fair_comparison_invalid_area_metric" in active_pattern_ids
        or "benchmark_denominator_error" in active_pattern_ids
    ):
        _push_pattern(
            (
                "fair_comparison_invalid_area_metric"
                if "fair_comparison_invalid_area_metric" in active_pattern_ids
                else "benchmark_denominator_error"
            ),
            nugget_theme="comparison_invalidity",
            preferred_actions=["BUILD_FAIR_PEER_SET", "COMPARE_FAIRLY"],
            linked_financial_exposure="wrong peer valuation",
            linked_comparison_failure="fair comparison remains invalid until the comparison basis is normalized",
        )

    if (
        "warehouse_mhe_charging_demand_peak" in active_pattern_ids
        or "demand_charge_exposure_unknown" in active_pattern_ids
        or "reactive_power_exposure" in active_pattern_ids
    ):
        _push_pattern(
            (
                "warehouse_mhe_charging_demand_peak"
                if "warehouse_mhe_charging_demand_peak" in active_pattern_ids
                else "demand_charge_exposure_unknown"
                if "demand_charge_exposure_unknown" in active_pattern_ids
                else "reactive_power_exposure"
            ),
            nugget_theme="tariff_orchestration",
            preferred_actions=[
                "VALIDATE_TARIFF_EXPOSURE",
                "VALIDATE_CHARGING_PROFILE",
                "VALIDATE_PF_TARIFF_EXPOSURE",
            ],
            linked_financial_exposure="hidden demand charge exposure, tariff exposure",
        )

    if "warehouse_dock_infiltration_loss" in active_pattern_ids:
        _push_pattern(
            "warehouse_dock_infiltration_loss",
            nugget_theme="logistics_interface",
            preferred_actions=["VALIDATE_LOSS_PATTERN"],
        )

    if "compressed_air_leak_plausibility" in active_pattern_ids:
        _push_pattern(
            "compressed_air_leak_plausibility",
            nugget_theme="support_utility_loss",
            preferred_actions=["VALIDATE_LOSS_PATTERN", "VALIDATE_MAINTENANCE_REALITY", "DO_NOT_SENSOR_YET"],
            linked_financial_exposure="maintenance downtime exposure",
        )

    if "hvac_schedule_drift" in active_pattern_ids:
        _push_pattern(
            "hvac_schedule_drift",
            nugget_theme="controls_or_schedule",
            preferred_actions=["VALIDATE_LOSS_PATTERN", "REQUEST_MINIMUM_EVIDENCE", "DO_NOT_INVEST_YET"],
        )

    if "maintenance_maturity_not_evidenced" in active_pattern_ids:
        _push_pattern(
            "maintenance_maturity_not_evidenced",
            nugget_theme="maintenance_reality",
            preferred_actions=["VALIDATE_MAINTENANCE_REALITY", "REQUEST_MINIMUM_EVIDENCE", "DO_NOT_INVEST_YET"],
            linked_financial_exposure="maintenance downtime exposure",
        )

    if asset_family == "industrial_manufacturing" and "maintenance_hidden_value_driver" in active_pattern_ids:
        _push_pattern(
            "maintenance_hidden_value_driver",
            nugget_theme="maintenance_hidden_value",
            preferred_actions=["VALIDATE_MAINTENANCE_REALITY", "DO_NOT_INVEST_YET"],
            linked_financial_exposure="maintenance downtime exposure",
        )

    if (
        "value_boundary_leakage_owner_operator" in active_pattern_ids
        or "tenant_operator_boundary_unresolved" in active_pattern_ids
    ):
        _push_pattern(
            "value_boundary_leakage_owner_operator",
            nugget_theme="boundary_leakage",
            preferred_actions=["VALIDATE_CONTROL_BOUNDARY", "PROHIBIT_ROI"],
            linked_financial_exposure="boundary leakage, savings capture risk",
        )

    if _find_tad_row("DO_NOT_MODEL_YET"):
        _push_pattern(
            "digital_twin_prematurity",
            nugget_theme="model_prematurity",
            preferred_actions=["DO_NOT_MODEL_YET"],
            linked_financial_exposure="over-modeling cost",
        )

    if len(rows) < 3 and first_combination:
        combination_id = _text(first_combination.get("combination_id"))
        _push(
            nugget_id=f"combo_{combination_id}",
            gold_nugget=_text(first_combination.get("allowed_language")) or _text(first_combination.get("combined_hypothesis")),
            why_it_matters=_text(first_combination.get("strategic_risk")),
            evidence_state=_text(first_combination.get("evidence_state_ceiling")) or "L2",
            what_to_do_next=_text(first_combination.get("tad_action")),
            minimum_evidence=_list_text(first_combination.get("minimum_evidence")),
            linked_financial_exposure=", ".join(_list_text(first_combination.get("financial_exposure"))),
            linked_comparison_failure=", ".join(_list_text(first_combination.get("prohibited_claims"))),
            tad_action=_text(first_combination.get("tad_action")),
            source_combination_id=combination_id,
            nugget_theme="combined_hypothesis",
            validator_state=_text(first_combination.get("validator_state")) or "passed",
        )

    if len(rows) < 3 and _find_tad_row("DO_NOT_SENSOR_YET"):
        action_row = _find_tad_row("DO_NOT_SENSOR_YET")
        _push(
            nugget_id="skill_wrong_measurement_instinct",
            gold_nugget="The next best evidence may be a bill, map or log, not a new sensor.",
            why_it_matters="Measurement cost and speed improve when evidence follows the dominant hypothesis instead of hardware reflex.",
            evidence_state="L2",
            what_to_do_next=_text(action_row.get("why")) or _text(action_row.get("prohibited_action")),
            minimum_evidence=_list_text(action_row.get("evidence_needed")),
            linked_financial_exposure="instrumentation waste",
            linked_dependency=_text(action_row.get("trigger")),
            tad_action=_text(action_row.get("strategic_action")),
            nugget_theme="measurement_minimality",
            validator_state="passed",
        )

    if asset_family == "industrial_manufacturing":
        preferred_theme_order = [
            "process_dominance",
            "support_utility_loss",
            "maintenance_hidden_value",
            "tariff_orchestration",
            "model_prematurity",
            "maintenance_reality",
            "boundary_leakage",
            "comparison_invalidity",
        ]
        order_index = {theme: idx for idx, theme in enumerate(preferred_theme_order)}
        rows = sorted(
            rows,
            key=lambda row: (
                order_index.get(_text(row.get("nugget_theme")), 999),
                _text(row.get("nugget_id")),
            ),
        )

    return rows[:5]


def build_skill_cutover_authority_register(
    *,
    legacy_pattern_register: list[dict[str, Any]] | None,
    skill_pattern_register: list[dict[str, Any]] | None,
    legacy_financial_exposure_register: list[dict[str, Any]] | None,
    skill_financial_exposure_register: list[dict[str, Any]] | None,
    skill_combination_review_register: list[dict[str, Any]] | None,
    legacy_tad_register: list[dict[str, Any]] | None,
    skill_tad_register: list[dict[str, Any]] | None,
    legacy_gold_nugget_register: list[dict[str, Any]] | None,
    skill_gold_nugget_register: list[dict[str, Any]] | None,
    promoted_domains: list[str] | set[str] | tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    promoted = {_normalize_label(value) for value in list(promoted_domains or []) if _normalize_label(value)}
    legacy_pattern_count = len(list(legacy_pattern_register or []))
    skill_pattern_count = len(list(skill_pattern_register or []))
    legacy_financial_count = len(list(legacy_financial_exposure_register or []))
    skill_financial_count = len(list(skill_financial_exposure_register or []))
    skill_combo_count = len(list(skill_combination_review_register or []))
    legacy_tad_count = len(list(legacy_tad_register or []))
    skill_tad_count = len(list(skill_tad_register or []))
    legacy_nugget_count = len(list(legacy_gold_nugget_register or []))
    skill_nugget_count = len(list(skill_gold_nugget_register or []))

    legacy_financial_keys = {
        _normalize_label(row.get("financial_exposure_type"))
        for row in list(legacy_financial_exposure_register or [])
        if _normalize_label(row.get("financial_exposure_type"))
    }
    skill_financial_keys = {
        _normalize_label(row.get("governed_exposure_category"))
        for row in list(skill_financial_exposure_register or [])
        if _normalize_label(row.get("governed_exposure_category"))
    }
    shared_financial = sorted(legacy_financial_keys.intersection(skill_financial_keys))

    legacy_tad_keys = {
        _normalize_label(row.get("strategic_action"))
        for row in list(legacy_tad_register or [])
        if _normalize_label(row.get("strategic_action"))
    }
    skill_tad_keys = {
        _normalize_label(row.get("strategic_action"))
        for row in list(skill_tad_register or [])
        if _normalize_label(row.get("strategic_action"))
    }
    shared_tad = sorted(legacy_tad_keys.intersection(skill_tad_keys))

    rows = [
        {
            "domain": "patterns",
            "legacy_register": "motor_052.activated_pattern_register",
            "skill_register": "motor_052.skill_pattern_activation_register",
            "legacy_count": legacy_pattern_count,
            "skill_count": skill_pattern_count,
            "coverage_state": (
                "promoted"
                if "patterns" in promoted
                else "shadow_ready" if skill_pattern_count else "missing"
            ),
            "current_authority": (
                "skill_primary"
                if "patterns" in promoted
                else "legacy_primary_skill_shadow"
            ),
            "cutover_readiness": (
                "promoted"
                if "patterns" in promoted
                else "shadow_ready" if skill_pattern_count else "not_ready"
            ),
            "notes": "Registry-first pattern activation is now emitted additively from motor_052.",
        },
        {
            "domain": "financial_exposure",
            "legacy_register": "motor_053.financial_exposure_type_register",
            "skill_register": "motor_053.skill_financial_exposure_register",
            "legacy_count": legacy_financial_count,
            "skill_count": skill_financial_count,
            "coverage_state": (
                "promoted"
                if "financial exposure" in promoted
                else "shadow_ready" if skill_financial_count else "missing"
            ),
            "current_authority": (
                "skill_primary"
                if "financial exposure" in promoted
                else "legacy_primary_skill_shadow"
            ),
            "cutover_readiness": (
                "promoted"
                if "financial exposure" in promoted
                else "shadow_ready" if skill_financial_count else "not_ready"
            ),
            "shared_keys": shared_financial,
            "notes": "Governed categories now shadow legacy financial exposures without replacing them yet.",
        },
        {
            "domain": "combinations",
            "legacy_register": "",
            "skill_register": "motor_054.skill_combination_review_register",
            "legacy_count": 0,
            "skill_count": skill_combo_count,
            "coverage_state": "ready_for_adjudication" if skill_combo_count else "missing",
            "current_authority": "skill_primary_adjudicated",
            "cutover_readiness": "ready_for_adjudication" if skill_combo_count else "not_ready",
            "notes": "Combinations are native skill objects and already run through validators plus adjudication states.",
        },
        {
            "domain": "tad",
            "legacy_register": "motor_054.expanded_tad_action_register",
            "skill_register": "motor_054.skill_expanded_tad_action_register",
            "legacy_count": legacy_tad_count,
            "skill_count": skill_tad_count,
            "coverage_state": (
                "promoted"
                if "tad" in promoted
                else "shadow_ready" if skill_tad_count else "missing"
            ),
            "current_authority": (
                "skill_primary"
                if "tad" in promoted
                else "legacy_primary_skill_shadow"
            ),
            "cutover_readiness": (
                "promoted"
                if "tad" in promoted
                else "shadow_ready" if skill_tad_count else "not_ready"
            ),
            "shared_keys": shared_tad,
            "notes": "Skill TAD stays additive until registry combinations cover the full action surface.",
        },
        {
            "domain": "gold_nuggets",
            "legacy_register": "motor_054.gold_nugget_register",
            "skill_register": "motor_054.skill_gold_nugget_register",
            "legacy_count": legacy_nugget_count,
            "skill_count": skill_nugget_count,
            "coverage_state": (
                "promoted"
                if "gold nuggets" in promoted
                else "shadow_ready" if skill_nugget_count else "missing"
            ),
            "current_authority": (
                "skill_primary"
                if "gold nuggets" in promoted
                else "legacy_primary_skill_shadow"
            ),
            "cutover_readiness": (
                "promoted"
                if "gold nuggets" in promoted
                else "shadow_ready" if skill_nugget_count else "not_ready"
            ),
            "notes": "Skill nuggets are combination-derived bounded framings and still shadow the broader legacy nugget surface.",
        },
    ]
    return rows


def _target_definition_from_skill_context(
    *,
    motor_007_output: dict[str, Any] | None = None,
    motor_012_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    m07 = dict(motor_007_output or {})
    m12 = dict(motor_012_output or {})
    target_definition = dict(m07.get("target_definition_contract", {}) or {})
    if target_definition:
        return target_definition
    facility_prior = dict(m12.get("facility_prior", {}) or {})
    return dict(facility_prior.get("target_definition", {}) or {})


def _default_skill_report_mode(target_type: str) -> str:
    target = _normalize_label(target_type)
    if any(token in target for token in ("manufacturing", "process", "industrial facility")):
        return "Industrial Process Diagnostic Brief"
    return "Compliance / Investment Screening Brief"


def _ensure_declared_address_asset_field(
    *,
    asset_field_register: list[dict[str, Any]] | None,
    address_value: str,
    source_id: str,
) -> list[dict[str, Any]]:
    rows = [dict(row) for row in list(asset_field_register or [])]
    known_fields = {_normalize_label(row.get("field")) for row in rows if _normalize_label(row.get("field"))}
    if "address" in known_fields or not _text(address_value):
        return rows
    rows.append(
        {
            "field": "address",
            "value": _text(address_value),
            "status": "OBSERVED",
            "source_id": _text(source_id) or "skill_runtime_wrapper::address",
            "scope": "ASSET_LEVEL",
            "authority_score": "declared_input",
            "recency": "current",
            "admissibility": "DECLARED_INPUT_ONLY",
            "notes": "",
        }
    )
    return rows


def build_skill_first_compliance_applicability_case(
    *,
    target_definition: dict[str, Any] | None = None,
    report_mode: str = "",
    rule_family_name: str = "Bounded structural screening context",
) -> dict[str, Any]:
    target_definition = dict(target_definition or {})
    target_type = _text(target_definition.get("target_type"))
    address_raw = _text(target_definition.get("address_raw"))
    jurisdiction_scope = [_text(item) for item in list(target_definition.get("jurisdiction_scope", []) or []) if _text(item)]

    trigger_field_register: list[dict[str, Any]] = []
    if target_type:
        trigger_field_register.append(
            {
                "field_name": "target_type",
                "field_value": target_type,
                "trigger_state": "declared_context",
                "epistemic_state": "DECLARED_INPUT_ONLY",
            }
        )
    if address_raw:
        trigger_field_register.append(
            {
                "field_name": "address_raw",
                "field_value": address_raw,
                "trigger_state": "declared_context",
                "epistemic_state": "DECLARED_INPUT_ONLY",
            }
        )
    if jurisdiction_scope:
        trigger_field_register.append(
            {
                "field_name": "jurisdiction_scope",
                "field_value": ", ".join(jurisdiction_scope),
                "trigger_state": "declared_context",
                "epistemic_state": "DECLARED_INPUT_ONLY",
            }
        )

    return {
        "rule_family_record": [{"rule_family_name": _text(rule_family_name) or "Bounded structural screening context"}],
        "applicability_state": "screening_only",
        "compliance_posture_state": "validate_first",
        "determination_status": "not_closed",
        "publication_ceiling": "screening_only",
        "jurisdiction_trace_record": {
            "primary_regulation": _text(rule_family_name) or "Bounded structural screening context",
            "jurisdiction_codes": jurisdiction_scope,
        },
        "trigger_field_register": trigger_field_register,
        "threshold_register": [],
        "visible_report_mode_guard": _text(report_mode),
        "source_register": "zlab_skill.runtime_bridge.build_skill_first_compliance_applicability_case",
        "epistemic_note": (
            "This compliance case is a bounded structural screening surface. "
            "It cannot close regulation-specific applicability without case evidence."
        ),
    }


def build_skill_first_runtime_wrapper_inputs(
    *,
    motor_007_output: dict[str, Any] | None = None,
    motor_012_output: dict[str, Any] | None = None,
    motor_028_output: dict[str, Any] | None = None,
    motor_035_output: dict[str, Any] | None = None,
    case_id: str = "",
    case_title: str = "",
    case_subtitle: str = "Asset Decision-Admissibility Brief",
    organization: str = "ZLab",
    analyst: str = "Autonomous Decision System",
    sector_context: dict[str, Any] | None = None,
    report_mode_override: str = "",
    address_override: str = "",
    address_source_id: str = "",
    target_admissibility_state: str = "bounded_asset",
    asset_context_readiness: str = "asset_context_minimal",
    dominant_evidence_scope: str = "asset_level",
    missing_observable_clusters: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    m07 = dict(motor_007_output or {})
    m12 = dict(motor_012_output or {})
    m28 = dict(motor_028_output or {})
    m35 = dict(motor_035_output or {})

    target_definition = _target_definition_from_skill_context(
        motor_007_output=m07,
        motor_012_output=m12,
    )
    target_type = _text(target_definition.get("target_type"))
    target_name = _text(case_title) or _text(target_definition.get("target_name")) or _format_label(target_type) or "the asset"
    address_raw = _text(address_override) or _text(target_definition.get("address_raw"))
    jurisdiction_scope = [_text(item) for item in list(target_definition.get("jurisdiction_scope", []) or []) if _text(item)]
    report_mode = canonicalize_output_mode(
        _text(m35.get("report_type_allowed"))
        or _text(m07.get("report_identity_state"))
        or _text(m07.get("recommended_report_type"))
        or _text(report_mode_override)
        or _default_skill_report_mode(target_type)
    )

    compliance_case = build_skill_first_compliance_applicability_case(
        target_definition=target_definition,
        report_mode=report_mode,
    )

    asset_field_register = _ensure_declared_address_asset_field(
        asset_field_register=list(m12.get("asset_field_register", []) or []),
        address_value=address_raw,
        source_id=_text(address_source_id) or "skill_runtime_wrapper::address",
    )
    normalized_m12 = {
        **m12,
        "asset_field_register": asset_field_register,
        "evidence_lineage": dict(m12.get("evidence_lineage", {}) or {}),
        "compliance_applicability_case": compliance_case,
    }
    facility_prior = dict(normalized_m12.get("facility_prior", {}) or {})
    facility_prior["compliance_applicability_case"] = dict(compliance_case)
    if target_definition and not dict(facility_prior.get("target_definition", {}) or {}):
        facility_prior["target_definition"] = dict(target_definition)
    normalized_m12["facility_prior"] = facility_prior

    pipeline = {
        "case_id": _text(case_id) or f"skill-wrapper:{_normalize_label(target_name).replace(' ', '-') or 'case'}",
        "case_title": target_name,
        "case_subtitle": _text(case_subtitle) or "Asset Decision-Admissibility Brief",
        "organization": _text(organization) or "ZLab",
        "analyst": _text(analyst) or "Autonomous Decision System",
        "facility_inputs": {
            "input_01_location": {"address": address_raw},
            "input_02_facility_type": {"primary_classification": target_type},
            "input_03_sector": dict(sector_context or {}),
        },
    }

    runtime = {
        "target_definition": target_definition,
        "target_admissibility_state": _text(target_admissibility_state) or "bounded_asset",
        "asset_context_readiness": _text(asset_context_readiness) or "asset_context_minimal",
        "report_identity_state": report_mode,
        "recommended_report_type": report_mode,
        "dominant_evidence_scope": _text(dominant_evidence_scope) or "asset_level",
        "missing_observable_clusters": list(missing_observable_clusters or ["control_boundary_cluster", "operating_regime_cluster"]),
    }

    jurisdiction_resolution = dict(m35.get("jurisdiction_resolution", {}) or {})
    if jurisdiction_scope and not list(jurisdiction_resolution.get("jurisdiction_scope", []) or []):
        jurisdiction_resolution["jurisdiction_scope"] = jurisdiction_scope
    normalized_m35 = {
        **m35,
        "jurisdiction_resolution": jurisdiction_resolution,
    }
    if report_mode and not _text(normalized_m35.get("report_type_allowed")):
        normalized_m35["report_type_allowed"] = report_mode

    return {
        "__pipeline__": pipeline,
        "__runtime__": runtime,
        "motor_001": {},
        "motor_012": normalized_m12,
        "motor_018": {"chart_assets": [], "chart_errors": []},
        "motor_019": {"written_sections": [], "codex_available": False, "llm_governance_summary": {}},
        "motor_028": m28,
        "motor_035": normalized_m35,
    }


def _skill_first_minimum_evidence(
    *,
    motor_051_output: dict[str, Any] | None = None,
    motor_054_output: dict[str, Any] | None = None,
) -> tuple[list[str], str]:
    m51 = dict(motor_051_output or {})
    m54 = dict(motor_054_output or {})
    first_invalid_problem = dict((list(m51.get("invalid_problem_frame_register", []) or []) or [{}])[0] or {})
    first_tad = dict((list(m54.get("authoritative_tad_action_register", []) or []) or [{}])[0] or {})
    first_combo = dict((list(m54.get("skill_combination_review_register", []) or []) or [{}])[0] or {})
    first_nugget = dict((list(m54.get("authoritative_gold_nugget_register", []) or []) or [{}])[0] or {})

    evidence = (
        _list_text(first_tad.get("evidence_needed"))
        or _list_text(first_combo.get("minimum_evidence"))
        or _list_text(first_nugget.get("minimum_evidence"))
        or _list_text(first_invalid_problem.get("evidence_needed"))
    )
    source = (
        "motor_054.authoritative_tad_action_register"
        if _list_text(first_tad.get("evidence_needed"))
        else "motor_054.skill_combination_review_register"
        if _list_text(first_combo.get("minimum_evidence"))
        else "motor_054.authoritative_gold_nugget_register"
        if _list_text(first_nugget.get("minimum_evidence"))
        else "motor_051.invalid_problem_frame_register"
        if _list_text(first_invalid_problem.get("evidence_needed"))
        else ""
    )
    return evidence, source


def build_skill_first_executive_thesis_context(
    *,
    motor_007_output: dict[str, Any] | None = None,
    motor_012_output: dict[str, Any] | None = None,
    motor_051_output: dict[str, Any] | None = None,
    motor_053_output: dict[str, Any] | None = None,
    motor_054_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    m51 = dict(motor_051_output or {})
    m53 = dict(motor_053_output or {})
    m54 = dict(motor_054_output or {})
    target_definition = _target_definition_from_skill_context(
        motor_007_output=motor_007_output,
        motor_012_output=motor_012_output,
    )
    target_type = _text(target_definition.get("target_type"))
    target_name = _text(target_definition.get("target_name")) or _format_label(target_type) or "the asset"
    report_mode = _default_skill_report_mode(target_type)

    invalid_problem_rows = list(m51.get("invalid_problem_frame_register", []) or [])
    invalid_comparison_rows = list(m51.get("invalid_comparison_risk_register", []) or [])
    congruence_rows = list(m51.get("cross_layer_congruence_register", []) or [])
    tad_rows = list(m54.get("authoritative_tad_action_register", []) or [])
    congruence_action_rows = list(m54.get("congruence_action_priority_register", []) or [])
    nugget_rows = list(m54.get("authoritative_gold_nugget_register", []) or [])
    financial_rows = list(
        m53.get("authoritative_financial_exposure_register", m53.get("skill_financial_exposure_register", [])) or []
    )
    first_invalid_problem = dict((invalid_problem_rows or [{}])[0] or {})
    first_invalid_comparison = dict((invalid_comparison_rows or [{}])[0] or {})
    first_congruence = dict((congruence_rows or [{}])[0] or {})
    first_tad = dict((tad_rows or congruence_action_rows or [{}])[0] or {})
    first_nugget = dict((nugget_rows or [{}])[0] or {})
    first_financial = dict((financial_rows or [{}])[0] or {})
    minimum_evidence, minimum_evidence_source = _skill_first_minimum_evidence(
        motor_051_output=m51,
        motor_054_output=m54,
    )

    stated_problem = (
        _format_label(first_invalid_problem.get("apparent_problem"))
        or f"Need the right structural decision frame for {target_name}."
    )
    reframed_problem = (
        _text(first_invalid_problem.get("what_problem_should_be_tested_instead"))
        or _text(first_congruence.get("strategic_risk"))
        or _text(first_tad.get("why"))
        or _text(first_nugget.get("what_to_do_next"))
        or _text(first_nugget.get("gold_nugget"))
    )
    dominant_conflict = (
        _text(first_congruence.get("contradiction"))
        or _format_label(first_invalid_comparison.get("risk_name"))
        or _text(first_nugget.get("linked_comparison_failure"))
        or _text(first_tad.get("trigger"))
    )
    problem_frame_active = bool(reframed_problem or dominant_conflict or minimum_evidence)

    skill_tad_rows: list[dict[str, Any]] = []
    if tad_rows:
        for row in tad_rows[:5]:
            skill_tad_rows.append(
                {
                    "action": _format_label(row.get("strategic_action")).title(),
                    "status": _text(row.get("status")),
                    "why": _text(row.get("why")),
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "financial_exposure": _text(row.get("trigger")),
                    "evidence_needed": "; ".join(_list_text(row.get("evidence_needed"))),
                    "prohibited_action": _text(row.get("prohibited_action")),
                    "linked_claim": "congruence_action_claim",
                }
            )

    structural_financial_rows: list[dict[str, Any]] = []
    for row in financial_rows[:3]:
        structural_financial_rows.append(
            {
                "structural_assumption": _text(row.get("trigger")) or _text(row.get("financial_exposure_type")),
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure_if_wrong": _text(row.get("why_it_matters")),
                "evidence_needed": _list_text(row.get("evidence_needed")),
                "allowed_financial_output": ["scenario framing"],
                "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
            }
        )

    competitive_rows: list[dict[str, Any]] = []
    if first_invalid_comparison:
        competitive_rows.append(
            {
                "peer_type": _text(first_invalid_comparison.get("trigger"))
                or _text(first_invalid_comparison.get("risk_name"))
                or "bounded peer normalization required",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "transferability": "conditional on normalized comparison basis",
            }
        )

    conflict_rows: list[dict[str, Any]] = []
    if congruence_rows:
        for row in congruence_rows[:3]:
            conflict_rows.append(
                {
                    "conflict": _text(row.get("contradiction")),
                    "layers_involved": _list_text(row.get("layers")),
                    "why_it_matters": _text(row.get("strategic_risk")),
                    "potential_redesign_direction": _text(row.get("possible_redesign")),
                    "evidence_state": _text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                }
            )

    dominant_variable = (
        _text(first_tad.get("trigger"))
        or _text(first_nugget.get("nugget_theme"))
        or _text(first_invalid_comparison.get("trigger"))
        or _text(first_financial.get("financial_exposure_type"))
        or "dominant structural discriminator"
    )

    return {
        "canonical_problem_frame": {
            "stated_problem": stated_problem,
            "reframed_problem": reframed_problem,
            "dominant_conflict": dominant_conflict,
            "minimum_evidence_to_discriminate": " + ".join(minimum_evidence),
            "minimum_evidence_source": minimum_evidence_source,
            "problem_frame_active": problem_frame_active,
            "reasoning_path": "structural_first" if problem_frame_active else "legacy_decision_gating_only",
            "leading_structural_output_mode": report_mode,
            "evidence_state": "CONDITIONAL_HYPOTHESIS" if problem_frame_active else "INADMISSIBLE_CLAIM",
        },
        "report_output_mode_classifier_table": [
            {
                "canonical_output_mode": report_mode,
                "selected_for_publication": True,
                "classification_state": "selected_primary_default",
            }
        ],
        "claim_contract_register": list(m54.get("congruence_claim_contract_register", []) or []),
        "system_abstraction": {
            "selected_archetype_id": f"{_text(target_type) or 'generic'}_skill_runtime_bridge",
            "asset_type": {"statement": _format_label(target_type)},
            "dominant_process_type": {"statement": _format_label(dominant_variable)},
        },
        "problem_framing_register": [
            {
                "stated_problem": stated_problem,
                "reframed_problem": reframed_problem,
                "why_original_framing_may_be_wrong": _text(first_invalid_problem.get("why_invalid_or_premature"))
                or _text(first_nugget.get("gold_nugget")),
                "evidence_needed": "; ".join(minimum_evidence),
                "strategic_risk": _text(first_congruence.get("strategic_risk"))
                or _text(first_financial.get("why_it_matters")),
                "evidence_state": "CONDITIONAL_HYPOTHESIS" if problem_frame_active else "INADMISSIBLE_CLAIM",
            }
        ]
        if problem_frame_active
        else [],
        "dominant_variable_register": [
            {
                "variable": dominant_variable,
                "layer": "structural",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "why_it_could_matter": _text(first_financial.get("why_it_matters")) or reframed_problem,
                "decision_impact": _text(first_tad.get("strategic_action")) or "bounded structural decision sequencing",
            }
        ]
        if dominant_variable
        else [],
        "cross_layer_conflict_register": conflict_rows,
        "structural_financial_exposure_register": structural_financial_rows,
        "competitive_comparison_register": competitive_rows,
        "conditional_redesign_register": [],
        "minimum_evidence_for_discrimination_register": [
            {
                "rival_hypotheses": [
                    stated_problem,
                    reframed_problem,
                ],
                "minimum_evidence": ", ".join(minimum_evidence),
                "source": minimum_evidence_source,
                "what_it_confirms": reframed_problem,
                "what_it_falsifies": dominant_conflict,
                "unlocks": [_text(first_tad.get("strategic_action"))] if _text(first_tad.get("strategic_action")) else [],
            }
        ]
        if minimum_evidence
        else [],
        "expanded_structural_tad_action_register": skill_tad_rows,
    }


def build_skill_first_report_compression_context(
    *,
    executive_thesis: dict[str, Any] | None = None,
    motor_054_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    thesis = dict(executive_thesis or {})
    m54 = dict(motor_054_output or {})
    report_mode = _text(thesis.get("report_mode")) or "Compliance / Investment Screening Brief"
    canonical_problem_frame = {
        "leading_structural_output_mode": report_mode,
        "stated_problem": _text(thesis.get("declared_problem")),
        "reframed_problem": _text(thesis.get("reframed_problem")),
        "dominant_conflict": _text(thesis.get("dominant_contradiction")),
        "minimum_evidence_to_discriminate": " + ".join(_list_text(thesis.get("minimum_discriminating_evidence"))),
        "minimum_evidence_source": _text(thesis.get("minimum_discriminating_evidence_source")),
        "problem_frame_active": _text(thesis.get("thesis_state")) == "admissible_structural_thesis",
        "reasoning_path": "structural_first" if _text(thesis.get("thesis_state")) == "admissible_structural_thesis" else "legacy_decision_gating_only",
    }
    report_output_mode_classifier_table = [
        {
            "canonical_output_mode": report_mode,
            "selected_for_publication": True,
            "classification_state": "selected_primary_default",
        }
    ]
    return {
        "canonical_problem_frame": canonical_problem_frame,
        "claim_contract_register": list(m54.get("congruence_claim_contract_register", []) or []),
        "report_output_mode_classifier_table": report_output_mode_classifier_table,
    }


def build_skill_first_report_package_context(
    *,
    target_definition: dict[str, Any] | None = None,
    executive_thesis: dict[str, Any] | None = None,
    main_report_outline: dict[str, Any] | None = None,
    motor_053_output: dict[str, Any] | None = None,
    motor_054_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target_definition = dict(target_definition or {})
    thesis = dict(executive_thesis or {})
    outline = dict(main_report_outline or {})
    m53 = dict(motor_053_output or {})
    m54 = dict(motor_054_output or {})

    target_type = _text(target_definition.get("target_type"))
    target_name = _text(target_definition.get("target_name")) or _format_label(target_type) or "the asset"
    report_mode = (
        _text(outline.get("visible_report_mode"))
        or _text(thesis.get("report_mode"))
        or _default_skill_report_mode(target_type)
    )
    minimum_evidence = _list_text(thesis.get("minimum_discriminating_evidence"))
    minimum_evidence_source = _text(thesis.get("minimum_discriminating_evidence_source")) or "motor_047.executive_thesis"
    stated_problem = _text(thesis.get("declared_problem")) or f"Need the right structural decision frame for {target_name}."
    reframed_problem = _text(thesis.get("reframed_problem"))
    dominant_conflict = _text(thesis.get("dominant_contradiction"))
    dominant_variable_candidates = _list_text(thesis.get("top_dominant_variables"))
    dominant_variable = (
        dominant_variable_candidates[0]
        if dominant_variable_candidates
        else _text(thesis.get("dominant_lens"))
        or _format_label(target_type)
        or "dominant structural discriminator"
    )
    evidence_state = _text(thesis.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS"
    claim_contract_register = list(m54.get("congruence_claim_contract_register", []) or [])
    financial_rows = list(
        m53.get("authoritative_financial_exposure_register", m53.get("skill_financial_exposure_register", [])) or []
    )
    tad_rows = list(
        m54.get("authoritative_tad_action_register", m54.get("skill_expanded_tad_action_register", [])) or []
    )
    primary_action = dict((list(thesis.get("top_actions", []) or []) or [{}])[0] or {})
    primary_financial = dict(thesis.get("primary_financial_exposure", {}) or {})
    primary_peer = dict(thesis.get("primary_peer_comparison", {}) or {})
    primary_redesign = dict(thesis.get("conditional_redesign", {}) or {})

    structural_financial_rows: list[dict[str, Any]] = []
    for row in financial_rows[:3]:
        structural_financial_rows.append(
            {
                "structural_assumption": _text(row.get("trigger")) or _text(row.get("financial_exposure_type")),
                "evidence_state": evidence_state,
                "financial_exposure_if_wrong": _text(row.get("why_it_matters")),
                "evidence_needed": _list_text(row.get("evidence_needed")),
                "allowed_financial_output": ["scenario framing"],
                "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
            }
        )

    evidence_state_by_layer_register: list[dict[str, Any]] = []
    if minimum_evidence or structural_financial_rows:
        evidence_state_by_layer_register.append(
            {
                "layer": "structural runtime bridge",
                "evidence_state": evidence_state,
                "dominant_open_questions": minimum_evidence,
                "observed_support": [],
                "structural_risk_if_wrong": _text(primary_financial.get("why_it_matters"))
                or _text(primary_financial.get("financial_exposure_if_wrong"))
                or _text(thesis.get("dominant_risk")),
                "linked_conflicts": [dominant_conflict] if dominant_conflict else [],
                "linked_problem_frames": [reframed_problem] if reframed_problem else [],
            }
        )

    competitive_comparison_register: list[dict[str, Any]] = []
    if primary_peer:
        competitive_comparison_register.append(
            {
                "peer_type": _text(primary_peer.get("comparison_basis"))
                or _text(primary_peer.get("peer_type"))
                or _text(primary_peer.get("comparison_status"))
                or "bounded peer normalization required",
                "evidence_state": evidence_state,
                "transferability": _text(primary_peer.get("comparison_status")) or "conditional on normalized comparison basis",
            }
        )

    conditional_redesign_register: list[dict[str, Any]] = []
    if primary_redesign:
        conditional_redesign_register.append(
            {
                "hypothesis": reframed_problem or stated_problem,
                "evidence_state": evidence_state,
                "if_confirmed": _text(primary_redesign.get("if_confirmed")) or _text(primary_redesign.get("redesign_direction")),
                "redesign_direction": _text(primary_redesign.get("redesign_direction")) or _text(primary_redesign.get("if_confirmed")),
                "if_falsified": _text(primary_redesign.get("if_falsified")),
                "next_evidence": minimum_evidence,
            }
        )

    structural_claim_permission_register: list[dict[str, Any]] = []
    if claim_contract_register or minimum_evidence:
        structural_claim_permission_register.append(
            {
                "claim": "skill_structural_claim_bundle",
                "permission": "hypothesis_only",
                "evidence_required": minimum_evidence,
                "current_evidence": "Skill-first runtime synthesis remains bounded by L2 structural priors and case-level gaps.",
                "allowed_language": "Conditional structural framing only.",
                "forbidden_language": "Local truth, superiority or hard financial closure as fact.",
            }
        )

    structural_output_mode_classifier_table = [
        {
            "asset": target_name,
            "recommended_output_mode": report_mode,
            "activation_state": "activated_secondary",
            "activation_reason": "Skill-first executive thesis and report compression are available from bounded runtime signals.",
            "required_claims": ["skill_structural_claim_bundle"] if structural_claim_permission_register else [],
            "primary_report_type_guard": [report_mode],
            "why": reframed_problem or stated_problem,
        }
    ]
    structural_output_mode_summary = {
        "primary_report_type": report_mode,
        "activated_secondary_modes": [report_mode],
        "blocked_secondary_modes": [],
        "policy_note": "Structural output modes remain governed bounded surfaces until upstream full-live structural lanes replace the bridge.",
        "eligible_primary_modes": [report_mode],
        "non_promotable_primary_modes": [],
        "leading_primary_promotion_candidate": report_mode,
        "primary_promotion_policy_note": "Promotion remains bounded by the skill authority state and the evidence ceiling.",
        "activation_count": 1,
        "blocked_count": 0,
        "eligible_primary_count": 1,
    }
    structural_primary_promotion_gate = {
        "override_allowed": False,
        "reason": "Skill-first report package synthesis remains bounded and should not silently promote the visible report type.",
        "evidence_state_ceiling": "L2",
    }

    return {
        "canonical_problem_frame": {
            "leading_structural_output_mode": report_mode,
            "stated_problem": stated_problem,
            "reframed_problem": reframed_problem,
            "dominant_conflict": dominant_conflict,
            "minimum_evidence_to_discriminate": " + ".join(minimum_evidence),
            "minimum_evidence_source": minimum_evidence_source,
            "problem_frame_active": _text(thesis.get("thesis_state")) == "admissible_structural_thesis",
            "reasoning_path": "structural_first" if _text(thesis.get("thesis_state")) == "admissible_structural_thesis" else "legacy_decision_gating_only",
            "evidence_state": evidence_state,
        },
        "claim_contract_register": claim_contract_register,
        "structural_claim_permission_register": structural_claim_permission_register,
        "report_type_classifier_table": [
            {
                "asset": target_name,
                "recommended_report_type": report_mode,
                "why": reframed_problem or stated_problem,
                "allowed_claims": ["congruence_gold_nugget_claim (conditional)"],
                "blocked_claims": ["roi_claim", "savings_claim"],
            }
        ],
        "structural_output_mode_classifier_table": structural_output_mode_classifier_table,
        "structural_output_mode_summary": structural_output_mode_summary,
        "structural_primary_promotion_gate": structural_primary_promotion_gate,
        "system_abstraction": {
            "selected_archetype_id": f"{target_type or 'generic'}_skill_package_bridge",
            "asset_type": {"statement": _format_label(target_type) or target_name},
            "dominant_process_type": {"statement": dominant_variable},
        },
        "dominant_variable_register": [
            {
                "variable": dominant_variable,
                "layer": "structural",
                "evidence_state": evidence_state,
                "why_it_could_matter": _text(primary_financial.get("why_it_matters")) or reframed_problem,
                "decision_impact": _text(primary_action.get("action")) or _text(primary_action.get("status")) or "bounded structural sequencing",
            }
        ]
        if dominant_variable
        else [],
        "cross_layer_conflict_register": [
            {
                "conflict": dominant_conflict,
                "layers_involved": ["operations", "finance", "comparison"],
                "why_it_matters": _text(thesis.get("why_it_matters")) or _text(primary_financial.get("why_it_matters")),
                "potential_redesign_direction": _text(primary_redesign.get("redesign_direction")) or _text(primary_redesign.get("if_confirmed")),
                "evidence_state": evidence_state,
            }
        ]
        if dominant_conflict
        else [],
        "problem_framing_register": [
            {
                "stated_problem": stated_problem,
                "reframed_problem": reframed_problem,
                "why_original_framing_may_be_wrong": _text(thesis.get("hidden_assumption_at_risk"))
                or _text(thesis.get("why_current_question_is_premature"))
                or _text(thesis.get("surprising_but_evidenced_takeaway")),
                "evidence_needed": "; ".join(minimum_evidence),
                "strategic_risk": _text(thesis.get("dominant_risk"))
                or _text(primary_financial.get("why_it_matters")),
                "evidence_state": evidence_state,
            }
        ]
        if reframed_problem or dominant_conflict
        else [],
        "structural_benchmark_register": [],
        "competitive_comparison_register": competitive_comparison_register,
        "conditional_redesign_register": conditional_redesign_register,
        "structural_financial_exposure_register": structural_financial_rows,
        "evidence_state_by_layer_register": evidence_state_by_layer_register,
        "minimum_evidence_for_discrimination_register": [
            {
                "rival_hypotheses": [value for value in [stated_problem, reframed_problem] if value],
                "minimum_evidence": ", ".join(minimum_evidence),
                "source": minimum_evidence_source,
                "what_it_confirms": reframed_problem,
                "what_it_falsifies": dominant_conflict,
                "unlocks": _text(primary_action.get("action")) or _text(primary_action.get("status")),
            }
        ]
        if minimum_evidence
        else [],
        "expanded_structural_tad_action_register": tad_rows,
    }


def build_skill_first_package_support_context(
    *,
    target_definition: dict[str, Any] | None = None,
    executive_thesis: dict[str, Any] | None = None,
    motor_053_output: dict[str, Any] | None = None,
    motor_054_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target_definition = dict(target_definition or {})
    thesis = dict(executive_thesis or {})
    m53 = dict(motor_053_output or {})
    m54 = dict(motor_054_output or {})

    target_name = _text(target_definition.get("target_name")) or _format_label(target_definition.get("target_type")) or "the asset"
    report_mode = _text(thesis.get("report_mode")) or _default_skill_report_mode(_text(target_definition.get("target_type")))
    minimum_evidence = _list_text(thesis.get("minimum_discriminating_evidence"))
    minimum_evidence_source = _text(thesis.get("minimum_discriminating_evidence_source")) or "motor_047.executive_thesis"
    primary_financial = dict(thesis.get("primary_financial_exposure", {}) or {})
    primary_peer = dict(thesis.get("primary_peer_comparison", {}) or {})
    authoritative_tad_rows = list(
        m54.get("authoritative_tad_action_register", m54.get("skill_expanded_tad_action_register", [])) or []
    )
    authoritative_gold_rows = list(
        m54.get("authoritative_gold_nugget_register", m54.get("skill_gold_nugget_register", [])) or []
    )
    financial_rows = list(
        m53.get("authoritative_financial_exposure_register", m53.get("skill_financial_exposure_register", [])) or []
    )
    claim_contract_rows = list(m54.get("congruence_claim_contract_register", []) or [])
    first_gold = dict((authoritative_gold_rows or [{}])[0] or {})

    claim_permission_register: list[dict[str, Any]] = []
    allowed_count = 0
    conditional_count = 0
    prohibited_count = 0
    for row in claim_contract_rows:
        permission = _text(row.get("permission")) or "conditional"
        normalized_permission = permission.lower()
        if normalized_permission == "allowed":
            allowed_count += 1
        elif normalized_permission == "prohibited":
            prohibited_count += 1
        else:
            conditional_count += 1
        claim_permission_register.append(
            {
                "claim_name": _text(row.get("claim_id")) or _text(row.get("statement")) or "bounded_claim",
                "current_permission": permission,
                "reason_if_blocked": _text(row.get("falsification_condition")),
                "upgrade_path": _list_text(row.get("minimum_evidence_required")),
            }
        )

    if not claim_permission_register and minimum_evidence:
        conditional_count = 1
        claim_permission_register.append(
            {
                "claim_name": "skill_structural_claim_bundle",
                "current_permission": "conditional",
                "reason_if_blocked": "Skill-first synthesis remains bounded by structural priors and case-level evidence gaps.",
                "upgrade_path": minimum_evidence,
            }
        )

    decision_permission_register: list[dict[str, Any]] = []
    for row in authoritative_tad_rows[:5]:
        evidence_needed = _list_text(row.get("evidence_needed"))
        decision_permission_register.append(
            {
                "decision_name": _text(row.get("strategic_action")),
                "admissibility_state": _text(row.get("status")) or "NEEDS REVIEW",
                "current_variable_bottleneck": _text(row.get("trigger")) or (evidence_needed[0] if evidence_needed else ""),
                "allowed_action": _text(row.get("why")) or _text(row.get("prohibited_action")),
                "evidence_needed": evidence_needed,
            }
        )

    variable_bottleneck_register = [
        {"variable_name": item}
        for item in minimum_evidence[:5]
    ]

    scenario_space = []
    for row in authoritative_gold_rows[:3]:
        evidence_needed = _list_text(row.get("minimum_evidence")) or minimum_evidence
        scenario_space.append(
            {
                "scenario": _text(row.get("gold_nugget")),
                "financial_meaning": _text(row.get("why_it_matters")),
                "evidence_needed": ", ".join(evidence_needed),
                "falsification_condition": _text(row.get("linked_dependency")) or "Asset-specific evidence closes the live contradiction differently.",
            }
        )

    decision_front_rows = []
    for row in authoritative_tad_rows[:5]:
        decision_front_rows.append(
            {
                "decision_front": _text(row.get("strategic_action")),
                "current_status": _text(row.get("status")),
            }
        )

    report_readiness_reason = (
        _text(thesis.get("why_current_question_is_premature"))
        or _text(thesis.get("why_it_matters"))
        or _text(first_gold.get("what_to_do_next"))
        or "Bounded structural evidence supports screening-grade framing only."
    )
    report_readiness_register = {
        "report_type_allowed": [report_mode] if report_mode else [],
        "report_type_prohibited": (
            ["Full Technical Decision Intelligence Report"]
            if report_mode != "Full Technical Decision Intelligence Report"
            else []
        ),
        "reason": report_readiness_reason,
    }

    output_blocks: list[dict[str, Any]] = []
    output_blocks.append(
        {
            "block_type": "decision_admissibility_block",
            "decision_state": _text(thesis.get("thesis_state")) or "bounded screening only",
            "primary_block_reason": report_readiness_reason,
            "decision_evaluated": _text((authoritative_tad_rows[0] or {}).get("strategic_action")) if authoritative_tad_rows else "REQUEST_MINIMUM_EVIDENCE",
            "recommended_action": _text((authoritative_tad_rows[0] or {}).get("prohibited_action")) if authoritative_tad_rows else "Keep the case bounded until discriminating evidence is observed.",
        }
    )
    if minimum_evidence:
        output_blocks.append(
            {
                "block_type": "minimum_evidence_pack_block",
                "rows": [
                    {
                        "evidence_item": item,
                        "source": minimum_evidence_source,
                        "why_needed": _text(first_gold.get("why_it_matters")) or report_readiness_reason,
                        "cases_resolved": [_text(target_definition.get("target_type")) or "current_case"],
                        "effort": "CRITICAL",
                        "decision_unlock": _text((authoritative_tad_rows[0] or {}).get("strategic_action")) if authoritative_tad_rows else "bounded decision advance",
                    }
                    for item in minimum_evidence
                ],
            }
        )
    if scenario_space:
        output_blocks.append(
            {
                "block_type": "scenario_space_block",
                "rows": scenario_space,
            }
        )
    if financial_rows:
        output_blocks.append(
            {
                "block_type": "financial_exposure_block",
                "rows": [
                    {
                        "assumption": _text(thesis.get("reframed_problem")) or _text(target_name),
                        "current_support": _text(row.get("why_it_matters")) or "Bounded structural reading only.",
                        "downside_if_wrong": _text(row.get("governed_exposure_category")) or _text(row.get("financial_exposure_type")),
                        "evidence_needed": ", ".join(_list_text(row.get("evidence_needed"))),
                        "financial_consequence": _text(row.get("tad_consequence")) or "Do not harden financial claims yet.",
                        "linked_decision_front": _text((authoritative_tad_rows[0] or {}).get("strategic_action")) if authoritative_tad_rows else "REQUEST_MINIMUM_EVIDENCE",
                    }
                    for row in financial_rows[:3]
                ],
            }
        )
    if decision_permission_register:
        output_blocks.append(
            {
                "block_type": "decision_fronts_block",
                "rows": [
                    {
                        "decision_front": _text(row.get("decision_name")),
                        "current_status": _text(row.get("admissibility_state")),
                        "why": _text(row.get("allowed_action")),
                        "required_evidence": ", ".join(_list_text(row.get("evidence_needed"))),
                        "admissible_action": _text(row.get("allowed_action")) or "Keep the case bounded.",
                    }
                    for row in decision_permission_register[:5]
                ],
            }
        )

    return {
        "output_blocks": output_blocks,
        "composite_reading": {
            "decision_state": "Blocked pending minimum discriminating evidence."
            if minimum_evidence
            else "Bounded structural screening only."
        },
        "variable_bottleneck_register": variable_bottleneck_register,
        "decision_front_register": decision_front_rows,
        "scenario_space": scenario_space,
        "report_readiness_register": report_readiness_register,
        "claim_permission_summary": {
            "allowed": allowed_count,
            "allowed_count": allowed_count,
            "conditional": conditional_count,
            "conditional_count": conditional_count,
            "prohibited": prohibited_count,
            "prohibited_count": prohibited_count,
        },
        "claim_permission_register": claim_permission_register,
        "decision_permission_register": decision_permission_register,
        "primary_peer_comparison": primary_peer,
        "primary_financial_exposure": primary_financial,
    }


def build_skill_first_runtime_analysis_registers(
    *,
    target_definition: dict[str, Any] | None = None,
    executive_thesis: dict[str, Any] | None = None,
    motor_053_output: dict[str, Any] | None = None,
    motor_054_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target_definition = dict(target_definition or {})
    thesis = dict(executive_thesis or {})
    m53 = dict(motor_053_output or {})
    m54 = dict(motor_054_output or {})

    target_name = _text(target_definition.get("target_name")) or _format_label(target_definition.get("target_type")) or "the asset"
    minimum_evidence = _list_text(thesis.get("minimum_discriminating_evidence"))
    dominant_conflict = _text(thesis.get("dominant_contradiction"))
    reframed_problem = _text(thesis.get("reframed_problem"))
    why_it_matters = _text(thesis.get("why_it_matters"))
    gold_rows = list(
        m54.get("authoritative_gold_nugget_register", m54.get("skill_gold_nugget_register", [])) or []
    )
    tad_rows = list(
        m54.get("authoritative_tad_action_register", m54.get("skill_expanded_tad_action_register", [])) or []
    )
    financial_rows = list(
        m53.get("authoritative_financial_exposure_register", m53.get("skill_financial_exposure_register", [])) or []
    )

    def _family_from_theme(theme: str) -> str:
        normalized = _normalize_label(theme)
        if normalized in {"comparison invalidity", "boundary leakage"}:
            return "conflict"
        if normalized in {"maintenance reality", "controls or schedule", "measurement minimality"}:
            return "tension"
        if normalized in {"combined hypothesis", "model prematurity"}:
            return "evidence_gap"
        return "plausible_hypothesis"

    inference_records: list[dict[str, Any]] = []
    for idx, row in enumerate(gold_rows[:5], start=1):
        evidence_needed = _list_text(row.get("minimum_evidence")) or minimum_evidence
        family = _family_from_theme(_text(row.get("nugget_theme")))
        urgency = max(0.55, 0.92 - ((idx - 1) * 0.07))
        relevance = max(0.55, 0.90 - ((idx - 1) * 0.05))
        plausibility = max(0.50, 0.86 - ((idx - 1) * 0.04))
        case_id = f"skill_case_{idx:02d}"
        inference_records.append(
            {
                "case_id": case_id,
                "case_name": _text(row.get("nugget_theme")) or f"Skill case {idx}",
                "claim_family": family,
                "plausibility_score": plausibility,
                "decision_relevance_score": relevance,
                "validation_urgency_score": urgency,
                "conditional_statement": _text(row.get("gold_nugget")),
                "inference_logic": _text(row.get("why_it_matters")) or why_it_matters,
                "dependency_assumptions": evidence_needed,
                "base_support_traces": [
                    value
                    for value in [
                        _text(row.get("source_combination_id")),
                        _text(row.get("source_pattern_id")),
                        _text(row.get("linked_financial_exposure")),
                        _text(row.get("linked_dependency")),
                    ]
                    if value
                ],
                "score_rationale": {
                    "plausibility": "Registry-first pattern or combination remains bounded at L2 and still needs local falsification.",
                    "decision_relevance": _text(row.get("what_to_do_next")) or "The framing changes admissible capital or measurement sequencing.",
                    "validation_urgency": "The case stays bounded until the minimum discriminating evidence is observed.",
                },
                "validation_requirement": ", ".join(evidence_needed),
            }
        )

    conflict_register: list[dict[str, Any]] = []
    if dominant_conflict:
        linked_case_id = inference_records[0]["case_id"] if inference_records else "skill_case_01"
        conflict_register.append(
            {
                "conflict_id": "skill_conflict_01",
                "inference_case_id": linked_case_id,
                "conflict_name": dominant_conflict,
                "conflict_type": "structural_contradiction",
                "blocking_status": "bounded_until_discriminated",
                "plausibility_score": 0.88,
                "decision_relevance_score": 0.93,
                "validation_urgency_score": 0.94,
                "conflict_statement": reframed_problem or dominant_conflict,
                "validation_requirement": ", ".join(minimum_evidence) or "bounded discriminating evidence",
            }
        )

    validation_queue: list[dict[str, Any]] = []
    for idx, row in enumerate(tad_rows[:5], start=1):
        linked_case_id = inference_records[min(idx - 1, len(inference_records) - 1)]["case_id"] if inference_records else f"skill_case_{idx:02d}"
        validation_queue.append(
            {
                "queue_position": idx,
                "case_id": linked_case_id,
                "case_name": _text(row.get("strategic_action")) or f"Skill validation {idx}",
                "claim_family": "plausible_hypothesis",
                "validation_urgency_score": max(0.55, 0.94 - ((idx - 1) * 0.06)),
                "decision_relevance_score": max(0.55, 0.91 - ((idx - 1) * 0.05)),
                "validation_requirement": ", ".join(_list_text(row.get("evidence_needed")) or minimum_evidence),
            }
        )

    next_best_questions: list[dict[str, Any]] = []
    for idx, evidence_item in enumerate(minimum_evidence[:5], start=1):
        supporting_row = dict((gold_rows[min(idx - 1, len(gold_rows) - 1):] or gold_rows[:1] or [{}])[0] or {})
        linked_case_id = inference_records[min(idx - 1, len(inference_records) - 1)]["case_id"] if inference_records else f"skill_case_{idx:02d}"
        next_best_questions.append(
            {
                "question_id": f"skill_q_{idx:02d}",
                "question": f"Can the case produce bounded evidence for: {evidence_item}?",
                "linked_case": linked_case_id,
                "why_it_matters": _text(supporting_row.get("why_it_matters")) or why_it_matters,
                "how_to_answer": _text(supporting_row.get("what_to_do_next")) or "Request the minimum discriminating evidence directly before expanding instrumentation or modeling scope.",
                "urgency": "high" if idx <= 2 else "medium",
            }
        )

    evidence_gap_register: list[dict[str, Any]] = []
    for idx, evidence_item in enumerate(minimum_evidence[:5], start=1):
        evidence_gap_register.append(
            {
                "gap_id": f"skill_gap_{idx:02d}",
                "description": evidence_item,
                "epistemic_impact": "Blocks upgrade from structural prior to asset-supported reasoning.",
                "blocking_inference_cases": [record["case_id"] for record in inference_records[:2]] or ["skill_case_01"],
                "validation_urgency_score": max(0.55, 0.93 - ((idx - 1) * 0.05)),
            }
        )

    uncertainty_register: list[dict[str, Any]] = []
    if minimum_evidence or financial_rows:
        uncertainty_register.append(
            {
                "uncertainty_name": "dominant_variable_not_yet_discriminated",
                "statement": why_it_matters or reframed_problem or dominant_conflict,
                "evidence_needed": minimum_evidence,
            }
        )

    opportunity_candidates: list[dict[str, Any]] = []
    for idx, row in enumerate(financial_rows[:3], start=1):
        opportunity_candidates.append(
            {
                "opportunity_id": f"skill_opp_{idx:02d}",
                "opportunity_name": _text(row.get("governed_exposure_category")) or _text(row.get("financial_exposure_type")),
                "opportunity_type": "conditional_pathway",
                "plausibility_score": max(0.55, 0.84 - ((idx - 1) * 0.05)),
                "decision_relevance_score": max(0.55, 0.89 - ((idx - 1) * 0.05)),
                "validation_urgency_score": max(0.55, 0.86 - ((idx - 1) * 0.05)),
                "conditional_statement": _text(row.get("why_it_matters")),
                "dependency_assumptions": _list_text(row.get("evidence_needed")) or minimum_evidence,
                "validation_requirement": ", ".join(_list_text(row.get("evidence_needed")) or minimum_evidence),
            }
        )

    return {
        "inference_records": inference_records,
        "conflict_register": conflict_register,
        "validation_queue": validation_queue,
        "next_best_questions": next_best_questions,
        "evidence_gap_register": evidence_gap_register,
        "uncertainty_register": uncertainty_register,
        "opportunity_candidates": opportunity_candidates,
    }
