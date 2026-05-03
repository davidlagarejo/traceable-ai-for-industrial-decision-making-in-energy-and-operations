# Technical Schema — Canonical Normalization Engine

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
NormalizedRecord: objeto de salida principal de la etapa `schema_technical` para `motor_005`. Representa la forma canónica mínima derivada de exactamente un `parsed_record`, conserva el `record_id` original, registra la versión de taxonomía usada y separa campos normalizados de campos no mapeados. Vive como artefacto derivado del procesamiento de normalización y no sustituye al registro fuente.

NormalizationRule: representación técnica de una regla determinista tomada de la `canonical_taxonomy` entregada por `motor_003`. Describe qué patrón de campo o alias puede mapearse a un campo canónico, qué conversión está permitida y bajo qué versión de taxonomía opera. Vive como referencia auditada dentro del log de reglas; este motor no crea ni aprueba reglas nuevas.

FieldMapping: traza técnica por campo que enlaza un campo del `parsed_record` con un campo canónico, el valor original, el valor normalizado cuando existe, la regla usada y el estado de mapeo. Vive en `field_mapping_trace` y permite reconstruir cada decisión de normalización sin mutar el input.

## fields
NormalizedRecord:
- `record_id`: string (required) — identificador estable heredado de `parsed_record.record_id`.
- `source_id`: string (required) — referencia a la fuente original recibida desde `parsed_record`.
- `taxonomy_id`: string (required) — identificador de la taxonomía canónica usada para la normalización.
- `taxonomy_version`: string (required) — versión exacta de la taxonomía usada para producir el registro.
- `normalized_fields`: object<string, any> (required) — campos canónicos emitidos; cada key debe existir en `canonical_taxonomy`.
- `unmapped_fields`: array<object> (required) — campos de entrada sin mapeo canónico, preservados con nombre original, valor original y causa.
- `normalization_trace_ref`: string (required) — referencia estable al conjunto de `FieldMapping` que explica el registro.
- `normalization_rule_log_ref`: string (required) — referencia estable al log de reglas evaluadas y aplicadas para este registro.
- `version_id`: string (required) — versión del artefacto normalizado emitido por `motor_005`.
- `created_at`: string<ISO8601> (required) — momento de creación del artefacto derivado.
- `updated_at`: string<ISO8601> (required) — momento de última actualización material del artefacto derivado.
- `version_hash`: string (required) — hash determinista calculado sobre input relevante, versión de taxonomía y campos emitidos.
- `source_ref`: string (required) — referencia reconstruible al `parsed_record` de origen.
- `produced_by_motor`: string (required) — valor fijo `motor_005`.
- `produced_at`: string<ISO8601> (required) — momento en que `motor_005` produjo el objeto.
- `parent_id`: string (required) — identificador del artefacto padre; para esta entidad corresponde a `parsed_record.record_id`.

NormalizationRule:
- `rule_id`: string (required) — identificador estable de la regla declarada en `canonical_taxonomy`.
- `taxonomy_id`: string (required) — identificador de la taxonomía propietaria de la regla.
- `taxonomy_version`: string (required) — versión exacta de la taxonomía donde la regla está vigente.
- `source_pattern`: string (required) — nombre de campo, alias o patrón determinista aceptado como entrada.
- `canonical_field`: string (required) — campo canónico objetivo declarado por la taxonomía.
- `normalization_type`: string (required) — tipo de transformación permitida, por ejemplo passthrough, alias_map, date_format, numeric_cast o enum_map.
- `allowed_value_type`: string (required) — tipo canónico esperado para el valor normalizado.
- `rule_priority`: integer (required) — prioridad determinista usada para ordenar reglas cuando varias son candidatas.
- `conflict_policy`: string (required) — acción estructurada ante reglas incompatibles; valores permitidos: `reject_field`, `prefer_exact_alias`, `prefer_higher_priority`.
- `version_id`: string (required) — versión local de la referencia de regla dentro del run de normalización.
- `created_at`: string<ISO8601> (required) — momento en que la referencia fue registrada para el run.
- `updated_at`: string<ISO8601> (required) — momento de última actualización material de la referencia dentro del artefacto.
- `version_hash`: string (required) — hash determinista del contenido de la regla y su versión de taxonomía.
- `source_ref`: string (required) — referencia a la regla dentro de `canonical_taxonomy`.
- `produced_by_motor`: string (required) — valor fijo `motor_005` como productor de la referencia auditada, no de la regla normativa.
- `produced_at`: string<ISO8601> (required) — momento en que la referencia fue incluida en el output.
- `parent_id`: string (required) — identificador de la taxonomía o regla fuente; normalmente `taxonomy_id:rule_id`.

FieldMapping:
- `mapping_id`: string (required) — identificador estable de la traza de campo dentro del registro normalizado.
- `record_id`: string (required) — identificador del `parsed_record` y del `NormalizedRecord` asociado.
- `source_field`: string (required) — nombre del campo recibido desde `parsed_record`.
- `canonical_field`: string or null (required) — campo canónico objetivo; null cuando el campo queda `unmapped` o falla conversión.
- `original_value`: any (required) — valor original preservado sin mutación.
- `normalized_value`: any or null (required) — valor normalizado emitido; null si no hay mapeo o conversión válida.
- `mapping_status`: string (required) — estado determinista del mapeo; valores permitidos: `mapped`, `unmapped`, `conversion_failed`, `rule_conflict`.
- `rule_id`: string or null (required) — regla aplicada; null solo cuando no hay regla aplicable.
- `taxonomy_version`: string (required) — versión de taxonomía evaluada para el campo.
- `provenance_ref`: string (required) — provenance del campo o del registro fuente.
- `error_code`: string or null (required) — código estructurado para estados no exitosos, por ejemplo `NO_CANONICAL_MAPPING`, `CONVERSION_FAILED` o `RULE_CONFLICT`.
- `version_id`: string (required) — versión de la traza de mapeo.
- `created_at`: string<ISO8601> (required) — momento de creación de la traza.
- `updated_at`: string<ISO8601> (required) — momento de última actualización material de la traza.
- `version_hash`: string (required) — hash determinista de campo fuente, valor original, regla, valor normalizado y estado.
- `source_ref`: string (required) — referencia al campo de origen dentro de `parsed_record`.
- `produced_by_motor`: string (required) — valor fijo `motor_005`.
- `produced_at`: string<ISO8601> (required) — momento en que la traza fue emitida.
- `parent_id`: string (required) — identificador del registro padre; corresponde a `record_id`.

