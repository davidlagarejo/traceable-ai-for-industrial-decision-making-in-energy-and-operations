# Master Concept Document — Taxonomy + Canonical Entity Service

Motor ID: motor_003

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Gobernar taxonomías, términos canónicos, aliases y límites semánticos del sistema.
why_it_exists:  Evita drift semántico, dialectos paralelos y joins inestables entre fuentes.
key_inputs:     raw terms, aliases, source vocabularies
key_outputs:    canonical_term, alias_map, taxonomy_tree, boundary_definition
key_objects:    CanonicalEntity, TaxonomyNode, AliasMappings
what_not_to_do: No normaliza datos. No resuelve identidad de registros. Solo gobierna el vocabulario.
design_notes:   Depende de motor_001. Es la referencia semántica que todos los motores downstream consultan.

Sections below are complete for documentation_base gate validation.
-->

## purpose
Este motor gobierna el vocabulario semántico del sistema: taxonomías, términos canónicos, aliases aceptados y límites de significado. Mantiene una referencia determinista para que los motores downstream consulten el mismo término, la misma jerarquía y la misma definición de alcance. Su salida no transforma registros de datos; solo define el vocabulario autorizado y sus fronteras semánticas.

## what_it_does
- Recibe candidatos de términos crudos, aliases declarados y vocabularios fuente con referencia de origen.
- Valida que cada candidato tenga texto, fuente, alcance semántico y compatibilidad con el contrato de fase definido por motor_001.
- Registra `canonical_term` como una entidad canónica con identificador estable, etiqueta autorizada, estado y alcance.
- Construye y mantiene `taxonomy_tree` mediante nodos con relación padre-hijo acíclica dentro de una taxonomía declarada.
- Produce `alias_map` que vincula cada alias aceptado con exactamente un término canónico dentro de un alcance taxonómico.
- Emite `boundary_definition` para declarar qué significado incluye y excluye cada término canónico.
- Rechaza colisiones, nodos huérfanos, ciclos taxonómicos y aliases ambiguos antes de publicar vocabulario.

## what_it_does_not_do
- No normaliza datos, campos, unidades, fechas, valores de registros ni payloads de fuentes.
- No resuelve identidad de registros, facilities, organizaciones, documentos ni entidades observadas.
- No ingesta ni parsea documentos fuente; solo consume vocabularios o candidatos ya presentados como insumo.
- No evalúa calidad, completitud o fitness de datasets downstream.
- No decide joins entre registros; solo provee vocabulario canónico para que otros motores lo usen bajo contrato.
- No usa IA como autoridad semántica final ni genera términos obligatorios desde texto libre sin revisión estructurada.

## why_it_exists
Existe como motor separado porque la estabilidad semántica no debe mezclarse con ingesta, normalización o resolución de identidad. Depende de motor_001 para respetar contratos de fase y actúa como referencia común para evitar drift semántico, dialectos paralelos y joins inestables entre fuentes.
