# Acceptance Tests — Dataset / Object Test Harness Engine

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

## happy_path
Input: `phase_contracts` contiene `contract_id = PC-001-normalized-handoff`, `phase_id = normalization`, `required_outputs = [normalized_record]`, `field_requirements = [record_id, dataset_id, taxonomy_refs, version_ref, lineage_refs]` y `status = approved`; `version_records` contiene `version_id = VR-002-NR-884-v1`, `object_id = NR-884`, `object_type = normalized_record`, `object_version = 1`, `lineage_refs = [LN-SRC-12, LN-NORM-884]`; `canonical_taxonomy` contiene `taxonomy_id = TAX-003-main`, `taxonomy_version = 2026.04`, `allowed_terms = [sector.energy, geography.us.tx]`; `normalized_records` contiene `record_id = NR-884`, `dataset_id = DS-55`, `taxonomy_refs = [sector.energy, geography.us.tx]`, `version_ref = VR-002-NR-884-v1`, `lineage_refs = [LN-SRC-12, LN-NORM-884]`; `identity_records` contiene `identity_id = ID-006-ENT-17`, `entity_ref = supplier:acme-grid`, `canonical_entity_id = ENT-17`, `version_ref = VR-002-ID-17-v2`; `quality_records` contiene `quality_record_id = QR-007-NR-884`, `subject_ref = NR-884`, `phase_contract_ref = PC-001-normalized-handoff`, `evaluation_status = pass`.

Action: el motor ejecuta los casos `contract_required_fields_present`, `version_ref_resolves`, `taxonomy_refs_allowed`, `identity_ref_resolves` y `quality_record_present` sobre el lote, usando los contratos y snapshots recibidos como autoridad.

Expected output: emite cinco `TestResult` con `status = pass`, `input_refs` completos, `failure_ids = []` y `severity = info`; emite un `HarnessReport` con `status = pass`, `result_counts.pass = 5`, `result_counts.fail = 0`, `tested_contract_refs = [PC-001-normalized-handoff]`, `tested_object_refs` incluyendo `NR-884`; emite `integration_failure_log = []`.

## edge_cases
- Lote valido sin records normalizados: si contratos, taxonomia, versiones, identidades y quality records estan presentes pero `normalized_records = []`, el motor no debe inventar objetos; emite `TestResult.status = skipped` para casos que requieren normalized record, conserva `input_refs` de autoridad y marca `HarnessReport.status = warning` si la cobertura minima esperada no se cumple.
- Taxonomia vigente con terminos no usados: si `canonical_taxonomy.allowed_terms` contiene cientos de terminos pero el lote usa solo dos, el motor valida solo las referencias observadas y registra cobertura parcial sin fallar por terminos no usados.
- Quality record condicional: si `quality_records` contiene `evaluation_status = conditional_pass` para un objeto requerido, el motor puede emitir `TestResult.status = warning` con `IntegrationFailure.failure_type = quality_missing` solo cuando el contrato exige `pass` estricto; si el contrato permite condicional, el resultado debe ser `pass`.
- Duplicados de referencia de version: si dos normalized records apuntan a la misma `version_ref` pero tienen `record_id` distintos y lineage compatible, el motor no falla por duplicidad; registra ambos en `tested_object_refs` y solo falla si el contrato exige version unica por objeto.

## rejection_criteria
- Rechaza con `INVALID_HARNESS_INPUT` cuando `phase_contracts`, `version_records`, `canonical_taxonomy`, `normalized_records`, `identity_records` o `quality_records` no son objetos o colecciones estructuradas.
- Rechaza con `INVALID_HARNESS_INPUT` cuando un `phase_contract` carece de `contract_id`, `phase_id`, `required_outputs`, `field_requirements`, version o estado aprobado para prueba.
- Rechaza con `UNRESOLVED_REFERENCE` cuando un `normalized_record.version_ref = VR-unknown` no existe en `version_records`.
- Rechaza con `TAXONOMY_MISMATCH` cuando un record usa `taxonomy_refs = [sector.unregistered]` y ese termino no existe en `canonical_taxonomy.allowed_terms`.
- Rechaza con `LINEAGE_GAP` cuando un objeto bajo prueba no tiene `lineage_refs` ni `provenance_refs` aunque el contrato los exige.
- Rechaza con `UNSAFE_HARNESS_REPORT` si un reporte agregado se iba a emitir con conteos que no coinciden con la lista real de `TestResult`.
