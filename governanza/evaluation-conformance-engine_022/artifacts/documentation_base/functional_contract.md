# Functional Contract — Evaluation / Conformance Engine

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

## inputs
- phase_contracts: collection[PhaseContract] - source `motor_001`; contratos vigentes por fase con `contract_id`, `phase_id`, `required_outputs`, `allowed_inputs`, `handoff_rules`, `boundary_rules` y `version_id`.
- version_records: collection[VersionRecord] - source `motor_002`; registros de versionado y lineage con `object_id`, `version_id`, `lineage_id`, `created_at`, `supersedes` y `provenance_ref`.
- quality_records: collection[QualityRecord] - source `motor_007`; evaluaciones de calidad o fitness con `object_id`, `version_id`, `quality_status`, `fitness_score`, `failed_checks` y `evidence_refs`.
- harness_results: collection[HarnessResult] - source `motor_021`; resultados de pruebas sobre datasets, handoffs, contratos u objetos con `test_run_id`, `target_id`, `target_version_id`, `result_status`, `failed_assertions` y `evidence_refs`.

## outputs
- conformance_record: ConformanceRecord - destination conformance review, governance reporting and downstream observability; resume el estado de conformidad de una unidad evaluada contra contrato, version, calidad y harness.
- violation_log: collection[ViolationRecord] - destination governance event/exception handling and audit trail consumers; registra incumplimientos con regla afectada, severidad, evidencia y referencias a inputs.
- architectural_drift_signal: DriftSignal - destination orchestration, observability and governance consumers; senala desviaciones recurrentes o sistemicas respecto a limites, contratos o lineage esperados.

## limits
- No acepta inputs sin identificador estable de objeto o fase, sin version asociada o sin referencia de provenance cuando el input declara evaluar un artefacto versionado.
- No acepta reglas de conformidad libres, narrativas o generadas ad hoc que no esten ancladas en `phase_contracts`, `version_records`, `quality_records` o `harness_results`.
- No acepta resultados de harness que no indiquen de forma explicita `target_id`, `target_version_id` y `result_status`.
- No produce objetos corregidos, contratos editados, datasets normalizados ni cambios de estado operativo de otros motores.
- No produce `PASS` si falta evidencia minima de contrato, versionado, calidad o harness para la unidad evaluada; en ese caso emite rechazo estructurado o estado `WARNING` segun la completitud disponible.
- No degrada una violacion material a recomendacion narrativa: toda violacion de contrato o boundary produce entrada en `violation_log`.

## validations
- Antes de procesar, cada input debe ser parseable como coleccion estructurada y contener los campos minimos declarados en la seccion `inputs`.
- Antes de procesar, cada `quality_record` y `harness_result` debe poder asociarse a un `object_id` o `target_id` y a una version compatible presente en `version_records`.
- Antes de evaluar conformidad, debe existir al menos un `phase_contract` aplicable al objeto, fase o handoff evaluado.
- Antes de emitir `conformance_record`, el motor debe incluir `record_id`, `evaluated_object_id`, `evaluated_version_id`, `contract_id`, `lineage_id`, `status`, `evidence_refs` y `evaluated_at`.
- Antes de emitir `violation_log`, cada `ViolationRecord` debe incluir `violation_id`, `conformance_record_id`, `rule_ref`, `severity`, `input_ref`, `observed_value` y `expected_condition`.
- Antes de emitir `architectural_drift_signal`, el motor debe incluir `signal_id`, `scope`, `basis`, `severity`, `related_violation_ids` y `evidence_refs`.
- Los estados de salida permitidos para conformidad son `PASS`, `WARNING` y `FAIL`; cualquier otro estado invalida la salida.
