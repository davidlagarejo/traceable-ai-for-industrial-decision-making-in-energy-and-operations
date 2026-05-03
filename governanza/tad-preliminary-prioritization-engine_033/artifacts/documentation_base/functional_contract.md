# Functional Contract — TAD Preliminary Prioritization Engine

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

## inputs
synthetic_ml_support_register: structured register — source motor_032; contains synthetic support signals for inference cases with `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `intended_use=preliminary_support`, `source_problem_ref`, `domain_validity_limits`, and `limitations_note`.

inference_cases: list of structured inference case records — source motor_013; contains active case identifiers, case status, case scope, current epistemic state, and links to claims or questions under analysis.

phase_contracts: list of phase contract records — source motor_001; defines phase authority, allowed handoffs, decision boundaries, and constraints that the preliminary ranking must respect.

version_records: list of version and lineage records — source motor_002; provides immutable references to input versions, registry versions, and rebuild metadata used for traceable ranking.

## outputs
preliminary_priority_register: structured register — destination downstream review, Decision Core as subordinate signal, and human prioritization review; contains ordered case entries, rank position, preliminary score band, `ranking_basis`, `rank_uncertainty_record` reference, `requires_real_evidence`, `source_problem_ref`, `expert_spec_ref`, `intended_use=preliminary_support`, `domain_validity_limits`, `limitations_note`, and mandatory flags `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`.

ranking_basis: structured explanation object — destination preliminary_priority_register and conformance review; records signal names, source object references, weighting rule, phase constraints, excluded signals, tie handling, and the reason each case received its position; includes the same epistemic scope fields as the register.

rank_uncertainty_record: structured uncertainty object — destination preliminary_priority_register and downstream review; records missing signals, weak rank separation, conflicting synthetic signals, sensitivity notes, tie groups, and conditions requiring real evidence before any decision use; includes the same epistemic scope fields as the register.

## limits
- The motor never accepts a `synthetic_ml_support_register` that lacks `synthetic_support_flag=true` or `non_evidentiary_flag=true`.
- The motor never accepts inactive, closed, archived, or unidentified inference cases as rankable entries.
- The motor never accepts support signals whose `source_problem_ref` cannot be matched to an active inference case.
- The motor never treats `synthetic_support` as `field_evidence`, `validation_data`, or direct proof of a claim.
- The motor never produces TAD final, inference case closure, decision-grade evidence, or field validation.
- The motor never emits a ranking without `rank_is_preliminary=true` and explicit `requires_real_evidence`.
- The motor never emits an output object without `source_problem_ref`, `expert_spec_ref`, `intended_use`, `domain_validity_limits`, and `limitations_note`.
- The motor never mutates source registers, case records, phase contracts, or version records.

## validations
- Before processing, every synthetic support item must include `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `source_problem_ref`, `intended_use`, `domain_validity_limits`, and `limitations_note`.
- Before processing, every ranked case must exist in `inference_cases`, have active status, and have a stable `inference_case_id`.
- Before processing, every source reference used in ranking must resolve to a `version_records` entry or be rejected with a provenance error.
- Before processing, the phase contract for each case must permit preliminary prioritization as a non-final analytic signal.
- Before emitting output, every `preliminary_priority_register` entry must include `inference_case_id`, `rank_position`, `priority_band`, `ranking_basis_ref`, `rank_uncertainty_ref`, `requires_real_evidence`, `source_problem_ref`, `expert_spec_ref`, `intended_use=preliminary_support`, `domain_validity_limits`, `limitations_note`, and lineage references.
- Before emitting output, all outputs must include `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`, `source_problem_ref`, `expert_spec_ref`, `intended_use`, `domain_validity_limits`, and `limitations_note`.
- Before emitting output, ties, missing support, conflicting signals, or low rank separation must be represented in `rank_uncertainty_record`; they must not be silently collapsed.
- Before emitting output, the register must state that it cannot close inference cases, cannot serve as TAD final, and always requires review with real evidence.
