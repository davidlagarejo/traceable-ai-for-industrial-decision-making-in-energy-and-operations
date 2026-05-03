# Test Spec — Synthetic ML Decision Support Integration

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

All placeholder markers in this test specification have been replaced with concrete test content.
-->

## happy_path
Input fixture:
- `capability_demonstration_report`: `report_id="cdr-031-0007"`, `source_ref="src-031-cdr-0007__ir-014-221__pc-001-dc-alpha"`, `source_problem_ref="case-014-221"`, `expert_spec_ref="eps-029-041"`, `generator_version="1.4.2"`, `gap_to_real_validation="requires 90 days of measured site outcomes"`, `gap_to_deployment="requires field calibration and monitoring plan"`, `known_failure_modes=["generator range too narrow"]`, `domain_validity_limits="valid only for synthetic scenarios defined by eps-029-041"`, `limitations_note="synthetic capability report; not evidence of real-world predictability"`, `synthetic_data_flag=true`, `non_evidentiary_flag=true`.
- `inference_records`: contains `inference_record_id="ir-014-221"`, `inference_case_id="case-014-221"`, `epistemic_state="hypothesis_only"`, `decision_grade=null`, `accepted_signal_classes=["synthetic_support", "library_knowledge"]`.
- `phase_contracts`: contains `phase_contract_ref="pc-001-dc-alpha"` with `allowed_subordinate_signal_classes=["synthetic_support"]` and no authorization for synthetic support to close claims.
- `version_records`: contains stable refs `capability_report="ver-031-cdr-0007"`, `inference_record="ver-014-ir-221"`, `phase_contract="ver-001-pc-alpha"` and emits lineage id `lin-032-0007`.

Expected output:
- One `synthetic_ml_support_register` with `support_register_id="smr-032-cdr-031-0007-ir-014-221"`, `source_report_id="cdr-031-0007"`, `target_inference_record_id="ir-014-221"`, `source_problem_ref="case-014-221"`, `expert_spec_ref="eps-029-041"`, `support_level="capability_demo"`, `intended_use="preliminary_support"`, `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `produced_by_motor="motor_032"`, `lineage_id="lin-032-0007"` and a populated `version_id`.
- The register `cannot_substitute` list includes `Validation Data Bridge`, `Verification Bridge`, `field_evidence`, `validation_data`, `claim_closure` and `final_TAD_output`.
- One `hypothesis_signal` with `signal_role="subordinate"`, `evidence_level="synthetic_support"`, `permitted_effect="preliminary_prioritization"` or `permitted_effect="exploration"`, `decision_grade_change_allowed=false`, and the same `source_problem_ref`, `expert_spec_ref`, `lineage_id` and epistemic flags as the register.
- One `labeled_support_record` with labels including `synthetic_support`, `non_evidentiary`, `subordinate_signal` and `preliminary_support`; its `rejection_boundaries` prohibit decision-grade promotion, claim closure, field validation, Validation Data Bridge replacement and Verification Bridge replacement.
- The input `inference_record` remains read-only: `epistemic_state` stays `hypothesis_only`, `decision_grade` stays `null`, and no upstream object content is mutated.

## sparse_case
Input fixture:
- The same required fields as the happy path are present, including `report_id`, `source_problem_ref`, `expert_spec_ref`, `generator_version`, `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes`, `domain_validity_limits`, `limitations_note`, `non_evidentiary_flag=true`, target inference record, phase contract and version refs.
- Optional report details that motor_032 does not consume are absent: `selected_model`, `metric_breakdown`, `narrative_summary`, `training_run_notes` and `model_artifact_ref`.
- `parent_id` is not supplied by the caller because this is a first-generation support registration.

Expected behavior:
- The motor does not reject the input for missing optional analytic details owned by motor_031.
- The emitted `SyntheticMLSupportRegister`, `HypothesisSignal` and `LabeledSupportRecord` still include every required motor_032 field from the technical schema.
- `parent_id` is emitted as `null` on all three output objects.
- The output preserves the exact `domain_validity_limits`, `limitations_note`, validation gap, deployment gap and `known_failure_modes` text supplied by the source report.
- The output remains non-evidentiary and subordinate: `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `evidence_level="synthetic_support"` and `decision_grade_change_allowed=false`.

