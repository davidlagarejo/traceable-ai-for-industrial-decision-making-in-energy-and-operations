# Design Done Criteria — Duplicate / Similarity Control Engine

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

## criteria
- The seven documentation-base artifacts exist and contain filled sections for purpose, contract, conceptual schema, operational rules, acceptance tests, failure modes and design completion criteria.
- `functional_contract.md` lists `parsed_records`, `normalized_records` and `version_records` as inputs and lists `duplicate_cluster`, `similarity_score` and `dedup_recommendation` as outputs.
- `conceptual_schema.md` defines `DuplicateCluster`, `SimilarityRecord` and `DeduplicationDecision` with required fields and relationships.
- `operational_rules.md` explicitly requires deterministic comparison, stable scoring, version-context checks and non-destructive recommendations.
- `acceptance_tests.md` includes a concrete happy path, sparse and version-related edge cases, and explicit rejection signals.
- `failure_modes.md` documents fingerprint, versioning, normalization and threshold degradation risks with observable signals.
- The design boundaries explicitly exclude entity identity resolution, quality evaluation, source mutation and final curation decisions.
