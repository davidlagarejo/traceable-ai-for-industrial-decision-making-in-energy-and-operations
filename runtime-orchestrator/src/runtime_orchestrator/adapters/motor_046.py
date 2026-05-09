from __future__ import annotations

import re
from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_minimum_evidence_for_discrimination_register
from .base import BaseMotorAdapter


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slugify_hypothesis(text: str, fallback_index: int) -> str:
    """Stable slug for a rival hypothesis, e.g. for use as a dict key.

    'Owner-controllable base-building upside dominates.' →
    'owner_controllable_base_building_upside_dominates'
    """
    if not text:
        return f"hypothesis_{fallback_index:03d}"
    cleaned = _NON_ALNUM.sub("_", text.strip().lower()).strip("_")
    if not cleaned:
        return f"hypothesis_{fallback_index:03d}"
    # Cap length to avoid degenerate keys
    return cleaned[:80]


def _build_evidence_pack_per_hypothesis_id(
    register: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Index every rival hypothesis to the evidence pack that discriminates it.

    Same evidence pack may map to multiple hypotheses (rivals from a single
    discrimination row share their `minimum_evidence`). The dict allows
    consumers (motor_055, motor_056, composer) to ask "what evidence
    discriminates *this specific* hypothesis?" rather than receiving a
    canonical pack reused across all sections (the artefact visible in
    the Sunrise PDF).
    """
    out: dict[str, dict[str, Any]] = {}
    next_index = 0
    for row in register:
        if not isinstance(row, dict):
            continue
        rivals = row.get("rival_hypotheses", []) or []
        if not isinstance(rivals, list):
            continue
        shared = {
            "minimum_evidence": str(row.get("minimum_evidence", "")).strip(),
            "source": str(row.get("source", "")).strip(),
            "what_it_confirms": str(row.get("what_it_confirms", "")).strip(),
            "what_it_falsifies": str(row.get("what_it_falsifies", "")).strip(),
            "unlocks": list(row.get("unlocks", []) or []),
        }
        for rival in rivals:
            text = str(rival or "").strip()
            slug = _slugify_hypothesis(text, next_index)
            next_index += 1
            # Skip duplicate slugs but keep the first occurrence stable
            if slug in out:
                continue
            out[slug] = {
                "rival_hypothesis": text,
                **shared,
            }
    return out


class Motor046Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_046"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_038", "motor_040", "motor_041", "motor_044"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        target_definition = (
            inputs.get("motor_012", {}).get("facility_prior", {}).get("target_definition")
            or inputs.get("motor_007", {}).get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )
        register = build_minimum_evidence_for_discrimination_register(
            target_definition=target_definition,
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            problem_framing_register=list(inputs.get("motor_041", {}).get("problem_framing_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
        )
        evidence_pack_per_hypothesis_id = _build_evidence_pack_per_hypothesis_id(register)
        return {
            "minimum_evidence_for_discrimination_register": register,
            "minimum_evidence_for_discrimination_count": len(register),
            "evidence_pack_per_hypothesis_id": evidence_pack_per_hypothesis_id,
            "hypothesis_indexed_count": len(evidence_pack_per_hypothesis_id),
        }

