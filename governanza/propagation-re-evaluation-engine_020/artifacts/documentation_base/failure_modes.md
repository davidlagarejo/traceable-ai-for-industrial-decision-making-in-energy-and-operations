# Failure Modes — Propagation / Re-evaluation Engine

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

## failure_modes_list
- LINEAGE_GAP: el motor recibe triggers validos pero no puede construir rutas de dependencia hacia objetos downstream; aparecen muchos `blocked_untraceable` y pocos jobs incluso ante cambios criticos.
- OVER_PROPAGATION_STORM: un trigger pequeno genera jobs para objetos no relacionados por falta de filtros de lineage o deduplicacion; el numero de jobs por trigger crece sin relacion con el `impact_set`.
- UNDER_PROPAGATION_MISS: objetos downstream afectados no se marcan stale porque el motor ignora `quality_records`, `impact_set` o `lineage_refs` presentes.
- DUPLICATE_JOB_EMISSION: el mismo target recibe varios `ReEvaluationJob` equivalentes para el mismo trigger y version de reglas.
- SILENT_MUTATION_DRIFT: una implementacion futura empieza a corregir objetos o quality flags en lugar de emitir senales de re-evaluacion.
- UNBOUNDED_CHAIN_EXPANSION: la propagacion recorre dependencias sin limite de reglas o sin registrar decision, generando logs incompletos e imposibles de auditar.

## anti_patterns
- Usar este motor como reparador de datos o ejecutor de rebuild; eso mezcla senalizacion con transformacion y oculta responsabilidades de los motores propietarios.
- Tratar `refresh_priority` o `change_detection_event` como orden directa de recaptura sin verificar impacto downstream mediante versionado y lineage.
- Encolar jobs por coincidencia textual de nombres de objeto o fuente en lugar de referencias estables.
- Reducir `propagation_log` a mensajes narrativos sin `input_refs`, `decision`, `rule_version` y caminos de dependencia.
- Bypassear deduplicacion para "asegurar cobertura", produciendo ruido operativo y perdida de trazabilidad.

## degradation_signals
- Porcentaje de `blocked_untraceable` mayor al umbral operativo en lotes con lineage conocido.
- Ratio de `ReEvaluationJob` por trigger muy superior al tamano declarado de `impact_set`.
- Triggers `critical` con `affected_object_refs = []` de forma repetida mientras existen dependencias registradas en motor_002.
- Incremento sostenido de jobs duplicados suprimidos para la misma combinacion de trigger, target y rule version.
- `PropagationRecord` sin `input_refs`, sin `dependency_path` o sin `rule_version`.
- Diferencia entre objetos marcados stale y jobs emitidos sin decision documentada `blocked_untraceable`, `deduplicated` o `no_affected_objects`.
- Aumento de latencia entre `detected_at` del trigger y `created_at` del job sin explicacion en logs.
