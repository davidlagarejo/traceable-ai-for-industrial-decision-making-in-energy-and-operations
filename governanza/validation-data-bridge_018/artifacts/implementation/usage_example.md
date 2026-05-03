# Usage Example — Validation Data Bridge

Motor ID: motor_018

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Conectar datos estructurados del framework con evidencia local, medición y datos de sitio.
why_it_exists:  La verificación necesita anclarse al sistema completo de Fase 1.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    validation_data_set, bridge_manifest, evidentiary_record
key_objects:    ValidationDataSet, BridgeRecord, EvidentiaryLink
what_not_to_do: No puede ser sustituido por datos sintéticos. No produce field_evidence. Solo estructura datos reales para validación.
design_notes:   Produce evidencia de nivel validation_data (no synthetic_support). Requiere pipeline completo de Fase 1.
-->

## example
Verification Bridge prepares the April 2026 internal validation dataset for one site-meter reading after motors 004, 005, 006, 007 and 008 have emitted their upstream records. motor_018 receives the registered source snapshot, ingestion lineage, normalized value references, identity resolution and quality assessment, then emits a `ValidationDataSet` with one eligible `BridgeRecord`, a reconstruction manifest and a downstream `EvidentiaryRecord`. The output remains `validation_data`; it is not field evidence and cannot close claims by itself.

## inputs_used
```json
{
  "source_registry": {
    "snapshot_id": "SRS-2026-04-VALIDATION",
    "sources": [
      {
        "source_id": "SRC-LOCAL-001",
        "rights_profile_id": "RIGHTS-VAL-001",
        "validation_use": true,
        "access_class": "internal_allowed",
        "restriction_refs": ["license:internal-validation-only"],
        "allowed_destination_policies": ["policy:internal-validation"]
      }
    ]
  },
  "ingestion_records": [
    {
      "ingestion_record_id": "ING-100",
      "source_id": "SRC-LOCAL-001",
      "raw_record_ref": "raw://local/100",
      "parsed_record_ref": "parsed://local/100",
      "ingestion_lineage": ["capture:site_meter_a", "parse:v1"]
    }
  ],
  "normalized_records": [
    {
      "normalized_record_id": "NORM-100",
      "source_id": "SRC-LOCAL-001",
      "ingestion_record_id": "ING-100",
      "original_value_ref": "raw://local/100#value",
      "canonical_value_ref": "norm://local/100#canonical",
      "normalization_rule_ref": "rule://normalization/unit_kw_v1"
    }
  ],
  "identity_records": [
    {
      "identity_record_id": "ID-100",
      "normalized_record_id": "NORM-100",
      "ambiguity_flag": false
    }
  ],
  "quality_records": [
    {
      "quality_record_id": "QUAL-100",
      "normalized_record_id": "NORM-100",
      "fitness_score": 0.94,
      "quality_flags": [],
      "disqualification_reason": null
    }
  ],
  "validation_scope": "site_meter_validation_april_2026",
  "destination_policy_ref": "policy:internal-validation",
  "minimum_fitness_score": 0.70,
  "low_fitness_policy": "warn"
}
```

## expected_output
```json
{
  "validation_data_set": {
    "validation_data_set_id": "motor_018:validation_data_set:site_meter_validation_april_2026:<version_hash_prefix>",
    "evidence_level": "validation_data",
    "validation_scope": "site_meter_validation_april_2026",
    "source_registry_snapshot_id": "SRS-2026-04-VALIDATION",
    "bridge_record_ids": [
      "motor_018:bridge_record:NORM-100:<version_hash_prefix>"
    ],
    "exclusion_summary": {},
    "warning_summary": {},
    "restriction_refs": ["license:internal-validation-only"],
    "produced_by_motor": "motor_018"
  },
  "bridge_records": [
    {
      "bridge_record_id": "motor_018:bridge_record:NORM-100:<version_hash_prefix>",
      "source_id": "SRC-LOCAL-001",
      "rights_profile_id": "RIGHTS-VAL-001",
      "access_class": "internal_allowed",
      "ingestion_record_id": "ING-100",
      "raw_record_ref": "raw://local/100",
      "parsed_record_ref": "parsed://local/100",
      "normalized_record_id": "NORM-100",
      "original_value_ref": "raw://local/100#value",
      "canonical_value_ref": "norm://local/100#canonical",
      "normalization_rule_ref": "rule://normalization/unit_kw_v1",
      "identity_record_id": "ID-100",
      "identity_ambiguity_flag": false,
      "quality_record_id": "QUAL-100",
      "fitness_score": 0.94,
      "quality_flags": [],
      "validation_status": "eligible",
      "warning_codes": [],
      "exclusion_reason": null,
      "evidence_level": "validation_data",
      "restriction_refs": ["license:internal-validation-only"]
    }
  ],
  "bridge_manifest": {
    "source_registry_snapshot_id": "SRS-2026-04-VALIDATION",
    "source_ids": ["SRC-LOCAL-001"],
    "included_record_ids": [
      "motor_018:bridge_record:NORM-100:<version_hash_prefix>"
    ],
    "excluded_record_refs": [],
    "exclusion_reasons": {},
    "warning_reasons": {},
    "restriction_refs": ["license:internal-validation-only"],
    "rebuild_inputs": {
      "source_registry": ["SRS-2026-04-VALIDATION"],
      "ingestion_records": ["ING-100"],
      "normalized_records": ["NORM-100"],
      "identity_records": ["ID-100"],
      "quality_records": ["QUAL-100"]
    },
    "produced_by_motor": "motor_018"
  },
  "evidentiary_record": {
    "evidence_level": "validation_data",
    "validation_scope": "site_meter_validation_april_2026",
    "limits_of_use": [
      "Output evidence_level is validation_data only.",
      "This record is not field_evidence.",
      "This record cannot close claims or emit truth decisions by itself.",
      "Rights, access, license and redistribution restrictions remain binding."
    ],
    "restriction_refs": ["license:internal-validation-only"],
    "produced_by_motor": "motor_018"
  }
}
```

## notes
The example assumes all upstream records are already materialized and stable; motor_018 only copies references and classifies eligibility. If `SRC-LOCAL-001` is absent from the registry, validation use is denied, ingestion lineage is incomplete, normalization trace is missing, quality is disqualified, or any input is marked as synthetic support, the candidate is excluded and the reason is written into `bridge_manifest.exclusion_reasons`. Rights restrictions from motor_008 remain attached to the dataset, bridge record, evidentiary links, manifest and evidentiary record.
