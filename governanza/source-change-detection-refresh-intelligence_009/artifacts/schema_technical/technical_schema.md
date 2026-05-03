# Technical Schema — Source Change Detection / Refresh Intelligence

Motor ID: motor_009

<!-- MOTOR CONTEXT (read this before using the schema below)

purpose:        Detectar cambios de fuente, metodologia, estructura, disponibilidad y prioridad de recaptura.
why_it_exists:  Sin este motor los datasets quedan stale sin que el sistema lo sepa.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), version_history (motor_002)
key_outputs:    change_detection_event, refresh_priority, staleness_signal
key_objects:    ChangeEvent, RefreshPriority, StalenessRecord
what_not_to_do: No descarga datos. No decide que hacer con cambios. Solo detecta y senaliza.
design_notes:   Depende de motor_008, motor_004, motor_002.

Schema sections below are complete for Gate 2 review.
-->

## entities
- `ChangeEvent`: persisted output entity for one deterministic detected change on a registered source. It represents a difference in availability, methodology, schema, refresh frequency, access state or content fingerprint. Stage: defined in `schema_technical`; produced by `implementation` as `change_detection_event`.
- `RefreshPriority`: persisted output entity for the recapture priority signal derived from one or more ChangeEvent records, a StalenessRecord, or a documented temporal staleness rule. It is an advisory signal only and never an execution order. Stage: defined in `schema_technical`; produced by `implementation` as `refresh_priority`.
- `StalenessRecord`: persisted output entity for the freshness state of one registered source or dataset reference. It records last observation, expected refresh interval, age and trigger condition. Stage: defined in `schema_technical`; produced by `implementation` as `staleness_signal`.

## fields
ChangeEvent:
- record_id: string (required) — immutable storage identifier for this emitted ChangeEvent version; equal to `event_id` unless a storage adapter requires a separate key.
- event_id: string (required) — stable logical identifier for the detected change event.
- source_id: string (required) — registered source identifier from motor_008 `SourceRecord.source_id`.
- change_type: enum[availability, methodology, schema, frequency, access, content_fingerprint] (required) — deterministic category of the observed change.
- detected_at: datetime (required) — timestamp when motor_009 detected the change from accepted inputs.
- severity: enum[info, warning, critical] (required) — deterministic severity assigned by rule, not by narrative judgement.
- previous_ingestion_ref: string|null (required) — prior motor_004 ingestion reference used for comparison; null only when the change is derived solely from version_history.
- current_ingestion_ref: string|null (required) — current motor_004 ingestion reference used for comparison; null only when the change is derived solely from version_history.
- previous_version_ref: string|null (required) — prior motor_002 version_id used for comparison; null only when no version record exists for the previous observation.
- current_version_ref: string|null (required) — current motor_002 version_id used for comparison; null only when the event is based on ingestion evidence without a new version record.
- comparison_basis: dict[string, string|integer|null] (required) — normalized values compared by the rule, such as schema signatures, availability states, access error codes, record counts, content fingerprints, methodology refs and declared refresh interval.
- evidence_refs: list[string] (required) — ingestion_id, version_id, source registry or other accepted input references supporting the event; at least one ingestion or version reference is required.
- lineage_refs: list[string] (required) — lineage references inherited from motor_002 and input records, sufficient to reconstruct the comparison.
- detection_rule_ref: string (required) — deterministic rule identifier that emitted the event.
- version_id: string (required) — technical version identifier for this immutable ChangeEvent output.
- created_at: datetime (required) — timestamp when this ChangeEvent version was first created.
- updated_at: datetime (required) — timestamp when this ChangeEvent version was last updated; for immutable first emission it may equal `created_at`.
- version_hash: string (required) — deterministic hash over canonical event content, evidence references and lineage fields.
- source_ref: string (required) — primary source registry reference or composed input reference anchoring provenance for the event.
- produced_by_motor: string (required) — fixed value `motor_009`.
- produced_at: datetime (required) — timestamp when motor_009 emitted this event.
- parent_id: string|null (required) — previous ChangeEvent.record_id when this event supersedes an earlier emitted event for the same source and change type; null for a first event.

