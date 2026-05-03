# Conceptual Schema — Propagation / Re-evaluation Engine

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

## entities
- `ReEvaluationJob`: orden encolada y trazable que solicita volver a evaluar un objeto downstream afectado por un cambio versionado, una senal de calidad o un evento de fuente.
- `StaleObject`: representacion de un objeto o version downstream que no debe tratarse como vigente sin re-evaluacion adicional.
- `PropagationRecord`: registro auditable de una decision de propagacion, incluyendo inputs, ruta de dependencia, jobs emitidos, objetos marcados stale y rechazos.

## relationships
- `version_records.VersionRecord` -> `PropagationRecord` (un cambio versionado puede disparar una evaluacion de impacto downstream).
- `quality_records.QualityRecord` -> `PropagationRecord` (una degradacion de calidad o descalificacion puede disparar propagacion hacia consumidores del sujeto evaluado).
- `change_events.ChangeEvent` -> `PropagationRecord` (un cambio de fuente o stale signal puede disparar propagacion cuando afecta lineage conocido).
- `PropagationRecord` -> `StaleObject` (cada decision puede marcar cero o muchos objetos como stale).
- `StaleObject` -> `ReEvaluationJob` (cada objeto stale elegible produce cero o un job activo por trigger, version objetivo y version de regla).
- `ReEvaluationJob` -> `PropagationRecord` (cada job conserva la referencia al registro de propagacion que justifica su creacion).

## key_fields
`ReEvaluationJob`
- `job_id`: string
- `target_object_ref`: string
- `target_version_ref`: string|null
- `trigger_ref`: string
- `reason_code`: enum string (`version_change`, `quality_change`, `source_change`, `contract_change`, `taxonomy_change`, `library_change`)
- `priority`: enum string (`low`, `medium`, `high`, `urgent`)
- `dependency_path`: list[string]
- `status`: enum string (`queued`, `blocked`, `rejected`)
- `created_at`: datetime string

`StaleObject`
- `stale_object_id`: string
- `object_ref`: string
- `version_ref`: string|null
- `stale_reason`: enum string (`upstream_version_changed`, `quality_degraded`, `source_changed`, `contract_changed`, `taxonomy_changed`, `library_changed`)
- `trigger_ref`: string
- `lineage_refs`: list[string]
- `severity`: enum string (`info`, `warning`, `critical`)
- `detected_at`: datetime string

`PropagationRecord`
- `propagation_record_id`: string
- `input_refs`: list[string]
- `trigger_ref`: string
- `affected_object_refs`: list[string]
- `emitted_job_ids`: list[string]
- `stale_set_ref`: string|null
- `decision`: enum string (`jobs_emitted`, `no_affected_objects`, `blocked_untraceable`, `rejected_invalid_input`, `deduplicated`)
- `rule_version`: string
- `evaluated_at`: datetime string
