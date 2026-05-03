# Failure Modes — Quality / Fitness Evaluation Engine

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

## failure_modes_list
- CONTRACT_DRIFT_UNDETECTED: el motor evalua contra un contrato obsoleto y genera `quality_record` que contradice la version vigente de motor_001.
- SILENT_METADATA_TOLERANCE: registros sin provenance, lineage o version reciben `pass` en lugar de `conditional_pass`, `disqualified` o rechazo estructurado.
- SCORE_INFLATION: el `fitness_score.total_score` queda alto aunque existan flags bloqueantes o dimensiones bajo umbral.
- RESPONSIBILITY_LEAKAGE: el motor empieza a corregir registros, normalizar campos o resolver ambiguedades para poder emitir mejor score.
- NON_RECONSTRUCTIBLE_EVALUATION: un `quality_record` no permite reconstruir sujeto, contrato, version de reglas y run de evaluacion.

## anti_patterns
- Usar el motor como reparador de datos, haciendo que complete campos faltantes o normalice valores antes de puntuar.
- Tratar `fitness_score` como verdad epistemologica final en vez de senal operativa de aptitud estructural.
- Configurar umbrales implicitos fuera del contrato de fase y no registrar version de reglas.
- Mezclar evaluacion de calidad con conformance review del motor o con test harness transversal.

## degradation_signals
- Aumento sostenido de `quality_record` con `evaluation_status = pass` pese a crecimiento de flags warning o blocking.
- Porcentaje de `quality_record` sin `phase_contract_ref`, `scoring_rule_version` o `evaluation_run_id` mayor que cero.
- Divergencia entre version de contrato usada en outputs y version vigente en motor_001.
- Incremento de `conditional_pass` sin crecimiento proporcional de `quality_flags`, senal de scoring opaco o incompleto.
- Aparicion de diffs en registros de entrada despues de la evaluacion, lo que indica mutacion prohibida.
- Repeticion de `disqualification_reason.code = "unknown"` o mensajes genericos que impiden auditoria.
