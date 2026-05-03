# Operational Rules — Propagation / Re-evaluation Engine

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

## rules
1. Cada propagacion debe iniciar desde un trigger explicito: `version_record`, `quality_record` o `change_event`; no se permite propagacion por intuicion o por texto libre sin referencia.
2. Cada objeto afectado debe estar conectado al trigger por `lineage_refs`, `impact_set`, `subject_ref`, `source_id` o dependency edge declarado; si la ruta no existe, el objeto se registra como no propagable.
3. Cada `ReEvaluationJob` debe tener `job_id`, `target_object_ref`, `trigger_ref`, `reason_code`, `priority`, `dependency_path`, `status` y `created_at`.
4. Cada `StaleObject` debe preservar la referencia al objeto original y a la evidencia que lo volvio stale; el motor no puede reemplazar esa evidencia por un resumen no trazable.
5. La deduplicacion es obligatoria por combinacion de `trigger_ref`, `target_object_ref`, `target_version_ref` y `propagation_rule_version`.
6. La prioridad del job debe derivarse de severidad del evento, estado de calidad, tipo de mutacion y profundidad de dependencia; no puede asignarse manualmente sin quedar en `propagation_log`.
7. Un trigger valido que no tenga downstream afectado debe producir un `PropagationRecord` con decision `no_affected_objects`, no un job vacio.
8. Cada rechazo debe quedar registrado con codigo de error estructurado y referencias al input rechazado.

## invariants
- Los inputs aceptados siguen siendo inmutables desde la perspectiva de este motor antes y despues de procesar.
- Todo output puede reconstruirse desde `input_refs`, `trigger_ref`, `dependency_path`, `rule_version` y timestamp de evaluacion.
- Ningun `ReEvaluationJob` existe sin un `PropagationRecord` asociado.
- Ningun `StaleObject` existe sin `trigger_ref`, `stale_reason` y referencia al objeto afectado.
- Los identificadores emitidos son estables para la misma combinacion de trigger, objeto objetivo y version de reglas.
- Las decisiones `blocked_untraceable` y `rejected_invalid_input` no producen jobs activos.

## forbidden_operations
- Modificar objetos downstream directamente; este motor solo encola y senaliza para re-evaluacion.
- Crear, borrar, sobrescribir o corregir `VersionRecord`, `LineageNode` o `ImpactEdge`.
- Cambiar `QualityRecord`, `FitnessScore`, `QualityFlag` o `DisqualificationReason`.
- Detectar cambios de fuente, descargar datos, recapturar fuentes o alterar prioridades de refresh.
- Ejecutar transformaciones de dominio, normalizacion, identity resolution, scoring, reporting analitico o rebuild material.
- Declarar que un objeto re-evaluado ya esta vigente sin que el motor propietario complete su propio proceso.
- Resolver manualmente una falta de lineage inventando un camino de dependencia.
