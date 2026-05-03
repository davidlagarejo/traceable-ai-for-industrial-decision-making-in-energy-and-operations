# Design Done Criteria — Decision Core / Inference Engine

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

## criteria
- `master_concept_doc.md` defines purpose, concrete actions, explicit exclusions, and separate-motor rationale for `motor_014`.
- `functional_contract.md` lists `inference_cases` and `phase_contracts` as inputs and lists `inference_record`, `tension_record`, `gap_agenda`, and `validation_agenda` as outputs.
- `functional_contract.md` states strict rejection rules for inactive cases, missing phase contracts, missing provenance, contract violations, and duplicate or empty case identifiers.
- `conceptual_schema.md` defines `InferenceRecord`, `Tension`, `GapAgenda`, and `ValidationAgenda` with required fields and relationships.
- `operational_rules.md` prohibits final report generation, claim verification, upstream mutation, activation override, evidence promotion, and AI-as-final-decision behavior.
- `acceptance_tests.md` covers a happy path, sparse valid input, conflicting evidence, synthetic-only support, and explicit rejection criteria.
- `failure_modes.md` names contract bypass, evidence promotion, lineage loss, conflict collapse, reporting leakage, and activation override as observable failure modes.
- All documentation-base artifacts are non-empty and contain no open markers such as bracketed placeholders, unresolved task labels, or question-mark placeholders.
