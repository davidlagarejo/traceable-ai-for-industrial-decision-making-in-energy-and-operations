# Failure Modes Spec — Duplicate / Similarity Control Engine

Motor ID: motor_010

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar duplicados exactos y near-duplicates a nivel raw, parsed y otros niveles.
why_it_exists:  No es lo mismo que identity resolution; controla repetición documental y dataset inflation.
key_inputs:     parsed_records (motor_004), normalized_records (motor_005), version_records (motor_002)
key_outputs:    duplicate_cluster, similarity_score, dedup_recommendation
key_objects:    DuplicateCluster, SimilarityRecord, DeduplicationDecision
what_not_to_do: No resuelve identidad de entidades. No evalúa calidad. Solo detecta repetición.
design_notes:   Opera antes de resolución de identidad. Controla repetición documental, no semántica.

Failure-mode specification completed for Gate 4 validation.
-->

## failure_modes_list
- `FINGERPRINT_COLLISION_OR_TRUNCATION`: a raw or canonical fingerprint is missing entropy, truncated, reused across incompatible payloads or generated from only partial content → unrelated records receive `similarity_score = 1.0`, clusters grow across unrelated sources, and downstream consumers see false `suppress_duplicate` recommendations → reject malformed fingerprint evidence, require evidence features to identify the exact fingerprint source, recompute affected `SimilarityRecord` and `DuplicateCluster` objects with a corrected `method_version`, and preserve prior object versions through `parent_id`.
- `VERSION_SUCCESSION_COLLAPSE`: `version_records` are absent, not resolved against the compared record refs, or ignored during recommendation construction → legitimate changed versions are clustered as duplicates and newer records become suppression targets → fail closed with `DUPLICATE_INPUT_INVALID_VERSION_CONTEXT` when version context is inconsistent, emit only reviewable evidence when successor status is unresolved, and require `version_context_refs` on every similarity and cluster object before producing a `DeduplicationDecision`.
- `NORMALIZATION_OVERCOMPRESSION`: normalized signatures collapse distinguishing fields such as document date, permit id, source document id or changed content markers → distinct documents that share entity-like fields cross the near-duplicate threshold and create false positive normalized clusters → keep comparison evidence split by `comparison_level`, require evidence features to list the normalized fields used, route boundary cases to `manual_review`, and do not cluster solely from facility or entity overlap.
- `THRESHOLD_PROFILE_DRIFT`: near-duplicate thresholds, scoring weights or manual-review bands change without a new `threshold_profile_ref` or `method_version` → the same input produces different `SimilarityRecord.similarity_score`, `similarity_kind`, `DuplicateCluster.cluster_id` or `DeduplicationDecision.decision_id` across runs → treat threshold profiles as immutable for a run, include profile references in similarity, cluster and decision hashes, and regenerate superseding output versions when the profile legitimately changes.
- `INPUT_ORDER_NONDETERMINISM`: comparisons, cluster assembly or identifier hashing depend on incoming list order rather than canonical sorted references → repeated runs over the same records emit different ids, member order, fingerprints or recommendations → canonicalize pair ordering, sort cluster members and target refs before hashing, and compare rerun outputs against stable id expectations before accepting the run.
- `TRACEABILITY_GAP_ACCEPTANCE`: parsed, normalized or version records with missing identifiers, missing provenance, broken lineage bridges or unresolved `object_ref` values enter comparison → emitted clusters cannot be rebuilt from source records and conformance review cannot verify evidence → reject the candidate set with a structured traceability error, emit no advisory decision for the malformed set, and require `source_ref`, `version_context_refs` and `produced_by_motor = "motor_010"` on all outputs.
- `IDENTITY_RESOLUTION_LEAKAGE`: entity names, addresses, analyst labels or external identity objects are treated as duplicate evidence → records that describe the same real-world entity but represent different documents are clustered incorrectly → block identity-only payloads with `DUPLICATE_INPUT_UNSUPPORTED_PAYLOAD`, require document-level raw, parsed or normalized evidence, and keep identity resolution evidence outside `SimilarityRecord.evidence_features`.
- `ADVISORY_OUTPUT_MUTATION`: a deduplication recommendation is applied as an in-place delete, merge, overwrite, normalization repair or final curation action inside this motor → upstream `parsed_records`, `normalized_records` or `version_records` lose provenance and cannot be audited against original inputs → enforce `decision_status = "recommended_only"`, keep all outputs reference-based, and route any actual suppression or curation action to downstream consumers outside motor_010.

