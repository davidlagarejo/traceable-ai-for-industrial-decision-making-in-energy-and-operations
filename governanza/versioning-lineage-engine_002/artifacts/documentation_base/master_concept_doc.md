# Master Concept Document — Versioning + Lineage Engine

Motor ID: motor_002

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
why_it_exists:  Sin versionado no hay rebuild, stale detection ni auditoría seria.
key_inputs:     object mutations, source references, transformation records
key_outputs:    version_record, lineage_graph, impact_set, rebuild_manifest
key_objects:    VersionRecord, LineageNode, ImpactEdge
what_not_to_do: No decide si un objeto es válido. Solo registra versiones y dependencias.
design_notes:   Depende de motor_001 (phase contracts anclan el contexto de versión).

Sections below are complete for Gate 1 review.
-->

## purpose
Versioning + Lineage Engine registra versiones estables de objetos del framework cuando recibe mutaciones declaradas, referencias de fuente y registros de transformación. Mantiene el lineage entre versiones, fuentes y transformaciones para que cualquier objeto pueda auditarse y reconstruirse desde sus antecedentes declarados. También produce dependencias, conjuntos de impacto y manifiestos de reconstrucción sin decidir si el objeto versionado es válido o apto para uso.

## what_it_does
- Recibe mutaciones de objetos con identificador estable, versión previa opcional, fase y contrato de fase asociado desde motor_001.
- Valida que cada mutación incluya provenance mínimo: objeto afectado, causa del cambio, actor o proceso emisor, timestamp y referencias de entrada.
- Crea un `VersionRecord` inmutable para cada nueva versión aceptada.
- Registra `LineageNode` para objetos, fuentes y transformaciones que participan en la producción de una versión.
- Registra `ImpactEdge` entre versiones cuando una versión depende de otra, la reemplaza, la deriva o la invalida estructuralmente.
- Construye un `lineage_graph` consultable con nodos y bordes de dependencia.
- Calcula un `impact_set` determinista a partir de bordes registrados, limitado a objetos directa o transitivamente dependientes.
- Produce un `rebuild_manifest` con las versiones, fuentes y transformaciones necesarias para reconstruir un objeto o subgrafo.

## what_it_does_not_do
- No decide si un objeto es válido, verdadero, completo, de calidad suficiente o apto para una fase; solo registra versiones y dependencias declaradas.
- No corrige, normaliza ni transforma el contenido de objetos versionados.
- No resuelve identidad semántica entre entidades ni decide si dos objetos representan la misma entidad.
- No decide qué objetos deben re-evaluarse operativamente; solo entrega el impacto estructural que otros motores pueden consumir.
- No ejecuta rebuilds, recapturas, refresh de fuentes ni recomputaciones downstream.
- No modifica versiones históricas ya emitidas ni reescribe lineage previo.

## why_it_exists
Existe como motor separado porque la trazabilidad temporal y causal debe ser una capacidad transversal, determinista y auditable, no una función incidental dentro de cada motor productor. Depende de motor_001 porque los contratos de fase anclan el contexto permitido de cada versión, pero motor_001 no mantiene historial, lineage, impacto ni manifiestos de reconstrucción.
