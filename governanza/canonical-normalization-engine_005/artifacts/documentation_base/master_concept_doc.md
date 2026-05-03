# Master Concept Document — Canonical Normalization Engine

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

## purpose
Canonical Normalization Engine convierte cada `parsed_record` heterogéneo en una representación canónica mínima usando la `canonical_taxonomy` vigente. Para cada campo transformado conserva el valor original, el valor normalizado, la regla aplicada y el rastro de mapeo que permite reconstruir la decisión. Su salida no afirma identidad entre registros ni calidad del dato; solo produce una forma estructural común para motores posteriores.

## what_it_does
- Recibe `parsed_record` producido por el motor de ingesta y parsing junto con la `canonical_taxonomy` cerrada por `motor_003`.
- Valida que el registro tenga identificador estable, campos extraidos y metadatos de provenance suficientes para trazabilidad.
- Resuelve cada nombre de campo entrante contra alias, tipos y reglas declaradas en la taxonomía canónica.
- Convierte valores a tipos canónicos cuando existe una regla determinista aplicable.
- Preserva cada valor original junto al valor canónico emitido, sin mutar el registro fuente.
- Emite `normalized_record` con campos canónicos mínimos, campos no mapeados preservados como trazas y metadatos de taxonomía usada.
- Emite `normalization_rule_log` con una entrada por transformación aplicada o rechazada.
- Emite `field_mapping_trace` que enlaza campo de origen, campo canónico, regla, estado de mapeo y provenance.

## what_it_does_not_do
- No resuelve identidad entre registros, entidades, personas, lugares u organizaciones.
- No evalúa calidad, confianza, completitud, fitness, frescura ni veracidad de los datos.
- No corrige valores por inferencia semántica ni rellena campos ausentes con conocimiento externo.
- No modifica la taxonomía canónica ni crea nuevos campos canónicos fuera de `motor_003`.
- No deduplica registros, fusiona objetos ni decide equivalencias entre fuentes.
- No descarta valores originales aunque no pueda producir un valor normalizado.

## why_it_exists
Existe como motor separado porque la heterogeneidad de fuentes debe aislarse antes de identidad, calidad y análisis downstream. Su separación permite que `motor_004` capture y parse datos sin imponer semántica canónica, mientras `motor_005` aplica reglas de normalización trazables derivadas de `motor_003` y preserva tanto el valor original como la regla aplicada.
