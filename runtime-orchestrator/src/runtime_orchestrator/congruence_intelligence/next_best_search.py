from __future__ import annotations

from typing import Any

from .schemas import text

_PRIORITY_BASE = {
    "critical": 100,
    "high": 70,
    "medium": 40,
    "low": 20,
}

_SEVERITY_BONUS = {
    "critical": 35,
    "high": 20,
    "medium": 10,
    "low": 4,
}

_GENERIC_FAMILY_TOKENS = {"record", "page", "clues", "clue"}

_HIGH_DIFFICULTY_FAMILIES = {
    "satellite_photo_clues",
    "site_plan_or_photo_clues",
    "parcel_gis",
    "refrigeration_clues",
    "equipment_listing",
    "technical_sourcebook",
}

_MEDIUM_DIFFICULTY_FAMILIES = {
    "property_listing",
    "leasing_brochure",
    "tenant_operator_page",
    "operator_page",
    "property_photo_clues",
    "permit_record",
    "environmental_registry",
    "utility_service_territory",
    "logistics_market_report",
    "market_or_product_description",
}

_AUTHORITATIVE_PUBLIC_FAMILIES = {
    "county_assessor",
    "parcel_gis",
    "property_record",
    "benchmark_record",
    "permit_record",
    "environmental_registry",
    "utility_service_territory",
    "utility_tariff_schedule",
    "utility_rate_context",
    "business_registry",
    "zoning_record",
}

_OPERATOR_CENTRIC_FAMILIES = {
    "operator_page",
    "tenant_operator_page",
    "lease_summary",
    "owner_asset_page",
}

_FAMILY_VALUE_BY_NEED_ID: dict[str, dict[str, int]] = {
    "asset_identity_anchor": {
        "county_assessor": 18,
        "parcel_gis": 16,
        "property_record": 16,
        "owner_asset_page": 12,
        "benchmark_record": 10,
    },
    "utility_territory_and_tariff_context": {
        "utility_service_territory": 18,
        "utility_tariff_schedule": 16,
        "utility_rate_context": 12,
    },
    "warehouse_subtype_classification": {
        "leasing_brochure": 16,
        "tenant_operator_page": 14,
        "owner_asset_page": 12,
        "zoning_record": 12,
        "county_assessor": 12,
        "property_listing": 10,
        "satellite_photo_clues": 4,
    },
    "dock_and_service_intensity": {
        "site_plan_or_photo_clues": 18,
        "property_listing": 14,
        "leasing_brochure": 14,
        "tenant_operator_page": 12,
        "logistics_market_report": 6,
        "satellite_photo_clues": 6,
    },
    "refrigeration_presence": {
        "refrigeration_clues": 18,
        "permit_record": 16,
        "operator_page": 14,
        "leasing_brochure": 12,
        "property_listing": 10,
        "satellite_photo_clues": 4,
    },
    "operator_boundary_and_control": {
        "lease_summary": 18,
        "tenant_operator_page": 16,
        "business_registry": 10,
        "property_listing": 8,
    },
    "mhe_charging_and_mechanical_clues": {
        "permit_record": 16,
        "equipment_listing": 14,
        "property_photo_clues": 12,
        "operator_page": 10,
        "satellite_photo_clues": 6,
    },
    "cold_chain_confirmation": {
        "refrigeration_clues": 18,
        "permit_record": 16,
        "operator_page": 14,
        "leasing_brochure": 12,
        "property_listing": 10,
    },
    "process_and_permit_profile": {
        "permit_record": 18,
        "environmental_registry": 16,
        "operator_page": 10,
        "property_record": 8,
        "industry_guidance": 6,
    },
    "thermal_system_and_utility_mix": {
        "utility_service_territory": 18,
        "permit_record": 16,
        "environmental_registry": 14,
        "technical_sourcebook": 10,
        "operator_page": 6,
    },
    "throughput_proxy_and_schedule": {
        "operator_page": 16,
        "market_or_product_description": 14,
        "industry_guidance": 10,
        "business_registry": 8,
    },
}


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _remaining_budget_state(search_budget_register: list[dict[str, Any]]) -> str:
    for row in list(search_budget_register or []):
        if text(row.get("budget_scope")) == "total_public_discovery":
            return text(row.get("budget_state")) or "bounded"
    return "bounded"


