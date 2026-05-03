# Technical Schema — Validation Data Bridge

Motor ID: motor_018

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Conectar datos estructurados del framework con evidencia local, medición y datos de sitio.
why_it_exists:  La verificación necesita anclarse al sistema completo de Fase 1.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    validation_data_set, bridge_manifest, evidentiary_record
key_objects:    ValidationDataSet, BridgeRecord, EvidentiaryLink
what_not_to_do: No puede ser sustituido por datos sintéticos. No produce field_evidence. Solo estructura datos reales para validación.
design_notes:   Produce evidencia de nivel validation_data (no synthetic_support). Requiere pipeline completo de Fase 1.

This file defines the closed technical schema for motor_018.
-->

## entities
- ValidationDataSet
  - Technical type: persisted output aggregate.
  - Stage: schema_technical as the canonical contract; instantiated during implementation and validated during tests.
  - Description: versioned package of real, structured records eligible for validation. It declares scope, evidence level, inclusion policy, source snapshot, included BridgeRecord ids and exclusion summary. It never represents synthetic support and never upgrades data to field evidence.
- BridgeRecord
  - Technical type: persisted atomic record.
  - Stage: schema_technical as the row-level contract; instantiated during implementation and validated during tests.
  - Description: single bridge between one normalized real datum and its registered source, ingestion lineage, identity resolution when available, quality assessment, rights restrictions and validation eligibility status.
- EvidentiaryLink
  - Technical type: persisted provenance link.
  - Stage: schema_technical as the lineage contract; instantiated during implementation and audited during conformance_review.
  - Description: typed link from a BridgeRecord to the upstream artifact that justifies source rights, ingestion lineage, normalization trace, identity resolution or quality assessment.
- BridgeManifest
  - Technical type: persisted audit manifest.
  - Stage: schema_technical as the reconstruction contract; emitted during implementation and reviewed during conformance_review.
  - Description: manifest that lists source snapshots, included records, excluded records, warnings, propagated restrictions and rebuild metadata for the bridge run.
- EvidentiaryRecord
  - Technical type: persisted downstream handoff record.
  - Stage: schema_technical as the output handoff contract; emitted during implementation for consumers such as Verification Bridge.
  - Description: compact declaration that a ValidationDataSet is evidence level validation_data, with scope, lineage links, limits of use and rights restrictions.

## fields
ValidationDataSet:
- validation_data_set_id: string (required) — stable identifier for the dataset produced by motor_018.
- version_id: string (required) — immutable version identifier for this dataset instance.
- created_at: datetime (required) — timestamp when the dataset version was first produced.
- updated_at: datetime (required) — timestamp when this dataset version metadata was last materialized; must equal created_at unless a new version is emitted.
- version_hash: string (required) — deterministic hash over dataset scope, record ids, exclusion summary, source snapshot id and lineage fields.
- evidence_level: enum[`validation_data`] (required) — fixed evidentiary level; no other value is valid for this motor.
- validation_scope: string (required) — declared scope or validation target that the dataset is prepared to support.
- destination_policy_ref: string|null (optional) — declared downstream use policy used to evaluate rights restrictions.
- source_registry_snapshot_id: string (required) — snapshot id from motor_008 used for all source and rights checks.
- bridge_record_ids: list[string] (required) — ordered ids of included BridgeRecord objects; may be empty only when all candidates are excluded and exclusions are fully documented.
- inclusion_criteria: list[string] (required) — machine-readable criteria applied to admit records.
- exclusion_summary: dict[string, integer] (required) — count of excluded records by explicit reason code.
- warning_summary: dict[string, integer] (required) — count of included records with warnings by warning code.
- restriction_refs: list[string] (required) — propagated rights, license, access or redistribution restrictions that apply to the dataset.
- bridge_manifest_id: string (required) — reference to the BridgeManifest that reconstructs included and excluded records.
- evidentiary_record_id: string (required) — reference to the downstream EvidentiaryRecord for this dataset.
- source_ref: string (required) — canonical reference to the source registry snapshot used by the dataset.
- produced_by_motor: enum[`motor_018`] (required) — producing motor id.
- produced_at: datetime (required) — timestamp when motor_018 emitted this object.
- parent_id: string|null (required) — previous validation_data_set_id when this dataset supersedes another version; null for the first version.

