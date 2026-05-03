# Test Spec — Duplicate / Similarity Control Engine

Motor ID: motor_010

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar duplicados exactos y near-duplicates a nivel raw, parsed y otros niveles.
why_it_exists:  No es lo mismo que identity resolution; controla repetición documental y dataset inflation.
key_inputs:     parsed_records (motor_004), normalized_records (motor_005), version_records (motor_002)
key_outputs:    duplicate_cluster, similarity_score, dedup_recommendation
key_objects:    DuplicateCluster, SimilarityRecord, DeduplicationDecision
what_not_to_do: No resuelve identidad de entidades. No evalúa calidad. Solo detecta repetición.
design_notes:   Opera antes de resolución de identidad. Controla repetición documental, no semántica.

This test specification refines the documentation-base acceptance tests into concrete gate-ready scenarios for the tests stage.
-->

## happy_path
Scenario: exact raw duplicate plus normalized near-duplicate.

Input:
- `parsed_records` contains three records:
  - `rec_A`: `record_id = "parsed:rec_A"`, `source_id = "source:alpha"`, `raw_fingerprint = "sha256:111aaa"`, `parsed_fields = {"facility_name": "Alpha Plant", "state": "TX", "permit_id": "44"}`, `provenance = {"ingestion_run_id": "ing:2026-04-01", "parser_version": "parser-1.4.0"}`.
  - `rec_B`: `record_id = "parsed:rec_B"`, `source_id = "source:alpha_mirror"`, `raw_fingerprint = "sha256:111aaa"`, `parsed_fields = {"facility_name": "Alpha Plant", "state": "TX", "permit_id": "44"}`, `provenance = {"ingestion_run_id": "ing:2026-04-02", "parser_version": "parser-1.4.0"}`.
  - `rec_C`: `record_id = "parsed:rec_C"`, `source_id = "source:beta"`, `raw_fingerprint = "sha256:222bbb"`, `parsed_fields = {"facility_name": "Alpha Plant Inc.", "state": "TX", "permit_id": "44"}`, `provenance = {"ingestion_run_id": "ing:2026-04-03", "parser_version": "parser-1.4.0"}`.
- `normalized_records` contains:
  - `norm_A`: `normalized_record_id = "norm:rec_A"`, `record_id = "parsed:rec_A"`, `normalized_signature = "facility=alpha plant|state=TX|permit=44"`, `normalization_version = "norm-2.1.0"`, `lineage_ref = "lineage:rec_A"`.
  - `norm_B`: `normalized_record_id = "norm:rec_B"`, `record_id = "parsed:rec_B"`, `normalized_signature = "facility=alpha plant|state=TX|permit=44"`, `normalization_version = "norm-2.1.0"`, `lineage_ref = "lineage:rec_B"`.
  - `norm_C`: `normalized_record_id = "norm:rec_C"`, `record_id = "parsed:rec_C"`, `normalized_signature = "facility=alpha plant inc|state=TX|permit=44"`, `normalization_version = "norm-2.1.0"`, `lineage_ref = "lineage:rec_C"`.
- `version_records` contains one context record for each parsed and normalized object with `version_id`, `object_ref`, `lineage_id`, `content_fingerprint`, and no successor relation that would make the records legitimate changed versions.
- `method_version = "dup-sim-1.0.0"`.
- `threshold_profile_ref = "threshold:default:2026-04"`, with near-duplicate acceptance threshold `0.92` and manual-review band `[0.85, 0.92)`.

