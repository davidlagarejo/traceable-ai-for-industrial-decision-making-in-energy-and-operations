from __future__ import annotations

from typing import Any

from .schemas import text


def _first(register: list[dict[str, Any]]) -> dict[str, Any]:
    return dict(register[0] if register else {})


def _list_text(value: Any) -> list[str]:
    if isinstance(value, list):
        return [text(item) for item in value if text(item)]
    single = text(value)
    return [single] if single else []


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        normalized = text(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


def _overlap(left: list[str], right: list[str]) -> bool:
    return bool(set(_dedupe(left)).intersection(_dedupe(right)))


def _find_matching_action(
    *,
    expanded_tad_action_register: list[dict[str, Any]],
    evidence_needed: list[str],
    strategic_hint: str,
) -> dict[str, Any]:
    hint = text(strategic_hint).lower()
    for row in list(expanded_tad_action_register or []):
        row_evidence = _list_text(row.get("evidence_needed"))
        if evidence_needed and _overlap(evidence_needed, row_evidence):
            return dict(row)
        action = text(row.get("strategic_action")).lower()
        trigger = text(row.get("trigger")).lower()
        why = text(row.get("why")).lower()
        if hint and any(token in f"{action} {trigger} {why}" for token in hint.split() if len(token) > 4):
            return dict(row)
    return {}


def _find_matching_pattern(
    *,
    activated_pattern_register: list[dict[str, Any]],
    candidate_text: str,
    evidence_needed: list[str],
) -> dict[str, Any]:
    candidate = text(candidate_text).lower()
    for row in list(activated_pattern_register or []):
        pattern = text(row.get("pattern_name")).lower()
        confirms = " ".join(_list_text(row.get("what_confirms"))).lower()
        if evidence_needed and _overlap(evidence_needed, _list_text(row.get("what_confirms"))):
            return dict(row)
        if any(token in f"{pattern} {confirms}" for token in candidate.split() if len(token) > 5):
            return dict(row)
    return {}


def _find_matching_exposure(
    *,
    financial_exposure_type_register: list[dict[str, Any]],
    candidate_text: str,
    evidence_needed: list[str],
) -> dict[str, Any]:
    candidate = text(candidate_text).lower()
    for row in list(financial_exposure_type_register or []):
        exposure_type = text(row.get("financial_exposure_type")).lower()
        why = text(row.get("why_it_matters")).lower()
        if evidence_needed and _overlap(evidence_needed, _list_text(row.get("evidence_needed"))):
            return dict(row)
        if any(token in f"{exposure_type} {why}" for token in candidate.split() if len(token) > 5):
            return dict(row)
    return {}


def _comparison_failure_text(
    *,
    comparison_not_yet_valid_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
) -> str:
    comparison_row = _first(comparison_not_yet_valid_register)
    if comparison_row:
        return text(comparison_row.get("explanation"))
    invalid_row = _first(invalid_comparison_risk_register)
    if invalid_row:
        return text(invalid_row.get("trigger"))
    return ""


def _nugget(
    *,
    nugget_id: str,
    gold_nugget: str,
    why_it_matters: str,
    evidence_state: str,
    what_to_do_next: str,
    minimum_evidence: list[str],
    contradiction: str = "",
    linked_dependency: str = "",
    linked_loss_pattern: str = "",
    linked_financial_exposure: str = "",
    linked_comparison_failure: str = "",
    tad_action: str = "",
) -> dict[str, Any]:
    return {
        "nugget_id": text(nugget_id),
        "gold_nugget": text(gold_nugget),
        "why_it_matters": text(why_it_matters),
        "why_it_surprises": text(why_it_matters),
        "evidence_state": text(evidence_state) or "CONDITIONAL_HYPOTHESIS",
        "what_to_do_next": text(what_to_do_next),
        "minimum_evidence": _dedupe(list(minimum_evidence or [])),
        "contradiction": text(contradiction),
        "linked_dependency": text(linked_dependency) or ", ".join(_dedupe(list(minimum_evidence or []))),
        "linked_loss_pattern": text(linked_loss_pattern),
        "linked_financial_exposure": text(linked_financial_exposure),
        "linked_comparison_failure": text(linked_comparison_failure),
        "tad_action": text(tad_action),
    }


def _candidate_nuggets(
    *,
    gold_nugget_candidate_register: list[dict[str, Any]],
    activated_pattern_register: list[dict[str, Any]],
    financial_exposure_type_register: list[dict[str, Any]],
    comparison_not_yet_valid_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    expanded_tad_action_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    comparison_failure = _comparison_failure_text(
        comparison_not_yet_valid_register=comparison_not_yet_valid_register,
        invalid_comparison_risk_register=invalid_comparison_risk_register,
    )
    for row in list(gold_nugget_candidate_register or []):
        candidate = text(row.get("gold_nugget_candidate"))
        if not candidate:
            continue
        evidence_needed = _list_text(row.get("evidence_needed"))
        action_row = _find_matching_action(
            expanded_tad_action_register=expanded_tad_action_register,
            evidence_needed=evidence_needed,
            strategic_hint=candidate,
        )
        pattern_row = _find_matching_pattern(
            activated_pattern_register=activated_pattern_register,
            candidate_text=candidate,
            evidence_needed=evidence_needed,
        )
        exposure_row = _find_matching_exposure(
            financial_exposure_type_register=financial_exposure_type_register,
            candidate_text=candidate,
            evidence_needed=evidence_needed,
        )
        correlation_id = text(row.get("correlation_id")) or f"corr_{len(rows) + 1:02d}"
        rows.append(
            _nugget(
                nugget_id=f"candidate_{correlation_id}",
                gold_nugget=candidate,
                why_it_matters=text(row.get("why_it_matters")),
                evidence_state=text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                what_to_do_next=text(action_row.get("why")) or text(action_row.get("prohibited_action")),
                minimum_evidence=evidence_needed,
                contradiction=comparison_failure,
                linked_dependency=", ".join(evidence_needed),
                linked_loss_pattern=text(pattern_row.get("pattern_name")),
                linked_financial_exposure=text(exposure_row.get("financial_exposure_type")),
                linked_comparison_failure=comparison_failure,
                tad_action=text(action_row.get("strategic_action")),
            )
        )
    return rows


def _priority_key(row: dict[str, Any]) -> tuple[int, int, str]:
    gold_nugget = text(row.get("gold_nugget")).lower()
    priority = 50
    if "wrong denominator" in gold_nugget or "measured with the wrong denominator" in gold_nugget:
        priority = 0
    elif "tariff design problem" in gold_nugget or "peak demand" in gold_nugget:
        priority = 1
    elif "logistics interface" in gold_nugget or "conditioned air" in gold_nugget:
        priority = 2
    elif "leak across the boundary" in gold_nugget or "control boundary" in gold_nugget:
        priority = 3
    elif "changes the asset family" in gold_nugget:
        priority = 4
    return (
        priority,
        -len(_list_text(row.get("minimum_evidence"))),
        text(row.get("nugget_id")),
    )


def build_strategic_gold_nugget_register(  # noqa: PLR0913
    *,
    asset_family_research_profile: dict[str, Any],
    invalid_problem_frame_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    measurement_strategy_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
    maintenance_reality_register: list[dict[str, Any]],
    gold_nugget_candidate_register: list[dict[str, Any]] | None = None,
    activated_pattern_register: list[dict[str, Any]] | None = None,
    financial_exposure_type_register: list[dict[str, Any]] | None = None,
    comparison_not_yet_valid_register: list[dict[str, Any]] | None = None,
    expanded_tad_action_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    gold_nugget_candidate_register = list(gold_nugget_candidate_register or [])
    activated_pattern_register = list(activated_pattern_register or [])
    financial_exposure_type_register = list(financial_exposure_type_register or [])
    comparison_not_yet_valid_register = list(comparison_not_yet_valid_register or [])
    expanded_tad_action_register = list(expanded_tad_action_register or [])

    nuggets: list[dict[str, Any]] = []
    comparison_failure = _comparison_failure_text(
        comparison_not_yet_valid_register=comparison_not_yet_valid_register,
        invalid_comparison_risk_register=invalid_comparison_risk_register,
    )

    invalid_problem = _first(invalid_problem_frame_register)
    if invalid_problem:
        evidence_needed = _list_text(invalid_problem.get("evidence_needed"))
        action_row = _find_matching_action(
            expanded_tad_action_register=expanded_tad_action_register,
            evidence_needed=evidence_needed,
            strategic_hint=text(invalid_problem.get("what_problem_should_be_tested_instead")),
        )
        nuggets.append(
            _nugget(
                nugget_id="wrong_problem_frame",
                gold_nugget=f"The visible question may be premature: {text(invalid_problem.get('apparent_problem')).replace('_', ' ')}.",
                why_it_matters="The case can fund the wrong investigation if the visible symptom is treated as the real economic driver too early.",
                evidence_state=text(invalid_problem.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                what_to_do_next=text(action_row.get("why")) or text(action_row.get("prohibited_action")),
                minimum_evidence=evidence_needed,
                contradiction=text(invalid_problem.get("why_invalid_or_premature")),
                linked_dependency=text(invalid_problem.get("what_problem_should_be_tested_instead")),
                linked_comparison_failure=comparison_failure,
                tad_action=text(action_row.get("strategic_action")),
            )
        )

    nuggets.extend(
        _candidate_nuggets(
            gold_nugget_candidate_register=gold_nugget_candidate_register,
            activated_pattern_register=activated_pattern_register,
            financial_exposure_type_register=financial_exposure_type_register,
            comparison_not_yet_valid_register=comparison_not_yet_valid_register,
            invalid_comparison_risk_register=invalid_comparison_risk_register,
            expanded_tad_action_register=expanded_tad_action_register,
        )
    )

    finance_dependency = _first(finance_physics_dependency_register)
    if finance_dependency:
        action_row = _find_matching_action(
            expanded_tad_action_register=expanded_tad_action_register,
            evidence_needed=_list_text(finance_dependency.get("evidence_needed")),
            strategic_hint=text(finance_dependency.get("risk_if_wrong")),
        )
        nuggets.append(
            _nugget(
                nugget_id="wrong_capital_target",
                gold_nugget="The capital target may be wrong even if the technical symptom is real.",
                why_it_matters="Physical truth and value capture can separate when the controllable boundary or cost driver is still unbounded.",
                evidence_state=text(finance_dependency.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                what_to_do_next=text(action_row.get("why")) or text(action_row.get("prohibited_action")),
                minimum_evidence=_list_text(finance_dependency.get("evidence_needed")),
                contradiction=comparison_failure,
                linked_dependency=text(finance_dependency.get("physical_dependency")),
                linked_financial_exposure=text(_find_matching_exposure(
                    financial_exposure_type_register=financial_exposure_type_register,
                    candidate_text=text(finance_dependency.get("risk_if_wrong")),
                    evidence_needed=_list_text(finance_dependency.get("evidence_needed")),
                ).get("financial_exposure_type")),
                linked_comparison_failure=comparison_failure,
                tad_action=text(action_row.get("strategic_action")),
            )
        )

    measurement_row = _first(measurement_strategy_register)
    if measurement_row:
        action_row = _find_matching_action(
            expanded_tad_action_register=expanded_tad_action_register,
            evidence_needed=[text(measurement_row.get("minimum_measurement"))],
            strategic_hint=text(measurement_row.get("why")),
        )
        nuggets.append(
            _nugget(
                nugget_id="wrong_measurement_instinct",
                gold_nugget="The next best measurement may be a bill, map or log, not a new sensor.",
                why_it_matters="Measurement cost and speed can improve when the evidence path follows the dominant hypothesis instead of hardware reflex.",
                evidence_state="ARCHETYPAL_PRIOR",
                what_to_do_next=text(action_row.get("why")) or text(action_row.get("prohibited_action")),
                minimum_evidence=[text(measurement_row.get("minimum_measurement"))],
                linked_dependency=text(measurement_row.get("minimum_measurement")),
                tad_action=text(action_row.get("strategic_action")),
            )
        )

    if any("downtime economics" in text(row.get("reality_claim")).lower() for row in maintenance_reality_register):
        maintenance_row = next(
            row for row in maintenance_reality_register
            if "downtime economics" in text(row.get("reality_claim")).lower()
        )
        action_row = _find_matching_action(
            expanded_tad_action_register=expanded_tad_action_register,
            evidence_needed=["maintenance logs", "downtime records", "preventive maintenance proof"],
            strategic_hint=text(maintenance_row.get("why_it_matters")),
        )
        nuggets.append(
            _nugget(
                nugget_id="wrong_loss_story",
                gold_nugget="The visible energy story may be secondary to uptime or maintenance economics.",
                why_it_matters="An asset can look utility-inefficient while the real economic problem is reliability, execution or avoidable downtime.",
                evidence_state="CONDITIONAL_HYPOTHESIS",
                what_to_do_next=text(action_row.get("why")) or text(action_row.get("prohibited_action")),
                minimum_evidence=["maintenance logs", "downtime records", "preventive maintenance proof"],
                linked_dependency="maintenance and downtime evidence",
                linked_loss_pattern=text(_find_matching_pattern(
                    activated_pattern_register=activated_pattern_register,
                    candidate_text=text(maintenance_row.get("reality_claim")),
                    evidence_needed=["maintenance logs", "downtime records", "preventive maintenance proof"],
                ).get("pattern_name")),
                linked_financial_exposure=text(_find_matching_exposure(
                    financial_exposure_type_register=financial_exposure_type_register,
                    candidate_text="maintenance downtime exposure",
                    evidence_needed=["maintenance logs", "downtime records", "preventive maintenance proof"],
                ).get("financial_exposure_type")),
                tad_action=text(action_row.get("strategic_action")),
            )
        )

    deduped: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()
    for row in sorted(nuggets, key=_priority_key):
        nugget_id = text(row.get("nugget_id"))
        nugget_text = text(row.get("gold_nugget"))
        if not nugget_id or not nugget_text or nugget_id in seen_ids or nugget_text in seen_texts:
            continue
        seen_ids.add(nugget_id)
        seen_texts.add(nugget_text)
        deduped.append(row)
    return deduped[:5]


def build_gold_nugget_strength_register(
    *,
    gold_nugget_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(gold_nugget_register or []):
        score = 1
        if text(row.get("linked_comparison_failure")):
            score += 1
        if text(row.get("linked_loss_pattern")):
            score += 1
        if text(row.get("linked_financial_exposure")):
            score += 1
        if _list_text(row.get("minimum_evidence")):
            score += 1
        if text(row.get("what_to_do_next")):
            score += 1
        rows.append(
            {
                "nugget_id": text(row.get("nugget_id")),
                "strength_score": score,
                "strength_label": (
                    "strong"
                    if score >= 5
                    else "bounded"
                    if score >= 3
                    else "weak"
                ),
                "evidence_state": text(row.get("evidence_state")),
                "what_to_do_next": text(row.get("what_to_do_next")),
            }
        )
    return rows
