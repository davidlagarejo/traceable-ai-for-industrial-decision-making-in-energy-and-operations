# Functional Contract — Quality / Fitness Evaluation Engine

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

## inputs
- identity_resolved_records: list[IdentityRecord-like dict] — source: motor_006 Entity Identity / Resolution Engine; contiene registros con identidad resuelta, estado de ambiguedad, provenance, lineage, version y referencias al objeto original.
- phase_contracts: list[PhaseContract-like dict] — source: motor_001 Phase Contract Registry; contiene definiciones de campos requeridos, limites de fase, outputs permitidos, reglas minimas de handoff y criterios de aptitud por fase u objeto.
- evaluation_context: dict — origin: caller/orchestrator; contiene `evaluation_run_id`, timestamp, fase objetivo y version de reglas de evaluacion usada para producir resultados reconstruibles.

## outputs
- quality_record: dict — destination: downstream motors, audit trail and quality_records registry; documenta una evaluacion concreta con `quality_record_id`, `subject_ref`, `phase_contract_ref`, dimensiones evaluadas, flags, score, resultado y lineage.
- fitness_score: dict — destination: quality_record and downstream gating consumers; expresa puntajes deterministas por dimension y puntaje total normalizado entre 0.0 y 1.0.
- quality_flags: list[dict] — destination: quality_record and downstream consumers; enumera senales como `missing_required_field`, `missing_lineage`, `contract_mismatch`, `restricted_use`, `ambiguous_identity` o `not_fit_for_phase`.
- disqualification_reason: dict|null — destination: quality_record and consumers that must block unsafe handoff; explica la razon estructurada por la que un objeto no es apto para la fase evaluada.

## limits
- No acepta registros sin identificador estable de objeto, referencia de version o provenance minima; esos casos se rechazan antes de scoring.
- No acepta contratos de fase sin identificador, version, lista de campos requeridos y criterios minimos de aptitud.
- No produce registros modificados, normalizados, fusionados ni enriquecidos; el objeto evaluado permanece fuera de escritura por este motor.
- No produce decisiones de identidad, taxonomia, evidencia de campo, claims analiticos ni reportes finales.
- No emite `fitness_score` sin un `quality_record` asociado y trazable al contrato usado.
- No convierte advertencias en correcciones silenciosas; cada defecto queda como flag o razon de descalificacion.

## validations
- Rechaza el lote si `identity_resolved_records` no es una lista o si algun item carece de `record_id` o `identity_status`.
- Rechaza un item evaluable si no puede enlazarse a un `phase_contract` vigente mediante fase, tipo de objeto o contrato declarado.
- Rechaza el contrato si faltan `contract_id`, `contract_version`, `required_fields` o `fitness_thresholds`.
- Antes de calcular score, verifica presencia de identificador estable, provenance, lineage, version y referencias al productor del registro.
- Antes de emitir output, asegura que `quality_record_id`, `subject_ref`, `phase_contract_ref`, `fitness_score`, `quality_flags`, `evaluation_status` y `evaluation_run_id` no esten vacios.
- Cuando el puntaje total queda por debajo del umbral contractual, emite `evaluation_status = disqualified` y un `disqualification_reason` no nulo.
- Cuando existen defectos no bloqueantes, emite `evaluation_status = conditional_pass` y al menos un `quality_flag` con severidad `warning`.
- Todo output conserva enlaces a input, contrato, version de reglas y timestamp para permitir reconstruccion y auditoria.