BridgeRecord:
- bridge_record_id: string (required) — stable identifier for the bridged datum.
- validation_data_set_id: string (required) — parent ValidationDataSet id.
- version_id: string (required) — immutable version identifier for this record instance.
- created_at: datetime (required) — timestamp when the record version was first produced.
- updated_at: datetime (required) — timestamp when this record version metadata was last materialized; must equal created_at unless a new version is emitted.
- version_hash: string (required) — deterministic hash over upstream ids, validation status, warnings, restrictions and lineage refs.
- source_id: string (required) — source id registered by motor_008.
- rights_profile_id: string (required) — rights profile id from motor_008 that permits the declared validation use.
- access_class: string (required) — access class propagated from source registry.
- ingestion_record_id: string (required) — ingestion record id from motor_004.
- raw_record_ref: string (required) — immutable reference to the raw record behind the ingested datum.
- parsed_record_ref: string|null (optional) — reference to the parsed record when motor_004 produced one.
- normalized_record_id: string (required) — normalized record id from motor_005.
- original_value_ref: string (required) — reference to the original value preserved by motor_005.
- canonical_value_ref: string (required) — reference to the canonical value emitted by motor_005.
- normalization_rule_ref: string (required) — reference to the normalization rule or rule log from motor_005.
- identity_record_id: string|null (optional) — identity record id from motor_006 when identity resolution exists.
- identity_ambiguity_flag: bool (required) — true when the linked identity record is ambiguous; false when absent or resolved.
- quality_record_id: string (required) — quality record id from motor_007.
- fitness_score: decimal|null (optional) — quality fitness score copied from motor_007 when available.
- quality_flags: list[string] (required) — quality flags copied from motor_007 without reinterpretation.
- disqualification_reason: string|null (optional) — disqualification reason copied from motor_007 when the candidate is excluded.
- validation_status: enum[`eligible`, `eligible_with_warning`, `excluded`] (required) — bridge eligibility status after source, lineage, identity, quality and rights checks.
- warning_codes: list[string] (required) — explicit warnings such as identity_ambiguous, low_fitness_score or restricted_rights.
- exclusion_reason: string|null (optional) — explicit exclusion reason when validation_status is excluded.
- evidence_level: enum[`validation_data`] (required) — fixed evidentiary level for accepted bridge records.
- evidentiary_link_ids: list[string] (required) — ids of EvidentiaryLink objects that reconstruct this record.
- restriction_refs: list[string] (required) — rights, license, access or redistribution restrictions propagated from motor_008.
- source_ref: string (required) — canonical upstream source reference used for this record.
- produced_by_motor: enum[`motor_018`] (required) — producing motor id.
- produced_at: datetime (required) — timestamp when motor_018 emitted this object.
- parent_id: string|null (required) — prior bridge_record_id when this record supersedes an earlier version; null for first materialization.

EvidentiaryLink:
- evidentiary_link_id: string (required) — stable identifier for the lineage link.
- bridge_record_id: string (required) — BridgeRecord id that owns this link.
- version_id: string (required) — immutable version identifier for this link instance.
- created_at: datetime (required) — timestamp when the link version was first produced.
- updated_at: datetime (required) — timestamp when this link version metadata was last materialized; must equal created_at unless a new version is emitted.
- version_hash: string (required) — deterministic hash over bridge_record_id, upstream artifact ref, link type, restrictions and evidence level.
- upstream_motor_id: enum[`motor_004`, `motor_005`, `motor_006`, `motor_007`, `motor_008`] (required) — upstream motor that produced or governs the linked artifact.
- upstream_artifact_ref: string (required) — stable id or reference to the upstream artifact.
- link_type: enum[`source_rights`, `ingestion_lineage`, `normalization_trace`, `identity_resolution`, `quality_assessment`] (required) — reason this link exists.
- evidence_level: enum[`validation_data`] (required) — fixed evidentiary level carried by the link.
- restriction_refs: list[string] (required) — restrictions that apply to this upstream artifact.
- lineage_hash: string (required) — deterministic hash of the upstream artifact reference and link metadata used for rebuild checks.
- source_ref: string (required) — canonical source or upstream artifact reference.
- produced_by_motor: enum[`motor_018`] (required) — producing motor id.
- produced_at: datetime (required) — timestamp when motor_018 emitted this object.
- parent_id: string|null (required) — prior evidentiary_link_id when this link supersedes an earlier version; null for first materialization.

