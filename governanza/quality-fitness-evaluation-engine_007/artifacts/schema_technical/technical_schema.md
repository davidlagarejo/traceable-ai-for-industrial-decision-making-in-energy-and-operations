# Technical Schema — Quality / Fitness Evaluation Engine

Motor ID: motor_007

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Evaluar calidad estructural, completitud, trazabilidad y aptitud de uso por fase u objeto.
why_it_exists:  Evita que objetos defectuosos o no aptos contaminen fases posteriores.
key_inputs:     identity_resolved_records, phase_contracts (motor_001)
key_outputs:    quality_record, fitness_score, quality_flags, disqualification_reason
key_objects:    QualityRecord, FitnessScore, QualityFlag
what_not_to_do: No modifica registros. No normaliza. Solo evalúa y emite señales de calidad.
design_notes:   Motor evaluador, no transformador. Depende de motor_006.

All placeholder markers have been replaced with concrete technical schema content.
-->

## entities
- QualityRecord: persisted output record for one deterministic quality evaluation of one `identity_resolved_record` against one applicable `phase_contract`. It lives in `schema_technical` as the canonical output schema and is produced by the implementation stage.
- FitnessScore: embedded scoring object owned by a QualityRecord. It records dimension scores, total score, threshold and scoring rule version used for the evaluation. It lives in `schema_technical` as a typed value object and is emitted inside each QualityRecord.
- QualityFlag: repeated child object owned by a QualityRecord. It records each detected defect, warning, restriction or blocking condition without modifying the evaluated record. It lives in `schema_technical` as a typed signal object and is emitted inside `quality_flags`.
- DisqualificationReason: optional child object owned by a QualityRecord. It is required only when `evaluation_status = disqualified` and explains the blocking failure in a reconstructible form. It lives in `schema_technical` as a typed reason object and is emitted as `disqualification_reason`.

## fields
QualityRecord:
- quality_record_id: string (required) — stable identifier for this evaluation output.
- subject_ref: string (required) — reference to the evaluated `identity_resolved_record.record_id` or equivalent stable subject identifier.
- subject_version_ref: string (required) — version reference of the evaluated subject at evaluation time.
- phase_contract_ref: string (required) — reference to the `phase_contract.contract_id` used for evaluation.
- phase_contract_version: string (required) — contract version used to avoid contract drift.
- evaluation_run_id: string (required) — identifier of the evaluation run that produced this record.
- evaluation_status: enum[pass, conditional_pass, disqualified, rejected] (required) — final deterministic status for this evaluated subject.
- fitness_score: FitnessScore (required) — score object produced for this evaluation.
- quality_flags: list[QualityFlag] (required) — list of detected quality signals; empty list is valid.
- disqualification_reason: DisqualificationReason|null (required) — blocking explanation when disqualified; null otherwise.
- evaluated_dimensions: list[enum[completeness, traceability, contract_consistency, fitness]] (required) — dimensions evaluated for the score.
- evaluation_errors: list[string] (required) — structured validation errors for rejected items; empty list when not rejected.
- version_id: string (required) — version identifier for this QualityRecord object.
- created_at: datetime (required) — timestamp when this QualityRecord was first created.
- updated_at: datetime (required) — timestamp when this QualityRecord version was last updated.
- version_hash: string (required) — deterministic hash over canonical QualityRecord content.
- source_ref: string (required) — upstream input reference used for provenance reconstruction.
- produced_by_motor: string (required) — constant value `motor_007`.
- produced_at: datetime (required) — timestamp when motor_007 produced this output.
- parent_id: string|null (required) — previous QualityRecord id when this is a re-evaluation of an earlier quality record; null for first evaluation.

