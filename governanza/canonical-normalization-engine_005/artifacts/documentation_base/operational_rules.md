# Operational Rules — Canonical Normalization Engine

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

## rules
1. El motor solo normaliza usando reglas presentes en la `canonical_taxonomy` recibida como input.
2. Cada valor normalizado debe conservar el valor original correspondiente en `field_mapping_trace`.
3. Cada transformación aplicada debe registrar `rule_id`, `taxonomy_version`, `source_field`, `canonical_field` y `provenance_ref`.
4. Si un campo de entrada no coincide con una regla canónica, el motor debe marcarlo como `unmapped` y no debe inventar un campo canónico.
5. Si dos reglas de la misma taxonomía reclaman el mismo campo de origen con resultados incompatibles, el motor debe rechazar ese campo con estado `rule_conflict` y no emitir valor normalizado para ese campo.
6. La salida debe ser determinista: el mismo `parsed_record` y la misma `canonical_taxonomy` producen el mismo `normalized_record`, `normalization_rule_log` y `field_mapping_trace`.
7. El motor no debe mutar `parsed_record` ni `canonical_taxonomy`; todas las salidas se producen como artefactos derivados.

## invariants
- `record_id` permanece igual entre `parsed_record`, `normalized_record`, `normalization_rule_log` y `field_mapping_trace`.
- `taxonomy_version` usada para normalizar queda registrada en cada salida emitida.
- Ningun valor original se pierde, sobrescribe o reemplaza por el valor normalizado.
- Cada campo normalizado tiene una traza de mapeo reconstruible.
- Cada campo no mapeado queda representado en `unmapped_fields` o en `field_mapping_trace` con estado `unmapped`.
- La normalización no cambia provenance, source identity ni version metadata recibidos.

## forbidden_operations
- Resolver identidad entre registros o declarar que dos registros representan la misma entidad.
- Evaluar calidad, confianza, exactitud, completitud, fitness o veracidad de un dato.
- Crear, renombrar o aprobar campos nuevos dentro de la taxonomía canónica.
- Fusionar registros, deduplicar entradas o consolidar entidades.
- Eliminar valores originales porque ya existe una forma normalizada.
- Corregir valores mediante inferencia probabilística, consulta externa o conocimiento no declarado en la taxonomía.
- Emitir outputs sintéticos, predicciones o recomendaciones analíticas.
