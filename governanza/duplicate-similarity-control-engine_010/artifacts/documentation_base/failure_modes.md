# Failure Modes — Duplicate / Similarity Control Engine

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

## failure_modes_list
- `FINGERPRINT_COLLISION_OR_TRUNCATION`: unrelated records are grouped because fingerprints are too short, malformed or generated from insufficient content.
- `VERSION_CHAIN_CONFUSION`: expected version successors are treated as duplicates, causing valid updated records to be recommended for suppression.
- `NORMALIZATION_OVERCOMPRESSION`: aggressive upstream normalization collapses distinct documents into the same signature and increases false positive clusters.
- `THRESHOLD_DRIFT`: near-duplicate thresholds change between runs without method version changes, making outputs non-reproducible.
- `MISSING_PROVENANCE_ACCEPTANCE`: records without traceable provenance enter clusters, making duplicate evidence impossible to audit.

## anti_patterns
- Treating a duplicate cluster as proof that all records describe the same real-world entity.
- Allowing this motor to delete, merge or rewrite source records based on its own recommendations.
- Adding source quality scoring or truth evaluation to similarity logic.
- Using language-model similarity judgments as a replacement for deterministic fingerprints, signatures or declared scoring rules.

## degradation_signals
- Sudden increase in duplicate cluster rate after a parser or normalization version change.
- Growth of very large clusters that combine many source systems without clear shared fingerprint evidence.
- Sharp drop in exact duplicate detections while raw ingestion volume remains stable.
- High percentage of `manual_review` recommendations caused by low evidence coverage.
- Similarity records missing method version, comparison level or evidence feature lists.
- Repeated downstream rejections because clusters include records from unrelated lineage chains.
