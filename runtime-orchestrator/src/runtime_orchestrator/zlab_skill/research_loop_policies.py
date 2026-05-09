from __future__ import annotations

from typing import Any, Mapping


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def build_target_combination_floor_record(
    *,
    asset_context_vector: Mapping[str, Any] | None,
    source_coverage_summary: Mapping[str, Any] | None,
) -> dict[str, Any]:
    asset_vector = dict(asset_context_vector or {})
    coverage = dict(source_coverage_summary or {})
    provider_count = int(coverage.get("provider_count", 0) or 0)
    document_count = int(coverage.get("document_count", 0) or 0)
    knowledge_atom_count = int(coverage.get("knowledge_atom_count", 0) or 0)
    visible_reference_count = int(coverage.get("visible_reference_count", 0) or 0)
    asset_family = _text(asset_vector.get("asset_family")).lower() or "unknown_asset_family"
    coverage_started = any(
        count > 0
        for count in (
            provider_count,
            document_count,
            knowledge_atom_count,
            visible_reference_count,
        )
    )

    if provider_count >= 4 and document_count >= 8 and knowledge_atom_count >= 12:
        return {
            "target_combination_floor": 100,
            "policy_state": "rich_source_target",
            "bootstrap_floor_exception": False,
            "coverage_started": coverage_started,
            "policy_reason": "rich multi-source coverage justifies the 100+ latent-combination target",
            "asset_family": asset_family,
        }

    if not coverage_started:
        return {
            "target_combination_floor": 20,
            "policy_state": "bootstrap_floor_exception",
            "bootstrap_floor_exception": True,
            "coverage_started": False,
            "policy_reason": (
                "campaign has not yet produced providers, documents, visible references, "
                "or knowledge atoms, so a temporary bootstrap floor is allowed"
            ),
            "asset_family": asset_family,
        }

    return {
        "target_combination_floor": 50,
        "policy_state": "normal_target",
        "bootstrap_floor_exception": False,
        "coverage_started": True,
        "policy_reason": (
            "normal industrial/commercial runs should be driven toward the standard 50+ "
            "latent-combination target"
        ),
        "asset_family": asset_family,
    }


def determine_target_combination_floor(
    *,
    asset_context_vector: Mapping[str, Any] | None,
    source_coverage_summary: Mapping[str, Any] | None,
) -> int:
    return int(
        build_target_combination_floor_record(
            asset_context_vector=asset_context_vector,
            source_coverage_summary=source_coverage_summary,
        ).get("target_combination_floor", 50)
        or 50
    )


