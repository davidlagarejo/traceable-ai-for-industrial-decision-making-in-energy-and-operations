# Technical Schema — Decision Core / Inference Engine

Motor ID: motor_014

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
why_it_exists:  Es el corazón analítico de Fase 2.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001)
key_outputs:    inference_record, tension_record, gap_agenda, validation_agenda
key_objects:    InferenceRecord, Tension, ValidationAgenda
what_not_to_do: No produce reportes finales. No verifica claims. Solo infiere y registra con contratos explícitos.
design_notes:   Determinismo primero. La IA puede asistir pero no decide. Depende de motor_013 y motor_001.

Sections below define the completed technical schema for this motor.
-->

## entities
- `InferenceRecord`: primary deterministic output for one activated inference case. It records the permitted inference state, evidence basis, phase contract boundary, rule version, version metadata, and lineage required for reconstruction. Stage: `schema_technical` as the canonical output object for the later implementation stage.
- `Tension`: conflict, inconsistency, opportunity, missing-evidence, or contract-limit signal derived from an `InferenceRecord`. It never resolves the conflict by itself; it records the pressure and the validation requirement. Stage: `schema_technical` as a child output object emitted with the inference batch.
- `GapAgenda`: ordered agenda of missing evidence, missing validation data, unresolved tension, or contract-limited conditions that prevent a stronger inference state. Stage: `schema_technical` as a structured derived output from an `InferenceRecord` and any related `Tension` records.
- `ValidationAgenda`: downstream validation plan derived from the inference and gap agenda. It lists required evidence level, reason, priority, and handoff target without performing validation or claim verification. Stage: `schema_technical` as the handoff object for downstream validation or verification motors.

## fields
`InferenceRecord`
- `inference_id: string` (required) — stable identifier for this inference record.
- `motor_id: string` (required) — constant value `motor_014`.
- `case_id: string` (required) — reference to the activated `InferenceCase.case_id` from `motor_013`.
- `activation_record_ref: string` (required) — reference to the activation record that authorized the case.
- `trigger_log_ref: string` (required) — reference to the trigger log associated with the activated case.
- `phase_id: string` (required) — phase identifier shared by the case and the matching phase contract.
- `phase_contract_ref: string` (required) — reference to the `PhaseContract.contract_id` from `motor_001`.
- `contract_version: string` (required) — version of the phase contract used to authorize processing.
- `analysis_question: string` (required) — bounded question copied from the activated inference case.
- `inference_state: enum[hypothesis_only, bounded_inference, blocked_by_gap]` (required) — deterministic state assigned under the contract and evidence rules.
- `inference_basis: list[string]` (required) — normalized references to evidence, case signals, or rule inputs used to produce the state.
- `evidence_refs: list[EvidenceRef]` (required) — evidence references with identifier, source class or evidence level, and provenance or lineage.
- `lineage_refs: list[string]` (required) — upstream lineage references needed to reconstruct the record.
- `rule_version: string` (required) — deterministic rule set version applied by this motor.
- `decision_trace: list[string]` (required) — ordered rule or condition identifiers that explain how the state was selected.
- `synthetic_support_present: boolean` (required) — true when the case includes synthetic or non-evidentiary support.
- `created_at: datetime` (required) — creation timestamp for this record.
- `updated_at: datetime` (required) — last update timestamp; equals `created_at` for immutable first emission.
- `version_id: string` (required) — version identifier for the emitted record.
- `version_hash: string` (required) — deterministic hash over canonicalized content, version metadata, and lineage.
- `source_ref: string` (required) — canonical upstream source reference, normally the `case_id`.
- `produced_by_motor: string` (required) — constant value `motor_014`.
- `produced_at: datetime` (required) — production timestamp for lineage.
- `parent_id: string | null` (required) — previous `InferenceRecord.inference_id` when this record supersedes an earlier version; otherwise null.

