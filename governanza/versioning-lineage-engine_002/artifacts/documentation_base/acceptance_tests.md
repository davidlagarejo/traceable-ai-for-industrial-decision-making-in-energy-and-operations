# Acceptance Tests — Versioning + Lineage Engine

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

## happy_path
Input: a governed motor submits an `update` mutation for `object_id = facility_prior:site_042`, `object_type = facility_prior`, `prior_version_ref = vr_001`, `phase_contract_ref = phase_contract:fase_1:v1`, source references `src_public_registry_2026_04_10` and transformation record `tr_normalize_884`. Action: the engine validates required fields, confirms the prior version exists, creates a new VersionRecord `vr_002`, registers lineage nodes for the prior version, source reference and transformation, and adds edges `src_public_registry_2026_04_10 -> vr_002`, `tr_normalize_884 -> vr_002`, and `vr_001 -> vr_002`. Expected output: `version_record.version_id = vr_002`, a lineage graph containing all referenced nodes and edges, an impact_set containing objects registered as dependent on `vr_001` or `vr_002`, and a rebuild_manifest listing `src_public_registry_2026_04_10`, `vr_001`, `tr_normalize_884`, then `vr_002`.

## edge_cases
- First version of an object: input has `mutation_type = create` and `prior_version_ref = null`; correct behavior is to create a VersionRecord with no predecessor and still require phase_contract_ref, provenance_refs and content_hash.
- Shared dependency fan-out: one source reference feeds 200 downstream object versions; correct behavior is to register one source LineageNode, many ImpactEdge records and an impact_set that includes all affected dependent refs without duplicating the source node.
- Supersession without payload change: mutation declares `mutation_type = supersede` with the same content_hash but a new phase_contract_ref; correct behavior is to create a new VersionRecord because governance context changed, while preserving lineage to the prior version.
- Empty downstream impact: a version has no registered dependents; correct behavior is to emit an empty impact_set and a valid rebuild_manifest for the target version.

## rejection_criteria
- Missing phase contract: reject with `LINEAGE_INPUT_MISSING_PHASE_CONTRACT` when `phase_contract_ref` is null or empty.
- Unknown predecessor: reject with `VERSION_PRIOR_NOT_FOUND` when an update, supersede, withdraw or restore mutation references a prior_version_ref absent from the registry.
- Missing provenance: reject with `PROVENANCE_REQUIRED` when source references and transformation records are both absent for a mutation that produces a derived object.
- Cycle in causal lineage: reject with `LINEAGE_CYCLE_DETECTED` when a new causal edge would make a version depend on itself through a path of dependency edges.
- In-place rewrite attempt: reject with `IMMUTABLE_VERSION_RECORD` when input attempts to alter fields of an existing VersionRecord instead of creating a new version.
