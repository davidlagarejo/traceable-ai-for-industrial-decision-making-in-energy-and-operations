# Test Spec — Propagation / Re-evaluation Engine

Motor ID: motor_020

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Re-evaluar objetos downstream cuando cambian fuentes, reglas, taxonomías, contratos o bibliotecas.
why_it_exists:  Versioning registra cambios, pero este motor decide qué debe re-evaluarse.
key_inputs:     version_records (motor_002), quality_records (motor_007), change_events (motor_009)
key_outputs:    re_evaluation_job, stale_set, propagation_log
key_objects:    ReEvaluationJob, StaleObject, PropagationRecord
what_not_to_do: No modifica objetos directamente. Encola y señaliza para re-evaluación.
design_notes:   Corre en respuesta a cambios detectados. Crea cadenas de re-evaluación.

Tests-stage content is filled for Gate 3 review.
-->

## happy_path
Input minimo valido:
- `change_events` contiene un objeto con `event_id = CE-009-2026-04-17-001`, `source_id = SRC-418`, `change_type = schema`, `severity = critical`, `detected_at = 2026-04-17T10:00:00Z`, `evidence_refs = [ING-884]` y `lineage_refs = [LN-SRC-418]`.
- `version_records` contiene un objeto con `version_id = VR-002-DATASET-418-v5`, `object_id = DATASET-418`, `object_type = normalized_dataset`, `mutation_type = update`, `prior_version_ref = VR-002-DATASET-418-v4`, `impact_set = [OBJ-REPORT-121, OBJ-CLAIM-077]`, `lineage_refs = [LN-SRC-418, LN-DATASET-418]`, `phase_contract_ref = PCR-F2-REPORTING`, `created_at = 2026-04-17T09:55:00Z` y `provenance_refs = [ING-884]`.
- `quality_records` contiene un objeto con `quality_record_id = QR-007-OBJ-REPORT-121`, `subject_ref = OBJ-REPORT-121`, `phase_contract_ref = PCR-F2-REPORTING`, `evaluation_status = conditional_pass`, `quality_flags = [contract_mismatch]`, `fitness_score = 0.71`, `evaluation_run_id = QE-007-2026-04-17-004`, `evaluated_at = 2026-04-17T10:02:00Z` y `lineage_refs = [LN-DATASET-418]`.

Expected output:
- `stale_set` contiene exactamente dos `StaleObject`: uno para `object_ref = OBJ-REPORT-121` y otro para `object_ref = OBJ-CLAIM-077`.
- Cada `StaleObject` incluye `stale_object_id`, `object_ref`, `stale_reason = source_changed`, `trigger_ref = CE-009-2026-04-17-001`, `trigger_type = change_event`, `lineage_refs`, `dependency_path`, `severity = critical`, `detected_at = 2026-04-17T10:00:00Z`, `propagation_record_id`, `version_id`, `version_hash`, `source_ref`, `produced_by_motor = motor_020` y `produced_at`.
- `re_evaluation_job` contiene exactamente dos `ReEvaluationJob` en `status = queued`, uno por objeto afectado, con `reason_code = source_change`, `priority` en `[high, urgent]`, `trigger_ref = CE-009-2026-04-17-001`, `trigger_type = change_event`, `dependency_path` reconstruible desde `LN-SRC-418` y `LN-DATASET-418`, `input_refs` que incluyen los tres identificadores de entrada y `propagation_record_id` igual al registro emitido.
- `propagation_log` contiene un `PropagationRecord` con `decision = jobs_emitted`, `error_code = null`, `trigger_ref = CE-009-2026-04-17-001`, `trigger_type = change_event`, `input_refs = [CE-009-2026-04-17-001, VR-002-DATASET-418-v5, QR-007-OBJ-REPORT-121]`, `affected_object_refs = [OBJ-REPORT-121, OBJ-CLAIM-077]`, dos `emitted_job_ids`, dos `stale_object_ids`, `rule_version` no vacio, `produced_by_motor = motor_020` y timestamps parseables.
- Ningun input, objeto downstream, `VersionRecord`, `QualityRecord` o `ChangeEvent` es modificado por el motor.

