# Acceptance Tests — Library Curation Engine

Motor ID: motor_011

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
why_it_exists:  Evita que cada fase arme su propia pseudo-biblioteca local.
key_inputs:     quality_records (motor_007), identity_records (motor_006), dedup_records (motor_010)
key_outputs:    library_object, curated_bundle, library_version
key_objects:    LibraryObject, CuratedBundle, LibraryVersion
what_not_to_do: No ingesta datos nuevos. No evalúa calidad. Solo selecciona y organiza objetos aptos como biblioteca.
design_notes:   Requiere el pipeline completo de Fase 1.

All open placeholders in this file have been resolved with concrete documentation.
-->

## happy_path
Input:
- `quality_records` contains `qr-100` with `subject_ref = nr-100`, `evaluation_status = pass`, `fitness_score.total_score = 0.94`, no blocking flags and `phase_contract_ref = pc-phase1-context`.
- `identity_records` contains `ir-100` with `evaluated_record_ids = [nr-100]`, `decision = same_entity`, `confidence_band = high`, `evidence_refs = [cm-44]` and lineage reference `lin-100`.
- `dedup_records` contains no cluster that suppresses `nr-100`.
- `curation_policy` declares `curation_run_id = cur-2026-04-17-a`, `bundle_scope = phase_1_context_library`, `curation_rule_version = libcur-1.0.0`, accepted statuses `[pass, conditional_pass]` and blocking flag codes `[missing_lineage, missing_provenance, not_fit_for_phase]`.

Action: the motor validates the candidate evidence, promotes `nr-100` into a `LibraryObject`, places it in a `CuratedBundle` for `phase_1_context_library` and emits a `LibraryVersion` for both the object and the bundle.

Expected output:
- One `library_object` with non-empty `library_object_id`, `source_object_ref = nr-100`, `quality_record_ref = qr-100`, `identity_record_ref = ir-100`, `curation_status = included`, `curation_rule_version = libcur-1.0.0`, provenance refs and lineage refs.
- One `curated_bundle` with `bundle_scope = phase_1_context_library`, `member_library_object_refs` containing the emitted library object and stable membership fingerprint.
- At least one `library_version` whose `versioned_object_ref` resolves to the emitted object or bundle and whose `content_fingerprint` is non-empty.

## edge_cases
- Empty eligible set: when all input lists are valid but every candidate is rejected by quality, identity or duplicate rules, the motor emits no `LibraryObject`, emits a `CuratedBundle` with empty `member_library_object_refs`, records every candidate in `excluded_candidate_refs` with a structured reason and emits a bundle `LibraryVersion` for the empty but valid scope.
- Duplicate representative selection: when `dedup_records` contains cluster `dc-20` with members `[nr-100, nr-101]` and a `DeduplicationDecision` recommending `suppress_duplicate` for `nr-101`, the motor includes only the eligible representative for the cluster in bundle membership, records `nr-101` as excluded duplicate evidence and preserves all cluster and rationale references.
- Allowed warning inclusion: when a candidate has `evaluation_status = conditional_pass` with only policy-allowed warning flag `restricted_use`, the motor may emit a `LibraryObject` with `curation_status = included_with_warning` and must copy the warning reference into the object metadata.
- Stable ordering: when the same valid candidates arrive in different input order, the emitted bundle membership and content fingerprint remain identical because ordering is derived from stable identifiers.

## rejection_criteria
- Missing quality evidence: if candidate `nr-200` has no matching `quality_record.subject_ref`, reject that candidate with error signal `CURATION_QUALITY_REF_MISSING` and emit no `LibraryObject` for `nr-200`.
- Disqualified quality: if `qr-201.evaluation_status = disqualified` or `qr-201.disqualification_reason` is non-null, reject the candidate with error signal `CURATION_QUALITY_NOT_ELIGIBLE`.
- Missing identity evidence: if candidate `nr-300` has no matching `IdentityRecord` or the matching record lacks `identity_record_id`, reject with `CURATION_IDENTITY_REF_MISSING`.
- Blocking identity ambiguity: if `ir-301.decision = ambiguous` and the active policy requires resolved identity, reject with `CURATION_IDENTITY_AMBIGUOUS`.
- Invalid duplicate reference: if a deduplication recommendation references a cluster or record not present in the candidate set or supplied duplicate evidence, reject the run with `CURATION_DEDUP_REF_INVALID`.
