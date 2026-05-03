# Design Done Criteria — Propagation / Re-evaluation Engine

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

## criteria
- `functional_contract.md` declara como inputs `version_records`, `quality_records` y `change_events`, y como outputs `re_evaluation_job`, `stale_set` y `propagation_log`.
- `functional_contract.md` prohibe la modificacion directa de objetos y limita el motor a encolar y senalizar re-evaluacion.
- `conceptual_schema.md` define `ReEvaluationJob`, `StaleObject` y `PropagationRecord` con campos obligatorios, relaciones y referencias de trazabilidad.
- `operational_rules.md` exige trigger explicito, ruta de dependencia reconstruible, deduplicacion y registro de rechazos estructurados.
- `acceptance_tests.md` cubre al menos un happy path con valores concretos, casos limite de ausencia de downstream y deduplicacion, y criterios de rechazo con codigos de error.
- `failure_modes.md` documenta fallos de sobre-propagacion, sub-propagacion, falta de lineage, duplicados y mutacion silenciosa.
- Los siete artefactos de `documentation_base` existen, tienen contenido sustantivo y no contienen marcadores abiertos de trabajo.
- La documentacion base permite derivar un schema tecnico sin inventar nuevas responsabilidades, motores, inputs principales u outputs principales.
