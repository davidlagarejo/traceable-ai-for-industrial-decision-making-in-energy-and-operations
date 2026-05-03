# Operational Rules — Epistemic Governance Layer

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

## rules
1. The motor must use supplied phase contracts as the governing authority for phase boundaries, allowed handoffs, and responsibility limits.
2. Every emitted `EpistemicTension` must cite at least one upstream evidence reference and at least one governing contract reference.
3. A tension is classified as `local` only when evidence is isolated to one motor, one contract boundary, and no repeated exception pattern exists in the evaluation window.
4. A tension is classified as `structural` when the same recurrence key appears at least three times in the evaluation window, affects more than one motor, or indicates a repeated mismatch between contract limits and actual governance events.
5. A tension is classified as `constitutional` only when evidence indicates conflict with documented authority hierarchy, workflow sequence, phase semantics, or a contract rule that cannot be corrected locally without rewriting framework-level governance.
6. Taxonomic insufficiency can be detected only from structured upstream signals such as `taxonomy_gap`, `unknown_canonical_term`, `semantic_boundary_conflict`, or equivalent conformance findings already recorded by upstream motors.
7. The motor must emit structured rejection errors instead of producing partial outputs when required IDs, timestamps, provenance references, lineage references, or contract references are missing.
8. The motor must preserve all upstream evidence references unchanged and must not collapse multiple source records into an untraceable summary.

## invariants
- Upstream records remain immutable; the motor reads and references them without changing their content.
- Every output remains traceable to source `conformance_records`, `governance_events`, and relevant `phase_contracts`.
- Each output has a stable ID, deterministic timestamp source, severity, classification basis, and affected scope.
- The distinction between local, structural, and constitutional change pressure is preserved in every signal and report.
- Absence of detected tension is represented explicitly in `governance_health_report`; it is not treated as missing execution.
- Human or external review remains required for any policy, contract, taxonomy, or constitutional change.

## forbidden_operations
- Modifying phase contracts, workflow rules, taxonomies, governance policies, or motor states directly.
- Approving, rejecting, or resolving exceptions and overrides.
- Recomputing conformance results owned by motor_022.
- Creating primary governance events owned by motor_024.
- Creating canonical taxonomy terms or aliases.
- Inferring constitutional violations from raw text without structured upstream evidence.
- Using an LLM or narrative rationale as the terminal classifier for change class.
- Closing, reopening, advancing, pausing, or blocking any motor.
