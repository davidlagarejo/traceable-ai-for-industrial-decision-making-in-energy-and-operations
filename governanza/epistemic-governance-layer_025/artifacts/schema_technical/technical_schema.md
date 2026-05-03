# Technical Schema — Epistemic Governance Layer

Motor ID: motor_025

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar tensiones estructurales, inflación de excepciones, insuficiencia taxonómica y distinguir cambio local, estructural o constitucional.
why_it_exists:  Evita que el framework crezca rompiendo su constitución en silencio.
key_inputs:     conformance_records (motor_022), governance_events (motor_024), phase_contracts (motor_001)
key_outputs:    epistemic_tension_record, constitutional_change_signal, governance_health_report
key_objects:    EpistemicTension, ConstitutionalSignal, GovernanceHealthReport
what_not_to_do: No modifica contratos ni políticas directamente. Solo detecta y señaliza tensiones estructurales.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Capa de gobernanza de más alto nivel.

Schema technical content completed for Gate 2 validation.
-->

## entities
EpistemicTension — output entity produced by `motor_025` during implementation and governed by the `schema_technical` stage. It records one detected governance pressure pattern, such as exception inflation, taxonomic insufficiency, boundary drift, conformance gap, or structural conflict. It is a signal object only; it never changes the upstream contract, taxonomy, policy, governance event, or conformance record.

ConstitutionalSignal — output entity produced by `motor_025` during implementation and governed by the `schema_technical` stage. It represents an escalation derived from one or more `EpistemicTension` records and classifies the required review level as local, structural, or constitutional. It requests review; it does not approve, reject, resolve, or apply any governance change.

GovernanceHealthReport — aggregate output entity produced by `motor_025` during implementation and governed by the `schema_technical` stage. It summarizes one deterministic evaluation window, including evaluated contract references, tension counts, open signals, evidence coverage, exception pressure, and the resulting governance status.

## fields
EpistemicTension:
- `tension_id`: string (required) — stable canonical identifier for the tension record.
- `tension_type`: enum[`exception_inflation`, `taxonomic_insufficiency`, `boundary_drift`, `conformance_gap`, `structural_conflict`] (required) — deterministic type assigned from structured conformance records and governance events.
- `affected_scope`: object (required) — affected governance area with `motor_ids: list[string]`, `phase_ids: list[string]`, and `contract_ids: list[string]`.
- `severity`: enum[`low`, `medium`, `high`, `critical`] (required) — highest deterministic severity assigned by the input evidence and classification rules.
- `change_pressure`: enum[`local`, `structural`, `constitutional`] (required) — correction level indicated by recurrence, severity, scope, and contract authority checks.
- `evidence_refs`: list[string] (required) — non-empty stable IDs from upstream `conformance_records` and `governance_events`.
- `governing_contract_refs`: list[string] (required) — non-empty `PhaseContract.contract_id` or historical contract version references used as authority.
- `recurrence_key`: string | null (required) — recurrence key copied from governance events when a pattern exists; null when the tension is not recurrence-based.
- `classification_basis`: string (required) — concise deterministic rule statement explaining why the tension type and change pressure were assigned.
- `detected_at`: datetime (required) — ISO-8601 UTC timestamp for when the tension was emitted.
- `version_id`: string (required) — version identifier for this tension instance.
- `created_at`: datetime (required) — ISO-8601 UTC timestamp for first creation of the tension record.
- `updated_at`: datetime (required) — ISO-8601 UTC timestamp for this material version of the tension record.
- `version_hash`: string (required) — SHA-256 hash of the canonical serialized tension payload excluding `version_hash`.
- `source_ref`: list[string] (required) — canonical lineage references to evidence records and governing contracts that produced the tension.
- `produced_by_motor`: enum[`motor_025`] (required) — producing motor identifier.
- `produced_at`: datetime (required) — ISO-8601 UTC timestamp for production of this output object.
- `parent_id`: string | null (required) — prior `tension_id` when this record supersedes an earlier version; null for first emission.

