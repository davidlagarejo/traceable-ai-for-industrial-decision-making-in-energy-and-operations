from __future__ import annotations

from typing import Any

from ..congruence_intelligence.operational_logic import build_asset_operational_logic
from ..knowledge_layer import knowledge_layer_summary
from .base import BaseMotorAdapter


class Motor050Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_050"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_049", "motor_060"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m49 = dict(inputs.get("motor_049", {}) or {})
        m60 = inputs.get("motor_060", {}) if isinstance(inputs.get("motor_060", {}), dict) else {}
        diversity_axis_plan = dict(m60.get("diversity_axis_plan", {}) or {})
        required_themes = list(diversity_axis_plan.get("required_themes", []) or [])
        # The Pattern Library defines which axes are valid for this asset
        # family; any axis NOT in required_themes is structurally
        # inappropriate to claim for this asset (e.g. process_heat for a
        # warehouse). Surface the set so downstream consumers can guard.
        all_known_axes = {
            "logistics_throughput", "tariff_orchestration", "thermal_exchange",
            "service_level_intensity", "process_heat", "compressed_air",
            "power_quality", "maintenance_reality", "production_throughput",
            "tenant_boundary", "bms_schedule", "after_hours_load",
            "hvac_topology", "regulatory", "pue_composition",
            "redundancy_posture", "cooling_topology", "water_use",
            "continuity_duty", "dispatch_posture", "thermal_continuity",
            "intermodal_throughput",
        }
        prohibited_themes = sorted(all_known_axes - set(required_themes)) if required_themes else []
        out = build_asset_operational_logic(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            local_evidence_binding_register=list(m49.get("local_evidence_binding_register", []) or []),
        )
        return {
            **out,
            "subsystem_count": len(out.get("subsystem_register", []) or []),
            "control_boundary_count": len(out.get("control_boundary_map", []) or []),
            "equipment_dominance_count": len(out.get("equipment_dominance_register", []) or []),
            # R-57: surface prohibited_themes (axes that do NOT belong to this
            # asset family per the Pattern Library) for validators to guard.
            "diversity_required_themes": required_themes,
            "diversity_prohibited_themes": prohibited_themes,
            # V2-LIVE Item 4: surface the 4 Gap-F knowledge YAMLs so
            # downstream consumers (composer, validators) can reach them
            # through motor_050's bundle.
            "knowledge_layer_registry": knowledge_layer_summary(),
        }

