# Test Spec — Versioning + Lineage Engine

Motor ID: motor_002

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
why_it_exists:  Sin versionado no hay rebuild, stale detection ni auditoría seria.
key_inputs:     object mutations, source references, transformation records
key_outputs:    version_record, lineage_graph, impact_set, rebuild_manifest
key_objects:    VersionRecord, LineageNode, ImpactEdge
what_not_to_do: No decide si un objeto es válido. Solo registra versiones y dependencias.
design_notes:   Depende de motor_001 (phase contracts anclan el contexto de versión).

Sections below are complete for Gate 3 review.
-->

## happy_path
Input: registry already contains `VersionRecord.version_id = vr_facility_prior_041_v1` for `object_id = facility_prior:site_041`. A governed producer submits an `update` mutation with:
- `object_id = facility_prior:site_041`
- `object_type = facility_prior`
- `mutation_type = update`
- `phase_contract_ref = phase_contract:fase_1:v1`
- `prior_version_ref = vr_facility_prior_041_v1`
- `source_ref = src_registry_2026_04_10`
- `provenance_refs = ["src_registry_2026_04_10", "tr_normalize_884"]`
- `transformation_refs = ["tr_normalize_884"]`
- `dependency_version_refs = ["vr_facility_prior_041_v1"]`
- `produced_by_motor = motor_010`
- `produced_at = 2026-04-10T14:20:00Z`
- `content_hash = sha256:9a45f6a7b8c9d001`

Expected behavior: motor_002 accepts the mutation, creates one new append-only `VersionRecord` with `version_id = vr_facility_prior_041_v2`, `record_id = vr_facility_prior_041_v2`, `parent_id = vr_facility_prior_041_v1`, `prior_version_ref = vr_facility_prior_041_v1`, `version_hash = sha256:9a45f6a7b8c9d001`, and `updated_at = created_at`. It registers `LineageNode` records for the prior version, the new version, `src_registry_2026_04_10`, `tr_normalize_884`, and `phase_contract:fase_1:v1`. It registers causal `ImpactEdge` records from the prior version, source reference and transformation nodes to the new version node, plus a governance edge from the phase contract node. It emits a `LineageGraph` containing the referenced nodes and edges, an `ImpactSet` computed only from registered outgoing causal edges, and a `RebuildManifest` whose required versions, sources and transformations are ordered before `vr_facility_prior_041_v2`.

## sparse_case
Input: a governed producer submits a first `create` mutation for `object_id = evidence_bundle:eb_100`, `object_type = evidence_bundle`, `mutation_type = create`, `phase_contract_ref = phase_contract:fase_1:v1`, `source_ref = src_upload_2026_04_12`, `provenance_refs = ["src_upload_2026_04_12"]`, `transformation_refs = []`, `dependency_version_refs = []`, `prior_version_ref = null`, `parent_id = null`, `metadata` omitted, `produced_by_motor = motor_006`, `produced_at = 2026-04-12T09:00:00Z`, and `content_hash = sha256:1000abcdeffed001`.

Expected behavior: motor_002 accepts the input without fatal error because only optional `metadata` is absent and there is no predecessor for a first version. The emitted `VersionRecord` has `parent_id = null`, `prior_version_ref = null`, an empty `transformation_refs` list, an empty `dependency_version_refs` list, a non-empty `source_ref`, a non-empty `provenance_refs` list, and `updated_at = created_at`. The emitted `LineageGraph` contains at least the object-version node, source-reference node and phase-contract node. The emitted `ImpactSet.affected_refs` may be empty. The emitted `RebuildManifest.required_source_refs = ["src_upload_2026_04_12"]` and does not invent transformation references.

## malformed_input
Input: an `update` mutation is submitted with `object_id = 4102` as an integer, `object_type = facility_prior`, `mutation_type = update`, `phase_contract_ref = ""`, `prior_version_ref = vr_missing_parent`, `source_ref = ""`, `provenance_refs = []`, `produced_by_motor = motor_010`, `produced_at = 2026-04-10T14:20:00Z`, and `content_hash = sha256:badinput001`.

Expected behavior: motor_002 rejects the mutation before creating any `VersionRecord`, `LineageNode`, `ImpactEdge`, `LineageGraph`, `ImpactSet` or `RebuildManifest`. The structured error includes `status = REJECTED`, `error_code = LINEAGE_INPUT_MISSING_PHASE_CONTRACT`, and field-level violations for `object_id` type, empty `phase_contract_ref`, empty `source_ref`, empty `provenance_refs`, and unresolved `prior_version_ref`. If the implementation reports one primary error at a time, the first rejection must still be deterministic and no registry write may occur.

## edge_cases
- First version with no predecessor: input has `mutation_type = create`, `prior_version_ref = null`, `parent_id = null`, one source reference and no transformation references. Correct behavior is to create a new `VersionRecord`, create source and phase-contract lineage nodes, leave parent fields null, and keep rebuild requirements limited to declared source and version references.
- Causal cycle attempt: existing graph has causal edges `node_a -> node_b` and `node_b -> node_c`. A new causal `ImpactEdge` request would add `node_c -> node_a`. Correct behavior is to reject with `error_code = LINEAGE_CYCLE_DETECTED`, preserve the prior graph unchanged, and emit no derived impact set from the rejected edge.
- Duplicate edge submission: the same antecedent node, target node, `edge_type = derived_from`, and `evidence_ref = tr_normalize_884` are submitted twice. Correct behavior is idempotent registration of one deterministic `ImpactEdge.impact_edge_id`; the graph view and rebuild manifest must not contain duplicate edge or transformation references.
- Large fan-out impact traversal: one source-reference node has 200 outgoing causal edges to distinct object-version nodes. Correct behavior is to emit one source `LineageNode`, 200 distinct `ImpactEdge` records, and an `ImpactSet.affected_refs` list containing exactly the 200 dependent refs with deterministic ordering and no duplicates.

## pass_criteria
A test passes when all observable outputs match the contract:
- Accepted mutations emit exactly one new append-only `VersionRecord` with required identifiers, phase contract reference, provenance references, version hash, parent fields, `created_at`, and `updated_at = created_at`.
- Every emitted `LineageGraph.node_ids` entry resolves to a registered `LineageNode`, and every `LineageGraph.edge_ids` entry resolves to a registered `ImpactEdge` whose source and target nodes exist.
- `ImpactSet.affected_refs` is derived only from registered causal `ImpactEdge` traversal and is deterministic for the same registry state and root reference.
- `RebuildManifest.required_version_refs`, `required_source_refs`, and `required_transformation_refs` contain only declared lineage references, have no duplicates, and order prerequisites before dependent versions.
- Rejected inputs return structured errors with stable `error_code` values and leave the version registry and lineage graph unchanged.

## fail_criteria
A test fails if any of these conditions are observed:
- motor_002 accepts a mutation with missing or empty `object_id`, `object_type`, `mutation_type`, `phase_contract_ref`, `source_ref`, `provenance_refs`, `produced_by_motor`, `produced_at`, or content fingerprint.
- An `update`, `supersede`, `withdraw` or `restore` mutation is accepted with an unknown `prior_version_ref`.
- An existing `VersionRecord` is edited in place, deleted, overwritten, or given `updated_at` different from `created_at`.
- A causal `ImpactEdge` references an unknown node or creates a directed cycle.
- A lineage graph, impact set or rebuild manifest contains references that were inferred from narrative content instead of registered source, transformation, version or edge records.
- A malformed input produces a partial registry write, a non-structured exception, or a success output with null required fields.
