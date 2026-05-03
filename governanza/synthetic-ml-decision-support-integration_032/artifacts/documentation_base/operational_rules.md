# Operational Rules — Synthetic ML Decision Support Integration

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

## rules
1. Every emitted object must include `synthetic_support_flag=true` and `non_evidentiary_flag=true`.
2. The motor may attach synthetic support only as a subordinate signal to an existing `inference_record`; it may not create a primary inference record.
3. A target `inference_record` with status `hypothesis_only` remains `hypothesis_only` after this motor emits support records.
4. The motor must reject any input report that lacks `source_problem_ref`, `expert_spec_ref`, `generator_version`, `domain_validity_limits` or `limitations_note`.
5. The motor must preserve upstream lineage from motor_031, motor_014, motor_001 and motor_002 in each output object.
6. The motor must set `intended_use="preliminary_support"` for outputs handed to Decision Core.
7. The motor must include `cannot_substitute` with explicit references to Validation Data Bridge, Verification Bridge, field evidence and validation data in each `synthetic_ml_support_register`.
8. The motor must emit structured rejection errors rather than silently downgrading, correcting or inferring missing epistemic labels.

## invariants
- `source_problem_ref` is never null for accepted input or emitted output.
- `expert_spec_ref` is never null for accepted input or emitted output.
- `lineage_id` is never null after output creation.
- `version_id` is never null after output creation.
- `evidence_level` remains `synthetic_support` for all signals produced by this motor.
- `non_evidentiary_flag` remains `true` for all outputs produced by this motor.
- Upstream objects are referenced, not mutated.

## forbidden_operations
- Converting `hypothesis_only` `inference_records` to `decision_grade`.
- Substituting Validation Data Bridge or Verification Bridge.
- Marking synthetic support as `field_evidence`, `validation_data` or verified evidence.
- Closing an inference case based on synthetic support alone.
- Recomputing model metrics, retraining models or selecting production models.
- Removing or weakening `synthetic_support_flag=true` or `non_evidentiary_flag=true`.
- Editing upstream `capability_demonstration_report`, `phase_contracts`, `version_records` or existing `inference_records`.
- Producing final TAD output, final priority decisions or deployment-ready model artifacts.