def _public_search_likelihood(*, search_family: str, budget_state: str, acquisition_difficulty: str) -> str:
    if budget_state == "exhausted":
        if acquisition_difficulty == "high":
            return "low"
        return "medium"
    if search_family in _OPERATOR_CENTRIC_FAMILIES or acquisition_difficulty == "high":
        return "medium"
    return "high"


def _priority_score(need: dict[str, Any], budget_state: str) -> int:
    base = _PRIORITY_BASE.get(text(need.get("priority")).lower(), 20)
    bonuses = sum(
        _SEVERITY_BONUS.get(str(severity).lower(), 0)
        for severity in list(need.get("matched_gap_severities", []) or [])
    )
    if budget_state == "bounded":
        base += 10
    elif budget_state == "exhausted":
        base -= 15
    return max(base + bonuses, 0)


def _family_tokens(family: str) -> set[str]:
    return {
        token
        for token in text(family).lower().replace("-", "_").split("_")
        if token and token not in _GENERIC_FAMILY_TOKENS
    }


def _family_matches(candidate_family: str, observed_family: str) -> bool:
    candidate = text(candidate_family).lower()
    observed = text(observed_family).lower()
    if not candidate or not observed:
        return False
    if candidate == observed:
        return True
    candidate_tokens = _family_tokens(candidate)
    observed_tokens = _family_tokens(observed)
    if candidate == "county_assessor" and observed_tokens.intersection({"assessor", "appraisal", "cad", "parcel"}):
        return True
    if candidate == "permit_record" and "permit" in observed_tokens:
        return True
    if candidate == "property_record" and observed_tokens.intersection({"property", "parcel"}):
        return True
    if candidate == "utility_service_territory" and observed_tokens.intersection({"utility", "territory"}):
        return True
    if not candidate_tokens or not observed_tokens:
        return False
    overlap = len(candidate_tokens.intersection(observed_tokens))
    required_overlap = min(2, len(candidate_tokens), len(observed_tokens))
    return overlap >= max(required_overlap, 1)


def _history_count(summary_rows: list[dict[str, Any]], family: str) -> int:
    count = 0
    for row in list(summary_rows or []):
        payload = _as_dict(row)
        if _family_matches(family, text(payload.get("source_family"))):
            count += int(payload.get("count", 0) or 0)
    return count


def _yield_memory_entry(dynamic_case_state: dict[str, Any], family: str) -> dict[str, Any]:
    by_source_family = _as_dict(dynamic_case_state.get("source_family_yield_memory"))
    for observed_family, row in by_source_family.items():
        if _family_matches(family, observed_family):
            return _as_dict(row)
    return {}


def _acquisition_memory_entry(dynamic_case_state: dict[str, Any], family: str) -> dict[str, Any]:
    acquisition_memory = _as_dict(
        _as_dict(dynamic_case_state.get("source_acquisition_yield_memory")).get("by_source_family")
    )
    for observed_family, row in acquisition_memory.items():
        if _family_matches(family, observed_family):
            return _as_dict(row)
    return {}


def _discriminative_value(need_id: str, family: str) -> int:
    return int(_FAMILY_VALUE_BY_NEED_ID.get(need_id, {}).get(family, 0))


def _gap_relevance(matched_gap_types: list[str], family: str) -> int:
    family_tokens = _family_tokens(family)
    score = 0
    if "asset_primary_anchor_missing" in matched_gap_types and family in {
        "county_assessor",
        "parcel_gis",
        "property_record",
        "owner_asset_page",
        "benchmark_record",
    }:
        score += 6
    if "asset_context_readiness" in matched_gap_types and family in {
        "tenant_operator_page",
        "lease_summary",
        "business_registry",
        "operator_page",
    }:
        score += 5
    if "asset_energy_behavior_reference" in matched_gap_types and family_tokens.intersection(
        {"utility", "tariff", "demand", "dock", "refrigeration", "thermal", "permit", "equipment", "charging"}
    ):
        score += 6
    return score