ConstitutionalSignal:
- `signal_id`: string (required) — stable canonical identifier for the escalation signal.
- `originating_tension_ids`: list[string] (required) — non-empty references to `EpistemicTension.tension_id` values that caused the signal.
- `change_class`: enum[`local`, `structural`, `constitutional`] (required) — review class determined from the originating tensions.
- `escalation_reason`: string (required) — concise deterministic explanation of the recurrence, severity, scope, or authority conflict that justifies review.
- `affected_contract_refs`: list[string] (required) — `PhaseContract.contract_id` or historical version references affected by the signal.
- `recommended_review_path`: enum[`local_correction_review`, `structural_design_review`, `constitutional_review`] (required) — review path implied by `change_class`.
- `signal_severity`: enum[`low`, `medium`, `high`, `critical`] (required) — maximum severity inherited from originating tensions.
- `emitted_at`: datetime (required) — ISO-8601 UTC timestamp for signal emission.
- `version_id`: string (required) — version identifier for this signal instance.
- `created_at`: datetime (required) — ISO-8601 UTC timestamp for first creation of the signal.
- `updated_at`: datetime (required) — ISO-8601 UTC timestamp for this material version of the signal.
- `version_hash`: string (required) — SHA-256 hash of the canonical serialized signal payload excluding `version_hash`.
- `source_ref`: list[string] (required) — canonical lineage references to originating tensions and affected contract references.
- `produced_by_motor`: enum[`motor_025`] (required) — producing motor identifier.
- `produced_at`: datetime (required) — ISO-8601 UTC timestamp for production of this output object.
- `parent_id`: string | null (required) — prior `signal_id` when this signal supersedes an earlier version; null for first emission.

GovernanceHealthReport:
- `report_id`: string (required) — stable canonical identifier for the evaluation-window report.
- `window_start`: datetime (required) — ISO-8601 UTC lower bound of the evaluated evidence window.
- `window_end`: datetime (required) — ISO-8601 UTC upper bound of the evaluated evidence window.
- `evaluated_contract_refs`: list[string] (required) — phase contracts considered authoritative for the report window.
- `tension_ids`: list[string] (required) — `EpistemicTension.tension_id` values emitted or carried into the report window.
- `constitutional_signal_ids`: list[string] (required) — `ConstitutionalSignal.signal_id` values emitted or carried into the report window.
- `tension_counts_by_type`: object<string, integer> (required) — count of tensions by `tension_type`; absent categories are represented with zero values.
- `severity_counts`: object<string, integer> (required) — count of tensions by `severity`; absent severities are represented with zero values.
- `exception_inflation_score`: number (required) — deterministic score derived from repeated exception recurrence keys and evaluated event volume.
- `unresolved_signal_ids`: list[string] (required) — open signal identifiers that require review outside this motor.
- `evidence_coverage`: object (required) — source coverage summary with `conformance_records_count: integer`, `governance_events_count: integer`, `phase_contracts_count: integer`, and `rejected_records_count: integer`.
- `governance_status`: enum[`stable`, `watch`, `escalate`] (required) — deterministic status for the evaluated window.
- `classification_basis_summary`: string (required) — concise description of the deterministic rules that drove the report status.
- `version_id`: string (required) — version identifier for this report instance.
- `created_at`: datetime (required) — ISO-8601 UTC timestamp for first creation of the report.
- `updated_at`: datetime (required) — ISO-8601 UTC timestamp for this material version of the report.
- `version_hash`: string (required) — SHA-256 hash of the canonical serialized report payload excluding `version_hash`.
- `source_ref`: list[string] (required) — canonical lineage references to evaluated tensions, signals, contracts, and upstream evidence groups.
- `produced_by_motor`: enum[`motor_025`] (required) — producing motor identifier.
- `produced_at`: datetime (required) — ISO-8601 UTC timestamp for production of this output object.
- `parent_id`: string | null (required) — previous `report_id` for the same reporting stream when superseded; null for first report in the stream.

