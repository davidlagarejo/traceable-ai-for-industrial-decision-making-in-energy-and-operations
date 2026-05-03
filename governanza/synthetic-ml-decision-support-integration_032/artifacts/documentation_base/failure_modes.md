# Failure Modes — Synthetic ML Decision Support Integration

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

## failure_modes_list
- EPISTEMIC_PROMOTION_LEAK: an output causes or implies `decision_grade`, claim closure, verification or field validation from synthetic support.
- FLAG_OMISSION: an emitted object lacks `synthetic_support_flag=true` or `non_evidentiary_flag=true`, making downstream consumers unable to distinguish synthetic support from stronger evidence.
- LINEAGE_BREAK: the support record cannot be traced back to the source `capability_demonstration_report`, target inference record, phase contract and version records.
- CONTRACT_BYPASS: the motor emits support even though the receiving phase contract does not allow subordinate `synthetic_support`.
- LIMITATION_COLLAPSE: `domain_validity_limits`, `limitations_note`, `gap_to_real_validation` or `known_failure_modes` are dropped or summarized so broadly that the signal appears stronger than the source report permits.

## anti_patterns
- Treating a high synthetic ML metric as real-world validation or as sufficient basis for final decision status.
- Using this motor as a fallback when Validation Data Bridge or Verification Bridge lacks data.
- Attaching synthetic support to all similar inference records instead of the exact `source_problem_ref`.
- Silently filling missing report metadata from assumptions or nearby records.

## degradation_signals
- Increase in outputs where `support_level` is stronger than the source report language supports.
- Any occurrence of emitted objects missing `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `source_problem_ref` or `lineage_id`.
- Repeated `PROMOTION_REQUEST_FORBIDDEN` rejections, indicating upstream consumers are trying to use synthetic support as evidence.
- Register entries whose `cannot_substitute` field is empty or omits Validation Data Bridge and Verification Bridge.
- Signals attached to inference records with no exact `source_problem_ref` match.
- Audit trail gaps where version ids cannot reconstruct the path from report to support record.
