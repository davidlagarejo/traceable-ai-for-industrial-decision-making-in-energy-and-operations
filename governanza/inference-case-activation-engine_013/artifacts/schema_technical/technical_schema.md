# Technical Schema — Inference Case Activation Engine

Motor ID: motor_013

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
why_it_exists:  Separa selección de casos del análisis del Decision Core.
key_inputs:     facility_prior (motor_012), library_objects (motor_011), quality_records (motor_007)
key_outputs:    inference_case, activation_record, trigger_log
key_objects:    InferenceCase, ActivationRecord, TriggerCondition
what_not_to_do: No analiza los casos. No produce conclusiones. Solo activa y registra.
design_notes:   Crea los casos que alimentan al Decision Core. Sin este motor, motor_014 no tiene input.

All open placeholders in this file have been resolved with concrete technical schema content.
-->

## entities
- `InferenceCase`: primary persisted output representing one governed case opened for later analysis by `motor_014`. It lives in the `schema_technical` stage as the canonical activated-case shape and is produced by implementation only after an eligible trigger condition matches a valid `facility_prior`, valid library context and passing quality evidence.
- `ActivationRecord`: immutable audit output for one deterministic activation decision. It lives in the `schema_technical` stage as the decision trace for activated, not activated and rejected evaluations; it records evaluated inputs, trigger rule version, result and reason code without producing analytical conclusions.
- `TriggerCondition`: governed trigger definition read from a `motor_011` library object. It lives in the `schema_technical` stage as an accepted input/reference entity, not as an ad hoc rule created by this motor; the implementation evaluates it against explicit prior, bundle and quality fields.
- `TriggerLogEntry`: immutable observability output for each evaluated trigger condition. It lives in the `schema_technical` stage as the per-trigger evaluation log that preserves matched, not matched and rejected outcomes for audit and rebuild.

## fields
`InferenceCase`
- `case_id: string` (required) — stable canonical identifier for the activated inference case.
- `record_id: string` (required) — generic record identifier equal to `case_id` for storage and audit interfaces.
- `facility_id: string` (required) — facility identifier copied exactly from the accepted `facility_prior`.
- `source_prior_ref: string` (required) — reference to the `motor_012.FacilityPrior.facility_prior_id` or compatible prior id used to open the case.
- `source_prior_version: string` (required) — `facility_prior.prior_version` or version identifier used during activation.
- `contextual_bundle_refs: list[string]` (required) — references to contextual bundles from `motor_012` considered for this case; empty only when the accepted prior has no applicable bundle.
- `library_object_refs: list[string]` (required) — references to eligible `motor_011.LibraryObject.library_object_id` values that supplied the matching trigger or activation context.
- `trigger_condition_ref: string` (required) — primary `TriggerCondition.trigger_condition_id` that activated the case.
- `supporting_trigger_refs: list[string]` (required) — all trigger condition identifiers supporting the same case when duplicate-prevention collapses multiple matches into one case.
- `activation_record_ref: string` (required) — reference to the `ActivationRecord.activation_id` with `result = activated`.
- `activation_case_type: string` (required) — governed case type declared by the matching trigger condition.
- `case_status: enum[activated]` (required) — fixed status for emitted cases; rejected or skipped evaluations are represented by records and logs, not by cases.
- `activation_rule_version: string` (required) — version of deterministic activation and duplicate-handling rules used to emit the case.
- `quality_record_refs: list[string]` (required) — `motor_007.QualityRecord.quality_record_id` references used to authorize the prior, bundle and library object inputs.
- `conditional_quality_notes: list[string]` (required) — references or codes for non-blocking `CONDITIONAL_PASS` quality conditions carried into activation metadata; empty when none apply.
- `activation_rationale_code: string` (required) — deterministic non-analytical code explaining why the case was opened.
- `provenance_refs: list[string]` (required) — upstream provenance references copied from the accepted prior, bundle, library and quality inputs.
- `lineage_id: string` (required) — canonical lineage reference for this activated case.
- `lineage_refs: list[string]` (required) — upstream lineage references sufficient to rebuild this case from the same accepted inputs and rule versions.
- `source_ref: string` (required) — lineage anchor for the case, normally `source_prior_ref`.
- `produced_by_motor: string` (required) — constant value `motor_013`.
- `produced_at: datetime` (required) — timestamp when this case was emitted.
- `parent_id: string | null` (required) — prior `case_id` superseded by this case for the same facility, prior and case type; null for first emission.
- `version_id: string` (required) — stable version identifier for this case record.
- `created_at: datetime` (required) — creation timestamp for this case record.
- `updated_at: datetime` (required) — latest metadata update timestamp; equal to `created_at` for immutable first emission.
- `version_hash: string` (required) — deterministic hash over the stable case payload, trigger references, accepted input references, activation rule version and lineage fields.

