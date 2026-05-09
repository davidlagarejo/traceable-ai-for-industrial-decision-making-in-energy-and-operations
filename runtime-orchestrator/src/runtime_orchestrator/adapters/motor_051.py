from __future__ import annotations

from typing import Any

from ..congruence_intelligence.congruence_engine import (
    build_cross_layer_congruence_register,
    build_invalid_problem_frame_register,
)
from ..congruence_intelligence.correlation_engine import build_structural_correlation_register
from ..congruence_intelligence.correlation_engine import (
    build_correlation_priority_register,
    build_gold_nugget_candidate_register,
    build_structural_correlation_graph,
)
from ..congruence_intelligence.fair_comparison import (
    build_comparison_validity_register,
    build_invalid_comparison_risk_register,
)
from ..congruence_intelligence.gap_taxonomy import (
    build_evidence_need_class_register,
    extend_gap_taxonomy_with_comparison_risks,
)
from ..congruence_intelligence.peer_normalization import (
    build_fair_comparison_profile,
    build_normalization_requirements_register,
)
from ..congruence_intelligence.peer_set_builder import (
    build_comparison_blocker_register,
    build_comparison_not_yet_valid_register,
    build_peer_candidate_family_register,
    build_peer_requirement_register,
)
from .base import BaseMotorAdapter


