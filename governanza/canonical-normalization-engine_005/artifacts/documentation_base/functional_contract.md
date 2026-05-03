# Functional Contract — Canonical Normalization Engine

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

## inputs
parsed_record: object — output de `motor_004`; contiene `record_id`, `source_id`, `parsed_fields`, `provenance_ref`, `parser_version` y metadatos de extracción.
canonical_taxonomy: object — output de `motor_003`; contiene `taxonomy_id`, `taxonomy_version`, campos canónicos, alias aceptados, tipos canónicos y reglas deterministas de conversión.

## outputs
normalized_record: object — registro canónico mínimo para consumidores downstream como identidad, versionado, calidad y reporting.
normalization_rule_log: array<object> — bitácora auditable de reglas evaluadas, aplicadas, omitidas o rechazadas durante la normalización.
field_mapping_trace: array<object> — trazas de mapeo entre campo original, campo canónico, valor original, valor normalizado, regla aplicada y provenance.

## limits
- No acepta registros sin `record_id`, sin `parsed_fields` o sin referencia de provenance.
- No acepta taxonomías sin `taxonomy_id`, sin `taxonomy_version` o sin reglas de campos canónicos declaradas.
- No acepta instrucciones de normalización externas a la taxonomía canónica entregada como input.
- No produce decisiones de identidad, clusters, merges, duplicados resueltos ni entidades consolidadas.
- No produce score de calidad, confianza, ranking, fitness, veracidad ni recomendación de uso.
- No produce campos canónicos nuevos que no existan en `canonical_taxonomy`.
- No elimina valores originales; los conserva en la traza incluso cuando no hay normalización posible.

## validations
- Rechaza el procesamiento si `parsed_record.record_id` es nulo, vacio o no es string estable.
- Rechaza el procesamiento si `parsed_record.parsed_fields` no es un objeto o array de campos parseados.
- Rechaza el procesamiento si `parsed_record.provenance_ref` falta, porque no puede emitir trazabilidad reconstruible.
- Rechaza el procesamiento si `canonical_taxonomy.taxonomy_version` falta o si no hay definiciones de campos canónicos.
- Antes de normalizar cada campo, verifica que la regla aplicada provenga de `canonical_taxonomy` y tenga `rule_id`.
- Cada entrada de `field_mapping_trace` incluye `source_field`, `canonical_field` o `null`, `original_value`, `normalized_value` o `null`, `mapping_status`, `rule_id` o `null` y `provenance_ref`.
- Cada `normalized_record` emitido incluye `record_id`, `source_id`, `taxonomy_version`, `normalized_fields`, `unmapped_fields` y `normalization_trace_ref`.
- Si un campo no tiene mapeo canónico, el motor lo marca como `unmapped` y preserva el valor original sin inventar normalización.
