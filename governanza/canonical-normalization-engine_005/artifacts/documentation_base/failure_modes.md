# Failure Modes — Canonical Normalization Engine

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

## failure_modes_list
MISSING_PROVENANCE: el motor recibe registros parseados sin `provenance_ref` y no puede reconstruir de dónde salió un valor normalizado.
TAXONOMY_DRIFT: la taxonomía usada para normalizar no coincide con la versión registrada en salidas previas, produciendo resultados no comparables entre ejecuciones.
RULE_CONFLICT: dos reglas vigentes mapean el mismo campo de origen a campos canónicos incompatibles o aplican conversiones contradictorias.
LOSSY_NORMALIZATION: una transformación reemplaza el valor original sin preservarlo en `field_mapping_trace`.
SILENT_UNMAPPED_DROP: campos sin mapeo desaparecen de la salida en lugar de quedar registrados como `unmapped`.

## anti_patterns
- Usar este motor para deduplicar, fusionar entidades o decidir identidad entre registros.
- Agregar reglas ad hoc en código para casos de fuente sin incorporarlas antes a la taxonomía canónica.
- Tratar `normalized_record` como dato de mayor calidad o mayor verdad que el registro original.
- Eliminar `field_mapping_trace` para reducir tamaño de salida, rompiendo reconstruibilidad.

## degradation_signals
- Aumento sostenido de campos con `mapping_status="unmapped"` para fuentes que antes normalizaban correctamente.
- Entradas de `normalization_rule_log` sin `rule_id` o sin `taxonomy_version`.
- Diferencias de salida para el mismo par `parsed_record` + `canonical_taxonomy` entre ejecuciones repetidas.
- Descenso abrupto del número de `field_mapping_trace` por registro mientras el volumen de campos parseados permanece estable.
- Aparición de campos normalizados que no existen en la `canonical_taxonomy` registrada.
