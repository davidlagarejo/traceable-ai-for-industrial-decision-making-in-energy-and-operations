# Acceptance Tests — Propagation / Re-evaluation Engine

Motor ID: motor_020

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Re-evaluar objetos downstream cuando cambian fuentes, reglas, taxonomías, contratos o bibliotecas.
why_it_exists:  Versioning registra cambios, pero este motor decide qué debe re-evaluarse.
key_inputs:     version_records (motor_002), quality_records (motor_007), change_events (motor_009)
key_outputs:    re_evaluation_job, stale_set, propagation_log
key_objects:    ReEvaluationJob, StaleObject, PropagationRecord
what_not_to_do: No modifica objetos directamente. Encola y señaliza para re-evaluación.
design_notes:   Corre en respuesta a cambios detectados. Crea cadenas de re-evaluación.

Documentation-base content is filled for Gate 1 review.
-->

## happy_path
Input: `change_events` contiene `event_id = CE-009-2026-04-17-001`, `source_id = SRC-418`, `change_type = schema`, `severity = critical`, `lineage_refs = [LN-SRC-418]` y `evidence_refs = [ING-884]`; `version_records` contiene `version_id = VR-002-DATASET-418-v5`, `object_id = DATASET-418`, `object_type = normalized_dataset`, `mutation_type = update`, `impact_set = [OBJ-REPORT-121, OBJ-CLAIM-077]`, `lineage_refs = [LN-SRC-418, LN-DATASET-418]`; `quality_records` contiene `quality_record_id = QR-007-OBJ-REPORT-121`, `subject_ref = OBJ-REPORT-121`, `evaluation_status = conditional_pass` y una `quality_flag` de `contract_mismatch`.

Action: el motor valida los tres inputs, enlaza `CE-009-2026-04-17-001` con `VR-002-DATASET-418-v5`, atraviesa `impact_set`, marca `OBJ-REPORT-121` y `OBJ-CLAIM-077` como afectados y deduplica por trigger mas objeto objetivo.

Expected output: emite dos `StaleObject` con `stale_reason = source_changed`, dos `ReEvaluationJob` en estado `queued` con prioridad `urgent` o `high` segun severidad y quality flag, y un `PropagationRecord` con decision `jobs_emitted`, `input_refs = [CE-009-2026-04-17-001, VR-002-DATASET-418-v5, QR-007-OBJ-REPORT-121]` y `affected_object_refs = [OBJ-REPORT-121, OBJ-CLAIM-077]`.

## edge_cases
- Trigger valido sin downstream afectado: si `change_event CE-009-SRC-900` tiene `source_id`, evidencia y timestamp validos pero ningun `version_record` o dependency edge referencia esa fuente, el motor emite `PropagationRecord.decision = no_affected_objects`, `stale_set = []` y no crea `ReEvaluationJob`.
- Duplicados en el mismo run: si dos `quality_records` y un `version_record` apuntan al mismo `target_object_ref = OBJ-77` bajo el mismo `trigger_ref` y `rule_version`, el motor emite un solo `ReEvaluationJob`, conserva todos los `input_refs` en el `PropagationRecord` y registra decision secundaria `deduplicated`.
- Cambio de severidad baja: si un `change_event` tiene `severity = info` y solo afecta objetos no bloqueantes, el motor puede crear jobs de prioridad `low` o solo marcar stale si la regla de propagacion asi lo permite, pero debe conservar el trigger y la razon en `propagation_log`.
- Ruta parcial de lineage: si el trigger puede enlazarse al objeto fuente pero no a un objeto downstream concreto, el motor registra `blocked_untraceable` para esa rama y continua procesando las ramas trazables del mismo lote.

## rejection_criteria
- Rechaza con `INVALID_PROPAGATION_INPUT` cuando un `change_event` no tiene `event_id`, `source_id`, `detected_at` o evidencia minima.
- Rechaza con `INVALID_PROPAGATION_INPUT` cuando un `version_record` no tiene `version_id`, `object_id`, `object_type`, `mutation_type` o referencia de lineage/dependencia.
- Rechaza con `UNTRACEABLE_PROPAGATION_PATH` cuando un objeto objetivo no puede conectarse al trigger por lineage, impact_set, source reference o subject reference.
- Rechaza con `UNSAFE_REEVALUATION_JOB` cuando el job que se iba a emitir carece de `target_object_ref`, `trigger_ref`, `reason_code` o evidencia reconstruible.
