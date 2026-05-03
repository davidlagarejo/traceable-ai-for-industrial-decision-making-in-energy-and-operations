# Conceptual Schema — Decision Core / Inference Engine

Motor ID: motor_014

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
why_it_exists:  Es el corazón analítico de Fase 2.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001)
key_outputs:    inference_record, tension_record, gap_agenda, validation_agenda
key_objects:    InferenceRecord, Tension, ValidationAgenda
what_not_to_do: No produce reportes finales. No verifica claims. Solo infiere y registra con contratos explícitos.
design_notes:   Determinismo primero. La IA puede asistir pero no decide. Depende de motor_013 y motor_001.

Sections below define the completed documentation-base contract for this motor.
-->

## entities
- `InferenceRecord`: structured analytical record for one activated inference case, including bounded inference state, evidence basis, lineage, and applied rule references.
- `Tension`: explicit record of a conflict, inconsistency, opportunity, or unresolved analytical pressure detected while processing an inference case.
- `GapAgenda`: ordered set of gaps that block stronger inference, including missing evidence, missing validation data, unresolved conflict, or contract-limited conclusions.
- `ValidationAgenda`: downstream validation plan derived from the inference and gap agenda, listing evidence needs and handoff targets without performing validation itself.

## relationships
- `InferenceCase` → `InferenceRecord` (one activated case produces one primary inference record when all input validations pass).
- `PhaseContract` → `InferenceRecord` (the contract authorizes the permitted input class, output class, and inference limits).
- `InferenceRecord` → `Tension` (one inference record may produce zero or more tensions when evidence, triggers, or interpretation constraints conflict).
- `InferenceRecord` → `GapAgenda` (one inference record produces a gap agenda when evidence, validation data, or contract scope is insufficient for stronger status).
- `Tension` → `GapAgenda` (each unresolved tension can create one or more gap items that specify what must be clarified).
- `GapAgenda` → `ValidationAgenda` (gap items become validation agenda items when downstream evidence collection or verification is required).
- `InferenceRecord` → `ValidationAgenda` (the inference record anchors the validation route and preserves the case-level lineage for downstream motors).

## key_fields
`InferenceRecord`
- `inference_id`: `string`
- `case_id`: `string`
- `phase_contract_ref`: `string`
- `inference_state`: `enum[hypothesis_only, bounded_inference, blocked_by_gap]`
- `evidence_refs`: `list[string]`
- `lineage_refs`: `list[string]`

`Tension`
- `tension_id`: `string`
- `inference_id`: `string`
- `tension_type`: `enum[conflict, inconsistency, opportunity, missing_evidence, contract_limit]`
- `severity`: `enum[low, medium, high, blocking]`
- `source_refs`: `list[string]`
- `requires_validation`: `boolean`

`GapAgenda`
- `gap_agenda_id`: `string`
- `inference_id`: `string`
- `gap_items`: `list[object]`
- `priority_order`: `list[string]`
- `validation_dependency_refs`: `list[string]`

`ValidationAgenda`
- `validation_agenda_id`: `string`
- `inference_id`: `string`
- `validation_items`: `list[object]`
- `required_evidence_level`: `enum[validation_data, field_evidence]`
- `handoff_target`: `string`