def _regulatory_value(dynamic_case_state: dict[str, Any], family: str) -> int:
    triggers = " ".join(
        text(item).lower()
        for item in _as_list(dynamic_case_state.get("active_regulatory_triggers"))
        + _as_list(dynamic_case_state.get("jurisdiction_scope"))
    )
    score = 0
    if any(token in triggers for token in ("ll84", "ll97", "benchmark", "benchmarking", "nyc")):
        if family == "benchmark_record":
            score += 14
        elif family == "permit_record":
            score += 8
    if any(token in triggers for token in ("ercot", "utility", "demand", "tceq", "oncor", "centerpoint", "austin")):
        if family == "utility_service_territory":
            score += 12
        elif family == "utility_tariff_schedule":
            score += 10
        elif family == "permit_record":
            score += 6
    if any(token in triggers for token in ("title24", "calgreen", "permit", "dob", "emission")) and family == "permit_record":
        score += 8
    return score


def _comparison_unlock_value(need_id: str, family: str, discriminative_value: int) -> int:
    comparison_critical_needs = {
        "utility_territory_and_tariff_context",
        "warehouse_subtype_classification",
        "dock_and_service_intensity",
        "refrigeration_presence",
        "cold_chain_confirmation",
        "thermal_system_and_utility_mix",
        "throughput_proxy_and_schedule",
    }
    if need_id not in comparison_critical_needs:
        return 0
    if discriminative_value >= 16:
        return 8
    if discriminative_value >= 12:
        return 5
    return 0


def _acquisition_difficulty(family: str) -> str:
    if family in _HIGH_DIFFICULTY_FAMILIES:
        return "high"
    if family in _MEDIUM_DIFFICULTY_FAMILIES:
        return "medium"
    return "low"


def _budget_fit(*, family: str, budget_state: str) -> int:
    difficulty = _acquisition_difficulty(family)
    if budget_state == "exhausted":
        if difficulty == "high":
            return -20
        if difficulty == "medium":
            return -6
        return 0
    if budget_state == "bounded":
        if difficulty == "low":
            return 4
        if difficulty == "medium":
            return 1
        return -1
    return 0


def _operator_fit(*, need_id: str, family: str) -> int:
    if family not in _OPERATOR_CENTRIC_FAMILIES:
        return 4 if family in _AUTHORITATIVE_PUBLIC_FAMILIES else 0
    if need_id in {"operator_boundary_and_control", "throughput_proxy_and_schedule"}:
        return 4
    return -3


def _template_prior(order: int, total: int) -> int:
    return max((total - order) * 2, 0)


def _family_score_components(
    *,
    need: dict[str, Any],
    family: str,
    order: int,
    total: int,
    budget_state: str,
    dynamic_case_state: dict[str, Any],
) -> tuple[dict[str, int], dict[str, Any]]:
    need_id = text(need.get("need_id"))
    matched_gap_types = [text(item) for item in list(need.get("matched_gap_types", []) or []) if text(item)]
    preference_hints = {text(item) for item in list(need.get("source_family_preference_hints", []) or []) if text(item)}
    success_summary = list(dynamic_case_state.get("source_family_success_summary", []) or [])
    failure_summary = list(dynamic_case_state.get("source_family_failure_summary", []) or [])
    yield_entry = _yield_memory_entry(dynamic_case_state, family)
    acquisition_entry = _acquisition_memory_entry(dynamic_case_state, family)
    yield_band = text(yield_entry.get("yield_band"))
    success_count = _history_count(success_summary, family)
    failure_count = _history_count(failure_summary, family)
    recommended_acquisition_mode = text(acquisition_entry.get("recommended_acquisition_mode"))

    components = {
        "template_prior": _template_prior(order, total),
        "jurisdiction_fit": 18 if family in preference_hints else 0,
        "discriminative_value": _discriminative_value(need_id, family),
        "success_memory": min(success_count * 5, 10),
        "failure_penalty": -min(failure_count * 7, 21),
        "yield_memory": {
            "high": 12,
            "medium": 8,
            "productive": 8,
            "low": -5,
            "identity_only": -8,
        }.get(yield_band, 0),
        "operator_fit": _operator_fit(need_id=need_id, family=family),
        "regulatory_value": _regulatory_value(dynamic_case_state, family),
        "comparison_unlock_value": _comparison_unlock_value(
            need_id,
            family,
            _discriminative_value(need_id, family),
        ),
        "gap_relevance": _gap_relevance(matched_gap_types, family),
        "budget_fit": _budget_fit(family=family, budget_state=budget_state),
        "acquisition_memory": {
            "prefer_browser": 6,
            "prefer_static": 2,
            "avoid_browser": -8,
        }.get(recommended_acquisition_mode, 0),
    }
    metadata = {
        "observed_success_count": success_count,
        "observed_failure_count": failure_count,
        "yield_band": yield_band or "none",
        "acquisition_difficulty": _acquisition_difficulty(family),
        "recommended_acquisition_mode": recommended_acquisition_mode or "undecided",
    }
    return components, metadata


