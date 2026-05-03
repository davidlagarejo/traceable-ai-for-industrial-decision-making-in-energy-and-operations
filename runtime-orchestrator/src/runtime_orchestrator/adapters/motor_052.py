from __future__ import annotations

from typing import Any

from ..congruence_intelligence.hardware_minimality import build_hardware_minimality_register
from ..congruence_intelligence.leakage_hidden_waste import build_leakage_hypothesis_register
from ..congruence_intelligence.loss_patterns import (
    build_activated_pattern_register,
    build_industrial_common_sense_register,
    build_loss_pattern_hypothesis_register,
    build_pattern_discrimination_register,
)
from ..congruence_intelligence.maintenance_reality import (
    build_downtime_dependency_register,
    build_maintenance_proof_gap_register,
    build_maintenance_reality_register,
)
from ..congruence_intelligence.measurement_strategy import build_measurement_strategy_register
from ..congruence_intelligence.power_quality import build_power_quality_hypothesis_register
from .base import BaseMotorAdapter


class Motor052Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_052"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_049", "motor_050", "motor_051"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m49 = dict(inputs.get("motor_049", {}) or {})
        m50 = dict(inputs.get("motor_050", {}) or {})
        m51 = dict(inputs.get("motor_051", {}) or {})
        asset_family_research_profile = dict(m49.get("asset_family_research_profile", {}) or {})
        operational_intake_pack = dict(m49.get("operational_intake_pack", {}) or {})
        subsystem_register = list(m50.get("subsystem_register", []) or [])
        maintenance_dependency_map = list(m50.get("maintenance_dependency_map", []) or [])
        dynamic_intake_question_register = list(m49.get("dynamic_intake_question_register", []) or [])
        peer_requirement_register = list(m51.get("peer_requirement_register", []) or [])
        loss_pattern_hypothesis_register = build_loss_pattern_hypothesis_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            subsystem_register=subsystem_register,
            dynamic_intake_question_register=dynamic_intake_question_register,
            peer_requirement_register=peer_requirement_register,
        )
        activated_pattern_register = build_activated_pattern_register(
            loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
        )
        pattern_discrimination_register = build_pattern_discrimination_register(
            loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
        )
        industrial_common_sense_register = build_industrial_common_sense_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
        )
        maintenance_reality_register = build_maintenance_reality_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            maintenance_dependency_map=maintenance_dependency_map,
        )
        maintenance_proof_gap_register = build_maintenance_proof_gap_register(
            asset_family_research_profile=asset_family_research_profile,
            maintenance_dependency_map=maintenance_dependency_map,
        )
        downtime_dependency_register = build_downtime_dependency_register(
            asset_family_research_profile=asset_family_research_profile,
            maintenance_dependency_map=maintenance_dependency_map,
        )
        power_quality_hypothesis_register = build_power_quality_hypothesis_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            subsystem_register=subsystem_register,
        )
        leakage_hypothesis_register = build_leakage_hypothesis_register(
            asset_family_research_profile=asset_family_research_profile,
            subsystem_register=subsystem_register,
        )
        measurement_strategy_register = build_measurement_strategy_register(
            asset_family_research_profile=asset_family_research_profile,
            power_quality_hypothesis_register=power_quality_hypothesis_register,
            leakage_hypothesis_register=leakage_hypothesis_register,
            loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
            maintenance_reality_register=maintenance_reality_register,
        )
        hardware_minimality_register = build_hardware_minimality_register(
            measurement_strategy_register=measurement_strategy_register,
        )
        return {
            "loss_pattern_hypothesis_register": loss_pattern_hypothesis_register,
            "activated_pattern_register": activated_pattern_register,
            "pattern_discrimination_register": pattern_discrimination_register,
            "industrial_common_sense_register": industrial_common_sense_register,
            "maintenance_reality_register": maintenance_reality_register,
            "maintenance_proof_gap_register": maintenance_proof_gap_register,
            "downtime_dependency_register": downtime_dependency_register,
            "measurement_strategy_register": measurement_strategy_register,
            "hardware_minimality_register": hardware_minimality_register,
            "power_quality_hypothesis_register": power_quality_hypothesis_register,
            "leakage_hypothesis_register": leakage_hypothesis_register,
            "loss_pattern_count": len(loss_pattern_hypothesis_register),
            "activated_pattern_count": len(activated_pattern_register),
            "pattern_discrimination_count": len(pattern_discrimination_register),
            "maintenance_reality_count": len(maintenance_reality_register),
            "maintenance_proof_gap_count": len(maintenance_proof_gap_register),
            "downtime_dependency_count": len(downtime_dependency_register),
            "measurement_strategy_count": len(measurement_strategy_register),
            "hardware_minimality_count": len(hardware_minimality_register),
            "power_quality_hypothesis_count": len(power_quality_hypothesis_register),
            "leakage_hypothesis_count": len(leakage_hypothesis_register),
        }
