# Failure Modes Spec — Synthetic ML Decision Support Integration

Motor ID: motor_032

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Integrar capability_demonstration_report al Decision Core como señal subordinada etiquetada.
why_it_exists:  El Decision Core necesita recibir soporte sintético de forma trazable, etiquetada y epistemológicamente limitada.
key_inputs:     capability_demonstration_report (motor_031), inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    synthetic_ml_support_register, hypothesis_signal, labeled_support_record
key_objects:    SyntheticMLSupportRegister, HypothesisSignal, LabeledSupportRecord
what_not_to_do: No puede convertir hypothesis_only inference_records a decision_grade. No sustituye Validation Data Bridge ni Verification Bridge.
design_notes:   No puede elevar claims. No puede sustituir evidencia real. synthetic_support_flag=true en todo output.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true

All placeholder markers in this failure mode specification have been replaced with concrete content.
-->

## failure_modes_list
- EPISTEMIC_FLAG_LOSS: accepted `capability_demonstration_report` or emitted support object lacks `synthetic_support_flag=true` or `non_evidentiary_flag=true` -> downstream Decision Core cannot distinguish the signal from stronger evidence classes -> reject the bundle before emission, return `MISSING_EPISTEMIC_FLAGS`, and require corrected source metadata from the producing stage.
- SYNTHETIC_PROMOTION_LEAK: input payload, phase contract mapping or output template sets `decision_grade_change_allowed=true`, assigns `evidence_level` other than `synthetic_support`, or implies claim closure -> `HypothesisSignal` appears capable of changing `inference_record.epistemic_state` or `decision_grade` -> abort emission with `PROMOTION_REQUEST_FORBIDDEN`, preserve upstream objects unchanged, and force the caller to submit a subordinate-only request.
- TARGET_RECORD_MISMATCH: `capability_demonstration_report.source_problem_ref` does not exactly match any candidate `inference_record.inference_case_id`, or multiple records are selected by fuzzy similarity -> support attaches to an unrelated inference record or to more than one target -> reject with `NO_TARGET_INFERENCE_RECORD` or an explicit ambiguity error and require an exact target reference before retry.
- PHASE_CONTRACT_BYPASS: `phase_contracts` do not list `synthetic_support` in `allowed_subordinate_signal_classes` or omit the receiving phase contract reference -> a `SyntheticMLSupportRegister` is emitted without Decision Core authorization for synthetic support -> reject with `PHASE_CONTRACT_DISALLOWS_SYNTHETIC_SUPPORT` and emit no register, signal or labeled support record.
- LINEAGE_OR_VERSION_BREAK: `version_records` cannot supply stable refs for the source report, target inference record, phase contract and emitted objects -> `source_ref`, `lineage_id`, `version_id` or `version_hash` becomes non-reconstructible -> reject with `MISSING_LINEAGE_REFERENCE`, keep prior versions immutable and rerun only after motor_002 references are available.
- LIMITATION_COLLAPSE: `domain_validity_limits`, `limitations_note`, `gap_to_real_validation`, `gap_to_deployment` or `known_failure_modes` are truncated, generalized or rewritten into stronger language -> synthetic support appears broader or more validated than the motor_031 report permits -> block emission, preserve the original limitation text verbatim and require the output bundle to carry all limitation fields.
- PARTIAL_BUNDLE_EMISSION: one of the three outputs is emitted while another fails validation -> Decision Core receives an orphan `HypothesisSignal`, `SyntheticMLSupportRegister` or `LabeledSupportRecord` without matching IDs and lineage -> treat emission as atomic, discard the partial bundle and rerun after all entities pass validation together.
- UPSTREAM_MUTATION: implementation updates the source `capability_demonstration_report`, target `inference_record`, `phase_contract` or `version_record` while registering support -> audit history loses the distinction between input state and motor_032 output state -> stop processing, restore the read-only upstream reference model and emit a new corrected support object version rather than mutating prior records.

