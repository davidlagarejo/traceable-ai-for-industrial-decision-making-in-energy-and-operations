# Operational Rules — Dataset / Object Test Harness Engine

Motor ID: motor_021

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Correr pruebas sobre datasets, handoffs, contratos y objetos del sistema.
why_it_exists:  Los motores pueden pasar solos y aun así fallar juntos en integración.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    test_result, harness_report, integration_failure_log
key_objects:    TestResult, HarnessReport, IntegrationFailure
what_not_to_do: No modifica datos. No produce outputs analíticos. Solo prueba y reporta.
design_notes:   Harness transversal. Prueba el sistema integrado, no motores individuales.

Documentation-base content is filled for Gate 1 review.
-->

## rules
1. Cada prueba debe declarar `case_name`, inputs requeridos, condicion esperada y regla de evaluacion antes de ejecutarse.
2. Cada objeto bajo prueba debe estar referenciado por identificador estable y conectado a un contrato, una version o una fuente de provenance verificable.
3. Cada validacion contractual debe usar `phase_contracts` como autoridad de campos requeridos, outputs permitidos y handoff rules.
4. Cada validacion taxonomica debe usar la `canonical_taxonomy` recibida como snapshot versionado; no se permiten terminos inferidos fuera de esa taxonomia.
5. Cada validacion de lineage debe confirmar que `version_records`, `lineage_refs` o `provenance_refs` permiten reconstruir el origen del objeto bajo prueba.
6. Cada validacion de identidad debe comprobar que las referencias de entidad usadas por datasets y objetos resuelven a un `identity_record` compatible.
7. Cada validacion de calidad debe comprobar que el objeto bajo prueba tiene `quality_record` cuando el contrato o handoff lo exige.
8. Cada fallo debe producir un `IntegrationFailure` con `failure_type`, `affected_object_ref`, `expected_ref`, `observed_value`, `source_input_refs`, severidad y owner sugerido.
9. Un `HarnessReport` solo puede marcar `status = pass` cuando todos los `TestResult` obligatorios estan en `pass` y no existen fallas criticas.
10. Todo rechazo de input debe quedar expresado con codigo estructurado y no como texto narrativo sin referencias.

## invariants
- Los inputs aceptados permanecen inmutables desde la perspectiva del harness antes, durante y despues de cada ejecucion.
- Cada `TestResult` conserva referencias a los inputs que fueron evaluados y a la version del harness que ejecuto el caso.
- Cada `IntegrationFailure` puede rastrearse a un `TestResult` y a uno o mas `source_input_refs`.
- Los conteos de `HarnessReport.result_counts` siempre coinciden con la cantidad real de resultados emitidos por estado.
- La decision agregada del reporte nunca contradice la severidad maxima de las fallas detectadas.
- Ningun output del harness existe sin timestamp de ejecucion o generacion.
- Los identificadores emitidos son estables para la misma combinacion de `harness_run_id`, `case_name`, input refs y version del harness.

## forbidden_operations
- Modificar datos, datasets, normalized records, identity records, quality records, contracts, version records o taxonomy snapshots.
- Producir outputs analiticos, inferencias, interpretaciones sustantivas, rankings, recomendaciones de decision o conclusiones de investigacion.
- Reparar silenciosamente referencias rotas, campos faltantes, taxonomias invalidas, lineage gaps o conflictos de identidad.
- Crear nuevos contratos de fase, nuevas versiones de objeto, nuevos terminos canonicos, nuevos registros de identidad o nuevos quality scores.
- Ejecutar normalizacion, identity resolution, quality scoring, propagation, rebuild, reporting analitico o conformance review arquitectonica.
- Cambiar estado operativo de otro motor o cerrar un gate por cuenta propia.
- Tratar un warning como pass sin conservar la falla, severidad y evidencia que justifican la degradacion.
