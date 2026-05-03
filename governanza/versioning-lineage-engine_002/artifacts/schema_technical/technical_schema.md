# Technical Schema — Versioning + Lineage Engine

Motor ID: motor_002

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
why_it_exists:  Sin versionado no hay rebuild, stale detection ni auditoría seria.
key_inputs:     object mutations, source references, transformation records
key_outputs:    version_record, lineage_graph, impact_set, rebuild_manifest
key_objects:    VersionRecord, LineageNode, ImpactEdge
what_not_to_do: No decide si un objeto es válido. Solo registra versiones y dependencias.
design_notes:   Depende de motor_001 (phase contracts anclan el contexto de versión).

Schema sections below are complete for Gate 2 review.
-->

## entities
- VersionRecord: append-only record for one accepted object version. It stores the governed object reference, mutation metadata, phase contract reference from motor_001, payload fingerprint, provenance references and immediate parent version. Lives in `schema_technical` as the canonical persistent entity and in `implementation` as the immutable registry row.
- LineageNode: graph node representing a versioned object, source reference, transformation record or phase contract that participates in reconstruction. Lives in `schema_technical` as the graph vertex contract and in `implementation` as the node table or in-memory node model.
- ImpactEdge: directed graph edge from antecedent to dependent node. It records dependency, derivation, supersession, invalidation or source-use relationships without deciding quality or operational action. Lives in `schema_technical` as the graph edge contract and in `implementation` as the edge table or in-memory edge model.
- LineageGraph: deterministic view over LineageNode and ImpactEdge records for a root object, root version or subgraph query. Lives in `schema_technical` as an output DTO and in `implementation` as a computed read model.
- ImpactSet: deterministic set of object or version references affected by a registered node, computed only by traversing ImpactEdge records. Lives in `schema_technical` as an output DTO and in `implementation` as a computed read model.
- RebuildManifest: ordered manifest of source references, transformation records and version records required to reconstruct a target version. Lives in `schema_technical` as an output DTO and in `implementation` as a computed read model.

## fields
VersionRecord:
- version_id: string (required) — stable identifier for this emitted version record.
- record_id: string (required) — storage identifier for the registry row; equal to `version_id` unless a storage adapter needs a separate key.
- object_id: string (required) — stable identifier of the governed object being versioned.
- object_type: string (required) — governed object class allowed by the referenced phase contract.
- mutation_type: enum(create, update, supersede, withdraw, restore) (required) — declared kind of object mutation.
- phase_contract_ref: string (required) — reference to the motor_001 phase contract that authorizes the object type, handoff and boundary.
- parent_id: string|null (required) — immediate prior `version_id`; null only for a `create` mutation.
- prior_version_ref: string|null (required) — compatibility alias for `parent_id` in documentation-base artifacts.
- source_ref: string (required) — primary source, transformation or input reference anchoring this version's provenance.
- provenance_refs: list[string] (required) — complete declared provenance references for the version.
- transformation_refs: list[string] (required) — declared transformation records used to produce the version; empty only when the accepted mutation is not derived.
- dependency_version_refs: list[string] (required) — upstream version identifiers this version depends on.
- produced_by_motor: string (required) — governed motor identifier that produced or declared the mutation.
- produced_at: datetime (required) — timestamp at which the producing motor created the mutation or transformation output.
- created_at: datetime (required) — timestamp at which motor_002 accepted and registered the version.
- updated_at: datetime (required) — immutable audit timestamp; for VersionRecord it must equal `created_at`.
- version_hash: string (required) — deterministic payload fingerprint for the versioned content and required immutable metadata.
- metadata: object (optional) — non-authoritative adapter metadata that does not change identity, lineage, version hash or phase context.

LineageNode:
- lineage_node_id: string (required) — stable identifier for the graph node.
- node_type: enum(object_version, source_reference, transformation, phase_contract) (required) — technical class of the represented lineage element.
- ref_id: string (required) — external reference represented by the node, such as `version_id`, source id, transformation id or phase contract id.
- version_ref: string|null (required) — VersionRecord identifier when the node represents an object version; null for source, transformation and phase contract nodes.
- source_ref: string (required) — source reference used to anchor provenance for this node; for object-version nodes this mirrors the VersionRecord primary source.
- produced_by_motor: string (required) — motor that produced or declared the represented element.
- produced_at: datetime (required) — original production timestamp of the represented element.
- parent_id: string|null (required) — parent lineage node identifier for direct version ancestry; null for source roots and first object versions.
- created_at: datetime (required) — timestamp at which the node was registered by motor_002.
- updated_at: datetime (required) — immutable audit timestamp; for LineageNode it must equal `created_at`.

ImpactEdge:
- impact_edge_id: string (required) — stable identifier for the directed edge.
- source_node_id: string (required) — antecedent LineageNode identifier.
- target_node_id: string (required) — dependent or affected LineageNode identifier.
- edge_type: enum(depends_on, derived_from, supersedes, invalidates, uses_source, produced_by, governed_by_phase_contract) (required) — semantic class of the registered relationship.
- evidence_ref: string (required) — source, transformation, mutation or contract reference that justifies the edge.
- is_causal: boolean (required) — true when the edge participates in acyclic dependency traversal.
- created_at: datetime (required) — timestamp at which motor_002 registered the edge.
- updated_at: datetime (required) — immutable audit timestamp; for ImpactEdge it must equal `created_at`.

