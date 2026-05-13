from __future__ import annotations

from typing import Any

from ..congruence_intelligence.climate_location import (
    build_climate_location_context_register,
    build_utility_tariff_context_register,
)
from ..congruence_intelligence.culture_proxy import build_culture_execution_proxy_register
from ..congruence_intelligence.finance_to_physics import (
    build_capital_logic_register,
    build_cost_driver_dependency_register,
    build_finance_physics_dependency_register,
    build_financial_exposure_type_register,
    build_underwriting_misread_register,
    build_value_leakage_register,
)
from ..congruence_intelligence.regulatory_physics import (
    build_permit_signal_register,
    build_regulatory_constraint_register,
    build_regulatory_physics_register,
)
from ..phase_units import to_compliance_applicability_case_register
from ..zlab_skill.runtime_bridge import build_registry_financial_exposure_register
from .base import BaseMotorAdapter


class Motor053Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_053"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_012", "motor_028", "motor_049", "motor_050", "motor_051", "motor_052"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m12 = dict(inputs.get("motor_012", {}) or {})
        m28 = dict(inputs.get("motor_028", {}) or {})
        m49 = dict(inputs.get("motor_049", {}) or {})
        m50 = dict(inputs.get("motor_050", {}) or {})
        m51 = dict(inputs.get("motor_051", {}) or {})
        m52 = dict(inputs.get("motor_052", {}) or {})

        facility_prior = dict(m12.get("facility_prior", {}) or {})
        target_definition = dict(
            (facility_prior.get("target_definition") or {})
            or (m49.get("operational_intake_pack", {}).get("asset_identity_pack", {}) or {})
        )
        source_register = list(m28.get("source_register", []) or [])
        asset_family_research_profile = dict(m49.get("asset_family_research_profile", {}) or {})
        operational_intake_pack = dict(m49.get("operational_intake_pack", {}) or {})

        regulatory_physics_register = build_regulatory_physics_register(
            target_definition=target_definition,
            asset_family_research_profile=asset_family_research_profile,
            subsystem_register=list(m50.get("subsystem_register", []) or []),
            source_register=source_register,
        )
        permit_signal_register = build_permit_signal_register(
            target_definition=target_definition,
            asset_family_research_profile=asset_family_research_profile,
            source_register=source_register,
        )
        regulatory_constraint_register = build_regulatory_constraint_register(
            asset_family_research_profile=asset_family_research_profile,
            regulatory_physics_register=regulatory_physics_register,
        )
        finance_physics_dependency_register = build_finance_physics_dependency_register(
            asset_family_research_profile=asset_family_research_profile,
            fair_comparison_profile=dict(m51.get("fair_comparison_profile", {}) or {}),
            cross_layer_congruence_register=list(m51.get("cross_layer_congruence_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
        )
        cost_driver_dependency_register = build_cost_driver_dependency_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_value_flow_register=list(m50.get("operational_value_flow_register", []) or []),
            power_quality_hypothesis_register=list(m52.get("power_quality_hypothesis_register", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
        )
        capital_logic_register = build_capital_logic_register(
            asset_family_research_profile=asset_family_research_profile,
            regulatory_constraint_register=regulatory_constraint_register,
            finance_physics_dependency_register=finance_physics_dependency_register,
        )
        financial_exposure_type_register = build_financial_exposure_type_register(
            asset_family_research_profile=asset_family_research_profile,
            finance_physics_dependency_register=finance_physics_dependency_register,
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            comparison_not_yet_valid_register=list(m51.get("comparison_not_yet_valid_register", []) or []),
            regulatory_constraint_register=regulatory_constraint_register,
            structural_correlation_graph=list(m51.get("structural_correlation_graph", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            hardware_minimality_register=list(m52.get("hardware_minimality_register", []) or []),
        )
        underwriting_misread_register = build_underwriting_misread_register(
            financial_exposure_type_register=financial_exposure_type_register,
        )
        value_leakage_register = build_value_leakage_register(
            financial_exposure_type_register=financial_exposure_type_register,
        )
        climate_location_context_register = build_climate_location_context_register(
            target_definition=target_definition,
            asset_family_research_profile=asset_family_research_profile,
            source_register=source_register,
        )
        utility_tariff_context_register = build_utility_tariff_context_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            source_register=source_register,
        )
        culture_execution_proxy_register = build_culture_execution_proxy_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            source_register=source_register,
        )
        skill_financial_exposure_register = build_registry_financial_exposure_register(
            financial_exposure_type_register=financial_exposure_type_register,
        )
        authoritative_financial_exposure_register = (
            skill_financial_exposure_register
            if skill_financial_exposure_register
            else financial_exposure_type_register
        )
        financial_exposure_authority_state = (
            "skill_primary"
            if skill_financial_exposure_register
            else "legacy_primary"
        )
        skill_financial_exposure_summary = {
            "total": len(skill_financial_exposure_register),
            "governed_categories": sorted(
                {
                    str(row.get("governed_exposure_category", "")).strip()
                    for row in skill_financial_exposure_register
                    if str(row.get("governed_exposure_category", "")).strip()
                }
            ),
            "authority_state": financial_exposure_authority_state,
        }
        # V5 P2: canonical Phase 6 unit (Master Doc §4) — projection of
        # regulatory_constraint_register into compliance_applicability_case
        # with explicit applicability_state ladder.
        compliance_applicability_case_register = to_compliance_applicability_case_register(
            regulatory_constraint_register
        )
        return {
            "regulatory_physics_register": regulatory_physics_register,
            "permit_signal_register": permit_signal_register,
            "regulatory_constraint_register": regulatory_constraint_register,
            "compliance_applicability_case_register": compliance_applicability_case_register,
            "finance_physics_dependency_register": finance_physics_dependency_register,
            "cost_driver_dependency_register": cost_driver_dependency_register,
            "capital_logic_register": capital_logic_register,
            "financial_exposure_type_register": financial_exposure_type_register,
            "skill_financial_exposure_register": skill_financial_exposure_register,
            "authoritative_financial_exposure_register": authoritative_financial_exposure_register,
            "financial_exposure_authority_state": financial_exposure_authority_state,
            "skill_financial_exposure_summary": skill_financial_exposure_summary,
            "underwriting_misread_register": underwriting_misread_register,
            "value_leakage_register": value_leakage_register,
            "climate_location_context_register": climate_location_context_register,
            "utility_tariff_context_register": utility_tariff_context_register,
            "culture_execution_proxy_register": culture_execution_proxy_register,
            "regulatory_physics_count": len(regulatory_physics_register),
            "permit_signal_count": len(permit_signal_register),
            "finance_physics_dependency_count": len(finance_physics_dependency_register),
            "capital_logic_count": len(capital_logic_register),
            "financial_exposure_type_count": len(financial_exposure_type_register),
            "skill_financial_exposure_count": len(skill_financial_exposure_register),
            "underwriting_misread_count": len(underwriting_misread_register),
            "value_leakage_count": len(value_leakage_register),
            "climate_context_count": len(climate_location_context_register),
            "culture_proxy_count": len(culture_execution_proxy_register),
        }
