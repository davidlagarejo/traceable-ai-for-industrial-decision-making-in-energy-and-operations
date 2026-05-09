"""Adapter for motor_060 — Report Diversity Engine (Layer B).

Generates a `diversity_axis_plan` that downstream Layer-B/E consumers
(problem framing, dominant variable, asset operational logic, composer)
can use to force per-asset diversification of hypotheses, evidence packs,
themes, and chart types.

The plan is grounded in the Pattern Library JSON files
(governanza/asset-operational-logic-engine_050/patterns/<family>.json) so
adding a new asset family is a Pattern-Library edit, not a code edit.

This is the producer commit. Consumers opt in incrementally (R-55..R-57
in RECOVERY_BACKLOG.md). Until then, motor_060's output is a no-op for
downstream behaviour but is published on the LayerBundle bus and visible
to any motor that wants to read it.
"""
from __future__ import annotations

from typing import Any

from ..pattern_library import asset_family_concept_markers, load_pattern_library
from .base import BaseMotorAdapter


def _text(value: Any) -> str:
    return str(value or "").strip()


def _resolve_asset_family(inputs: dict[str, Any]) -> str:
    m007 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
    target_definition = (
        m007.get("target_definition_contract", {})
        if isinstance(m007.get("target_definition_contract", {}), dict)
        else {}
    )
    return _text(
        target_definition.get("target_type")
        or target_definition.get("asset_family")
    )


def _build_diversity_axis_plan(asset_family: str) -> dict[str, Any]:
    pattern = load_pattern_library(asset_family)
    if pattern is None:
        return {
            "asset_family": asset_family,
            "library_version": None,
            "dominant_axis": None,
            "required_themes": [],
            "axis_concept_markers": {},
            "axis_falsifiers": {},
            "minimum_unique_evidence_packs": 0,
            "forbidden_repetition_signature_count_max": 2,
            "status": "no_pattern_library_for_family",
        }

    axes = pattern.get("axes", {}) or {}
    axis_concept_markers: dict[str, list[str]] = {}
    axis_falsifiers: dict[str, list[str]] = {}
    for axis_name, axis_data in axes.items():
        if not isinstance(axis_data, dict):
            continue
        axis_concept_markers[str(axis_name)] = [
            _text(t) for t in axis_data.get("concept_markers", []) or [] if _text(t)
        ]
        axis_falsifiers[str(axis_name)] = [
            _text(t) for t in axis_data.get("falsifiers", []) or [] if _text(t)
        ]

    required_themes = list(axis_concept_markers.keys())
    dominant_axis = required_themes[0] if required_themes else None

    return {
        "asset_family": asset_family,
        "library_version": _text(pattern.get("library_version")),
        "dominant_axis": dominant_axis,
        "required_themes": required_themes,
        "axis_concept_markers": axis_concept_markers,
        "axis_falsifiers": axis_falsifiers,
        # Heuristic minima derived from the catalogue size; consumers can
        # override but this gives motor_055/056 something concrete to compare
        # against.
        "minimum_unique_evidence_packs": max(3, len(required_themes)),
        "forbidden_repetition_signature_count_max": 2,
        "status": "ok",
    }


class Motor060Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_060"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        asset_family = _resolve_asset_family(inputs)
        plan = _build_diversity_axis_plan(asset_family)

        # Surface a flat catalog of all asset-family tokens for consumers
        # (e.g. motor_057) that want a single set rather than per-axis.
        flat_tokens = sorted(asset_family_concept_markers(asset_family))

        return {
            "diversity_axis_plan": plan,
            "asset_family_evaluated": asset_family,
            "axis_count": len(plan.get("required_themes", []) or []),
            "library_version": plan.get("library_version"),
            "flat_concept_markers": flat_tokens,
            "concept_marker_count": len(flat_tokens),
        }
