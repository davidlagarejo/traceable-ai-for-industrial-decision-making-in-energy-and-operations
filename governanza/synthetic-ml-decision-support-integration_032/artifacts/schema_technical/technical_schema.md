# Technical Schema — Synthetic ML Decision Support Integration

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

This schema is complete for Gate 2 validation.
-->

## entities
- `SyntheticMLSupportRegister`: immutable register entry emitted by motor_032 after accepting one motor_031 `capability_demonstration_report` for one target `inference_record`. It records the support as subordinate, non evidentiary synthetic support with explicit substitution limits, version references and lineage. Stage: specified in `schema_technical`, produced during `implementation`, verified during `tests` and `conformance_review`.
- `HypothesisSignal`: subordinate Decision Core signal derived from a `SyntheticMLSupportRegister` and attached to an existing motor_014 inference record. It preserves the target record state and never authorizes decision-grade promotion, claim closure, validation or verification. Stage: specified in `schema_technical`, produced during `implementation`, verified during `tests` and `conformance_review`.
- `LabeledSupportRecord`: audit and handoff object that packages the register entry and hypothesis signal with labels, upstream versions, lineage, intended use and rejection boundaries for Decision Core, audit consumers and motor_033. Stage: specified in `schema_technical`, produced during `implementation`, verified during `tests` and `conformance_review`.

## fields
### SyntheticMLSupportRegister
- `support_register_id: string` (required) — canonical stable identifier for the register entry emitted by motor_032.
- `source_report_id: string` (required) — motor_031 `capability_demonstration_report.report_id` accepted as the synthetic support source.
- `source_ref: string` (required) — canonical lineage reference for the accepted source report and target inference bundle.
- `source_problem_ref: string` (required) — originating inference case identifier propagated from the report and matching the target inference record context.
- `expert_spec_ref: string` (required) — motor_029 `expert_problem_spec.spec_id` propagated from the capability report.
- `target_inference_record_id: string` (required) — existing motor_014 inference record that may receive the subordinate signal.
- `phase_contract_ref: string` (required) — motor_001 phase contract reference proving that subordinate `synthetic_support` is allowed for the receiving phase.
- `version_refs: dict[string, string]` (required) — motor_002 version identifiers for the source report, target inference record, phase contract and emitted register object.
- `generator_version: string` (required) — generator semantic version propagated from the capability report for traceability.
- `support_level: enum[exploratory, preliminary_signal, capability_demo]` (required) — declared synthetic support level allowed by the report and receiving phase.
- `intended_use: enum[preliminary_support]` (required) — fixed downstream use for motor_032 outputs handed to Decision Core.
- `domain_validity_limits: string` (required) — scope limits propagated from the capability report.
- `limitations_note: string` (required) — explicit statement that the support is synthetic, non evidentiary and not field validation.
- `gap_to_real_validation: string` (required) — real evidence or validation bridge gap propagated from the capability report.
- `gap_to_deployment: string` (required) — deployment gap propagated from the capability report.
- `known_failure_modes: list[string]` (required) — known synthetic-context failure modes propagated from the capability report.
- `cannot_substitute: list[string]` (required) — explicit list including Validation Data Bridge, Verification Bridge, field evidence, validation data, claim closure and final TAD output.
- `lineage_id: string` (required) — lineage graph identifier or lineage node reference supplied by motor_002 for this emitted object.
- `synthetic_support_flag: boolean` (required) — fixed `true`; required for every motor_032 output.
- `non_evidentiary_flag: boolean` (required) — fixed `true`; required for every motor_032 output.
- `produced_by_motor: string` (required) — fixed value `motor_032`.
- `produced_at: datetime` (required) — timestamp when motor_032 produced the register entry.
- `parent_id: string | null` (required) — prior `support_register_id` for a controlled correction; null for the first emitted version.
- `version_id: string` (required) — immutable version identifier for this register entry.
- `created_at: datetime` (required) — timestamp when this version was created.
- `updated_at: datetime` (required) — timestamp of the last allowed metadata registration for this immutable version; normally equal to `created_at`.
- `version_hash: string` (required) — deterministic hash over canonicalized register content, upstream references, flags, limits and version references.

