from __future__ import annotations

from typing import Any

from ..congruence_intelligence.operational_logic import build_asset_operational_logic
from .base import BaseMotorAdapter


class Motor050Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_050"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_049"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m49 = dict(inputs.get("motor_049", {}) or {})
        out = build_asset_operational_logic(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            local_evidence_binding_register=list(m49.get("local_evidence_binding_register", []) or []),
        )
        return {
            **out,
            "subsystem_count": len(out.get("subsystem_register", []) or []),
            "control_boundary_count": len(out.get("control_boundary_map", []) or []),
            "equipment_dominance_count": len(out.get("equipment_dominance_register", []) or []),
        }

