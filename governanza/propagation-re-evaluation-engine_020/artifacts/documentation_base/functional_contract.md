# Functional Contract — Propagation / Re-evaluation Engine

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

## inputs
- `version_records`: list[VersionRecord-like object] — source: motor_002; contiene `version_id`, `object_id`, `object_type`, `mutation_type`, `prior_version_ref`, `lineage_refs` o dependency edges, `impact_set` cuando exista, `phase_contract_ref`, `created_at` y provenance.
- `quality_records`: list[QualityRecord-like object] — source: motor_007; contiene `quality_record_id`, `subject_ref`, `phase_contract_ref`, `evaluation_status`, `quality_flags`, `fitness_score`, `evaluation_run_id`, `evaluated_at` y referencias de version o lineage.
- `change_events`: list[ChangeEvent-like object] — source: motor_009; contiene `event_id`, `source_id`, `change_type`, `severity`, `detected_at`, `evidence_refs`, `lineage_refs` y referencias de version o staleness cuando existan.

## outputs
- `re_evaluation_job`: ReEvaluationJob object — destination: orchestrator, owning downstream motor, or job queue; contiene el objeto objetivo, disparador, razon, prioridad, dependencia seguida, estado `queued` o `blocked` y referencias de evidencia.
- `stale_set`: list[StaleObject] — destination: consumers that need stale awareness before use; enumera objetos downstream marcados para re-evaluacion con version objetivo, severidad, razon y trigger asociado.
- `propagation_log`: list[PropagationRecord] — destination: audit trail, conformance review and rebuild operators; registra inputs aceptados, caminos de propagacion, decisiones de encolado, deduplicaciones y rechazos estructurados.

## limits
- No acepta inputs sin identificador estable, timestamp parseable y referencia de provenance o lineage reconstruible.
- No acepta `change_events` que no puedan enlazarse a una fuente, version, objeto o lineage conocido en los inputs disponibles.
- No acepta `quality_records` sin `subject_ref`, `evaluation_status` y `quality_record_id`.
- No acepta `version_records` sin `version_id`, `object_id`, `object_type`, `mutation_type` y referencias de lineage o dependencia.
- No produce objetos modificados, versiones nuevas, scores de calidad, eventos de cambio de fuente, contratos, taxonomias ni datos recapturados.
- No produce una decision de re-evaluacion completada; el output maximo es una orden encolada o una senal stale trazable.
- No emite jobs sin target, trigger, razon, prioridad y referencias suficientes para reconstruir la decision.

## validations
- Rechaza un lote si los tres inputs principales no son colecciones o si todos estan vacios.
- Rechaza cada input item cuyo identificador primario este vacio: `version_id`, `quality_record_id` o `event_id` segun corresponda.
- Rechaza timestamps no parseables en `created_at`, `evaluated_at` o `detected_at`.
- Rechaza disparadores que no incluyan al menos una referencia de evidencia: `provenance_refs`, `evidence_refs`, `lineage_refs`, `impact_set` o `subject_ref`.
- Antes de propagar, verifica que cada objeto objetivo tenga `object_ref` o `target_object_ref`, `target_version_ref` cuando exista versionado, y una ruta de dependencia declarada.
- Deduplica jobs por `trigger_ref`, `target_object_ref`, `target_version_ref` y `propagation_rule_version`.
- Antes de emitir `stale_set`, asegura que cada StaleObject incluya `stale_object_id`, `object_ref`, `stale_reason`, `trigger_ref`, `detected_at` y `severity`.
- Antes de emitir `propagation_log`, asegura que cada PropagationRecord incluya `propagation_record_id`, `input_refs`, `affected_object_refs`, `decision`, `evaluated_at` y `rule_version`.
- Emite error estructurado `INVALID_PROPAGATION_INPUT` cuando falta estructura minima, `UNTRACEABLE_PROPAGATION_PATH` cuando no puede reconstruir el camino de impacto, y `UNSAFE_REEVALUATION_JOB` cuando un job carece de target o evidencia.