## sparse_case
Input con campos opcionales ausentes:
- `change_events` contiene `CE-009-LOW-001` con `event_id`, `source_id = SRC-900`, `change_type = availability`, `severity = warning`, `detected_at = 2026-04-17T11:00:00Z`, `evidence_refs = [SRC-SNAPSHOT-900]` y `lineage_refs = [LN-SRC-900]`; no incluye referencia de version ni campo de staleness externo.
- `version_records` contiene `VR-002-SRC-900-v2` con `version_id`, `object_id = SRC-900`, `object_type = source_record`, `mutation_type = update`, `prior_version_ref = null`, `lineage_refs = [LN-SRC-900]`, `impact_set = []`, `phase_contract_ref = PCR-F1-SOURCE`, `created_at = 2026-04-17T10:59:00Z` y `provenance_refs = [SRC-SNAPSHOT-900]`.
- `quality_records = []`.

Expected output:
- El lote se acepta porque los inputs principales son colecciones y existe al menos un trigger trazable con identificador estable, timestamp parseable y evidencia minima.
- El motor emite un `PropagationRecord` con `decision = no_affected_objects`, `trigger_ref = CE-009-LOW-001`, `input_refs = [CE-009-LOW-001, VR-002-SRC-900-v2]`, `affected_object_refs = []`, `emitted_job_ids = []`, `stale_object_ids = []`, `rejected_input_refs = []`, `error_code = null` y `rule_version` no vacio.
- `stale_set = []` y no se emite ningun `ReEvaluationJob`.
- La ausencia de `quality_records`, `target_version_ref` o downstream en `impact_set` no produce error fatal mientras se conserve la trazabilidad del trigger y se registre la decision `no_affected_objects`.

## malformed_input
Input invalido:
- Caso A: `version_records` llega como objeto simple en vez de lista, con valor `{ "version_id": "VR-002-BAD" }`; `quality_records = []`; `change_events = []`.
- Caso B: `change_events` contiene `{ "event_id": "CE-009-BAD-001", "source_id": "SRC-500", "change_type": "schema", "severity": "critical", "detected_at": "17-04-2026", "evidence_refs": [], "lineage_refs": [] }`; `version_records = []`; `quality_records = []`.
- Caso C: `quality_records` contiene `{ "quality_record_id": "QR-007-BAD-001", "evaluation_status": "fail", "evaluated_at": "2026-04-17T12:00:00Z" }` sin `subject_ref`; `version_records = []`; `change_events = []`.

Expected behavior:
- Caso A rechaza el lote completo con error estructurado `INVALID_PROPAGATION_INPUT` porque los tres inputs principales deben ser colecciones y no puede normalizar silenciosamente un objeto suelto.
- Caso B rechaza el item `CE-009-BAD-001` con `INVALID_PROPAGATION_INPUT` porque `detected_at` no es parseable y no existe evidencia minima en `evidence_refs`, `lineage_refs`, `impact_set` o referencia equivalente.
- Caso C rechaza el item `QR-007-BAD-001` con `INVALID_PROPAGATION_INPUT` porque un `quality_record` requiere `quality_record_id`, `subject_ref` y `evaluation_status`.
- En cada rechazo, `propagation_log` conserva el identificador rechazado en `rejected_input_refs`, usa `decision = rejected_invalid_input`, deja `affected_object_refs = []`, `emitted_job_ids = []`, `stale_object_ids = []`, y no produce jobs activos ni stale markers.

## edge_cases
1. Trigger valido sin downstream afectado:
   - Input: `change_event CE-009-SRC-900` tiene `source_id = SRC-900`, `detected_at = 2026-04-17T11:30:00Z`, `evidence_refs = [SRC-SNAPSHOT-900]` y `lineage_refs = [LN-SRC-900]`, pero ningun `version_record`, `impact_set`, dependency edge o `quality_record.subject_ref` conecta esa fuente con objetos downstream.
   - Expected output: un `PropagationRecord` con `decision = no_affected_objects`, `error_code = null`, `affected_object_refs = []`, `emitted_job_ids = []`, `stale_object_ids = []`; `stale_set = []`; no se crea `ReEvaluationJob`.

2. Duplicados bajo el mismo trigger y version de reglas:
   - Input: `change_event CE-009-DUP-001`, `version_record VR-002-DUP-v3` y dos `quality_records` apuntan a `target_object_ref = OBJ-77` o `subject_ref = OBJ-77` bajo el mismo `trigger_ref`, `target_version_ref = OBJ-77-v9` y `propagation_rule_version = prop-rules-020.1.0`.
   - Expected output: se emite un solo `ReEvaluationJob` para la clave logica `(CE-009-DUP-001, OBJ-77, OBJ-77-v9, prop-rules-020.1.0)`, un solo `StaleObject` activo para `OBJ-77`, y el `PropagationRecord` conserva todos los `input_refs` con `secondary_decisions` que incluye `deduplicated`.

