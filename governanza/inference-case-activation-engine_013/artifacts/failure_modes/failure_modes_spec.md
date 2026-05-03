# Failure Modes Spec — Inference Case Activation Engine

Motor ID: motor_013

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
why_it_exists:  Separa selección de casos del análisis del Decision Core.
key_inputs:     facility_prior (motor_012), library_objects (motor_011), quality_records (motor_007)
key_outputs:    inference_case, activation_record, trigger_log
key_objects:    InferenceCase, ActivationRecord, TriggerCondition
what_not_to_do: No analiza los casos. No produce conclusiones. Solo activa y registra.
design_notes:   Crea los casos que alimentan al Decision Core. Sin este motor, motor_014 no tiene input.

All placeholder markers in this file have been replaced with concrete failure-mode content.
-->

## failure_modes_list
- `INPUT_PRIOR_IDENTITY_LOSS`: `facility_prior` lacks `prior_id`, `facility_id`, `prior_version`, lineage or provenance required by the contract → activation proceeds against an unrebuildable or ambiguous prior, and emitted records cannot be tied back to `motor_012` → reject the run with `INPUT_VALIDATION_ERROR`, emit no `InferenceCase`, preserve the failed validation in audit output, and require a corrected prior from the upstream handoff.
- `QUALITY_GATE_BYPASS`: a prior, contextual bundle or library object has no matching `quality_record`, has `fitness_status` outside `PASS` or `CONDITIONAL_PASS`, or carries a blocking flag → a case is activated from input that `motor_007` marked unfit, contaminating downstream Decision Core analysis → block activation for the affected object with `QUALITY_GATE_BLOCKED`, emit rejected activation/log records where applicable, and require quality metadata correction upstream.
- `TRIGGER_SCOPE_DRIFT`: a `TriggerCondition.scope` does not match the facility prior context, bundle class or declared object scope, but the trigger is still evaluated as eligible → cases open for the wrong facility dimension or analytical domain → mark the trigger evaluation as rejected with `TRIGGER_SCOPE_MISMATCH`, do not reinterpret the trigger, and require a governed library object or trigger version update from `motor_011`.
- `REQUIRED_FIELD_SILENCE`: a trigger requires prior, bundle or quality fields that are absent, but the implementation skips the trigger without a structured log entry → trigger coverage appears lower than reality and rebuild cannot explain why no case opened → emit one `TriggerLogEntry` with `evaluation_result = rejected` and `reason_code = REQUIRED_FIELD_MISSING` for each affected trigger, then continue with other eligible triggers.
- `DUPLICATE_CASE_FANOUT`: multiple matching triggers for the same `facility_id`, `source_prior_ref` and `activation_case_type` each create separate `InferenceCase` records → downstream `motor_014` receives duplicate analytical cases and may double-count the same activation event → collapse duplicates deterministically into one `InferenceCase`, select the primary trigger by governed priority, and store all matching trigger ids in `supporting_trigger_refs`.
- `LINEAGE_AND_VERSION_BREAK`: emitted `InferenceCase`, `ActivationRecord` or `TriggerLogEntry` records omit `source_prior_version`, `trigger_version`, `activation_rule_version`, `quality_record_refs`, `lineage_id`, `lineage_refs`, `provenance_refs` or `version_hash` → the activation cannot be reproduced from the same inputs and rule versions → fail output validation before persistence, regenerate only from the original accepted inputs, and never fill missing metadata with guessed values.
- `ANALYSIS_LEAKAGE`: activation rationale, reason codes or output fields include conclusions, recommendations, confidence claims, tensions, opportunities or evidence judgments → `motor_013` becomes a shadow Decision Core and violates the boundary with `motor_014` → reject the offending output shape, constrain rationale to deterministic activation codes, and route any analytical work exclusively to `motor_014` after case activation.