`ActivationRecord`
- `activation_id: string` (required) — stable canonical identifier for the activation decision record.
- `record_id: string` (required) — generic record identifier equal to `activation_id`.
- `case_id: string | null` (required) — `InferenceCase.case_id` when `result = activated`; null for not activated or rejected decisions.
- `facility_id: string` (required) — facility identifier copied from the accepted or rejected prior context.
- `source_prior_ref: string` (required) — prior reference evaluated by the decision.
- `evaluated_input_refs: list[string]` (required) — ordered references to the prior, contextual bundles, library objects and quality records evaluated for this decision.
- `trigger_condition_ref: string` (required) — evaluated `TriggerCondition.trigger_condition_id`.
- `trigger_version: string` (required) — version of the governed trigger definition evaluated.
- `activation_case_type: string` (required) — case type the trigger would open when matched.
- `result: enum[activated, not_activated, rejected]` (required) — deterministic activation outcome.
- `reason_code: enum[TRIGGER_MATCHED, TRIGGER_NOT_MATCHED, REQUIRED_FIELD_MISSING, QUALITY_GATE_BLOCKED, INPUT_VALIDATION_ERROR, LIBRARY_OBJECT_INVALID, TRIGGER_SCOPE_MISMATCH, DUPLICATE_CASE_COLLAPSED]` (required) — machine-readable reason for the result.
- `decision_detail_refs: list[string]` (required) — references to trigger log entries, quality flags or validation records supporting the decision.
- `activation_rule_version: string` (required) — version of deterministic activation, quality-gating and duplicate-handling rules used for the record.
- `provenance_refs: list[string]` (required) — upstream provenance references considered by the decision.
- `lineage_id: string` (required) — canonical lineage reference for this decision record.
- `lineage_refs: list[string]` (required) — upstream lineage references needed to reconstruct the same decision.
- `source_ref: string` (required) — lineage anchor, normally the evaluated prior reference plus trigger condition reference.
- `produced_by_motor: string` (required) — constant value `motor_013`.
- `produced_at: datetime` (required) — timestamp when this activation decision was emitted.
- `parent_id: string | null` (required) — prior activation record superseded for the same prior, trigger and rule version lineage; null for first emission.
- `version_id: string` (required) — stable version identifier for this activation record.
- `created_at: datetime` (required) — creation timestamp for this record.
- `updated_at: datetime` (required) — latest metadata update timestamp.
- `version_hash: string` (required) — deterministic hash over evaluated input references, trigger version, result, reason code, rule version and lineage fields.

`TriggerCondition`
- `trigger_condition_id: string` (required) — stable canonical identifier for the governed trigger definition.
- `record_id: string` (required) — generic record identifier equal to `trigger_condition_id`.
- `library_object_ref: string` (required) — `motor_011.LibraryObject.library_object_id` that owns or supplies the trigger.
- `library_object_version: string` (required) — version of the library object containing the trigger definition.
- `condition_type: enum[field_threshold, tag_match, bundle_presence, quality_gate, compound]` (required) — deterministic trigger evaluation type.
- `scope: string` (required) — declared facility, bundle, object or phase scope in which the trigger may be evaluated.
- `required_fields: list[string]` (required) — prior, bundle or quality metadata fields required before evaluation.
- `activation_case_type: string` (required) — case type emitted when the condition matches.
- `condition_expression_ref: string` (required) — governed reference or fingerprint for the trigger expression, not free text interpreted during activation.
- `allowed_result_values: list[string]` (required) — accepted evaluation outcomes for this trigger type.
- `trigger_priority: integer` (required) — deterministic ordering value for evaluating and collapsing duplicate matching triggers.
- `version: string` (required) — trigger definition version supplied by the governing library object.
- `provenance_refs: list[string]` (required) — provenance references for the trigger definition as carried by the library object.
- `lineage_refs: list[string]` (required) — lineage references for the trigger definition and owning library object.
- `source_ref: string` (required) — lineage anchor for the trigger definition, normally `library_object_ref`.
- `produced_by_motor: string` (required) — upstream producer of the governed trigger definition, normally `motor_011`; when copied into a motor_013 output envelope, the envelope records `motor_013` separately.
- `produced_at: datetime` (required) — timestamp from the governed trigger definition or validated copy used for evaluation.
- `parent_id: string | null` (required) — prior trigger condition version superseded by this trigger; null when none is declared.
- `version_id: string` (required) — stable version identifier for this trigger definition.
- `created_at: datetime` (required) — creation timestamp for the trigger definition or validated copy.
- `updated_at: datetime` (required) — latest metadata update timestamp for the trigger definition or validated copy.
- `version_hash: string` (required) — deterministic hash over the trigger definition, scope, required fields, case type, library object version and lineage fields.

