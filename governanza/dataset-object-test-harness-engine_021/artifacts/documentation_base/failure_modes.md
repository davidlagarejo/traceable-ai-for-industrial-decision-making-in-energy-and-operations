# Failure Modes — Dataset / Object Test Harness Engine

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

## failure_modes_list
- FALSE_PASS_ON_BROKEN_HANDOFF: el harness marca `pass` aunque un objeto no cumple campos requeridos por `phase_contracts`; aparecen reportes verdes con fallas downstream repetidas.
- REFERENCE_RESOLUTION_BLINDNESS: el harness no detecta `version_ref`, `taxonomy_ref`, `identity_ref` o `quality_record.subject_ref` inexistentes; los resultados carecen de `IntegrationFailure` pese a referencias rotas.
- LINEAGE_GAP_UNDETECTED: objetos sin lineage o provenance pasan pruebas porque el harness solo valida forma superficial y no reconstruibilidad.
- OVERREACHING_REPAIR: la implementacion futura empieza a corregir records, mapear terminos o fusionar identidades durante la prueba, ocultando fallas del motor propietario.
- COVERAGE_INFLATION: el `HarnessReport` declara cobertura completa aunque se saltaron casos obligatorios o no existian inputs necesarios para ejecutarlos.
- FAILURE_LOG_DRIFT: `TestResult.failure_ids` apunta a fallas ausentes o el `integration_failure_log` contiene fallas sin resultado asociado.
- NONDETERMINISTIC_RESULTS: el mismo lote y la misma version del harness producen estados distintos sin cambio de inputs.

## anti_patterns
- Usar el harness como reparador de datos para normalizar campos, corregir taxonomias o completar lineage faltante en lugar de reportar fallas.
- Reducir los resultados a mensajes narrativos sin `input_refs`, `expected_condition`, `observed_condition`, codigos de fallo y severidad.
- Probar solo un motor productor aislado y declarar integracion exitosa sin validar handoffs entre contratos, datasets, identidad, versionado y calidad.
- Tratar ausencia de objeto como `pass` por conveniencia operativa cuando el contrato exige que el objeto exista.
- Permitir reglas de prueba implicitas no versionadas, lo que impide reproducir por que un resultado fue `pass`, `warning`, `fail` o `skipped`.

## degradation_signals
- Ratio alto de `skipped` en casos obligatorios sin explicacion de falta de input o sin decision de cobertura parcial.
- `HarnessReport.result_counts` que no coincide con la cantidad real de `TestResult` emitidos.
- Fallas criticas en `integration_failure_log` mientras `HarnessReport.status = pass`.
- Aumento sostenido de `UNRESOLVED_REFERENCE`, `TAXONOMY_MISMATCH` o `LINEAGE_GAP` para contratos que antes pasaban con el mismo tipo de input.
- `TestResult` sin `input_refs`, sin `expected_condition`, sin `observed_condition` o sin `harness_version`.
- Re-ejecucion del mismo lote con misma version del harness que produce cambios de estado no explicados.
- Fallas asignadas a `owner_motor_ref` generico o vacio, lo que impide dirigir la correccion al motor responsable.