## anti_patterns
- Coupling motor_032 directly to motor_014 state mutation APIs so that support registration can alter `epistemic_state`, `decision_grade`, claim closure or verification fields.
- Treating high motor_031 synthetic metrics as evidence strength and mapping them to `field_evidence`, `validation_data`, verified status or final TAD output.
- Replacing the exact `source_problem_ref` match with fuzzy matching, text similarity or bulk attachment to all related inference records.
- Generating `cannot_substitute` or `rejection_boundaries` from optional prose instead of fixed mandatory boundaries that include Validation Data Bridge, Verification Bridge, field evidence, validation data, claim closure and final TAD output.
- Silently filling missing `expert_spec_ref`, `generator_version`, `lineage_id`, `version_refs`, `domain_validity_limits` or validation gaps from nearby records or default values.
- Collapsing `SyntheticMLSupportRegister`, `HypothesisSignal` and `LabeledSupportRecord` into one mutable object that loses separate identifiers, version hashes, parent IDs or handoff labels.
- Allowing output templates, operator notes or downstream requests to override `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `signal_role="subordinate"` or `decision_grade_change_allowed=false`.
- Using this motor as a fallback path when Validation Data Bridge or Verification Bridge lacks real evidence, instead of preserving synthetic support as non-evidentiary preliminary support.
- Reusing existing support object IDs for controlled corrections instead of emitting new immutable IDs with `parent_id` pointing to the prior same-type object.

## degradation_signals
- Any validation log containing `MISSING_EPISTEMIC_FLAGS`, emitted object audits with `synthetic_support_flag != true`, or emitted object audits with `non_evidentiary_flag != true`.
- Any `HypothesisSignal` audit where `signal_role` differs from `subordinate`, `evidence_level` differs from `synthetic_support`, or `decision_grade_change_allowed` differs from `false`.
- Rising counts of `PROMOTION_REQUEST_FORBIDDEN` rejections, especially from the same downstream consumer, indicating pressure to use synthetic support as evidentiary decision input.
- `SyntheticMLSupportRegister.cannot_substitute` or `LabeledSupportRecord.rejection_boundaries` missing Validation Data Bridge, Verification Bridge, field evidence, validation data, claim closure or final TAD output.
- Mismatch rate greater than zero between source report `source_problem_ref` and target `inference_record.inference_case_id` in accepted bundles.
- Accepted bundle count where any one of `support_register_id`, `hypothesis_signal_id` or `labeled_support_record_id` is absent while another is present.
- Any emitted object missing `source_ref`, `lineage_id`, `version_id`, `version_hash`, `produced_by_motor="motor_032"` or upstream motor_002 version references.
- Output limitation field length materially shorter than the corresponding source report limitation field, or logs indicating summarization of `domain_validity_limits`, `limitations_note`, `gap_to_real_validation`, `gap_to_deployment` or `known_failure_modes`.
- Nonzero attempts to attach one source report to multiple target inference records without explicit separate accepted reports and exact matching `source_problem_ref` values.
- `updated_at` diverging from `created_at` on immutable first-generation objects without a new `version_id`, new `version_hash` and same-type `parent_id`.

## expensive_errors
- Mislabeling synthetic support as evidentiary: expensive because downstream inference records, priorities and audit trails may treat a synthetic capability demo as real validation, forcing manual review of every derived decision path; prevent with hard validation of `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `evidence_level="synthetic_support"` and `decision_grade_change_allowed=false` before any object is emitted.
- Dropping lineage or version references: expensive because later reviewers cannot reconstruct which report, inference record, phase contract and generator version produced the support signal; prevent by rejecting emission unless `source_ref`, `lineage_id`, `version_refs`, `version_id` and `version_hash` are complete for all three output entities.
- Attaching support to the wrong inference record: expensive because synthetic support may contaminate unrelated cases and downstream motor_033 prioritization, requiring case-by-case cleanup; prevent by requiring exact equality between `capability_demonstration_report.source_problem_ref` and the selected `inference_record.inference_case_id`.
- Mutating upstream inference or report objects in place: expensive because it destroys the audit boundary between input evidence state and motor_032 synthetic support output; prevent by enforcing read-only upstream inputs and emitting new immutable support object versions for corrections.
- Emitting partial bundles: expensive because orphan signals or registers cannot be safely consumed by Decision Core or audit consumers and may require graph repair; prevent by validating and committing `SyntheticMLSupportRegister`, `HypothesisSignal` and `LabeledSupportRecord` as one atomic output bundle.
- Weakening limitation text: expensive because overly broad support labels can travel into downstream prioritization and reports before anyone notices the original motor_031 constraints; prevent by copying `domain_validity_limits`, `limitations_note`, `gap_to_real_validation`, `gap_to_deployment` and `known_failure_modes` without broadening or omission.
- Ignoring phase contract restrictions: expensive because it creates support records that the receiving phase is not authorized to consume, requiring rollback across Decision Core handoffs; prevent by rejecting any bundle whose `phase_contract_ref` does not explicitly allow subordinate `synthetic_support`.
