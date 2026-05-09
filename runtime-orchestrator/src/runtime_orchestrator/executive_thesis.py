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

_CONCEPT_MARKER_MAP = {
    "denominator_reframe": {"denominator", "benchmark", "comparison", "peer"},
    "boundary_reframe": {"boundary", "owner", "tenant", "control", "capture", "meter"},
    "tariff_logic": {"tariff", "demand", "peak", "charging"},
    "thermal_exchange": {"dock", "infiltration", "thermal", "refrigeration", "hvac"},
    "maintenance_reality": {"maintenance", "downtime", "reliability", "uptime"},
    "model_prematurity": {"model", "sensor", "digital", "instrumentation"},
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


def _overlap_ratio(left: Any, right: Any) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    shared = len(left_tokens.intersection(right_tokens))
    return shared / max(min(len(left_tokens), len(right_tokens)), 1)


def _shared_token_count(left: Any, right: Any) -> int:
    return len(_tokens(left).intersection(_tokens(right)))


def _concept_markers(*values: Any) -> set[str]:
    tokens = _tokens(*values)
    markers: set[str] = set()
    for marker, required_tokens in _CONCEPT_MARKER_MAP.items():
        if tokens.intersection(required_tokens):
            markers.add(marker)
    return markers


def _is_semantically_redundant(
    candidate: Any,
    existing_values: list[Any],
    *,
    threshold: float = 0.7,
    allow_marker_collapse: bool = True,
    marker_overlap_token_floor: int = 1,
) -> bool:
    candidate_markers = _concept_markers(candidate)
    for existing in list(existing_values or []):
        if _overlap_ratio(candidate, existing) >= threshold:
            return True
        if not allow_marker_collapse:
            continue
        shared_markers = candidate_markers.intersection(_concept_markers(existing))
        if shared_markers and _shared_token_count(candidate, existing) >= marker_overlap_token_floor:
            return True
    return False


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


def _top_gold_nugget_rows(
    strategic_gold_nugget_register: list[dict[str, Any]],
    *,
    gold_nugget_strength_register: list[dict[str, Any]] | None = None,
    limit: int = 5,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_text: set[str] = set()
    seen_themes: set[str] = set()
    selected_statements: list[str] = []
    strength_by_id = {
        _text(row.get("nugget_id")): dict(row)
        for row in list(gold_nugget_strength_register or [])
        if _text(row.get("nugget_id"))
    }
    ranked_candidates = sorted(
        [dict(row or {}) for row in list(strategic_gold_nugget_register or [])],
        key=lambda row: (
            -int(
                (strength_by_id.get(_text(row.get("nugget_id")), {}) or {}).get("selection_priority_score", 0) or 0
            ),
            -int(
                (strength_by_id.get(_text(row.get("nugget_id")), {}) or {}).get("cross_layer_breadth_score", 0) or 0
            ),
            _text(row.get("nugget_id")),
        ),
    )

    def _append_if_allowed(row: dict[str, Any], *, enforce_theme_diversity: bool) -> None:
        gold_nugget = _text(row.get("gold_nugget"))
        if not gold_nugget or gold_nugget in seen_text:
            return
        nugget_id = _text(row.get("nugget_id"))
        strength_row = strength_by_id.get(nugget_id, {})
        nugget_theme = _text(strength_row.get("nugget_theme")) or _text(row.get("nugget_theme"))
        if enforce_theme_diversity and nugget_theme and nugget_theme in seen_themes:
            return
        redundancy_threshold = 0.68 if nugget_theme == "problem_reframe" else 0.6
        if _is_semantically_redundant(gold_nugget, selected_statements, threshold=redundancy_threshold):
            return
        seen_text.add(gold_nugget)
        if nugget_theme:
            seen_themes.add(nugget_theme)
        selected_statements.append(gold_nugget)
        rows.append(
            {
                "nugget_id": nugget_id,
                "gold_nugget": gold_nugget,
                "evidence_state": _text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                "what_to_do_next": _text(row.get("what_to_do_next")),
                "nugget_theme": nugget_theme,
                "strength_label": _text(strength_row.get("strength_label")) or "bounded",
            }
        )
    prioritized_problem_reframe = next(
        (
            row for row in ranked_candidates
            if _text(row.get("nugget_id")) == "wrong_problem_frame"
            or (_text((strength_by_id.get(_text(row.get("nugget_id")), {}) or {}).get("nugget_theme")) == "problem_reframe")
        ),
        None,
    )
    if prioritized_problem_reframe:
        _append_if_allowed(prioritized_problem_reframe, enforce_theme_diversity=False)
        if len(rows) >= limit:
            return rows

    for row in ranked_candidates:
        _append_if_allowed(row, enforce_theme_diversity=True)
        if len(rows) >= limit:
            return rows
    for row in ranked_candidates:
        _append_if_allowed(row, enforce_theme_diversity=False)
        if len(rows) >= limit:
            return rows
    return rows


def _build_evidence_pack_register(
    *,
    minimum_discriminating_evidence: list[str],
    minimum_evidence_source: str,
    minimum_evidence_unlocks: list[str],
    invalid_comparison_risk_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
    loss_pattern_hypothesis_register: list[dict[str, Any]],
    effective_primary_problem: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def _append(
        *,
        pack_family: str,
        pack_title: str,
        evidence_items: list[str],
        unlocks: list[str],
        why: str,
        evidence_state: str = "CONDITIONAL_HYPOTHESIS",
    ) -> None:
        normalized_items = _dedupe(_list_text(evidence_items))
        if not normalized_items:
            return
        if any(
            _text(existing.get("pack_family")) == pack_family
            and _dedupe(_list_text(existing.get("evidence_items"))) == normalized_items
            for existing in rows
        ):
            return
        rows.append(
            {
                "pack_family": pack_family,
                "pack_title": pack_title,
                "evidence_items": normalized_items,
                "unlocks": _dedupe(_list_text(unlocks)),
                "why": _text(why),
                "evidence_state": _text(evidence_state) or "CONDITIONAL_HYPOTHESIS",
                "source": _text(minimum_evidence_source) if pack_family == "primary_discriminator_pack" else "derived_structural_pack",
            }
        )

    _append(
        pack_family="primary_discriminator_pack",
        pack_title="Primary discriminator pack",
        evidence_items=minimum_discriminating_evidence,
        unlocks=minimum_evidence_unlocks or [
            "local structural closure",
            "capital logic discrimination",
        ],
        why=_text(effective_primary_problem.get("why_original_framing_may_be_wrong"))
        or _text(effective_primary_problem.get("strategic_risk"))
        or "This is the minimum pack that changes the meaning of the case.",
        evidence_state=_text(effective_primary_problem.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
    )

    invalid_comparison = dict(invalid_comparison_risk_register[0] if invalid_comparison_risk_register else {})
    _append(
        pack_family="fair_comparison_pack",
        pack_title="Fair comparison pack",
        evidence_items=_list_text(invalid_comparison.get("required_normalization")),
        unlocks=[
            "fair comparison admissibility",
            "bounded peer screening",
        ],
        why=_text(invalid_comparison.get("trigger"))
        or "These fields determine whether comparison logic is valid at all.",
    )
    if not any(_text(row.get("pack_family")) == "fair_comparison_pack" for row in rows):
        comparison_unlocks = [
            unlock
            for unlock in _list_text(minimum_evidence_unlocks)
            if any(token in unlock.lower() for token in ("comparison", "peer", "denominator"))
        ]
        _append(
            pack_family="fair_comparison_pack",
            pack_title="Fair comparison pack",
            evidence_items=minimum_discriminating_evidence[:3],
            unlocks=comparison_unlocks or [
                "fair comparison admissibility",
                "bounded peer screening",
            ],
            why="The primary discriminator pack also decides whether comparison logic is structurally valid.",
            evidence_state=_text(effective_primary_problem.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
        )

    finance_dependency = dict(finance_physics_dependency_register[0] if finance_physics_dependency_register else {})
    finance_evidence = _list_text(finance_dependency.get("evidence_needed"))
    finance_dependency_text = " ".join(
        [
            _text(finance_dependency.get("financial_assumption")),
            _text(finance_dependency.get("physical_dependency")),
            _text(finance_dependency.get("risk_if_wrong")),
        ]
    ).lower()
    boundary_family = (
        "control_boundary_pack"
        if any(token in finance_dependency_text for token in ("boundary", "owner", "tenant", "meter", "capture", "control"))
        else "capital_logic_pack"
    )
    _append(
        pack_family=boundary_family,
        pack_title="Control-boundary pack" if boundary_family == "control_boundary_pack" else "Capital logic pack",
        evidence_items=finance_evidence,
        unlocks=[
            "value-capture discrimination",
            "capital logic validity",
        ],
        why=_text(finance_dependency.get("risk_if_wrong"))
        or _text(finance_dependency.get("physical_dependency"))
        or "These fields decide whether the visible economics are even capturable.",
        evidence_state=_text(finance_dependency.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
    )

    loss_pattern = dict(loss_pattern_hypothesis_register[0] if loss_pattern_hypothesis_register else {})
    _append(
        pack_family="loss_falsification_pack",
        pack_title="Loss falsification pack",
        evidence_items=_list_text(loss_pattern.get("minimum_local_evidence")),
        unlocks=[
            "pattern falsification",
            "dominant loss discrimination",
        ],
        why=_text(loss_pattern.get("why_plausible"))
        or _text(loss_pattern.get("hypothesis"))
        or "These fields decide whether the dominant loss story is real or only archetypal.",
        evidence_state=_text(loss_pattern.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
    )
    compacted_rows: list[dict[str, Any]] = []
    retained_signatures: list[str] = []
    for row in rows:
        signature = " ".join(
            [
                _text(row.get("pack_title")),
                " ".join(_list_text(row.get("evidence_items"))),
                " ".join(_list_text(row.get("unlocks"))),
                _text(row.get("why")),
            ]
        )
        if _is_semantically_redundant(signature, retained_signatures, threshold=0.82):
            continue
        compacted_rows.append(row)
        retained_signatures.append(signature)
    return compacted_rows


def _build_thesis_constellation_register(
    *,
    primary_conflict: dict[str, Any],
    ranked_conflicts: list[dict[str, Any]],
    top_variables: list[dict[str, str]],
    invalid_comparison_risk: str,
    dominant_loss_logic: str,
    hidden_system_boundary_error: str,
    top_gold_nuggets: list[dict[str, str]],
    evidence_pack_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def _append(
        *,
        element_type: str,
        title: str,
        statement: str,
        evidence_state: str = "CONDITIONAL_HYPOTHESIS",
        why_it_matters: str = "",
        supporting_layers: list[str] | None = None,
        differentiator: str = "",
        evidence_pack_family: str = "",
    ) -> None:
        text = _text(statement)
        if not text:
            return
        rows.append(
            {
                "constellation_id": f"{element_type}_{len(rows) + 1:02d}",
                "element_type": element_type,
                "title": _text(title),
                "statement": text,
                "evidence_state": _text(evidence_state) or "CONDITIONAL_HYPOTHESIS",
                "why_it_matters": _text(why_it_matters),
                "supporting_layers": _dedupe(_list_text(supporting_layers or [])),
                "differentiator": _text(differentiator),
                "evidence_pack_family": _text(evidence_pack_family),
            }
        )

    primary_layers = _list_text(primary_conflict.get("layers_involved"))
    primary_pack_family = _text((evidence_pack_register[0] or {}).get("pack_family")) if evidence_pack_register else ""
    _append(
        element_type="dominant_contradiction",
        title="Dominant contradiction",
        statement=_text(primary_conflict.get("conflict")),
        evidence_state=_text(primary_conflict.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
        why_it_matters=_text(primary_conflict.get("why_it_matters")),
        supporting_layers=primary_layers,
        differentiator="This is the lead contradiction currently changing the decision frame the most.",
        evidence_pack_family=primary_pack_family,
    )

    for row in list(ranked_conflicts or [])[1:3]:
        _append(
            element_type="challenger_hypothesis",
            title="Challenger hypothesis",
            statement=_text(row.get("conflict")),
            evidence_state=_text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
            why_it_matters=_text(row.get("why_it_matters")),
            supporting_layers=_list_text(row.get("layers_involved")),
            differentiator="This is not the lead contradiction, but it would still materially change interpretation if it survives falsification.",
            evidence_pack_family=primary_pack_family,
        )

    for index, row in enumerate(list(top_variables or [])[:4]):
        _append(
            element_type="dominant_variable_candidate" if index == 0 else "alternative_variable_candidate",
            title="Dominant variable candidate" if index == 0 else "Alternative variable candidate",
            statement=_text(row.get("variable")),
            evidence_state=_text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
            why_it_matters=_text(row.get("why_it_could_matter")) or _text(row.get("decision_impact")),
            supporting_layers=[_text(row.get("layer"))],
            differentiator=(
                "This is the most decision-relevant variable candidate currently visible."
                if index == 0
                else "This variable matters for a different reason than the lead driver and should not be collapsed into the same explanation."
            ),
            evidence_pack_family=primary_pack_family,
        )

    _append(
        element_type="comparison_failure",
        title="Comparison failure",
        statement=invalid_comparison_risk,
        evidence_state="CONDITIONAL_HYPOTHESIS",
        why_it_matters="Comparison can distort the whole decision if the denominator is structurally invalid.",
        supporting_layers=["benchmarking", "finance", "operation"],
        differentiator="This attacks the denominator and peer frame rather than the physical system itself.",
        evidence_pack_family="fair_comparison_pack",
    )
    _append(
        element_type="boundary_failure",
        title="Boundary failure",
        statement=hidden_system_boundary_error,
        evidence_state="CONDITIONAL_HYPOTHESIS",
        why_it_matters="A valid technical move can still fail economically if the control and capture boundary are wrong.",
        supporting_layers=["control", "finance", "responsibility"],
        differentiator="This attacks who controls, pays, and captures rather than which subsystem consumes.",
        evidence_pack_family="control_boundary_pack",
    )
    _append(
        element_type="loss_logic",
        title="Dominant loss logic",
        statement=dominant_loss_logic,
        evidence_state="CONDITIONAL_HYPOTHESIS",
        why_it_matters="This frames what kind of loss story is actually plausible under the current archetype.",
        supporting_layers=["physics", "operation", "maintenance"],
        differentiator="This attacks the loss mechanism rather than the benchmark or payer boundary.",
        evidence_pack_family="loss_falsification_pack",
    )

    for row in list(top_gold_nuggets or [])[:2]:
        _append(
            element_type="strategic_nugget",
            title="Strategic nugget",
            statement=_text(row.get("gold_nugget")),
            evidence_state=_text(row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
            why_it_matters="This is the shortest executive reframe that still changes interpretation.",
            differentiator="This is the executive shock layer, not the structural proof layer.",
            evidence_pack_family=primary_pack_family,
        )
    compacted_rows: list[dict[str, Any]] = []
    retained_signatures: list[str] = []
    protected_types = {"dominant_contradiction", "comparison_failure", "boundary_failure", "loss_logic"}
    for row in rows:
        signature = _text(row.get("statement")) or " ".join(
            [
                _text(row.get("title")),
                _text(row.get("why_it_matters")),
                _text(row.get("differentiator")),
            ]
        )
        element_type = _text(row.get("element_type"))
        redundancy_threshold = 0.45 if element_type == "strategic_nugget" else 0.6
        allow_marker_collapse = element_type != "challenger_hypothesis"
        if (
            element_type not in protected_types
            and _is_semantically_redundant(
                signature,
                retained_signatures,
                threshold=redundancy_threshold,
                allow_marker_collapse=allow_marker_collapse,
            )
        ):
            continue
        compacted_rows.append(row)
        retained_signatures.append(signature)
    return compacted_rows


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
                "supporting_correlation_count": int(row.get("supporting_correlation_count", 0) or 0),
                "supporting_correlation_register": list(row.get("supporting_correlation_register", []) or []),
                "supporting_correlation_ids": _list_text(row.get("supporting_correlation_ids")),
                "supporting_correlation_headlines": _list_text(row.get("supporting_correlation_headlines")),
                "fair_comparison_pressure_score": int(row.get("fair_comparison_pressure_score", 0) or 0),
                "boundary_pressure_score": int(row.get("boundary_pressure_score", 0) or 0),
                "maintenance_pressure_score": int(row.get("maintenance_pressure_score", 0) or 0),
                "correlation_constellation_score": int(row.get("correlation_constellation_score", 0) or 0),
            }
        )
    return rows


def _build_correlation_constellation_register(
    ranked_conflicts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for conflict_row in list(ranked_conflicts or [])[:3]:
        conflict = _text(conflict_row.get("conflict"))
        supporting_rows = list(conflict_row.get("supporting_correlation_register", []) or [])
        if not supporting_rows and conflict:
            layers = _list_text(conflict_row.get("layers_involved"))
            layer_label = " + ".join(layers[:3]) if layers else "cross-layer coupling"
            rows.append(
                {
                    "constellation_id": f"corr_const_{len(rows) + 1:02d}",
                    "linked_conflict": conflict,
                    "correlation": f"{layer_label} coupling",
                    "strategic_meaning": _text(conflict_row.get("why_it_matters")),
                    "evidence_needed": _list_text(conflict_row.get("what_confirms_it")),
                    "evidence_state": _text(conflict_row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                    "support_score": int(conflict_row.get("correlation_constellation_score", 0) or 0),
                }
            )
            continue
        for support_row in supporting_rows[:2]:
            correlation = _text(support_row.get("correlation"))
            if not conflict or not correlation:
                continue
            rows.append(
                {
                    "constellation_id": f"corr_const_{len(rows) + 1:02d}",
                    "linked_conflict": conflict,
                    "correlation": correlation,
                    "strategic_meaning": _text(support_row.get("strategic_meaning")),
                    "evidence_needed": _list_text(support_row.get("evidence_needed")),
                    "evidence_state": _text(support_row.get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
                    "support_score": int(support_row.get("support_score", 0) or 0),
                }
            )
    compacted_rows: list[dict[str, Any]] = []
    retained_signatures: list[str] = []
    for row in rows:
        signature = " ".join(
            [
                _text(row.get("linked_conflict")),
                _text(row.get("correlation")),
                _text(row.get("strategic_meaning")),
                " ".join(_list_text(row.get("evidence_needed"))),
            ]
        )
        if _is_semantically_redundant(signature, retained_signatures, threshold=0.8):
            continue
        compacted_rows.append(row)
        retained_signatures.append(signature)
    return compacted_rows[:5]


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
        action = _text(row.get("action")) or _format_label(row.get("strategic_action")).title()
        if not action:
            continue
        maps_to = contradiction_map if _text(row.get("linked_claim")) != "TAD_action_claim" else evidence_map
        evidence_needed_text = (
            _text(row.get("evidence_needed"))
            or "; ".join(_list_text(row.get("evidence_needed")))
        )
        financial_exposure = _text(row.get("financial_exposure"))
        if not financial_exposure and "tariff" in _text(row.get("trigger")).lower():
            financial_exposure = "Tariff or demand logic may dominate economics before generic efficiency logic."
        elif not financial_exposure and "boundary" in _text(row.get("trigger")).lower():
            financial_exposure = "Value can leak across owner / operator / payer boundaries before CAPEX reaches the balance sheet."
        elif not financial_exposure and "maintenance" in _text(row.get("trigger")).lower():
            financial_exposure = "Downtime and maintenance economics may dominate before utility savings do."
        rows.append(
            {
                "action": action,
                "status": _text(row.get("status")),
                "decision_front": _text(row.get("decision_front")) or action,
                "trigger": _text(row.get("trigger")),
                "trigger_family": _text(row.get("trigger_family")),
                "why": _text(row.get("why")),
                "evidence_state": _text(row.get("evidence_state")),
                "financial_exposure": financial_exposure,
                "evidence_needed": evidence_needed_text,
                "evidence_pack_family": _text(row.get("evidence_pack_family")),
                "action_posture": _text(row.get("action_posture")) or _text(row.get("status")),
                "prohibited_action": _text(row.get("prohibited_action")),
                "prohibited_action_class": _text(row.get("prohibited_action_class")),
                "linked_claim": _text(row.get("linked_claim")),
                "maps_to": maps_to,
            }
        )
        if len(rows) >= 5:
            break
    if rows:
        return rows
    for row in list(congruence_action_priority_register or [])[:5]:
        action = _format_label(row.get("strategic_action")).title()
        if not action:
            continue
        rows.append(
            {
                "action": action,
                "status": _text(row.get("status")),
                "decision_front": action,
                "trigger": _text(row.get("strategic_action")),
                "trigger_family": "",
                "why": _text(row.get("why")) or _text(row.get("gold_nugget")),
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "financial_exposure": "",
                "evidence_needed": "; ".join(_list_text(row.get("evidence_needed"))),
                "evidence_pack_family": "",
                "action_posture": _text(row.get("status")),
                "prohibited_action": _text(row.get("prohibited_action")),
                "prohibited_action_class": "",
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


def _conditional_structural_intelligence_available(
    *,
    effective_primary_problem: dict[str, Any],
    canonical_problem_frame: dict[str, Any],
    ranked_conflicts: list[dict[str, Any]],
    invalid_problem_frame_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    loss_pattern_hypothesis_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
    strategic_gold_nugget_register: list[dict[str, Any]],
    congruence_action_priority_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    top_variables: list[dict[str, str]],
) -> bool:
    meaningful_top_variables = [
        row
        for row in top_variables
        if (
            _text(row.get("variable")).lower() != "dominant structural discriminator"
            or _text(row.get("why_it_could_matter"))
            or _text(row.get("decision_impact")) != "bounded structural decision sequencing"
        )
    ]
    effective_problem_state = _text(effective_primary_problem.get("evidence_state")).upper()
    effective_reframe_text = _text(effective_primary_problem.get("reframed_problem"))
    meaningful_effective_reframe = bool(
        effective_reframe_text
        and effective_problem_state
        and effective_problem_state not in {"", "INADMISSIBLE_CLAIM"}
    )
    meaningful_structural_registers = bool(
        ranked_conflicts
        or invalid_comparison_risk_register
        or loss_pattern_hypothesis_register
        or finance_physics_dependency_register
        or strategic_gold_nugget_register
        or congruence_action_priority_register
        or conditional_redesign_register
        or meaningful_top_variables
    )
    return bool(
        meaningful_structural_registers
        or meaningful_effective_reframe
    )


def _fallback_conditional_conflict(
    *,
    canonical_problem_frame: dict[str, Any],
    effective_primary_problem: dict[str, Any],
    invalid_problem_frame_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
    loss_pattern_hypothesis_register: list[dict[str, Any]],
) -> dict[str, Any]:
    canonical_conflict = _text(canonical_problem_frame.get("dominant_conflict"))
    primary_invalid = dict(invalid_problem_frame_register[0] if invalid_problem_frame_register else {})
    invalid_comparison = dict(invalid_comparison_risk_register[0] if invalid_comparison_risk_register else {})
    finance_dependency = dict(finance_physics_dependency_register[0] if finance_physics_dependency_register else {})
    loss_pattern = dict(loss_pattern_hypothesis_register[0] if loss_pattern_hypothesis_register else {})
    effective_reframe = _text(effective_primary_problem.get("reframed_problem"))
    strategic_risk = _text(effective_primary_problem.get("strategic_risk")) or _text(primary_invalid.get("why_invalid_or_premature"))

    conflict = (
        canonical_conflict
        or _text(primary_invalid.get("what_problem_should_be_tested_instead"))
        or _text(invalid_comparison.get("trigger"))
        or _text(finance_dependency.get("physical_dependency"))
        or _text(loss_pattern.get("hypothesis"))
        or effective_reframe
        or "Visible framing vs dominant structural driver"
    )
    layers = (
        _list_text(primary_invalid.get("linked_layers"))
        or _list_text(effective_primary_problem.get("linked_layers"))
        or ["benchmarking", "operation", "finance", "control/responsibility"]
    )
    why_it_matters = (
        strategic_risk
        or _text(invalid_comparison.get("trigger"))
        or _text(finance_dependency.get("risk_if_wrong"))
        or _text(loss_pattern.get("why_plausible"))
        or "The current frame may optimize a secondary variable before the dominant structural driver is bounded."
    )
    redesign = (
        _text(primary_invalid.get("what_problem_should_be_tested_instead"))
        or _text(finance_dependency.get("physical_dependency"))
        or "Discriminate the dominant structural driver before local diagnosis or capital closure."
    )
    return {
        "conflict": conflict,
        "layers_involved": layers,
        "why_it_matters": why_it_matters,
        "potential_redesign_direction": redesign,
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "selection_basis": {
            "conditional_fallback": True,
            "source_priority": "problem_frame_or_congruence_guardrail",
            "economic_exposure_score": 1,
            "decision_blocking_score": 1,
            "evidence_discrimination_score": 1,
            "cross_layer_breadth_score": len(layers),
            "claim_permission_consequence_score": 1,
            "canonical_problem_frame_bonus": 1 if canonical_conflict else 0,
            "total_rank_score": max(4, len(layers) + (1 if canonical_conflict else 0)),
        },
    }


def _conditional_minimum_evidence(
    *,
    primary_minimum_evidence: dict[str, Any],
    canonical_problem_frame: dict[str, Any],
    effective_primary_problem: dict[str, Any],
    invalid_comparison_risk_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
    loss_pattern_hypothesis_register: list[dict[str, Any]],
) -> list[str]:
    direct = _split_compound_evidence(
        primary_minimum_evidence.get("minimum_evidence")
        or canonical_problem_frame.get("minimum_evidence_to_discriminate")
    )
    if direct:
        return direct
    effective_needed = _list_text(effective_primary_problem.get("evidence_needed"))
    if effective_needed:
        return effective_needed
    invalid_comparison = dict(invalid_comparison_risk_register[0] if invalid_comparison_risk_register else {})
    if invalid_comparison:
        return _list_text(invalid_comparison.get("required_normalization"))
    finance_dependency = dict(finance_physics_dependency_register[0] if finance_physics_dependency_register else {})
    if finance_dependency:
        return _list_text(finance_dependency.get("evidence_needed"))
    loss_pattern = dict(loss_pattern_hypothesis_register[0] if loss_pattern_hypothesis_register else {})
    return _list_text(loss_pattern.get("minimum_local_evidence"))


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
    strategic_gold_nugget_source_register: str = "motor_054.strategic_gold_nugget_register",
    strategic_gold_nugget_authority_state: str = "legacy_primary_skill_shadow",
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
    selected_top_gold_nuggets = _top_gold_nugget_rows(
        strategic_gold_nugget_register,
        gold_nugget_strength_register=gold_nugget_strength_register,
        limit=8,
    )
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
        conditional_intelligence_available = _conditional_structural_intelligence_available(
            effective_primary_problem=effective_primary_problem,
            canonical_problem_frame=canonical_problem_frame,
            ranked_conflicts=ranked_conflicts,
            invalid_problem_frame_register=invalid_problem_frame_register,
            invalid_comparison_risk_register=invalid_comparison_risk_register,
            loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
            finance_physics_dependency_register=finance_physics_dependency_register,
            strategic_gold_nugget_register=strategic_gold_nugget_register,
            congruence_action_priority_register=congruence_action_priority_register,
            conditional_redesign_register=conditional_redesign_register,
            top_variables=top_variables,
        )
        if conditional_intelligence_available:
            fallback_conflict = primary_conflict or _fallback_conditional_conflict(
                canonical_problem_frame=canonical_problem_frame,
                effective_primary_problem=effective_primary_problem,
                invalid_problem_frame_register=invalid_problem_frame_register,
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
            )
            conditional_ranked_conflicts = list(ranked_conflicts or [fallback_conflict])
            conditional_primary_conflict = dict(conditional_ranked_conflicts[0] if conditional_ranked_conflicts else fallback_conflict)
            conditional_dominant_contradiction = _text(conditional_primary_conflict.get("conflict")) or "Visible framing vs dominant structural driver"
            conditional_minimum_evidence = _conditional_minimum_evidence(
                primary_minimum_evidence=primary_minimum_evidence,
                canonical_problem_frame=canonical_problem_frame,
                effective_primary_problem=effective_primary_problem,
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
            )
            conditional_top_actions = _client_facing_tad_actions(
                expanded_structural_tad_action_register,
                conditional_dominant_contradiction,
                conditional_minimum_evidence,
                congruence_action_priority_register=congruence_action_priority_register,
            )
            conditional_evidence_state = (
                _text(effective_primary_problem.get("evidence_state"))
                or _text(conditional_primary_conflict.get("evidence_state"))
                or _text(primary_financial.get("evidence_state"))
                or "CONDITIONAL_HYPOTHESIS"
            )
            conditional_why_it_matters = (
                _text(conditional_primary_conflict.get("why_it_matters"))
                or _text(primary_financial.get("financial_exposure_if_wrong"))
                or _text(effective_primary_problem.get("strategic_risk"))
                or inadmissibility_reason
            )
            conditional_dominant_risk = (
                _text(primary_financial.get("financial_exposure_if_wrong"))
                or _text(effective_primary_problem.get("strategic_risk"))
                or "A local structural thesis would still overstate what the system actually knows, but the current framing may still be strategically wrong."
            )
            conditional_hidden_assumption = _hidden_assumption_at_risk(subject_family, conditional_dominant_contradiction)
            conditional_measurement_take = _measurement_minimality_take(measurement_strategy_register)
            conditional_regulatory_take = _regulatory_physics_take(regulatory_physics_register)
            conditional_finance_take = _finance_to_physics_take(finance_physics_dependency_register)
            conditional_maintenance_take = _maintenance_reality_take(maintenance_reality_register)
            conditional_operational_misunderstanding = _dominant_operational_misunderstanding(
                invalid_problem_frame_register=invalid_problem_frame_register,
                strategic_gold_nugget_register=strategic_gold_nugget_register,
            )
            conditional_hidden_boundary_error = _hidden_system_boundary_error(
                cross_layer_congruence_register=cross_layer_congruence_register,
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
            )
            conditional_invalid_comparison = _invalid_comparison_risk_take(invalid_comparison_risk_register)
            conditional_loss_logic = _dominant_loss_logic_take(
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
                maintenance_reality_register=maintenance_reality_register,
                strategic_gold_nugget_register=strategic_gold_nugget_register,
            )
            conditional_evidence_pack_register = _build_evidence_pack_register(
                minimum_discriminating_evidence=conditional_minimum_evidence,
                minimum_evidence_source=_text(primary_minimum_evidence.get("source"))
                or _text(canonical_problem_frame.get("minimum_evidence_source"))
                or "conditional_structural_intelligence_layer",
                minimum_evidence_unlocks=_list_text(primary_minimum_evidence.get("unlocks"))
                or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks"))
                or [
                    "local structural closure",
                    "fair comparison admissibility",
                    "capital logic discrimination",
                ],
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
                effective_primary_problem=effective_primary_problem,
            )
            conditional_thesis_constellation_register = _build_thesis_constellation_register(
                primary_conflict=conditional_primary_conflict,
                ranked_conflicts=conditional_ranked_conflicts,
                top_variables=top_variables,
                invalid_comparison_risk=conditional_invalid_comparison,
                dominant_loss_logic=conditional_loss_logic,
                hidden_system_boundary_error=conditional_hidden_boundary_error,
                top_gold_nuggets=selected_top_gold_nuggets,
                evidence_pack_register=conditional_evidence_pack_register,
            )
            conditional_correlation_constellation_register = _build_correlation_constellation_register(
                conditional_ranked_conflicts,
            )
            conditional_interpretive_signal_register = _interpretive_signal_register(
                subject_family=subject_family,
                dominant_contradiction=conditional_dominant_contradiction,
                evidence_state=conditional_evidence_state,
                primary_problem=effective_primary_problem,
                primary_financial=primary_financial,
                primary_redesign=primary_redesign,
                primary_peer=primary_peer,
                minimum_discriminating_evidence=conditional_minimum_evidence,
            )
            return {
                "declared_problem": _text(effective_primary_problem.get("stated_problem"))
                or _text(canonical_problem_frame.get("stated_problem"))
                or "Need bounded target understanding before structural interpretation.",
                "reframed_problem": _text(effective_primary_problem.get("reframed_problem"))
                or _text(canonical_problem_frame.get("reframed_problem"))
                or "The current framing may be wrong even though local structural closure remains blocked.",
                "dominant_contradiction": conditional_dominant_contradiction,
                "why_it_matters": conditional_why_it_matters,
                "dominant_risk": conditional_dominant_risk,
                "hidden_assumption_at_risk": conditional_hidden_assumption,
                "why_current_question_is_premature": _join_sentences(
                    inadmissibility_reason,
                    _why_current_question_is_premature(
                        subject_family,
                        conditional_dominant_contradiction,
                        conditional_minimum_evidence,
                    ),
                    conditional_measurement_take,
                ),
                "what_reality_feature_changes_the_decision": _what_reality_feature_changes_the_decision(
                    subject_family,
                    conditional_dominant_contradiction,
                ),
                "capital_logic_if_assumption_holds": _join_sentences(
                    _capital_logic_if_assumption_holds(
                        subject_family,
                        primary_redesign,
                        primary_financial,
                    ),
                    conditional_finance_take,
                ),
                "capital_logic_if_assumption_breaks": _capital_logic_if_assumption_breaks(
                    subject_family,
                    primary_financial,
                    primary_redesign,
                ),
                "surprising_but_evidenced_takeaway": _surprising_takeaway(
                    subject_family=subject_family,
                    interpretive_signal_register=conditional_interpretive_signal_register,
                    hidden_assumption_at_risk=conditional_hidden_assumption,
                    dominant_contradiction=conditional_dominant_contradiction,
                ),
                "what_is_admissible_now": [row["action"] for row in conditional_top_actions[:3]],
                "what_is_not_admissible": prohibited_actions,
                "minimum_discriminating_evidence": conditional_minimum_evidence,
                "minimum_discriminating_evidence_source": _text(primary_minimum_evidence.get("source"))
                or _text(canonical_problem_frame.get("minimum_evidence_source"))
                or "conditional_structural_intelligence_layer",
                "minimum_discriminating_evidence_unlocks": _list_text(primary_minimum_evidence.get("unlocks"))
                or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks"))
                or [
                    "local structural closure",
                    "fair comparison admissibility",
                    "capital logic discrimination",
                ],
                "conditional_redesign": primary_redesign,
                "evidence_state": conditional_evidence_state,
                "report_mode": selected_mode,
                "confidence_level": _confidence_level(conditional_evidence_state),
                "top_dominant_variables": top_variables,
                "top_scenarios": top_scenarios,
                "top_actions": conditional_top_actions,
                "dominant_lens": conditional_dominant_contradiction,
                "supporting_modes": supporting_modes,
                "primary_financial_exposure": primary_financial,
                "primary_peer_comparison": primary_peer,
                "dominant_operational_misunderstanding": conditional_operational_misunderstanding,
                "hidden_system_boundary_error": conditional_hidden_boundary_error,
                "invalid_comparison_risk": conditional_invalid_comparison,
                "dominant_loss_logic": conditional_loss_logic,
                "measurement_minimality_take": conditional_measurement_take,
                "regulatory_physics_take": conditional_regulatory_take,
                "finance_to_physics_take": conditional_finance_take,
                "maintenance_reality_take": conditional_maintenance_take,
                "top_gold_nuggets": selected_top_gold_nuggets,
                "gold_nugget_source_register": _text(strategic_gold_nugget_source_register),
                "gold_nugget_authority_state": _text(strategic_gold_nugget_authority_state) or "legacy_primary_skill_shadow",
                "gold_nugget_strength_register": gold_nugget_strength_register[:8],
                "evidence_pack_register": conditional_evidence_pack_register,
                "thesis_constellation_register": conditional_thesis_constellation_register,
                "correlation_constellation_register": conditional_correlation_constellation_register,
                "congruence_action_priority_register": congruence_action_priority_register[:5],
                "interpretive_signal_register": conditional_interpretive_signal_register,
                "dominant_contradiction_selection_basis": dict(conditional_primary_conflict.get("selection_basis", {}) or {}),
                "thesis_ranked_conflict_register": conditional_ranked_conflicts,
                "rejected_contradiction_candidates": conditional_ranked_conflicts[1:],
                "thesis_state": "conditional_structural_intelligence",
                "local_thesis_state": "inadmissible_local_closure",
                "local_claim_closure_state": "blocked",
                "conditional_intelligence_available": True,
                "conditional_intelligence_reason": "Local structural closure remains blocked, but bounded archetypal and conditional intelligence is still admissible.",
                "inadmissibility_reason": inadmissibility_reason,
                "compression_targets": {
                    "max_dominant_variables": 4,
                    "max_primary_scenarios": 3,
                    "max_primary_actions": 4,
                    "max_primary_redesign_paths": 2,
                    "max_primary_evidence_packs": 3,
                },
            }
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
            "gold_nugget_source_register": _text(strategic_gold_nugget_source_register),
            "gold_nugget_authority_state": _text(strategic_gold_nugget_authority_state) or "legacy_primary_skill_shadow",
            "gold_nugget_strength_register": [],
            "evidence_pack_register": [],
            "thesis_constellation_register": [],
            "correlation_constellation_register": [],
            "congruence_action_priority_register": [],
            "interpretive_signal_register": [],
            "dominant_contradiction_selection_basis": {},
            "thesis_ranked_conflict_register": [],
            "rejected_contradiction_candidates": [],
            "thesis_state": "inadmissible_thesis",
            "local_thesis_state": "inadmissible_local_closure",
            "local_claim_closure_state": "blocked",
            "conditional_intelligence_available": False,
            "conditional_intelligence_reason": "",
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
    evidence_pack_register = _build_evidence_pack_register(
        minimum_discriminating_evidence=minimum_discriminating_evidence,
        minimum_evidence_source=_text(primary_minimum_evidence.get("source"))
        or _text(canonical_problem_frame.get("minimum_evidence_source")),
        minimum_evidence_unlocks=_list_text(primary_minimum_evidence.get("unlocks"))
        or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks")),
        invalid_comparison_risk_register=invalid_comparison_risk_register,
        finance_physics_dependency_register=finance_physics_dependency_register,
        loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
        effective_primary_problem=effective_primary_problem,
    )
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
    thesis_constellation_register = _build_thesis_constellation_register(
        primary_conflict=primary_conflict,
        ranked_conflicts=ranked_conflicts,
        top_variables=top_variables,
        invalid_comparison_risk=invalid_comparison_risk,
        dominant_loss_logic=dominant_loss_logic,
        hidden_system_boundary_error=hidden_system_boundary_error,
        top_gold_nuggets=selected_top_gold_nuggets,
        evidence_pack_register=evidence_pack_register,
    )
    correlation_constellation_register = _build_correlation_constellation_register(
        ranked_conflicts,
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
        "top_gold_nuggets": selected_top_gold_nuggets,
        "gold_nugget_source_register": _text(strategic_gold_nugget_source_register),
        "gold_nugget_authority_state": _text(strategic_gold_nugget_authority_state) or "legacy_primary_skill_shadow",
        "gold_nugget_strength_register": gold_nugget_strength_register[:8],
        "evidence_pack_register": evidence_pack_register,
        "thesis_constellation_register": thesis_constellation_register,
        "correlation_constellation_register": correlation_constellation_register,
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
        "local_thesis_state": "admissible_local_structural_closure",
        "local_claim_closure_state": "admissible",
        "conditional_intelligence_available": False,
        "conditional_intelligence_reason": "",
        "inadmissibility_reason": "",
        "compression_targets": {
            "max_dominant_variables": 4,
            "max_primary_scenarios": 3,
            "max_primary_actions": 4,
            "max_primary_redesign_paths": 2,
            "max_primary_evidence_packs": 3,
        },
    }
