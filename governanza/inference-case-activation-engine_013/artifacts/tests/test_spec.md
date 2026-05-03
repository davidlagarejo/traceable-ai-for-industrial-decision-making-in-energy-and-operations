# Test Spec — Inference Case Activation Engine

Motor ID: motor_013

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
why_it_exists:  Separa selección de casos del análisis del Decision Core.
key_inputs:     facility_prior (motor_012), library_objects (motor_011), quality_records (motor_007)
key_outputs:    inference_case, activation_record, trigger_log
key_objects:    InferenceCase, ActivationRecord, TriggerCondition
what_not_to_do: No analiza los casos. No produce conclusiones. Solo activa y registra.
design_notes:   Crea los casos que alimentan al Decision Core. Sin este motor, motor_014 no tiene input.

All pending markers in this test specification have been resolved with concrete cases.
-->

## happy_path
Input fixture:
- `facility_prior.prior_id = "prior-FAC-221-v3"`
- `facility_prior.facility_id = "FAC-221"`
- `facility_prior.prior_version = "3.0.0"`
- `facility_prior.lineage_id = "lin-prior-221-3"`
- `facility_prior.provenance_refs = ["prov-prior-221", "prov-bundle-energy-221"]`
- `facility_prior.contextual_bundles = [{"bundle_id": "bundle-energy-221", "signals": {"energy_variance_band": "high"}}]`
- `library_objects = [{"library_object_id": "lib-energy-gap-001", "version": "1.4.0", "scope": "facility_energy", "activation_tags": ["energy_variance"], "triggers": [{"trigger_condition_id": "trg-energy-gap-high", "version": "1.4.0", "condition_type": "tag_match", "scope": "facility_energy", "required_fields": ["contextual_bundles.signals.energy_variance_band"], "activation_case_type": "energy_variance_gap", "condition_expression_ref": "expr-energy-band-high", "expected_value": "high"}]}]`
- `quality_records = [{"quality_record_id": "qr-prior-221", "object_ref": "prior-FAC-221-v3", "fitness_status": "PASS"}, {"quality_record_id": "qr-bundle-energy-221", "object_ref": "bundle-energy-221", "fitness_status": "PASS"}, {"quality_record_id": "qr-lib-energy-gap-001", "object_ref": "lib-energy-gap-001", "fitness_status": "PASS"}]`

Expected behavior:
- The motor accepts the prior, library object and quality records as structurally valid.
- The trigger `trg-energy-gap-high` is evaluated because its scope matches `facility_energy` and its required field is present.
- Exactly one `InferenceCase` is emitted with `facility_id = "FAC-221"`, `source_prior_ref = "prior-FAC-221-v3"`, `source_prior_version = "3.0.0"`, `activation_case_type = "energy_variance_gap"`, `case_status = "activated"`, `trigger_condition_ref = "trg-energy-gap-high"`, `library_object_refs = ["lib-energy-gap-001"]`, and non-empty `case_id`, `activation_record_ref`, `lineage_id`, `lineage_refs`, `provenance_refs`, `created_at`, `produced_at`, `version_id` and `version_hash`.
- Exactly one `ActivationRecord` is emitted with `result = "activated"`, `reason_code = "TRIGGER_MATCHED"`, `trigger_condition_ref = "trg-energy-gap-high"`, `trigger_version = "1.4.0"`, `case_id` equal to the emitted case id, `evaluated_input_refs` containing the prior, bundle, library object and quality record references, and `produced_by_motor = "motor_013"`.
- Exactly one `TriggerLogEntry` is emitted with `evaluation_result = "matched"`, `reason_code = "TRIGGER_MATCHED"`, `case_ref` equal to the emitted case id, and `activation_record_ref` equal to the emitted activation record id.
- Re-running the same fixture with the same activation rule version reproduces the same `case_id`, `activation_id`, `trigger_log_id` and `version_hash` values, excluding only transport metadata that the schema marks as non-material.

## sparse_case
Input fixture:
- `facility_prior.prior_id = "prior-FAC-318-v1"`, `facility_id = "FAC-318"`, `prior_version = "1.0.0"`, `lineage_id = "lin-prior-318-1"` and `provenance_refs = ["prov-prior-318"]`.
- `facility_prior.contextual_bundles = []`; no optional contextual bundle is supplied.
- `library_objects` contains two governed triggers from `lib-energy-gap-001`: `trg-energy-gap-high` requires `contextual_bundles.signals.energy_variance_band`, and `trg-prior-tag-audit` requires `facility_prior.activation_tags`.
- `facility_prior.activation_tags = ["audit_required"]`.
- Required quality records for the prior and library object have `fitness_status = "PASS"` and no blocking flag.

Expected behavior:
- The motor does not raise a fatal error merely because the optional contextual bundle list is empty.
- The trigger requiring `facility_prior.activation_tags` is evaluated normally and activates one case when the tag matches.
- The trigger requiring `contextual_bundles.signals.energy_variance_band` is not evaluated as a match; it produces a `TriggerLogEntry` with `evaluation_result = "rejected"` and `reason_code = "REQUIRED_FIELD_MISSING"`.
- The emitted `InferenceCase`, if activated by the available tag trigger, has `contextual_bundle_refs = []`, carries the prior and library quality record references, and does not invent bundle references.
- No output mutates the input prior, library object or quality record payloads.

