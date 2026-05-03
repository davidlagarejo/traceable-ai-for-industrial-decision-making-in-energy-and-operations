# Operational Rules — Decision Core / Inference Engine

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

## rules
1. The motor processes only cases whose `case_status` is `activated` and whose `phase_id` has a matching `PhaseContract`.
2. The motor emits only output classes explicitly allowed by the matching phase contract.
3. Every emitted record is a deterministic function of the input case, the phase contract, the rule version, and the configured evidence classification rules.
4. Every inference must preserve the source case reference, phase contract reference, evidence references, lineage references, and rule version.
5. Conflicting or insufficient evidence must be represented as a `Tension` or `GapAgenda` item rather than silently collapsed into a stronger conclusion.
6. If the available support is only synthetic or otherwise non-evidentiary, the `InferenceRecord.inference_state` must be `hypothesis_only`.
7. The motor must create a `ValidationAgenda` entry for every blocking gap that prevents a bounded inference.
8. The motor must reject malformed inputs with structured error codes rather than emitting partial analytical outputs.

## invariants
- `case_id` is never null in any accepted input or emitted output.
- `phase_contract_ref` is present in every emitted `InferenceRecord`, `Tension`, `GapAgenda`, and `ValidationAgenda`.
- Upstream `inference_cases` and `phase_contracts` remain immutable during processing.
- Every output record has `motor_id = motor_014`.
- Every output record has at least one lineage reference or is rejected before emission.
- No output from this motor represents a final report, verified claim, or field evidence object.
- The number and class of emitted outputs remain within the limits declared by the applicable phase contract.

## forbidden_operations
- Producing final reports, report packages, output blocks, executive views, technical views, or rendered documents.
- Verifying claims, closing claims as true, or substituting for `motor_019`.
- Activating inference cases or overriding activation decisions from `motor_013`.
- Editing, deleting, or reclassifying `inference_cases`, phase contracts, source records, evidence records, or validation data.
- Ingesting sources, parsing documents, normalizing data, resolving identities, curating libraries, or evaluating upstream data quality.
- Promoting synthetic support to validation data or field evidence.
- Using an LLM or other AI component as the final decision maker for inference state, conflict resolution, or validation need.
- Emitting outputs without lineage, provenance, rule version, and phase contract reference.