## relationships
- `EpistemicTension.evidence_refs` references upstream `ConformanceRecord.record_id` values from `motor_022` and `GovernanceEvent.event_id` values from `motor_024`. These are read-only external references.
- `EpistemicTension.governing_contract_refs` references `PhaseContract.contract_id` or explicit historical contract version identifiers from `motor_001`.
- `ConstitutionalSignal.originating_tension_ids` is a required many-to-many reference to `EpistemicTension.tension_id`. A signal must not exist without at least one originating tension.
- `ConstitutionalSignal.affected_contract_refs` references the same contract authority namespace used by `EpistemicTension.governing_contract_refs`.
- `GovernanceHealthReport.tension_ids` references all `EpistemicTension.tension_id` values included in the evaluation window.
- `GovernanceHealthReport.constitutional_signal_ids` and `GovernanceHealthReport.unresolved_signal_ids` reference `ConstitutionalSignal.signal_id`.
- `GovernanceHealthReport.evaluated_contract_refs` references the `PhaseContract` objects supplied to the run and defines the contract universe for the report window.
- `parent_id` is a self-reference within the same entity type for lineage across material versions. It must not point to a different entity type.

## identifiers
- EpistemicTension canonical ID: `tension_id`. Recommended deterministic form: `motor_025:tension:{hash(evidence_refs, governing_contract_refs, tension_type, affected_scope)}`.
- ConstitutionalSignal canonical ID: `signal_id`. Recommended deterministic form: `motor_025:signal:{hash(originating_tension_ids, change_class, affected_contract_refs)}`.
- GovernanceHealthReport canonical ID: `report_id`. Recommended deterministic form: `motor_025:report:{hash(window_start, window_end, evaluated_contract_refs)}`.
- Generic persistence adapters may expose a `record_id`, but for this motor it must be an alias of the entity canonical ID and must not introduce a separate identity namespace.
- All IDs are stable across rebuilds when the canonical inputs and deterministic classification rules are unchanged.

## versioning
Every persisted `EpistemicTension`, `ConstitutionalSignal`, and `GovernanceHealthReport` must include the following versioning fields:

- `version_id`: string (required) — monotonically comparable version label for the material object instance.
- `created_at`: datetime (required) — first creation timestamp for the canonical object identity.
- `updated_at`: datetime (required) — timestamp for the current material version.
- `version_hash`: string (required) — SHA-256 hash computed from canonical JSON with stable key ordering and without the `version_hash` field.

Versioning rules:
- A material change to type, severity, change class, affected scope, evidence references, governing contract references, report window, or governance status creates a new version rather than mutating the previous version silently.
- `updated_at` must be greater than or equal to `created_at`.
- `version_hash` must change when any material field changes and must remain stable when the canonical payload is unchanged.
- Earlier versions remain reconstructible through `parent_id`, `source_ref`, and the unchanged upstream evidence IDs.

## lineage
Every persisted `EpistemicTension`, `ConstitutionalSignal`, and `GovernanceHealthReport` must include the following lineage fields:

- `source_ref`: list[string] (required) — canonical upstream references used to produce the object.
- `produced_by_motor`: enum[`motor_025`] (required) — the only valid producing motor for these entities.
- `produced_at`: datetime (required) — ISO-8601 UTC timestamp for output production.
- `parent_id`: string | null (required) — previous canonical ID in the same entity lineage, or null for first emission.

Lineage rules by entity:
- `EpistemicTension.source_ref` contains the upstream conformance record IDs, governance event IDs, and governing contract references used to detect the tension.
- `ConstitutionalSignal.source_ref` contains `originating_tension_ids` plus the affected contract references that define the escalation boundary.
- `GovernanceHealthReport.source_ref` contains the report `tension_ids`, `constitutional_signal_ids`, `evaluated_contract_refs`, and any upstream evidence group references needed to reconstruct the evaluated window.
- Upstream evidence IDs, provenance references, lineage references, contract references, and timestamps must be preserved without rewriting.
- Missing lineage, missing provenance, duplicate evidence IDs with conflicting payloads, or unresolved contract references block output production with structured rejection errors.
