# Master Concept Document — Propagation / Re-evaluation Engine

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

## purpose
El Propagation / Re-evaluation Engine determina que objetos downstream deben volver a evaluarse cuando cambian fuentes, reglas, taxonomias, contratos, versiones o bibliotecas que afectan su lineage. Consume registros de versionado, senales de calidad y eventos de cambio para construir un conjunto trazable de objetos potencialmente stale. Su salida no corrige ni recalcula esos objetos: emite trabajos de re-evaluacion, un stale_set y un log de propagacion para que los motores responsables actuen dentro de sus propios contratos.

## what_it_does
- Recibe `version_records` de motor_002 y lee dependencias, versiones afectadas, `impact_set` o referencias de lineage disponibles.
- Recibe `quality_records` de motor_007 y usa flags, estados de aptitud y referencias de sujeto para detectar objetos que requieren re-evaluacion por deterioro estructural.
- Recibe `change_events` de motor_009 y los trata como disparadores de propagacion cuando hay cambios de fuente, metodologia, disponibilidad, schema, frecuencia o staleness.
- Vincula cada disparador con objetos downstream mediante referencias explicitas de version, lineage, fuente o sujeto evaluado.
- Construye un `stale_set` con los objetos que quedan marcados para re-evaluacion, incluyendo razon, severidad y referencias de evidencia.
- Encola `re_evaluation_job` deterministas para cada objeto afectado y evita duplicados por combinacion de disparador, objeto objetivo y version de reglas.
- Produce un `propagation_log` que permite reconstruir que inputs se recibieron, que caminos de dependencia se siguieron y por que se emitio o no cada job.

## what_it_does_not_do
- No modifica objetos directamente, no reescribe datasets, no parchea registros y no actualiza versiones existentes; encola y senaliza para re-evaluacion.
- No registra versiones ni crea lineage nuevo; esa responsabilidad pertenece a motor_002.
- No calcula fitness scores, no corrige quality flags y no decide aptitud final de uso; consume los resultados de motor_007.
- No detecta cambios de fuente ni decide recaptura; consume `change_events` y senales de staleness de motor_009.
- No ejecuta la re-evaluacion de contenido, no reconstruye objetos y no cierra jobs como completados por cuenta propia.
- No redefine contratos de fase, taxonomias, reglas de negocio ni criterios de calidad.

## why_it_exists
Versioning registra que algo cambio, quality indica si un objeto es apto, y source-change detection identifica cambios externos; este motor existe porque ninguna de esas piezas decide por si sola que objetos downstream deben entrar en una cadena de re-evaluacion. Separarlo evita que los motores productores muten consumidores de forma silenciosa y crea una capa auditada para propagar impacto sin invadir responsabilidades.
