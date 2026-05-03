# Functional Contract — Inference Case Activation Engine

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

## inputs
- `facility_prior`: object — produced by `motor_012`; contains `prior_id`, `facility_id`, `prior_version`, contextual bundles, candidate signals, provenance and lineage references.
- `library_objects`: list[object] — produced by `motor_011`; contains governed reusable objects with `library_object_id`, `object_type`, `version`, `activation_tags`, `scope` and trigger definitions.
- `quality_records`: list[object] — produced by `motor_007`; contains `quality_record_id`, `object_ref`, `fitness_status`, quality score, blocking flags and provenance for each input object used by this motor.

## outputs
- `inference_case`: object — consumed by `motor_014`; contains the activated case, source prior reference, trigger reference, eligible library references, activation rationale and lineage.
- `activation_record`: object — persisted for audit and consumed by downstream conformance checks; records the activation decision, evaluated inputs, rule version, result and deterministic reason code.
- `trigger_log`: list[object] — persisted for observability and audit; records every trigger condition evaluated, including matched, not matched and rejected conditions.

## limits
- The motor never accepts a `facility_prior` without `prior_id`, `facility_id`, `prior_version` and lineage metadata.
- The motor never accepts `library_objects` that lack governed trigger definitions, version identifiers or scope declarations.
- The motor never activates a case for an object whose `quality_records` mark it as blocked, unfit or missing required provenance.
- The motor never produces an inference conclusion, decision grade, confidence claim, recommendation or validated finding.
- The motor never mutates upstream prior, bundle, quality or library objects; every change in status is represented as a new activation output.
- The motor never opens cases from free-text intuition or unguided AI interpretation; activation requires explicit trigger conditions.

## validations
- Reject input with `INPUT_VALIDATION_ERROR` when `facility_prior.prior_id`, `facility_prior.facility_id`, `facility_prior.prior_version` or lineage fields are empty.
- Reject input with `QUALITY_GATE_BLOCKED` when any required `quality_record` for the prior, referenced bundle or selected library object has `fitness_status` outside `PASS` or `CONDITIONAL_PASS`.
- Reject input with `LIBRARY_OBJECT_INVALID` when a selected library object has no stable `library_object_id`, no version, no scope or no trigger definition.
- Evaluate only trigger conditions whose declared scope matches the facility prior context and whose required fields are present.
- Before emitting `inference_case`, require `case_id`, `facility_id`, `source_prior_ref`, `trigger_condition_ref`, `activation_record_ref`, `created_at`, `lineage_id` and `case_status = activated`.
- Before emitting `activation_record`, require `activation_id`, `case_id` when activated, `evaluated_input_refs`, `trigger_version`, `result`, `reason_code` and `lineage_id`.
- Before emitting `trigger_log`, require one log entry per evaluated trigger with `trigger_condition_ref`, `evaluation_result`, `reason_code` and timestamp.
