# Design Done Criteria — Epistemic Governance Layer

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

## criteria
- `master_concept_doc.md` states the motor purpose, concrete actions, explicit non-responsibilities, and separate rationale for the lightweight governance layer.
- `functional_contract.md` lists `conformance_records`, `governance_events`, and `phase_contracts` as inputs with source motors and lists all three expected outputs with consumers.
- `conceptual_schema.md` defines `EpistemicTension`, `ConstitutionalSignal`, and `GovernanceHealthReport` with required fields, types, and relationships.
- `operational_rules.md` includes deterministic rules for local, structural, and constitutional classification and prohibits direct contract, policy, taxonomy, or state mutation.
- `acceptance_tests.md` covers a happy path, empty evidence window, single low-severity exception, duplicate evidence IDs, taxonomy gap handling, and explicit rejection errors.
- `failure_modes.md` lists observable failure modes, anti-patterns, and degradation signals specific to epistemic governance.
- All documentation_base artifacts are non-empty, contain the required section headings, and contain no open-content markers blocked by Gate 1.
