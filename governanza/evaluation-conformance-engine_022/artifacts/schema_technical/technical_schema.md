# Technical Schema — Evaluation / Conformance Engine

Motor ID: motor_022

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
why_it_exists:  Evita degradación silenciosa del sistema con el tiempo.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), quality_records (motor_007), harness_results (motor_021)
key_outputs:    conformance_record, violation_log, architectural_drift_signal
key_objects:    ConformanceRecord, ViolationRecord, DriftSignal
what_not_to_do: No corrige violaciones. No modifica el sistema. Solo detecta y registra conformidad.
design_notes:   Evaluación formal de conformidad. Depende de motor_001, motor_002, motor_007 y motor_021.

Schema content is completed for Gate 2 review.
-->

## entities
- ConformanceRecord: canonical output record for one deterministic conformance evaluation of a motor, dataset, artifact, handoff or phase-scoped object against the applicable phase contract, version record, quality evidence and harness evidence. It lives in `schema_technical` as the persistent evaluation schema and is produced by the implementation stage without mutating the evaluated object.
- ViolationRecord: atomic child record for one detected breach of contract, boundary, lineage, quality evidence or harness evidence. It lives in `schema_technical` as the durable violation log item and is emitted only as evidence of nonconformance, not as a correction.
- DriftSignal: aggregate signal derived from one or more ViolationRecord objects when repeated, systemic or high-severity deviations indicate architectural drift. It lives in `schema_technical` as the drift output schema and is emitted for observability and governance consumers.

## fields
ConformanceRecord:
- record_id: string (required) — stable identifier for this conformance evaluation output.
- evaluated_object_id: string (required) — stable identifier of the motor, dataset, artifact, handoff or phase-scoped object being evaluated.
- evaluated_object_type: enum[`motor`, `dataset`, `artifact`, `handoff`, `phase`] (required) — technical category of the evaluated unit.
- evaluated_version_id: string (required) — version identifier of the evaluated unit, resolved from `version_records`.
- contract_id: string (required) — `phase_contracts.contract_id` used as the conformance authority.
- contract_version_id: string (required) — version of the phase contract used for the evaluation.
- lineage_id: string (required) — lineage or graph reference from `version_records` used to reconstruct ancestry.
- quality_record_ids: list[string] (required) — `quality_records` used as quality evidence; empty only when quality evidence is not applicable to the evaluated type.
- harness_result_ids: list[string] (required) — `harness_results` used as test evidence; empty only when no applicable harness result is present and the status records that evidence gap.
- status: enum[`PASS`, `WARNING`, `FAIL`] (required) — deterministic conformance outcome.
- status_reason: string (required) — concise deterministic explanation of the selected status.
- violation_ids: list[string] (required) — linked ViolationRecord identifiers; empty only when `status = PASS`.
- drift_signal_ids: list[string] (required) — linked DriftSignal identifiers derived from this evaluation; empty when no drift signal is emitted.
- evidence_refs: list[string] (required) — input references sufficient to reconstruct the evaluation decision.
- evaluated_at: datetime (required) — timestamp when the conformance evaluation was performed.
- version_id: string (required) — version identifier for this emitted ConformanceRecord.
- created_at: datetime (required) — timestamp when this ConformanceRecord was first created.
- updated_at: datetime (required) — timestamp when this ConformanceRecord version was last updated; equals `created_at` for immutable first emissions.
- version_hash: string (required) — deterministic hash over the canonical serialized ConformanceRecord content.
- source_ref: string (required) — primary upstream input bundle or evaluated object reference that caused the record to exist.
- produced_by_motor: string (required) — constant value `motor_022`.
- produced_at: datetime (required) — timestamp when motor_022 emitted the record.
- parent_id: string|null (required) — prior ConformanceRecord identifier when this evaluation supersedes a previous evaluation of the same unit; null for the first evaluation.

