# Usage Example — Versioning + Lineage Engine

Motor ID: motor_002

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
why_it_exists:  Sin versionado no hay rebuild, stale detection ni auditoría seria.
key_inputs:     object mutations, source references, transformation records
key_outputs:    version_record, lineage_graph, impact_set, rebuild_manifest
key_objects:    VersionRecord, LineageNode, ImpactEdge
what_not_to_do: No decide si un objeto es válido. Solo registra versiones y dependencias.
design_notes:   Depende de motor_001 (phase contracts anclan el contexto de versión).
-->

## example
Motor `motor_010` updates the governed object `facility_prior:site_041` after applying transformation `tr_normalize_884` to source `src_registry_2026_04_10`. The engine receives the mutation under phase contract `phase_contract:fase_1:v1`, verifies that the prior version exists, appends one new version record, and registers explicit lineage edges from the prior version, source, transformation and phase contract nodes.

## inputs_used
```json
{
  "known_phase_contract_refs": ["phase_contract:fase_1:v1"],
  "initial_version_records": [
    {
      "version_id": "vr_facility_prior_041_v1",
      "object_id": "facility_prior:site_041",
      "object_type": "facility_prior",
      "mutation_type": "create",
      "phase_contract_ref": "phase_contract:fase_1:v1",
      "parent_id": null,
      "source_ref": "src_registry_2026_04_01",
      "provenance_refs": ["src_registry_2026_04_01"],
      "transformation_refs": [],
      "dependency_version_refs": [],
      "produced_by_motor": "motor_010",
      "produced_at": "2026-04-01T10:15:00Z",
      "created_at": "2026-04-01T10:16:00Z",
      "version_hash": "sha256:1f3a7c0b9e2d4401"
    }
  ],
  "object_mutation": {
    "version_id": "vr_facility_prior_041_v2",
    "object_id": "facility_prior:site_041",
    "object_type": "facility_prior",
    "mutation_type": "update",
    "phase_contract_ref": "phase_contract:fase_1:v1",
    "prior_version_ref": "vr_facility_prior_041_v1",
    "source_ref": "src_registry_2026_04_10",
    "provenance_refs": ["src_registry_2026_04_10", "tr_normalize_884"],
    "transformation_refs": ["tr_normalize_884"],
    "dependency_version_refs": ["vr_facility_prior_041_v1"],
    "produced_by_motor": "motor_010",
    "produced_at": "2026-04-10T14:20:00Z",
    "content_hash": "sha256:9a45f6a7b8c9d001"
  },
  "source_references": [
    {
      "source_id": "src_registry_2026_04_10",
      "source_version_id": "registry_snapshot_2026_04_10",
      "citation": "facility registry snapshot 2026-04-10",
      "accessed_at": "2026-04-10T14:18:00Z"
    }
  ],
  "transformation_records": [
    {
      "transformation_id": "tr_normalize_884",
      "input_object_refs": ["vr_facility_prior_041_v1", "src_registry_2026_04_10"],
      "rule_or_process_ref": "normalization_rule:facility_prior:v3",
      "parameter_set": {"country_scope": "US"},
      "timestamp": "2026-04-10T14:19:30Z",
      "output_object_ref": "facility_prior:site_041"
    }
  ]
}
```

## expected_output
```json
{
  "status": "ACCEPTED",
  "version_record": {
    "version_id": "vr_facility_prior_041_v2",
    "record_id": "vr_facility_prior_041_v2",
    "object_id": "facility_prior:site_041",
    "object_type": "facility_prior",
    "object_ref": "facility_prior:site_041",
    "mutation_type": "update",
    "phase_contract_ref": "phase_contract:fase_1:v1",
    "parent_id": "vr_facility_prior_041_v1",
    "prior_version_ref": "vr_facility_prior_041_v1",
    "source_ref": "src_registry_2026_04_10",
    "provenance_refs": ["src_registry_2026_04_10", "tr_normalize_884"],
    "transformation_refs": ["tr_normalize_884"],
    "dependency_version_refs": ["vr_facility_prior_041_v1"],
    "produced_by_motor": "motor_010",
    "produced_at": "2026-04-10T14:20:00Z",
    "created_at": "2026-04-10T14:21:00Z",
    "updated_at": "2026-04-10T14:21:00Z",
    "version_hash": "sha256:9a45f6a7b8c9d001"
  },
  "lineage_graph": {
    "root_ref": "vr_facility_prior_041_v2",
    "traversal_policy": "ancestors",
    "node_ids": [
      "object-version node for vr_facility_prior_041_v1",
      "object-version node for vr_facility_prior_041_v2",
      "source-reference node for src_registry_2026_04_10",
      "transformation node for tr_normalize_884",
      "phase-contract node for phase_contract:fase_1:v1"
    ],
    "edge_ids": [
      "prior-version-to-new-version edge",
      "source-to-new-version edge",
      "transformation-to-new-version edge",
      "phase-contract-to-new-version edge"
    ]
  },
  "impact_set": {
    "root_ref": "vr_facility_prior_041_v2",
    "affected_refs": [],
    "edge_ids": []
  },
  "rebuild_manifest": {
    "target_version_ref": "vr_facility_prior_041_v2",
    "required_version_refs": ["vr_facility_prior_041_v1"],
    "required_source_refs": ["src_registry_2026_04_01", "src_registry_2026_04_10"],
    "required_transformation_refs": ["tr_normalize_884"]
  },
  "lineage_validation_error": null
}
```

## notes
The example assumes `vr_facility_prior_041_v1` is already registered and that `phase_contract:fase_1:v1` was supplied by motor_001. The engine records lineage and rebuild prerequisites only; it does not decide whether the facility prior is correct, approved, stale, high quality or ready for downstream action.
