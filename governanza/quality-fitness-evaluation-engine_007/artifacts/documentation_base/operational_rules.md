# Operational Rules — Quality / Fitness Evaluation Engine

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

## rules
1. Cada evaluacion debe referenciar exactamente un registro de entrada y exactamente un contrato de fase vigente.
2. El motor debe calcular puntajes de forma determinista usando solo campos del registro, contrato aplicable y version declarada de reglas de scoring.
3. Todo defecto de completitud, trazabilidad, consistencia contractual o aptitud debe quedar expresado como `quality_flag` o como `disqualification_reason`.
4. Un registro con provenance o lineage ausente no puede recibir `evaluation_status = pass`.
5. Un registro cuyo `total_score` sea menor que el umbral contractual debe recibir `evaluation_status = disqualified`.
6. Un registro con defectos no bloqueantes y score suficiente debe recibir `evaluation_status = conditional_pass`, no `pass`.
7. Todo `quality_record` emitido debe ser reconstruible desde `subject_ref`, `phase_contract_ref`, `evaluation_run_id` y `scoring_rule_version`.
8. El motor debe preservar el orden y contenido de los registros evaluados como referencias externas; no puede mutarlos internamente ni devolverlos alterados.

## invariants
- Los registros de entrada son de solo lectura durante toda la operacion.
- Ningun output existe sin referencia al objeto evaluado y al contrato usado.
- `fitness_score.total_score` siempre esta en el rango cerrado de 0.0 a 1.0.
- `quality_flags` siempre es una lista, incluso cuando esta vacia.
- `disqualification_reason` es nulo salvo cuando `evaluation_status = disqualified`; en ese caso es obligatorio.
- La version de reglas de scoring queda registrada en cada `FitnessScore`.
- Provenance, lineage y version se evalucan como metadatos criticos y nunca se sustituyen por valores inferidos por este motor.

## forbidden_operations
- Modificar, normalizar, enriquecer, fusionar o eliminar registros de entrada.
- Resolver identidad, cerrar ambiguedades de identidad o crear entity clusters.
- Crear, editar o aprobar contratos de fase.
- Crear taxonomias, aliases canonicos o reglas semanticas.
- Producir claims analiticos, inferencias, reportes finales o evidencia de campo.
- Elevar un objeto descalificado a apto por excepcion no registrada.
- Ocultar defectos corrigiendolos dentro del output.
- Usar IA o heuristicas no declaradas como fuente soberana de scoring.
