# Conceptual Schema — Inference Case Activation Engine

Motor ID: motor_013

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
why_it_exists:  Separa selección de casos del análisis del Decision Core.
key_inputs:     facility_prior (motor_012), library_objects (motor_011), quality_records (motor_007)
key_outputs:    inference_case, activation_record, trigger_log
key_objects:    InferenceCase, ActivationRecord, TriggerCondition
what_not_to_do: No analiza los casos. No produce conclusiones. Solo activa y registra.
design_notes:   Crea los casos que alimentan al Decision Core. Sin este motor, motor_014 no tiene input.

Sections below completed for Gate 1 validation.
-->

## entities
- `InferenceCase`: governed case opened for later analysis by `motor_014` after a trigger condition matches an eligible prior and library context.
- `ActivationRecord`: auditable record of one activation decision, including the inputs, trigger version, result and reason code.
- `TriggerCondition`: governed condition from a library object that defines when an inference case may be activated.
- `TriggerLogEntry`: immutable log entry for each evaluated trigger condition, whether it activated a case or not.

## relationships
- `facility_prior` -> `InferenceCase` (one prior can activate zero or more cases when governed triggers match).
- `library_object` -> `TriggerCondition` (one library object can define one or more trigger conditions within its declared scope).
- `TriggerCondition` -> `ActivationRecord` (each evaluated trigger produces one activation decision record).
- `ActivationRecord` -> `InferenceCase` (a positive activation record creates or references exactly one activated inference case).
- `TriggerCondition` -> `TriggerLogEntry` (every evaluated trigger produces one log entry for audit, including non-activation).
- `InferenceCase` -> `motor_014` (activated cases are the governed input set for Decision Core analysis).

## key_fields
`InferenceCase`
- `case_id`: string
- `facility_id`: string
- `source_prior_ref`: string
- `trigger_condition_ref`: string
- `activation_record_ref`: string
- `case_status`: enum[`activated`]
- `lineage_id`: string

`ActivationRecord`
- `activation_id`: string
- `case_id`: string or null
- `evaluated_input_refs`: list[string]
- `trigger_version`: string
- `result`: enum[`activated`, `not_activated`, `rejected`]
- `reason_code`: string
- `lineage_id`: string

`TriggerCondition`
- `trigger_condition_id`: string
- `library_object_ref`: string
- `condition_type`: enum[`field_threshold`, `tag_match`, `bundle_presence`, `quality_gate`, `compound`]
- `required_fields`: list[string]
- `activation_case_type`: string
- `version`: string

`TriggerLogEntry`
- `trigger_log_id`: string
- `trigger_condition_ref`: string
- `facility_prior_ref`: string
- `evaluation_result`: enum[`matched`, `not_matched`, `rejected`]
- `reason_code`: string
- `evaluated_at`: string
