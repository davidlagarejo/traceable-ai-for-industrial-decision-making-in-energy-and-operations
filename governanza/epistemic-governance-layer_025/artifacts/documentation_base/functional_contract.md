# Functional Contract — Epistemic Governance Layer

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

## inputs
conformance_records: list[ConformanceRecord] — source motor_022; records of contract checks with `record_id`, `target_motor_id`, `contract_ref`, `status`, `severity`, `findings`, `checked_at`, and `provenance_ref`.

governance_events: list[GovernanceEvent] — source motor_024; registered anomalies, overrides, exceptions, and tension signals with `event_id`, `event_type`, `affected_motor_id`, `severity`, `recurrence_key`, `contract_ref`, `occurred_at`, and `lineage_ref`.

phase_contracts: list[PhaseContract] — source motor_001; authoritative phase contracts with `contract_id`, `phase_id`, `allowed_inputs`, `allowed_outputs`, `handoff_limits`, `responsibility_limits`, `version`, and `status`.

## outputs
epistemic_tension_record: EpistemicTension — destination governance review queue and downstream observability; one record per detected structural tension with evidence references and deterministic classification.

constitutional_change_signal: ConstitutionalSignal — destination governance review queue; escalation signal when a tension indicates local, structural, or constitutional change pressure.

governance_health_report: GovernanceHealthReport — destination operators and conformance review; aggregate health summary for the evaluated window with counts, unresolved signals, and governance status.

## limits
- Never accepts raw source documents, free-form notes, or unregistered human claims as direct evidence.
- Never accepts input records without stable IDs, provenance or lineage references, timestamps, and contract references where contract impact is asserted.
- Never treats an LLM-generated explanation as authoritative evidence unless it is attached to a structured record from an upstream motor.
- Never produces modified phase contracts, updated policies, taxonomy edits, exception approvals, conformance decisions, or motor state transitions.
- Never classifies a tension as constitutional unless the evidence points to a repeated conflict with documented authority, workflow order, phase boundaries, or contract semantics.
- Never silently repairs malformed input; malformed or untraceable records are rejected with structured errors.

## validations
- Validates that `phase_contracts` is present and contains at least one active or historically referenced contract.
- Validates that every conformance record has `record_id`, `target_motor_id`, `contract_ref`, `status`, `severity`, `checked_at`, and `provenance_ref`.
- Validates that every governance event has `event_id`, `event_type`, `affected_motor_id`, `severity`, `occurred_at`, and `lineage_ref`.
- Validates that any `contract_ref` cited by an input record resolves to a supplied phase contract or is explicitly marked as historical with a version reference.
- Validates that timestamps are parseable and that the evaluation window can be reconstructed deterministically.
- Validates before output that every `EpistemicTension` includes `tension_id`, `tension_type`, `severity`, `evidence_refs`, `governing_contract_refs`, `classification_basis`, and `detected_at`.
- Validates before output that every `ConstitutionalSignal` includes `signal_id`, `originating_tension_ids`, `change_class`, `escalation_reason`, `affected_contract_refs`, and `emitted_at`.
- Validates before output that every `GovernanceHealthReport` includes `report_id`, `window_start`, `window_end`, `tension_counts_by_type`, `unresolved_signal_ids`, and `governance_status`.
