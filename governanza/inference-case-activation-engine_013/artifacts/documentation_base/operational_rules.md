# Operational Rules — Inference Case Activation Engine

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

## rules
1. The motor evaluates trigger conditions only after the `facility_prior`, selected `library_objects` and required `quality_records` pass structural validation.
2. A case is activated only when a governed `TriggerCondition` matches explicit fields in the prior, bundles or quality metadata.
3. Every trigger evaluation produces a `TriggerLogEntry`, including evaluations that do not activate a case.
4. Every activated case has exactly one `ActivationRecord` with `result = activated` and a deterministic `reason_code`.
5. If multiple triggers would create the same case type for the same `facility_id` and `source_prior_ref`, the motor emits one `InferenceCase` and records all supporting trigger references in activation metadata.
6. Inputs marked blocked or unfit by `quality_records` stop activation for the affected object and produce a rejected activation record or trigger log entry.
7. Output identifiers are stable for the same prior id, trigger id, library object version and activation rule version.
8. The motor passes only `InferenceCase` objects with `case_status = activated` to `motor_014`.

## invariants
- `facility_id` is preserved exactly from `facility_prior` into every related output.
- `source_prior_ref`, `trigger_condition_ref`, `activation_record_ref` and `lineage_id` are never empty on activated cases.
- Upstream input objects remain immutable; this motor creates new output records instead of modifying prior, library or quality records.
- Each output has enough provenance to reconstruct which input objects, versions and trigger rules produced it.
- A rejected trigger evaluation never becomes an activated inference case in the same run.
- `trigger_log` cardinality equals the number of trigger conditions evaluated in the run.

## forbidden_operations
- Analyze activated cases or produce inference results.
- Produce conclusions, recommendations, decision grades, tensions, opportunities or evidence claims.
- Modify `facility_prior`, contextual bundles, `library_objects` or `quality_records`.
- Create ad hoc trigger conditions from free text, operator preference or model output.
- Ignore missing lineage, missing quality records or blocked quality flags.
- Merge distinct facilities, priors or library object versions into one case without explicit deterministic identity rules.
- Send rejected, incomplete or non-activated cases to `motor_014`.