`Tension`
- `tension_id: string` (required) — stable identifier for this tension record.
- `motor_id: string` (required) — constant value `motor_014`.
- `inference_id: string` (required) — reference to the owning `InferenceRecord`.
- `case_id: string` (required) — copied reference to the activated case for direct traceability.
- `phase_contract_ref: string` (required) — contract reference inherited from the owning inference.
- `contract_version: string` (required) — phase contract version inherited from the owning inference.
- `tension_type: enum[conflict, inconsistency, opportunity, missing_evidence, contract_limit]` (required) — deterministic category of the analytical pressure.
- `severity: enum[low, medium, high, blocking]` (required) — impact level assigned by deterministic rules.
- `source_refs: list[string]` (required) — evidence, trigger, contract, or case references that produced the tension.
- `description: string` (required) — concise structured statement of the tension without report narrative or final claim language.
- `requires_validation: boolean` (required) — true when the tension must create or feed a validation agenda item.
- `related_gap_item_ids: list[string]` (required) — gap items created from this tension; empty list when no gap is derived.
- `lineage_refs: list[string]` (required) — upstream lineage references inherited from the inference and tension sources.
- `rule_version: string` (required) — deterministic rule set version used to classify the tension.
- `created_at: datetime` (required) — creation timestamp for this record.
- `updated_at: datetime` (required) — last update timestamp; equals `created_at` for immutable first emission.
- `version_id: string` (required) — version identifier for the tension record.
- `version_hash: string` (required) — deterministic hash over canonicalized content, version metadata, and lineage.
- `source_ref: string` (required) — canonical upstream source reference, normally the owning `inference_id` or source evidence reference.
- `produced_by_motor: string` (required) — constant value `motor_014`.
- `produced_at: datetime` (required) — production timestamp for lineage.
- `parent_id: string | null` (required) — previous `tension_id` when this record supersedes an earlier version; otherwise null.

`GapAgenda`
- `gap_agenda_id: string` (required) — stable identifier for the gap agenda associated with one inference.
- `motor_id: string` (required) — constant value `motor_014`.
- `inference_id: string` (required) — reference to the owning `InferenceRecord`.
- `case_id: string` (required) — copied reference to the activated case for direct traceability.
- `phase_contract_ref: string` (required) — contract reference inherited from the owning inference.
- `contract_version: string` (required) — phase contract version inherited from the owning inference.
- `gap_items: list[GapItem]` (required) — ordered items describing missing condition, affected object, required action, and priority.
- `priority_order: list[string]` (required) — ordered list of `gap_item_id` values from highest to lowest operational priority.
- `validation_dependency_refs: list[string]` (required) — references to validation agenda items, downstream routes, or required evidence dependencies.
- `lineage_refs: list[string]` (required) — upstream lineage references inherited from the inference, source evidence, and related tensions.
- `rule_version: string` (required) — deterministic rule set version used to derive gap items.
- `created_at: datetime` (required) — creation timestamp for this record.
- `updated_at: datetime` (required) — last update timestamp; equals `created_at` for immutable first emission.
- `version_id: string` (required) — version identifier for the gap agenda.
- `version_hash: string` (required) — deterministic hash over canonicalized content, version metadata, and lineage.
- `source_ref: string` (required) — canonical upstream source reference, normally the owning `inference_id`.
- `produced_by_motor: string` (required) — constant value `motor_014`.
- `produced_at: datetime` (required) — production timestamp for lineage.
- `parent_id: string | null` (required) — previous `gap_agenda_id` when this agenda supersedes an earlier version; otherwise null.

`GapItem`
- `gap_item_id: string` (required) — stable identifier for the individual gap item.
- `gap_type: enum[missing_evidence, missing_validation_data, unresolved_conflict, contract_limit]` (required) — deterministic gap category.
- `affected_ref: string` (required) — `inference_id`, `tension_id`, or source reference affected by the gap.
- `missing_condition: string` (required) — specific missing evidence, metadata, validation data, or contract condition.
- `required_downstream_action: string` (required) — action expected from a downstream validation or verification flow.
- `priority: enum[low, medium, high, blocking]` (required) — priority assigned by deterministic rules.
- `source_refs: list[string]` (required) — source references used to create the gap item.

