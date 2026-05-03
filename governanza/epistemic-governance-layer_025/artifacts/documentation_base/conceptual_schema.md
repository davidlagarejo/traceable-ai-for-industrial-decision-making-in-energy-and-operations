# Conceptual Schema — Epistemic Governance Layer

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

## entities
EpistemicTension: object that represents a detected governance pressure pattern, such as exception inflation, structural boundary drift, conformance gap, or declared taxonomic insufficiency.

ConstitutionalSignal: object that represents an escalation derived from one or more tensions and classifies the required review level as local, structural, or constitutional.

GovernanceHealthReport: object that summarizes the evaluated governance window, including tension counts, unresolved signals, evidence coverage, and overall governance health.

## relationships
ConformanceRecord + GovernanceEvent + PhaseContract → EpistemicTension (a tension is created only when upstream evidence conflicts with, repeats against, or stresses a governing contract boundary).

EpistemicTension → ConstitutionalSignal (one or more tensions create an escalation signal when recurrence, severity, or scope exceeds local correction).

EpistemicTension → GovernanceHealthReport (all tensions in the evaluation window are aggregated into health metrics and status).

ConstitutionalSignal → GovernanceHealthReport (open and newly emitted signals are summarized as escalation pressure in the report).

PhaseContract → ConstitutionalSignal (affected contract references define which authority boundary would need local, structural, or constitutional review).

## key_fields
EpistemicTension:
- `tension_id`: string
- `tension_type`: enum[`exception_inflation`, `taxonomic_insufficiency`, `boundary_drift`, `conformance_gap`, `structural_conflict`]
- `affected_scope`: object with `motor_ids`: list[string], `phase_ids`: list[string], and `contract_ids`: list[string]
- `severity`: enum[`low`, `medium`, `high`, `critical`]
- `evidence_refs`: list[string]
- `governing_contract_refs`: list[string]
- `classification_basis`: string
- `detected_at`: datetime

ConstitutionalSignal:
- `signal_id`: string
- `originating_tension_ids`: list[string]
- `change_class`: enum[`local`, `structural`, `constitutional`]
- `escalation_reason`: string
- `affected_contract_refs`: list[string]
- `recommended_review_path`: enum[`local_correction_review`, `structural_design_review`, `constitutional_review`]
- `emitted_at`: datetime

GovernanceHealthReport:
- `report_id`: string
- `window_start`: datetime
- `window_end`: datetime
- `evaluated_contract_refs`: list[string]
- `tension_counts_by_type`: object mapping string to integer
- `exception_inflation_score`: number
- `unresolved_signal_ids`: list[string]
- `governance_status`: enum[`stable`, `watch`, `escalate`]
