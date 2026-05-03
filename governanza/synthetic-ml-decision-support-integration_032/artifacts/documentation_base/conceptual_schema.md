# Conceptual Schema — Synthetic ML Decision Support Integration

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

## entities
- SyntheticMLSupportRegister: durable register entry that records one accepted `capability_demonstration_report` as non evidentiary synthetic support for a target inference record.
- HypothesisSignal: subordinate Decision Core signal derived from the support register and attached to an inference record without changing the claim's decision grade.
- LabeledSupportRecord: handoff and audit object that packages the signal, labels, lineage, version references and explicit substitution limits for downstream consumers.

## relationships
- capability_demonstration_report → SyntheticMLSupportRegister (one report creates zero or one register entry after validation).
- SyntheticMLSupportRegister → HypothesisSignal (one register entry creates one subordinate signal for the target inference record).
- HypothesisSignal → inference_record (many signals may attach to one inference record, but each signal remains subordinate and non evidentiary).
- SyntheticMLSupportRegister → LabeledSupportRecord (one register entry creates one labeled handoff record for audit and downstream preliminary prioritization).
- version_records → SyntheticMLSupportRegister, HypothesisSignal, LabeledSupportRecord (each emitted object stores upstream version and lineage references).
- phase_contracts → SyntheticMLSupportRegister (the register entry is only created when the receiving phase contract allows `synthetic_support`).

## key_fields
SyntheticMLSupportRegister:
- support_register_id: string
- source_report_id: string
- target_inference_record_id: string
- support_level: enum(`exploratory`, `preliminary_signal`, `capability_demo`)
- synthetic_support_flag: boolean
- non_evidentiary_flag: boolean
- cannot_substitute: list[string]
- lineage_id: string
- version_id: string

HypothesisSignal:
- hypothesis_signal_id: string
- target_inference_record_id: string
- signal_role: enum(`subordinate`)
- evidence_level: enum(`synthetic_support`)
- intended_use: enum(`preliminary_support`)
- source_problem_ref: string
- domain_validity_limits: string
- limitations_note: string

LabeledSupportRecord:
- labeled_support_record_id: string
- support_register_id: string
- labels: list[string]
- expert_spec_ref: string
- source_problem_ref: string
- upstream_version_refs: list[string]
- synthetic_support_flag: boolean
- non_evidentiary_flag: boolean
