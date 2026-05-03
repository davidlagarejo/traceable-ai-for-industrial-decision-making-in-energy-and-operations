# Operational Rules — Versioning + Lineage Engine

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

## rules
1. Every accepted mutation must produce exactly one new VersionRecord with a globally stable version_id.
2. VersionRecords are append-only; a correction, rollback or withdrawal must be represented by a new VersionRecord and explicit edge, not by editing history.
3. Every VersionRecord must be linked to a phase_contract_ref from motor_001 before it can be emitted.
4. Every dependency recorded in an ImpactEdge must reference existing LineageNode identifiers.
5. A derived VersionRecord must retain references to all declared input versions, source references and transformation records.
6. Impact sets must be computed only from registered ImpactEdge relationships, not from semantic guesses about object content.
7. Rebuild manifests must list dependencies in deterministic parent-before-child order.
8. The motor must emit structured rejection errors rather than silently dropping incomplete provenance, duplicate identifiers or invalid edges.

## invariants
- A version_id, once emitted, always refers to the same object_id, content_hash, phase_contract_ref and created_at.
- No accepted VersionRecord exists without at least one provenance reference.
- No causal lineage edge points to an unknown node.
- The lineage graph remains directed and acyclic for causal edge types.
- Historical records remain reconstructible from stored version, source and transformation references.
- ImpactEdge direction always runs from antecedent or cause toward dependent or affected object.
- A rebuild_manifest never contains a dependency that is absent from the registered lineage graph.

## forbidden_operations
- Deciding whether an object is valid, high quality, true, approved or phase-ready.
- Editing, deleting or replacing an existing VersionRecord in place.
- Inferring missing provenance, source references or transformation records from free text.
- Creating canonical entity identities, semantic aliases or taxonomy terms.
- Normalizing object payloads or changing domain values.
- Deciding that downstream objects must be re-evaluated; the motor only emits impact data for a separate decision process.
- Executing a rebuild or source refresh instead of emitting a rebuild_manifest.
- Accepting lineage edges that bypass the phase contract boundary supplied by motor_001.