`ValidationAgenda`
- `validation_agenda_id: string` (required) — stable identifier for the validation agenda associated with one inference.
- `motor_id: string` (required) — constant value `motor_014`.
- `inference_id: string` (required) — reference to the owning `InferenceRecord`.
- `case_id: string` (required) — copied reference to the activated case for direct traceability.
- `gap_agenda_id: string` (required) — reference to the `GapAgenda` that triggered or organized validation needs.
- `phase_contract_ref: string` (required) — contract reference inherited from the owning inference.
- `contract_version: string` (required) — phase contract version inherited from the owning inference.
- `validation_items: list[ValidationItem]` (required) — ordered validation needs derived from gap items or blocking tensions.
- `required_evidence_level: enum[validation_data, field_evidence]` (required) — strongest evidence level required by any agenda item.
- `handoff_target: string` (required) — downstream motor, workflow, or queue designated by the phase contract.
- `lineage_refs: list[string]` (required) — upstream lineage references inherited from inference, gap, tension, and evidence sources.
- `rule_version: string` (required) — deterministic rule set version used to create the validation agenda.
- `created_at: datetime` (required) — creation timestamp for this record.
- `updated_at: datetime` (required) — last update timestamp; equals `created_at` for immutable first emission.
- `version_id: string` (required) — version identifier for the validation agenda.
- `version_hash: string` (required) — deterministic hash over canonicalized content, version metadata, and lineage.
- `source_ref: string` (required) — canonical upstream source reference, normally the related `gap_agenda_id` or owning `inference_id`.
- `produced_by_motor: string` (required) — constant value `motor_014`.
- `produced_at: datetime` (required) — production timestamp for lineage.
- `parent_id: string | null` (required) — previous `validation_agenda_id` when this agenda supersedes an earlier version; otherwise null.

`ValidationItem`
- `validation_item_id: string` (required) — stable identifier for the individual validation item.
- `gap_item_id: string` (required) — reference to the gap item that created this validation need.
- `required_evidence_level: enum[validation_data, field_evidence]` (required) — required evidence class for this item.
- `reason: string` (required) — specific reason validation is needed.
- `handoff_target: string` (required) — downstream target authorized by the phase contract.
- `priority: enum[low, medium, high, blocking]` (required) — priority inherited from or derived from the gap item.
- `source_refs: list[string]` (required) — source references that justify this validation item.

`EvidenceRef`
- `evidence_id: string` (required) — stable evidence or source reference identifier.
- `source_class: enum[source_record, normalized_record, library_object, facility_prior, validation_data, field_evidence, synthetic_support]` (required) — source class declared by upstream data.
- `evidence_level: enum[synthetic, contextual, validation_data, field_evidence]` (required) — evidence level used by deterministic inference rules.
- `provenance_ref: string` (required) — upstream provenance reference; may be paired with lineage but cannot be absent.
- `lineage_ref: string` (required) — upstream lineage reference; may be paired with provenance but cannot be absent.

## relationships
- `InferenceRecord.case_id` references `InferenceCase.case_id` from `motor_013`; cardinality is one activated case to one primary inference record per accepted processing run.
- `InferenceRecord.activation_record_ref` references `ActivationRecord` from `motor_013`; cardinality is many inference records over time to one activation record when a case is reprocessed under a new version.
- `InferenceRecord.phase_contract_ref` references `PhaseContract.contract_id` from `motor_001`; the referenced contract must allow `inference_cases` as input and `inference_record`, `tension_record`, `gap_agenda`, and `validation_agenda` as outputs.
- `Tension.inference_id` references `InferenceRecord.inference_id`; cardinality is one inference record to zero or more tensions.
- `GapAgenda.inference_id` references `InferenceRecord.inference_id`; cardinality is one inference record to one gap agenda, including an agenda with an empty `gap_items` list when no gap exists.
- `GapItem.affected_ref` references `InferenceRecord.inference_id`, `Tension.tension_id`, or a source evidence reference according to the gap category.
- `GapAgenda.validation_dependency_refs` references `ValidationAgenda.validation_agenda_id` or `ValidationItem.validation_item_id` when a gap requires downstream validation.
- `ValidationAgenda.inference_id` references `InferenceRecord.inference_id`; cardinality is one inference record to one validation agenda, including an agenda with an empty `validation_items` list when no validation is required.
- `ValidationAgenda.gap_agenda_id` references `GapAgenda.gap_agenda_id`; cardinality is one gap agenda to one validation agenda for the same inference run.
- `ValidationItem.gap_item_id` references `GapItem.gap_item_id`; cardinality is one gap item to zero or more validation items, depending on the phase contract handoff rules.
- `EvidenceRef.evidence_id`, `EvidenceRef.provenance_ref`, and `EvidenceRef.lineage_ref` reference upstream source, provenance, and lineage records; this motor records those references but does not mutate or verify the upstream objects.