def _selection_reason(
    *,
    family: str,
    components: dict[str, int],
    metadata: dict[str, Any],
) -> str:
    reasons: list[str] = []
    if components.get("jurisdiction_fit", 0) > 0:
        reasons.append("matches jurisdiction-preferred routing")
    if components.get("discriminative_value", 0) >= 14:
        reasons.append("has high discriminative value for this discovery need")
    if components.get("regulatory_value", 0) > 0:
        reasons.append("aligns with active tariff or regulatory triggers")
    if components.get("comparison_unlock_value", 0) > 0:
        reasons.append("unlocks fair-comparison gating")
    if int(metadata.get("observed_failure_count", 0) or 0) > 0:
        reasons.append("beats previously failing alternatives")
    yield_band = text(metadata.get("yield_band"))
    if yield_band in {"high", "medium", "productive"}:
        reasons.append(f"has {yield_band} prior yield memory")
    acquisition_preference = text(metadata.get("recommended_acquisition_mode"))
    if acquisition_preference == "prefer_browser":
        reasons.append("has prior evidence that browser fallback is justified")
    elif acquisition_preference == "avoid_browser":
        reasons.append("avoids previously wasteful browser fallback")
    if components.get("budget_fit", 0) < 0:
        reasons.append("stays admissible despite tight discovery budget")
    if not reasons and components.get("template_prior", 0) > 0:
        reasons.append("retains the strongest governed template prior")
    if not reasons:
        reasons.append("remains the strongest available public route")
    return f"Selected {family} because it " + ", ".join(reasons[:3]) + "."


def _build_family_rank_register(
    *,
    need: dict[str, Any],
    budget_state: str,
    dynamic_case_state: dict[str, Any],
) -> list[dict[str, Any]]:
    families = [text(item) for item in list(need.get("search_family_options", []) or []) if text(item)]
    ranked: list[dict[str, Any]] = []
    total = len(families)
    for order, family in enumerate(families, start=1):
        components, metadata = _family_score_components(
            need=need,
            family=family,
            order=order,
            total=total,
            budget_state=budget_state,
            dynamic_case_state=dynamic_case_state,
        )
        score = sum(int(value) for value in components.values())
        ranked.append(
            {
                "search_family": family,
                "family_score": score,
                "score_components": components,
                "selection_reason": _selection_reason(
                    family=family,
                    components=components,
                    metadata=metadata,
                ),
                **metadata,
            }
        )
    ranked.sort(key=lambda row: (-int(row.get("family_score", 0) or 0), text(row.get("search_family"))))
    for index, row in enumerate(ranked, start=1):
        row["family_rank"] = index
    return ranked


