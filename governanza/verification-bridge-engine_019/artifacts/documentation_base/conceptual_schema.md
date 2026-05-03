# Conceptual Schema — Verification Bridge Engine

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

## entities
- VerificationPath: explicit route from a claim or tension to the evidence required to harden it, including steps, thresholds, blockers and lineage.
- HardeningAgenda: prioritized worklist derived from one or more verification paths, ordering the evidence-hardening actions that must happen next.
- EvidenceGap: structured record of missing, insufficient, conflicting or non-actionable evidence that prevents a claim or tension from reaching the target evidence level.

## relationships
- InferenceRecord → VerificationPath (each verifiable claim or tension from motor_014 may create one active path when phase_contracts permit verification).
- ValidationDataRecord → VerificationPath (real validation data from motor_018 may satisfy one or more required evidence items when lineage and provenance match).
- VerificationPath → EvidenceGap (a path creates one or more gaps when required evidence is absent, weak, stale, conflicting or below threshold).
- VerificationPath → HardeningAgenda (open paths contribute actions to the agenda according to priority, dependency order and blocking severity).
- EvidenceGap → HardeningAgenda (each blocking gap contributes at least one recommended action unless the path is declared not currently actionable).
- PhaseContract → VerificationPath (the contract constrains allowed inputs, outputs, evidence thresholds and handoff status).

## key_fields
VerificationPath:
- path_id: string
- target_ref: object with claim_id or tension_id
- source_inference_ref: string
- required_evidence: list[object]
- verification_steps: list[object]
- current_evidence_level: enum[hypothesis, inference_result, validation_data, field_evidence]
- target_evidence_level: enum[validation_data, field_evidence]
- lineage_refs: list[string]
- status: enum[draft, actionable, blocked, verified_evidence_ready]

HardeningAgenda:
- agenda_id: string
- path_refs: list[string]
- prioritized_actions: list[object]
- dependency_order: list[string]
- blocking_gaps: list[string]
- owner_role: string
- review_trigger: string
- generated_from_version: string

EvidenceGap:
- gap_id: string
- target_ref: object with claim_id or tension_id
- missing_evidence_type: enum[measurement, observation, source_confirmation, site_validation, conflict_resolution, provenance]
- gap_severity: enum[low, medium, high, blocking]
- blocking_reason: string
- recommended_next_action: string
- lineage_refs: list[string]
- status: enum[open, assigned, resolved_by_validation_data, deferred_with_reason]
