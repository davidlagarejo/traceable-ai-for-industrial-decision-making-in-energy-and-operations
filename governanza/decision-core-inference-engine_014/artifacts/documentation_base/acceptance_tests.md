# Acceptance Tests — Decision Core / Inference Engine

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

## happy_path
Input: `inference_cases` contains case `IC-014-001` with `case_status = activated`, `phase_id = phase_2`, `analysis_question = "Does facility FAC-123 require validation of backup power resilience?"`, `evidence_refs = ["facility_prior:FAC-123", "library_object:LIB-456"]`, and non-empty `lineage_refs`. `phase_contracts` contains contract `PC-PHASE-2-v1` allowing `inference_cases` as input and allowing `inference_record`, `tension_record`, `gap_agenda`, and `validation_agenda` as outputs.

Action: the motor validates the case and contract, applies deterministic inference rules, records that the available evidence supports a bounded inference about backup power risk, detects that field validation is still required, and emits structured outputs.

Expected output: one `InferenceRecord` with `case_id = IC-014-001`, `phase_contract_ref = PC-PHASE-2-v1`, `inference_state = bounded_inference`, evidence and lineage references preserved; one `Tension` of type `missing_evidence` if no field measurement exists; one `GapAgenda` item requesting site-level backup power evidence; and one `ValidationAgenda` item targeted to downstream validation or verification flow.

## edge_cases
- Sparse but valid input: a case has one valid evidence reference, a valid activation record, and a matching phase contract. Correct behavior is to emit an `InferenceRecord` with `inference_state = blocked_by_gap` or `hypothesis_only` according to evidence level, plus a `GapAgenda`; the motor must not invent missing evidence.
- Conflicting evidence input: one evidence reference suggests adequate resilience while another suggests a possible failure condition. Correct behavior is to emit a `Tension` with `tension_type = conflict`, preserve both source references, and create a validation item; the motor must not silently choose one source.
- Synthetic-only support: a case contains only support marked as synthetic or non-evidentiary. Correct behavior is to emit `InferenceRecord.inference_state = hypothesis_only` and a validation agenda requiring `validation_data` or `field_evidence`.
- Empty tension case: a case has sufficient consistent real evidence for a bounded inference and no detected conflict. Correct behavior is to emit an empty `tension_record` list and still preserve lineage in the `InferenceRecord`.

## rejection_criteria
- Reject with `INFERENCE_CASE_NOT_ACTIVATED` when any case has `case_status` other than `activated`.
- Reject with `PHASE_CONTRACT_MISSING` when no matching phase contract exists for the case `phase_id`.
- Reject with `PHASE_CONTRACT_VIOLATION` when the phase contract does not allow one of the required output classes.
- Reject with `PROVENANCE_REQUIRED` when an evidence reference lacks provenance or lineage.
- Reject with `CASE_ID_REQUIRED` when `case_id` is null, empty, or duplicated within the processing batch.
