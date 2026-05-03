# Failure Modes — TAD Preliminary Prioritization Engine

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

## failure_modes_list
EPISTEMIC_PROMOTION_LEAK: downstream usage treats the preliminary register as evidence, TAD final, or case closure authority despite `non_evidentiary_flag=true`.

MISSING_FLAG_ACCEPTANCE: the motor accepts support records without required synthetic epistemic flags, causing unlabelled synthetic material to enter ranking.

RANK_CERTAINTY_OVERSTATEMENT: ties, weak score separation, sparse support, or conflicting signals are absent from `rank_uncertainty_record`, making the output look more certain than it is.

LINEAGE_BREAK: ranked entries cannot be traced back to source support records, inference cases, phase contracts, and version records.

SCOPE_DRIFT_TO_DECISION_CORE: the motor begins assigning final action, resource allocation, case status, or claim validity instead of producing only a preliminary order of attention.

## anti_patterns
- Treating rank position as proof that a claim is true, false, verified, or ready to close.
- Removing the mandatory epistemic flags to make the register look equivalent to validation data.
- Ranking every active case even when support signals are missing, out of scope, or unresolved.
- Hiding tie groups or uncertainty notes to produce a cleaner stakeholder-facing list.
- Combining this motor with motor_032 or Decision Core logic into one monolithic ranking and decision module.

## degradation_signals
- Increase in ranked entries with empty `ranking_basis_ref`, missing `version_record_refs`, or unresolved source references.
- `rank_uncertainty_record` is empty across many runs even when inputs contain sparse support, ties, or conflicting synthetic signals.
- Outputs lack `requires_real_evidence` or repeat generic limitation text that does not identify evidence needed for each priority group.
- Downstream logs show `preliminary_priority_register` being used to close cases, mark claims decision-grade, or bypass validation bridges.
- Frequent rank churn occurs between runs with unchanged source versions, indicating unstable or undocumented ranking logic.
- Large numbers of excluded signals are not accompanied by explicit exclusion reasons in `ranking_basis`.
