# Technical Schema — Duplicate / Similarity Control Engine

Motor ID: motor_010

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar duplicados exactos y near-duplicates a nivel raw, parsed y otros niveles.
why_it_exists:  No es lo mismo que identity resolution; controla repetición documental y dataset inflation.
key_inputs:     parsed_records (motor_004), normalized_records (motor_005), version_records (motor_002)
key_outputs:    duplicate_cluster, similarity_score, dedup_recommendation
key_objects:    DuplicateCluster, SimilarityRecord, DeduplicationDecision
what_not_to_do: No resuelve identidad de entidades. No evalúa calidad. Solo detecta repetición.
design_notes:   Opera antes de resolución de identidad. Controla repetición documental, no semántica.

Schema sections are completed for Gate 2 validation.
-->

## entities
- `DuplicateCluster`
  - Description: output object that groups two or more distinct record references when deterministic exact-duplicate or near-duplicate evidence links them.
  - Stage: defined in `schema_technical`; produced by the motor output layer after comparison and clustering.
  - Scope boundary: represents document repetition only. It is not an entity identity match, a quality score or a final curation action.
- `SimilarityRecord`
  - Description: pairwise comparison evidence between two record references, including score, comparison level, method version and the evidence features used.
  - Stage: defined in `schema_technical`; produced during comparison before or alongside `DuplicateCluster` construction.
  - Scope boundary: explains duplicate evidence. It does not assert same real-world entity, factual truth or source reliability.
- `DeduplicationDecision`
  - Description: non-destructive recommendation derived from a `DuplicateCluster`, declaring whether downstream consumers should keep all records, suppress a duplicate candidate or send the cluster to manual review.
  - Stage: defined in `schema_technical`; produced after cluster construction as an advisory output.
  - Scope boundary: recommendation only. It must not delete, merge, rewrite or normalize upstream records.

## fields
`DuplicateCluster`
- `cluster_id`: string (required) — stable identifier for the cluster, generated from `motor_010`, sorted member references, `match_scope`, `cluster_kind` and `method_version`.
- `member_record_refs`: list[string] (required) — unique references to parsed or normalized records included in the cluster; must contain at least two items.
- `cluster_fingerprint`: string (required) — deterministic hash of the canonical cluster membership and evidence summary.
- `match_scope`: enum[`raw`, `parsed`, `normalized`, `cross_level`] (required) — comparison level that produced the cluster.
- `cluster_kind`: enum[`exact_duplicate`, `near_duplicate`, `version_repetition`] (required) — class of repetition evidenced by the cluster.
- `evidence_refs`: list[string] (required) — references to `SimilarityRecord.similarity_id` values or equivalent persisted comparison evidence.
- `method_version`: string (required) — version of the duplicate comparison and clustering method used for this cluster.
- `threshold_profile_ref`: string (optional) — reference to the threshold profile used when `cluster_kind` is `near_duplicate`.
- `version_context_refs`: list[string] (required) — references to version records from `motor_002` used to distinguish duplicates from legitimate version succession.
- `version_id`: string (required) — version identifier for this cluster object.
- `created_at`: datetime_iso8601 (required) — timestamp when this cluster object was first produced.
- `updated_at`: datetime_iso8601 (required) — timestamp when this cluster object version was last updated.
- `version_hash`: string (required) — deterministic hash of the serialized cluster content and method metadata.
- `source_ref`: list[string] (required) — upstream parsed, normalized and version record references that support the cluster.
- `produced_by_motor`: string (required) — constant value `motor_010`.
- `produced_at`: datetime_iso8601 (required) — timestamp when `motor_010` emitted this object.
- `parent_id`: string|null (required) — prior `cluster_id` when this cluster supersedes an earlier cluster version; otherwise `null`.

