# Operational Rules — Verification Bridge Engine

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

## rules
1. Every verification_path must reference exactly one primary claim_id or tension_id from an inference_record produced by motor_014.
2. Every verification_path must include phase_contract_id and contract_version from motor_001 before it can be marked actionable.
3. A validation_data item can satisfy required evidence only when it has real-data provenance, lineage_refs, version_id and quality_status not equal to rejected.
4. Any missing, conflicting or below-threshold evidence must create an EvidenceGap instead of being silently ignored.
5. A hardening_agenda must be generated from explicit verification_path and EvidenceGap records, never from free-text intuition.
6. The motor may mark a path as verified_evidence_ready only when required_evidence is satisfied by validation_data or field evidence references allowed by the phase contract.
7. The motor must preserve immutable references to all upstream records and must not rewrite upstream content.
8. Synthetic support is always rejected as verification evidence even when it is linked to the same inference case.

## invariants
- path_id, agenda_id and gap_id are stable once emitted.
- lineage_refs are never empty on emitted VerificationPath, HardeningAgenda or EvidenceGap objects.
- source_inference_ref always points to a motor_014 inference_record.
- phase_contract_id always points to a motor_001 phase contract used at evaluation time.
- current_evidence_level never exceeds the strongest validated real evidence linked to the path.
- EvidenceGap records remain open until a new validation_data or field evidence reference explicitly resolves them.
- Upstream object versions are referenced, not mutated.

## forbidden_operations
- Closing claims automatically.
- Replacing verification evidence with synthetic_support.
- Promoting synthetic data, expert specifications or ML outputs to validation_data or field_evidence.
- Creating or editing phase_contracts.
- Creating new inference_records or changing confidence_state inside motor_014 outputs.
- Capturing raw field data, parsing sources or normalizing records.
- Producing final report packages, rendered documents or executive summaries.
- Suppressing evidence gaps to make a verification path appear complete.