RefreshPriority:
- record_id: string (required) — immutable storage identifier for this emitted RefreshPriority version; equal to `priority_id` unless a storage adapter requires a separate key.
- priority_id: string (required) — stable logical identifier for the priority signal.
- source_id: string (required) — registered source identifier from motor_008 `SourceRecord.source_id`.
- priority_level: enum[none, low, medium, high, urgent] (required) — deterministic priority level for downstream recapture planning.
- priority_reason: string (required) — concise reason produced from the triggering rule and evidence; it is explanatory, not an operational command.
- derived_from_event_ids: list[string] (required) — ChangeEvent.event_id values supporting the priority; empty only when priority is based exclusively on a documented temporal staleness rule.
- staleness_id: string|null (required) — StalenessRecord.staleness_id used in the calculation when present; null when no staleness record contributed.
- rule_ref: string (required) — deterministic priority rule identifier.
- calculated_at: datetime (required) — timestamp when the priority was calculated.
- evidence_refs: list[string] (required) — ChangeEvent ids, ingestion ids, version ids or source registry refs used by the priority calculation.
- version_id: string (required) — technical version identifier for this immutable RefreshPriority output.
- created_at: datetime (required) — timestamp when this RefreshPriority version was first created.
- updated_at: datetime (required) — timestamp when this RefreshPriority version was last updated; for immutable first emission it may equal `created_at`.
- version_hash: string (required) — deterministic hash over canonical priority content, rule reference, evidence and lineage fields.
- source_ref: string (required) — primary ChangeEvent, StalenessRecord or source registry reference anchoring provenance.
- produced_by_motor: string (required) — fixed value `motor_009`.
- produced_at: datetime (required) — timestamp when motor_009 emitted this priority signal.
- parent_id: string|null (required) — previous RefreshPriority.record_id when this signal supersedes a prior priority for the same source; null for a first priority signal.

StalenessRecord:
- record_id: string (required) — immutable storage identifier for this emitted StalenessRecord version; equal to `staleness_id` unless a storage adapter requires a separate key.
- staleness_id: string (required) — stable logical identifier for the freshness or stale-state signal.
- source_id: string (required) — registered source identifier from motor_008 `SourceRecord.source_id`.
- staleness_status: enum[fresh, watch, stale, unknown] (required) — deterministic freshness state for the source or dataset reference.
- last_observed_at: datetime|null (required) — latest accepted ingestion or version observation timestamp; null only when accepted inputs prove that no observation exists.
- expected_refresh_interval: duration|string|null (required) — declared refresh interval from motor_008 or equivalent source registry metadata; null only when the registry explicitly has no interval.
- age_days: integer|null (required) — number of days between `last_observed_at` and `calculated_at`; null only when `last_observed_at` is null.
- triggering_condition: string (required) — deterministic condition that produced the status, such as interval exceeded, access blocked, schema changed or insufficient observation history.
- trigger_event_ids: list[string] (required) — ChangeEvent.event_id values that contributed to the stale-state signal; empty when the signal is purely age-based.
- basis_ingestion_refs: list[string] (required) — motor_004 ingestion references used to compute `last_observed_at`, availability and evidence sufficiency.
- basis_version_refs: list[string] (required) — motor_002 version_id values used to compute or validate freshness state.
- calculated_at: datetime (required) — timestamp when motor_009 calculated the freshness state.
- version_id: string (required) — technical version identifier for this immutable StalenessRecord output.
- created_at: datetime (required) — timestamp when this StalenessRecord version was first created.
- updated_at: datetime (required) — timestamp when this StalenessRecord version was last updated; for immutable first emission it may equal `created_at`.
- version_hash: string (required) — deterministic hash over canonical staleness content, triggering condition, evidence references and lineage fields.
- source_ref: string (required) — primary source registry, ingestion or version reference anchoring provenance.
- produced_by_motor: string (required) — fixed value `motor_009`.
- produced_at: datetime (required) — timestamp when motor_009 emitted this stale-state signal.
- parent_id: string|null (required) — previous StalenessRecord.record_id when this signal supersedes an earlier state for the same source; null for a first staleness signal.