## malformed_input
Case 1: missing prior identity.
- Input has `facility_prior.prior_id = ""`, `facility_prior.facility_id = "FAC-401"`, `facility_prior.prior_version = "1.0.0"` and `facility_prior.lineage_id = "lin-prior-401-1"`.
- Expected result: the motor rejects the run with `INPUT_VALIDATION_ERROR`, emits no `InferenceCase`, and does not evaluate library triggers for that prior.

Case 2: wrong input type.
- Input has `library_objects = {"library_object_id": "lib-energy-gap-001"}` instead of a list of objects.
- Expected result: the motor rejects the library input with `LIBRARY_OBJECT_INVALID` or equivalent structured validation failure mapped to invalid library input, emits no activated case from that library object, and records no successful trigger evaluation for it.

Case 3: missing lineage.
- Input has a non-empty `prior_id`, `facility_id` and `prior_version`, but `facility_prior.lineage_id = ""` and `provenance_refs = []`.
- Expected result: the motor rejects the prior with `INPUT_VALIDATION_ERROR`, emits no `InferenceCase`, and performs no silent repair of lineage or provenance fields.

Case 4: blocked quality.
- Input is otherwise valid, but `quality_records` contains `{"quality_record_id": "qr-lib-energy-gap-001", "object_ref": "lib-energy-gap-001", "fitness_status": "FAIL", "blocking_flag": true}`.
- Expected result: the affected library object cannot activate a case; the motor returns or records `QUALITY_GATE_BLOCKED`, emits no `InferenceCase` from that object, and any related trigger log uses `evaluation_result = "rejected"` with `reason_code = "QUALITY_GATE_BLOCKED"`.

## edge_cases
1. No trigger matches.
   Input: all required prior, library and quality fields are valid, but the prior has `energy_variance_band = "normal"` while the only trigger expects `"high"`.
   Expected behavior: no `InferenceCase` is emitted; one `ActivationRecord` is emitted with `result = "not_activated"`, `case_id = null` and `reason_code = "TRIGGER_NOT_MATCHED"`; one `TriggerLogEntry` is emitted with `evaluation_result = "not_matched"` and `case_ref = null`.

2. Multiple triggers match the same case type.
   Input: two valid triggers, `trg-energy-gap-high` and `trg-energy-volatility-high`, both match `facility_id = "FAC-221"`, `source_prior_ref = "prior-FAC-221-v3"` and `activation_case_type = "energy_variance_gap"`.
   Expected behavior: exactly one `InferenceCase` is emitted; `supporting_trigger_refs` contains both trigger ids in deterministic order; `trigger_condition_ref` is the primary trigger selected by deterministic priority; all evaluated triggers have `TriggerLogEntry` records; duplicate activation is represented by activation metadata, not by a second case.

3. Conditional quality pass.
   Input: the prior and library object are valid, one required quality record has `fitness_status = "CONDITIONAL_PASS"`, `blocking_flag = false` and `condition_note = "source freshness accepted for activation only"`.
   Expected behavior: activation may proceed when the trigger matches; `quality_record_refs` includes the conditional quality record; `conditional_quality_notes` carries the condition note or its governed reference; no conclusion or confidence statement is produced.

4. Trigger scope mismatch.
   Input: a valid prior has scope context `facility_energy`, while a library object trigger declares `scope = "facility_staffing"`.
   Expected behavior: the trigger does not activate a case; the trigger log records `evaluation_result = "rejected"` with `reason_code = "TRIGGER_SCOPE_MISMATCH"`; the motor does not reinterpret the trigger under a different scope.

## pass_criteria
A test passes only when every observable output follows the closed contract:
- Valid matching inputs produce exactly the expected `InferenceCase`, `ActivationRecord` and `TriggerLogEntry` counts.
- Every activated case has `case_status = "activated"`, `produced_by_motor = "motor_013"`, stable identifiers, non-empty versioning fields, non-empty lineage/provenance fields, and references back to the accepted prior, trigger, library object and quality records.
- Every evaluated trigger has exactly one trigger log entry with the correct `evaluation_result`, `reason_code`, `activation_record_ref` and `case_ref` nullability.
- Rejected and not-matched evaluations do not produce `InferenceCase` objects.
- Inputs are not mutated; all status changes appear only in motor_013 output records.
- No output contains an inference conclusion, recommendation, decision grade, confidence claim, validated finding or free-text trigger invented by this motor.

## fail_criteria
A test fails when any of the following is observed:
- A valid happy-path fixture does not emit one activated case, one activated activation record and one matched trigger log entry.
- An activated case is missing `case_id`, `facility_id`, `source_prior_ref`, `source_prior_version`, `trigger_condition_ref`, `activation_record_ref`, `created_at`, `lineage_id`, `lineage_refs`, `provenance_refs`, `version_id` or `version_hash`.
- A malformed prior, invalid library object or blocked quality record produces an activated case instead of the required structured rejection.
- Missing required trigger fields, scope mismatch or non-matching trigger values are silently ignored without a trigger log entry.
- Duplicate matching triggers for the same facility, source prior and case type create more than one `InferenceCase`.
- The motor mutates upstream prior, bundle, library or quality objects.
- The motor emits analytical content such as conclusions, recommendations, grades, tensions, opportunities, evidence claims or Decision Core results.
