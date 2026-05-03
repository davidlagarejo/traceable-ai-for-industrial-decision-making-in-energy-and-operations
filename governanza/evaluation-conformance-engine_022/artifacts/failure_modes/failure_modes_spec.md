# Failure Modes Spec — Evaluation / Conformance Engine

Motor ID: motor_022

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
why_it_exists:  Evita degradación silenciosa del sistema con el tiempo.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), quality_records (motor_007), harness_results (motor_021)
key_outputs:    conformance_record, violation_log, architectural_drift_signal
key_objects:    ConformanceRecord, ViolationRecord, DriftSignal
what_not_to_do: No corrige violaciones. No modifica el sistema. Solo detecta y registra conformidad.
design_notes:   Evaluación formal de conformidad. Depende de motor_001, motor_002, motor_007 y motor_021.

Placeholder markers have been resolved with motor-specific content.
-->

## failure_modes_list
- FM022_MISSING_CONTRACT_AUTHORITY: an evaluated object, phase or handoff cannot be matched to a `phase_contract` from motor_001 -> evaluation attempts to infer rules, emits `PASS` without authority, or rejects inconsistently across runs -> stop evaluation with `ERROR_MISSING_CONTRACT`, preserve the offending `input_ref`, require an upstream contract record, and rerun without synthesizing local rules.
- FM022_VERSION_EVIDENCE_DESYNCHRONIZATION: `quality_records` or `harness_results` reference an object/version pair absent from `version_records` or incompatible with the selected contract version -> conformance status differs from the versioned evidence or `ERROR_MISSING_VERSION_RECORD` spikes for otherwise valid objects -> quarantine the input bundle, emit a structured rejection, request corrected version evidence from motor_002, and rerun the same evaluation after version alignment.
- FM022_LINEAGE_BLIND_PASS: contract, quality and harness evidence pass while the matching `version_record.lineage_id` is null, empty or not preserved in the emitted `ConformanceRecord` -> output claims `status=PASS` but cannot reconstruct ancestry through `lineage_id`, `source_ref` and `evidence_refs` -> force `status=FAIL`, emit a material `ViolationRecord` with `violation_type=lineage`, and require upstream lineage repair before any passing conformance record is allowed.
- FM022_VIOLATION_LOG_SUPPRESSION: a material harness, boundary, quality or contract failure is mentioned only in `status_reason` or prose -> `ConformanceRecord.status=FAIL` has empty `violation_ids`, or `violation_log` lacks `rule_ref`, `input_ref`, `expected_condition` and `observed_value` -> reject the output as non-conformant, add one atomic `ViolationRecord` per failed rule, and recompute status from linked violations.
- FM022_DRIFT_SIGNAL_WITHOUT_EVIDENCE: `architectural_drift_signal` is emitted from trend language, operator judgment or isolated warnings without linked material violations -> `DriftSignal.related_violation_ids` is empty, references unknown violations, or cannot support its `basis` -> suppress the drift signal, require deterministic violation evidence, and emit drift only from repeated, systemic or critical violation sets.
- FM022_UPSTREAM_MUTATION_DURING_EVALUATION: the engine edits phase contracts, version records, quality records, harness results, evaluated artifacts or motor state while evaluating conformance -> audit trail shows changed input hashes or timestamps caused by motor_022 instead of a pure read-only output bundle -> discard the run, restore upstream objects from authoritative sources, harden read-only boundaries, and rerun evaluation against immutable inputs.
- FM022_SEVERITY_COLLAPSE: multiple failure types are collapsed into a single aggregate score, generic warning, or default severity -> material boundary or harness failures are downgraded to `WARNING`, unrelated violations share the same severity, or drift severity no longer follows linked violation materiality -> replace aggregate scoring with rule-specific severity mapping, preserve `material=true` for blocking violations, and reissue affected output records with traceable evidence.
- FM022_ORPHAN_OUTPUT_RECORD: `ViolationRecord` or `DriftSignal` objects are emitted without a valid parent `ConformanceRecord`, linked violation set, or source evidence reference -> downstream governance cannot trace a violation to the evaluated object/version, contract and input bundle -> reject orphan records, rebuild the parent-child links from the canonical evaluation record, and emit a batch-level structured rejection if no parent can be formed.

