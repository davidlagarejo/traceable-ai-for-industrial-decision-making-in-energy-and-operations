# Functional Contract — Synthetic ML Decision Support Integration

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

## inputs
- capability_demonstration_report: object — source motor_031; contains model capability findings over synthetic data, `source_problem_ref`, `expert_spec_ref`, `generator_version`, `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes`, `domain_validity_limits`, `limitations_note`, `synthetic_data_flag=true` and `non_evidentiary_flag=true`.
- inference_records: object collection — source motor_014; contains target `inference_record_id`, `inference_case_id`, current epistemic state, current decision grade, accepted signal classes and existing evidence references.
- phase_contracts: object collection — source motor_001; defines whether the receiving Decision Core phase accepts `synthetic_support` as subordinate input and which fields must be preserved in handoff.
- version_records: object collection — source motor_002; provides stable version ids, lineage ids and upstream object references for the report, inference record and emitted support records.

## outputs
- synthetic_ml_support_register: object — destination Decision Core and downstream priority engines; records the accepted synthetic support signal with `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `support_level`, `cannot_substitute`, lineage and explicit limitations.
- hypothesis_signal: object — destination motor_014 Decision Core; represents a subordinate signal attached to an inference record with `signal_role="subordinate"`, `evidence_level="synthetic_support"` and no authority to change decision grade.
- labeled_support_record: object — destination audit trail, Decision Core handoff and motor_033; wraps the support signal with labels, version references, source report reference, accepted use and rejection boundaries.

## limits
- The motor never accepts a `capability_demonstration_report` that lacks required synthetic chain flags, source references, generator metadata, limits or validation gaps.
- The motor never accepts an inference record whose receiving phase contract does not allow subordinate `synthetic_support`.
- The motor never produces `decision_grade`, `field_evidence`, `validation_data`, verification status or final TAD output.
- The motor never converts `hypothesis_only` `inference_records` to `decision_grade`.
- The motor never substitutes Validation Data Bridge or Verification Bridge and never emits output that can be interpreted as field validation.
- The motor never mutates upstream reports, inference records, phase contracts or version records; it only emits new labeled support objects.

## validations
- Reject input if `capability_demonstration_report.report_id`, `source_problem_ref`, `expert_spec_ref`, `generator_version`, `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes`, `domain_validity_limits` or `limitations_note` is missing or empty.
- Reject input if the report does not declare `non_evidentiary_flag=true`; for motor_032 outputs, always emit `synthetic_support_flag=true` and `non_evidentiary_flag=true`.
- Reject input if `inference_records` do not contain an `inference_record_id` matching the report `source_problem_ref` or an explicitly supplied target inference case.
- Reject processing if the target `phase_contracts` do not permit `synthetic_support` as a subordinate signal class for the Decision Core handoff.
- Reject processing if `version_records` cannot provide stable upstream references for the report and target inference record.
- Before emission, ensure every output includes `source_problem_ref`, `expert_spec_ref`, `intended_use="preliminary_support"`, `domain_validity_limits`, `limitations_note`, lineage id, version id and a `cannot_substitute` declaration where applicable.
- Before emission, ensure no output field requests or implies promotion to `decision_grade`, closure of a claim, replacement of field evidence or replacement of validation data.