Expected output:
- At least one `SimilarityRecord` for `parsed:rec_A` versus `parsed:rec_B` has `comparison_level = "raw"`, `similarity_score = 1.0`, `similarity_kind = "exact_duplicate"`, `method_version = "dup-sim-1.0.0"`, and `evidence_features` including `raw_fingerprint`.
- A normalized comparison involving `norm:rec_C` has `comparison_level = "normalized"`, `similarity_kind` in `["near_duplicate", "reviewable_similarity"]`, a numeric `similarity_score` in `[0.0, 1.0]`, and `threshold_profile_ref = "threshold:default:2026-04"`.
- One `DuplicateCluster` includes at least two member references, preserves unique `member_record_refs`, includes `evidence_refs` pointing to emitted `SimilarityRecord.similarity_id` values, declares `produced_by_motor = "motor_010"`, and includes `source_ref` references to the upstream parsed, normalized and version records used as evidence.
- One `DeduplicationDecision` references the emitted cluster, has `decision_status = "recommended_only"`, uses a recommendation enum from `["keep_all", "suppress_duplicate", "manual_review"]`, and does not mutate any parsed, normalized or version input object.

## sparse_case
Scenario: minimal traceable raw duplicate with optional normalized evidence absent.

Input:
- `parsed_records` contains exactly two records:
  - `rec_min_1`: `record_id = "parsed:min_1"`, `source_id = "source:minimal"`, `raw_fingerprint = "sha256:minimal123"`, `parsed_fields = {}`, `provenance = {"ingestion_run_id": "ing:minimal", "parser_version": "parser-1.4.0"}`.
  - `rec_min_2`: `record_id = "parsed:min_2"`, `source_id = "source:minimal_copy"`, `raw_fingerprint = "sha256:minimal123"`, `parsed_fields = {}`, `provenance = {"ingestion_run_id": "ing:minimal-copy", "parser_version": "parser-1.4.0"}`.
- `normalized_records` is an empty list.
- `version_records` contains valid context for both parsed records, with `object_ref` values matching `parsed:min_1` and `parsed:min_2`.
- Optional fields such as `threshold_profile_ref`, normalized signatures and parsed field signatures are absent.

Expected output:
- The motor completes without fatal error because all required identifiers, raw fingerprints, provenance and version context are present.
- The motor emits one raw-level `SimilarityRecord` with `similarity_score = 1.0`, `comparison_level = "raw"`, and `evidence_features = ["raw_fingerprint"]` or an equivalent feature list containing `raw_fingerprint`.
- The motor emits one `DuplicateCluster` with `cluster_kind = "exact_duplicate"`, `match_scope = "raw"`, and two unique `member_record_refs`.
- The motor does not attempt normalized near-duplicate scoring and does not fail because normalized optional evidence is missing.

## malformed_input
Scenario: required traceability and schema fields are missing or typed incorrectly.

Invalid inputs and required rejection behavior:
- If a parsed record lacks `record_id`, or has `record_id = ""`, reject the run with `DUPLICATE_INPUT_MISSING_TRACEABILITY`; no `DuplicateCluster`, `SimilarityRecord` or `DeduplicationDecision` is emitted for that candidate set.
- If a parsed record has `raw_fingerprint` as a list or object instead of a string, reject with `DUPLICATE_INPUT_INVALID_FINGERPRINT_TYPE`; the motor must not coerce the value silently.
- If a `normalized_record` has `record_id = "parsed:missing"` and no explicit lineage bridge to an included parsed record, reject with `DUPLICATE_INPUT_BROKEN_REFERENCE`.
- If a `version_record.object_ref` points to `parsed:rec_A` but its `lineage_id` conflicts with the lineage reference supplied by the input record, reject with `DUPLICATE_INPUT_INVALID_VERSION_CONTEXT`.
- If input consists only of analyst notes, prompts, entity labels or identity-resolution records without parsed or normalized record objects, reject with `DUPLICATE_INPUT_UNSUPPORTED_PAYLOAD`.

Expected output:
- Each rejection is structured, deterministic and specific to the invalid condition.
- The motor preserves all input records unchanged and emits no advisory deduplication recommendation for malformed candidate sets.

## edge_cases
1. Legitimate changed version is not suppressed.
   - Input: `parsed:v1` and `parsed:v2` share `source_id = "source:agency"` but have different `raw_fingerprint` values. `version_records` declares `parsed:v1` as predecessor of `parsed:v2` and the normalized signatures differ in a field that represents changed source content.
   - Correct behavior: the motor emits no `DeduplicationDecision` with `recommendation = "suppress_duplicate"` for `parsed:v2`. It may emit reviewable similarity evidence only if the method rules allow it, and any emitted `SimilarityRecord` must include `version_context_refs` explaining the successor relationship.