BridgeManifest:
- bridge_manifest_id: string (required) — stable identifier for the audit manifest.
- validation_data_set_id: string (required) — dataset reconstructed by this manifest.
- version_id: string (required) — immutable version identifier for this manifest instance.
- created_at: datetime (required) — timestamp when the manifest version was first produced.
- updated_at: datetime (required) — timestamp when this manifest version metadata was last materialized; must equal created_at unless a new version is emitted.
- version_hash: string (required) — deterministic hash over source snapshots, included ids, excluded refs, warnings, restrictions and rebuild inputs.
- source_registry_snapshot_id: string (required) — snapshot id from motor_008 used during bridge construction.
- source_ids: list[string] (required) — source ids observed in accepted and excluded candidates.
- included_record_ids: list[string] (required) — BridgeRecord ids included in the ValidationDataSet.
- excluded_record_refs: list[string] (required) — candidate refs excluded from the dataset.
- exclusion_reasons: dict[string, string] (required) — mapping from excluded_record_ref to explicit exclusion code.
- warning_reasons: dict[string, list[string]] (required) — mapping from BridgeRecord id to warning codes.
- restriction_refs: list[string] (required) — all propagated rights, access, license or redistribution restrictions.
- rebuild_inputs: dict[string, list[string]] (required) — upstream ids grouped by source_registry, ingestion_records, normalized_records, identity_records and quality_records.
- source_ref: string (required) — canonical reference to the source registry snapshot and candidate set.
- produced_by_motor: enum[`motor_018`] (required) — producing motor id.
- produced_at: datetime (required) — timestamp when motor_018 emitted this object.
- parent_id: string|null (required) — prior bridge_manifest_id when this manifest supersedes another version; null for first materialization.

EvidentiaryRecord:
- evidentiary_record_id: string (required) — stable identifier for downstream handoff.
- validation_data_set_id: string (required) — dataset being declared as validation_data.
- bridge_manifest_id: string (required) — manifest that reconstructs the evidentiary record.
- version_id: string (required) — immutable version identifier for this evidentiary record instance.
- created_at: datetime (required) — timestamp when the evidentiary record version was first produced.
- updated_at: datetime (required) — timestamp when this evidentiary record version metadata was last materialized; must equal created_at unless a new version is emitted.
- version_hash: string (required) — deterministic hash over dataset id, link ids, evidence level, scope and limits of use.
- evidence_level: enum[`validation_data`] (required) — fixed evidentiary level for all downstream consumers.
- validation_scope: string (required) — declared validation target or data scope.
- evidentiary_link_ids: list[string] (required) — links that reconstruct source, ingestion, normalization, identity and quality lineage.
- limits_of_use: list[string] (required) — explicit limits, including that this record is not field evidence and cannot close claims alone.
- restriction_refs: list[string] (required) — rights, access, license or redistribution restrictions inherited from the dataset.
- source_ref: string (required) — canonical reference to the dataset and source registry snapshot.
- produced_by_motor: enum[`motor_018`] (required) — producing motor id.
- produced_at: datetime (required) — timestamp when motor_018 emitted this object.
- parent_id: string|null (required) — prior evidentiary_record_id when this handoff supersedes another version; null for first materialization.

## relationships
- ValidationDataSet.bridge_record_ids references BridgeRecord.bridge_record_id with cardinality 0..n. Empty lists are valid only when BridgeManifest.exclusion_reasons documents every rejected candidate.
- ValidationDataSet.bridge_manifest_id references BridgeManifest.bridge_manifest_id with cardinality 1..1.
- ValidationDataSet.evidentiary_record_id references EvidentiaryRecord.evidentiary_record_id with cardinality 1..1.
- BridgeRecord.validation_data_set_id references ValidationDataSet.validation_data_set_id with cardinality n..1.
- BridgeRecord.source_id references motor_008 SourceRegistrySnapshot.source_id with cardinality n..1 and requires a rights profile that permits declared validation use.
- BridgeRecord.ingestion_record_id references motor_004 IngestionRecord.ingestion_record_id with cardinality n..1.
- BridgeRecord.normalized_record_id references motor_005 NormalizedRecord.normalized_record_id with cardinality n..1.
- BridgeRecord.identity_record_id references motor_006 IdentityRecord.identity_record_id with cardinality n..0..1; ambiguity is preserved through identity_ambiguity_flag.
- BridgeRecord.quality_record_id references motor_007 QualityRecord.quality_record_id with cardinality n..1.
- BridgeRecord.evidentiary_link_ids references EvidentiaryLink.evidentiary_link_id with cardinality 1..n for included records and 0..n for excluded records retained only in the manifest.
- EvidentiaryLink.bridge_record_id references BridgeRecord.bridge_record_id with cardinality n..1.
- EvidentiaryLink.upstream_artifact_ref references exactly one upstream artifact from motor_004, motor_005, motor_006, motor_007 or motor_008 according to upstream_motor_id and link_type.
- BridgeManifest.validation_data_set_id references ValidationDataSet.validation_data_set_id with cardinality 1..1.
- BridgeManifest.included_record_ids references BridgeRecord.bridge_record_id and must match ValidationDataSet.bridge_record_ids exactly.
- BridgeManifest.excluded_record_refs references rejected candidate ids from upstream records or temporary candidate refs; excluded candidates must not appear in ValidationDataSet.bridge_record_ids.
- EvidentiaryRecord.validation_data_set_id references ValidationDataSet.validation_data_set_id with cardinality 1..1.
- EvidentiaryRecord.bridge_manifest_id references BridgeManifest.bridge_manifest_id with cardinality 1..1.
- EvidentiaryRecord.evidentiary_link_ids references EvidentiaryLink.evidentiary_link_id and must cover source_rights, ingestion_lineage, normalization_trace, quality_assessment and identity_resolution when identity_record_id exists.

