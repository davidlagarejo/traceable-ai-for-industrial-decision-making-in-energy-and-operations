# Operational Rules — TAD Preliminary Prioritization Engine

Motor ID: motor_033

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ordenar preliminarmente inference cases activos usando señales sintéticas del motor_032.
why_it_exists:  Cuando hay múltiples inference cases activos compitiendo por recursos, se necesita una señal preliminar de orden de atención trazable y no arbitraria.
key_inputs:     synthetic_ml_support_register (motor_032), inference_cases (motor_013), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    preliminary_priority_register, ranking_basis, rank_uncertainty_record
key_objects:    PreliminaryPriorityRegister, RankingBasis, RankUncertaintyRecord
what_not_to_do: No puede ser TAD final. No puede usarse como evidencia para cerrar inference cases. Siempre requiere revisión con evidencia real.
design_notes:   Output es preliminary_priority_register, nunca TAD final. El ranking es exploratorio.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true, rank_is_preliminary=true

All sections below are completed with concrete content for this motor.
-->

## rules
1. The motor must process only active inference cases with stable `inference_case_id` values and must exclude closed, archived, or unidentified cases from ranking.
2. Every synthetic support item used for ranking must carry `synthetic_support_flag=true` and `non_evidentiary_flag=true`; any item without both flags is invalid.
3. Every emitted `preliminary_priority_register`, `ranking_basis`, and `rank_uncertainty_record` must carry `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`, `source_problem_ref`, `expert_spec_ref`, `intended_use=preliminary_support`, `domain_validity_limits`, and `limitations_note`.
4. The ranking must be reproducible from recorded inputs, version references, phase contracts, and the deterministic weighting or ordering rule documented in `ranking_basis`.
5. The motor must preserve lineage from every ranked case back to the source support item, inference case record, phase contract, and version record used.
6. The motor must represent missing support, conflicting support, weak separation, and ties in `rank_uncertainty_record` instead of hiding those conditions.
7. The motor must include `requires_real_evidence` in the register so downstream consumers know what real evidence would confirm, revise, or invalidate the preliminary order.
8. The motor must label the output as a subordinate exploration signal and must not allow it to be consumed as final decision evidence.

## invariants
- Source input objects remain immutable; the motor reads them and emits derived registers only.
- `synthetic_support_flag`, `non_evidentiary_flag`, and `rank_is_preliminary` are always true on motor_033 outputs, while `intended_use` remains `preliminary_support`.
- No output from this motor changes an inference case status, phase contract, version record, claim status, or evidentiary level.
- Every ranked entry has a non-empty `inference_case_id`, `ranking_basis_ref`, and lineage reference.
- Every output object has non-empty `source_problem_ref`, `expert_spec_ref`, `domain_validity_limits`, and `limitations_note`.
- Every ranking run has a rebuild path through `version_record_refs`.
- Every register states that real evidence review is required before any decision-grade use.

## forbidden_operations
- Producing TAD final or any final operational decision.
- Closing, approving, rejecting, or escalating an inference case as a direct consequence of the ranking.
- Using synthetic support as evidence to close inference cases.
- Substituting Validation Data Bridge, Verification Bridge, field evidence, or validation data.
- Promoting synthetic support to `decision_grade`, `field_evidence`, or `validation_data`.
- Removing or weakening `synthetic_support_flag=true`, `non_evidentiary_flag=true`, or `rank_is_preliminary=true`.
- Removing `source_problem_ref`, `expert_spec_ref`, `intended_use`, `domain_validity_limits`, or `limitations_note` from any motor_033 output.
- Rewriting source support records, inference case records, phase contracts, or version records.
- Suppressing uncertainty, ties, missing signal notes, or limitations to make the rank order appear more certain.
- Treating ranking position as causal proof, truth score, or claim validity score.
