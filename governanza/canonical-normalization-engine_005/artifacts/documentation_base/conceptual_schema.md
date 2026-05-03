# Conceptual Schema — Canonical Normalization Engine

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

## entities
NormalizedRecord: representación canónica mínima de un `parsed_record`, con valores normalizados, valores originales preservados y referencia a la taxonomía usada.
NormalizationRule: regla determinista tomada de la `canonical_taxonomy` que declara cómo mapear o convertir un campo específico.
FieldMapping: vínculo auditable entre un campo original parseado, su campo canónico objetivo, la regla usada y el resultado de normalización.

## relationships
NormalizedRecord → FieldMapping (un registro normalizado contiene una o más trazas de campo que explican cómo se obtuvo su forma canónica).
FieldMapping → NormalizationRule (cada mapeo aplicado referencia cero o una regla; cero solo cuando el campo queda `unmapped`).
NormalizationRule → canonical_taxonomy (cada regla pertenece a una versión específica de la taxonomía recibida de `motor_003`).
FieldMapping → parsed_record field (cada mapeo conserva el nombre de campo original, valor original y provenance del campo entrante).
NormalizedRecord → parsed_record (cada registro normalizado deriva de exactamente un registro parseado y conserva su `record_id`).

## key_fields
NormalizedRecord:
- `record_id`: string
- `source_id`: string
- `taxonomy_version`: string
- `normalized_fields`: object
- `unmapped_fields`: array<object>
- `normalization_trace_ref`: string

NormalizationRule:
- `rule_id`: string
- `taxonomy_version`: string
- `source_pattern`: string
- `canonical_field`: string
- `normalization_type`: string
- `allowed_value_type`: string

FieldMapping:
- `mapping_id`: string
- `record_id`: string
- `source_field`: string
- `canonical_field`: string or null
- `original_value`: any
- `normalized_value`: any or null
- `mapping_status`: string
- `rule_id`: string or null
- `provenance_ref`: string
