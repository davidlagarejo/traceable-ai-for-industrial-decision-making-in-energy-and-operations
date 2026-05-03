# Conceptual Schema — Duplicate / Similarity Control Engine

Motor ID: motor_010

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar duplicados exactos y near-duplicates a nivel raw, parsed y otros niveles.
why_it_exists:  No es lo mismo que identity resolution; controla repetición documental y dataset inflation.
key_inputs:     parsed_records (motor_004), normalized_records (motor_005), version_records (motor_002)
key_outputs:    duplicate_cluster, similarity_score, dedup_recommendation
key_objects:    DuplicateCluster, SimilarityRecord, DeduplicationDecision
what_not_to_do: No resuelve identidad de entidades. No evalúa calidad. Solo detecta repetición.
design_notes:   Opera antes de resolución de identidad. Controla repetición documental, no semántica.

Sections completed for Gate 1 validation.
-->

## entities
- `DuplicateCluster`: group of two or more record references that share exact duplicate evidence or near-duplicate evidence under the motor's deterministic comparison rules.
- `SimilarityRecord`: comparison record for a pair of records, including the score, comparison level, method version and evidence features that explain why the pair was accepted or flagged.
- `DeduplicationDecision`: advisory decision derived from a cluster that recommends retention, suppression or manual review without modifying upstream data.

## relationships
- `SimilarityRecord` -> `DuplicateCluster` (one or more accepted similarity records justify the membership of a cluster).
- `DuplicateCluster` -> `DeduplicationDecision` (each cluster can produce one or more non-destructive recommendations).
- `parsed_records` -> `SimilarityRecord` (parsed content supplies field-level comparison evidence).
- `normalized_records` -> `SimilarityRecord` (normalized content supplies canonical comparison evidence).
- `version_records` -> `SimilarityRecord` (version lineage qualifies whether repeated content is a duplicate, unchanged reissue or expected version successor).
- `DeduplicationDecision` -> `DuplicateCluster` (every recommendation must reference exactly one existing cluster).

## key_fields
`DuplicateCluster`
- `cluster_id`: string
- `member_record_refs`: list[string]
- `cluster_fingerprint`: string
- `match_scope`: enum[`raw`, `parsed`, `normalized`, `cross_level`]
- `cluster_kind`: enum[`exact_duplicate`, `near_duplicate`, `version_repetition`]
- `evidence_refs`: list[string]

`SimilarityRecord`
- `similarity_id`: string
- `left_record_ref`: string
- `right_record_ref`: string
- `comparison_level`: enum[`raw`, `parsed`, `normalized`, `cross_level`]
- `similarity_score`: number
- `method_version`: string
- `evidence_features`: list[string]

`DeduplicationDecision`
- `decision_id`: string
- `cluster_id`: string
- `recommendation`: enum[`keep_all`, `suppress_duplicate`, `manual_review`]
- `target_record_refs`: list[string]
- `rationale_refs`: list[string]
- `decision_status`: enum[`recommended_only`]
