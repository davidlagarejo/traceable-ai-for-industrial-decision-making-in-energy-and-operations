from __future__ import annotations

import re
from typing import Any

from .output_taxonomy import canonicalize_output_mode

_TAD_STATUS_PRIORITY = {
    "ACT NOW": 0,
    "VALIDATE FIRST": 1,
    "COMPARE TO PEERS": 2,
    "REDESIGN HYPOTHESIS": 3,
    "INVESTIGATE": 4,
    "DEFER": 5,
    "NO-GO": 6,
    "DO NOT MODEL YET": 7,
}

_STRUCTURAL_CLASSIFICATION_STATES = {
    "selected_primary_structural",
    "active_secondary_structural",
    "eligible_primary_structural",
}

_TOKEN_STOPWORDS = {
    "and",
    "the",
    "with",
    "from",
    "into",
    "this",
    "that",
    "what",
    "when",
    "where",
    "while",
    "under",
    "over",
    "before",
    "after",
    "against",
    "between",
    "rather",
    "than",
    "does",
    "doesnt",
    "not",
    "yet",
    "can",
    "may",
    "remain",
    "remains",
    "wrong",
    "because",
    "being",
    "have",
    "has",
    "will",
    "until",
    "current",
    "main",
    "problem",
    "need",
    "needs",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _list_text(values: Any) -> list[str]:
    if isinstance(values, list):
        return [str(value).strip() for value in values if str(value).strip()]
    text = _text(values)
    return [text] if text else []


def _split_compound_evidence(value: Any) -> list[str]:
    text = _text(value)
    if not text:
        return []
    if " + " in text:
        return [item.strip() for item in text.split(" + ") if item.strip()]
    return [text]


def _format_label(value: Any) -> str:
    text = _text(value).replace("_", " ")
    return " ".join(text.split())


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = _text(value)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _join_sentences(*parts: Any) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for part in parts:
        text = _text(part)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return " ".join(out)


def _tokens(*values: Any) -> set[str]:
    merged = " ".join(_text(value).lower() for value in values if _text(value))
    raw_tokens = re.findall(r"[a-z0-9]+", merged)
    return {
        token
        for token in raw_tokens
        if len(token) >= 3 and token not in _TOKEN_STOPWORDS
    }


def _overlap_score(*groups: Any) -> int:
    token_sets = [_tokens(group) for group in groups if _tokens(group)]
    if len(token_sets) < 2:
        return 0
    base = token_sets[0]
    score = 0
    for candidate in token_sets[1:]:
        score += len(base.intersection(candidate))
    return score


def _selected_output_mode(report_output_mode_classifier_table: list[dict[str, Any]]) -> str:
    for row in report_output_mode_classifier_table:
        if bool(row.get("selected_for_publication", False)):
            return canonicalize_output_mode(
                row.get("canonical_output_mode")
                or row.get("visible_output_mode")
                or row.get("recommended_output_mode")
                or ""
            )
    for row in report_output_mode_classifier_table:
        state = _text(row.get("classification_state"))
        if state.startswith("selected_"):
            return canonicalize_output_mode(
                row.get("canonical_output_mode")
                or row.get("visible_output_mode")
                or row.get("recommended_output_mode")
                or ""
            )
    return ""


def _supporting_modes(
    report_output_mode_classifier_table: list[dict[str, Any]],
    selected_mode: str,
) -> list[str]:
    supporting: list[str] = []
    for row in report_output_mode_classifier_table:
        mode = canonicalize_output_mode(
            row.get("canonical_output_mode")
            or row.get("visible_output_mode")
            or row.get("recommended_output_mode")
            or ""
        )
        if not mode or mode == selected_mode:
            continue
        state = _text(row.get("classification_state"))
        if state in _STRUCTURAL_CLASSIFICATION_STATES:
            supporting.append(mode)
    return _dedupe(supporting)


def _top_dominant_variables(dominant_variable_register: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in dominant_variable_register:
        evidence_state = _text(row.get("evidence_state"))
        variable = _text(row.get("variable"))
        if not variable or evidence_state not in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS"}:
            continue
        rows.append(
            {
                "variable": variable,
                "layer": _text(row.get("layer")),
                "evidence_state": evidence_state,
                "why_it_could_matter": _text(row.get("why_it_could_matter")),
                "decision_impact": _text(row.get("decision_impact")),
            }
        )
        if len(rows) >= 3:
            break
    return rows


def _translated_congruence_conflict_register(
    cross_layer_congruence_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in cross_layer_congruence_register:
        conflict = _text(row.get("contradiction"))
        if not conflict:
            continue
        rows.append(
            {
                "conflict": conflict,
                "layers_involved": _list_text(row.get("layers")),
                "why_it_matters": _text(row.get("strategic_risk")),
                "potential_redesign_direction": _text(row.get("possible_redesign")),
                "evidence_state": _text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
            }
        )
    return rows


def _effective_primary_problem(
    problem_framing_register: list[dict[str, Any]],
    invalid_problem_frame_register: list[dict[str, Any]],
) -> dict[str, Any]:
    primary = dict(problem_framing_register[0] if problem_framing_register else {})
    if primary and _text(primary.get("evidence_state")).upper() != "INADMISSIBLE_CLAIM":
        return primary
    invalid = dict(invalid_problem_frame_register[0] if invalid_problem_frame_register else {})
    if not invalid:
        return primary
    return {
        "stated_problem": _format_label(invalid.get("apparent_problem")),
        "reframed_problem": _text(invalid.get("what_problem_should_be_tested_instead")),
        "why_original_framing_may_be_wrong": _text(invalid.get("why_invalid_or_premature")),
        "evidence_needed": list(invalid.get("evidence_needed", []) or []),
        "strategic_risk": _text(invalid.get("why_invalid_or_premature")),
        "evidence_state": _text(invalid.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
    }


def _subject_family(
    *,
    system_abstraction: dict[str, Any],
    canonical_problem_frame: dict[str, Any],
    cross_layer_conflict_register: list[dict[str, Any]],
) -> str:
    asset_type_text = " ".join(
        [
            _text((system_abstraction.get("asset_type", {}) or {}).get("statement")),
            _text((system_abstraction.get("dominant_process_type", {}) or {}).get("statement")),
            _text(canonical_problem_frame.get("reframed_problem")),
            " ".join(_text(row.get("conflict")) for row in cross_layer_conflict_register),
        ]
    ).lower()
    if any(token in asset_type_text for token in ("utility_heavy", "utility heavy", "power factor", "reactive", "pf charge", "utility island")):
        return "utility_heavy"
    if any(token in asset_type_text for token in ("manufacturing", "process", "throughput", "thermal", "curing", "scrap", "downtime")):
        return "manufacturing"
    if any(token in asset_type_text for token in ("infrastructure", "substation", "continuity", "dispatch", "redundancy", "switching", "feeder")):
        return "infrastructure"
    if any(token in asset_type_text for token in ("building", "office", "tower", "tenant", "ll97", "central plant", "bms", "lease")):
        return "building"
    return "generic"


def _financial_rows(
    structural_financial_exposure_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return list(structural_financial_exposure_register or [])


def _ranked_conflict_register(
    *,
    canonical_problem_frame: dict[str, Any],
    cross_layer_conflict_register: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    expanded_structural_tad_action_register: list[dict[str, Any]],
    claim_contract_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    canonical_conflict = _text(canonical_problem_frame.get("dominant_conflict"))
    minimum_row = minimum_evidence_for_discrimination_register[0] if minimum_evidence_for_discrimination_register else {}
    minimum_text = " ".join(
        [
            _text(minimum_row.get("minimum_evidence")),
            _text(minimum_row.get("what_it_confirms")),
            _text(minimum_row.get("what_it_falsifies")),
            _text(minimum_row.get("unlocks")),
        ]
    )
    tad_rows = _sorted_tad_actions(expanded_structural_tad_action_register)
    prohibited_claim_text = " ".join(
        _text(row.get("statement")) or _text(row.get("claim_id"))
        for row in claim_contract_register
        if _text(row.get("permission")).lower() == "prohibited"
    )
    ranked: list[dict[str, Any]] = []
    for row in list(cross_layer_conflict_register or []):
        conflict = _text(row.get("conflict"))
        if not conflict:
            continue
        layers = _list_text(row.get("layers_involved"))
        conflict_text = " ".join(
            [
                conflict,
                " ".join(layers),
                _text(row.get("why_it_matters")),
                _text(row.get("potential_redesign_direction")),
            ]
        )
        economic_score = 0
        for fin_row in _financial_rows(structural_financial_exposure_register):
            financial_text = " ".join(
                [
                    _text(fin_row.get("structural_assumption")),
                    _text(fin_row.get("financial_exposure_if_wrong")),
                    " ".join(_list_text(fin_row.get("evidence_needed"))),
                ]
            )
            economic_score = max(economic_score, _overlap_score(conflict_text, financial_text))
        decision_score = 0
        for idx, tad_row in enumerate(tad_rows[:5]):
            action_text = " ".join(
                [
                    _text(tad_row.get("action")),
                    _text(tad_row.get("why")),
                    _text(tad_row.get("evidence_needed")),
                    _text(tad_row.get("financial_exposure")),
                ]
            )
            overlap = _overlap_score(conflict_text, action_text)
            if overlap:
                decision_score = max(decision_score, max(1, 5 - idx) + overlap)
        evidence_score = _overlap_score(conflict_text, minimum_text)
        claim_score = _overlap_score(conflict_text, prohibited_claim_text)
        breadth_score = len(layers)
        canonical_bonus = 5 if canonical_conflict and conflict == canonical_conflict else 0
        total_score = (
            economic_score * 5
            + decision_score * 4
            + evidence_score * 3
            + breadth_score * 2
            + claim_score
            + canonical_bonus
        )
        ranked.append(
            {
                **row,
                "economic_exposure_score": economic_score,
                "decision_blocking_score": decision_score,
                "evidence_discrimination_score": evidence_score,
                "cross_layer_breadth_score": breadth_score,
                "claim_permission_consequence_score": claim_score,
                "canonical_problem_frame_bonus": canonical_bonus,
                "total_rank_score": total_score,
                "selection_basis": {
                    "economic_exposure_score": economic_score,
                    "decision_blocking_score": decision_score,
                    "evidence_discrimination_score": evidence_score,
                    "cross_layer_breadth_score": breadth_score,
                    "claim_permission_consequence_score": claim_score,
                    "canonical_problem_frame_bonus": canonical_bonus,
                    "total_rank_score": total_score,
                },
            }
        )
    return sorted(
        ranked,
        key=lambda row: (
            -int(row.get("total_rank_score", 0) or 0),
            -int(row.get("economic_exposure_score", 0) or 0),
            _text(row.get("conflict")),
        ),
    )


def _top_scenarios(scenario_register: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in scenario_register:
        title = (
            _text(row.get("scenario"))
            or _text(row.get("scenario_name"))
            or _text(row.get("headline"))
            or _text(row.get("label"))
            or _text(row.get("name"))
        )
        if not title:
            continue
        rows.append(
            {
                "scenario": title,
                "financial_meaning": _text(row.get("financial_meaning"))
                or _text(row.get("decision_impact"))
                or _text(row.get("why_it_matters")),
                "evidence_needed": _text(row.get("evidence_needed"))
                or _text(row.get("evidence_link"))
                or _text(row.get("evidence_state")),
                "falsification_condition": _text(row.get("falsification_condition"))
                or _text(row.get("falsifies_it")),
            }
        )
        if len(rows) >= 3:
            break
    return rows


def _sorted_tad_actions(expanded_structural_tad_action_register: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        list(expanded_structural_tad_action_register or []),
        key=lambda row: (
            _TAD_STATUS_PRIORITY.get(_text(row.get("status")), 99),
            _text(row.get("action")),
        ),
    )


def _client_facing_tad_actions(
    expanded_structural_tad_action_register: list[dict[str, Any]],
    dominant_contradiction: str,
    minimum_discriminating_evidence: list[str],
    congruence_action_priority_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    contradiction_map = dominant_contradiction or "dominant_contradiction"
    evidence_map = "; ".join(minimum_discriminating_evidence) or "evidence_discriminator"
    rows: list[dict[str, Any]] = []
    for row in _sorted_tad_actions(expanded_structural_tad_action_register):
        action = _text(row.get("action"))
        if not action:
            continue
        maps_to = contradiction_map if _text(row.get("linked_claim")) != "TAD_action_claim" else evidence_map
        rows.append(
            {
                "action": action,
                "status": _text(row.get("status")),
                "why": _text(row.get("why")),
                "evidence_state": _text(row.get("evidence_state")),
                "financial_exposure": _text(row.get("financial_exposure")),
                "evidence_needed": _text(row.get("evidence_needed")),
                "prohibited_action": _text(row.get("prohibited_action")),
                "linked_claim": _text(row.get("linked_claim")),
                "maps_to": maps_to,
            }
        )
        if len(rows) >= 3:
            break
    if rows:
        return rows
    for row in list(congruence_action_priority_register or [])[:3]:
        action = _format_label(row.get("strategic_action")).title()
        if not action:
            continue
        rows.append(
            {
                "action": action,
                "status": _text(row.get("status")),
                "why": _text(row.get("why")) or _text(row.get("gold_nugget")),
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": "",
                "evidence_needed": "; ".join(_list_text(row.get("evidence_needed"))),
                "prohibited_action": _text(row.get("prohibited_action")),
                "linked_claim": "congruence_action_claim",
                "maps_to": contradiction_map if _text(row.get("strategic_action")) != "REQUEST_MINIMUM_EVIDENCE" else evidence_map,
            }
        )
    return rows


def _primary_redesign(conditional_redesign_register: list[dict[str, Any]]) -> dict[str, Any]:
    row = conditional_redesign_register[0] if conditional_redesign_register else {}
    return {
        "hypothesis": _text(row.get("hypothesis")),
        "trigger_hypothesis": _text(row.get("trigger_hypothesis")) or _text(row.get("hypothesis")),
        "evidence_state": _text(row.get("evidence_state")),
        "conflict_resolved": _text(row.get("conflict_resolved")),
        "economic_logic": _text(row.get("economic_logic")),
        "if_confirmed": _text(row.get("if_confirmed")),
        "redesign_direction": _text(row.get("redesign_direction")),
        "if_falsified": _text(row.get("if_falsified")),
        "evidence_needed": _list_text(row.get("evidence_needed")) or _list_text(row.get("next_evidence")),
        "kill_condition": _text(row.get("kill_condition")) or _text(row.get("if_falsified")),
        "next_evidence": _list_text(row.get("next_evidence")),
    }


def _primary_financial_exposure(structural_financial_exposure_register: list[dict[str, Any]]) -> dict[str, Any]:
    row = structural_financial_exposure_register[0] if structural_financial_exposure_register else {}
    return {
        "structural_assumption": _text(row.get("structural_assumption")),
        "evidence_state": _text(row.get("evidence_state")),
        "financial_exposure_if_wrong": _text(row.get("financial_exposure_if_wrong")),
        "evidence_needed": _list_text(row.get("evidence_needed")),
        "allowed_financial_output": _list_text(row.get("allowed_financial_output")),
        "prohibited_financial_output": _list_text(row.get("prohibited_financial_output")),
    }


def _primary_peer_comparison(competitive_comparison_register: list[dict[str, Any]]) -> dict[str, Any]:
    row = competitive_comparison_register[0] if competitive_comparison_register else {}
    return dict(row or {})


def _what_is_not_admissible(claim_contract_register: list[dict[str, Any]]) -> list[str]:
    blocked: list[str] = []
    for row in claim_contract_register:
        if _text(row.get("permission")).lower() != "prohibited":
            continue
        statement = _text(row.get("statement")) or _text(row.get("claim_id"))
        if statement:
            blocked.append(statement)
        if len(blocked) >= 5:
            break
    return _dedupe(blocked)


def _evidence_state(
    canonical_problem_frame: dict[str, Any],
    cross_layer_conflict_register: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
) -> str:
    for source in (
        cross_layer_conflict_register[0] if cross_layer_conflict_register else {},
        structural_financial_exposure_register[0] if structural_financial_exposure_register else {},
        canonical_problem_frame,
    ):
        state = _text(source.get("evidence_state"))
        if state:
            return state
    return "NOT_OBSERVED"


def _confidence_level(evidence_state: str) -> str:
    if evidence_state == "OBSERVED_FACT":
        return "high"
    if evidence_state == "CONDITIONAL_HYPOTHESIS":
        return "bounded_conditional"
    if evidence_state == "ARCHETYPAL_PRIOR":
        return "low"
    if evidence_state == "INADMISSIBLE_CLAIM":
        return "inadmissible"
    return "uncertain"


def _interpretive_signal_register(
    *,
    subject_family: str,
    dominant_contradiction: str,
    evidence_state: str,
    primary_problem: dict[str, Any],
    primary_financial: dict[str, Any],
    primary_redesign: dict[str, Any],
    primary_peer: dict[str, Any],
    minimum_discriminating_evidence: list[str],
) -> list[dict[str, str]]:
    conflict_text = dominant_contradiction.lower()
    financial_risk = _text(primary_financial.get("financial_exposure_if_wrong"))
    redesign_direction = _text(primary_redesign.get("redesign_direction"))
    kill_condition = _text(primary_redesign.get("kill_condition"))
    why_wrong = _text(primary_problem.get("why_original_framing_may_be_wrong"))
    evidence_pack = "; ".join(minimum_discriminating_evidence)
    signals: list[dict[str, str]] = []

    if "control boundary" in conflict_text or ("regulation" in conflict_text and "control" in conflict_text):
        signals.append(
            {
                "signal_type": "boundary_misalignment",
                "statement": "The cost bearer and the control holder may not be the same actor.",
                "why_non_obvious": "Public compliance visibility can make the asset look economically actionable before the load-capture boundary is actually proven.",
                "why_decision_relevant": why_wrong or "A technically valid building can still be a bad retrofit-underwriting surface if the owner does not capture the dominant savings boundary.",
                "economic_consequence": financial_risk,
                "evidence_state": evidence_state,
                "kill_condition": kill_condition or "Observed full owner control over the dominant covered loads.",
            }
        )
        signals.append(
            {
                "signal_type": "false_capex_logic",
                "statement": "Technical CAPEX can be economically premature even when the building is real, large, and regulated.",
                "why_non_obvious": "Screening-grade public evidence often gets misread as proof of owner-capturable economics.",
                "why_decision_relevant": "The real risk is not missing building identity. It is funding the wrong side of the value boundary.",
                "economic_consequence": financial_risk,
                "evidence_state": evidence_state,
                "kill_condition": kill_condition or "Owner-controlled central plant and covered loads clearly dominate realized economics.",
            }
        )
    if "benchmark" in conflict_text:
        signals.append(
            {
                "signal_type": "benchmark_false_positive",
                "statement": "Benchmark visibility is not the same thing as owner-correctable inefficiency.",
                "why_non_obvious": "Public benchmarking can feel decision-ready while still being structurally ambiguous.",
                "why_decision_relevant": "Benchmark-led CAPEX can target the wrong driver if the load truth is not yet bounded.",
                "economic_consequence": financial_risk,
                "evidence_state": evidence_state,
                "kill_condition": "Observed utility baseline and topology prove an owner-controlled waste mechanism.",
            }
        )
    if subject_family == "utility_heavy" or any(
        token in conflict_text for token in ("demand-structure", "demand structure", "reactive", "power factor", "support-system duty", "sequencing")
    ):
        signals.append(
            {
                "signal_type": "false_consumption_priority",
                "statement": "Aggregate consumption may be the wrong lead variable if demand structure, PF or support-system duty dominate the economics.",
                "why_non_obvious": "Utility-heavy sites often look like consumption problems first, even when the real boundary sits in tariff structure, sequencing or major-motor duty.",
                "why_decision_relevant": why_wrong or "Consumption-reduction CAPEX can misfire if the site is being priced and constrained by demand, PF or support-duty logic instead.",
                "economic_consequence": financial_risk or "Capital can chase kWh reduction while the actual cost driver remains demand, PF or unstable support-duty behavior.",
                "evidence_state": evidence_state,
                "kill_condition": kill_condition or "Observed tariff, interval-demand and support-duty evidence prove that broad consumption reduction is still the dominant value lever.",
            }
        )
        signals.append(
            {
                "signal_type": "tariff_front_not_root_cause",
                "statement": "PF or demand charges can be visible without proving that tariff correction is the first or only capital answer.",
                "why_non_obvious": "Billing pressure can look economically decisive before the site proves whether support-system duty or maintenance instability is what creates the tariff symptom.",
                "why_decision_relevant": "The wrong sequencing can fund tariff logic while the underlying support-system or maintenance problem remains untouched.",
                "economic_consequence": financial_risk or "The case can optimize the bill surface while leaving the real support-duty or reliability leak intact.",
                "evidence_state": evidence_state,
                "kill_condition": "Observed maintenance stability, duty profile and tariff exposure show that PF or demand correction is the first material lever.",
            }
        )
    if subject_family == "infrastructure" or any(
        token in conflict_text for token in ("continuity", "dispatch", "redundancy", "reliability obligation", "demand structure")
    ):
        signals.append(
            {
                "signal_type": "continuity_boundary_confusion",
                "statement": "Visible energy or tariff pressure may be a continuity-duty symptom, not proof of avoidable node waste.",
                "why_non_obvious": "Infrastructure nodes can look energy-heavy precisely because redundancy, dispatch posture, and service continuity are structurally expensive.",
                "why_decision_relevant": why_wrong or "Tariff or optimization logic can misfire if continuity burden and reliability posture are the real boundary conditions.",
                "economic_consequence": financial_risk or "Optimization capital can target a visible utility symptom while the real economic boundary remains continuity or constrained dispatch.",
                "evidence_state": evidence_state,
                "kill_condition": kill_condition or "Observed continuity profile, redundancy class, and dispatch logs prove that controllable support-load waste dominates the case.",
            }
        )
        signals.append(
            {
                "signal_type": "false_tariff_priority",
                "statement": "Tariff pressure can be real and still be the wrong first capital target.",
                "why_non_obvious": "Demand or PF charges often look financially actionable before the node proves that reliability posture allows tariff-aware changes.",
                "why_decision_relevant": "The wrong sequencing can optimize the bill on paper while increasing service or uptime risk in practice.",
                "economic_consequence": financial_risk or "Reliability or dispatch risk can dominate the apparent utility upside.",
                "evidence_state": evidence_state,
                "kill_condition": "Observed switching logic, redundancy policy, and maintenance reality allow tariff-aware operating changes without service degradation.",
            }
        )
    if subject_family == "manufacturing" or any(
        token in conflict_text for token in ("process load", "throughput", "thermal", "uptime", "downtime")
    ):
        signals.append(
            {
                "signal_type": "structural_vs_operational_confusion",
                "statement": "Visible intensity may be structural process load rather than operational waste.",
                "why_non_obvious": "Energy symptoms can dominate attention even when throughput, thermal duty, uptime, or scrap economics are the true driver.",
                "why_decision_relevant": "Funding utility-oriented CAPEX can miss the actual economic leak.",
                "economic_consequence": financial_risk,
                "evidence_state": evidence_state,
                "kill_condition": kill_condition or "Observed support-system waste clearly dominates the total economic loss.",
            }
        )
    peer_state = _text(primary_peer.get("evidence_state"))
    transferability = _text(primary_peer.get("transferability"))
    if peer_state and peer_state != "OBSERVED_FACT" and transferability:
        signals.append(
            {
                "signal_type": "non_transferable_peer_advantage",
                "statement": "A peer can look superior for reasons that do not automatically transfer.",
                "why_non_obvious": "Best-practice language can hide contractual, operational, or control-boundary differences.",
                "why_decision_relevant": "Copying the peer pattern before proving transferability can import the wrong solution logic.",
                "economic_consequence": "Peer-led action can misallocate attention and capital if the subject boundary differs.",
                "evidence_state": peer_state,
                "kill_condition": evidence_pack or "Observed peer comparability across the relevant boundary conditions.",
            }
        )
    return signals[:3]


def _hidden_assumption_at_risk(subject_family: str, dominant_contradiction: str) -> str:
    conflict_text = dominant_contradiction.lower()
    if "control boundary" in conflict_text:
        return "The working assumption is that the actor facing the burden also controls the loads and captures the economics that matter."
    if subject_family == "utility_heavy" or any(token in conflict_text for token in ("demand-structure", "demand structure", "reactive", "power factor", "support-system duty")):
        return "The working assumption is that visible consumption is the real problem rather than the demand, PF, sequencing or support-system duty structure that actually sets the cost boundary."
    if subject_family == "infrastructure" or any(token in conflict_text for token in ("continuity", "dispatch", "redundancy", "reliability obligation")):
        return "The working assumption is that visible energy or tariff pressure is the real problem rather than the continuity, dispatch, or redundancy duty that structurally shapes the node."
    if subject_family == "manufacturing" or any(token in conflict_text for token in ("process", "throughput", "thermal", "uptime")):
        return "The working assumption is that visible intensity is operational waste rather than structural process load or uptime economics."
    if "benchmark" in conflict_text:
        return "The working assumption is that a visible benchmark gap already proves local inefficiency."
    return "The working assumption is that the currently visible symptom is also the true decision variable."


def _why_current_question_is_premature(
    subject_family: str,
    dominant_contradiction: str,
    minimum_discriminating_evidence: list[str],
) -> str:
    evidence_pack = "; ".join(minimum_discriminating_evidence)
    conflict_text = dominant_contradiction.lower()
    if "control boundary" in conflict_text:
        return (
            "The current question is premature because retrofit or compliance capital logic is being asked before the value-capture boundary is closed. "
            f"The discriminating pack is: {evidence_pack}."
        )
    if subject_family == "utility_heavy" or any(token in conflict_text for token in ("demand-structure", "demand structure", "reactive", "power factor", "support-system duty")):
        return (
            "The current question is premature because consumption-reduction logic is being asked before the site separates demand, PF, sequencing and support-system duty from the visible utility symptom. "
            f"The discriminating pack is: {evidence_pack}."
        )
    if subject_family == "infrastructure" or any(token in conflict_text for token in ("continuity", "dispatch", "redundancy", "reliability obligation")):
        return (
            "The current question is premature because optimization logic is being asked before the node can separate structural continuity duty from controllable support-load waste. "
            f"The discriminating pack is: {evidence_pack}."
        )
    if subject_family == "manufacturing" or any(token in conflict_text for token in ("process", "throughput", "thermal", "uptime")):
        return (
            "The current question is premature because CAPEX logic is being asked before the system can distinguish structural process load from operational waste. "
            f"The discriminating pack is: {evidence_pack}."
        )
    return f"The current question is premature until the discriminating evidence pack is observed: {evidence_pack}."


def _what_reality_feature_changes_the_decision(subject_family: str, dominant_contradiction: str) -> str:
    conflict_text = dominant_contradiction.lower()
    if "control boundary" in conflict_text:
        return "Whether owner-controlled base-building systems dominate the economics, or whether tenant-driven loads and metering boundaries dominate them instead."
    if subject_family == "utility_heavy" or any(token in conflict_text for token in ("demand-structure", "demand structure", "reactive", "power factor", "support-system duty")):
        return "Whether the visible cost is being driven by controllable demand, PF, sequencing and support-system loss, or instead by structural support-duty that is economically rational at the current operating boundary."
    if subject_family == "infrastructure" or any(token in conflict_text for token in ("continuity", "dispatch", "redundancy", "reliability obligation")):
        return "Whether the visible cost is being driven by continuity duty, dispatch posture, and redundancy class, or instead by controllable support-load loss that can be optimized without harming service."
    if subject_family == "manufacturing" or any(token in conflict_text for token in ("process", "throughput", "thermal", "uptime")):
        return "Whether the dominant driver is structural process load, or instead support-system waste and maintenance discipline."
    if "benchmark" in conflict_text:
        return "Whether the visible benchmark signal reflects local waste, or merely screening visibility without local control."
    return "Which structural variable actually dominates the economics once the false front variable is removed."


def _capital_logic_if_assumption_holds(
    subject_family: str,
    primary_redesign: dict[str, Any],
    primary_financial: dict[str, Any],
) -> str:
    redesign_direction = _text(primary_redesign.get("redesign_direction"))
    if redesign_direction:
        return f"If the assumption holds, capital can be framed around {redesign_direction.lower()} after the boundary is confirmed."
    if subject_family == "utility_heavy":
        return "If the assumption holds, tariff-aware control, sequencing or targeted correction may become economically defensible before broader consumption CAPEX."
    if subject_family == "manufacturing":
        return "If the assumption holds, targeted operational or process-side intervention may become economically defensible."
    return _text(primary_financial.get("structural_assumption"))


def _capital_logic_if_assumption_breaks(
    subject_family: str,
    primary_financial: dict[str, Any],
    primary_redesign: dict[str, Any],
) -> str:
    financial_risk = _text(primary_financial.get("financial_exposure_if_wrong"))
    if financial_risk:
        return financial_risk
    if subject_family == "utility_heavy":
        return "If the assumption breaks, broad consumption CAPEX is likely to chase a secondary symptom while demand structure, support-duty or maintenance instability remains the real cost driver."
    if subject_family == "manufacturing":
        return "If the assumption breaks, utility-oriented CAPEX is likely to target a secondary symptom rather than the primary economic driver."
    return _text(primary_redesign.get("if_falsified"))


def _surprising_takeaway(
    *,
    subject_family: str,
    interpretive_signal_register: list[dict[str, str]],
    hidden_assumption_at_risk: str,
    dominant_contradiction: str,
) -> str:
    if interpretive_signal_register:
        first_signal = interpretive_signal_register[0]
        if _text(first_signal.get("signal_type")) == "boundary_misalignment":
            return "The unresolved issue is not whether the asset is visible, large, or regulated. It is a control-boundary problem: whether the actor facing the burden actually controls and captures the load economics."
        if _text(first_signal.get("signal_type")) == "false_consumption_priority":
            return "This may not be a consumption problem yet. It may be a demand-structure and support-system-duty problem: whether visible cost sits in kWh, or in PF, peaks, sequencing and major-motor behavior."
        if _text(first_signal.get("signal_type")) == "continuity_boundary_confusion":
            return "This may not be an efficiency problem yet. It may be a continuity-duty problem: whether the node is expensive because it is wasteful, or because reliability and dispatch obligations structurally shape the load."
        if _text(first_signal.get("signal_type")) == "structural_vs_operational_confusion":
            return "The most dangerous mistake may be funding energy CAPEX against a symptom that is actually structural process load or uptime economics."
    if subject_family == "utility_heavy":
        return "This may not be a consumption problem yet. It may be a demand-structure and support-system-duty problem."
    if subject_family == "infrastructure":
        return "This may not be an energy-waste problem yet. It may be a continuity and dispatch boundary problem."
    if subject_family == "manufacturing":
        return "This may not be an efficiency problem yet. It may be a process-structure problem."
    if "control boundary" in dominant_contradiction.lower():
        return "This may not be an energy problem yet. It may be a control-boundary problem."
    return hidden_assumption_at_risk


def _first_row(register: list[dict[str, Any]]) -> dict[str, Any]:
    return dict(register[0] if register else {})


def _first_nugget(
    strategic_gold_nugget_register: list[dict[str, Any]],
    nugget_id: str,
) -> dict[str, Any]:
    for row in strategic_gold_nugget_register:
        if _text(row.get("nugget_id")) == nugget_id:
            return dict(row)
    return {}


def _dominant_operational_misunderstanding(
    *,
    invalid_problem_frame_register: list[dict[str, Any]],
    strategic_gold_nugget_register: list[dict[str, Any]],
) -> str:
    nugget = _first_nugget(strategic_gold_nugget_register, "wrong_problem_frame")
    if nugget:
        return _text(nugget.get("gold_nugget"))
    first = _first_row(invalid_problem_frame_register)
    apparent_problem = _text(first.get("apparent_problem")).replace("_", " ")
    alternative = _text(first.get("what_problem_should_be_tested_instead"))
    if apparent_problem and alternative:
        return f"The visible issue may be '{apparent_problem}', but the system should first test whether {alternative.lower()}."
    return ""


def _hidden_system_boundary_error(
    *,
    cross_layer_congruence_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
) -> str:
    for row in cross_layer_congruence_register:
        contradiction = _text(row.get("contradiction")).lower()
        if "control boundary" in contradiction:
            return "The hidden system-boundary error is assuming that the burdened actor and the controllable load boundary are the same thing."
    for row in invalid_comparison_risk_register:
        requirements = " ".join(_list_text(row.get("required_normalization"))).lower()
        if "control boundary" in requirements:
            return "The hidden system-boundary error is comparing outcomes before the control boundary is normalized."
        if any(
            token in requirements
            for token in (
                "service level",
                "throughput proxy",
                "dock activity",
                "charging schedule",
                "temperature duty",
                "service continuity",
                "dispatch burden",
                "redundancy class",
                "demand structure",
            )
        ):
            return "The hidden system-boundary error is comparing area-normalized outcomes before the operational-intensity boundary is normalized."
    for row in finance_physics_dependency_register:
        physical_dependency = _text(row.get("physical_dependency")).lower()
        if "boundary" in physical_dependency or "control" in physical_dependency:
            return "The hidden system-boundary error is treating economic pressure as proof that the controllable physical boundary is already known."
        if any(
            token in physical_dependency
            for token in (
                "service level",
                "temperature duty",
                "movement intensity",
                "charging profile",
                "service continuity",
                "dispatch duty",
                "dispatch burden",
                "redundancy class",
                "demand structure",
                "reliability posture",
            )
        ):
            return "The hidden system-boundary error is treating area-normalized energy as decision truth before the duty boundary is known."
    if cross_layer_congruence_register:
        contradiction = _text(cross_layer_congruence_register[0].get("contradiction")).lower()
        if "service-level complexity" in contradiction or "benchmark" in contradiction:
            return "The hidden system-boundary error is assuming that area alone is the relevant system boundary for comparison and capital logic."
        if any(token in contradiction for token in ("service continuity", "dispatch", "reliability obligation", "redundancy")):
            return "The hidden system-boundary error is assuming that average energy is the relevant system boundary before continuity and dispatch duty are normalized."
    return ""


def _invalid_comparison_risk_take(
    invalid_comparison_risk_register: list[dict[str, Any]],
) -> str:
    first = _first_row(invalid_comparison_risk_register)
    required = _dedupe(_list_text(first.get("required_normalization")))[:4]
    trigger = _text(first.get("trigger"))
    if required:
        return f"This comparison remains structurally invalid until {', '.join(required)} are normalized."
    return trigger


def _dominant_loss_logic_take(
    *,
    loss_pattern_hypothesis_register: list[dict[str, Any]],
    maintenance_reality_register: list[dict[str, Any]],
    strategic_gold_nugget_register: list[dict[str, Any]],
) -> str:
    nugget = _first_nugget(strategic_gold_nugget_register, "wrong_loss_story")
    if nugget:
        return _text(nugget.get("gold_nugget"))
    for row in maintenance_reality_register:
        reality_claim = _text(row.get("reality_claim")).lower()
        if "downtime economics" in reality_claim:
            return _text(row.get("why_it_matters")) or _text(row.get("reality_claim"))
    first = _first_row(loss_pattern_hypothesis_register)
    if first:
        return _text(first.get("hypothesis")) or _text(first.get("why_plausible"))
    return ""


def _measurement_minimality_take(
    measurement_strategy_register: list[dict[str, Any]],
) -> str:
    first = _first_row(measurement_strategy_register)
    minimum_measurement = _text(first.get("minimum_measurement"))
    why = _text(first.get("why"))
    if minimum_measurement:
        return _join_sentences(
            f"The next best discriminator is {minimum_measurement}, not broader sensor deployment.",
            why,
        )
    return why


def _regulatory_physics_take(
    regulatory_physics_register: list[dict[str, Any]],
) -> str:
    first = _first_row(regulatory_physics_register)
    signal = _text(first.get("regulatory_signal"))
    implication = _text(first.get("physical_implication"))
    if signal and implication:
        return f"{signal}: {implication}"
    return implication or signal


def _finance_to_physics_take(
    finance_physics_dependency_register: list[dict[str, Any]],
) -> str:
    first = _first_row(finance_physics_dependency_register)
    assumption = _text(first.get("financial_assumption"))
    dependency = _text(first.get("physical_dependency"))
    if assumption and dependency:
        return f"{assumption.capitalize()} only holds if {dependency}."
    return _text(first.get("risk_if_wrong"))


def _maintenance_reality_take(
    maintenance_reality_register: list[dict[str, Any]],
) -> str:
    first = _first_row(maintenance_reality_register)
    reality_claim = _text(first.get("reality_claim"))
    why = _text(first.get("why_it_matters"))
    if reality_claim and why:
        normalized_why = why.rstrip(".")
        normalized_why = (
            normalized_why[0].lower() + normalized_why[1:]
            if len(normalized_why) > 1
            else normalized_why.lower()
        )
        return f"{reality_claim.capitalize()} because {normalized_why}."
    return reality_claim or why


def _inadmissibility_reason(
    *,
    selected_mode: str,
    canonical_problem_frame: dict[str, Any],
    system_abstraction: dict[str, Any],
) -> str:
    selected_archetype = _text(system_abstraction.get("selected_archetype_id"))
    if selected_archetype == "target_not_yet_structurally_modelable":
        return "Structural thesis remains inadmissible until the case is bounded as an operating asset with discriminable dominant variables."
    if not bool(canonical_problem_frame.get("problem_frame_active", False)):
        return "Structural thesis remains inadmissible until the case crosses the problem-framing threshold for structural interpretation."
    if selected_mode == "Target Classification Brief":
        return "Structural thesis remains inadmissible while the case is still in target-classification mode."
    return "Structural thesis remains inadmissible until the dominant contradiction and minimum discriminating evidence are sufficiently bounded."


def build_executive_thesis(  # noqa: PLR0913
    *,
    system_abstraction: dict[str, Any],
    canonical_problem_frame: dict[str, Any],
    problem_framing_register: list[dict[str, Any]],
    dominant_variable_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    scenario_register: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    expanded_structural_tad_action_register: list[dict[str, Any]],
    claim_contract_register: list[dict[str, Any]],
    report_output_mode_classifier_table: list[dict[str, Any]],
    invalid_problem_frame_register: list[dict[str, Any]] | None = None,
    invalid_comparison_risk_register: list[dict[str, Any]] | None = None,
    cross_layer_congruence_register: list[dict[str, Any]] | None = None,
    loss_pattern_hypothesis_register: list[dict[str, Any]] | None = None,
    maintenance_reality_register: list[dict[str, Any]] | None = None,
    measurement_strategy_register: list[dict[str, Any]] | None = None,
    regulatory_physics_register: list[dict[str, Any]] | None = None,
    finance_physics_dependency_register: list[dict[str, Any]] | None = None,
    strategic_gold_nugget_register: list[dict[str, Any]] | None = None,
    gold_nugget_strength_register: list[dict[str, Any]] | None = None,
    congruence_action_priority_register: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    invalid_problem_frame_register = list(invalid_problem_frame_register or [])
    invalid_comparison_risk_register = list(invalid_comparison_risk_register or [])
    cross_layer_congruence_register = list(cross_layer_congruence_register or [])
    loss_pattern_hypothesis_register = list(loss_pattern_hypothesis_register or [])
    maintenance_reality_register = list(maintenance_reality_register or [])
    measurement_strategy_register = list(measurement_strategy_register or [])
    regulatory_physics_register = list(regulatory_physics_register or [])
    finance_physics_dependency_register = list(finance_physics_dependency_register or [])
    strategic_gold_nugget_register = list(strategic_gold_nugget_register or [])
    gold_nugget_strength_register = list(gold_nugget_strength_register or [])
    congruence_action_priority_register = list(congruence_action_priority_register or [])

    effective_primary_problem = _effective_primary_problem(
        problem_framing_register=problem_framing_register,
        invalid_problem_frame_register=invalid_problem_frame_register,
    )
    effective_conflict_register = list(cross_layer_conflict_register or [])
    if not effective_conflict_register:
        effective_conflict_register = _translated_congruence_conflict_register(cross_layer_congruence_register)
    ranked_conflicts = _ranked_conflict_register(
        canonical_problem_frame=canonical_problem_frame,
        cross_layer_conflict_register=effective_conflict_register,
        structural_financial_exposure_register=structural_financial_exposure_register,
        minimum_evidence_for_discrimination_register=minimum_evidence_for_discrimination_register,
        expanded_structural_tad_action_register=expanded_structural_tad_action_register,
        claim_contract_register=claim_contract_register,
    )
    primary_conflict = ranked_conflicts[0] if ranked_conflicts else {}
    primary_minimum_evidence = (
        minimum_evidence_for_discrimination_register[0]
        if minimum_evidence_for_discrimination_register
        else {}
    )
    primary_redesign = _primary_redesign(conditional_redesign_register)
    primary_financial = _primary_financial_exposure(structural_financial_exposure_register)
    primary_peer = _primary_peer_comparison(competitive_comparison_register)
    selected_mode = _selected_output_mode(report_output_mode_classifier_table)
    supporting_modes = _supporting_modes(report_output_mode_classifier_table, selected_mode)
    subject_family = _subject_family(
        system_abstraction=system_abstraction,
        canonical_problem_frame=canonical_problem_frame,
        cross_layer_conflict_register=effective_conflict_register,
    )
    minimum_discriminating_evidence = _split_compound_evidence(
        primary_minimum_evidence.get("minimum_evidence")
        or canonical_problem_frame.get("minimum_evidence_to_discriminate")
    )
    top_actions = _client_facing_tad_actions(
        expanded_structural_tad_action_register,
        _text(primary_conflict.get("conflict")) or _text(canonical_problem_frame.get("dominant_conflict")),
        minimum_discriminating_evidence,
        congruence_action_priority_register=congruence_action_priority_register,
    )
    evidence_state = _evidence_state(
        canonical_problem_frame,
        cross_layer_conflict_register,
        structural_financial_exposure_register,
    )
    what_is_admissible_now = [row["action"] for row in top_actions[:3]]
    prohibited_actions = _what_is_not_admissible(claim_contract_register)
    top_scenarios = _top_scenarios(scenario_register)
    top_variables = _top_dominant_variables(dominant_variable_register)
    why_it_matters = (
        _text(primary_conflict.get("why_it_matters"))
        or _text(primary_financial.get("financial_exposure_if_wrong"))
        or _text(effective_primary_problem.get("strategic_risk"))
    )
    dominant_risk = (
        _text(primary_financial.get("financial_exposure_if_wrong"))
        or _text(effective_primary_problem.get("strategic_risk"))
    )
    dominant_contradiction = _text(primary_conflict.get("conflict")) or _text(canonical_problem_frame.get("dominant_conflict"))
    structural_thesis_admissible = bool(canonical_problem_frame.get("problem_frame_active", False)) and bool(dominant_contradiction)
    if not structural_thesis_admissible:
        inadmissibility_reason = _inadmissibility_reason(
            selected_mode=selected_mode,
            canonical_problem_frame=canonical_problem_frame,
            system_abstraction=system_abstraction,
        )
        return {
            "declared_problem": _text(effective_primary_problem.get("stated_problem"))
            or _text(canonical_problem_frame.get("stated_problem"))
            or "Need bounded target understanding before structural interpretation.",
            "reframed_problem": "Structural interpretation remains premature because the case is not yet bounded enough to support a dominant contradiction.",
            "dominant_contradiction": "",
            "why_it_matters": inadmissibility_reason,
            "dominant_risk": "A structural thesis here would overstate what the system actually knows about the case.",
            "hidden_assumption_at_risk": "",
            "why_current_question_is_premature": inadmissibility_reason,
            "what_reality_feature_changes_the_decision": "",
            "capital_logic_if_assumption_holds": "",
            "capital_logic_if_assumption_breaks": "",
            "surprising_but_evidenced_takeaway": "",
            "what_is_admissible_now": [],
            "what_is_not_admissible": prohibited_actions,
            "minimum_discriminating_evidence": [],
            "minimum_discriminating_evidence_source": "",
            "minimum_discriminating_evidence_unlocks": [],
            "conditional_redesign": {},
            "evidence_state": "INADMISSIBLE_CLAIM",
            "report_mode": selected_mode,
            "confidence_level": "inadmissible",
            "top_dominant_variables": [],
            "top_scenarios": [],
            "top_actions": [],
            "dominant_lens": "",
            "supporting_modes": [],
            "primary_financial_exposure": {},
            "primary_peer_comparison": {},
            "dominant_operational_misunderstanding": "",
            "hidden_system_boundary_error": "",
            "invalid_comparison_risk": "",
            "dominant_loss_logic": "",
            "measurement_minimality_take": "",
            "regulatory_physics_take": "",
            "finance_to_physics_take": "",
            "maintenance_reality_take": "",
            "top_gold_nuggets": [],
            "gold_nugget_strength_register": [],
            "congruence_action_priority_register": [],
            "interpretive_signal_register": [],
            "dominant_contradiction_selection_basis": {},
            "thesis_ranked_conflict_register": [],
            "rejected_contradiction_candidates": [],
            "thesis_state": "inadmissible_thesis",
            "inadmissibility_reason": inadmissibility_reason,
            "compression_targets": {
                "max_dominant_variables": 0,
                "max_primary_scenarios": 0,
                "max_primary_actions": 0,
                "max_primary_redesign_paths": 0,
                "max_primary_evidence_packs": 0,
            },
        }
    hidden_assumption_at_risk = _hidden_assumption_at_risk(subject_family, dominant_contradiction)
    dominant_operational_misunderstanding = _dominant_operational_misunderstanding(
        invalid_problem_frame_register=invalid_problem_frame_register,
        strategic_gold_nugget_register=strategic_gold_nugget_register,
    )
    hidden_system_boundary_error = _hidden_system_boundary_error(
        cross_layer_congruence_register=cross_layer_congruence_register,
        invalid_comparison_risk_register=invalid_comparison_risk_register,
        finance_physics_dependency_register=finance_physics_dependency_register,
    )
    invalid_comparison_risk = _invalid_comparison_risk_take(invalid_comparison_risk_register)
    dominant_loss_logic = _dominant_loss_logic_take(
        loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
        maintenance_reality_register=maintenance_reality_register,
        strategic_gold_nugget_register=strategic_gold_nugget_register,
    )
    measurement_minimality_take = _measurement_minimality_take(measurement_strategy_register)
    regulatory_physics_take = _regulatory_physics_take(regulatory_physics_register)
    finance_to_physics_take = _finance_to_physics_take(finance_physics_dependency_register)
    maintenance_reality_take = _maintenance_reality_take(maintenance_reality_register)
    interpretive_signal_register = _interpretive_signal_register(
        subject_family=subject_family,
        dominant_contradiction=dominant_contradiction,
        evidence_state=evidence_state,
        primary_problem=effective_primary_problem,
        primary_financial=primary_financial,
        primary_redesign=primary_redesign,
        primary_peer=primary_peer,
        minimum_discriminating_evidence=minimum_discriminating_evidence,
    )
    return {
        "declared_problem": _text(effective_primary_problem.get("stated_problem"))
        or _text(canonical_problem_frame.get("stated_problem")),
        "reframed_problem": _text(effective_primary_problem.get("reframed_problem"))
        or _text(canonical_problem_frame.get("reframed_problem")),
        "dominant_contradiction": dominant_contradiction,
        "why_it_matters": why_it_matters,
        "dominant_risk": dominant_risk,
        "hidden_assumption_at_risk": hidden_assumption_at_risk,
        "why_current_question_is_premature": _join_sentences(
            _why_current_question_is_premature(
                subject_family,
                dominant_contradiction,
                minimum_discriminating_evidence,
            ),
            measurement_minimality_take,
        ),
        "what_reality_feature_changes_the_decision": _what_reality_feature_changes_the_decision(
            subject_family,
            dominant_contradiction,
        ),
        "capital_logic_if_assumption_holds": _join_sentences(
            _capital_logic_if_assumption_holds(
                subject_family,
                primary_redesign,
                primary_financial,
            ),
            finance_to_physics_take,
        ),
        "capital_logic_if_assumption_breaks": _capital_logic_if_assumption_breaks(
            subject_family,
            primary_financial,
            primary_redesign,
        ),
        "surprising_but_evidenced_takeaway": _surprising_takeaway(
            subject_family=subject_family,
            interpretive_signal_register=interpretive_signal_register,
            hidden_assumption_at_risk=hidden_assumption_at_risk,
            dominant_contradiction=dominant_contradiction,
        ),
        "dominant_operational_misunderstanding": dominant_operational_misunderstanding,
        "hidden_system_boundary_error": hidden_system_boundary_error,
        "invalid_comparison_risk": invalid_comparison_risk,
        "dominant_loss_logic": dominant_loss_logic,
        "measurement_minimality_take": measurement_minimality_take,
        "regulatory_physics_take": regulatory_physics_take,
        "finance_to_physics_take": finance_to_physics_take,
        "maintenance_reality_take": maintenance_reality_take,
        "top_gold_nuggets": [
            {
                "nugget_id": _text(row.get("nugget_id")),
                "gold_nugget": _text(row.get("gold_nugget")),
                "evidence_state": _text(row.get("evidence_state")),
                "what_to_do_next": _text(row.get("what_to_do_next")),
            }
            for row in strategic_gold_nugget_register[:3]
            if _text(row.get("gold_nugget"))
        ],
        "gold_nugget_strength_register": gold_nugget_strength_register[:5],
        "what_is_admissible_now": what_is_admissible_now,
        "what_is_not_admissible": prohibited_actions,
        "minimum_discriminating_evidence": minimum_discriminating_evidence,
        "minimum_discriminating_evidence_source": _text(primary_minimum_evidence.get("source"))
        or _text(canonical_problem_frame.get("minimum_evidence_source")),
        "minimum_discriminating_evidence_unlocks": _list_text(primary_minimum_evidence.get("unlocks"))
        or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks")),
        "conditional_redesign": primary_redesign,
        "evidence_state": evidence_state,
        "report_mode": selected_mode,
        "confidence_level": _confidence_level(evidence_state),
        "top_dominant_variables": top_variables,
        "top_scenarios": top_scenarios,
        "top_actions": top_actions,
        "dominant_lens": dominant_contradiction,
        "supporting_modes": supporting_modes,
        "primary_financial_exposure": primary_financial,
        "primary_peer_comparison": primary_peer,
        "congruence_action_priority_register": congruence_action_priority_register[:5],
        "interpretive_signal_register": interpretive_signal_register,
        "dominant_contradiction_selection_basis": dict(primary_conflict.get("selection_basis", {}) or {}),
        "thesis_ranked_conflict_register": ranked_conflicts,
        "rejected_contradiction_candidates": ranked_conflicts[1:],
        "thesis_state": "admissible_structural_thesis",
        "inadmissibility_reason": "",
        "compression_targets": {
            "max_dominant_variables": 3,
            "max_primary_scenarios": 3,
            "max_primary_actions": 3,
            "max_primary_redesign_paths": 1,
            "max_primary_evidence_packs": 1,
        },
    }