def evaluate_combination_pool_sufficiency(
    *,
    latent_candidate_count: int,
    target_combination_floor: int,
    coverage_strength: str,
    search_status: str,
) -> dict[str, Any]:
    normalized_coverage = _text(coverage_strength) or "empty"
    normalized_status = _text(search_status) or "unknown"
    latent_count = int(latent_candidate_count or 0)
    target_floor = max(int(target_combination_floor or 0), 0)

    if latent_count >= target_floor:
        pool_sufficiency = "meets_floor"
    elif latent_count >= max(target_floor // 2, 1):
        pool_sufficiency = "approaching_floor"
    else:
        pool_sufficiency = "below_floor"

    coverage_is_strong = normalized_coverage == "strong"
    search_is_complete = normalized_status == "complete_enough_for_review"
    can_stop = pool_sufficiency == "meets_floor" or (coverage_is_strong and search_is_complete)

    return {
        "target_combination_floor": target_floor,
        "pool_sufficiency": pool_sufficiency,
        "coverage_strength": normalized_coverage,
        "search_status": normalized_status,
        "can_stop": can_stop,
    }


def build_research_depth_enforcement_record(
    *,
    research_loop_metrics: Mapping[str, Any] | None,
    source_coverage_summary: Mapping[str, Any] | None,
    source_family_coverage_register: list[dict[str, Any]] | None,
    combination_search_gap_record: Mapping[str, Any] | None,
    asset_context_vector: Mapping[str, Any] | None,
) -> dict[str, Any]:
    metrics = dict(research_loop_metrics or {})
    coverage = dict(source_coverage_summary or {})
    gap = dict(combination_search_gap_record or {})
    asset_vector = dict(asset_context_vector or {})
    coverage_rows = [dict(row) for row in list(source_family_coverage_register or [])]

    floor_record = build_target_combination_floor_record(
        asset_context_vector=asset_vector,
        source_coverage_summary=coverage,
    )
    target_floor = int(floor_record.get("target_combination_floor", 50) or 50)
    sufficiency = evaluate_combination_pool_sufficiency(
        latent_candidate_count=int(metrics.get("latent_candidate_count", 0) or 0),
        target_combination_floor=target_floor,
        coverage_strength=_text(coverage.get("coverage_strength")),
        search_status=_text(gap.get("search_status")),
    )

    available_rows = [
        row for row in coverage_rows if _text(row.get("coverage_state")) != "not_available"
    ]
    strong_rows = [
        row for row in available_rows if _text(row.get("coverage_state")) == "strong"
    ]
    touched_rows = [
        row for row in available_rows if _text(row.get("coverage_state")) in {"thin", "strong"}
    ]
    high_priority_rows = [
        row for row in available_rows if _text(row.get("importance")) == "high"
    ]
    strong_high_priority_rows = [
        row for row in high_priority_rows if _text(row.get("coverage_state")) == "strong"
    ]
    touched_high_priority_rows = [
        row for row in high_priority_rows if _text(row.get("coverage_state")) in {"thin", "strong"}
    ]

    if target_floor >= 100:
        minimum_strong_source_family_count = 3
    elif target_floor >= 50:
        minimum_strong_source_family_count = 2
    else:
        minimum_strong_source_family_count = 1
    minimum_strong_source_family_count = min(
        minimum_strong_source_family_count,
        max(len(available_rows), 1),
    )
    minimum_touched_high_priority_count = min(
        2 if target_floor >= 50 else 1,
        len(high_priority_rows),
    )

    source_depth_met = len(strong_rows) >= minimum_strong_source_family_count
    high_priority_depth_met = (
        not high_priority_rows
        or (
            len(touched_high_priority_rows) >= minimum_touched_high_priority_count
            and len(strong_high_priority_rows) >= 1
        )
    )
    raw_coverage_strong = _text(coverage.get("coverage_strength")) == "strong"
    saturation_proof_strong = (
        raw_coverage_strong
        and source_depth_met
        and high_priority_depth_met
        and _text(gap.get("search_status")) in {"thin_but_reviewable", "complete_enough_for_review"}
    )

    weak_high_priority_families = [
        _text(row.get("display_name")) or _text(row.get("source_family"))
        for row in high_priority_rows
        if _text(row.get("coverage_state")) != "strong"
    ]
    weak_source_families = [
        _text(row.get("display_name")) or _text(row.get("source_family"))
        for row in available_rows
        if _text(row.get("coverage_state")) != "strong"
    ]
    required_next_source_families = []
    for item in weak_high_priority_families + weak_source_families:
        label = _text(item)
        if label and label not in required_next_source_families:
            required_next_source_families.append(label)

    policy_reasons: list[str] = []
    if _text(sufficiency.get("pool_sufficiency")) == "below_floor":
        policy_reasons.append("latent combination floor is still below the policy threshold")
    elif _text(sufficiency.get("pool_sufficiency")) == "approaching_floor" and not saturation_proof_strong:
        policy_reasons.append("latent pool is still below target and saturation proof is not strong enough yet")
    if not source_depth_met:
        policy_reasons.append("source-family depth is still too shallow for the target floor")
    if not high_priority_depth_met:
        policy_reasons.append("high-priority source families still lack strong coverage")
    if _text(gap.get("search_status")) == "incomplete_under_investigated":
        policy_reasons.append("combination search gap still marks the run as under-investigated")

    if _text(sufficiency.get("pool_sufficiency")) == "below_floor":
        depth_state = "under_floor"
    elif not high_priority_depth_met:
        depth_state = "high_priority_depth_missing"
    elif not source_depth_met:
        depth_state = "source_depth_missing"
    elif _text(sufficiency.get("pool_sufficiency")) == "approaching_floor":
        depth_state = "thin_but_reviewable"
    else:
        depth_state = "depth_satisfied"

    return {
        "asset_family": _text(asset_vector.get("asset_family")) or "unknown_asset_family",
        "target_combination_floor": target_floor,
        "target_floor_policy_state": _text(floor_record.get("policy_state")) or "normal_target",
        "bootstrap_floor_exception": bool(floor_record.get("bootstrap_floor_exception")),
        "target_floor_policy_reason": _text(floor_record.get("policy_reason")),
        "coverage_started": bool(floor_record.get("coverage_started")),
        "pool_sufficiency": _text(sufficiency.get("pool_sufficiency")),
        "depth_state": depth_state,
        "must_continue_research": bool(policy_reasons),
        "saturation_proof_strong": saturation_proof_strong,
        "strong_source_family_count": len(strong_rows),
        "available_source_family_count": len(available_rows),
        "minimum_strong_source_family_count": minimum_strong_source_family_count,
        "high_priority_source_family_count": len(high_priority_rows),
        "strong_high_priority_source_family_count": len(strong_high_priority_rows),
        "touched_high_priority_source_family_count": len(touched_high_priority_rows),
        "minimum_touched_high_priority_count": minimum_touched_high_priority_count,
        "required_next_source_families": required_next_source_families,
        "policy_reasons": policy_reasons,
        "summary": (
            f"{_text(asset_vector.get('asset_family')) or 'asset'} depth gate: "
            f"latent floor {int(metrics.get('latent_candidate_count', 0) or 0)}/{target_floor}, "
            f"strong source families {len(strong_rows)}/{minimum_strong_source_family_count}, "
            f"high-priority strong {len(strong_high_priority_rows)}/{max(len(high_priority_rows), 1) if high_priority_rows else 0}."
        ),
    }
