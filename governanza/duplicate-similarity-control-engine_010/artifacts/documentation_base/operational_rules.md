# Operational Rules — Duplicate / Similarity Control Engine

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

## rules
1. The motor must reject processing when a comparable input record lacks stable record identity, provenance and lineage or version context.
2. Exact duplicate detection must be based on deterministic fingerprints or exact canonical field signatures, never on free-form judgment.
3. Near-duplicate detection must use fixed, versioned similarity rules and thresholds that remain unchanged during a run.
4. Similarity scores must always remain within `[0.0, 1.0]`, with exact duplicate evidence represented as `1.0`.
5. Cluster membership must be derived from accepted similarity edges and must be stable under reordering of input records.
6. Version records must be consulted before emitting a duplicate recommendation so legitimate version succession is not collapsed into document repetition.
7. Outputs must reference source records by identifier; the motor must not copy large payloads unless needed as explicit evidence excerpts.
8. Recommendations must be advisory only and must never perform deletion, merge or overwrite operations.

## invariants
- Every output object preserves traceable references to the input records and comparison evidence that produced it.
- No output object changes the content, provenance, lineage or version metadata of any upstream record.
- A `DuplicateCluster` always contains at least two distinct member record references.
- A record reference can appear only once within a single cluster.
- Every `DeduplicationDecision` references an existing `DuplicateCluster`.
- The same ordered set of valid inputs and method versions produces the same clusters, scores and recommendations.
- The motor's objects express document repetition only, not entity identity, source quality or truth status.

## forbidden_operations
- Resolving whether two records refer to the same real-world entity.
- Evaluating source quality, record reliability, factual correctness or analytic fitness.
- Deleting, merging, rewriting, normalizing or repairing upstream records.
- Fetching new source data or invoking ingestion, parsing, normalization or versioning responsibilities.
- Promoting a deduplication recommendation into a final curation action.
- Using opaque language-model judgment as the basis for duplicate or near-duplicate classification.
- Creating new motor responsibilities or new output classes beyond duplicate clusters, similarity records and deduplication recommendations.
