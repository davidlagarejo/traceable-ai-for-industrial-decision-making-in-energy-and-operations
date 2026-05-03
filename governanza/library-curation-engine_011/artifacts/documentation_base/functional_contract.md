# Functional Contract — Library Curation Engine

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

## inputs
- `quality_records`: list[QualityRecord-like dict] — source: `motor_007`; each item provides `quality_record_id`, `subject_ref`, `evaluation_status`, `fitness_score`, `quality_flags`, optional `disqualification_reason`, `phase_contract_ref`, `evaluation_run_id` and scoring rule version for a candidate object.
- `identity_records`: list[IdentityRecord-like dict] — source: `motor_006`; each item provides `identity_record_id`, evaluated record references, identity decision, confidence band, entity cluster reference when available, evidence references, rule version and lineage references.
- `dedup_records`: list[DuplicateCluster | SimilarityRecord | DeduplicationDecision-like dict] — source: `motor_010`; each item provides duplicate cluster membership, similarity evidence, non-destructive deduplication recommendation, method version and rationale references.
- `curation_policy`: dict — origin: orchestrator or configured run context; declares `curation_run_id`, accepted quality statuses, blocking flag codes, duplicate handling policy, bundle scope, curation rule version and publication timestamp.

## outputs
- `library_object`: LibraryObject dict — destination: framework library registry, `motor_012`, `motor_013` and other downstream consumers; represents one reusable object with upstream references, eligibility evidence, curation status, provenance, lineage and rule version.
- `curated_bundle`: CuratedBundle dict — destination: downstream phase assembly, public data preparation and inference activation; represents a scoped collection of `library_object` references with membership rationale and bundle-level metadata.
- `library_version`: LibraryVersion dict — destination: version registry, propagation consumers and audit trail; records the immutable version identity, content fingerprint, prior version reference, publication event and rebuild context for a library object or bundle.
- `curation_rejection`: dict — destination: audit trail and governance review; records a candidate reference that was not promoted to a library object, with error code, blocking evidence and source record references.

## limits
- The motor never accepts raw records, parsed-only records, normalized records without quality evidence, free-text notes or analyst-selected objects that lack upstream `quality_records`, `identity_records` and duplicate-control evidence.
- The motor never accepts candidate objects whose `evaluation_status` is `disqualified` or `rejected`, or whose quality flags include a blocking code under the active `curation_policy`.
- The motor never accepts identity evidence that is missing, contradictory to the candidate reference or marked with a blocking ambiguity state under the active policy.
- The motor never accepts deduplication references that point to unknown candidate records or clusters with fewer than two distinct members.
- The motor never produces new source data, normalized data, quality scores, identity decisions, duplicate scores, evidence of field validation, inference records or reports.
- The motor never mutates, deletes, merges, repairs or overwrites upstream objects; outputs contain references and curation metadata only.

## validations
- Reject the run if `curation_policy.curation_run_id`, `curation_policy.curation_rule_version` or `curation_policy.bundle_scope` is missing or empty.
- Reject any candidate without exactly one matching `quality_record.subject_ref` and at least one matching identity reference for the same upstream record or entity cluster.
- Reject any candidate whose quality record lacks `quality_record_id`, `subject_ref`, `evaluation_status`, `fitness_score`, `phase_contract_ref` or `evaluation_run_id`.
- Reject any candidate with `evaluation_status` outside the policy's accepted set; by default only `pass` and explicitly allowed `conditional_pass` records are eligible.
- Reject any candidate whose `quality_flags` contain a blocking flag listed by the active curation policy.
- Reject any candidate whose identity record lacks `identity_record_id`, `decision`, `confidence_band`, `evidence_refs` or `rule_version`.
- Reject any candidate whose identity decision is incompatible with library reuse, including unresolved ambiguity when the policy requires resolved identity.
- Validate all referenced duplicate clusters and deduplication recommendations before bundle construction; recommendations may suppress membership but may not delete upstream records.
- Before emitting `library_object`, ensure `library_object_id`, `source_object_ref`, `quality_record_ref`, `identity_record_ref`, `curation_status`, `curation_rule_version`, `provenance_refs` and `lineage_refs` are non-empty.
- Before emitting `curated_bundle`, ensure every member reference resolves to an emitted `library_object` and bundle membership is stable under input ordering.
- Before emitting `library_version`, ensure `library_version_id`, `versioned_object_ref`, `content_fingerprint`, `created_at`, `curation_rule_version` and `lineage_refs` are non-empty.