ViolationRecord:
- violation_id: string (required) — stable identifier for this violation.
- conformance_record_id: string (required) — parent ConformanceRecord.record_id that produced this violation.
- evaluated_object_id: string (required) — evaluated unit affected by the violation.
- evaluated_version_id: string (required) — version of the evaluated unit affected by the violation.
- violation_type: enum[`contract`, `boundary`, `lineage`, `quality`, `harness`, `missing_evidence`] (required) — technical class of nonconformance detected.
- rule_ref: string (required) — contract rule, boundary rule, lineage requirement, quality requirement or harness assertion that was evaluated.
- severity: enum[`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`] (required) — operational severity assigned by deterministic conformance rules.
- input_ref: string (required) — specific input record or field reference that triggered the violation.
- expected_condition: string (required) — canonical statement of the required condition.
- observed_value: string (required) — canonical representation of the observed condition or missing value.
- material: boolean (required) — true when the violation prevents `ConformanceRecord.status = PASS`.
- evidence_refs: list[string] (required) — source evidence supporting the violation.
- detected_at: datetime (required) — timestamp when the violation was detected.
- version_id: string (required) — version identifier for this emitted ViolationRecord.
- created_at: datetime (required) — timestamp when this ViolationRecord was first created.
- updated_at: datetime (required) — timestamp when this ViolationRecord version was last updated; equals `created_at` for immutable first emissions.
- version_hash: string (required) — deterministic hash over the canonical serialized ViolationRecord content.
- source_ref: string (required) — primary input reference that caused the violation to exist.
- produced_by_motor: string (required) — constant value `motor_022`.
- produced_at: datetime (required) — timestamp when motor_022 emitted the violation.
- parent_id: string|null (required) — parent ConformanceRecord.record_id or prior ViolationRecord identifier when re-issued; null only for batch-level input rejection before a parent record can be emitted.

DriftSignal:
- signal_id: string (required) — stable identifier for this architectural drift signal.
- scope: enum[`motor`, `dataset`, `artifact`, `handoff`, `phase`] (required) — scope where drift is observed.
- scope_ref: string (required) — stable identifier for the scoped motor, dataset, artifact, handoff or phase.
- basis: enum[`repeated_violation`, `systemic_boundary_drift`, `lineage_degradation`, `quality_regression`, `harness_instability`, `critical_single_violation`] (required) — deterministic basis for emitting the signal.
- severity: enum[`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`] (required) — severity of the drift signal.
- related_violation_ids: list[string] (required) — ViolationRecord.violation_id values used as drift evidence.
- related_conformance_record_ids: list[string] (required) — ConformanceRecord.record_id values that produced the related violations.
- evidence_refs: list[string] (required) — source evidence references supporting the signal.
- emitted_at: datetime (required) — timestamp when the drift signal was emitted.
- version_id: string (required) — version identifier for this emitted DriftSignal.
- created_at: datetime (required) — timestamp when this DriftSignal was first created.
- updated_at: datetime (required) — timestamp when this DriftSignal version was last updated; equals `created_at` for immutable first emissions.
- version_hash: string (required) — deterministic hash over the canonical serialized DriftSignal content.
- source_ref: string (required) — primary ConformanceRecord or violation bundle reference that caused the signal to exist.
- produced_by_motor: string (required) — constant value `motor_022`.
- produced_at: datetime (required) — timestamp when motor_022 emitted the signal.
- parent_id: string|null (required) — prior DriftSignal identifier when this signal supersedes an earlier signal for the same scope and basis; null for the first signal.

## relationships
- ConformanceRecord.contract_id and ConformanceRecord.contract_version_id reference the applicable `phase_contracts` from motor_001. The reference is read-only and defines the authority for contract, boundary and handoff checks.
- ConformanceRecord.evaluated_version_id and ConformanceRecord.lineage_id reference `version_records` from motor_002. The reference is used to verify reconstructibility and lineage presence without creating or mutating upstream versions.
- ConformanceRecord.quality_record_ids reference `quality_records` from motor_007. These records are evidence inputs only; motor_022 does not recompute quality or fitness scores.
- ConformanceRecord.harness_result_ids reference `harness_results` from motor_021. These records are evidence inputs only; motor_022 does not execute harness tests.
- ViolationRecord.conformance_record_id references exactly one ConformanceRecord.record_id. A ViolationRecord must not exist as an orphan outside its evaluation context except for a structured batch rejection represented through source_ref.
- ConformanceRecord.violation_ids references zero or more ViolationRecord.violation_id values produced by the same evaluation. If status is `FAIL`, at least one referenced violation must be material.
- DriftSignal.related_violation_ids references one or more ViolationRecord.violation_id values. A DriftSignal cannot be emitted from narrative assessment without linked violations.
- DriftSignal.related_conformance_record_ids references the ConformanceRecord.record_id values that produced the related violations.
- ConformanceRecord.drift_signal_ids references zero or more DriftSignal.signal_id values emitted from the current evaluation or related evaluation set.
- ViolationRecord.input_ref, ConformanceRecord.evidence_refs and DriftSignal.evidence_refs preserve references to the exact upstream inputs used for the decision.
- parent_id on each entity links only to a prior same-type output or documented parent context for reconstruction. It never authorizes mutation of the prior record.

