# Usage Example — Library Curation Engine

Motor ID: motor_011

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
why_it_exists:  Evita que cada fase arme su propia pseudo-biblioteca local.
key_inputs:     quality_records (motor_007), identity_records (motor_006), dedup_records (motor_010)
key_outputs:    library_object, curated_bundle, library_version
key_objects:    LibraryObject, CuratedBundle, LibraryVersion
what_not_to_do: No ingesta datos nuevos. No evalúa calidad. Solo selecciona y organiza objetos aptos como biblioteca.
design_notes:   Requiere el pipeline completo de Fase 1.

All implementation-stage sections below are filled with concrete content.
-->

## example
The phase assembly process calls `LibraryCurationEngine` after `motor_007`, `motor_006` and `motor_010` have already produced governed evidence for candidate `obj-001`. The motor receives one passing quality record, one resolved identity record and one non-suppressing duplicate decision, then emits a reusable library object inside the `phase_1_context_library` bundle with immutable version records.

## inputs_used
```json
{
  "quality_records": [
    {
      "quality_record_id": "qr-lib-001",
      "subject_ref": "obj-001",
      "evaluation_status": "pass",
      "fitness_score": {"total_score": 0.92},
      "quality_flags": [],
      "phase_contract_ref": "pc-phase1",
      "evaluation_run_id": "qrun-001",
      "provenance_refs": ["prov-obj-001"],
      "lineage_refs": ["lin-quality-001"]
    }
  ],
  "identity_records": [
    {
      "identity_record_id": "ir-lib-001",
      "evaluated_record_ids": ["obj-001"],
      "decision": "same_entity",
      "confidence_band": "high",
      "evidence_refs": ["ev-id-001"],
      "rule_version": "idrule-1.0.0",
      "lineage_refs": ["lin-id-001"]
    }
  ],
  "dedup_records": [
    {
      "decision_id": "dd-lib-001",
      "candidate_ref": "obj-001",
      "recommendation": "retain",
      "cluster_ref": "dc-lib-001",
      "member_refs": ["obj-001", "obj-009"],
      "method_version": "dedup-1.0.0",
      "rationale_refs": ["rat-dedup-001"]
    }
  ],
  "curation_policy": {
    "curation_run_id": "cur-run-001",
    "curation_rule_version": "libcur-1.0.0",
    "bundle_scope": "phase_1_context_library",
    "accepted_quality_statuses": ["pass", "conditional_pass"],
    "blocking_flag_codes": [
      "missing_lineage",
      "missing_provenance",
      "not_fit_for_phase"
    ],
    "duplicate_policy": "retain_representative",
    "published_at": "2026-04-17T10:00:00Z"
  }
}
```

