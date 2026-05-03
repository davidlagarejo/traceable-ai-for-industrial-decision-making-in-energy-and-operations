# Master Concept Document — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.

Contenido completado para gate de documentation_base.
-->

## purpose
Este motor decide si dos o mas registros normalizados representan la misma entidad operativa, una entidad distinta o un caso que debe permanecer ambiguo. Usa los registros normalizados de `motor_005` y las entidades canonicas de `motor_003` como autoridad de comparacion. Su salida conserva la decision, la evidencia usada y el motivo por el que una identidad fue unificada, separada o mantenida abierta.

## what_it_does
- Recibe conjuntos de `normalized_records` ya estructurados por el motor de normalizacion.
- Recibe `canonical_entities` como marco de identidad autorizada desde `motor_003`.
- Compara identificadores, nombres canonicos, aliases, contexto taxonomico y metadatos de provenance para formar candidatos de identidad.
- Emite un `identity_resolution_record` por evaluacion de identidad realizada.
- Agrupa registros compatibles en un `entity_cluster` cuando la evidencia supera el umbral determinista definido.
- Emite `ambiguity_flag` cuando la evidencia es insuficiente, contradictoria o dependiente de revision externa.
- Registra conflictos de resolucion sin mutar silenciosamente los registros fuente.

## what_it_does_not_do
- No detecta duplicados documentales. Eso es responsabilidad de `motor_010`; este motor solo resuelve identidad de entidades.
- No normaliza campos crudos ni corrige valores originales; esa transformacion pertenece a `motor_005`.
- No crea taxonomias canonicas ni redefine entidades maestras; usa las entidades canonicas disponibles desde `motor_003`.
- No fuerza un merge cuando la evidencia no permite una decision determinista.
- No evalua calidad estructural o fitness de uso; esa evaluacion corresponde a motores posteriores como `motor_007`.
- No elimina registros, no fusiona documentos y no altera lineage/provenance de origen.

## why_it_exists
La resolucion de identidad necesita un motor separado porque confundir identidad semantica con normalizacion, taxonomia o deduplicacion documental produce merges erroneos y perdida de comparabilidad. Su capacidad central es aceptar una tercera salida valida: dejar la ambigüedad abierta cuando la evidencia no alcanza, preservando trazabilidad para revision o procesamiento posterior.
