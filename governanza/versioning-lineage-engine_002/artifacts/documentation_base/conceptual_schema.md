# Conceptual Schema — Versioning + Lineage Engine

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

## entities
- VersionRecord: registro inmutable de una versión de objeto, incluyendo referencia al objeto, versión previa, contrato de fase, fingerprint de contenido y provenance.
- LineageNode: nodo del grafo de lineage que representa un objeto versionado, fuente, transformación o contrato de fase relevante para reconstrucción.
- ImpactEdge: relación dirigida entre nodos que expresa dependencia, derivación, reemplazo, invalidación estructural o uso de una fuente.
- LineageGraph: vista materializada o calculada del conjunto de LineageNode e ImpactEdge para un objeto, una versión o un subgrafo.
- RebuildManifest: lista ordenada de versiones, fuentes y transformaciones necesarias para reconstruir un objeto o conjunto de objetos.

## relationships
- VersionRecord -> VersionRecord (prior_version_ref; cero o una versión previa por registro, muchas versiones posteriores pueden derivar del mismo registro).
- VersionRecord -> LineageNode (represented_by; cada versión aceptada tiene un nodo de lineage correspondiente).
- LineageNode -> ImpactEdge (source_node; un nodo puede originar cero o muchos bordes de impacto).
- ImpactEdge -> LineageNode (target_node; cada borde apunta a exactamente un nodo dependiente o relacionado).
- TransformationRecord -> VersionRecord (produces; una transformación declarada puede producir una o más versiones nuevas).
- SourceReference -> LineageNode (materialized_as; una fuente citada se representa como nodo cuando participa en lineage).
- LineageGraph -> LineageNode (contains; el grafo contiene los nodos alcanzables para una consulta de lineage).
- RebuildManifest -> VersionRecord (requires; el manifiesto lista versiones requeridas en orden de reconstrucción).

## key_fields
VersionRecord:
- version_id: string
- object_id: string
- object_type: string
- prior_version_ref: string|null
- phase_contract_ref: string
- mutation_type: enum(create, update, supersede, withdraw, restore)
- content_hash: string
- provenance_refs: list[string]
- created_at: datetime

LineageNode:
- lineage_node_id: string
- node_type: enum(object_version, source_reference, transformation, phase_contract)
- ref_id: string
- version_ref: string|null
- created_at: datetime

ImpactEdge:
- impact_edge_id: string
- source_node_id: string
- target_node_id: string
- edge_type: enum(depends_on, derived_from, supersedes, invalidates, uses_source)
- evidence_ref: string
- created_at: datetime

LineageGraph:
- graph_id: string
- root_ref: string
- node_ids: list[string]
- edge_ids: list[string]
- generated_at: datetime

RebuildManifest:
- manifest_id: string
- target_version_ref: string
- required_version_refs: list[string]
- required_source_refs: list[string]
- required_transformation_refs: list[string]
- generated_at: datetime
