# Acceptance Tests — Verification Bridge Engine

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

## happy_path
Input: inference_record `inf_014_2026_0007` contains claim_id `claim_facility_power_gap`, confidence_state `hypothesis_with_real_indicators`, unresolved_gaps `["site_meter_reading", "maintenance_log_confirmation"]`, lineage_refs `["lin_014_a"]` and version_id `v1`. Validation_data from motor_018 contains `val_018_meter_031` with evidence_level `validation_data`, source_provenance `site_meter_export`, quality_status `accepted`, lineage_refs `["lin_018_m"]` and version_id `v3`. Phase_contract `phase4_verification_v2` allows verification_path, hardening_agenda and evidence_gap_record outputs.

Action: the motor links the inference record to the accepted validation_data, checks the phase contract, builds the required evidence list and compares available evidence to the target field_evidence threshold.

Expected output: one VerificationPath with target_ref `claim_facility_power_gap`, status `actionable`, current_evidence_level `validation_data`, target_evidence_level `field_evidence`, and a required step for direct field confirmation. One HardeningAgenda prioritizes `collect_site_meter_reading` before `confirm_maintenance_log`. One EvidenceGap is emitted for `maintenance_log_confirmation` with severity `blocking` because that evidence is still absent.

## edge_cases
- Sparse validation data: an inference_record is valid but has no matching validation_data. Correct behavior: emit a VerificationPath with status `blocked`, emit an EvidenceGap with missing_evidence_type `site_validation`, and include a HardeningAgenda action to obtain real validation data.
- Conflicting validation data: two validation_data records link to the same claim but report incompatible observations and both have accepted quality_status. Correct behavior: do not choose one silently; emit an EvidenceGap with missing_evidence_type `conflict_resolution`, keep current_evidence_level at the last non-conflicting level, and require review in the HardeningAgenda.
- Already strong evidence: validation_data includes a field_evidence reference allowed by the phase contract. Correct behavior: mark the VerificationPath as `verified_evidence_ready`, preserve the evidence reference and still avoid emitting any claim_closed or final_decision output.

## rejection_criteria
- Reject with `MISSING_INFERENCE_LINEAGE` when an inference_record lacks lineage_refs, version_id or source_inference_ref.
- Reject with `INVALID_EVIDENCE_LEVEL` when the only supporting evidence is tagged synthetic_support, non_evidentiary or expert_spec.
- Reject with `CONTRACT_MISMATCH` when the phase_contract does not allow verification_path or hardening_agenda outputs for the current phase.
- Reject with `UNSUPPORTED_TARGET_REF` when the input lacks both claim_id and tension_id.
