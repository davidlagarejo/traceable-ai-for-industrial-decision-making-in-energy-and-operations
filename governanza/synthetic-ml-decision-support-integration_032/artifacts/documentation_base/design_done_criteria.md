# Design Done Criteria — Synthetic ML Decision Support Integration

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

## criteria
- `master_concept_doc.md` defines purpose, concrete actions, explicit non-responsibilities and rationale for keeping motor_032 separate from motor_031 and motor_014.
- `functional_contract.md` lists all required inputs and outputs with source or consumer and includes hard limits prohibiting `decision_grade`, field evidence, Validation Data Bridge replacement and Verification Bridge replacement.
- `functional_contract.md` and `operational_rules.md` require `synthetic_support_flag=true` and `non_evidentiary_flag=true` on every output produced by this motor.
- `conceptual_schema.md` defines `SyntheticMLSupportRegister`, `HypothesisSignal` and `LabeledSupportRecord` with required identity, lineage, version, epistemic flag and limitation fields.
- `operational_rules.md` preserves the invariant that synthetic support remains subordinate and cannot elevate `hypothesis_only` inference records.
- `acceptance_tests.md` includes one happy path, edge cases for weak support and multiple matching candidates, and rejection criteria with explicit error signals.
- `failure_modes.md` identifies promotion leakage, flag omission, lineage break, contract bypass and limitation collapse as observable risks.
- All documentation_base files contain no open placeholder markers and are each larger than the minimum size required by Gate 1.