`TriggerLogEntry`
- `trigger_log_id: string` (required) — stable canonical identifier for one trigger evaluation log entry.
- `record_id: string` (required) — generic record identifier equal to `trigger_log_id`.
- `trigger_condition_ref: string` (required) — evaluated `TriggerCondition.trigger_condition_id`.
- `facility_prior_ref: string` (required) — evaluated `motor_012.FacilityPrior` reference.
- `facility_id: string` (required) — facility identifier copied from the evaluated prior.
- `library_object_ref: string` (required) — library object that supplied the trigger.
- `evaluated_field_refs: list[string]` (required) — prior, bundle or quality field references read during trigger evaluation.
- `evaluation_result: enum[matched, not_matched, rejected]` (required) — per-trigger evaluation outcome.
- `reason_code: enum[TRIGGER_MATCHED, TRIGGER_NOT_MATCHED, REQUIRED_FIELD_MISSING, QUALITY_GATE_BLOCKED, INPUT_VALIDATION_ERROR, LIBRARY_OBJECT_INVALID, TRIGGER_SCOPE_MISMATCH]` (required) — machine-readable evaluation reason.
- `activation_record_ref: string` (required) — `ActivationRecord.activation_id` produced for the same evaluation.
- `case_ref: string | null` (required) — `InferenceCase.case_id` when the trigger produced or supported an activated case; null otherwise.
- `evaluated_at: datetime` (required) — timestamp when the trigger was evaluated.
- `activation_rule_version: string` (required) — version of the rule set used for evaluation.
- `provenance_refs: list[string]` (required) — upstream provenance references used by this evaluation.
- `lineage_id: string` (required) — canonical lineage reference for this log entry.
- `lineage_refs: list[string]` (required) — upstream lineage references needed to reconstruct this evaluation.
- `source_ref: string` (required) — lineage anchor, normally the evaluated prior plus trigger reference.
- `produced_by_motor: string` (required) — constant value `motor_013`.
- `produced_at: datetime` (required) — timestamp when this log entry was emitted.
- `parent_id: string | null` (required) — prior log entry superseded for the same prior, trigger and rule version lineage; null for first emission.
- `version_id: string` (required) — stable version identifier for this log entry.
- `created_at: datetime` (required) — creation timestamp for this log entry.
- `updated_at: datetime` (required) — latest metadata update timestamp.
- `version_hash: string` (required) — deterministic hash over trigger reference, prior reference, evaluated fields, evaluation result, reason code, rule version and lineage fields.

## relationships
- `InferenceCase.source_prior_ref` references `motor_012.FacilityPrior.facility_prior_id` or the accepted prior id supplied by the Fase 1 handoff; this relationship is read-only and cannot mutate the prior.
- `InferenceCase.contextual_bundle_refs[]` references `motor_012.ContextualBundle.bundle_id` values that belong to the same source prior or package context.
- `InferenceCase.library_object_refs[]` and `TriggerCondition.library_object_ref` reference `motor_011.LibraryObject.library_object_id`; this motor evaluates those references but does not curate, version or edit library objects.
- `InferenceCase.quality_record_refs[]` and `ActivationRecord.evaluated_input_refs[]` reference `motor_007.QualityRecord.quality_record_id` values used for quality gating; this motor does not recalculate quality.
- `InferenceCase.trigger_condition_ref` references the primary `TriggerCondition.trigger_condition_id` that opened the case.
- `InferenceCase.supporting_trigger_refs[]` references all `TriggerCondition.trigger_condition_id` values that matched the same facility, source prior and activation case type.
- `InferenceCase.activation_record_ref` references exactly one `ActivationRecord.activation_id` with `result = activated`.
- `ActivationRecord.case_id` references `InferenceCase.case_id` only when `result = activated`; it is null for rejected and not activated decisions.
- `ActivationRecord.trigger_condition_ref` references the evaluated `TriggerCondition.trigger_condition_id`.
- `TriggerLogEntry.trigger_condition_ref` references the same trigger evaluated by its paired `ActivationRecord`.
- `TriggerLogEntry.activation_record_ref` references the `ActivationRecord.activation_id` produced for that trigger evaluation.
- `TriggerLogEntry.case_ref` references `InferenceCase.case_id` only when the evaluated trigger matched or supported an activated case.
- `parent_id` fields reference the previous emitted entity of the same type only; they must not point to upstream prior, library object, quality record or downstream Decision Core records.
- `InferenceCase` outputs are the only records passed to `motor_014`; `ActivationRecord`, `TriggerCondition` copies and `TriggerLogEntry` records are audit and observability artifacts unless explicitly referenced by the activated case.

