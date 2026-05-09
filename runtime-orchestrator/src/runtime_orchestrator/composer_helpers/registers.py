"""Register builders — evidence pack, thesis constellation, correlation constellation.

Extracted verbatim from executive_thesis.py during composer slim
(RECOVERY_BACKLOG.md R-70..R-74). Behaviour is unchanged.
"""
from __future__ import annotations

from typing import Any

from .text_helpers import (
    _dedupe,
    _is_semantically_redundant,
    _list_text,
    _text,
)


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
