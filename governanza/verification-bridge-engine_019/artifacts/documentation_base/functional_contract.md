# Functional Contract — Verification Bridge Engine

Motor ID: motor_019

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir claims y tensiones en rutas explícitas de endurecimiento de evidencia.
why_it_exists:  Sin este motor el sistema se queda en hipótesis y reporting, sin puente real a verificación.
key_inputs:     inference_records (motor_014), validation_data (motor_018), phase_contracts (motor_001)
key_outputs:    verification_path, hardening_agenda, evidence_gap_record
key_objects:    VerificationPath, HardeningAgenda, EvidenceGap
what_not_to_do: No cierra claims automáticamente. No puede ser reemplazado por synthetic_support.
design_notes:   Produce field_evidence level cuando completa verificación. Depende de motor_014, motor_018 y motor_001.

All placeholder markers in this file have been replaced with governed content.
-->

## inputs
- inference_records: list[InferenceRecord] — source motor_014; each record must include inference_record_id, claim_id or tension_id, evidentiary_basis, confidence_state, unresolved_gaps, lineage_refs, version_id.
- validation_data: list[ValidationDataRecord] — source motor_018; each record must include validation_data_id, evidence_level, measured_value or observation_ref, source_provenance, lineage_refs, quality_status, version_id.
- phase_contracts: list[PhaseContract] — source motor_001; each contract must include phase_id, allowed_inputs, allowed_outputs, evidence_thresholds, handoff_rules, contract_version.

## outputs
- verification_path: VerificationPath — consumed by downstream verification workflow, reporting engines and conformance review; maps one claim or tension to required evidence-hardening steps.
- hardening_agenda: HardeningAgenda — consumed by field validation planning, governance review and pipeline orchestration; orders verification actions by urgency, dependency and evidentiary impact.
- evidence_gap_record: EvidenceGap — consumed by Decision Core feedback loops, validation planning and governance exception tracking; records missing, weak or non-actionable evidence conditions.

## limits
- The motor never accepts synthetic_support, synthetic_data, expert_spec or ML capability demonstrations as verification evidence.
- The motor never accepts inference_records without lineage_refs, source inference_record_id or an explicit claim_id or tension_id.
- The motor never accepts validation_data whose evidence_level is synthetic_support or whose provenance cannot be traced to real structured data.
- The motor never produces claim_closed, final_decision, report_package, output_block or source_capture artifacts.
- The motor never mutates upstream inference_records, validation_data or phase_contracts; it only references them.
- The motor never promotes a claim to field_evidence without concrete validation_data links and phase_contract authorization.

## validations
- Reject input with error `MISSING_INFERENCE_LINEAGE` when any inference_record lacks lineage_refs or version_id.
- Reject input with error `INVALID_EVIDENCE_LEVEL` when validation_data is tagged as synthetic_support, non_evidentiary or lacks real-data provenance.
- Reject input with error `CONTRACT_MISMATCH` when phase_contracts do not allow the proposed input-output handoff for the current phase.
- Before processing, verify that every claim_id or tension_id in scope has either linked validation_data or an explicit EvidenceGap reason.
- Before emitting verification_path, require path_id, target_ref, source_inference_ref, required_evidence, verification_steps, current_evidence_level, target_evidence_level, lineage_refs and status.
- Before emitting hardening_agenda, require agenda_id, path_refs, prioritized_actions, dependency_order, blocking_gaps, owner_role and review_trigger.
- Before emitting evidence_gap_record, require gap_id, target_ref, missing_evidence_type, gap_severity, blocking_reason, recommended_next_action and lineage_refs.
- Emit only immutable references to upstream objects; correction of upstream data must be represented as a new version upstream, not edited inside this motor.
