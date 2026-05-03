# Conceptual Schema — TAD Preliminary Prioritization Engine

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

## entities
PreliminaryPriorityRegister: the main output register containing the ordered list of active inference cases and the preliminary, non-evidentiary priority assigned to each case.

RankingBasis: the traceable explanation object that records which synthetic support signals, phase constraints, version references, and deterministic weighting rules produced the rank order.

RankUncertaintyRecord: the uncertainty object that records missing, conflicting, weak, tied, or sensitivity-prone ranking conditions that limit interpretability of the preliminary order.

## relationships
PreliminaryPriorityRegister -> RankingBasis (each register must reference the basis used to construct its rank order).

PreliminaryPriorityRegister -> RankUncertaintyRecord (each register must reference uncertainty conditions for the ranking as a whole and for affected entries).

RankingBasis -> synthetic_ml_support_register (basis cites source synthetic support items used as subordinate ranking signals).

RankingBasis -> inference_cases (basis maps each ranked position to one active inference case).

RankingBasis -> phase_contracts (basis records phase constraints that allowed or limited preliminary prioritization).

RankingBasis -> version_records (basis records immutable versions of input registers and contracts used for rebuild).

RankUncertaintyRecord -> PreliminaryPriorityRegister (uncertainty annotations qualify entries in the emitted register and prevent overinterpretation).

## key_fields
PreliminaryPriorityRegister:
- `register_id`: string
- `created_at`: datetime string
- `ranked_cases`: list of objects with `inference_case_id`, `rank_position`, `priority_band`, and `preliminary_score`
- `source_problem_ref`: string
- `expert_spec_ref`: string
- `intended_use`: string, always `preliminary_support`
- `domain_validity_limits`: string
- `limitations_note`: string
- `ranking_basis_ref`: string
- `rank_uncertainty_ref`: string
- `requires_real_evidence`: list of strings
- `synthetic_support_flag`: boolean, always true
- `non_evidentiary_flag`: boolean, always true
- `rank_is_preliminary`: boolean, always true

RankingBasis:
- `basis_id`: string
- `source_problem_ref`: string
- `expert_spec_ref`: string
- `intended_use`: string, always `preliminary_support`
- `domain_validity_limits`: string
- `limitations_note`: string
- `source_support_refs`: list of strings
- `source_case_refs`: list of strings
- `phase_contract_refs`: list of strings
- `version_record_refs`: list of strings
- `weighting_rule`: string
- `tie_break_rule`: string
- `excluded_signal_reasons`: list of strings

RankUncertaintyRecord:
- `uncertainty_id`: string
- `source_problem_ref`: string
- `expert_spec_ref`: string
- `intended_use`: string, always `preliminary_support`
- `domain_validity_limits`: string
- `limitations_note`: string
- `affected_case_refs`: list of strings
- `missing_signal_refs`: list of strings
- `conflicting_signal_notes`: list of strings
- `tie_groups`: list of lists of strings
- `rank_separation_notes`: list of strings
- `limitations_note`: string
