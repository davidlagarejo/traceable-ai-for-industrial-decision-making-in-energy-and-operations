from __future__ import annotations

from typing import Any

from ..congruence_intelligence.hardware_minimality import build_hardware_minimality_register
from ..knowledge_layer import knowledge_layer_summary
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
from ..zlab_skill.loader import load_registry_bundle
from ..zlab_skill.runtime_bridge import (
    build_active_skill_pattern_state,
    build_pattern_authority_state,
    build_registry_pattern_activation_register,
)
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
        try:
            registry_bundle = load_registry_bundle()
        except Exception:
            registry_bundle = {}
        skill_active_pattern_ids, skill_active_pattern_sources, _ = build_active_skill_pattern_state(
            motor_049_output=m49,
            motor_051_output=m51,
            motor_052_output={
                "activated_pattern_register": activated_pattern_register,
                "power_quality_hypothesis_register": power_quality_hypothesis_register,
                "measurement_strategy_register": measurement_strategy_register,
                "hardware_minimality_register": hardware_minimality_register,
            }
        )
        skill_pattern_activation_register = build_registry_pattern_activation_register(
            registry_bundle=registry_bundle,
            active_pattern_sources=skill_active_pattern_sources,
        )
        pattern_authority_summary = build_pattern_authority_state(
            legacy_pattern_register=activated_pattern_register,
            skill_pattern_activation_register=skill_pattern_activation_register,
            skill_active_pattern_ids=skill_active_pattern_ids,
        )
        pattern_authority_state = str(
            pattern_authority_summary.get("pattern_authority_state", "legacy_primary_skill_shadow")
        ).strip() or "legacy_primary_skill_shadow"
        authoritative_pattern_activation_register = (
            skill_pattern_activation_register
            if pattern_authority_state == "skill_primary"
            else activated_pattern_register
        )
        return {
            "loss_pattern_hypothesis_register": loss_pattern_hypothesis_register,
            "activated_pattern_register": activated_pattern_register,
            "pattern_discrimination_register": pattern_discrimination_register,
            "skill_active_pattern_ids": skill_active_pattern_ids,
            "skill_active_pattern_sources": skill_active_pattern_sources,
            "skill_pattern_activation_register": skill_pattern_activation_register,
            "authoritative_pattern_activation_register": authoritative_pattern_activation_register,
            "pattern_authority_state": pattern_authority_state,
            "pattern_authority_summary": pattern_authority_summary,
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
            "skill_pattern_activation_count": len(skill_pattern_activation_register),
            "pattern_discrimination_count": len(pattern_discrimination_register),
            "maintenance_reality_count": len(maintenance_reality_register),
            "maintenance_proof_gap_count": len(maintenance_proof_gap_register),
            "downtime_dependency_count": len(downtime_dependency_register),
            "measurement_strategy_count": len(measurement_strategy_register),
            "hardware_minimality_count": len(hardware_minimality_register),
            "power_quality_hypothesis_count": len(power_quality_hypothesis_register),
            "leakage_hypothesis_count": len(leakage_hypothesis_register),
            # V2-LIVE Item 4: surface the Gap-F knowledge YAMLs for the
            # composer + validators to reach via motor_052's bundle.
            "knowledge_layer_registry": knowledge_layer_summary(),
        }
