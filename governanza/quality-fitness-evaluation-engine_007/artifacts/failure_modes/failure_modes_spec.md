# Failure Modes Spec — Quality / Fitness Evaluation Engine

Motor ID: motor_007

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Evaluar calidad estructural, completitud, trazabilidad y aptitud de uso por fase u objeto.
why_it_exists:  Evita que objetos defectuosos o no aptos contaminen fases posteriores.
key_inputs:     identity_resolved_records, phase_contracts (motor_001)
key_outputs:    quality_record, fitness_score, quality_flags, disqualification_reason
key_objects:    QualityRecord, FitnessScore, QualityFlag
what_not_to_do: No modifica registros. No normaliza. Solo evalúa y emite señales de calidad.
design_notes:   Motor evaluador, no transformador. Depende de motor_006.

This artifact refines the documented failure modes into implementation-facing
conditions, observable symptoms and recovery paths for Gate 4.
-->

## failure_modes_list
- CONTRACT_VERSION_DRIFT: trigger condition: `phase_contract_version` used in a QualityRecord does not match the applicable contract selected for the evaluated object type and phase -> observable symptom: outputs with identical `subject_ref` and `evaluation_run_id` show different thresholds, or downstream audit cannot reconcile `threshold_applied` with motor_001 contract data -> recovery path: reject the affected evaluation run, reselect the phase contract by `contract_id` plus `contract_version`, re-run scoring, and emit new QualityRecord versions linked through `parent_id`.
- MUTATING_EVALUATOR: trigger condition: evaluation logic writes to, normalizes, enriches or deletes fields from `identity_resolved_records` or `phase_contracts` while calculating score -> observable symptom: byte comparison of input snapshots before and after evaluation differs, or upstream records acquire values not produced by motor_005/motor_006/motor_001 -> recovery path: fail the run, discard mutated outputs, restore the upstream input snapshot, and isolate scoring into read-only data access with explicit copy-on-write only for motor_007 outputs.
- TRACEABILITY_FALSE_PASS: trigger condition: a record with missing `provenance`, missing `lineage`, missing `subject_version_ref` or absent producer reference receives `evaluation_status = pass` -> observable symptom: emitted QualityRecord has empty source metadata while `quality_flags` lacks `missing_provenance` or `missing_lineage` -> recovery path: invalidate the QualityRecord, emit blocking or warning QualityFlag entries according to the phase contract, and recalculate status as `conditional_pass`, `disqualified` or `rejected`.
- BLOCKING_FLAG_SCORE_OVERRIDE: trigger condition: deterministic score calculation allows high `total_score` to override a QualityFlag with `severity = blocking` -> observable symptom: `fitness_score.blocking_flag_present = true` while `evaluation_status = pass`, or `disqualification_reason` is null for a blocked object -> recovery path: enforce status precedence where blocking flags force `disqualified`, require `disqualification_reason.supporting_flags`, and re-run affected records.
- NON_RECONSTRUCTIBLE_OUTPUT: trigger condition: QualityRecord, FitnessScore, QualityFlag or DisqualificationReason is emitted without required lineage, versioning, rule-version or source references -> observable symptom: audit cannot reconstruct `subject_ref`, `subject_version_ref`, `phase_contract_ref`, `phase_contract_version`, `evaluation_run_id`, `scoring_rule_version` and `version_hash` from the output -> recovery path: reject incomplete output serialization, rebuild the output from the original input snapshot and contract, and block downstream handoff until required references are present.
- AMBIGUITY_CLOSURE_LEAK: trigger condition: motor_007 treats `identity_status = ambiguous` as resolved or creates entity-cluster decisions while evaluating fitness -> observable symptom: no `quality_flag.code = ambiguous_identity` appears for ambiguous input, or output changes identity state instead of only assessing its fitness -> recovery path: remove identity-resolution behavior from motor_007, restore the original identity state as read-only input, and emit only a QualityFlag and status derived from the phase contract.

## anti_patterns
- Embedding repair logic in the evaluator, such as filling missing required fields, inferring provenance, normalizing strings or rewriting lineage before scoring.
- Coupling scoring thresholds to constants inside motor_007 instead of reading them from the referenced phase contract and recording `scoring_rule_version`.
- Treating `fitness_score.total_score` as the only decision signal and ignoring blocking QualityFlag severity, dimension thresholds or disqualification requirements.
- Combining quality evaluation with identity resolution, duplicate detection, taxonomy normalization, conformance review or downstream analytic claims in the same module.
- Emitting generic reasons such as `unknown`, `low_quality` or free-text-only messages without machine-readable `code`, `affected_field`, `contract_rule_ref` and supporting flags.
- Updating historical QualityRecord objects in place during re-evaluation instead of emitting a new version with `parent_id` and a new deterministic hash.
- Allowing an LLM or non-declared heuristic to decide pass/fail status without a deterministic rule basis and reproducible score inputs.

## degradation_signals
- `quality_records_missing_lineage_count > 0` for any run, measured across required fields `source_ref`, `produced_by_motor`, `produced_at`, `version_id`, `version_hash` and `parent_id`.
- `pass_with_blocking_flag_count > 0`, especially where `fitness_score.blocking_flag_present = true` and `evaluation_status = pass`.
- `pass_missing_traceability_count > 0` for records lacking provenance, lineage or subject version metadata.
- Contract drift log entries where `phase_contract_version` in QualityRecord does not equal the version used to derive `threshold_applied` or `dimension_thresholds`.
- Increase in `disqualification_reason.code = unknown` or empty `supporting_flags`, indicating loss of structured reason generation.
- Repeated warnings that input snapshots changed during evaluation, indicating violation of the read-only invariant.
- Rising ratio of `conditional_pass` records with empty `quality_flags`, indicating status and flag emission are no longer synchronized.
- Growth in records with scores outside `0.0 <= total_score <= 1.0`, missing dimension keys, or dimension scores not aligned with `evaluated_dimensions`.
- Audit failures where a QualityRecord cannot be rebuilt from `subject_ref`, `phase_contract_ref`, `evaluation_run_id` and `scoring_rule_version`.

## expensive_errors
- Silent input mutation: expensive because downstream motors may consume altered identity records or contracts while audit trails still point to the original upstream owners. Prevent by treating all inputs as read-only, snapshotting input hashes before evaluation and failing the run on post-evaluation diffs.
- Contract-version drift: expensive because historical quality decisions become incomparable and may need batch re-evaluation across every object scored under the wrong threshold. Prevent by binding each QualityRecord to `phase_contract_ref`, `phase_contract_version`, `threshold_applied`, `dimension_thresholds` and `scoring_rule_version`.
- False pass on missing provenance or lineage: expensive because defective objects can contaminate later phases, and later recovery requires tracing every derived artifact that trusted the bad pass. Prevent by making provenance, lineage and subject version checks preconditions for pass status.
- Blocking flag ignored by score aggregation: expensive because a single high total score can mask a contractual exclusion such as restricted use or critical traceability loss. Prevent by applying status precedence after score calculation: any blocking flag forces `disqualified` and a non-null DisqualificationReason.
- Non-deterministic scoring: expensive because audit cannot reproduce why a subject passed or failed, forcing manual review rather than automated rebuild. Prevent by restricting scoring to declared inputs, recording score basis and rule version, and keeping all thresholds externalized in the phase contract.
- In-place overwrite of historical QualityRecord objects: expensive because lineage, comparison across runs and rollback become unreliable. Prevent by emitting immutable output versions with deterministic identifiers, version hashes and `parent_id` links for re-evaluations.