`SimilarityRecord`
- `similarity_id`: string (required) — stable identifier for the pairwise comparison record.
- `left_record_ref`: string (required) — first input record reference in deterministic sorted pair order.
- `right_record_ref`: string (required) — second input record reference in deterministic sorted pair order.
- `comparison_level`: enum[`raw`, `parsed`, `normalized`, `cross_level`] (required) — level at which the comparison was computed.
- `similarity_score`: number (required) — numeric score in the closed interval `[0.0, 1.0]`; exact fingerprint matches use `1.0`.
- `similarity_kind`: enum[`exact_duplicate`, `near_duplicate`, `reviewable_similarity`] (required) — classification produced by the comparison rule.
- `method_version`: string (required) — version of the comparison method and scoring rule.
- `evidence_features`: list[string] (required) — named evidence features used for the score, such as raw fingerprint, parsed field signature or normalized field signature.
- `threshold_profile_ref`: string (optional) — reference to the threshold profile used for near-duplicate or reviewable similarity classification.
- `version_context_refs`: list[string] (required) — references to `version_records` consulted for the compared records.
- `cluster_id`: string|null (required) — referenced `DuplicateCluster.cluster_id` when the comparison contributes to a cluster; otherwise `null` for reviewable evidence not yet clustered.
- `version_id`: string (required) — version identifier for this similarity object.
- `created_at`: datetime_iso8601 (required) — timestamp when this similarity object was first produced.
- `updated_at`: datetime_iso8601 (required) — timestamp when this similarity object version was last updated.
- `version_hash`: string (required) — deterministic hash of compared references, score, comparison metadata and evidence features.
- `source_ref`: list[string] (required) — upstream parsed, normalized and version record references used by the comparison.
- `produced_by_motor`: string (required) — constant value `motor_010`.
- `produced_at`: datetime_iso8601 (required) — timestamp when `motor_010` emitted this object.
- `parent_id`: string|null (required) — prior `similarity_id` when this record supersedes an earlier comparison version; otherwise `null`.

`DeduplicationDecision`
- `decision_id`: string (required) — stable identifier for the advisory deduplication recommendation.
- `cluster_id`: string (required) — referenced `DuplicateCluster.cluster_id` that the decision is based on.
- `recommendation`: enum[`keep_all`, `suppress_duplicate`, `manual_review`] (required) — non-destructive downstream handling recommendation.
- `target_record_refs`: list[string] (required) — record references affected by the recommendation; must be a subset of `DuplicateCluster.member_record_refs`.
- `rationale_refs`: list[string] (required) — references to supporting `SimilarityRecord.similarity_id` values or cluster evidence notes.
- `decision_status`: enum[`recommended_only`] (required) — status that prevents the recommendation from being treated as an executed curation action.
- `method_version`: string (required) — version of the decision rule used to produce the recommendation.
- `version_id`: string (required) — version identifier for this decision object.
- `created_at`: datetime_iso8601 (required) — timestamp when this decision object was first produced.
- `updated_at`: datetime_iso8601 (required) — timestamp when this decision object version was last updated.
- `version_hash`: string (required) — deterministic hash of decision content, cluster reference, target references and rule metadata.
- `source_ref`: list[string] (required) — upstream cluster, similarity and input record references that support the decision.
- `produced_by_motor`: string (required) — constant value `motor_010`.
- `produced_at`: datetime_iso8601 (required) — timestamp when `motor_010` emitted this object.
- `parent_id`: string|null (required) — prior `decision_id` when this recommendation supersedes an earlier decision version; otherwise `null`.