## identifiers
- `InferenceRecord`: canonical ID is `inference_id`. Recommended deterministic form: `motor_014:inference:{case_id}:{version_id}`.
- `Tension`: canonical ID is `tension_id`. Recommended deterministic form: `motor_014:tension:{inference_id}:{ordinal}:{version_id}`.
- `GapAgenda`: canonical ID is `gap_agenda_id`. Recommended deterministic form: `motor_014:gap_agenda:{inference_id}:{version_id}`.
- `GapItem`: canonical ID is `gap_item_id`. Recommended deterministic form: `motor_014:gap_item:{gap_agenda_id}:{ordinal}`.
- `ValidationAgenda`: canonical ID is `validation_agenda_id`. Recommended deterministic form: `motor_014:validation_agenda:{inference_id}:{version_id}`.
- `ValidationItem`: canonical ID is `validation_item_id`. Recommended deterministic form: `motor_014:validation_item:{validation_agenda_id}:{gap_item_id}:{ordinal}`.
- `EvidenceRef`: canonical ID is `evidence_id`, inherited from the upstream evidence or source object.
- Identifier stability rule: IDs must be derived from canonical input identifiers and version metadata, never from list position alone except for a deterministic ordinal within an already stable parent record.

## versioning
- Every top-level emitted record must include `version_id: string`, `created_at: datetime`, `updated_at: datetime`, and `version_hash: string`.
- `version_id` identifies the schema and content version of the emitted record. It changes when the canonical content, rule version, contract version, or lineage set changes.
- `created_at` is the timestamp of first emission for that record version.
- `updated_at` is the timestamp of last material update for that record version. For immutable first-pass emission, `updated_at` equals `created_at`.
- `version_hash` is computed from canonicalized JSON content excluding non-deterministic runtime-only fields. The hash input must include `motor_id`, canonical ID, `case_id`, `phase_contract_ref`, `contract_version`, `rule_version`, output content, lineage references, and parent reference.
- Sub-objects such as `GapItem`, `ValidationItem`, and `EvidenceRef` inherit version context from their parent top-level record unless promoted to a separate persisted object by a later stage.
- Supersession is represented by `parent_id`; prior records remain reconstructible and are not overwritten silently.

## lineage
- Every top-level emitted record must include `source_ref: string`, `produced_by_motor: string`, `produced_at: datetime`, and `parent_id: string | null`.
- `source_ref` points to the canonical upstream object that caused the record to exist. For `InferenceRecord`, this is normally `case_id`; for `Tension`, it is normally `inference_id` or the source evidence reference; for `GapAgenda`, it is normally `inference_id`; for `ValidationAgenda`, it is normally `gap_agenda_id` or `inference_id`.
- `produced_by_motor` is always `motor_014` for records created by this motor.
- `produced_at` records when this motor produced the object and must not be copied from upstream timestamps.
- `parent_id` links to the previous version of the same object when the object supersedes an earlier emitted record. It is null for the first emitted version.
- `lineage_refs` must preserve all upstream references required to reconstruct the path from `InferenceCase`, activation record, trigger log, phase contract, evidence references, and rule version to the emitted output.
- Missing provenance or lineage on any evidence reference blocks emission with `PROVENANCE_REQUIRED`; the motor must not create a partial output to compensate.
- Lineage records document analytical derivation only. They do not represent claim verification, field evidence creation, source ingestion, or final report generation.