LineageGraph:
- graph_id: string (required) — deterministic identifier for the graph view.
- root_ref: string (required) — object, version or node reference used as traversal root.
- node_ids: list[string] (required) — LineageNode identifiers included in the view.
- edge_ids: list[string] (required) — ImpactEdge identifiers included in the view.
- generated_at: datetime (required) — timestamp at which the graph view was generated.
- traversal_policy: enum(ancestors, descendants, full_subgraph) (required) — deterministic traversal direction used to build the view.

ImpactSet:
- impact_set_id: string (required) — deterministic identifier for the impact result.
- root_ref: string (required) — version or node reference from which impact traversal starts.
- affected_refs: list[string] (required) — dependent object or version references reached through registered ImpactEdge records.
- edge_ids: list[string] (required) — edge identifiers used to compute the set.
- generated_at: datetime (required) — timestamp at which the impact set was generated.

RebuildManifest:
- manifest_id: string (required) — deterministic identifier for the rebuild manifest.
- target_version_ref: string (required) — version to reconstruct.
- required_version_refs: list[string] (required) — parent and dependency versions in parent-before-child order.
- required_source_refs: list[string] (required) — source references required by the target version and its dependencies.
- required_transformation_refs: list[string] (required) — transformation records required by the target version and its dependencies.
- generated_at: datetime (required) — timestamp at which the manifest was generated.

## relationships
- VersionRecord.parent_id references VersionRecord.version_id. It is nullable only for the first accepted version of an object.
- VersionRecord.phase_contract_ref references the motor_001 phase contract identifier. motor_002 stores the reference but does not own or validate phase approval semantics.
- VersionRecord.version_id is represented by exactly one LineageNode where `node_type = object_version` and `LineageNode.version_ref = VersionRecord.version_id`.
- LineageNode.ref_id references the represented external object: VersionRecord.version_id, source reference id, transformation id or phase contract id according to `node_type`.
- ImpactEdge.source_node_id references LineageNode.lineage_node_id and always points from antecedent or cause.
- ImpactEdge.target_node_id references LineageNode.lineage_node_id and always points to the dependent or affected node.
- ImpactEdge.edge_type governs traversal semantics: causal edge types must remain acyclic; non-causal metadata edges may be excluded from cycle checks.
- LineageGraph.node_ids reference LineageNode.lineage_node_id values reached by deterministic traversal.
- LineageGraph.edge_ids reference ImpactEdge.impact_edge_id values that connect included nodes.
- ImpactSet.affected_refs are derived from LineageNode.ref_id values reached through outgoing causal ImpactEdge traversal.
- RebuildManifest.target_version_ref references VersionRecord.version_id.
- RebuildManifest.required_version_refs reference VersionRecord.version_id values and must be ordered before the target or dependent versions that require them.
- RebuildManifest.required_source_refs and required_transformation_refs reference LineageNode.ref_id values where node_type is `source_reference` or `transformation`.

## identifiers
- VersionRecord canonical identifier: `version_id`. `record_id` is a storage alias and must not be used to redefine version identity.
- LineageNode canonical identifier: `lineage_node_id`, deterministically derived from `node_type` and `ref_id` when possible to support idempotent node registration.
- ImpactEdge canonical identifier: `impact_edge_id`, deterministically derived from source node, target node, edge type and evidence reference when possible to prevent duplicate causal edges.
- LineageGraph canonical identifier: `graph_id`, derived from root reference, traversal policy and included node or edge set.
- ImpactSet canonical identifier: `impact_set_id`, derived from root reference and sorted affected references.
- RebuildManifest canonical identifier: `manifest_id`, derived from target version and ordered required version, source and transformation references.
- External references are stored as strings and never rewritten by motor_002; adapters may validate format, but semantic ownership remains with the producing motor or source system.

## versioning
- `version_id` is required on every VersionRecord and is the stable identity of the emitted object version.
- `created_at` is required on VersionRecord, LineageNode and ImpactEdge and records when motor_002 accepted the immutable registry entry.
- `updated_at` is required on VersionRecord, LineageNode and ImpactEdge for uniform audit shape. Because these records are append-only, `updated_at` must equal `created_at`; corrections, withdrawal and supersession create a new VersionRecord and explicit ImpactEdge.
- `version_hash` is required on VersionRecord and is the technical payload fingerprint required by the documentation base as `content_hash` or equivalent. It must be computed deterministically from the canonical version payload plus immutable identity metadata.
- Version identity is not a latest-state pointer. Consumers that need the current version must resolve it from explicit supersession, withdrawal or restore edges without mutating historical records.
- A change in phase contract, provenance, payload hash or parent version creates a new VersionRecord even when object_id remains the same.

## lineage
- `source_ref` is required on VersionRecord and LineageNode. It anchors the primary declared source or transformation input for provenance; the complete set remains in `provenance_refs`, `required_source_refs` or graph nodes.
- `produced_by_motor` is required on VersionRecord and LineageNode. It identifies the governed motor that produced the mutation, transformation or referenced lineage element.
- `produced_at` is required on VersionRecord and LineageNode. It records the producing motor's event time, distinct from motor_002 `created_at`.
- `parent_id` is required on VersionRecord and LineageNode. It stores immediate ancestry and may be null only for first versions or root source nodes.
- Lineage edges are explicit ImpactEdge records. The engine must not infer source, transformation or dependency relationships from narrative content.
- Causal lineage traversal uses ImpactEdge records with `is_causal = true` and must reject any new causal edge that creates a directed cycle.
- Rebuild manifests are derived from registered lineage only and must order parent versions, source references and transformation records before dependent versions.