class Motor051Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_051"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_049", "motor_050"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m49 = dict(inputs.get("motor_049", {}) or {})
        m50 = dict(inputs.get("motor_050", {}) or {})

        fair_comparison_profile = build_fair_comparison_profile(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            operational_intake_pack=dict(m49.get("operational_intake_pack", {}) or {}),
            process_map=dict(m50.get("process_map", {}) or {}),
            control_boundary_map=list(m50.get("control_boundary_map", []) or []),
            local_evidence_binding_register=list(m49.get("local_evidence_binding_register", []) or []),
        )
        normalization_requirements_register = build_normalization_requirements_register(
            fair_comparison_profile=fair_comparison_profile,
        )
        peer_requirement_register = build_peer_requirement_register(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            fair_comparison_profile=fair_comparison_profile,
            operational_intake_pack=dict(m49.get("operational_intake_pack", {}) or {}),
            dynamic_intake_question_register=list(m49.get("dynamic_intake_question_register", []) or []),
        )
        peer_candidate_family_register = build_peer_candidate_family_register(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            peer_requirement_register=peer_requirement_register,
        )
        comparison_validity_register = build_comparison_validity_register(
            fair_comparison_profile=fair_comparison_profile,
            normalization_requirements_register=normalization_requirements_register,
        )
        comparison_blocker_register = build_comparison_blocker_register(
            peer_requirement_register=peer_requirement_register,
            comparison_validity_register=comparison_validity_register,
        )
        comparison_not_yet_valid_register = build_comparison_not_yet_valid_register(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            comparison_blocker_register=comparison_blocker_register,
        )
        invalid_comparison_risk_register = build_invalid_comparison_risk_register(
            fair_comparison_profile=fair_comparison_profile,
            comparison_validity_register=comparison_validity_register,
        )
        structural_correlation_register = build_structural_correlation_register(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            operational_intake_pack=dict(m49.get("operational_intake_pack", {}) or {}),
            subsystem_register=list(m50.get("subsystem_register", []) or []),
            control_boundary_map=list(m50.get("control_boundary_map", []) or []),
        )
        structural_correlation_graph = build_structural_correlation_graph(
            structural_correlation_register=structural_correlation_register,
        )
        correlation_priority_register = build_correlation_priority_register(
            structural_correlation_graph=structural_correlation_graph,
        )
        gold_nugget_candidate_register = build_gold_nugget_candidate_register(
            structural_correlation_graph=structural_correlation_graph,
        )
        cross_layer_congruence_register = build_cross_layer_congruence_register(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            operational_intake_pack=dict(m49.get("operational_intake_pack", {}) or {}),
            fair_comparison_profile=fair_comparison_profile,
            structural_correlation_register=structural_correlation_register,
            structural_correlation_graph=structural_correlation_graph,
            control_boundary_map=list(m50.get("control_boundary_map", []) or []),
            maintenance_dependency_map=list(m50.get("maintenance_dependency_map", []) or []),
        )
        invalid_problem_frame_register = build_invalid_problem_frame_register(
            asset_family_research_profile=dict(m49.get("asset_family_research_profile", {}) or {}),
            fair_comparison_profile=fair_comparison_profile,
        )
        gap_taxonomy_register = extend_gap_taxonomy_with_comparison_risks(
            gap_taxonomy_register=list(m49.get("gap_taxonomy_register", []) or []),
            invalid_comparison_risk_register=invalid_comparison_risk_register,
        )
        evidence_need_class_register = build_evidence_need_class_register(
            gap_taxonomy_register=gap_taxonomy_register,
        )
        rival_hypothesis_register = list(m49.get("rival_hypothesis_register", []) or [])
        hypothesis_discrimination_register = list(m49.get("hypothesis_discrimination_register", []) or [])
        claim_impact_register = list(m49.get("claim_impact_register", []) or [])
        # R-58: when local comparison is not yet valid (benchmark unavailable
        # or normalization gap), expose an archetypal-peer admissibility view.
        # This lets the composer render bounded peer comparison under
        # ARCHETYPAL_PRIOR instead of leaving "Peer Comparison" empty (which
        # is the artefact visible in the Sunrise PDF cap. 8).
        archetypal_peer_admissibility_register: list[dict[str, Any]] = []
        for row in comparison_not_yet_valid_register:
            if not isinstance(row, dict):
                continue
            archetypal_peer_admissibility_register.append({
                "comparison_basis": str(row.get("comparison_basis", "")).strip(),
                "blocker": str(row.get("blocker", "")).strip(),
                "archetypal_admissibility": "allowed_under_archetypal_prior",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "allowed_use": [
                    "Bounded peer warning",
                    "Structural pattern framing",
                ],
                "prohibited_use": [
                    "Peer superiority claim",
                    "Transferable ROI from peer",
                    "Local waste diagnosis from invalid comparison",
                ],
                "falsification_condition": (
                    "Asset-specific normalization evidence proves the peer "
                    "frame is not transferable."
                ),
            })
        return {
            "fair_comparison_profile": fair_comparison_profile,
            "comparison_validity_register": comparison_validity_register,
            "normalization_requirements_register": normalization_requirements_register,
            "peer_requirement_register": peer_requirement_register,
            "peer_candidate_family_register": peer_candidate_family_register,
            "comparison_blocker_register": comparison_blocker_register,
            "comparison_not_yet_valid_register": comparison_not_yet_valid_register,
            "invalid_comparison_risk_register": invalid_comparison_risk_register,
            "structural_correlation_register": structural_correlation_register,
            "structural_correlation_graph": structural_correlation_graph,
            "correlation_priority_register": correlation_priority_register,
            "gold_nugget_candidate_register": gold_nugget_candidate_register,
            "cross_layer_congruence_register": cross_layer_congruence_register,
            "invalid_problem_frame_register": invalid_problem_frame_register,
            "gap_taxonomy_register": gap_taxonomy_register,
            "evidence_need_class_register": evidence_need_class_register,
            "rival_hypothesis_register": rival_hypothesis_register,
            "hypothesis_discrimination_register": hypothesis_discrimination_register,
            "claim_impact_register": claim_impact_register,
            "comparison_validity_count": len(comparison_validity_register),
            "peer_requirement_count": len(peer_requirement_register),
            "peer_candidate_family_count": len(peer_candidate_family_register),
            "comparison_blocker_count": len(comparison_blocker_register),
            "comparison_not_yet_valid_count": len(comparison_not_yet_valid_register),
            "structural_correlation_count": len(structural_correlation_register),
            "structural_correlation_graph_count": len(structural_correlation_graph),
            "correlation_priority_count": len(correlation_priority_register),
            "gold_nugget_candidate_count": len(gold_nugget_candidate_register),
            "cross_layer_congruence_count": len(cross_layer_congruence_register),
            "invalid_problem_frame_count": len(invalid_problem_frame_register),
            "gap_taxonomy_count": len(gap_taxonomy_register),
            "evidence_need_class_count": len(evidence_need_class_register),
            "rival_hypothesis_count": len(rival_hypothesis_register),
            "hypothesis_discrimination_count": len(hypothesis_discrimination_register),
            "claim_impact_count": len(claim_impact_register),
            "archetypal_peer_admissibility_register": archetypal_peer_admissibility_register,
            "archetypal_peer_admissibility_count": len(archetypal_peer_admissibility_register),
        }