2. Same entity but different documents are not clustered by identity similarity.
   - Input: two normalized records contain the same facility name and address but different document fingerprints, dates, permit identifiers and version lineages.
   - Correct behavior: no `DuplicateCluster` is emitted solely from entity overlap. The motor must not use identity-resolution evidence as proof of document duplication.

3. Input order does not change identifiers or membership.
   - Input: the same four valid duplicate candidates are submitted in two opposite orders with the same `method_version` and threshold profile.
   - Correct behavior: `SimilarityRecord.similarity_id`, `DuplicateCluster.cluster_id`, `cluster_fingerprint`, `member_record_refs`, and `DeduplicationDecision.decision_id` are identical across both runs after canonical serialization.

4. Large repeated batch remains a stable cluster.
   - Input: fifty parsed records from five sources share the same raw fingerprint and valid lineage references.
   - Correct behavior: the motor emits a stable cluster with fifty unique `member_record_refs`, evidence references sufficient to rebuild the accepted duplicate edges, and one advisory decision or a deterministic small set of advisory decisions. It must not emit conflicting recommendations for the same cluster.

5. Threshold boundary is deterministic.
   - Input: one normalized comparison scores exactly `0.92` when the near-duplicate threshold is `0.92`, and another scores `0.919999` under the same method version.
   - Correct behavior: the exact-threshold score is classified according to the documented inclusive threshold rule for the profile, while the below-threshold score is either `reviewable_similarity` or excluded from clustering according to the same profile. Scores remain numeric and inside `[0.0, 1.0]`.

## pass_criteria
- All accepted candidate comparisons produce `SimilarityRecord` objects with non-empty `similarity_id`, `left_record_ref`, `right_record_ref`, `comparison_level`, `method_version`, `evidence_features`, `version_context_refs`, `source_ref`, `produced_by_motor = "motor_010"`, and `similarity_score` in `[0.0, 1.0]`.
- Exact raw fingerprint matches emit `similarity_score = 1.0` and `similarity_kind = "exact_duplicate"`.
- Every emitted `DuplicateCluster` has a non-empty `cluster_id`, at least two unique `member_record_refs`, non-empty `evidence_refs`, stable `cluster_fingerprint`, required versioning fields, required lineage fields and `produced_by_motor = "motor_010"`.
- Every emitted `DeduplicationDecision` references an existing `DuplicateCluster.cluster_id`, has `decision_status = "recommended_only"`, uses only the declared recommendation enum, and has `target_record_refs` that are a subset of the referenced cluster's members.
- Re-running the same valid input with the same `method_version` and threshold profile produces the same stable identifiers and equivalent scores, independent of input order.
- No source `parsed_record`, `normalized_record` or `version_record` is deleted, merged, rewritten, normalized or otherwise silently mutated.

## fail_criteria
- The motor accepts a record without stable identifier, provenance, lineage or resolvable version context.
- Any malformed input is silently coerced instead of rejected with the specific structured error code required by `malformed_input`.
- A `similarity_score` is missing, non-numeric, below `0.0` or above `1.0`.
- An exact fingerprint match fails to produce a raw-level `SimilarityRecord` with score `1.0`.
- A `DuplicateCluster` contains fewer than two members, duplicate member references, missing evidence references or references to records absent from the accepted input set.
- A `DeduplicationDecision` points to a nonexistent cluster, targets records outside the cluster, omits rationale references or has a status other than `recommended_only`.
- The motor treats same-entity evidence, source quality, factual correctness or analyst judgment as proof of document duplication.
- The motor deletes, merges, rewrites, normalizes or repairs upstream parsed, normalized or version records.
- The same valid inputs produce different stable identifiers solely because input order changed.
