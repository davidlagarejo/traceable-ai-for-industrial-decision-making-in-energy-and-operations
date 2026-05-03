# Design Done Criteria — Quality / Fitness Evaluation Engine

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

## criteria
- `master_concept_doc.md` define proposito, acciones, limites y justificacion sin marcadores abiertos.
- `functional_contract.md` lista inputs, outputs, limites y validaciones con nombres de objetos y fuentes trazables.
- `conceptual_schema.md` define `QualityRecord`, `FitnessScore`, `QualityFlag` y `DisqualificationReason` con relaciones y campos minimos.
- `operational_rules.md` prohibe explicitamente modificar, normalizar o resolver identidad y define reglas verificables de scoring.
- `acceptance_tests.md` cubre happy path, batch vacio, identidad ambigua, score bajo umbral y rechazos estructurados.
- `failure_modes.md` identifica degradaciones de contrato, metadata, scoring, responsabilidad y reconstruccion.
- Cada output conceptual puede enlazarse a `identity_resolved_records`, `phase_contracts`, version de reglas y `evaluation_run_id`.
- La documentacion base deja al motor listo para derivar schema tecnico sin inventar nuevas responsabilidades.
