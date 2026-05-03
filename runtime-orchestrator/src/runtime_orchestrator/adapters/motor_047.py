from __future__ import annotations

from typing import Any

from ..executive_thesis import build_executive_thesis
from .base import BaseMotorAdapter


class Motor047Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_047"

    @property
    def input_motor_ids(self) -> list[str]:
        return [
            "motor_014",
            "motor_033",
            "motor_034",
            "motor_037",
            "motor_038",
            "motor_040",
            "motor_041",
            "motor_043",
            "motor_044",
            "motor_045",
            "motor_046",
            "motor_051",
            "motor_052",
            "motor_053",
            "motor_054",
        ]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m14 = inputs.get("motor_014", {}) if isinstance(inputs.get("motor_014", {}), dict) else {}
        m33 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m34 = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        m51 = inputs.get("motor_051", {}) if isinstance(inputs.get("motor_051", {}), dict) else {}
        m52 = inputs.get("motor_052", {}) if isinstance(inputs.get("motor_052", {}), dict) else {}
        m53 = inputs.get("motor_053", {}) if isinstance(inputs.get("motor_053", {}), dict) else {}
        m54 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}
        thesis = build_executive_thesis(
            system_abstraction=dict(inputs.get("motor_037", {}).get("system_abstraction", {}) or {}),
            canonical_problem_frame=dict(m34.get("canonical_problem_frame", {}) or {}),
            problem_framing_register=list(inputs.get("motor_041", {}).get("problem_framing_register", []) or []),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            scenario_register=list(m14.get("scenario_space", []) or []),
            structural_financial_exposure_register=list(inputs.get("motor_045", {}).get("structural_financial_exposure_register", []) or []),
            competitive_comparison_register=list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
            minimum_evidence_for_discrimination_register=list(inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or []),
            expanded_structural_tad_action_register=list(m33.get("expanded_structural_tad_action_register", []) or []),
            claim_contract_register=list(m34.get("claim_contract_register", []) or []),
            report_output_mode_classifier_table=list(m34.get("report_output_mode_classifier_table", []) or []),
            invalid_problem_frame_register=list(m51.get("invalid_problem_frame_register", []) or []),
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            cross_layer_congruence_register=list(m51.get("cross_layer_congruence_register", []) or []),
            loss_pattern_hypothesis_register=list(m52.get("loss_pattern_hypothesis_register", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            regulatory_physics_register=list(m53.get("regulatory_physics_register", []) or []),
            finance_physics_dependency_register=list(m53.get("finance_physics_dependency_register", []) or []),
            strategic_gold_nugget_register=list(
                m54.get("gold_nugget_register", m54.get("strategic_gold_nugget_register", [])) or []
            ),
            gold_nugget_strength_register=list(m54.get("gold_nugget_strength_register", []) or []),
            congruence_action_priority_register=list(m54.get("congruence_action_priority_register", []) or []),
        )
        return {
            "executive_thesis": thesis,
            "dominant_contradiction": str(thesis.get("dominant_contradiction", "")).strip(),
            "supporting_mode_count": len(list(thesis.get("supporting_modes", []) or [])),
            "client_facing_action_count": len(list(thesis.get("top_actions", []) or [])),
        }
