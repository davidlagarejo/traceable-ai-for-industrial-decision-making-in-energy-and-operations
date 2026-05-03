# Test Spec — Quality / Fitness Evaluation Engine

Motor ID: motor_007

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Evaluar calidad estructural, completitud, trazabilidad y aptitud de uso por fase u objeto.
why_it_exists:  Evita que objetos defectuosos o no aptos contaminen fases posteriores.
key_inputs:     identity_resolved_records, phase_contracts (motor_001)
key_outputs:    quality_record, fitness_score, quality_flags, disqualification_reason
key_objects:    QualityRecord, FitnessScore, QualityFlag
what_not_to_do: No modifica registros. No normaliza. Solo evalúa y emite señales de calidad.
design_notes:   Motor evaluador, no transformador. Depende de motor_006.

All placeholder markers have been replaced with concrete test specification content.
-->

## happy_path
Input:
- `identity_resolved_records` contains one record:
  - `record_id = "idr_123"`
  - `identity_status = "resolved"`
  - `object_type = "facility"`
  - `phase_ref = "phase_1"`
  - `version = "1.0.0"`
  - `provenance.source_id = "src_01"`
  - `lineage.parent_record_id = "norm_123"`
  - required contract fields: `name = "Clinic Norte"`, `country = "CL"`, `source_url = "https://example.test/facility/123"`
- `phase_contracts` contains one applicable contract:
  - `contract_id = "phase_1_facility_prior_v2"`
  - `contract_version = "2.0.0"`
  - `object_type = "facility"`
  - `required_fields = ["name", "country", "source_url"]`
  - `fitness_thresholds.total = 0.90`
  - `fitness_thresholds.dimensions.traceability = 0.80`
  - `fitness_thresholds.dimensions.completeness = 0.90`
- `evaluation_context.evaluation_run_id = "eval_run_007_001"`
- `evaluation_context.scoring_rule_version = "quality_rules_v1"`

Expected output:
- exactly one `quality_record` is emitted.
- `quality_record.subject_ref = "idr_123"`.
- `quality_record.subject_version_ref = "1.0.0"`.
- `quality_record.phase_contract_ref = "phase_1_facility_prior_v2"`.
- `quality_record.phase_contract_version = "2.0.0"`.
- `quality_record.evaluation_run_id = "eval_run_007_001"`.
- `quality_record.evaluation_status = "pass"`.
- `quality_record.fitness_score.total_score >= 0.90`.
- `quality_record.fitness_score.threshold_applied = 0.90`.
- `quality_record.fitness_score.scoring_rule_version = "quality_rules_v1"`.
- `quality_record.fitness_score.blocking_flag_present = false`.
- `quality_record.quality_flags = []`.
- `quality_record.disqualification_reason = null`.
- `quality_record.produced_by_motor = "motor_007"`.
- the source `identity_resolved_record` remains byte-for-byte unchanged by the evaluation.

## sparse_case
Input:
- `identity_resolved_records` contains one record with all required structural fields but no optional descriptive metadata:
  - `record_id = "idr_sparse_001"`
  - `identity_status = "resolved"`
  - `object_type = "facility"`
  - `phase_ref = "phase_1"`
  - `version = "1.0.0"`
  - `provenance.source_id = "src_02"`
  - `lineage.parent_record_id = "norm_sparse_001"`
  - required contract fields: `name = "Unidad Sur"`, `country = "CL"`, `source_url = "https://example.test/facility/sparse"`
  - optional fields such as `description`, `address`, `operator_name` and `external_aliases` are absent.
- `phase_contracts` contains the same valid `phase_1_facility_prior_v2` contract used in the happy path, with optional fields declared as non-blocking.
- `evaluation_context.evaluation_run_id = "eval_run_007_sparse"`.

Expected output:
- exactly one `quality_record` is emitted.
- `evaluation_status = "pass"` when optional fields are not part of `required_fields` and no threshold is violated.
- `quality_flags` is an empty list or contains only `severity = "info"` flags tied to optional non-blocking observations.
- `fitness_score.total_score` remains within `0.0 <= total_score <= 1.0`.
- `disqualification_reason = null`.
- no fatal error is raised for the absent optional fields.

## malformed_input
Malformed collection case:
- Input sets `identity_resolved_records` to an object instead of a list:
  - `identity_resolved_records = {"record_id": "idr_bad_001"}`
  - `phase_contracts` is otherwise valid.
- Expected behavior: reject the batch before scoring with structured error code `QUALITY_INPUT_NOT_LIST`.
- Expected output: no `quality_record` is emitted for the malformed collection.