## anti_patterns
- Coupling cluster creation directly to entity identity resolution, facility matching or source-quality scoring instead of document-level raw, parsed or normalized duplicate evidence.
- Treating `DeduplicationDecision.recommendation = "suppress_duplicate"` as permission for this motor to delete, merge, rewrite or normalize upstream records.
- Generating `cluster_id`, `similarity_id`, `decision_id` or `version_hash` from unsorted input order, runtime timestamps, local filesystem order or non-canonical JSON serialization.
- Changing near-duplicate scoring rules or thresholds during a run without updating `method_version` and `threshold_profile_ref`.
- Emitting clusters without `SimilarityRecord` evidence references, or emitting decisions without `rationale_refs` tied to the cluster evidence.
- Accepting normalized records that do not point to an included parsed record or an explicit lineage bridge.
- Collapsing raw, parsed, normalized and cross-level comparison evidence into one opaque score that cannot explain which representation triggered the match.
- Using language-model judgment, analyst notes or free-text prompts as the primary duplicate classifier.
- Copying full source payloads into output objects when stable record refs, fingerprints and evidence refs are sufficient for audit.
- Expanding this motor into ingestion, parsing, normalization, versioning, identity resolution, quality scoring or final curation responsibilities.

## degradation_signals
- `duplicate_cluster_rate` or average `member_record_refs` per cluster rises sharply after a parser, normalization or threshold profile version change.
- High count of clusters with `cluster_kind = "near_duplicate"` but missing or low-cardinality `evidence_features`.
- Any emitted `SimilarityRecord` has missing `method_version`, missing `comparison_level`, empty `version_context_refs`, empty `source_ref`, or `similarity_score` outside `[0.0, 1.0]`.
- Repeated `DUPLICATE_INPUT_BROKEN_REFERENCE`, `DUPLICATE_INPUT_INVALID_VERSION_CONTEXT` or `DUPLICATE_INPUT_MISSING_TRACEABILITY` errors from the same upstream source.
- Rerunning the same accepted input and method versions produces different `SimilarityRecord.similarity_id`, `DuplicateCluster.cluster_id`, `cluster_fingerprint`, `member_record_refs` or `DeduplicationDecision.decision_id`.
- Manual review recommendations dominate exact duplicate and clear near-duplicate recommendations, indicating sparse evidence, unstable thresholds or over-broad candidate generation.
- Clusters span many unrelated `source_id` or lineage groups while sharing only entity-like fields and no raw fingerprint or parsed field signature evidence.
- Exact duplicate counts drop unexpectedly while raw ingestion volume and raw fingerprint coverage remain stable.
- Downstream consumers reject recommendations because `target_record_refs` are not a subset of the referenced cluster members or because rationale evidence is missing.
- Logs show fallback to opaque similarity text, prompt-based classification or analyst labels instead of declared deterministic comparison methods.

## expensive_errors
- False suppression of legitimate changed versions is expensive because downstream datasets may silently lose newer records and later audits must reconstruct version chains from upstream lineage. Prevent it by requiring resolvable `version_records`, preserving `version_context_refs`, and emitting `keep_all` or `manual_review` when version succession is unresolved.
- False positive clusters caused by normalization overcompression are expensive because one bad normalized signature can contaminate many clusters and recommendations across sources. Prevent it by recording comparison level, evidence features, threshold profile and method version on every similarity record, and by refusing to use entity overlap alone as duplicate evidence.
- Nondeterministic identifiers are expensive because downstream references to clusters, decisions and audit records break between reruns even when the input did not change. Prevent it by canonical sorting of pairs, members and target refs before hashing, and by deriving ids only from stable content and method metadata.
- Missing provenance or lineage in accepted outputs is expensive because no later conformance review can prove why a record was suppressed or retained. Prevent it by failing closed on missing traceability and requiring `source_ref`, `produced_by_motor`, `produced_at`, `parent_id` and version hashes on all output entities.
- Applying advisory recommendations as mutations is expensive because it destroys the original record state and mixes motor_010 with downstream curation responsibility. Prevent it by keeping decisions `recommended_only`, never writing to upstream records, and exposing only reference-based outputs.
- Threshold drift without versioning is expensive because historical similarity scores cannot be reproduced and prior cluster decisions become incomparable. Prevent it by treating scoring rules and thresholds as versioned configuration, embedding `method_version` and `threshold_profile_ref` in output objects, and producing superseding versions rather than rewriting old ones.
- Accepting unsupported identity-only payloads is expensive because it turns document repetition control into identity resolution and creates clusters that cannot be validated by duplicate evidence. Prevent it by rejecting analyst notes, prompts and entity labels unless attached to parsed or normalized record objects with provenance.
