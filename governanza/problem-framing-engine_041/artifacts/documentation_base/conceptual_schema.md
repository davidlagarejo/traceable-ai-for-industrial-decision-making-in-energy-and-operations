# Conceptual Schema — Problem Framing Engine

Motor ID: motor_041

## entities
- `ProblemFramingRecord`
- `ProblemFramingRegister`
- `InvalidFrameTranslation`
- `EvidenceNeedEnvelope`

## relationships
- sistema + variables dominantes + conflictos cross-layer -> `ProblemFramingRegister`
- invalid frame + congruencia cross-layer -> `InvalidFrameTranslation`
- `InvalidFrameTranslation` puede reemplazar al framing estructural cuando éste sea inadmisible o demasiado hueco
- cada `ProblemFramingRecord` arrastra un `EvidenceNeedEnvelope` que marca qué habría que probar antes de strategy o CAPEX

## key_fields
- `ProblemFramingRecord`: `stated_problem`, `reframed_problem`, `why_original_framing_may_be_wrong`, `evidence_needed`, `strategic_risk`, `evidence_state`, `linked_layers`
- `ProblemFramingRegister`: lista de `ProblemFramingRecord` y count plano
- `InvalidFrameTranslation`: `apparent_problem`, `what_problem_should_be_tested_instead`, `why_invalid_or_premature`, `evidence_needed`, `layers`
- `EvidenceNeedEnvelope`: lista de pruebas mínimas requeridas para distinguir framing prematuro de framing válido

## invariants
- el motor siempre preserva trazabilidad desde el framing viejo al framing corregido;
- `reframed_problem` debe ser investigable, no retórico;
- `evidence_state` no puede subir por encima de la calidad del conflicto o del invalid frame subyacente;
- `linked_layers` no es decorativo: sirve para evitar que downstream lea el problema como una sola dimensión;
- el registro debe poder quedarse en una sola fila útil cuando el caso sólo permite una reformulación dominante.
