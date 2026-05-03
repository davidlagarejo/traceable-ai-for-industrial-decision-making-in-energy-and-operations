# Conceptual Schema — Evaluation / Conformance Engine

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

## entities
- ConformanceRecord: registro principal que representa la evaluacion de una unidad versionada contra su contrato, quality record y harness result aplicables.
- ViolationRecord: registro atomico de una regla de contrato, limite, lineage o harness incumplida durante una evaluacion de conformidad.
- DriftSignal: senal agregada que representa desviacion arquitectonica recurrente, sistemica o de alta severidad derivada de uno o mas `ViolationRecord`.

## relationships
- ConformanceRecord -> ViolationRecord (un registro de conformidad puede contener cero o mas violaciones cuando su `status` es `WARNING` o `FAIL`).
- ViolationRecord -> ConformanceRecord (cada violacion pertenece exactamente a un registro de conformidad y no existe sin evaluacion fuente).
- DriftSignal -> ViolationRecord (una senal de drift referencia una o mas violaciones relacionadas por scope, regla o patron repetido).
- ConformanceRecord -> phase_contracts (cada evaluacion referencia exactamente un contrato aplicable como autoridad de comparacion).
- ConformanceRecord -> version_records (cada evaluacion referencia al menos un registro de versionado para preservar lineage y comparabilidad).
- ConformanceRecord -> quality_records (cada evaluacion puede incorporar cero o mas quality records aplicables, siempre que esten versionados).
- ConformanceRecord -> harness_results (cada evaluacion puede incorporar cero o mas resultados de harness aplicables, siempre que esten vinculados a target y version).

## key_fields
ConformanceRecord:
- record_id: string
- evaluated_object_id: string
- evaluated_version_id: string
- contract_id: string
- lineage_id: string
- status: enum[`PASS`, `WARNING`, `FAIL`]
- evidence_refs: list[string]
- evaluated_at: datetime

ViolationRecord:
- violation_id: string
- conformance_record_id: string
- rule_ref: string
- severity: enum[`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`]
- input_ref: string
- expected_condition: string
- observed_value: string

DriftSignal:
- signal_id: string
- scope: enum[`motor`, `dataset`, `artifact`, `handoff`, `phase`]
- basis: string
- severity: enum[`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`]
- related_violation_ids: list[string]
- evidence_refs: list[string]
- emitted_at: datetime
