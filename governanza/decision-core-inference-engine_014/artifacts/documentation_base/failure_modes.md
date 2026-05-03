# Failure Modes — Decision Core / Inference Engine

Motor ID: motor_014

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
why_it_exists:  Es el corazón analítico de Fase 2.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001)
key_outputs:    inference_record, tension_record, gap_agenda, validation_agenda
key_objects:    InferenceRecord, Tension, ValidationAgenda
what_not_to_do: No produce reportes finales. No verifica claims. Solo infiere y registra con contratos explícitos.
design_notes:   Determinismo primero. La IA puede asistir pero no decide. Depende de motor_013 y motor_001.

Sections below define the completed documentation-base contract for this motor.
-->

## failure_modes_list
- `CONTRACT_BYPASS`: the motor emits an inference, tension, gap, or validation agenda not allowed by the applicable phase contract.
- `EVIDENCE_PROMOTION`: the motor treats synthetic support, library context, or preliminary inference as validation data or field evidence.
- `LINEAGE_LOSS`: emitted records omit case references, evidence references, contract references, or rule version, making reconstruction impossible.
- `CONFLICT_COLLAPSE`: conflicting inputs are silently converted into a single stronger inference without a `Tension` or validation agenda.
- `REPORTING_LEAKAGE`: the motor starts producing narrative report blocks, executive summaries, final claims, or rendered documentation.
- `ACTIVATION_OVERRIDE`: the motor processes draft, inactive, rejected, or otherwise non-activated cases as if they were valid inputs.

## anti_patterns
- Using the Decision Core as a report writer instead of as a structured inference registry.
- Letting an LLM adjudicate conflicts, severity, or inference state without deterministic rule output and contract checks.
- Feeding raw source material or unactivated analytical ideas directly into the motor instead of using `motor_013` activation records.
- Treating an empty `gap_agenda` as proof that the claim is verified.
- Adding downstream validation, evidence collection, rendering, or package assembly logic into this motor for convenience.

## degradation_signals
- Rising count of emitted outputs with missing `phase_contract_ref`, `lineage_refs`, `rule_version`, or `evidence_refs`.
- High rate of `InferenceRecord.inference_state = bounded_inference` while `tension_record` and `gap_agenda` remain empty despite conflicting evidence inputs.
- Any output with `required_evidence_level = field_evidence` that lacks a downstream validation handoff target.
- Any synthetic-only case emitted with an inference state stronger than `hypothesis_only`.
- New output classes appearing outside `inference_record`, `tension_record`, `gap_agenda`, and `validation_agenda`.
- Repeated identical validation agendas for unrelated cases, indicating template copying rather than case-specific gap registration.
