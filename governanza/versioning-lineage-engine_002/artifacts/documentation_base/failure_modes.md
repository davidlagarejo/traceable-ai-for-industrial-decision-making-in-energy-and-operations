# Failure Modes — Versioning + Lineage Engine

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

## failure_modes_list
- LINEAGE_GAP: a VersionRecord exists but one or more required provenance, source or transformation references are absent, making rebuild impossible.
- HISTORY_REWRITE: an existing VersionRecord changes content_hash, phase_contract_ref or created_at after emission, breaking audit comparability.
- IMPACT_UNDERCOUNT: impact_set omits registered dependent nodes because edges were not traversed transitively or edge direction was reversed.
- IMPACT_OVERCOUNT: impact_set includes unrelated objects because the engine inferred semantic relationships instead of following registered ImpactEdge records.
- REBUILD_ORDER_ERROR: rebuild_manifest lists dependent versions before required parents, making deterministic reconstruction fail.
- PHASE_CONTEXT_LOSS: versions are emitted without a valid phase_contract_ref, so consumers cannot verify allowed handoffs or output boundaries.

## anti_patterns
- Treating versioning as a mutable status table where the latest row overwrites historical records.
- Using this motor to judge object quality or validity instead of delegating those decisions to the proper evaluation or phase contract mechanisms.
- Creating lineage edges from narrative descriptions without explicit source, transformation or version references.
- Collapsing source references, transformations and object versions into one generic blob that cannot be traversed or audited.
- Letting downstream consumers modify impact sets manually instead of deriving them from registered edges.

## degradation_signals
- Rising count of VersionRecords with empty provenance_refs or missing phase_contract_ref.
- Nonzero count of in-place modifications detected by comparing stored content_hash and immutable metadata snapshots.
- Frequent rebuild_manifest failures caused by missing parent versions, missing source references or unresolved transformation refs.
- Large divergence between registered dependency edge count and impact_set size for comparable object classes.
- Duplicate LineageNode records for the same ref_id and node_type beyond accepted idempotency rules.
- Cycle detection warnings appearing in routine version operations.
- Increase in lineage_validation_error events from governed motors that previously emitted complete mutation records.
