# Failure Modes Spec — Source Change Detection / Refresh Intelligence

Motor ID: motor_009

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar cambios de fuente, metodología, estructura, disponibilidad y prioridad de recaptura.
why_it_exists:  Sin este motor los datasets quedan stale sin que el sistema lo sepa.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), version_history (motor_002)
key_outputs:    change_detection_event, refresh_priority, staleness_signal
key_objects:    ChangeEvent, RefreshPriority, StalenessRecord
what_not_to_do: No descarga datos. No decide qué hacer con cambios. Solo detecta y señaliza.
design_notes:   Depende de motor_008, motor_004, motor_002.

All failure-mode sections are filled for Gate 4 review.
-->

## failure_modes_list
- `INVALID_SOURCE_ACCEPTED`: `ingestion_records` or `version_history` references a `source_id` absent from `source_registry` -> emitted `ChangeEvent`, `RefreshPriority` or `StalenessRecord` cannot be anchored to motor_008 -> reject the affected source batch with `INVALID_SOURCE_REFERENCE`, emit no partial outputs for that source, and require the upstream registry reference to be supplied before rerun.
- `MISSING_COMPARISON_EVIDENCE_ACCEPTED`: an ingestion record lacks all comparable evidence fields (`availability_status`, `observed_schema_signature`, `content_fingerprint`, `record_count`, `access_error_code`) -> the motor invents a no-change state or emits a weak event with empty `comparison_basis` -> reject the comparison with `MISSING_COMPARISON_EVIDENCE`, preserve the invalid input reference in validation logs, and wait for a new ingestion record with at least one deterministic comparison field.
- `UNTRACEABLE_CHANGE_EVENT`: a schema, access, methodology, frequency or fingerprint difference is detected but `evidence_refs`, `lineage_refs`, prior/current ingestion refs or prior/current version refs are absent or inconsistent -> downstream consumers cannot reconstruct why the event exists -> discard the proposed event, return `UNTRACEABLE_CHANGE_EVENT`, and require enough motor_004 or motor_002 references to rebuild the comparison.
- `NONDETERMINISTIC_ORDERING`: records for the same `source_id` are compared in input order instead of canonical order by `source_id`, timestamp and version lineage -> identical input sets produce different event ids, hashes, severities or priorities when delivered in a different sequence -> normalize ordering before comparison, recompute ids from canonical content, and fail the run if two records remain temporally incomparable.
- `FALSE_REFRESH_ESCALATION`: `RefreshPriority.priority_level` is raised without a supporting `ChangeEvent`, `StalenessRecord` or documented temporal rule -> downstream planning treats a weak signal as urgent recapture pressure -> downgrade to `none` only when a deterministic no-change or unknown-interval rule applies, otherwise reject the priority calculation and require a `rule_ref` plus supporting evidence refs.
- `STALE_SIGNAL_SUPPRESSED`: age, access or interval evidence exceeds the declared refresh rule but no `StalenessRecord` is emitted -> datasets remain marked fresh while source observations are stale or unavailable -> emit a deterministic `StalenessRecord` with `staleness_status` in `watch`, `stale` or `unknown`, preserve `basis_ingestion_refs` and `basis_version_refs`, and recalculate priority from the staleness rule.
- `UPSTREAM_MUTATION_ATTEMPT`: implementation writes into `source_registry`, `ingestion_records`, `version_history`, rights profiles or raw records while resolving a comparison -> provenance is altered and historical reconstruction becomes impossible -> abort the operation, report a boundary violation, and restrict recovery to producing immutable motor_009 outputs or structured rejection records.
- `ACTION_EXECUTION_LEAK`: the motor downloads, scrapes, calls external APIs, authenticates to a source, or creates recapture jobs after assigning a high or urgent priority -> refresh intelligence becomes an operational scheduler/downloader outside its contract -> stop external side effects, mark the run non-conformant, and emit only advisory `RefreshPriority` signals for downstream operators or motors.