## relationships
- `NormalizedRecord.record_id` references `parsed_record.record_id` from `motor_004`; cardinalidad uno a uno por run de normalización.
- `NormalizedRecord.taxonomy_id` and `NormalizedRecord.taxonomy_version` reference `canonical_taxonomy.taxonomy_id` and `canonical_taxonomy.taxonomy_version` from `motor_003`.
- `NormalizedRecord.normalization_trace_ref` references the collection of `FieldMapping.mapping_id` values emitted for the same `record_id`.
- `NormalizedRecord.normalization_rule_log_ref` references the collection of `NormalizationRule.rule_id` values evaluated or applied for the same run.
- `FieldMapping.record_id` references `NormalizedRecord.record_id`; cardinalidad muchos a uno.
- `FieldMapping.rule_id` references `NormalizationRule.rule_id` when `mapping_status="mapped"` or `mapping_status="conversion_failed"`; it is null only for fields with no applicable canonical rule.
- `FieldMapping.source_ref` references the source field path inside `parsed_record.parsed_fields`.
- `NormalizationRule.taxonomy_id` and `NormalizationRule.taxonomy_version` reference the immutable taxonomy version supplied as input.
- `NormalizationRule.parent_id` references the canonical taxonomy rule source, not an object authored by `motor_005`.
- No relationship in this schema represents identity equivalence, duplicate detection, quality scoring, confidence scoring or record merging.

## identifiers
- NormalizedRecord stable identifier: `record_id`. It is inherited from `parsed_record` and remains unchanged so downstream motors can join normalization output back to ingestion output without identity inference.
- NormalizationRule stable identifier: `rule_id` scoped by `taxonomy_id` and `taxonomy_version`. The composite identity is `taxonomy_id:taxonomy_version:rule_id` because the same rule id can only be interpreted under its taxonomy version.
- FieldMapping stable identifier: `mapping_id`. Recommended deterministic construction is `motor_005:{record_id}:{source_field}:{taxonomy_version}:{rule_id_or_unmapped}` after canonical serialization of the source field path.
- Cross-object run identity: `version_id` plus `version_hash` identifies a specific emitted version of any entity.
- Parent identity: `parent_id` always points to the immediate source object: `parsed_record.record_id` for `NormalizedRecord` and `FieldMapping`, and `taxonomy_id:rule_id` for `NormalizationRule`.

## versioning
All three entities carry the same required versioning envelope:
- `version_id`: string (required) — stable version label for the emitted artifact instance. It changes when normalized output, mapping trace, rule reference or lineage metadata changes.
- `created_at`: string<ISO8601> (required) — timestamp assigned when the artifact instance is first emitted.
- `updated_at`: string<ISO8601> (required) — timestamp assigned when the artifact instance is materially updated or regenerated.
- `version_hash`: string (required) — deterministic hash over canonical JSON serialization of required business fields, required lineage fields and the relevant input references.

Versioning rules:
- The same `parsed_record`, the same `canonical_taxonomy` and the same deterministic engine version must produce the same `version_hash`.
- A change in `taxonomy_version`, applied `rule_id`, `normalized_value`, `mapping_status`, `provenance_ref` or `source_ref` requires a new `version_hash`.
- Versioning does not authorize mutation of `parsed_record` or `canonical_taxonomy`; all objects emitted by this motor are derived artifacts.

## lineage
All three entities carry the same required lineage envelope:
- `source_ref`: string (required) — reconstructible pointer to the source object used for this emitted entity.
- `produced_by_motor`: string (required) — fixed value `motor_005`.
- `produced_at`: string<ISO8601> (required) — timestamp of emission by the normalization run.
- `parent_id`: string (required) — immediate parent artifact identifier used for rebuild and audit.

Entity-specific lineage:
- `NormalizedRecord.source_ref` points to the full `parsed_record`; `NormalizedRecord.parent_id` is `parsed_record.record_id`.
- `NormalizationRule.source_ref` points to the rule definition inside `canonical_taxonomy`; `NormalizationRule.parent_id` is `taxonomy_id:rule_id`.
- `FieldMapping.source_ref` points to the exact field path inside `parsed_record.parsed_fields`; `FieldMapping.parent_id` is the associated `record_id`.

Lineage constraints:
- A `NormalizedRecord` is invalid if any normalized field lacks a corresponding `FieldMapping`.
- A `FieldMapping` is invalid if it omits `original_value` or `provenance_ref`.
- A `NormalizationRule` reference is invalid if it lacks `rule_id`, `taxonomy_version` or a source pointer into `canonical_taxonomy`.
- Lineage must preserve original values and applied rules; it must not encode identity resolution, quality assessment or downstream analytic interpretation.
