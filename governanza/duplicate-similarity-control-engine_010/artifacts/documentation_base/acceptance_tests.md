# Acceptance Tests — Duplicate / Similarity Control Engine

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

## happy_path
Input: three parsed records and their normalized counterparts arrive with version context. `rec_A` and `rec_B` have different ingestion identifiers but the same raw fingerprint `sha256:111aaa` and the same normalized field signature `facility=alpha|state=TX|permit=44`. `rec_C` has raw fingerprint `sha256:222bbb` and normalized field signature `facility=alpha inc|state=TX|permit=44`, which crosses the configured near-duplicate threshold for the same comparison method.

Action: the motor validates record identifiers, lineage references and version records, computes comparison fingerprints and applies the exact and near-duplicate rules.

Expected output: one `DuplicateCluster` contains `rec_A`, `rec_B` and `rec_C`; the `SimilarityRecord` for `rec_A` versus `rec_B` has `similarity_score = 1.0` and `comparison_level = raw`; the `SimilarityRecord` linking `rec_C` has a score below `1.0` but above the configured near-duplicate threshold; the `DeduplicationDecision` recommends `manual_review` or `suppress_duplicate` according to the declared threshold band without changing source records.

## edge_cases
- Sparse exact duplicate: two parsed records have minimal fields but share a valid raw fingerprint and lineage. Correct behavior is to emit an exact duplicate cluster from raw evidence and avoid near-duplicate scoring that requires absent normalized fields.
- Legitimate changed version: two records share `source_record_id` but `version_records` show a successor relationship and different content fingerprints. Correct behavior is to avoid suppressing the newer version as a duplicate and to emit no duplicate recommendation unless unchanged repeated content is detected.
- Same entity, different document: two normalized records refer to the same facility name but have different document fingerprints, dates and permit identifiers. Correct behavior is to emit no cluster because identity similarity is outside this motor's scope.
- Large repeated batch: fifty records share the same canonical field signature. Correct behavior is to emit a stable cluster with unique member references and evidence, not fifty pairwise recommendations with conflicting targets.

## rejection_criteria
- Reject with `DUPLICATE_INPUT_MISSING_TRACEABILITY` when any candidate record lacks `record_id` or provenance and cannot be traced back to a parsed or normalized upstream object.
- Reject with `DUPLICATE_INPUT_BROKEN_REFERENCE` when a `normalized_record` references a parsed `record_id` that is absent from the provided input set and has no explicit lineage bridge.
- Reject with `DUPLICATE_INPUT_INVALID_VERSION_CONTEXT` when a referenced `version_record.object_ref` conflicts with the supplied record identifier or lineage reference.
- Reject with `DUPLICATE_INPUT_UNSUPPORTED_PAYLOAD` when the input contains only analyst notes, prompts or entity labels rather than parsed or normalized record objects.
