# Acceptance Tests — Inference Case Activation Engine

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

## happy_path
Input: `facility_prior.prior_id = "prior-FAC-221-v3"`, `facility_id = "FAC-221"`, `prior_version = "3.0.0"`, with bundle signal `energy_variance_band = "high"` and lineage `lin-prior-221-3`; `library_objects` contains `library_object_id = "lib-energy-gap-001"`, `version = "1.4.0"`, scope `facility_energy`, and trigger condition `energy_variance_band == high`; `quality_records` for the prior, bundle and library object all have `fitness_status = PASS`.

Action: the motor validates the three input sets, evaluates the trigger, matches the condition, creates one activated `InferenceCase`, creates one `ActivationRecord` with `result = activated`, and writes one matching `TriggerLogEntry`.

Expected output: `inference_case.case_id` is stable for `prior-FAC-221-v3 + lib-energy-gap-001 + trigger version`; `inference_case.facility_id = "FAC-221"`; `case_status = activated`; `source_prior_ref = "prior-FAC-221-v3"`; `trigger_condition_ref` points to the evaluated trigger; `activation_record.result = activated`; `trigger_log[0].evaluation_result = matched`.

## edge_cases
- No trigger matches: when all inputs are valid but no `TriggerCondition` matches the prior or bundles, the motor emits no `InferenceCase`, emits `ActivationRecord` entries with `result = not_activated` where decisions are material, and emits `TriggerLogEntry` records with `evaluation_result = not_matched`.
- Multiple triggers match the same case type: when two governed triggers match the same `facility_id`, `source_prior_ref` and `activation_case_type`, the motor emits one `InferenceCase`, records both trigger references in activation metadata, and emits one trigger log entry per evaluated trigger.
- Conditional quality pass: when a required `quality_record` has `fitness_status = CONDITIONAL_PASS` with no blocking flag, the motor may activate a case but must carry the quality record reference and condition note into the activation metadata.
- Sparse but valid prior: when optional contextual fields are absent but all trigger-required fields and lineage fields are present, the motor evaluates only triggers whose `required_fields` are satisfied and logs skipped triggers as `rejected` with reason `REQUIRED_FIELD_MISSING`.

## rejection_criteria
- Missing prior identity: if `facility_prior.prior_id`, `facility_id`, `prior_version` or `lineage_id` is empty, the motor returns `INPUT_VALIDATION_ERROR` and emits no `InferenceCase`.
- Blocked quality record: if a required `quality_record` has `fitness_status = FAIL` or a blocking flag, the motor returns or records `QUALITY_GATE_BLOCKED` for the affected object and emits no activated case from that object.
- Invalid library object: if a selected `library_object` has no `library_object_id`, version, scope or trigger definition, the motor returns `LIBRARY_OBJECT_INVALID` for that object and does not evaluate its triggers.
- Missing trigger fields: if a trigger requires fields absent from the prior and its bundles, the motor records `REQUIRED_FIELD_MISSING` in the trigger log and cannot activate that trigger.
