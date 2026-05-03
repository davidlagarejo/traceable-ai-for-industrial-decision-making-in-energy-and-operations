# Master Concept Document — Quality / Fitness Evaluation Engine

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

## purpose
El Quality / Fitness Evaluation Engine evalua registros ya resueltos por identidad contra contratos de fase vigentes para determinar si son estructuralmente completos, trazables y aptos para uso posterior. Su trabajo consiste en emitir una evaluacion determinista de calidad por objeto o fase, expresada como `quality_record`, `fitness_score`, `quality_flags` y, cuando corresponda, `disqualification_reason`. El motor no corrige ni transforma los registros evaluados; solo produce senales de calidad consumibles por etapas downstream.

## what_it_does
- Recibe `identity_resolved_records` provenientes de motor_006 con identificadores, provenance, lineage y estado de resolucion.
- Recibe `phase_contracts` de motor_001 para conocer los campos obligatorios, limites de fase, outputs permitidos y criterios minimos de aptitud.
- Verifica completitud estructural comparando cada registro contra los campos requeridos por su contrato de fase.
- Verifica trazabilidad confirmando que cada registro evaluado conserva referencias de origen, version, lineage y motor productor.
- Calcula un `fitness_score` determinista a partir de dimensiones explicitas: completitud, trazabilidad, consistencia contractual y aptitud de uso.
- Emite `quality_flags` que identifican defectos, advertencias o condiciones de uso restringido sin modificar el registro original.
- Emite `disqualification_reason` cuando un registro no puede pasar a fases posteriores bajo el contrato aplicable.
- Registra un `quality_record` por evaluacion, enlazado al objeto evaluado y al contrato usado.

## what_it_does_not_do
- No modifica, corrige, normaliza, fusiona ni reescribe `identity_resolved_records`.
- No ejecuta normalizacion canonica; esa responsabilidad pertenece al Canonical Normalization Engine.
- No resuelve identidad ni decide merges entre entidades; esa responsabilidad pertenece a motor_006.
- No redefine contratos de fase, criterios de handoff ni outputs permitidos; los consume desde motor_001.
- No decide verdad epistemologica final ni valida evidencia de campo; solo evalua calidad estructural y aptitud operativa.
- No bloquea o habilita fases por autoridad propia fuera de las senales documentadas que emite.

## why_it_exists
Existe como motor separado porque la calidad y aptitud de uso son una evaluacion transversal distinta de capturar, normalizar, resolver identidad o versionar objetos. Al depender de motor_006, puede evaluar registros ya estabilizados por identidad sin contaminar esa responsabilidad con reglas de scoring o fitness. Su separacion evita que objetos defectuosos avancen en silencio y permite que motores posteriores consuman senales de calidad uniformes sin reinterpretar cada registro.
