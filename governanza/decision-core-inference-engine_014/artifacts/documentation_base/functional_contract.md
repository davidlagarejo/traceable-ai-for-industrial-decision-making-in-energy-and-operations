# Functional Contract — Decision Core / Inference Engine

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

## inputs
- `inference_cases`: `list[InferenceCase]` — produced by `motor_013`; each item must include `case_id`, `activation_record_ref`, `trigger_log_ref`, `phase_id`, `case_status`, `analysis_question`, `evidence_refs`, and `lineage_refs`.
- `phase_contracts`: `list[PhaseContract]` — produced by `motor_001`; each item must include `contract_id`, `phase_id`, `allowed_inputs`, `allowed_outputs`, `handoff_rules`, `output_limits`, and `contract_version`.

## outputs
- `inference_record`: `InferenceRecord` JSON-compatible record — stored as the Fase 2 inferential result and consumed by downstream composition, verification, and re-evaluation flows.
- `tension_record`: `list[Tension]` JSON-compatible records — consumed by validation and verification planning when conflicts, opportunities, or unresolved analytical tensions must be tracked.
- `gap_agenda`: `GapAgenda` JSON-compatible record — consumed by validation planning and downstream hardening workflows to identify missing data, missing evidence, or unresolved contract gaps.
- `validation_agenda`: `ValidationAgenda` JSON-compatible record — consumed by downstream validation and verification flows as an explicit list of evidence needs, validation routes, and handoff targets.

## limits
- The motor never accepts an `inference_case` that is not activated by `motor_013`.
- The motor never accepts inputs without a matching `PhaseContract` from `motor_001`.
- The motor never accepts evidence references without provenance or lineage references.
- The motor never produces final reports, report packages, output blocks, rendered documents, verified claims, or field evidence.
- The motor never modifies upstream cases, contracts, source records, normalized records, quality records, or validation data.
- The motor never treats synthetic support as evidentiary; if synthetic support is present without real evidence, the inference state remains `hypothesis_only`.
- The motor never resolves conflicts by choosing a winner without a deterministic rule authorized by the phase contract.

## validations
- Before processing, every `inference_case.case_id` must be a non-empty string and unique within the batch.
- Before processing, every `inference_case.case_status` must equal `activated`.
- Before processing, every case `phase_id` must match a `PhaseContract.phase_id` whose `allowed_inputs` include `inference_cases`.
- Before processing, the matching phase contract must allow `inference_record`, `tension_record`, `gap_agenda`, and `validation_agenda` in `allowed_outputs`.
- Before processing, every `evidence_refs` entry must include an identifier, an evidence level or source class, and a provenance or lineage reference.
- Before processing, any case with contradictory contract metadata is rejected with `PHASE_CONTRACT_VIOLATION`.
- Before emitting output, every output record must include `motor_id`, `case_id`, `phase_contract_ref`, `contract_version`, `lineage_refs`, `rule_version`, and `created_at`.
- Before emitting output, every `tension_record` must reference a valid `inference_record.inference_id`.
- Before emitting output, every `gap_agenda` item must identify the missing condition, the affected inference or tension, and the required downstream action.
- Before emitting output, every `validation_agenda` item must identify the required evidence level, the reason validation is needed, and the downstream handoff target.
