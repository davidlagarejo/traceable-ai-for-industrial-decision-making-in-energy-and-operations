# Design Done Criteria — Canonical Normalization Engine

Motor ID: motor_005

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir extracción heterogénea en forma canónica mínima preservando valores originales y reglas aplicadas.
why_it_exists:  Desacopla el sistema de la heterogeneidad de fuentes.
key_inputs:     parsed_record, canonical_taxonomy (motor_003)
key_outputs:    normalized_record, normalization_rule_log, field_mapping_trace
key_objects:    NormalizedRecord, NormalizationRule, FieldMapping
what_not_to_do: No resuelve identidad entre registros. No evalúa calidad. Solo transforma a forma canónica.
design_notes:   Preserva el valor original junto al valor normalizado. Depende de motor_004 y motor_003.

Sections below are completed with motor-specific content.
-->

## criteria
- `master_concept_doc.md` define el propósito, acciones, exclusiones y razón de existencia del motor sin mezclar identidad ni calidad.
- `functional_contract.md` lista `parsed_record` y `canonical_taxonomy` como inputs, y `normalized_record`, `normalization_rule_log` y `field_mapping_trace` como outputs.
- `conceptual_schema.md` define `NormalizedRecord`, `NormalizationRule` y `FieldMapping` con campos mínimos y relaciones reconstruibles.
- `operational_rules.md` exige preservación de valor original, uso exclusivo de taxonomía canónica y salida determinista para el mismo input.
- `acceptance_tests.md` cubre happy path, campos desconocidos, valores ya canónicos, fallos de conversión y rechazos estructurados.
- `failure_modes.md` identifica perdida de provenance, drift de taxonomía, conflictos de reglas, normalización con perdida y descarte silencioso de campos.
- Ningun artefacto de `documentation_base` contiene marcadores abiertos como placeholders de trabajo.
