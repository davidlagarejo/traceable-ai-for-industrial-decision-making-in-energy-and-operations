# Functional Contract — Duplicate / Similarity Control Engine

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

## inputs
- `parsed_records`: collection of parsed record objects — produced by `motor_004`; each item must expose `record_id`, `source_id`, parsed field payload, raw content reference or raw fingerprint when available, provenance metadata and parser version.
- `normalized_records`: collection of normalized record objects — produced by `motor_005`; each item must expose `normalized_record_id`, upstream `record_id`, normalized field payload, normalization version and lineage reference.
- `version_records`: collection of version tracking objects — produced by `motor_002`; each item must expose `version_id`, `object_ref`, `lineage_id`, predecessor or successor references when known, content fingerprint and version timestamp or sequence.

## outputs
- `duplicate_cluster`: collection of `DuplicateCluster` objects — consumed as deduplication evidence by downstream curation and data assembly consumers, especially `motor_011`.
- `similarity_score`: collection of `SimilarityRecord` objects — audit trail for exact and near-duplicate comparisons; consumed by any downstream stage that needs explainable duplicate evidence.
- `dedup_recommendation`: collection of `DeduplicationDecision` objects — non-destructive recommendation set for downstream suppression, review or retention logic.

## limits
- The motor does not accept records without stable record identifiers and traceable provenance or lineage references.
- The motor does not accept free-text prompts, analyst notes or entity-only records as duplicate evidence unless they are attached to parsed or normalized record objects.
- The motor does not produce entity identity matches, canonical entity identifiers, quality scores, confidence in truth, source reliability ratings or final curation decisions.
- The motor never deletes, merges, rewrites or normalizes source records; every output is advisory and reference-based.
- The motor never treats version succession alone as duplication; version context is used to distinguish expected changes from repeated content.

## validations
- Before processing, every input item must have a non-empty stable identifier, source or object reference, and provenance or lineage metadata.
- Before processing, each `normalized_record` must reference a parsed upstream `record_id` or carry an explicit lineage bridge to the parsed source.
- Before processing, every `version_record.object_ref` used for comparison must resolve to an input record or be explicitly marked as external version context.
- Similarity scores must be numeric values in the closed interval `[0.0, 1.0]`; exact fingerprint matches must emit `1.0`.
- Each emitted `DuplicateCluster` must contain at least two unique member record references and at least one evidence reference.
- Each emitted `SimilarityRecord` must identify the two compared record references, the comparison level, the method version and the evidence features used.
- Each emitted `DeduplicationDecision` must reference an existing `DuplicateCluster`, declare a recommendation enum and preserve a rationale reference without mutating the source records.
