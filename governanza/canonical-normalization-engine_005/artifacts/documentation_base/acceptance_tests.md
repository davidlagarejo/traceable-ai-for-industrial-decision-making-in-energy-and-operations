# Acceptance Tests — Canonical Normalization Engine

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

## happy_path
Input: `parsed_record` con `record_id="rec-001"`, `source_id="src-a"`, `provenance_ref="prov-777"` y campos `{"DOB": "1984/03/09", "country": "United States", "employee_count": "42"}`. La `canonical_taxonomy` version `tax-2026-04` declara alias `DOB -> birth_date`, conversión de fecha `YYYY/MM/DD -> ISO_DATE`, alias `country -> country_name` y conversión de `employee_count` a integer.

Action: el motor evalúa cada campo contra la taxonomía, aplica reglas deterministas y construye salidas derivadas.

Expected output: `normalized_record.record_id="rec-001"`, `taxonomy_version="tax-2026-04"`, `normalized_fields.birth_date="1984-03-09"`, `normalized_fields.country_name="United States"` y `normalized_fields.employee_count=42`. `field_mapping_trace` contiene tres entradas con valor original, valor normalizado, `rule_id`, `mapping_status="mapped"` y `provenance_ref="prov-777"`. `normalization_rule_log` registra las tres reglas aplicadas sin score de calidad ni decisión de identidad.

## edge_cases
- Campo desconocido: si `parsed_record.parsed_fields` contiene `{"legacy_code": "A-19"}` y la taxonomía no define alias ni campo canónico para `legacy_code`, el motor emite una traza con `mapping_status="unmapped"`, conserva `original_value="A-19"` y no crea `normalized_fields.legacy_code`.
- Valor ya canónico: si el input trae `{"birth_date": "1984-03-09"}` y la taxonomía declara `birth_date` como campo canónico ISO_DATE, el motor conserva el mismo valor normalizado, registra la regla de passthrough y mantiene el valor original en la traza.
- Valor no convertible por regla existente: si `employee_count="forty two"` y la regla exige integer determinista, el motor registra ese campo con `mapping_status="conversion_failed"`, conserva el original y no emite valor normalizado para `employee_count`.

## rejection_criteria
- Rechaza el registro completo con error `MISSING_PROVENANCE` si `parsed_record.provenance_ref` falta o es nulo.
- Rechaza el registro completo con error `INVALID_TAXONOMY` si `canonical_taxonomy.taxonomy_version` falta o si no contiene definiciones de campos canónicos.
- Rechaza el registro completo con error `INVALID_PARSED_RECORD` si `parsed_record.record_id` falta o `parsed_record.parsed_fields` no es una estructura procesable.
- Rechaza el campo afectado con error `RULE_CONFLICT` si dos reglas vigentes de la misma taxonomía producen campos canónicos incompatibles para el mismo `source_field`.
