# Conceptual Schema — Quality / Fitness Evaluation Engine

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

## entities
- QualityRecord: registro trazable de una evaluacion de calidad aplicada a un objeto o fase especifica.
- FitnessScore: estructura de puntajes deterministas que resume completitud, trazabilidad, consistencia contractual y aptitud de uso.
- QualityFlag: senal estructurada de defecto, advertencia o restriccion detectada durante la evaluacion.
- DisqualificationReason: explicacion estructurada y obligatoria cuando un objeto no alcanza los criterios minimos de aptitud.

## relationships
- QualityRecord -> identity_resolved_record (un QualityRecord evalua exactamente un registro sujeto mediante `subject_ref`).
- QualityRecord -> phase_contract (un QualityRecord se calcula contra exactamente un contrato vigente mediante `phase_contract_ref`).
- QualityRecord -> FitnessScore (un QualityRecord contiene exactamente un FitnessScore calculado para esa evaluacion).
- QualityRecord -> QualityFlag (un QualityRecord contiene cero o muchas QualityFlag segun los defectos o advertencias detectados).
- QualityRecord -> DisqualificationReason (un QualityRecord contiene cero o una DisqualificationReason; es obligatoria cuando `evaluation_status = disqualified`).
- FitnessScore -> QualityFlag (puntajes bajo umbral generan QualityFlag con dimension, severidad y razon asociadas).

## key_fields
QualityRecord:
- quality_record_id: string
- subject_ref: string
- phase_contract_ref: string
- evaluation_status: enum[pass, conditional_pass, disqualified, rejected]
- fitness_score: FitnessScore
- quality_flags: list[QualityFlag]
- evaluation_run_id: string
- evaluated_at: datetime

FitnessScore:
- score_id: string
- total_score: float
- dimension_scores: dict[string, float]
- threshold_applied: float
- scoring_rule_version: string

QualityFlag:
- flag_id: string
- code: enum[missing_required_field, missing_lineage, missing_provenance, contract_mismatch, restricted_use, ambiguous_identity, not_fit_for_phase]
- severity: enum[info, warning, blocking]
- dimension: enum[completeness, traceability, contract_consistency, fitness]
- message: string
- affected_field: string|null

DisqualificationReason:
- reason_id: string
- code: string
- severity: enum[blocking]
- threshold_failed: string
- explanation: string
- supporting_flags: list[string]
