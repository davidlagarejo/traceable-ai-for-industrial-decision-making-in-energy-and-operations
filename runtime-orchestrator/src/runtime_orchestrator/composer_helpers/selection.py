"""Selection helpers — output modes, top variables, top gold nuggets.

Extracted verbatim from executive_thesis.py during composer slim
(RECOVERY_BACKLOG.md R-70..R-74). Behaviour is unchanged.
"""
from __future__ import annotations

from typing import Any

from ..output_taxonomy import canonicalize_output_mode
from .text_helpers import (
    _dedupe,
    _is_semantically_redundant,
    _text,
)


_STRUCTURAL_CLASSIFICATION_STATES = {
    "selected_primary_structural",
    "active_secondary_structural",
    "eligible_primary_structural",
}


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
