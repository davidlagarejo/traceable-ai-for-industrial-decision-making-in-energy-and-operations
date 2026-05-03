# Failure Modes — Inference Case Activation Engine

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

## failure_modes_list
- `QUALITY_BYPASS`: cases are activated even though one or more required `quality_records` are missing, failed or blocking.
- `TRIGGER_SCOPE_DRIFT`: triggers intended for a different object type, facility scope or bundle class activate cases outside their declared scope.
- `DUPLICATE_CASE_ACTIVATION`: repeated trigger matches create multiple equivalent `InferenceCase` records for the same prior, facility and case type.
- `LINEAGE_LOSS`: activation outputs lack references to prior version, library object version, trigger version or quality records, making rebuild impossible.
- `ANALYSIS_LEAKAGE`: activation records include conclusions, recommendations or decision-grade statements that belong to `motor_014` or downstream reporting.

## anti_patterns
- Using the motor as a lightweight Decision Core by embedding analytical conclusions in activation rationale.
- Treating any high-priority prior as automatically activated without explicit trigger evaluation.
- Collapsing trigger evaluation, case activation and quality gating into an opaque script with no per-trigger log.
- Allowing operators or model output to add ad hoc trigger rules during a run without a governed library object version.

## degradation_signals
- Rising ratio of activated cases to evaluated triggers without corresponding changes in governed trigger definitions.
- Increasing count of activation records missing quality record references, trigger version or lineage id.
- More than one activated case with the same `facility_id`, `source_prior_ref` and `activation_case_type`.
- Trigger log entries with generic reason codes instead of deterministic rule-specific codes.
- Growth in cases rejected by `REQUIRED_FIELD_MISSING`, indicating trigger definitions no longer match available prior and bundle fields.
- Presence of conclusion-like language in `activation_record.reason_code` or activation rationale.
