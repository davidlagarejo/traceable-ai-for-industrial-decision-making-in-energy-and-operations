# Acceptance Tests — Epistemic Governance Layer

Motor ID: motor_025

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar tensiones estructurales, inflación de excepciones, insuficiencia taxonómica y distinguir cambio local, estructural o constitucional.
why_it_exists:  Evita que el framework crezca rompiendo su constitución en silencio.
key_inputs:     conformance_records (motor_022), governance_events (motor_024), phase_contracts (motor_001)
key_outputs:    epistemic_tension_record, constitutional_change_signal, governance_health_report
key_objects:    EpistemicTension, ConstitutionalSignal, GovernanceHealthReport
what_not_to_do: No modifica contratos ni políticas directamente. Solo detecta y señaliza tensiones estructurales.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Capa de gobernanza de más alto nivel.

Documentation base completed for Gate 1 validation.
-->

## happy_path
Input: `phase_contracts` contains contract `PCR-014-v2` for phase `phase_2` with explicit output limits; `conformance_records` contains `CR-401` and `CR-402` showing repeated boundary findings against `PCR-014-v2`; `governance_events` contains `GE-771`, `GE-772`, and `GE-773` with recurrence key `phase_2_output_override`, each tied to the same contract and each carrying provenance and lineage.

Action: the motor validates all IDs, timestamps, provenance references, lineage references, and contract references; groups the three events by recurrence key; compares the pattern against the phase contract boundary; and classifies the pressure level.

Expected output: one `epistemic_tension_record` with `tension_type=exception_inflation`, `severity=high`, `evidence_refs=["CR-401","CR-402","GE-771","GE-772","GE-773"]`, and `governing_contract_refs=["PCR-014-v2"]`; one `constitutional_change_signal` with `change_class=structural` and `recommended_review_path=structural_design_review`; one `governance_health_report` with `governance_status=escalate`, `tension_counts_by_type.exception_inflation=1`, and the emitted signal listed in `unresolved_signal_ids`.

## edge_cases
- Empty evidence window: when `conformance_records=[]` and `governance_events=[]` but valid `phase_contracts` are present, the motor emits no tension records, no constitutional signals, and a `governance_health_report` with `governance_status=stable` and zero counts.
- Single low-severity exception: when one governance event has `severity=low` and no matching recurrence key appears, the motor records the event in the health report context but emits no structural or constitutional signal.
- Duplicate upstream record IDs: when two governance events share `event_id=GE-100` with different payloads, the motor rejects the run with `DUPLICATE_EVIDENCE_ID` instead of choosing one silently.
- Explicit taxonomy gap: when a conformance record has finding type `taxonomy_gap` with valid provenance and affected contract reference, the motor emits `tension_type=taxonomic_insufficiency` without creating or changing any taxonomy term.

## rejection_criteria
- Reject with `PHASE_CONTRACTS_REQUIRED` when `phase_contracts` is missing or empty.
- Reject with `PROVENANCE_REQUIRED` when any conformance record lacks `provenance_ref` or any governance event lacks `lineage_ref`.
- Reject with `UNKNOWN_CONTRACT_REF` when an input cites a contract reference absent from `phase_contracts` and not explicitly marked as a historical version reference.
- Reject with `INVALID_EVENT_TIMESTAMP` when `checked_at` or `occurred_at` cannot be parsed into the evaluation window.