def build_next_best_search_register(
    *,
    discovery_need_register: list[dict[str, Any]],
    discovery_stop_condition_register: list[dict[str, Any]],
    search_budget_register: list[dict[str, Any]],
    dynamic_case_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    stop_by_need = {
        text(row.get("need_id")): row
        for row in list(discovery_stop_condition_register or [])
        if text(row.get("need_id"))
    }
    budget_state = _remaining_budget_state(search_budget_register)
    dynamic_case_state = _as_dict(dynamic_case_state)
    ranked: list[dict[str, Any]] = []

    for need in list(discovery_need_register or []):
        need_id = text(need.get("need_id"))
        stop_row = stop_by_need.get(need_id, {})
        search_families = list(need.get("search_families_to_explore", []) or [])
        accepted_types = list(need.get("accepted_evidence_types", []) or [])
        score = _priority_score(need, budget_state)
        family_rank_register = _build_family_rank_register(
            need={
                **dict(need),
                "search_family_options": search_families,
            },
            budget_state=budget_state,
            dynamic_case_state=dynamic_case_state,
        )
        selected_family_row = family_rank_register[0] if family_rank_register else {}
        primary_search_family = text(selected_family_row.get("search_family"))
        selected_components = _as_dict(selected_family_row.get("score_components"))
        likelihood = _public_search_likelihood(
            search_family=primary_search_family,
            budget_state=budget_state,
            acquisition_difficulty=text(selected_family_row.get("acquisition_difficulty")) or "low",
        )
        ranked.append(
            {
                "need_id": need_id,
                "priority_score": score,
                "priority_band": text(need.get("priority")) or "medium",
                "next_search_target": text(need.get("discovery_need")),
                "why": text(need.get("why_it_exists")),
                "search_family": primary_search_family,
                "search_family_options": search_families,
                "family_rank_register": family_rank_register,
                "selected_search_family_reason": text(selected_family_row.get("selection_reason")),
                "selected_search_family_score": int(selected_family_row.get("family_score", 0) or 0),
                "family_score_components": selected_components,
                "expected_evidence": text(accepted_types[0] if accepted_types else ""),
                "expected_evidence_types": accepted_types,
                "public_source_likelihood": likelihood,
                "remaining_budget_state": budget_state,
                "if_found": (
                    f"Upgrade bounded understanding for {need_id} and unblock more specific comparison or hypothesis logic."
                    if need_id
                    else "Upgrade bounded understanding."
                ),
                "if_not_found": text(stop_row.get("escalation_condition")) or text(need.get("escalation_condition")),
                "downgrade_condition": text(stop_row.get("downgrade_condition")) or text(need.get("downgrade_condition")),
                "stop_condition": text(stop_row.get("stop_condition")) or text(need.get("stop_condition")),
                "matched_gap_types": list(need.get("matched_gap_types", []) or []),
            }
        )

    ranked.sort(key=lambda row: (-int(row.get("priority_score", 0) or 0), text(row.get("next_search_target"))))
    for idx, row in enumerate(ranked, start=1):
        row["target_rank"] = idx
    return ranked


def build_search_target_priority_register(
    *,
    next_best_search_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "need_id": text(row.get("need_id")),
            "target_rank": int(row.get("target_rank", 0) or 0),
            "priority_band": text(row.get("priority_band")),
            "priority_score": int(row.get("priority_score", 0) or 0),
            "public_source_likelihood": text(row.get("public_source_likelihood")),
            "remaining_budget_state": text(row.get("remaining_budget_state")),
        }
        for row in list(next_best_search_register or [])
    ]


def build_search_success_effect_register(
    *,
    next_best_search_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "need_id": text(row.get("need_id")),
            "next_search_target": text(row.get("next_search_target")),
            "if_found": text(row.get("if_found")),
        }
        for row in list(next_best_search_register or [])
    ]


def build_search_failure_effect_register(
    *,
    next_best_search_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "need_id": text(row.get("need_id")),
            "next_search_target": text(row.get("next_search_target")),
            "if_not_found": text(row.get("if_not_found")),
            "downgrade_condition": text(row.get("downgrade_condition")),
        }
        for row in list(next_best_search_register or [])
    ]