## identifiers
- `InferenceCase`: canonical identifier is `case_id`; `record_id` carries the same value. It is derived deterministically from `motor_013`, `facility_id`, `source_prior_ref`, `source_prior_version`, `activation_case_type`, the primary trigger condition id, supporting trigger set and `activation_rule_version`.
- `ActivationRecord`: canonical identifier is `activation_id`; `record_id` carries the same value. It is derived deterministically from `motor_013`, `source_prior_ref`, `trigger_condition_ref`, `trigger_version`, evaluated input references, `result`, `reason_code` and `activation_rule_version`.
- `TriggerCondition`: canonical identifier is `trigger_condition_id`; `record_id` carries the same value. It remains governed by the library object that supplied it and is derived from `library_object_ref`, `library_object_version`, condition expression reference, scope and trigger version.
- `TriggerLogEntry`: canonical identifier is `trigger_log_id`; `record_id` carries the same value. It is derived deterministically from `motor_013`, `source_prior_ref`, `trigger_condition_ref`, evaluated field references, evaluation result and `activation_rule_version`.
- Upstream identifiers from `motor_012`, `motor_011` and `motor_007` are preserved as references and are never replaced with locally invented ids.
- No entity uses mutable list position, display label, natural-language rationale or timestamp alone as a stable identifier.

## versioning
- All persisted entities carry `version_id`, `created_at`, `updated_at` and `version_hash`.
- `InferenceCase.version_hash` is computed from `facility_id`, `source_prior_ref`, `source_prior_version`, `contextual_bundle_refs`, `library_object_refs`, `trigger_condition_ref`, sorted `supporting_trigger_refs`, `activation_case_type`, `case_status`, `activation_rule_version`, `quality_record_refs`, `activation_rationale_code` and lineage fields.
- `ActivationRecord.version_hash` is computed from `case_id`, `facility_id`, `source_prior_ref`, sorted `evaluated_input_refs`, `trigger_condition_ref`, `trigger_version`, `activation_case_type`, `result`, `reason_code`, `decision_detail_refs`, `activation_rule_version` and lineage fields.
- `TriggerCondition.version_hash` is computed from `library_object_ref`, `library_object_version`, `condition_type`, `scope`, sorted `required_fields`, `activation_case_type`, `condition_expression_ref`, `allowed_result_values`, `trigger_priority`, `version` and lineage fields.
- `TriggerLogEntry.version_hash` is computed from `trigger_condition_ref`, `facility_prior_ref`, `facility_id`, `library_object_ref`, sorted `evaluated_field_refs`, `evaluation_result`, `reason_code`, `activation_record_ref`, `case_ref`, `activation_rule_version` and lineage fields.
- `created_at` is set once when the entity is first emitted or accepted into the activation envelope. `updated_at` changes only for governed metadata correction that preserves audit history.
- A material change to source prior version, contextual bundle references, library object version, trigger condition version, quality gating result, activation rule version, result, reason code or lineage requires a new `version_id` and `version_hash`.
- Re-running activation with the same accepted inputs and rule versions must reproduce the same identifiers and version hashes, excluding only non-material transport metadata.
- `parent_id` links a new versioned entity to the prior emitted entity of the same type when a governed rebuild, supersession or correction occurs.

## lineage
- All emitted motor_013 outputs carry `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `produced_by_motor` is always `motor_013` for `InferenceCase`, `ActivationRecord` and `TriggerLogEntry` records emitted by this motor. `TriggerCondition.produced_by_motor` preserves the upstream governed trigger producer when represented as an input/reference entity.
- `source_ref` identifies the lineage anchor: `source_prior_ref` for `InferenceCase`, the evaluated prior plus trigger reference for `ActivationRecord` and `TriggerLogEntry`, and `library_object_ref` for `TriggerCondition`.
- `produced_at` is the emission timestamp for motor_013 outputs and must be stable once persisted.
- `parent_id` is null for first emission and otherwise references the previous emitted entity of the same type for the same facility, source prior, trigger, case type and rule lineage.
- `lineage_id`, `lineage_refs` and `provenance_refs` must preserve references to the accepted `facility_prior`, contextual bundles, library objects, trigger definitions, quality records and activation rule version used during evaluation.
- Missing `source_ref`, missing `produced_by_motor`, missing `produced_at`, missing required parent linkage for supersession, missing quality record references or missing upstream lineage makes the entity invalid rather than silently repairable.
- Lineage fields are audit metadata only. They do not authorize this motor to analyze activated cases, mutate Fase 1 priors, rewrite library objects, recalculate quality or emit Decision Core conclusions.
