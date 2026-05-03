# Failure Modes — Epistemic Governance Layer

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

## failure_modes_list
TENSION_OVERCLASSIFICATION: isolated local events are escalated as structural or constitutional, causing review noise and governance fatigue.

EXCEPTION_INFLATION_BLINDNESS: repeated exceptions with the same recurrence key remain classified as independent local events, hiding systemic drift.

TAXONOMIC_GAP_COLLAPSE: declared taxonomy gaps are merged into generic conformance failures, so insufficient semantic coverage is never surfaced.

CONSTITUTIONAL_SIGNAL_SPAM: the motor emits constitutional signals without strong contract-level evidence, weakening the meaning of constitutional review.

PROVENANCE_LOSS: emitted tensions or reports cite aggregate counts but omit source record IDs, making the diagnosis impossible to reconstruct.

## anti_patterns
- Using this motor as a policy editor instead of a detector and signaler of governance pressure.
- Feeding raw notes, chat summaries, or unregistered claims as direct evidence.
- Treating every conformance failure as constitutional pressure without recurrence, severity, or scope checks.
- Collapsing governance events by human-readable title instead of stable recurrence keys and evidence IDs.
- Using an LLM explanation as the final source of classification rather than deterministic rules over structured inputs.

## degradation_signals
- Rising ratio of `governance_events` with valid recurrence keys but no corresponding `EpistemicTension` in repeated windows.
- More than one emitted `ConstitutionalSignal` lacking two or more independent evidence references.
- Increase in `UNKNOWN_CONTRACT_REF` rejections after new contracts are introduced, indicating upstream handoff mismatch.
- `governance_health_report` repeatedly reports `stable` while motor_024 contains high-severity repeated exceptions.
- Tension records with empty `governing_contract_refs`, empty `classification_basis`, or missing affected scope.
- Rapid growth in constitutional signals compared with structural signals, indicating classification thresholds may be too permissive.
