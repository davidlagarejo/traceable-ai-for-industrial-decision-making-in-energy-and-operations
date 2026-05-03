# Operational Rules — Evaluation / Conformance Engine

Motor ID: motor_022

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
why_it_exists:  Evita degradación silenciosa del sistema con el tiempo.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), quality_records (motor_007), harness_results (motor_021)
key_outputs:    conformance_record, violation_log, architectural_drift_signal
key_objects:    ConformanceRecord, ViolationRecord, DriftSignal
what_not_to_do: No corrige violaciones. No modifica el sistema. Solo detecta y registra conformidad.
design_notes:   Evaluación formal de conformidad. Depende de motor_001, motor_002, motor_007 y motor_021.

Sections below are completed with motor-specific content.
-->

## rules
1. Every conformance evaluation must be anchored to one applicable `phase_contract`; evaluation without contract authority is rejected.
2. Every evaluated object must have a stable `object_id` or `target_id` and a compatible `version_id` present in `version_records`.
3. A `PASS` status is allowed only when no material contract, boundary, lineage, quality or harness violation is detected for the evaluated unit.
4. A `WARNING` status is used when evidence is complete enough to evaluate but non-material issues, soft quality failures or early drift indicators are present.
5. A `FAIL` status is used when any material contract breach, boundary breach, missing required lineage, incompatible version reference or failed required harness assertion is present.
6. Every detected violation must produce exactly one `ViolationRecord` with rule reference, severity, input reference and expected condition.
7. Every `DriftSignal` must be derived from explicit `ViolationRecord` evidence; drift cannot be emitted from intuition or narrative assessment.
8. The motor must preserve all input identifiers and evidence references needed to reconstruct why each status was assigned.

## invariants
- Input records are read-only during evaluation and are never rewritten by this motor.
- `record_id`, `violation_id` and `signal_id` are stable identifiers once emitted.
- `lineage_id` is never null in an emitted `ConformanceRecord`.
- Every emitted status has traceable evidence through `evidence_refs`.
- A `ViolationRecord` never exists without a parent `ConformanceRecord`.
- A `DriftSignal` never references violation identifiers absent from the emitted `violation_log`.
- Output records preserve the source motor references for contract, version, quality and harness evidence.

## forbidden_operations
- Correcting, patching or rewriting any violation detected in a motor, dataset, artifact, contract or handoff.
- Modifying the system under evaluation, including motor states, datasets, phase contracts, version records, quality records or harness results.
- Executing harness tests directly; test execution remains outside this motor.
- Recomputing quality or fitness scores already owned by `motor_007`.
- Creating new contracts, new motor responsibilities or new architectural boundaries.
- Suppressing material violations because a downstream process may handle them later.
- Emitting conformance outputs without provenance, lineage and evidence references.