FitnessScore:
- score_id: string (required) — stable identifier for this score object within the QualityRecord.
- total_score: float (required) — normalized score in the closed range 0.0 to 1.0.
- dimension_scores: dict[string, float] (required) — score per evaluated dimension; keys match `evaluated_dimensions`.
- threshold_applied: float (required) — minimum total threshold read from the phase contract.
- dimension_thresholds: dict[string, float] (required) — dimension-specific thresholds read from the phase contract; empty dict only when the contract has no dimension thresholds.
- scoring_rule_version: string (required) — deterministic scoring rule version used for this calculation.
- blocking_flag_present: boolean (required) — true when any associated QualityFlag has `severity = blocking`.
- score_basis: list[string] (required) — field names and metadata categories considered during scoring.
- version_id: string (required) — version identifier for this FitnessScore object.
- created_at: datetime (required) — timestamp when this FitnessScore was first created.
- updated_at: datetime (required) — timestamp when this FitnessScore version was last updated.
- version_hash: string (required) — deterministic hash over canonical FitnessScore content.
- source_ref: string (required) — reference to the QualityRecord and subject that produced the score.
- produced_by_motor: string (required) — constant value `motor_007`.
- produced_at: datetime (required) — timestamp when motor_007 produced this score.
- parent_id: string|null (required) — previous FitnessScore id when recalculated; null for first score.

QualityFlag:
- flag_id: string (required) — stable identifier for this flag within the QualityRecord.
- code: enum[missing_required_field, missing_lineage, missing_provenance, contract_mismatch, restricted_use, ambiguous_identity, not_fit_for_phase] (required) — machine-readable quality signal.
- severity: enum[info, warning, blocking] (required) — operational severity of the signal.
- dimension: enum[completeness, traceability, contract_consistency, fitness] (required) — evaluation dimension affected by the flag.
- message: string (required) — human-readable explanation of the detected condition.
- affected_field: string|null (required) — subject or contract field affected by the flag; null when the issue is object-wide.
- contract_rule_ref: string|null (required) — phase contract rule or threshold that triggered the flag; null when no specific rule applies.
- blocking: boolean (required) — true when this flag prevents `evaluation_status = pass`.
- version_id: string (required) — version identifier for this QualityFlag object.
- created_at: datetime (required) — timestamp when this QualityFlag was first created.
- updated_at: datetime (required) — timestamp when this QualityFlag version was last updated.
- version_hash: string (required) — deterministic hash over canonical QualityFlag content.
- source_ref: string (required) — reference to the QualityRecord and subject condition that produced the flag.
- produced_by_motor: string (required) — constant value `motor_007`.
- produced_at: datetime (required) — timestamp when motor_007 produced this flag.
- parent_id: string|null (required) — previous QualityFlag id when re-issued for the same condition; null for first issue.

DisqualificationReason:
- reason_id: string (required) — stable identifier for the disqualification reason.
- code: string (required) — machine-readable reason code, such as `traceability_below_threshold` or `critical_traceability_missing`.
- severity: enum[blocking] (required) — fixed blocking severity.
- threshold_failed: string (required) — failed threshold or rule reference from the phase contract.
- explanation: string (required) — concise explanation of why the subject is not fit for the evaluated phase.
- supporting_flags: list[string] (required) — list of `QualityFlag.flag_id` values supporting the disqualification.
- version_id: string (required) — version identifier for this DisqualificationReason object.
- created_at: datetime (required) — timestamp when this reason was first created.
- updated_at: datetime (required) — timestamp when this reason version was last updated.
- version_hash: string (required) — deterministic hash over canonical DisqualificationReason content.
- source_ref: string (required) — reference to the QualityRecord and failed subject condition that produced the reason.
- produced_by_motor: string (required) — constant value `motor_007`.
- produced_at: datetime (required) — timestamp when motor_007 produced this reason.
- parent_id: string|null (required) — previous DisqualificationReason id when re-issued; null for first issue.

