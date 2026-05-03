# Acceptance Tests — Synthetic ML Decision Support Integration

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

Sections below are fully specified for the documentation_base gate.
-->

## happy_path
Input: `capability_demonstration_report.report_id="cdr-031-0007"` declares `source_problem_ref="case-014-221"`, `expert_spec_ref="eps-029-041"`, `generator_version="1.4.2"`, `gap_to_real_validation="requires 90 days of measured site outcomes"`, `gap_to_deployment="requires field calibration and monitoring plan"`, `known_failure_modes=["generator range too narrow"]`, `domain_validity_limits="valid only for synthetic scenarios defined by eps-029-041"`, `limitations_note="not evidence of real-world predictability"`, `synthetic_data_flag=true` and `non_evidentiary_flag=true`. `inference_records` contains `inference_record_id="ir-014-221"` for `case-014-221` with `epistemic_state="hypothesis_only"`. `phase_contracts` allows subordinate `synthetic_support`, and `version_records` contains stable references for the report and inference record.

Action: the motor validates all required fields, confirms the allowed handoff class, creates lineage references and emits support objects.

Expected output: one `synthetic_ml_support_register`, one `hypothesis_signal` and one `labeled_support_record`. All outputs contain `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `source_problem_ref="case-014-221"`, `expert_spec_ref="eps-029-041"`, `intended_use="preliminary_support"`, stable lineage and version ids. The target inference record remains `hypothesis_only`; no `decision_grade`, field evidence or validation status is produced.

## edge_cases
- Capability demonstrated but weak support: if the report documents capability failure or metrics below motor_031 threshold while still being structurally valid, the motor may emit `support_level="exploratory"` with limitations and known failure modes preserved; it must not reject solely because the demonstration is weak.
- Multiple candidate inference records: if several `inference_records` share contextual similarity but only one matches `source_problem_ref`, the motor attaches support only to the exact matching record and emits no signal for the others.
- Existing real evidence on target record: if the target inference record already has `field_evidence` or `validation_data`, the synthetic signal is still labeled `synthetic_support` and subordinate; it cannot override or outrank the real evidence.
- Broad domain limits: if `domain_validity_limits` is long or restrictive, the output preserves the full limitation text and does not compress it into a broader claim.

## rejection_criteria
- Reject with `MISSING_EPISTEMIC_FLAGS` when the input report lacks `non_evidentiary_flag=true` or contains inconsistent synthetic chain flags.
- Reject with `MISSING_LINEAGE_REFERENCE` when `version_records` cannot provide stable upstream refs for the report or target inference record.
- Reject with `PHASE_CONTRACT_DISALLOWS_SYNTHETIC_SUPPORT` when the relevant phase contract does not permit subordinate `synthetic_support`.
- Reject with `NO_TARGET_INFERENCE_RECORD` when no `inference_record` matches the report `source_problem_ref`.
- Reject with `PROMOTION_REQUEST_FORBIDDEN` when input requests promotion to `decision_grade`, claim closure or replacement of Validation Data Bridge or Verification Bridge.