## anti_patterns
- Auto-remediation inside conformance evaluation: detecting a violation and then patching contracts, artifacts, datasets, motor state, quality scores or harness results in the same engine.
- Narrative rule authority: accepting free-form reviewer text, LLM-generated advice or local configuration as a conformance rule when it is not anchored to `phase_contracts`, `version_records`, `quality_records` or `harness_results`.
- Hidden aggregate scoring: reducing contract, lineage, quality and harness evidence to one numeric fitness score that hides the failed rule, materiality, severity and input reference.
- Cross-motor responsibility merge: recomputing quality metrics from motor_007, executing harness tests from motor_021, creating versions for motor_002 or redefining phase contracts from motor_001.
- Silent evidence normalization: rewriting identifiers, statuses, version ids, lineage ids or evidence references to make inputs appear compatible.
- Drift by intuition: emitting `DriftSignal` records from perceived trends without deterministic links to `ViolationRecord` identifiers and conformance records.
- Mutable historical conformance: editing prior `ConformanceRecord`, `ViolationRecord` or `DriftSignal` content instead of emitting a new version with `parent_id` when upstream evidence changes.
- Orphan violation storage: storing violations outside the evaluation context without `conformance_record_id`, `rule_ref`, `input_ref`, `expected_condition` and `observed_value`.

## degradation_signals
- Metric `pass_without_lineage_count > 0`: any `ConformanceRecord.status=PASS` where `lineage_id`, `source_ref` or `evidence_refs` is empty.
- Metric `fail_without_violation_count > 0`: any `ConformanceRecord.status=FAIL` where `violation_ids` is empty or linked `ViolationRecord.material=true` is absent.
- Metric `unknown_version_reference_rate` rising across runs: quality or harness evidence increasingly references object/version pairs missing from `version_records`.
- Metric `missing_contract_rejection_rate` rising for objects that previously evaluated successfully: contract authority lookup may be stale, incomplete or using the wrong contract version.
- Log pattern `drift_signal_emitted related_violation_ids=[]` or `unknown_related_violation_id`: drift emission is no longer evidence-backed.
- Log pattern `input_mutation_detected produced_by_motor=motor_022`: input bundle hash, upstream timestamp or motor state changed during a conformance run.
- Metric `generic_severity_ratio` above expected baseline: unrelated violations receive the same severity or `rule_ref`, indicating severity collapse or rule mapping loss.
- Metric `evidence_ref_reuse_ratio` spikes across unrelated evaluations: repeated generic evidence references may be masking object-specific provenance.
- Metric `structured_rejection_without_input_ref_count > 0`: malformed input is rejected without the `input_ref`, `expected_condition` and `observed_value` needed for recovery.
- Metric `orphan_child_record_count > 0`: `ViolationRecord.conformance_record_id` or `DriftSignal.related_conformance_record_ids` cannot be resolved inside the emitted bundle.

## expensive_errors
- Allowing `PASS` without contract authority. It is expensive because downstream governance may treat an unauthorised artifact as compliant and later reviews must reconstruct which rule set should have applied. Prevent it by making `phase_contract` resolution mandatory before evaluation and by rejecting with `ERROR_MISSING_CONTRACT` when no authority exists.
- Dropping lineage or provenance on passing records. It is expensive because historical conformance cannot be rebuilt, compared or challenged after outputs have propagated. Prevent it by requiring non-empty `lineage_id`, `source_ref`, `produced_by_motor`, `produced_at` and `evidence_refs` on every emitted record.
- Suppressing material violations into prose. It is expensive because downstream governance and observability cannot route, count or resolve violations that lack atomic identifiers and rule references. Prevent it by enforcing one `ViolationRecord` per failed material rule and by disallowing `FAIL` records with empty `violation_ids`.
- Mutating upstream evidence during evaluation. It is expensive because the audit trail loses the original condition being evaluated and later runs cannot distinguish remediation from evidence corruption. Prevent it with read-only input handling, input hash checks before and after evaluation, and strict separation between detection and correction.
- Emitting drift without linked violations. It is expensive because governance may chase noisy architectural drift signals while real systemic failures remain hidden. Prevent it by requiring non-empty `related_violation_ids`, valid parent conformance records and a deterministic `basis` before emitting any `DriftSignal`.
- Collapsing severity and materiality into one aggregate quality score. It is expensive because a critical boundary or lineage failure can be buried under otherwise good evidence and require broad re-audit after propagation. Prevent it by preserving violation type, severity, materiality, failed rule, expected condition and observed value separately from summary status.
- Rewriting historical conformance records in place. It is expensive because consumers lose comparability across evaluations and cannot determine what was true at the time of an earlier decision. Prevent it by treating outputs as append-only, issuing new `version_id` values for re-evaluations, and linking replacements through `parent_id`.
