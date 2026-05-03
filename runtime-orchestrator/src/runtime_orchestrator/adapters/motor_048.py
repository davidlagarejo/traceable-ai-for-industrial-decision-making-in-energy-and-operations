from __future__ import annotations

from typing import Any

from ..report_compression import build_report_compression
from .base import BaseMotorAdapter


class Motor048Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_048"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_034", "motor_047", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m34 = inputs.get("motor_034", {}) if isinstance(inputs.get("motor_034", {}), dict) else {}
        m47 = inputs.get("motor_047", {}) if isinstance(inputs.get("motor_047", {}), dict) else {}
        m54 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}
        compression = build_report_compression(
            executive_thesis=dict(m47.get("executive_thesis", {}) or {}),
            canonical_problem_frame=dict(m34.get("canonical_problem_frame", {}) or {}),
            claim_contract_register=list(m34.get("claim_contract_register", []) or []),
            report_output_mode_classifier_table=list(m34.get("report_output_mode_classifier_table", []) or []),
            congruence_claim_contract_register=list(m54.get("congruence_claim_contract_register", []) or []),
        )
        return {
            "main_report_outline": {
                "visible_report_mode": compression.get("visible_report_mode", ""),
                "dominant_lens": compression.get("dominant_lens", ""),
                "supporting_modes": list(compression.get("supporting_modes", []) or []),
                "max_primary_sections": int(compression.get("max_primary_sections", 0) or 0),
                "compression_state": compression.get("compression_state", ""),
                "sections": list(compression.get("sections", []) or []),
                "body_section_titles": list(compression.get("body_section_titles", []) or []),
                "congruence_visible_signal_count": len(list(compression.get("congruence_visibility_register", []) or [])),
            },
            "appendix_map": list(compression.get("appendix_map", []) or []),
            "section_authority_map": dict(compression.get("section_authority_map", {}) or {}),
            "deduplicated_claim_map": dict(compression.get("deduplicated_claim_map", {}) or {}),
            "client_facing_tad": dict(compression.get("client_facing_tad", {}) or {}),
            "congruence_visibility_register": list(compression.get("congruence_visibility_register", []) or []),
            "section_demotions_register": list(compression.get("section_demotions_register", []) or []),
            "body_to_appendix_justification_map": dict(compression.get("body_to_appendix_justification_map", {}) or {}),
            "prompt_block_mapping_register": list(compression.get("prompt_block_mapping_register", []) or []),
            "compression_decision_log": list(compression.get("compression_decision_log", []) or []),
        }