## identifiers
- ConformanceRecord canonical identifier: `record_id`. Recommended deterministic composition: `motor_022:{evaluated_object_type}:{evaluated_object_id}:{evaluated_version_id}:{contract_id}:{contract_version_id}`.
- ViolationRecord canonical identifier: `violation_id`. Recommended deterministic composition: `{record_id}:violation:{violation_type}:{rule_ref}:{input_ref}:{expected_condition_hash}:{observed_value_hash}`.
- DriftSignal canonical identifier: `signal_id`. Recommended deterministic composition: `motor_022:drift:{scope}:{scope_ref}:{basis}:{severity}:{related_violation_set_hash}`.
- `evaluated_object_id`, `contract_id`, `evaluated_version_id`, `lineage_id`, `quality_record_ids`, `harness_result_ids` and evidence references are external identifiers owned by their producing motors and must not be rewritten by motor_022.
- `record_id`, `violation_id` and `signal_id` are stable after emission. Re-evaluation or corrected upstream evidence creates new output versions rather than silently changing historical identifiers.

## versioning
- Every ConformanceRecord, ViolationRecord and DriftSignal carries `version_id: string`, `created_at: datetime`, `updated_at: datetime` and `version_hash: string`.
- `version_id` versions the emitted motor_022 output record. It does not create, modify or supersede upstream versions owned by motor_002.
- `created_at` records first creation of the emitted output. `updated_at` records the latest state-preserving update and equals `created_at` for immutable first emissions.
- `version_hash` is computed from canonical serialized semantic fields and excludes non-semantic transport metadata.
- ConformanceRecord.version_hash includes evaluated object identity, evaluated version, contract reference, lineage reference, quality record ids, harness result ids, status, status reason, violation ids, drift signal ids and evidence references.
- ViolationRecord.version_hash includes parent record id, evaluated object identity, evaluated version, violation type, rule reference, severity, input reference, expected condition, observed value, material flag and evidence references.
- DriftSignal.version_hash includes scope, scope reference, basis, severity, related violation ids, related conformance record ids and evidence references.
- Re-running evaluation against changed contracts, version records, quality records or harness results emits a new `version_id` and may set `parent_id` to the prior output. Historical outputs are append-only.

## lineage
- Every ConformanceRecord, ViolationRecord and DriftSignal carries `source_ref: string`, `produced_by_motor: string`, `produced_at: datetime` and `parent_id: string|null`.
- `source_ref` identifies the upstream evaluated object, input bundle, parent conformance record or violation set that caused the output to exist.
- `produced_by_motor` is always `motor_022` for records emitted by this motor.
- `produced_at` records the motor_022 emission time and is distinct from timestamps on upstream contracts, version records, quality records or harness results.
- `parent_id` links re-evaluations, re-issued violations or superseding drift signals to their prior output. Null means there is no prior same-scope output or parent output.
- ConformanceRecord lineage must preserve evaluated object id, evaluated version id, contract id, contract version id, lineage id, source_ref, produced_by_motor and produced_at.
- ViolationRecord lineage must preserve conformance_record_id, evaluated object id, evaluated version id, rule_ref, input_ref, evidence_refs, source_ref, produced_by_motor and produced_at.
- DriftSignal lineage must preserve scope, scope_ref, related_violation_ids, related_conformance_record_ids, evidence_refs, source_ref, produced_by_motor and produced_at.
- Lineage fields are audit metadata only. They do not authorize motor_022 to correct violations, modify contracts, edit version records, rerun quality evaluation, execute harness tests or change motor state.
