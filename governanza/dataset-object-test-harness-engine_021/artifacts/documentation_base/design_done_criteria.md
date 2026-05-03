# Design Done Criteria — Dataset / Object Test Harness Engine

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

## criteria
- `functional_contract.md` declara como inputs `phase_contracts`, `version_records`, `canonical_taxonomy`, `normalized_records`, `identity_records` y `quality_records`, y como outputs `test_result`, `harness_report` e `integration_failure_log`.
- `functional_contract.md` prohibe modificar datos, producir outputs analiticos o emitir aprobaciones de conformidad arquitectonica global.
- `conceptual_schema.md` define `TestResult`, `HarnessReport` e `IntegrationFailure` con campos obligatorios, relaciones y referencias trazables.
- `operational_rules.md` exige pruebas versionadas, referencias resolubles, conteos consistentes, severidad coherente y fallas estructuradas.
- `acceptance_tests.md` cubre un happy path con valores concretos, casos limite de cobertura parcial, taxonomia amplia, quality condicional y duplicidad no erronea.
- `acceptance_tests.md` define rechazos explicitos para input invalido, referencias no resueltas, mismatch taxonomico, lineage gap y reporte inseguro.
- `failure_modes.md` documenta fallos de falso pass, ceguera de referencias, lineage no detectado, reparacion indebida, cobertura inflada y resultados no deterministas.
- Los siete artefactos de `documentation_base` existen, tienen contenido sustantivo y no contienen marcadores abiertos de trabajo.
- La documentacion base permite derivar un schema tecnico sin inventar nuevas responsabilidades, motores, inputs principales ni outputs principales.