## relationships
- `ChangeEvent.source_id` references motor_008 `SourceRecord.source_id`; the source must exist before any event can be emitted.
- `ChangeEvent.previous_ingestion_ref` and `ChangeEvent.current_ingestion_ref` reference motor_004 ingestion records for the same `source_id` when ingestion evidence is used.
- `ChangeEvent.previous_version_ref` and `ChangeEvent.current_version_ref` reference motor_002 version records for the same source, dataset or object family when version evidence is used.
- `ChangeEvent.evidence_refs` must include at least one motor_004 ingestion id or motor_002 version id; source registry metadata alone is not sufficient to emit a change event.
- `ChangeEvent.lineage_refs` preserve motor_002 lineage references and must not be collapsed into narrative text.
- `RefreshPriority.source_id` references the same motor_008 source key used by supporting ChangeEvent or StalenessRecord objects.
- `RefreshPriority.derived_from_event_ids` references zero or more ChangeEvent.event_id values for the same `source_id`; the list may be empty only for a deterministic age-based priority with documented rule_ref.
- `RefreshPriority.staleness_id` references StalenessRecord.staleness_id for the same `source_id` when staleness contributed to the priority calculation.
- `StalenessRecord.source_id` references motor_008 `SourceRecord.source_id`.
- `StalenessRecord.trigger_event_ids` references ChangeEvent.event_id values for the same `source_id`.
- `StalenessRecord.basis_ingestion_refs` references motor_004 ingestion records used for last-observed and availability calculations.
- `StalenessRecord.basis_version_refs` references motor_002 version records used for version-aware staleness calculation.
- `parent_id` on every persisted entity references a prior record_id of the same entity type only when a newer signal supersedes an older signal; it never points across entity types.
- No relationship authorizes motor_009 to download data, mutate source registry metadata, rewrite ingestion records, rewrite version history, normalize content, deduplicate records or make final operational recapture decisions.

## identifiers
- ChangeEvent storage identifier: `record_id`; canonical logical identifier: `event_id`.
- RefreshPriority storage identifier: `record_id`; canonical logical identifier: `priority_id`.
- StalenessRecord storage identifier: `record_id`; canonical logical identifier: `staleness_id`.
- Recommended deterministic ChangeEvent id composition: `motor_009:{source_id}:event:{change_type}:{detected_at}:{hash(evidence_refs)}`.
- Recommended deterministic RefreshPriority id composition: `motor_009:{source_id}:priority:{priority_level}:{calculated_at}:{hash(evidence_refs)}`.
- Recommended deterministic StalenessRecord id composition: `motor_009:{source_id}:staleness:{staleness_status}:{calculated_at}:{hash(basis_ingestion_refs,basis_version_refs)}`.
- `source_id` is an external stable key owned by motor_008 and is never redefined by motor_009.
- `ingestion_id`, `raw_record_ref` and `parsed_record_ref` are external keys owned by motor_004 and are used only as references.
- `version_id` and lineage ids from version_history are external keys owned by motor_002 and are used only as references.
- Empty identifiers, reused identifiers with incompatible `version_hash`, or identifiers that cannot be reconstructed from accepted input references are invalid.

## versioning
- Every persisted motor_009 entity includes `version_id`, `created_at`, `updated_at` and `version_hash`.
- `version_id` identifies one immutable emitted version of a ChangeEvent, RefreshPriority or StalenessRecord.
- `created_at` is set when the entity version is first emitted.
- `updated_at` records the last metadata update for that immutable emitted version; when no post-emission metadata update exists, it equals `created_at`.
- `version_hash` is computed deterministically from canonical serialized content, including logical identifier, source_id, rule references, evidence refs, lineage refs, parent_id and material output fields.
- Any material change to `change_type`, `severity`, comparison basis, priority level, stale-state status, evidence refs, rule refs, lineage refs or parent linkage requires a new `version_id` and `version_hash`.
- Historical outputs are not mutated in place. A superseding signal uses `parent_id` to link to the previous record_id of the same entity type.
- Current signals, historical signals and rejected comparisons must remain separable so downstream consumers can rebuild why a source was considered fresh, stale or high priority at a given time.

## lineage
- Every persisted motor_009 entity includes `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref` anchors the primary provenance reference: a source registry record, an ingestion record, a version record or a controlled composed reference that names those inputs.
- `produced_by_motor` is always `motor_009` for outputs emitted by the Source Change Detection / Refresh Intelligence Engine.
- `produced_at` records when motor_009 emitted the entity, distinct from upstream `captured_at`, upstream `created_at`, `detected_at` or `calculated_at`.
- `parent_id` links a superseding output to the previous immutable record_id of the same entity type; it is null when no predecessor exists.
- ChangeEvent lineage must preserve source_id, evidence_refs, lineage_refs, previous/current ingestion references, previous/current version references and detection_rule_ref.
- RefreshPriority lineage must preserve source_id, derived_from_event_ids, staleness_id when present, evidence_refs and rule_ref.
- StalenessRecord lineage must preserve source_id, basis_ingestion_refs, basis_version_refs, trigger_event_ids, expected_refresh_interval and triggering_condition.
- Missing source_ref, missing produced_by_motor, missing produced_at, insufficient evidence_refs or lineage_refs, or upstream references outside motor_008, motor_004 and motor_002 make the output invalid rather than silently repairable.
- Lineage fields provide reconstruction and audit only. They do not grant motor_009 authority to mutate source_registry, ingestion_records or version_history.
