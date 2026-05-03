# Usage Example — Duplicate / Similarity Control Engine

Motor ID: motor_010

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar duplicados exactos y near-duplicates a nivel raw, parsed y otros niveles.
why_it_exists:  No es lo mismo que identity resolution; controla repetición documental y dataset inflation.
key_inputs:     parsed_records (motor_004), normalized_records (motor_005), version_records (motor_002)
key_outputs:    duplicate_cluster, similarity_score, dedup_recommendation
key_objects:    DuplicateCluster, SimilarityRecord, DeduplicationDecision
what_not_to_do: No resuelve identidad de entidades. No evalúa calidad. Solo detecta repetición.
design_notes:   Opera antes de resolución de identidad. Controla repetición documental, no semántica.

Implementation usage example for the completed gate 5 artifact.
-->

## example
A downstream curation preparation step calls `DuplicateSimilarityControlEngine` after parsing and version tracking have produced traceable record objects. Two parsed agency records share the same raw content fingerprint, and normalized evidence is absent in this minimal run. The motor emits pairwise similarity evidence, a duplicate cluster for accepted duplicate evidence and an advisory-only deduplication recommendation without changing any source record.

## inputs_used
```python
from codebase import DuplicateSimilarityControlEngine

engine = DuplicateSimilarityControlEngine()

result = engine.process(
    parsed_records=[
        {
            "record_id": "parsed:rec_A",
            "source_id": "source:alpha",
            "raw_fingerprint": "sha256:111aaa",
            "parsed_fields": {
                "facility_name": "Alpha Plant",
                "state": "TX",
                "permit_id": "44",
            },
            "provenance": {
                "ingestion_run_id": "ing:2026-04-01",
                "parser_version": "parser-1.4.0",
            },
        },
        {
            "record_id": "parsed:rec_B",
            "source_id": "source:alpha_mirror",
            "raw_fingerprint": "sha256:111aaa",
            "parsed_fields": {
                "facility_name": "Alpha Plant",
                "state": "TX",
                "permit_id": "44",
            },
            "provenance": {
                "ingestion_run_id": "ing:2026-04-02",
                "parser_version": "parser-1.4.0",
            },
        },
    ],
    normalized_records=[],
    version_records=[
        {
            "version_id": "version:parsed_rec_A",
            "object_ref": "parsed:rec_A",
            "lineage_id": "lineage:parsed_rec_A",
            "content_fingerprint": "sha256:111aaa",
        },
        {
            "version_id": "version:parsed_rec_B",
            "object_ref": "parsed:rec_B",
            "lineage_id": "lineage:parsed_rec_B",
            "content_fingerprint": "sha256:111aaa",
        },
    ],
    method_version="dup-sim-1.0.0",
    threshold_profile_ref="threshold:default:2026-04",
)
```

## expected_output
The result is a `DuplicateSimilarityResult` with the schema-level output keys:

```json
{
  "duplicate_cluster": [
    {
      "cluster_id": "motor_010:cluster:<stable_sha256>",
      "member_record_refs": ["parsed:rec_A", "parsed:rec_B"],
      "cluster_fingerprint": "stable_sha256",
      "match_scope": "raw",
      "cluster_kind": "exact_duplicate",
      "evidence_refs": ["motor_010:similarity:<stable_sha256>"],
      "method_version": "dup-sim-1.0.0",
      "threshold_profile_ref": "threshold:default:2026-04",
      "version_context_refs": ["version:parsed_rec_A", "version:parsed_rec_B"],
      "version_id": "motor_010:cluster:<stable_sha256>:version:<stable_hash_prefix>",
      "created_at": "1970-01-01T00:00:00Z",
      "updated_at": "1970-01-01T00:00:00Z",
      "version_hash": "stable_sha256",
      "source_ref": [
        "motor_010:similarity:<stable_sha256>",
        "parsed:rec_A",
        "parsed:rec_B",
        "version:parsed_rec_A",
        "version:parsed_rec_B"
      ],
      "produced_by_motor": "motor_010",
      "produced_at": "1970-01-01T00:00:00Z",
      "parent_id": null
    }
  ],
  "similarity_score": [
    {
      "similarity_id": "motor_010:similarity:<stable_sha256>",
      "left_record_ref": "parsed:rec_A",
      "right_record_ref": "parsed:rec_B",
      "comparison_level": "raw",
      "similarity_score": 1.0,
      "similarity_kind": "exact_duplicate",
      "evidence_features": ["raw_fingerprint"],
      "threshold_profile_ref": "threshold:default:2026-04",
      "version_context_refs": ["version:parsed_rec_A", "version:parsed_rec_B"],
      "cluster_id": "motor_010:cluster:<stable_sha256>",
      "version_id": "motor_010:similarity:<stable_sha256>:version:<stable_hash_prefix>",
      "created_at": "1970-01-01T00:00:00Z",
      "updated_at": "1970-01-01T00:00:00Z",
      "version_hash": "stable_sha256",
      "source_ref": [
        "parsed:rec_A",
        "parsed:rec_B",
        "source:alpha",
        "source:alpha_mirror",
        "version:parsed_rec_A",
        "version:parsed_rec_B"
      ],
      "produced_by_motor": "motor_010",
      "produced_at": "1970-01-01T00:00:00Z",
      "parent_id": null
    }
  ],
  "dedup_recommendation": [
    {
      "decision_id": "motor_010:decision:<stable_sha256>",
      "cluster_id": "motor_010:cluster:<stable_sha256>",
      "recommendation": "suppress_duplicate",
      "target_record_refs": ["parsed:rec_B"],
      "rationale_refs": ["motor_010:similarity:<stable_sha256>"],
      "decision_status": "recommended_only",
      "method_version": "dup-sim-1.0.0",
      "version_id": "motor_010:decision:<stable_sha256>:version:<stable_hash_prefix>",
      "created_at": "1970-01-01T00:00:00Z",
      "updated_at": "1970-01-01T00:00:00Z",
      "version_hash": "stable_sha256",
      "source_ref": [
        "motor_010:cluster:<stable_sha256>",
        "motor_010:similarity:<stable_sha256>",
        "parsed:rec_B"
      ],
      "produced_by_motor": "motor_010",
      "produced_at": "1970-01-01T00:00:00Z",
      "parent_id": null
    }
  ]
}
```

The concrete identifiers are deterministic SHA-256 based values derived from sorted member references, comparison scope, method version and advisory decision inputs. The source `parsed_records`, `normalized_records` and `version_records` are not deleted, merged, rewritten or normalized by this motor.

## notes
Inputs must already come from `motor_004`, `motor_005` and `motor_002` with stable identifiers, provenance or lineage metadata and resolvable version context. Version succession is consulted before a duplicate recommendation is produced, so legitimate changed versions are not collapsed into suppression targets. The motor only controls document repetition and dataset inflation; it does not resolve entity identity, evaluate quality, decide factual truth or perform final curation.