## identifiers
- ValidationDataSet canonical id: validation_data_set_id. Format: `motor_018:validation_data_set:{validation_scope}:{version_hash_prefix}`.
- BridgeRecord canonical id: bridge_record_id. Format: `motor_018:bridge_record:{normalized_record_id}:{version_hash_prefix}`.
- EvidentiaryLink canonical id: evidentiary_link_id. Format: `motor_018:evidentiary_link:{bridge_record_id}:{link_type}:{version_hash_prefix}`.
- BridgeManifest canonical id: bridge_manifest_id. Format: `motor_018:bridge_manifest:{validation_data_set_id}:{version_hash_prefix}`.
- EvidentiaryRecord canonical id: evidentiary_record_id. Format: `motor_018:evidentiary_record:{validation_data_set_id}:{version_hash_prefix}`.
- Upstream references remain owned by their source motors and are not rewritten: source_id by motor_008, ingestion_record_id by motor_004, normalized_record_id by motor_005, identity_record_id by motor_006 and quality_record_id by motor_007.
- New ids are emitted only when the deterministic content hash changes; motor_018 never mutates an existing id in place.

## versioning
- Every persisted entity has version_id, created_at, updated_at and version_hash.
- version_id is required and immutable for each materialized object version. Recommended format: `motor_018:v:{entity_name}:{version_hash_prefix}`.
- created_at is required and records the first materialization timestamp for the object version.
- updated_at is required and records the latest materialization timestamp for that exact version. If content changes, a new version_id and version_hash are required instead of silent mutation.
- version_hash is required and must be computed deterministically from canonicalized entity content excluding volatile runtime fields.
- ValidationDataSet.version_hash includes validation_scope, source_registry_snapshot_id, ordered bridge_record_ids, inclusion_criteria, exclusion_summary, warning_summary, restriction_refs, source_ref, parent_id and produced_by_motor.
- BridgeRecord.version_hash includes all upstream ids, rights_profile_id, access_class, value refs, identity_ambiguity_flag, quality fields, validation_status, warning_codes, exclusion_reason, restriction_refs and lineage refs.
- EvidentiaryLink.version_hash includes bridge_record_id, upstream_motor_id, upstream_artifact_ref, link_type, evidence_level, restriction_refs and lineage_hash.
- BridgeManifest.version_hash includes validation_data_set_id, source ids, included ids, excluded refs, exclusion reasons, warning reasons, restriction refs and rebuild inputs.
- EvidentiaryRecord.version_hash includes validation_data_set_id, bridge_manifest_id, evidence_level, validation_scope, evidentiary_link_ids, limits_of_use and restriction_refs.
- parent_id links a newer object version to the prior canonical id when the object supersedes an earlier version.

## lineage
- Every persisted entity has source_ref, produced_by_motor, produced_at and parent_id.
- source_ref is required and points to the canonical upstream source context used to create the object: source registry snapshot for datasets and manifests, upstream artifact ref for links, and dataset plus source snapshot for downstream evidentiary records.
- produced_by_motor is required and must be exactly `motor_018` for all entities produced by this motor.
- produced_at is required and records the emission time of the object from motor_018.
- parent_id is required as a nullable field. It is null for the first version and stores the prior canonical id when a new version supersedes an earlier object.
- BridgeRecord lineage must reconstruct to source_id, rights_profile_id, ingestion_record_id, raw_record_ref, normalized_record_id, original_value_ref, canonical_value_ref, quality_record_id and identity_record_id when present.
- EvidentiaryLink lineage must identify the upstream motor and artifact reference for each link_type, so a reviewer can verify source rights, ingestion lineage, normalization trace, identity resolution and quality assessment independently.
- BridgeManifest lineage must include rebuild_inputs grouped by upstream motor, included_record_ids, excluded_record_refs and restriction_refs so the bridge can be reconstructed without reading unregistered sources or mutating upstream records.
- EvidentiaryRecord lineage must preserve validation_data_set_id, bridge_manifest_id, evidentiary_link_ids, evidence_level and limits_of_use for downstream consumers.
- Lineage fields are copied or referenced from upstream artifacts; motor_018 does not normalize, resolve identity, recalculate quality or alter rights metadata.