## anti_patterns
- Coupling `RefreshPriority` directly to a downloader, scraper, scheduler queue or recapture command; priority is an advisory signal and must not execute work.
- Mutating motor_008, motor_004 or motor_002 records to make comparisons easier; motor_009 may reference those records but never rewrite them.
- Treating source registry metadata alone as enough evidence for a `ChangeEvent`; at least one motor_004 ingestion id or motor_002 version id must support each emitted event.
- Generating event ids, priority ids or hashes from wall-clock order, input list order or random values instead of canonical serialized content and stable evidence refs.
- Collapsing `evidence_refs`, `lineage_refs`, `comparison_basis` or rule references into narrative text, which breaks rebuild and audit.
- Interpreting content semantics from `content_fingerprint` changes; this motor may signal a fingerprint change but parsing, normalization, identity resolution and quality evaluation belong to other motors.
- Using LLM judgement, free-text summaries or operator preference to set `severity`, `staleness_status` or `priority_level` instead of deterministic rules.
- Emitting `RefreshPriority` as a final operational decision rather than a traceable input to downstream planning.
- Sharing mutable state across sources in a way that lets one source's access error, age, schema signature or priority contaminate another source.

## degradation_signals
- Rate of rejected comparisons with `MISSING_COMPARISON_EVIDENCE` rises above the normal ingestion baseline, indicating motor_004 inputs are no longer carrying comparable evidence.
- Any emitted `ChangeEvent` has empty `evidence_refs`, empty `lineage_refs`, missing `detection_rule_ref`, missing prior/current refs when applicable, or no motor_004 or motor_002 reference.
- Identical accepted inputs produce different `event_id`, `priority_id`, `staleness_id` or `version_hash` across repeated runs.
- Count of `RefreshPriority.priority_level` values `high` or `urgent` increases while supporting `ChangeEvent` and `StalenessRecord` counts remain flat.
- Sources with `age_days` greater than the declared refresh interval continue to receive `staleness_status = "fresh"`.
- `access_error_code` or `availability_status = "blocked"` appears in ingestion records without corresponding `ChangeEvent.change_type = "access"` or an explanatory structured rejection.
- Event volume drops to zero for active sources while new ingestion records and version records continue to arrive.
- Outputs show `produced_by_motor` values other than `motor_009`, missing `source_ref`, missing `produced_at`, or `parent_id` pointing across entity types.
- Logs include attempts to open network connections, create raw records, write source registry fields, write ingestion records or write version history from motor_009 code paths.
- Staleness records repeatedly use `expected_refresh_interval = null` for sources that have a declared interval in motor_008, indicating registry fields are not being read or mapped correctly.

## expensive_errors
- `LOSS_OF_LINEAGE_ON_EMISSION`: emitting events or priorities without `evidence_refs`, `lineage_refs`, `source_ref`, `version_hash` or rule refs is expensive because downstream stale-state decisions cannot be reconstructed after the fact. Prevention: validate all required provenance fields before persistence and reject the output instead of filling defaults.
- `UPSTREAM_RECORD_REWRITE`: modifying motor_008 source records, motor_004 ingestion records or motor_002 version history is expensive because it corrupts the evidence base used by multiple motors. Prevention: enforce read-only adapters for upstream inputs and allow writes only to motor_009 output objects.
- `PRIORITY_AS_COMMAND`: treating `RefreshPriority` as an executable recapture order is expensive because it can trigger unnecessary data collection, rights violations or rate-limit exposure. Prevention: keep the output schema advisory, require `rule_ref` and `evidence_refs`, and route actual execution to downstream components outside motor_009.
- `NONREPRODUCIBLE_IDENTIFIERS`: generating ids or hashes from noncanonical order, local time, process counters or randomness is expensive because historical comparisons and parent links cannot be matched reliably. Prevention: derive identifiers from `source_id`, change type, calculated/detected timestamp, canonical evidence refs and canonical content hash.
- `MISCLASSIFIED_ACCESS_FAILURE`: treating blocked access as no change or freshness is expensive because stale datasets can propagate silently while source availability has degraded. Prevention: map changes in `availability_status` and `access_error_code` to deterministic access events and staleness triggers.
- `SEMANTIC_OVERINTERPRETATION`: interpreting the meaning of changed content from fingerprints inside motor_009 is expensive because it bypasses parsing, normalization and quality motors and creates unreviewable claims. Prevention: limit this motor to signaling `content_fingerprint` changes and preserving comparison evidence for downstream analysis.
- `SILENT_DEFAULTS_FOR_MISSING_INTERVALS`: replacing missing refresh intervals with arbitrary defaults is expensive because staleness and priority become misleading and hard to audit. Prevention: emit `staleness_status = "unknown"` when the interval is absent and use an explicit unknown-interval priority rule.
- `PARTIAL_OUTPUT_AFTER_REJECTION`: emitting some outputs for a rejected source comparison is expensive because consumers may act on incomplete or invalid evidence. Prevention: make validation atomic per source comparison: either all required outputs are valid or the affected comparison emits only structured errors.