Malformed item case:
- Input sets `identity_resolved_records` to a list containing one item without a stable subject reference:
  - `identity_status = "resolved"`
  - `version = "1.0.0"`
  - `provenance.source_id = "src_03"`
  - `lineage.parent_record_id = "norm_bad_001"`
  - `record_id` is absent.
- Expected behavior: reject that item with structured error code `QUALITY_INPUT_MISSING_SUBJECT_REF`.
- Expected output: no `quality_record` is emitted for that item.

Malformed contract case:
- Input contains a phase contract without `contract_id`, `contract_version`, `required_fields` or `fitness_thresholds`.
- Expected behavior: reject the evaluation with structured error code `QUALITY_CONTRACT_INVALID`.
- Expected output: no passing `quality_record` is emitted from an invalid contract.

## edge_cases
1. Empty but valid batch:
   - Input: `identity_resolved_records = []`, `phase_contracts` contains at least one valid contract, and `evaluation_context.evaluation_run_id = "eval_run_007_empty"`.
   - Correct behavior: return an empty collection of `quality_record` outputs, record evaluated count as zero if run metadata is emitted, and do not raise a fatal validation error.

2. Missing critical traceability metadata:
   - Input: one record with valid `record_id`, `identity_status = "resolved"` and required contract fields, but missing `provenance.source_id` and `lineage.parent_record_id`.
   - Correct behavior: the record cannot receive `evaluation_status = "pass"`. The output is either `conditional_pass` with `quality_flag.code` values including `missing_provenance` and `missing_lineage`, or `disqualified` when the contract marks traceability as blocking. If disqualified, `disqualification_reason.code = "critical_traceability_missing"`.

3. Ambiguous identity with complete metadata:
   - Input: one record with `identity_status = "ambiguous"`, complete provenance, complete lineage, version and all required contract fields.
   - Correct behavior: motor_007 does not resolve the ambiguity. It emits a `quality_flag.code = "ambiguous_identity"` and sets `evaluation_status` to `conditional_pass` or `disqualified` according to the applicable contract threshold.

4. Score exactly at threshold:
   - Input: one valid record whose deterministic scoring produces `fitness_score.total_score = 0.90` with `fitness_thresholds.total = 0.90` and no blocking flags.
   - Correct behavior: the record is eligible for `evaluation_status = "pass"` because the threshold comparison is inclusive at the boundary.

5. Blocking flag despite high score:
   - Input: one record whose computed `fitness_score.total_score = 0.95`, but the contract detects `restricted_use` as a blocking condition.
   - Correct behavior: `fitness_score.blocking_flag_present = true`, `evaluation_status = "disqualified"`, a blocking `QualityFlag` is emitted, and `disqualification_reason.supporting_flags` references that flag.

## pass_criteria
The test suite passes when all applicable observations are true:
- required malformed inputs are rejected with the specified structured error codes.
- valid inputs emit one `QualityRecord` per evaluated record and zero records for an empty valid batch.
- every emitted `QualityRecord` has non-empty `quality_record_id`, `subject_ref`, `subject_version_ref`, `phase_contract_ref`, `phase_contract_version`, `evaluation_run_id`, `fitness_score`, `quality_flags`, `evaluation_status`, `version_id`, `version_hash`, `source_ref`, `produced_by_motor` and `produced_at`.
- every emitted `FitnessScore.total_score` is in the closed range `0.0` to `1.0`.
- `quality_flags` is always a list, including the empty-list case.
- `disqualification_reason` is null unless `evaluation_status = "disqualified"`.
- when `evaluation_status = "disqualified"`, `disqualification_reason` is non-null and references supporting blocking flags.
- no source `identity_resolved_record` or `phase_contract` is modified, normalized, enriched or rewritten during evaluation.

## fail_criteria
The test suite fails if any of these observations occurs:
- a malformed collection, missing subject reference or invalid contract is accepted without the expected structured rejection.
- an emitted `QualityRecord` lacks required lineage, versioning, provenance or contract reference fields.
- a record missing provenance or lineage receives `evaluation_status = "pass"`.
- `fitness_score.total_score` is less than `0.0`, greater than `1.0` or absent.
- `evaluation_status = "pass"` is emitted while any associated `QualityFlag.severity = "blocking"` exists.
- `evaluation_status = "disqualified"` is emitted with `disqualification_reason = null`.
- optional missing fields cause a fatal error when they are not listed in `required_fields` and no threshold is violated.
- motor_007 changes input record content, resolves identity ambiguity, edits the phase contract or performs normalization outside its evaluation-only scope.
