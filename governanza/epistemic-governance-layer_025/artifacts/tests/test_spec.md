# Test Spec — Epistemic Governance Layer

Motor ID: motor_025

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar tensiones estructurales, inflación de excepciones, insuficiencia taxonómica y distinguir cambio local, estructural o constitucional.
why_it_exists:  Evita que el framework crezca rompiendo su constitución en silencio.
key_inputs:     conformance_records (motor_022), governance_events (motor_024), phase_contracts (motor_001)
key_outputs:    epistemic_tension_record, constitutional_change_signal, governance_health_report
key_objects:    EpistemicTension, ConstitutionalSignal, GovernanceHealthReport
what_not_to_do: No modifica contratos ni políticas directamente. Solo detecta y señaliza tensiones estructurales.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Capa de gobernanza de más alto nivel.

All open content markers in this file have been resolved for Gate 3 validation.
-->

## happy_path
Input:
- `phase_contracts` contains one active contract:
  - `contract_id="PCR-014-v2"`
  - `phase_id="phase_2"`
  - `allowed_inputs=["normalized_evidence"]`
  - `allowed_outputs=["phase_2_report"]`
  - `handoff_limits=["no_unregistered_output_override"]`
  - `responsibility_limits=["phase_2_must_not_emit_phase_3_outputs"]`
  - `version="2.0.0"`
  - `status="active"`
- `conformance_records` contains:
  - `CR-401`: `target_motor_id="motor_014"`, `contract_ref="PCR-014-v2"`, `status="FAIL"`, `severity="high"`, `findings=[{"type":"boundary_drift","detail":"phase_2 output override repeated"}]`, `checked_at="2026-04-18T10:00:00Z"`, `provenance_ref="prov:cr:401"`
  - `CR-402`: `target_motor_id="motor_014"`, `contract_ref="PCR-014-v2"`, `status="FAIL"`, `severity="high"`, `findings=[{"type":"conformance_gap","detail":"handoff limit bypassed"}]`, `checked_at="2026-04-18T10:05:00Z"`, `provenance_ref="prov:cr:402"`
- `governance_events` contains:
  - `GE-771`, `GE-772`, and `GE-773`, each with `event_type="exception_override"`, `affected_motor_id="motor_014"`, `severity="high"`, `recurrence_key="phase_2_output_override"`, `contract_ref="PCR-014-v2"`, valid `occurred_at` timestamps in the same evaluation window, and lineage refs `lin:ge:771`, `lin:ge:772`, `lin:ge:773`.

Expected output:
- Exactly one `EpistemicTension` is emitted with `tension_type="exception_inflation"`, `severity="high"`, `change_pressure="structural"`, `evidence_refs=["CR-401","CR-402","GE-771","GE-772","GE-773"]`, `governing_contract_refs=["PCR-014-v2"]`, `recurrence_key="phase_2_output_override"`, and `produced_by_motor="motor_025"`.
- Exactly one `ConstitutionalSignal` is emitted with `change_class="structural"`, `recommended_review_path="structural_design_review"`, `signal_severity="high"`, `originating_tension_ids` containing the emitted tension ID, and `affected_contract_refs=["PCR-014-v2"]`.
- Exactly one `GovernanceHealthReport` is emitted with `evaluated_contract_refs=["PCR-014-v2"]`, `tension_counts_by_type.exception_inflation=1`, `severity_counts.high=1`, `constitutional_signal_ids` containing the emitted signal ID, `unresolved_signal_ids` containing the emitted signal ID, `evidence_coverage.conformance_records_count=2`, `evidence_coverage.governance_events_count=3`, `evidence_coverage.phase_contracts_count=1`, `evidence_coverage.rejected_records_count=0`, and `governance_status="escalate"`.
- All output objects include stable IDs, ISO-8601 UTC production timestamps, `version_id`, `version_hash`, `source_ref`, `created_at`, `updated_at`, and `parent_id` fields.

## sparse_case
Input:
- `phase_contracts` contains active contract `PCR-014-v2` with the required contract fields.
- `conformance_records=[]`.
- `governance_events=[]`.
- No recurrence keys, findings, tension candidates, or historical contract references are supplied.

Expected output:
- The run completes without fatal error because the required authority set exists.
- No `EpistemicTension` records are emitted.
- No `ConstitutionalSignal` records are emitted.
- One `GovernanceHealthReport` is emitted with `evaluated_contract_refs=["PCR-014-v2"]`, `tension_ids=[]`, `constitutional_signal_ids=[]`, `unresolved_signal_ids=[]`, `tension_counts_by_type` containing zero values for `exception_inflation`, `taxonomic_insufficiency`, `boundary_drift`, `conformance_gap`, and `structural_conflict`, `severity_counts` containing zero values for `low`, `medium`, `high`, and `critical`, `exception_inflation_score=0`, `evidence_coverage.conformance_records_count=0`, `evidence_coverage.governance_events_count=0`, `evidence_coverage.phase_contracts_count=1`, `evidence_coverage.rejected_records_count=0`, and `governance_status="stable"`.
- The report `source_ref` still cites the evaluated contract reference so the empty evidence window is reconstructible.

## malformed_input
Cases that must be rejected before any partial output is produced:

