from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..congruence_intelligence import (
    RESEARCH_LIBRARY_VERSION,
    build_asset_boundary_resolution_register,
    build_asset_family_research_dossier,
    build_authoritative_source_acquisition_trace,
    build_asset_family_research_profile,
    build_authoritative_source_trace_register,
    build_binding_sufficiency_reason_register,
    build_binding_upgrade_register,
    build_case_fingerprint,
    build_control_boundary_evidence_register,
    build_entity_conflict_register,
    build_entity_resolution_register,
    build_family_research_coverage_register,
    build_family_research_gap_register,
    build_family_source_gap_register,
    derive_family_source_refresh_state,
    derive_entity_resolution_state,
    build_local_evidence_binding_register,
    build_local_truth_confidence_register,
    build_maintenance_proof_evidence_register,
    build_operational_intake_pack,
    build_operational_bounding_scorecard,
    build_owner_operator_tenant_resolution_register,
    build_owner_operator_tenant_responsibility_register,
    build_permit_to_system_register,
    build_promotion_blocker_register,
    build_regulated_process_scope_register,
    build_raw_local_evidence_source_register,
    build_authority_precedence_register,
    build_conflict_resolution_outcome_register,
    build_structured_local_source_register,
    build_source_conflict_register,
    build_tariff_exposure_register,
    build_utility_charge_breakdown_register,
    build_downgrade_condition_register,
    build_escalation_condition_register,
    build_minimum_sufficient_evidence_register,
    build_decision_context_register,
    build_dynamic_intake_question_register,
    build_congruence_case_state,
    build_intake_priority_register,
    build_claim_impact_register,
    build_dominant_hypothesis_register,
    build_evidence_need_class_register,
    build_gap_taxonomy_register,
    build_hypothesis_claim_blocker_register,
    build_hypothesis_discrimination_register,
    build_hypothesis_evidence_gap_register,
    build_question_candidate_register,
    build_question_normalization_register,
    build_required_from_register,
    build_rival_hypothesis_register,
    build_rival_hypothesis_seed_register,
    build_stop_condition_register,
    build_truncated_question_register,
    merge_source_registers,
)
from .base import BaseMotorAdapter


def _synchronize_diligence_pack_register(operational_intake_pack: dict[str, Any]) -> None:
    diligence_pack_register = list(operational_intake_pack.get("diligence_pack_register", []) or [])
    if not diligence_pack_register:
        return

    for row in diligence_pack_register:
        pack_name = str(row.get("pack_name", "")).strip()
        if not pack_name:
            continue
        pack = operational_intake_pack.get(pack_name)
        if not isinstance(pack, dict):
            continue
        if "current_state" in pack:
            row["current_state"] = pack.get("current_state", "")
        if "present_source_families" in pack:
            row["present_source_families"] = list(pack.get("present_source_families", []) or [])
        if "binding_needed" in pack:
            row["binding_needed"] = list(pack.get("binding_needed", []) or [])

    operational_intake_pack["diligence_pack_register"] = diligence_pack_register


