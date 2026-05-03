# Failure Modes Spec — Versioning + Lineage Engine

Motor ID: motor_002

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
why_it_exists:  Sin versionado no hay rebuild, stale detection ni auditoría seria.
key_inputs:     object mutations, source references, transformation records
key_outputs:    version_record, lineage_graph, impact_set, rebuild_manifest
key_objects:    VersionRecord, LineageNode, ImpactEdge
what_not_to_do: No decide si un objeto es válido. Solo registra versiones y dependencias.
design_notes:   Depende de motor_001 (phase contracts anclan el contexto de versión).

Sections below are complete for Gate 4 review.
-->

## failure_modes_list
- LINEAGE_GAP: an accepted mutation lacks `source_ref`, complete `provenance_refs`, declared `transformation_refs`, or a required `dependency_version_refs` entry → `VersionRecord` is emitted but `RebuildManifest` cannot list all reconstruction prerequisites → reject the mutation before registry write with a structured lineage validation error, require the producer to resubmit complete provenance, and keep the prior registry unchanged.
- HISTORY_REWRITE: an implementation updates, deletes, or replaces an existing `VersionRecord`, `LineageNode`, or `ImpactEdge` instead of appending a new version or explicit supersession edge → audit comparison shows changed immutable fields such as `version_hash`, `phase_contract_ref`, `created_at`, `updated_at`, `parent_id`, or edge endpoints → stop the write path, restore the last immutable snapshot from audit storage, and re-register the correction as a new `VersionRecord` plus explicit causal edge.
- PHASE_CONTEXT_LOSS: `phase_contract_ref` is empty, unresolved, or stored only as adapter metadata rather than as a required field on the version and phase-contract node → downstream consumers cannot verify the authorized object boundary or handoff context for the version → reject the input with a stable phase-contract error code and require a valid motor_001 phase contract reference before any lineage node or impact edge is created.
- CAUSAL_CYCLE_ACCEPTED: a new causal `ImpactEdge` from antecedent to dependent would close a directed cycle and the engine accepts it → lineage traversal, impact traversal, or rebuild ordering repeats nodes or produces non-deterministic manifests → run cycle detection before edge persistence, reject the edge with `LINEAGE_CYCLE_DETECTED`, and leave the existing graph untouched.
- IMPACT_MISCOUNT: edge direction is reversed, duplicate edges are not deduplicated, or traversal includes non-causal metadata edges → `ImpactSet.affected_refs` undercounts true dependents, overcounts unrelated refs, or changes order between identical runs → compute impact only from registered `ImpactEdge` records with `is_causal = true`, deduplicate by deterministic `impact_edge_id`, and sort affected refs by the declared traversal policy.
- REBUILD_ORDER_ERROR: `RebuildManifest.required_version_refs`, `required_source_refs`, or `required_transformation_refs` are generated from unordered registry scans or narrative inference rather than graph topology → rebuild tooling receives dependent versions before parents or includes references absent from lineage → derive manifests only from registered lineage, topologically order parent versions before dependents, and reject manifest generation when any referenced node is unresolved.

## anti_patterns
- Mutable latest-state table: storing only the current object state or overwriting rows for the same `object_id` breaks append-only history and makes audit reconstruction impossible.
- Free-text lineage inference: deriving source, transformation, dependency, or phase-contract relationships from narrative content instead of explicit refs violates the deterministic-first contract and produces unauditable edges.
- Validation creep: using motor_002 to decide object quality, truth, phase approval, re-evaluation priority, source freshness, or canonical identity invades the responsibilities of other motors.
- Generic graph blob: collapsing versions, sources, transformations, and phase contracts into untyped nodes removes the ability to enforce `node_type`, `edge_type`, causal traversal, and rebuild semantics.
- Manual impact editing: allowing downstream tools or operators to patch `ImpactSet.affected_refs` directly instead of deriving it from registered causal edges destroys reproducibility.
- Opaque adapter ownership: letting storage adapters rewrite external references, version identifiers, timestamps, or hashes makes lineage depend on local persistence behavior rather than on stable engine contracts.
- Partial-write workflow: creating a `VersionRecord` before all lineage nodes, impact edges, and rejection checks are resolved leaves the registry in a state that cannot be safely traversed.

## degradation_signals
- `lineage_validation_error` rate increases for missing `phase_contract_ref`, empty `provenance_refs`, unresolved `prior_version_ref`, or missing `source_ref` from producers that previously emitted complete mutations.
- Any nonzero count of immutable-field drift where persisted `VersionRecord`, `LineageNode`, or `ImpactEdge` rows have `updated_at != created_at` or changed `version_hash`, `parent_id`, endpoint, or evidence fields after initial registration.
- Growth in duplicate `LineageNode` records for the same `(node_type, ref_id)` or duplicate `ImpactEdge` records for the same `(source_node_id, target_node_id, edge_type, evidence_ref)`.
- Rebuild manifest generation logs unresolved version, source, or transformation references, or produces dependency lists that fail parent-before-child ordering checks.
- Impact traversal metrics diverge unexpectedly: comparable roots produce unstable `affected_refs` counts across repeated runs, or traversal includes edges with `is_causal = false`.
- Cycle-detection warnings appear during routine ingestion, especially after bulk imports or adapter migrations.
- Registry write logs show accepted mutations followed by compensating deletes, manual edits, or non-structured exceptions, indicating partial-write recovery rather than atomic rejection.
- Repeated graph-query timeouts or memory spikes occur on roots with normal fan-out, suggesting duplicate edges, cycles, or unbounded traversal.

## expensive_errors
- Rewriting historical versions after downstream consumers have referenced them: expensive because every `ImpactSet`, `RebuildManifest`, audit trail, and downstream object may point to a version whose identity changed. Prevent by enforcing append-only persistence, storing immutable hash snapshots, and representing corrections with new versions plus explicit supersession or invalidation edges.
- Accepting versions without complete provenance: expensive because missing source or transformation refs cannot always be reconstructed after producers have moved on or source systems have changed. Prevent by rejecting missing `source_ref`, empty `provenance_refs`, unresolved `prior_version_ref`, and absent transformation records before any registry write.
- Registering reversed or cyclic causal edges: expensive because stale detection, impact propagation, and rebuild ordering can silently target the wrong objects across many downstream motors. Prevent by validating edge endpoint existence, edge direction, `is_causal`, and directed acyclicity before persisting an `ImpactEdge`.
- Generating manifests from inferred relationships: expensive because rebuilds may appear to work while using undeclared dependencies, making later audit disputes hard to unwind. Prevent by deriving `RebuildManifest` only from `LineageNode` and `ImpactEdge` records and failing closed when a dependency is not registered.
- Losing the phase contract reference: expensive because versions become detached from the motor_001 boundary that explains allowed object type, handoff, and output scope. Prevent by treating `phase_contract_ref` as a required first-class field on `VersionRecord` and a registered phase-contract lineage node, not optional metadata.
- Allowing partial writes on malformed input: expensive because cleanup requires graph surgery across versions, nodes, edges, impact views, and manifests. Prevent by validating the full mutation, edge set, cycle check, and manifest prerequisites before commit, then writing accepted registry entries atomically.