## malformed_input
Malformed fixtures and required rejection behavior:
- Missing epistemic flag: if `capability_demonstration_report.non_evidentiary_flag` is absent or false, reject before emission with `error_code="MISSING_EPISTEMIC_FLAGS"` and produce no support objects.
- Wrong type on known failures: if `known_failure_modes="generator range too narrow"` is a string instead of `list[string]`, reject with `error_code="INVALID_FIELD_TYPE"` and `field="known_failure_modes"`.
- Missing target record: if no `inference_record.inference_case_id` equals `source_problem_ref="case-014-221"`, reject with `error_code="NO_TARGET_INFERENCE_RECORD"` and do not attach support to a similar but non-matching record.
- Phase contract denial: if the matching `phase_contract` omits `synthetic_support` from `allowed_subordinate_signal_classes`, reject with `error_code="PHASE_CONTRACT_DISALLOWS_SYNTHETIC_SUPPORT"`.
- Missing lineage: if `version_records` cannot provide stable refs for the source report and target inference record, reject with `error_code="MISSING_LINEAGE_REFERENCE"`.
- Promotion request: if the input payload asks for `decision_grade_change_allowed=true`, claim closure, Validation Data Bridge replacement or Verification Bridge replacement, reject with `error_code="PROMOTION_REQUEST_FORBIDDEN"`.

## edge_cases
1. Weak but structurally valid capability report.
   Input: the source report states that the synthetic model did not meet the motor_031 primary metric threshold, but all required references, flags, gaps and limitations are present.
   Expected behavior: motor_032 may emit `support_level="exploratory"` only if the phase contract allows subordinate synthetic support; it must preserve the weak-capability limitation and must not treat weak metrics as a fatal structural error.

2. Multiple candidate inference records.
   Input: `inference_records` contains `ir-014-221` with `inference_case_id="case-014-221"` and `ir-014-222` with related wording but `inference_case_id="case-014-222"`.
   Expected behavior: support attaches only to `ir-014-221`; no signal, register or handoff record is produced for `ir-014-222`.

3. Target inference record already has stronger evidence.
   Input: the target record has existing `field_evidence` or `validation_data` references.
   Expected behavior: the synthetic signal is still emitted only as subordinate `synthetic_support`; output ordering, labels and `cannot_substitute` make clear that real evidence outranks the synthetic signal.

4. Very long domain limitation text.
   Input: `domain_validity_limits` contains a long restrictive statement with scenario boundaries, excluded populations and generator assumptions.
   Expected behavior: the full text is preserved in all applicable outputs without broadening or summarizing it into a stronger claim.

5. First controlled correction.
   Input: a corrected capability report version is accepted for the same source report and target inference record with prior ids `smr-032-cdr-031-0007-ir-014-221`, `hs-032-cdr-031-0007-ir-014-221` and `lsr-032-cdr-031-0007-ir-014-221`.
   Expected behavior: new output ids and `version_id` values are emitted; each `parent_id` points to the prior id of the same entity type; no prior object is mutated in place.

## pass_criteria
The test passes when all of the following are observable:
- Exactly one register, one hypothesis signal and one labeled support record are emitted for a valid accepted input.
- All emitted objects include `source_problem_ref`, `expert_spec_ref`, `source_ref`, `lineage_id`, `version_id`, `version_hash`, `produced_by_motor="motor_032"`, `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `intended_use="preliminary_support"` and non-empty limitation fields.
- `HypothesisSignal.signal_role="subordinate"`, `HypothesisSignal.evidence_level="synthetic_support"` and `HypothesisSignal.decision_grade_change_allowed=false`.
- `SyntheticMLSupportRegister.cannot_substitute` and `LabeledSupportRecord.rejection_boundaries` explicitly prohibit replacement of Validation Data Bridge, Verification Bridge, field evidence, validation data, claim closure and final TAD output.
- `source_problem_ref` and `expert_spec_ref` match across the source report, register, hypothesis signal and labeled support record.
- Existing `capability_demonstration_report`, `inference_record`, `phase_contract` and `version_record` inputs are referenced but not mutated.
- Malformed inputs return the specified structured `error_code` and emit zero support objects.

## fail_criteria
The test fails if any of the following are observed:
- Any emitted object lacks `synthetic_support_flag=true` or `non_evidentiary_flag=true`.
- Any output implies `decision_grade`, verified status, claim closure, field validation, Validation Data Bridge replacement or Verification Bridge replacement.
- The target inference record changes from `hypothesis_only` to `decision_grade`, or any upstream input object is mutated in place.
- A support object is emitted when required fields are missing, when field types are invalid, when lineage refs are unavailable, or when the phase contract disallows subordinate `synthetic_support`.
- Support attaches to an inference record whose `inference_case_id` does not exactly match the source report `source_problem_ref`.
- `domain_validity_limits`, `limitations_note`, `gap_to_real_validation`, `gap_to_deployment` or `known_failure_modes` are dropped, overwritten or broadened.
- A malformed input produces an unstructured exception, a silent correction, a partially emitted output bundle or an error code different from the one specified for that condition.
