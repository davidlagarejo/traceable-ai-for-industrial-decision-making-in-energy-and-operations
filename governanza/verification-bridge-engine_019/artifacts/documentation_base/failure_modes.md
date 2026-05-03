# Failure Modes — Verification Bridge Engine

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

## failure_modes_list
- SYNTHETIC_EVIDENCE_LEAK: synthetic_support or ML capability output appears inside required_evidence or linked_validation_data for a VerificationPath.
- CLAIM_CLOSURE_LEAK: output includes claim_closed, final_decision or equivalent terminal disposition instead of only verification path, hardening agenda and evidence gaps.
- GAP_SUPPRESSION: missing or conflicting evidence does not produce an EvidenceGap, causing an agenda to appear cleaner than the actual verification state.
- LINEAGE_BREAK: emitted objects lack source_inference_ref, validation_data refs, phase_contract_id or version references needed to reconstruct the path.
- CONTRACT_DRIFT: paths are generated without checking the current phase contract or with outputs not allowed by that contract version.

## anti_patterns
- Treating the motor as a final adjudicator that closes claims because enough data appears to exist.
- Feeding synthetic_support as a shortcut when field validation is expensive or slow.
- Collapsing VerificationPath, HardeningAgenda and EvidenceGap into one free-text note, which destroys structured auditability.
- Editing upstream inference_records or validation_data inside this motor to make a route pass.

## degradation_signals
- Percentage of verification_paths without EvidenceGap records remains near zero while unresolved_gaps in inference_records remains high.
- Any output contains synthetic_support, non_evidentiary_flag or capability_demo references as evidence.
- Rising count of paths with missing phase_contract_id, contract_version or lineage_refs.
- HardeningAgenda actions become generic repeated text instead of referencing path_refs, blocking_gaps and concrete evidence types.
- A growing share of paths move directly from hypothesis or inference_result to field_evidence without intermediate validation_data or explicit field evidence references.
- Review logs show repeated CONTRACT_MISMATCH or INVALID_EVIDENCE_LEVEL rejections for the same upstream producer.