1. Missing authority contract set:
   - Input sets `phase_contracts=[]` while supplying otherwise valid conformance records and governance events.
   - Expected rejection: `PHASE_CONTRACTS_REQUIRED`.

2. Missing provenance or lineage:
   - Input contains `CR-401` without `provenance_ref`, or `GE-771` without `lineage_ref`.
   - Expected rejection: `PROVENANCE_REQUIRED`.

3. Unknown contract reference:
   - Input contains `GE-771.contract_ref="PCR-999-v1"` and no supplied `phase_contracts.contract_id` matches `PCR-999-v1`; the reference is not marked as an explicit historical version reference.
   - Expected rejection: `UNKNOWN_CONTRACT_REF`.

4. Invalid timestamp:
   - Input contains `GE-771.occurred_at="18/04/2026 10:00"` or `CR-401.checked_at="not-a-date"`.
   - Expected rejection: `INVALID_EVENT_TIMESTAMP`.

5. Wrong container type:
   - Input sets `governance_events` to an object instead of a list, or sets `conformance_records[0].severity` to numeric value `3` instead of one of `low`, `medium`, `high`, or `critical`.
   - Expected rejection: `INVALID_INPUT_TYPE`.

For every malformed case, the observable result is a structured error containing `error_code`, `message`, and `source_ref` or `field_path` sufficient to identify the failing input field. The motor must not emit tensions, constitutional signals, health reports, edited contracts, policy changes, taxonomy edits, or motor state changes for rejected runs.

## edge_cases
1. Single low-severity exception without recurrence:
   - Input contains one valid active phase contract and one governance event `GE-101` with `event_type="exception_override"`, `severity="low"`, `recurrence_key=null`, `contract_ref` resolving to the phase contract, valid timestamp, and valid lineage.
   - Expected behavior: the event is counted in `GovernanceHealthReport.evidence_coverage.governance_events_count=1`, no structural or constitutional signal is emitted, no exception-inflation tension is emitted, and the report status is no higher than `watch`.

2. Duplicate evidence IDs with conflicting payloads:
   - Input contains two governance events with `event_id="GE-100"` but different `contract_ref`, `severity`, or `occurred_at` values.
   - Expected behavior: reject the full run with `DUPLICATE_EVIDENCE_ID`; do not pick one event silently and do not aggregate the conflicting records.

3. Explicit taxonomy gap from structured upstream evidence:
   - Input contains conformance record `CR-510` with `findings=[{"type":"taxonomy_gap","term":"unmapped_governance_boundary"}]`, valid `contract_ref="PCR-014-v2"`, valid `checked_at`, and valid `provenance_ref`.
   - Expected behavior: emit one `EpistemicTension` with `tension_type="taxonomic_insufficiency"`, `evidence_refs=["CR-510"]`, `governing_contract_refs=["PCR-014-v2"]`, and a classification basis that cites the upstream structured finding. The motor must not create a taxonomy term, alias, contract edit, or policy update.

4. Constitutional threshold from authority conflict:
   - Input contains repeated high-severity governance events and conformance records showing conflict with documented workflow sequence or phase authority hierarchy across more than one affected motor, all tied to valid contract references.
   - Expected behavior: emit `EpistemicTension.change_pressure="constitutional"` and a `ConstitutionalSignal` with `change_class="constitutional"` and `recommended_review_path="constitutional_review"`, while preserving all upstream evidence IDs unchanged.

## pass_criteria
A test passes when the following observable conditions hold:
- Valid inputs produce only the three allowed output families: `EpistemicTension`, `ConstitutionalSignal`, and `GovernanceHealthReport`.
- Every emitted output contains required identity, timestamp, versioning, lineage, provenance, and `produced_by_motor="motor_025"` fields from the technical schema.
- Tension classification follows deterministic rules: isolated non-recurring events remain local or non-escalating; three or more matching recurrence keys, multi-motor impact, or repeated contract boundary mismatch produce structural pressure; documented conflict with authority hierarchy, workflow sequence, phase semantics, or contract semantics produces constitutional pressure.
- Report counts match the emitted tensions and signals exactly, including zero counts in empty evidence windows.
- Rejection cases return the specified structured `error_code` and emit no partial governance outputs.
- Upstream evidence, contract references, provenance refs, lineage refs, and timestamps are preserved as read-only references and are not rewritten.

## fail_criteria
A test fails if any of the following is observed:
- The motor emits or mutates artifacts outside its allowed scope, including edited phase contracts, policy updates, taxonomy terms, exception approvals, conformance decisions, or motor state transitions.
- A valid structural recurrence pattern does not produce an `exception_inflation` tension and structural review signal.
- A malformed input is silently repaired, partially accepted, or rejected without a specific structured error code.
- Any emitted tension, signal, or report lacks required `source_ref`, evidence references, governing contract references, versioning fields, stable IDs, or production metadata.
- Duplicate conflicting upstream IDs are collapsed into one record instead of causing `DUPLICATE_EVIDENCE_ID`.
- An empty evidence window with valid phase contracts fails to produce an explicit stable `GovernanceHealthReport`.
- Constitutional classification is produced from raw narrative or LLM explanation rather than structured upstream evidence tied to contract authority.