3. Ruta parcialmente trazable:
   - Input: un `version_record` declara `impact_set = [OBJ-TRACEABLE-1, OBJ-UNKNOWN-2]`; `OBJ-TRACEABLE-1` tiene `lineage_refs` y dependency path reconstruible, pero `OBJ-UNKNOWN-2` no puede conectarse al trigger por lineage, source, impact edge o subject reference.
   - Expected output: el motor emite job y stale marker solo para `OBJ-TRACEABLE-1`; registra la rama de `OBJ-UNKNOWN-2` con `decision` o `secondary_decisions` que incluye `blocked_untraceable`, `error_code = UNTRACEABLE_PROPAGATION_PATH`, y no inventa un dependency path.

4. Job no seguro antes de emision:
   - Input: la resolucion de impacto produce un candidato sin `target_object_ref` o sin evidencia reconstruible aunque el trigger sea valido.
   - Expected output: no se emite job activo para ese candidato; `PropagationRecord` registra `decision = blocked_untraceable` o `rejected_invalid_input` segun el punto de falla, `error_code = UNSAFE_REEVALUATION_JOB`, `emitted_job_ids` no contiene el candidato y los inputs originales quedan inmutables.

## pass_criteria
El test pasa si se observan todas estas condiciones:
- Cada input valido produce una decision auditada en `propagation_log` con `PropagationRecord.produced_by_motor = motor_020`, `input_refs`, `trigger_ref`, `trigger_type`, `decision`, `rule_version`, `evaluated_at`, `version_id`, `version_hash`, `source_ref` y `produced_at` no vacios.
- Cada objeto afectado y trazable aparece en `stale_set` con `StaleObject.object_ref`, `stale_reason`, `trigger_ref`, `dependency_path`, `severity`, `propagation_record_id`, `version_id`, `version_hash` y lineage suficiente para reconstruir la propagacion.
- Cada `ReEvaluationJob` activo tiene `status = queued`, `target_object_ref`, `trigger_ref`, `reason_code`, `priority`, `dependency_path`, `input_refs`, `evidence_refs`, `propagation_record_id`, `propagation_rule_version`, `version_id`, `version_hash`, `source_ref` y `produced_by_motor = motor_020`.
- Los jobs se deduplican por `trigger_ref`, `target_object_ref`, `target_version_ref` y `propagation_rule_version`; las entradas duplicadas quedan visibles en `PropagationRecord.input_refs` o `secondary_decisions`.
- Los casos sin downstream afectado generan `decision = no_affected_objects`, `stale_set = []` y cero jobs, sin error fatal.
- Los inputs invalidos o no trazables generan errores estructurados entre `INVALID_PROPAGATION_INPUT`, `UNTRACEABLE_PROPAGATION_PATH` y `UNSAFE_REEVALUATION_JOB`, preservando `rejected_input_refs`.
- Ningun output modifica, reconstruye, reversiona, recalifica o declara vigente un objeto downstream; el motor solo senaliza stale state, registra propagacion y encola re-evaluacion.

## fail_criteria
El test falla si se detecta cualquiera de estas condiciones:
- Se acepta un lote cuyos tres inputs principales no son colecciones o estan todos vacios.
- Se acepta un item sin identificador primario requerido, timestamp parseable o referencia minima de evidence, provenance, lineage, impact o subject.
- Se emite un `ReEvaluationJob` sin `target_object_ref`, `trigger_ref`, `reason_code`, `priority`, `dependency_path`, `evidence_refs`, `propagation_record_id` o `propagation_rule_version`.
- Se emite un `StaleObject` sin `object_ref`, `stale_reason`, `trigger_ref`, `dependency_path`, `severity`, `detected_at` o `propagation_record_id`.
- Se emiten jobs duplicados para la misma combinacion de `trigger_ref`, `target_object_ref`, `target_version_ref` y `propagation_rule_version`.
- Un trigger valido sin downstream afectado produce un job vacio, una excepcion fatal o ausencia de `PropagationRecord`.
- Una ruta no trazable se resuelve inventando lineage, omitiendo `UNTRACEABLE_PROPAGATION_PATH` o perdiendo la referencia al input rechazado.
- El motor modifica `version_records`, `quality_records`, `change_events`, objetos downstream, scores de calidad, contratos, taxonomias o versiones upstream.