## relationships
- `DuplicateCluster.evidence_refs` references one or more `SimilarityRecord.similarity_id` values. This is a one-cluster-to-many-evidence relationship.
- `SimilarityRecord.cluster_id` references `DuplicateCluster.cluster_id` when the comparison contributes to an emitted cluster. Reviewable comparisons may keep `cluster_id = null`.
- `DeduplicationDecision.cluster_id` references exactly one `DuplicateCluster.cluster_id`.
- `DeduplicationDecision.target_record_refs` must be a subset of the referenced cluster's `member_record_refs`.
- `DeduplicationDecision.rationale_refs` references `SimilarityRecord.similarity_id` values or the referenced cluster's evidence notes.
- `SimilarityRecord.left_record_ref` and `SimilarityRecord.right_record_ref` reference input records from `parsed_records` (`motor_004`) or `normalized_records` (`motor_005`), with `comparison_level` declaring which representation was used.
- `DuplicateCluster.member_record_refs` references input records from `parsed_records` or `normalized_records`; cross-level clusters must preserve the upstream parsed-to-normalized lineage bridge.
- `version_context_refs` on `DuplicateCluster` and `SimilarityRecord` reference `version_records.version_id` or `version_records.object_ref` from `motor_002`.
- Common lineage field `parent_id` references the previous version of the same entity type only; it must not point across entity types.
- No relationship in this schema may point to an entity identity object as proof of duplication. Entity identity resolution remains outside `motor_010`.

## identifiers
- `DuplicateCluster.cluster_id` is the canonical stable identifier for `DuplicateCluster`.
  - Format: `motor_010:cluster:{sha256(sorted(member_record_refs), match_scope, cluster_kind, method_version)}`.
  - Stability rule: input order must not affect the identifier.
- `SimilarityRecord.similarity_id` is the canonical stable identifier for `SimilarityRecord`.
  - Format: `motor_010:similarity:{sha256(left_record_ref, right_record_ref, comparison_level, method_version)}`.
  - Stability rule: pair order is normalized before hashing, so comparing A to B and B to A produces the same identifier.
- `DeduplicationDecision.decision_id` is the canonical stable identifier for `DeduplicationDecision`.
  - Format: `motor_010:decision:{sha256(cluster_id, recommendation, sorted(target_record_refs), method_version)}`.
  - Stability rule: advisory decisions with changed target records, recommendation or rule version receive a new identifier.
- Input records keep their upstream identifiers as `record_id`, `normalized_record_id`, `version_id` or `object_ref`; `motor_010` stores references to them and does not mint replacement upstream identifiers.

## versioning
- Every `DuplicateCluster`, `SimilarityRecord` and `DeduplicationDecision` must include:
  - `version_id`: string (required) — stable version identifier for the object version emitted by this run.
  - `created_at`: datetime_iso8601 (required) — first creation timestamp for the object identity.
  - `updated_at`: datetime_iso8601 (required) — timestamp for the current object version.
  - `version_hash`: string (required) — deterministic hash of canonical serialized content, method metadata and lineage references.
- `version_hash` must change when membership, score, recommendation, method version, threshold profile, evidence references or lineage references change.
- `version_hash` must not change because of input ordering, non-semantic serialization ordering or runtime environment differences.
- `method_version` is required on all three entities so duplicate detection, similarity scoring and advisory decision rules can be reproduced.
- Versioning is non-mutating: a corrected object version supersedes an earlier object by reference through `parent_id`; it does not rewrite the prior object.

## lineage
- Every `DuplicateCluster`, `SimilarityRecord` and `DeduplicationDecision` must include:
  - `source_ref`: list[string] (required) — references to upstream parsed records, normalized records, version records and internal evidence objects used to produce the output.
  - `produced_by_motor`: string (required) — constant value `motor_010`.
  - `produced_at`: datetime_iso8601 (required) — emission timestamp for the object.
  - `parent_id`: string|null (required) — prior object identifier for same-type supersession, or `null` for first versions.
- Lineage must preserve enough upstream references to rebuild the comparison path from source record to similarity evidence, cluster and decision.
- A `SimilarityRecord.source_ref` must include both compared record references and any version context used to qualify the comparison.
- A `DuplicateCluster.source_ref` must include all member record references plus the supporting similarity evidence references.
- A `DeduplicationDecision.source_ref` must include the referenced cluster, rationale evidence and target record references.
- The lineage chain must remain advisory and reference-based. It must not mutate upstream parsed records, normalized records or version records.