### HypothesisSignal
- `hypothesis_signal_id: string` (required) — canonical stable identifier for the subordinate signal.
- `support_register_id: string` (required) — `SyntheticMLSupportRegister.support_register_id` from which this signal is derived.
- `source_report_id: string` (required) — motor_031 capability report referenced by the supporting register.
- `source_ref: string` (required) — canonical lineage reference shared with the supporting register.
- `source_problem_ref: string` (required) — originating inference case identifier propagated from the report and register.
- `expert_spec_ref: string` (required) — motor_029 expert spec reference propagated from the report and register.
- `target_inference_record_id: string` (required) — existing motor_014 inference record to which the signal is attached.
- `signal_role: enum[subordinate]` (required) — fixed subordinate role in Decision Core.
- `evidence_level: enum[synthetic_support]` (required) — fixed evidence level; never field evidence, validation data or verified evidence.
- `intended_use: enum[preliminary_support]` (required) — fixed allowed use for the signal.
- `permitted_effect: enum[exploration, preliminary_prioritization]` (required) — bounded effect allowed for the signal; it does not close claims or change decision grade.
- `decision_grade_change_allowed: boolean` (required) — fixed `false`.
- `domain_validity_limits: string` (required) — scope limits propagated from the register.
- `limitations_note: string` (required) — explicit non-evidentiary limitation statement.
- `version_refs: dict[string, string]` (required) — motor_002 version identifiers for the source report, target inference record, phase contract, support register and emitted signal.
- `lineage_id: string` (required) — lineage graph identifier or lineage node reference supplied by motor_002 for this emitted object.
- `synthetic_support_flag: boolean` (required) — fixed `true`; required for every motor_032 output.
- `non_evidentiary_flag: boolean` (required) — fixed `true`; required for every motor_032 output.
- `produced_by_motor: string` (required) — fixed value `motor_032`.
- `produced_at: datetime` (required) — timestamp when motor_032 produced the signal.
- `parent_id: string | null` (required) — prior `hypothesis_signal_id` for a controlled correction; null for the first emitted version.
- `version_id: string` (required) — immutable version identifier for this signal.
- `created_at: datetime` (required) — timestamp when this version was created.
- `updated_at: datetime` (required) — timestamp of the last allowed metadata registration for this immutable version; normally equal to `created_at`.
- `version_hash: string` (required) — deterministic hash over canonicalized signal content, upstream references, flags, limits and version references.

### LabeledSupportRecord
- `labeled_support_record_id: string` (required) — canonical stable identifier for the audit and handoff record.
- `support_register_id: string` (required) — `SyntheticMLSupportRegister.support_register_id` packaged by this record.
- `hypothesis_signal_id: string` (required) — `HypothesisSignal.hypothesis_signal_id` packaged by this record.
- `source_report_id: string` (required) — motor_031 capability report from which the packaged support derives.
- `source_ref: string` (required) — canonical lineage reference shared by the packaged register and signal.
- `source_problem_ref: string` (required) — originating inference case identifier propagated from the report, register and signal.
- `expert_spec_ref: string` (required) — motor_029 expert spec reference propagated from the report, register and signal.
- `target_inference_record_id: string` (required) — existing motor_014 inference record receiving the subordinate signal.
- `labels: list[string]` (required) — labels applied to the handoff; must include `synthetic_support`, `non_evidentiary`, `subordinate_signal` and `preliminary_support`.
- `support_level: enum[exploratory, preliminary_signal, capability_demo]` (required) — support level copied from the register.
- `intended_use: enum[preliminary_support]` (required) — fixed allowed use for downstream consumers.
- `destination_consumers: list[string]` (required) — declared consumers such as Decision Core handoff, audit trail and motor_033 preliminary prioritization.
- `rejection_boundaries: list[string]` (required) — prohibited interpretations, including decision-grade promotion, claim closure, field validation, Validation Data Bridge replacement and Verification Bridge replacement.
- `cannot_substitute: list[string]` (required) — explicit list of artifacts, phases or evidence classes the record cannot replace.
- `upstream_version_refs: list[string]` (required) — ordered upstream motor_002 version identifiers for the source report, inference record and phase contract.
- `version_refs: dict[string, string]` (required) — motor_002 version identifiers for all packaged objects and this emitted handoff record.
- `generator_version: string` (required) — generator semantic version propagated from the source report.
- `domain_validity_limits: string` (required) — scope limits propagated from the register and signal.
- `limitations_note: string` (required) — explicit non-evidentiary limitation statement.
- `lineage_id: string` (required) — lineage graph identifier or lineage node reference supplied by motor_002 for this emitted object.
- `synthetic_support_flag: boolean` (required) — fixed `true`; required for every motor_032 output.
- `non_evidentiary_flag: boolean` (required) — fixed `true`; required for every motor_032 output.
- `produced_by_motor: string` (required) — fixed value `motor_032`.
- `produced_at: datetime` (required) — timestamp when motor_032 produced the handoff record.
- `parent_id: string | null` (required) — prior `labeled_support_record_id` for a controlled correction; null for the first emitted version.
- `version_id: string` (required) — immutable version identifier for this handoff record.
- `created_at: datetime` (required) — timestamp when this version was created.
- `updated_at: datetime` (required) — timestamp of the last allowed metadata registration for this immutable version; normally equal to `created_at`.
- `version_hash: string` (required) — deterministic hash over canonicalized handoff content, labels, boundaries, upstream references, flags and version references.