## expected_output
```json
{
  "library_object": [
    {
      "library_object_id": "lo_7970738076b9545fe252",
      "source_object_ref": "obj-001",
      "quality_record_ref": "qr-lib-001",
      "identity_record_ref": "ir-lib-001",
      "dedup_evidence_refs": ["dc-lib-001", "dd-lib-001", "rat-dedup-001"],
      "curation_status": "included",
      "curation_rule_version": "libcur-1.0.0",
      "curation_run_id": "cur-run-001",
      "bundle_scope": "phase_1_context_library",
      "warning_refs": [],
      "rejection_reason_ref": null,
      "provenance_refs": [
        "dc-lib-001",
        "dd-lib-001",
        "ev-id-001",
        "ir-lib-001",
        "pc-phase1",
        "prov-obj-001",
        "qr-lib-001",
        "qrun-001",
        "rat-dedup-001"
      ],
      "lineage_refs": [
        "dc-lib-001",
        "dd-lib-001",
        "idrule-1.0.0",
        "lin-id-001",
        "lin-quality-001",
        "pc-phase1",
        "qrun-001",
        "rat-dedup-001"
      ],
      "source_ref": "obj-001",
      "produced_by_motor": "motor_011",
      "produced_at": "2026-04-17T10:00:00Z",
      "parent_id": null,
      "version_id": "lv_c701f14427e72283be9d",
      "created_at": "2026-04-17T10:00:00Z",
      "updated_at": "2026-04-17T10:00:00Z",
      "version_hash": "7970738076b9545fe252ee079095c58c4febde9babc37468461a5e067bdb5d6e"
    }
  ],
  "curated_bundle": {
    "curated_bundle_id": "cb_dcddc267cc2cd154623c",
    "bundle_scope": "phase_1_context_library",
    "member_library_object_refs": ["lo_7970738076b9545fe252"],
    "excluded_candidate_refs": [],
    "rejection_refs": [],
    "selection_rule_version": "libcur-1.0.0",
    "curation_run_id": "cur-run-001",
    "membership_fingerprint": "fb3b45e134e2bfd481ddda158b5e804edf43f99fe7e83ea665d4a0e1db66fb82",
    "provenance_refs": [
      "cur-run-001",
      "dc-lib-001",
      "dd-lib-001",
      "ev-id-001",
      "ir-lib-001",
      "pc-phase1",
      "phase_1_context_library",
      "prov-obj-001",
      "qr-lib-001",
      "qrun-001",
      "rat-dedup-001"
    ],
    "lineage_refs": [
      "cur-run-001",
      "dc-lib-001",
      "dd-lib-001",
      "idrule-1.0.0",
      "libcur-1.0.0",
      "lin-id-001",
      "lin-quality-001",
      "pc-phase1",
      "phase_1_context_library",
      "qrun-001",
      "rat-dedup-001"
    ],
    "source_ref": "phase_1_context_library",
    "produced_by_motor": "motor_011",
    "produced_at": "2026-04-17T10:00:00Z",
    "parent_id": null,
    "version_id": "lv_a4c49f1bafc471927e80",
    "created_at": "2026-04-17T10:00:00Z",
    "updated_at": "2026-04-17T10:00:00Z",
    "version_hash": "dcddc267cc2cd154623c53283b766be64e9634aec0186b5eedd403fe516c1ff3"
  },
  "library_version": [
    {
      "library_version_id": "lv_a4c49f1bafc471927e80",
      "version_id": "lv_a4c49f1bafc471927e80",
      "versioned_object_ref": "cb_dcddc267cc2cd154623c",
      "versioned_object_type": "curated_bundle",
      "content_fingerprint": "dcddc267cc2cd154623c53283b766be64e9634aec0186b5eedd403fe516c1ff3",
      "version_hash": "a4c49f1bafc471927e80001e0a79a6322fd1e8c6c7a6363958efab2396fec38e",
      "prior_version_ref": null,
      "curation_rule_version": "libcur-1.0.0",
      "rebuild_manifest_ref": null,
      "source_ref": "phase_1_context_library",
      "produced_by_motor": "motor_011",
      "produced_at": "2026-04-17T10:00:00Z",
      "parent_id": null,
      "lineage_refs": [
        "cur-run-001",
        "dc-lib-001",
        "dd-lib-001",
        "idrule-1.0.0",
        "libcur-1.0.0",
        "lin-id-001",
        "lin-quality-001",
        "pc-phase1",
        "phase_1_context_library",
        "qrun-001",
        "rat-dedup-001"
      ],
      "created_at": "2026-04-17T10:00:00Z",
      "updated_at": "2026-04-17T10:00:00Z"
    },
    {
      "library_version_id": "lv_c701f14427e72283be9d",
      "version_id": "lv_c701f14427e72283be9d",
      "versioned_object_ref": "lo_7970738076b9545fe252",
      "versioned_object_type": "library_object",
      "content_fingerprint": "7970738076b9545fe252ee079095c58c4febde9babc37468461a5e067bdb5d6e",
      "version_hash": "c701f14427e72283be9d21aafd2838b2acb0eae6c6c7b2f8004a7750f2adc48c",
      "prior_version_ref": null,
      "curation_rule_version": "libcur-1.0.0",
      "rebuild_manifest_ref": null,
      "source_ref": "obj-001",
      "produced_by_motor": "motor_011",
      "produced_at": "2026-04-17T10:00:00Z",
      "parent_id": null,
      "lineage_refs": [
        "dc-lib-001",
        "dd-lib-001",
        "idrule-1.0.0",
        "lin-id-001",
        "lin-quality-001",
        "pc-phase1",
        "qrun-001",
        "rat-dedup-001"
      ],
      "created_at": "2026-04-17T10:00:00Z",
      "updated_at": "2026-04-17T10:00:00Z"
    }
  ],
  "curation_rejection": []
}
```

## notes
This example assumes candidate identity, quality and duplicate evidence already exists and is read-only for `motor_011`. If `evaluation_status` changes to `rejected`, a blocking quality flag appears, identity becomes ambiguous or the duplicate decision suppresses `obj-001`, the engine emits a structured exclusion instead of a `LibraryObject` and produces a new bundle version for the changed membership.
