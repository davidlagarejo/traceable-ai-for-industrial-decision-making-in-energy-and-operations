# Acceptance Tests — Quality / Fitness Evaluation Engine

Motor ID: motor_007

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Evaluar calidad estructural, completitud, trazabilidad y aptitud de uso por fase u objeto.
why_it_exists:  Evita que objetos defectuosos o no aptos contaminen fases posteriores.
key_inputs:     identity_resolved_records, phase_contracts (motor_001)
key_outputs:    quality_record, fitness_score, quality_flags, disqualification_reason
key_objects:    QualityRecord, FitnessScore, QualityFlag
what_not_to_do: No modifica registros. No normaliza. Solo evalúa y emite señales de calidad.
design_notes:   Motor evaluador, no transformador. Depende de motor_006.

All placeholder markers have been replaced with concrete documentation.
-->

## happy_path
Input: un `identity_resolved_record` con `record_id = "idr_123"`, `identity_status = "resolved"`, `provenance.source_id = "src_01"`, `lineage.parent_record_id = "norm_123"`, `version = "1.0.0"` y todos los campos requeridos por `phase_contract.contract_id = "phase_1_facility_prior_v2"`. Action: el motor compara el registro contra el contrato, verifica metadatos criticos, calcula dimension scores y genera el resultado. Expected output: un `quality_record` con `subject_ref = "idr_123"`, `phase_contract_ref = "phase_1_facility_prior_v2"`, `evaluation_status = "pass"`, `fitness_score.total_score >= 0.90`, `quality_flags = []` y `disqualification_reason = null`.

## edge_cases
- Empty but valid batch: `identity_resolved_records = []` con contratos validos disponibles. Correct behavior: retorna una coleccion vacia de `quality_record`, registra conteo evaluado en cero y no emite error porque no hay objeto invalido.
- Ambiguous identity record: registro con `identity_status = "ambiguous"` pero provenance y lineage completos. Correct behavior: emite `quality_record` con `evaluation_status = "conditional_pass"` o `disqualified` segun umbral contractual, incluye `quality_flag.code = "ambiguous_identity"` y no intenta resolver la ambiguedad.
- Complete record below phase threshold: registro con campos obligatorios presentes pero `dimension_scores.traceability = 0.60` frente a umbral `0.80`. Correct behavior: emite `evaluation_status = "disqualified"`, `quality_flag.severity = "blocking"` y `disqualification_reason.code = "traceability_below_threshold"`.
- Extra fields in input: registro contiene campos no requeridos por el contrato. Correct behavior: ignora los campos extra para scoring salvo que violen limites del contrato, conserva solo referencias en el `quality_record` y no modifica el registro original.

## rejection_criteria
- Missing subject identifier: si un registro no contiene `record_id` ni referencia estable equivalente, el motor rechaza ese item con error `QUALITY_INPUT_MISSING_SUBJECT_REF` y no emite `quality_record` para ese item.
- Missing phase contract: si no existe contrato aplicable o el contrato carece de `contract_id`, `contract_version`, `required_fields` o `fitness_thresholds`, el motor rechaza la evaluacion con error `QUALITY_CONTRACT_INVALID`.
- Malformed input collection: si `identity_resolved_records` no es una lista, el motor rechaza el lote con error `QUALITY_INPUT_NOT_LIST`.
- Missing critical metadata: si un registro no contiene provenance y lineage minimos, el motor no puede emitir `pass`; si el contrato exige bloqueo por esa ausencia, retorna `disqualified` con `disqualification_reason.code = "critical_traceability_missing"`.
