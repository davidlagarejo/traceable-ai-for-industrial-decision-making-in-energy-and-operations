# Master Concept Document — Dataset / Object Test Harness Engine

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

## purpose
El Dataset / Object Test Harness Engine ejecuta pruebas deterministas sobre datasets, objetos, handoffs y contratos ya producidos por otros motores del sistema. Su funcion es comprobar que los artefactos integrados pueden convivir sin romper referencias, taxonomias, versionado, identidad, calidad ni contratos de fase. El motor no repara los artefactos bajo prueba; solo clasifica resultados, registra fallas de integracion y produce reportes reconstruibles.

## what_it_does
- Recibe `phase_contracts` de motor_001 y los usa como autoridad para campos requeridos, outputs permitidos y limites de cada fase.
- Recibe `version_records` de motor_002 para comprobar que cada objeto bajo prueba tiene version, lineage y provenance reconstruibles.
- Recibe `canonical_taxonomy` de motor_003 para verificar que categorias, tipos de objeto, codigos y vocabularios usados por los artefactos existen en la taxonomia vigente.
- Recibe `normalized_records` de motor_005 y valida que su estructura declarada sea compatible con contratos, taxonomy refs, version refs y quality refs.
- Recibe `identity_records` de motor_006 y comprueba que las referencias de entidad, alias y resolucion de identidad usadas por datasets y objetos sean consistentes.
- Recibe `quality_records` de motor_007 y verifica que los objetos bajo prueba tengan estado de calidad trazable cuando el contrato lo exige.
- Ejecuta casos de prueba de integracion sobre combinaciones de objetos y handoffs declarados.
- Emite un `test_result` por caso de prueba con estado, evidencias, referencias de input y codigo de fallo cuando aplica.
- Emite un `harness_report` agregado con resumen de ejecucion, cobertura de objetos, conteo de resultados y decision operativa del harness.
- Emite un `integration_failure_log` con fallas estructuradas, objeto afectado, contrato esperado, valor observado y severidad.

## what_it_does_not_do
- No modifica datos, no corrige registros normalizados, no fusiona identidades y no reescribe contratos, versiones, taxonomias ni quality records.
- No produce outputs analiticos, inferencias, scores de calidad, conclusiones de investigacion ni decisiones finales de uso.
- No sustituye las pruebas unitarias internas de cada motor productor; prueba la integracion entre objetos ya emitidos.
- No decide conformidad arquitectonica global del motor implementado; esa responsabilidad pertenece al Evaluation / Conformance Engine.
- No crea nuevos motores, nuevas taxonomias, nuevos contratos de fase ni nuevas reglas de versionado.
- No ejecuta recaptura, rebuild, normalizacion, identity resolution, scoring, reporting ni propagacion de re-evaluacion.

## why_it_exists
Los motores productores pueden cumplir su contrato individual y aun asi fallar cuando sus outputs se combinan con datasets, handoffs y objetos de otros motores. Este motor existe como harness transversal separado porque prueba el sistema integrado sin invadir la responsabilidad de producir, modificar o aprobar los artefactos bajo prueba.