## anti_patterns
- Embedding inference, scoring, recommendation, tension detection or evidence evaluation in the activation step.
- Treating `facility_prior` priority, human preference or LLM text as sufficient to open a case without a governed `TriggerCondition`.
- Mutating `facility_prior`, contextual bundles, `library_objects` or `quality_records` to make activation easier.
- Creating ad hoc trigger rules inside this motor instead of reading governed trigger definitions from `motor_011` library objects.
- Collapsing validation, trigger evaluation, duplicate handling and output construction into an opaque function with no per-trigger log.
- Emitting only activated cases while omitting rejected and not-matched `ActivationRecord` or `TriggerLogEntry` records required for audit.
- Using timestamps, natural-language labels, list positions or unstable ordering as the basis for `case_id`, `activation_id`, `trigger_log_id` or `version_hash`.
- Passing rejected, incomplete, duplicated or non-activated records to `motor_014` as if they were valid `InferenceCase` objects.
- Silently repairing missing lineage, provenance, trigger version or quality references instead of blocking invalid activation.
- Sharing mutable in-memory references to upstream inputs in output records, which can make later changes appear as historical activation facts.

## degradation_signals
- `activated_case_count / evaluated_trigger_count` rises sharply without a corresponding governed trigger or rule-version change.
- More than one `InferenceCase` exists for the same `facility_id`, `source_prior_ref`, `source_prior_version`, `activation_case_type` and `activation_rule_version`.
- Any emitted `InferenceCase`, `ActivationRecord` or `TriggerLogEntry` has empty `lineage_id`, `lineage_refs`, `provenance_refs`, `version_id`, `version_hash` or `produced_by_motor`.
- `TriggerLogEntry` count is lower than the number of trigger conditions evaluated, or missing-field and scope-mismatch cases leave no rejected log.
- Rising `REQUIRED_FIELD_MISSING` rates indicate trigger definitions no longer match available prior or bundle fields.
- Rising `TRIGGER_SCOPE_MISMATCH` rates indicate drift between library object scopes and `facility_prior` context.
- `QUALITY_GATE_BLOCKED` events are absent despite failed or blocking `quality_records` in the input set.
- Reason-code distribution contains free-text values or values outside the closed schema enums.
- Repeated runs with identical accepted inputs and activation rule version produce different identifiers or version hashes.
- Activation records include conclusion-like terms such as recommendation, confidence, finding, tension, opportunity, validation result or decision grade.

## expensive_errors
- Activating cases from failed or missing quality records is expensive because downstream analysis may treat unfit inputs as legitimate and create inference, reporting and review artifacts that must be unwound. Prevention: require quality lookup before trigger evaluation, block on `FAIL` or blocking flags, and carry `quality_record_refs` into every activated case.
- Allowing duplicate case fanout is expensive because later motors may analyze and report the same activation more than once, making de-duplication ambiguous after analytical work has begun. Prevention: define deterministic identity over facility, prior, case type, trigger set and rule version before persistence.
- Losing lineage or version metadata is expensive because the activation cannot be rebuilt, audited or compared after upstream priors, library objects or trigger definitions change. Prevention: validate lineage, provenance, version fields and hashes as required output fields before any record leaves the motor.
- Evaluating triggers outside their declared scope is expensive because it creates analytically plausible but contractually invalid cases that are difficult to detect after `motor_014` produces inference records. Prevention: scope-check every trigger before field evaluation and log mismatches with `TRIGGER_SCOPE_MISMATCH`.
- Silently skipping triggers with missing required fields is expensive because operators cannot distinguish a true non-match from an unevaluable trigger, which corrupts coverage metrics and debugging. Prevention: emit rejected trigger logs with `REQUIRED_FIELD_MISSING` and monitor missing-field rates by trigger version.
- Letting analytical language leak into activation outputs is expensive because it blurs responsibility between this motor and the Decision Core, forcing later conformance review to separate activation facts from conclusions. Prevention: restrict outputs to activation status, deterministic reason codes, references and lineage metadata.