class Motor049Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_049"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_012", "motor_028"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        m07 = dict(inputs.get("motor_007", {}) or {})
        m12 = dict(inputs.get("motor_012", {}) or {})
        m28 = dict(inputs.get("motor_028", {}) or {})

        facility_prior = dict(m12.get("facility_prior", {}) or {})
        target_definition = (
            facility_prior.get("target_definition")
            or m07.get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )
        target_classification_object = dict(m07.get("target_classification_object", {}) or {})
        asset_field_register = list(
            m12.get("asset_field_register", [])
            or facility_prior.get("asset_field_register", [])
            or []
        )
        declared_input_downgrade_register = list(
            m12.get("declared_input_downgrade_register", [])
            or facility_prior.get("declared_input_downgrade_register", [])
            or []
        )
        upstream_source_register = list(m28.get("source_register", []) or [])
        structured_local_source_register = build_structured_local_source_register(
            pipeline=pipeline,
            target_definition=target_definition,
        )
        raw_local_source_register = build_raw_local_evidence_source_register(
            pipeline=pipeline,
            target_definition=target_definition,
        )
        source_register = merge_source_registers(
            upstream_source_register,
            structured_local_source_register,
            raw_local_source_register,
        )
        authority_precedence_register = build_authority_precedence_register(
            source_register=source_register,
        )
        source_conflict_register = build_source_conflict_register(
            source_register=source_register,
        )
        conflict_resolution_outcome_register = build_conflict_resolution_outcome_register(
            source_conflict_register=source_conflict_register,
        )
        enriched_data = dict(m28.get("enriched_data", {}) or {})
        search_budget_register = list(m28.get("search_budget_register", []) or [])
        search_attempt_ledger = list(m28.get("search_attempt_ledger", []) or [])
        search_attempt_outcome_register = list(m28.get("search_attempt_outcome_register", []) or [])
        search_exhaustion_register = list(m28.get("search_exhaustion_register", []) or [])
        discovery_need_register = list(m28.get("discovery_need_register", []) or [])
        search_family_execution_plan = list(m28.get("search_family_execution_plan", []) or [])
        accepted_evidence_type_register = list(m28.get("accepted_evidence_type_register", []) or [])
        discovery_stop_condition_register = list(m28.get("discovery_stop_condition_register", []) or [])
        next_best_search_register = list(m28.get("next_best_search_register", []) or [])
        search_target_priority_register = list(m28.get("search_target_priority_register", []) or [])
        search_success_effect_register = list(m28.get("search_success_effect_register", []) or [])
        search_failure_effect_register = list(m28.get("search_failure_effect_register", []) or [])
        upstream_stop_condition_register = list(m28.get("stop_condition_register", []) or [])
        upstream_downgrade_condition_register = list(m28.get("downgrade_condition_register", []) or [])
        upstream_escalation_condition_register = list(m28.get("escalation_condition_register", []) or [])
        upstream_minimum_sufficient_evidence_register = list(m28.get("minimum_sufficient_evidence_register", []) or [])
        case_fingerprint = build_case_fingerprint(target_definition=target_definition)
        entity_resolution_register = build_entity_resolution_register(
            target_definition=target_definition,
            source_register=source_register,
        )
        entity_conflict_register = build_entity_conflict_register(
            entity_resolution_register=entity_resolution_register,
        )
        asset_boundary_resolution_register = build_asset_boundary_resolution_register(
            target_definition=target_definition,
            entity_resolution_register=entity_resolution_register,
            entity_conflict_register=entity_conflict_register,
        )
        owner_operator_tenant_resolution_register = build_owner_operator_tenant_resolution_register(
            target_definition=target_definition,
            entity_resolution_register=entity_resolution_register,
        )
        entity_resolution_state = derive_entity_resolution_state(
            entity_resolution_register=entity_resolution_register,
            entity_conflict_register=entity_conflict_register,
            asset_boundary_resolution_register=asset_boundary_resolution_register,
        )

        asset_family_research_profile = build_asset_family_research_profile(
            target_definition=target_definition,
            target_classification_object=target_classification_object,
            facility_prior=facility_prior,
            asset_field_register=asset_field_register,
            source_register=source_register,
        )
        asset_family_research_dossier = build_asset_family_research_dossier(
            asset_family_research_profile=asset_family_research_profile,
        )
        family_research_coverage_register = build_family_research_coverage_register(
            asset_family_research_dossier=asset_family_research_dossier,
        )
        family_research_gap_register = build_family_research_gap_register(
            asset_family_research_dossier=asset_family_research_dossier,
            family_research_coverage_register=family_research_coverage_register,
        )
        authoritative_source_trace_register = build_authoritative_source_trace_register(
            asset_family_research_profile=asset_family_research_profile,
            source_register=source_register,
        )
        authoritative_source_acquisition_trace = build_authoritative_source_acquisition_trace(
            asset_family_research_dossier=asset_family_research_dossier,
            source_register=source_register,
        )
        family_source_gap_register = build_family_source_gap_register(
            authoritative_source_acquisition_trace=authoritative_source_acquisition_trace,
        )
        family_source_refresh_state = derive_family_source_refresh_state(
            authoritative_source_acquisition_trace=authoritative_source_acquisition_trace,
        )
        preliminary_local_evidence_binding_register = build_local_evidence_binding_register(
            asset_family_research_profile=asset_family_research_profile,
            target_classification_object=target_classification_object,
            source_register=source_register,
        )
        operational_intake_pack = build_operational_intake_pack(
            asset_family_research_profile=asset_family_research_profile,
            target_definition=target_definition,
            target_classification_object=target_classification_object,
            facility_prior=facility_prior,
            asset_field_register=asset_field_register,
            source_register=source_register,
            local_evidence_binding_register=preliminary_local_evidence_binding_register,
        )
        utility_charge_breakdown_register = build_utility_charge_breakdown_register(
            asset_family_research_profile=asset_family_research_profile,
            source_register=source_register,
            enriched_data=enriched_data,
        )
        tariff_exposure_register = build_tariff_exposure_register(
            asset_family_research_profile=asset_family_research_profile,
            source_register=source_register,
            enriched_data=enriched_data,
        )
        permit_to_system_register = build_permit_to_system_register(
            asset_family_research_profile=asset_family_research_profile,
            source_register=source_register,
            enriched_data=enriched_data,
        )
        regulated_process_scope_register = build_regulated_process_scope_register(
            asset_family_research_profile=asset_family_research_profile,
            permit_to_system_register=permit_to_system_register,
        )
        control_boundary_evidence_register = build_control_boundary_evidence_register(
            asset_family_research_profile=asset_family_research_profile,
            target_definition=target_definition,
            source_register=source_register,
            enriched_data=enriched_data,
        )
        owner_operator_tenant_responsibility_register = build_owner_operator_tenant_responsibility_register(
            asset_family_research_profile=asset_family_research_profile,
            target_definition=target_definition,
            control_boundary_evidence_register=control_boundary_evidence_register,
        )
        maintenance_proof_evidence_register = build_maintenance_proof_evidence_register(
            asset_family_research_profile=asset_family_research_profile,
            source_register=source_register,
            enriched_data=enriched_data,
        )
        operational_intake_pack["utility_charge_breakdown_register"] = utility_charge_breakdown_register
        operational_intake_pack["tariff_exposure_register"] = tariff_exposure_register
        operational_intake_pack["permit_to_system_register"] = permit_to_system_register
        operational_intake_pack["regulated_process_scope_register"] = regulated_process_scope_register
        operational_intake_pack["control_boundary_evidence_register"] = control_boundary_evidence_register
        operational_intake_pack["entity_resolution_register"] = entity_resolution_register
        operational_intake_pack["entity_conflict_register"] = entity_conflict_register
        operational_intake_pack["asset_boundary_resolution_register"] = asset_boundary_resolution_register
        operational_intake_pack["owner_operator_tenant_resolution_register"] = owner_operator_tenant_resolution_register
        operational_intake_pack["authority_precedence_register"] = authority_precedence_register
        operational_intake_pack["source_conflict_register"] = source_conflict_register
        operational_intake_pack["conflict_resolution_outcome_register"] = conflict_resolution_outcome_register
        operational_intake_pack["owner_operator_tenant_responsibility_register"] = owner_operator_tenant_responsibility_register
        operational_intake_pack["maintenance_proof_evidence_register"] = maintenance_proof_evidence_register
        operational_intake_pack["search_budget_register"] = search_budget_register
        operational_intake_pack["search_attempt_ledger"] = search_attempt_ledger
        operational_intake_pack["search_attempt_outcome_register"] = search_attempt_outcome_register
        operational_intake_pack["search_exhaustion_register"] = search_exhaustion_register
        operational_intake_pack["discovery_need_register"] = discovery_need_register
        operational_intake_pack["search_family_execution_plan"] = search_family_execution_plan
        operational_intake_pack["accepted_evidence_type_register"] = accepted_evidence_type_register
        operational_intake_pack["discovery_stop_condition_register"] = discovery_stop_condition_register
        operational_intake_pack["next_best_search_register"] = next_best_search_register
        operational_intake_pack["search_target_priority_register"] = search_target_priority_register
        operational_intake_pack["search_success_effect_register"] = search_success_effect_register
        operational_intake_pack["search_failure_effect_register"] = search_failure_effect_register
        operational_intake_pack["declared_input_downgrade_register"] = declared_input_downgrade_register
        operational_intake_pack["case_fingerprint"] = case_fingerprint
        operational_intake_pack["entity_resolution_state"] = entity_resolution_state

        extended_sources = dict(enriched_data.get("extended_sources", {}) or {})

        def _has_enriched_records(*source_families: str) -> bool:
            for source_family in source_families:
                payload = dict(extended_sources.get(source_family, {}) or {})
                if list(payload.get("records", []) or []):
                    return True
            return False

        if utility_charge_breakdown_register:
            operational_intake_pack["utility_and_tariff_pack"]["current_state"] = "evidenced"
            operational_intake_pack["utility_bill_pack"]["current_state"] = (
                "evidenced" if _has_enriched_records("utility_bill_record") else "partially_evidenced"
            )
        if tariff_exposure_register:
            operational_intake_pack["utility_tariff_pack"]["current_state"] = (
                "evidenced" if _has_enriched_records("utility_tariff_record") else "partially_evidenced"
            )
        if control_boundary_evidence_register:
            operational_intake_pack["control_boundary_pack"]["current_state"] = "evidenced" if len(control_boundary_evidence_register) >= 2 else "partially_evidenced"
            if any(str(row.get("source_family", "")).strip() == "lease_matrix_record" for row in control_boundary_evidence_register):
                operational_intake_pack["lease_responsibility_pack"]["current_state"] = (
                    "evidenced" if _has_enriched_records("lease_matrix_record") else "partially_evidenced"
                )
            if any(str(row.get("source_family", "")).strip() in {"submetering_record", "meter_interval_record"} for row in control_boundary_evidence_register):
                operational_intake_pack["metering_boundary_pack"]["current_state"] = (
                    "evidenced"
                    if _has_enriched_records("submetering_record", "meter_interval_record")
                    else "partially_evidenced"
                )
        if maintenance_proof_evidence_register:
            cmms_state = str(operational_intake_pack.get("cmms_or_workorder_pack", {}).get("current_state", "")).strip()
            cmms_evidence_present = any(
                str(row.get("source_family", "")).strip() == "cmms_record"
                for row in maintenance_proof_evidence_register
            )
            operational_intake_pack["maintenance_maturity_pack"]["current_state"] = (
                "evidenced"
                if len(maintenance_proof_evidence_register) >= 2 and (cmms_state == "evidenced" or cmms_evidence_present)
                else "partially_evidenced"
            )
            operational_intake_pack["maintenance_proof_pack"]["current_state"] = (
                "evidenced"
                if _has_enriched_records("maintenance_contract_record", "maintenance_log_record")
                else "partially_evidenced"
            )
            if any(str(row.get("source_family", "")).strip() == "cmms_record" for row in maintenance_proof_evidence_register):
                operational_intake_pack["cmms_or_workorder_pack"]["current_state"] = (
                    "evidenced" if _has_enriched_records("cmms_record") else "partially_evidenced"
                )
        _synchronize_diligence_pack_register(operational_intake_pack)
        stop_condition_register = build_stop_condition_register(
            discovery_need_register=discovery_need_register,
            next_best_search_register=next_best_search_register,
            search_budget_register=search_budget_register,
            operational_intake_pack=operational_intake_pack,
        )
        downgrade_condition_register = build_downgrade_condition_register(
            stop_condition_register=stop_condition_register,
        )
        escalation_condition_register = build_escalation_condition_register(
            stop_condition_register=stop_condition_register,
        )
        minimum_sufficient_evidence_register = build_minimum_sufficient_evidence_register(
            stop_condition_register=stop_condition_register,
        )
        initial_congruence_case_state = build_congruence_case_state(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            target_definition=target_definition,
        )
        rival_hypothesis_seed_register = build_rival_hypothesis_seed_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            congruence_case_state=initial_congruence_case_state,
        )
        dominant_hypothesis_register = build_dominant_hypothesis_register(
            rival_hypothesis_seed_register=rival_hypothesis_seed_register,
        )
        hypothesis_evidence_gap_register = build_hypothesis_evidence_gap_register(
            rival_hypothesis_seed_register=rival_hypothesis_seed_register,
            stop_condition_register=stop_condition_register,
            next_best_search_register=next_best_search_register,
        )
        hypothesis_claim_blocker_register = build_hypothesis_claim_blocker_register(
            rival_hypothesis_seed_register=rival_hypothesis_seed_register,
        )
        congruence_case_state = {
            **initial_congruence_case_state,
            "active_rival_hypotheses": [
                str(row.get("hypothesis_label", "")).strip()
                for row in rival_hypothesis_seed_register
                if str(row.get("hypothesis_label", "")).strip()
            ],
            "dominant_hypothesis_ids": [
                str(row.get("hypothesis_id", "")).strip()
                for row in dominant_hypothesis_register
                if str(row.get("hypothesis_id", "")).strip()
            ],
            "dominant_hypothesis_labels": [
                str(row.get("hypothesis_label", "")).strip()
                for row in dominant_hypothesis_register
                if str(row.get("hypothesis_label", "")).strip()
            ],
            "hypothesis_claim_blockers": [
                str(row.get("blocked_claim", "")).strip()
                for row in hypothesis_claim_blocker_register
                if str(row.get("blocked_claim", "")).strip()
            ],
        }
        decision_context_register = build_decision_context_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            congruence_case_state=congruence_case_state,
            target_definition=target_definition,
        )
        question_candidate_register = build_question_candidate_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            stop_condition_register=stop_condition_register,
            congruence_case_state=congruence_case_state,
            decision_context_register=decision_context_register,
            target_definition=target_definition,
        )
        question_normalization_register = build_question_normalization_register(
            asset_family_research_profile=asset_family_research_profile,
            question_candidate_register=question_candidate_register,
        )
        dynamic_intake_question_register = build_dynamic_intake_question_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            stop_condition_register=stop_condition_register,
            congruence_case_state=congruence_case_state,
            target_definition=target_definition,
        )
        truncated_question_register = build_truncated_question_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
            discovery_need_register=discovery_need_register,
            stop_condition_register=stop_condition_register,
            congruence_case_state=congruence_case_state,
            target_definition=target_definition,
        )
        required_from_register = build_required_from_register(
            dynamic_intake_question_register=dynamic_intake_question_register,
        )
        intake_priority_register = build_intake_priority_register(
            dynamic_intake_question_register=dynamic_intake_question_register,
        )
        rival_hypothesis_register = build_rival_hypothesis_register(
            dynamic_intake_question_register=dynamic_intake_question_register,
            stop_condition_register=stop_condition_register,
            next_best_search_register=next_best_search_register,
        )
        hypothesis_discrimination_register = build_hypothesis_discrimination_register(
            dynamic_intake_question_register=dynamic_intake_question_register,
            stop_condition_register=stop_condition_register,
            next_best_search_register=next_best_search_register,
        )
        claim_impact_register = build_claim_impact_register(
            dynamic_intake_question_register=dynamic_intake_question_register,
            stop_condition_register=stop_condition_register,
        )
        gap_taxonomy_register = build_gap_taxonomy_register(
            dynamic_intake_question_register=dynamic_intake_question_register,
            promotion_blocker_register=[],
            claim_impact_register=claim_impact_register,
        )
        evidence_need_class_register = build_evidence_need_class_register(
            gap_taxonomy_register=gap_taxonomy_register,
        )
        operational_intake_pack["stop_condition_register"] = stop_condition_register
        operational_intake_pack["downgrade_condition_register"] = downgrade_condition_register
        operational_intake_pack["escalation_condition_register"] = escalation_condition_register
        operational_intake_pack["minimum_sufficient_evidence_register"] = minimum_sufficient_evidence_register
        operational_intake_pack["congruence_case_state"] = congruence_case_state
        operational_intake_pack["rival_hypothesis_seed_register"] = rival_hypothesis_seed_register
        operational_intake_pack["dominant_hypothesis_register"] = dominant_hypothesis_register
        operational_intake_pack["hypothesis_evidence_gap_register"] = hypothesis_evidence_gap_register
        operational_intake_pack["hypothesis_claim_blocker_register"] = hypothesis_claim_blocker_register
        operational_intake_pack["decision_context_register"] = decision_context_register
        operational_intake_pack["question_candidate_register"] = question_candidate_register
        operational_intake_pack["question_normalization_register"] = question_normalization_register
        operational_intake_pack["dynamic_intake_question_register"] = dynamic_intake_question_register
        operational_intake_pack["truncated_question_register"] = truncated_question_register
        operational_intake_pack["required_from_register"] = required_from_register
        operational_intake_pack["intake_priority_register"] = intake_priority_register
        operational_intake_pack["rival_hypothesis_register"] = rival_hypothesis_register
        operational_intake_pack["hypothesis_discrimination_register"] = hypothesis_discrimination_register
        operational_intake_pack["claim_impact_register"] = claim_impact_register
        operational_intake_pack["gap_taxonomy_register"] = gap_taxonomy_register
        operational_intake_pack["evidence_need_class_register"] = evidence_need_class_register
        local_evidence_binding_register = build_local_evidence_binding_register(
            asset_family_research_profile=asset_family_research_profile,
            target_classification_object=target_classification_object,
            source_register=source_register,
            operational_intake_pack=operational_intake_pack,
            control_boundary_evidence_register=control_boundary_evidence_register,
            maintenance_proof_evidence_register=maintenance_proof_evidence_register,
            utility_charge_breakdown_register=utility_charge_breakdown_register,
            tariff_exposure_register=tariff_exposure_register,
            owner_operator_tenant_responsibility_register=owner_operator_tenant_responsibility_register,
        )
        binding_upgrade_register = build_binding_upgrade_register(
            local_evidence_binding_register=local_evidence_binding_register,
        )
        local_truth_confidence_register = build_local_truth_confidence_register(
            local_evidence_binding_register=local_evidence_binding_register,
        )
        binding_sufficiency_reason_register = build_binding_sufficiency_reason_register(
            local_evidence_binding_register=local_evidence_binding_register,
        )
        operational_bounding_scorecard = build_operational_bounding_scorecard(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
        )
        promotion_blocker_register = build_promotion_blocker_register(
            asset_family_research_profile=asset_family_research_profile,
            operational_intake_pack=operational_intake_pack,
        )
        unresolved_source_conflicts = [
            row
            for row in source_conflict_register
            if str(row.get("resolution_state", "")).strip() == "unresolved_high_authority_conflict"
        ]
        for row in unresolved_source_conflicts:
            promotion_blocker_register.append(
                {
                    "blocker_code": "unresolved_source_authority_conflict",
                    "severity": str(row.get("severity", "")).strip() or "critical",
                    "blocks_mode": "hybrid_diligence",
                    "conflict_domain": str(row.get("conflict_domain", "")).strip(),
                    "why": str(row.get("why", "")).strip() or "High-authority source conflict remains unresolved.",
                }
            )
        gap_taxonomy_register = build_gap_taxonomy_register(
            dynamic_intake_question_register=dynamic_intake_question_register,
            promotion_blocker_register=promotion_blocker_register,
            claim_impact_register=claim_impact_register,
        )
        evidence_need_class_register = build_evidence_need_class_register(
            gap_taxonomy_register=gap_taxonomy_register,
        )
        operational_intake_pack["operational_bounding_scorecard"] = operational_bounding_scorecard
        operational_intake_pack["promotion_blocker_register"] = promotion_blocker_register
        operational_intake_pack["gap_taxonomy_register"] = gap_taxonomy_register
        operational_intake_pack["evidence_need_class_register"] = evidence_need_class_register
        return {
            "case_fingerprint": case_fingerprint,
            "asset_family_research_profile": asset_family_research_profile,
            "asset_family_research_dossier": asset_family_research_dossier,
            "family_research_coverage_register": family_research_coverage_register,
            "family_research_gap_register": family_research_gap_register,
            "authoritative_source_trace_register": authoritative_source_trace_register,
            "authoritative_source_acquisition_trace": authoritative_source_acquisition_trace,
            "family_source_gap_register": family_source_gap_register,
            "family_source_refresh_state": family_source_refresh_state,
            "local_evidence_binding_register": local_evidence_binding_register,
            "binding_upgrade_register": binding_upgrade_register,
            "local_truth_confidence_register": local_truth_confidence_register,
            "binding_sufficiency_reason_register": binding_sufficiency_reason_register,
            "structured_local_source_register": structured_local_source_register,
            "raw_local_source_register": raw_local_source_register,
            "authority_precedence_register": authority_precedence_register,
            "source_conflict_register": source_conflict_register,
            "conflict_resolution_outcome_register": conflict_resolution_outcome_register,
            "entity_resolution_register": entity_resolution_register,
            "entity_conflict_register": entity_conflict_register,
            "asset_boundary_resolution_register": asset_boundary_resolution_register,
            "owner_operator_tenant_resolution_register": owner_operator_tenant_resolution_register,
            "entity_resolution_state": entity_resolution_state,
            "search_budget_register": search_budget_register,
            "search_attempt_ledger": search_attempt_ledger,
            "search_attempt_outcome_register": search_attempt_outcome_register,
            "search_exhaustion_register": search_exhaustion_register,
            "discovery_need_register": discovery_need_register,
            "search_family_execution_plan": search_family_execution_plan,
            "accepted_evidence_type_register": accepted_evidence_type_register,
            "discovery_stop_condition_register": discovery_stop_condition_register,
            "next_best_search_register": next_best_search_register,
            "search_target_priority_register": search_target_priority_register,
            "search_success_effect_register": search_success_effect_register,
            "search_failure_effect_register": search_failure_effect_register,
            "stop_condition_register": stop_condition_register,
            "downgrade_condition_register": downgrade_condition_register,
            "escalation_condition_register": escalation_condition_register,
            "minimum_sufficient_evidence_register": minimum_sufficient_evidence_register,
            "congruence_case_state": congruence_case_state,
            "rival_hypothesis_seed_register": rival_hypothesis_seed_register,
            "dominant_hypothesis_register": dominant_hypothesis_register,
            "hypothesis_evidence_gap_register": hypothesis_evidence_gap_register,
            "hypothesis_claim_blocker_register": hypothesis_claim_blocker_register,
            "decision_context_register": decision_context_register,
            "question_candidate_register": question_candidate_register,
            "question_normalization_register": question_normalization_register,
            "dynamic_intake_question_register": dynamic_intake_question_register,
            "truncated_question_register": truncated_question_register,
            "required_from_register": required_from_register,
            "intake_priority_register": intake_priority_register,
            "rival_hypothesis_register": rival_hypothesis_register,
            "hypothesis_discrimination_register": hypothesis_discrimination_register,
            "claim_impact_register": claim_impact_register,
            "gap_taxonomy_register": gap_taxonomy_register,
            "evidence_need_class_register": evidence_need_class_register,
            "declared_input_downgrade_register": declared_input_downgrade_register,
            "operational_intake_pack": operational_intake_pack,
            "operational_bounding_scorecard": operational_bounding_scorecard,
            "evidence_mode_state": operational_bounding_scorecard.get("evidence_mode_state", ""),
            "promotion_blocker_register": promotion_blocker_register,
            "utility_charge_breakdown_register": utility_charge_breakdown_register,
            "tariff_exposure_register": tariff_exposure_register,
            "permit_to_system_register": permit_to_system_register,
            "regulated_process_scope_register": regulated_process_scope_register,
            "control_boundary_evidence_register": control_boundary_evidence_register,
            "owner_operator_tenant_responsibility_register": owner_operator_tenant_responsibility_register,
            "maintenance_proof_evidence_register": maintenance_proof_evidence_register,
            "selected_asset_family": asset_family_research_profile.get("asset_family", ""),
            "research_mode": asset_family_research_profile.get("research_mode", ""),
            "route_state": asset_family_research_profile.get("route_state", ""),
            "research_library_version": RESEARCH_LIBRARY_VERSION,
            "authoritative_source_family_count": len(asset_family_research_profile.get("authoritative_source_families", []) or []),
            "family_research_coverage_count": len(family_research_coverage_register),
            "family_research_gap_count": len(family_research_gap_register),
            "authoritative_source_acquisition_count": len(authoritative_source_acquisition_trace),
            "family_source_gap_count": len(family_source_gap_register),
            "augmented_source_register_count": len(source_register),
            "structured_local_source_count": len(structured_local_source_register),
            "raw_local_source_count": len(raw_local_source_register),
            "authority_precedence_count": len(authority_precedence_register),
            "source_conflict_count": len(source_conflict_register),
            "entity_resolution_count": len(entity_resolution_register),
            "entity_conflict_count": len(entity_conflict_register),
            "search_budget_count": len(search_budget_register),
            "search_attempt_count": len(search_attempt_ledger),
            "search_exhaustion_count": len(search_exhaustion_register),
            "discovery_need_count": len(discovery_need_register),
            "next_best_search_count": len(next_best_search_register),
            "stop_condition_count": len(stop_condition_register),
            "dynamic_intake_question_count": len(dynamic_intake_question_register),
            "truncated_question_count": len(truncated_question_register),
            "required_from_count": len(required_from_register),
            "intake_priority_count": len(intake_priority_register),
            "rival_hypothesis_seed_count": len(rival_hypothesis_seed_register),
            "dominant_hypothesis_count": len(dominant_hypothesis_register),
            "hypothesis_evidence_gap_count": len(hypothesis_evidence_gap_register),
            "hypothesis_claim_blocker_count": len(hypothesis_claim_blocker_register),
            "decision_context_count": len(decision_context_register),
            "question_candidate_count": len(question_candidate_register),
            "question_normalization_count": len(question_normalization_register),
            "rival_hypothesis_count": len(rival_hypothesis_register),
            "hypothesis_discrimination_count": len(hypothesis_discrimination_register),
            "claim_impact_count": len(claim_impact_register),
            "gap_taxonomy_count": len(gap_taxonomy_register),
            "evidence_need_class_count": len(evidence_need_class_register),
            "declared_input_downgrade_count": len(declared_input_downgrade_register),
            "diligence_pack_count": len(operational_intake_pack.get("diligence_pack_register", []) or []),
            "requested_but_absent_pack_count": sum(
                1
                for row in list(operational_intake_pack.get("diligence_pack_register", []) or [])
                if str(row.get("current_state", "")).strip() == "requested_but_absent"
            ),
            "partially_evidenced_pack_count": sum(
                1
                for row in list(operational_intake_pack.get("diligence_pack_register", []) or [])
                if str(row.get("current_state", "")).strip() == "partially_evidenced"
            ),
            "utility_charge_breakdown_count": len(utility_charge_breakdown_register),
            "tariff_exposure_count": len(tariff_exposure_register),
            "permit_to_system_count": len(permit_to_system_register),
            "regulated_process_scope_count": len(regulated_process_scope_register),
            "control_boundary_evidence_count": len(control_boundary_evidence_register),
            "maintenance_proof_evidence_count": len(maintenance_proof_evidence_register),
            "promotion_blocker_count": len(promotion_blocker_register),
            "binding_gap_count": sum(
                1
                for row in local_evidence_binding_register
                if str(row.get("current_local_binding_state", "")).strip() not in {"partially_bound", "sufficiently_bound"}
            ),
        }