## relationships
- QualityRecord.subject_ref references `identity_resolved_record.record_id` from motor_006. This is a read-only external reference; motor_007 never writes back to the subject.
- QualityRecord.subject_version_ref references the evaluated subject version supplied by the upstream versioned record.
- QualityRecord.phase_contract_ref plus QualityRecord.phase_contract_version references `phase_contract.contract_id` and `phase_contract.contract_version` from motor_001.
- QualityRecord.fitness_score owns exactly one FitnessScore. The FitnessScore cannot exist as an orphan without its QualityRecord.
- QualityRecord.quality_flags owns zero or more QualityFlag objects. Each QualityFlag must reference its parent through `source_ref` and must describe a detected condition, not a correction.
- QualityRecord.disqualification_reason owns zero or one DisqualificationReason. It is non-null only when `evaluation_status = disqualified`.
- DisqualificationReason.supporting_flags references QualityFlag.flag_id values belonging to the same QualityRecord.
- FitnessScore.dimension_scores and QualityFlag.dimension use the same controlled dimensions: `completeness`, `traceability`, `contract_consistency`, `fitness`.
- QualityRecord.parent_id references a previous QualityRecord when the same subject is re-evaluated under a new run, contract version or scoring rule version.

## identifiers
- QualityRecord canonical identifier: `quality_record_id`. Recommended deterministic composition: `motor_007:{evaluation_run_id}:{subject_ref}:{phase_contract_ref}:{phase_contract_version}`.
- FitnessScore canonical identifier: `score_id`. Recommended deterministic composition: `{quality_record_id}:score:{scoring_rule_version}`.
- QualityFlag canonical identifier: `flag_id`. Recommended deterministic composition: `{quality_record_id}:flag:{code}:{affected_field_or_object}:{contract_rule_ref_or_none}`.
- DisqualificationReason canonical identifier: `reason_id`. Recommended deterministic composition: `{quality_record_id}:disqualification:{code}`.
- External subject identifier: `subject_ref`; this remains owned by motor_006 or the upstream producer and is never rewritten by motor_007.
- External contract identifier: `phase_contract_ref`; this remains owned by motor_001 and is always paired with `phase_contract_version`.

## versioning
- Every persisted entity carries `version_id: string` to identify the concrete version of the emitted object.
- Every persisted entity carries `created_at: datetime` and `updated_at: datetime`. For immutable first-pass outputs these timestamps may be equal.
- Every persisted entity carries `version_hash: string`, computed over a canonical serialization of the entity excluding volatile runtime transport details.
- QualityRecord.version_hash includes `subject_ref`, `subject_version_ref`, `phase_contract_ref`, `phase_contract_version`, `evaluation_status`, `fitness_score`, `quality_flags`, `disqualification_reason`, `evaluation_run_id` and `scoring_rule_version` reachable through FitnessScore.
- FitnessScore.version_hash includes `total_score`, `dimension_scores`, `threshold_applied`, `dimension_thresholds`, `scoring_rule_version`, `blocking_flag_present` and `score_basis`.
- QualityFlag.version_hash includes `code`, `severity`, `dimension`, `affected_field`, `contract_rule_ref`, `blocking` and `message`.
- DisqualificationReason.version_hash includes `code`, `threshold_failed`, `explanation` and `supporting_flags`.
- Re-evaluation never mutates a historical QualityRecord in place. A new QualityRecord is emitted with a new `quality_record_id` or `version_id` and a `parent_id` reference when it supersedes an earlier evaluation.

## lineage
- Every entity includes `source_ref: string` pointing to the upstream object or parent QualityRecord material used to produce it.
- Every entity includes `produced_by_motor: string` with constant value `motor_007`.
- Every entity includes `produced_at: datetime` recording the production timestamp for audit reconstruction.
- Every entity includes `parent_id: string|null` to link re-evaluations or recalculations to their prior object; null means there is no prior object.
- QualityRecord lineage must preserve `subject_ref`, `subject_version_ref`, `phase_contract_ref`, `phase_contract_version`, `evaluation_run_id`, `produced_by_motor` and `produced_at`.
- FitnessScore lineage must preserve the parent `quality_record_id`, the scoring rule version and the score basis used for calculation.
- QualityFlag lineage must preserve the parent `quality_record_id`, affected field or object-wide condition, and the contract rule reference when available.
- DisqualificationReason lineage must preserve the parent `quality_record_id` and supporting QualityFlag identifiers.
- Lineage fields are audit metadata only. They do not authorize motor_007 to modify the subject record, the phase contract or any upstream version record.