## relationships
- `SyntheticMLSupportRegister.source_report_id` references motor_031 `CapabilityDemonstrationReport.report_id`. The referenced report must carry the required synthetic-chain flags, gaps, limits, `source_problem_ref`, `expert_spec_ref` and `generator_version`.
- `SyntheticMLSupportRegister.target_inference_record_id` references an existing motor_014 `inference_record_id`. The reference is read-only; motor_032 does not mutate the inference record or change its decision grade.
- `SyntheticMLSupportRegister.phase_contract_ref` references a motor_001 phase contract that permits `synthetic_support` only as a subordinate signal class.
- `SyntheticMLSupportRegister.version_refs` references motor_002 version records for the accepted capability report, target inference record, phase contract and emitted register entry.
- `HypothesisSignal.support_register_id` references exactly one `SyntheticMLSupportRegister.support_register_id`; one accepted register entry produces one subordinate hypothesis signal.
- `HypothesisSignal.target_inference_record_id` references the same motor_014 inference record as its supporting register and remains subordinate to any higher evidence class present in Decision Core.
- `LabeledSupportRecord.support_register_id` references exactly one `SyntheticMLSupportRegister.support_register_id`.
- `LabeledSupportRecord.hypothesis_signal_id` references exactly one `HypothesisSignal.hypothesis_signal_id`.
- `LabeledSupportRecord.upstream_version_refs[]` and `version_refs` reference motor_002 version identifiers for all packaged upstream and emitted objects.
- `source_problem_ref` and `expert_spec_ref` must match across the source capability report, support register, hypothesis signal and labeled support record.
- `cannot_substitute` and `rejection_boundaries` are required boundary fields; they are not foreign keys and must not be used to imply evidence, validation or verification authority.

## identifiers
- `SyntheticMLSupportRegister` canonical identifier: `support_register_id`. It must be unique within motor_032 and stable across reads; controlled corrections emit a new `support_register_id` with `parent_id` pointing to the prior register entry.
- `HypothesisSignal` canonical identifier: `hypothesis_signal_id`. It must be unique within motor_032 and stable across reads; controlled corrections emit a new `hypothesis_signal_id` with `parent_id` pointing to the prior signal.
- `LabeledSupportRecord` canonical identifier: `labeled_support_record_id`. It must be unique within motor_032 and stable across reads; controlled corrections emit a new `labeled_support_record_id` with `parent_id` pointing to the prior handoff record.
- Cross-entity references must use canonical IDs only: `support_register_id` for register references, `hypothesis_signal_id` for signal references and `labeled_support_record_id` for handoff references.
- External references remain externally owned strings: `source_report_id` belongs to motor_031, `target_inference_record_id` belongs to motor_014, `phase_contract_ref` belongs to motor_001, and `version_refs` or `upstream_version_refs` belong to motor_002.

## versioning
- Every `SyntheticMLSupportRegister`, `HypothesisSignal` and `LabeledSupportRecord` must include `version_id`, `created_at`, `updated_at` and `version_hash`.
- `version_id` is required and identifies the immutable version of the emitted object registered through motor_002 semantics.
- `created_at` is required and records when the object version was first created by motor_032.
- `updated_at` is required for uniform audit shape. Because motor_032 outputs are immutable once registered, it normally equals `created_at`; semantic changes require a new object version rather than in-place mutation.
- `version_hash` is required and must be computed deterministically from canonicalized object content, including canonical IDs, lineage references, upstream version references, epistemic flags, intended use, limits and explicit substitution boundaries.
- Any material change to source report reference, target inference record, phase contract, support level, labels, boundaries, flags, lineage or limitation text creates a new `version_id` and `version_hash`.
- `version_refs` is required on every emitted object to preserve motor_002 references for upstream inputs and the emitted object itself. `LabeledSupportRecord.upstream_version_refs` provides the ordered audit list used for handoff review.

## lineage
- Every `SyntheticMLSupportRegister`, `HypothesisSignal` and `LabeledSupportRecord` must include `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref` is required and anchors the accepted capability report plus the target inference record and phase contract bundle. It must resolve to the same `source_problem_ref` carried by the emitted object.
- `produced_by_motor` is required and must be the literal value `motor_032` for every emitted object.
- `produced_at` is required and records the timestamp when motor_032 produced the object.
- `parent_id` is required and is null for first-generation emitted objects. For controlled corrections, it stores the prior canonical ID of the same entity type.
- Lineage must preserve references to motor_031 capability reports, motor_014 inference records, motor_001 phase contracts and motor_002 version records without mutating any upstream object.
- Lineage validation fails if `source_problem_ref` or `expert_spec_ref` differs across the source report, register, signal and labeled support record.
- Lineage validation fails if an emitted object lacks `synthetic_support_flag=true`, lacks `non_evidentiary_flag=true`, implies `decision_grade`, or points to Validation Data Bridge, Verification Bridge, field evidence or validation data as something synthetic support can replace.
