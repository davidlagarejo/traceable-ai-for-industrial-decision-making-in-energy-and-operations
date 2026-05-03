# Acceptance Tests — TAD Preliminary Prioritization Engine

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

## happy_path
Input: `synthetic_ml_support_register` contains support entries for `IC-100`, `IC-200`, and `IC-300`, all with `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `intended_use=preliminary_support`, valid `source_problem_ref`, and version references. `inference_cases` marks all three cases as active. `phase_contracts` permits preliminary prioritization for the current phase, and `version_records` resolves every input reference.

Action: the motor validates flags, active case status, phase authority, and lineage; applies the deterministic ranking basis; records the source signals and weights; and emits the preliminary register.

Expected output: `preliminary_priority_register` ranks `IC-200` first, `IC-100` second, and `IC-300` third according to the declared `ranking_basis`. The register includes `requires_real_evidence`, `ranking_basis_ref`, `rank_uncertainty_ref`, and mandatory flags `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`. The output explicitly states that it is not TAD final and cannot close any inference case.

## edge_cases
- Sparse support: only one active inference case has a matching synthetic support item. Correct behavior: emit a register that ranks the supported case, marks unsupported active cases as `insufficient_synthetic_signal`, and records the missing support in `rank_uncertainty_record`.
- Exact tie: two active cases produce identical preliminary score bands and equivalent support quality. Correct behavior: keep both cases in a tie group, use the documented `tie_break_rule` only if allowed by phase contract, and record the tie in `rank_uncertainty_record`.
- Conflicting support: one case has synthetic signals pointing to high priority and low priority across different scenario assumptions. Correct behavior: do not collapse the conflict into a single confident score; record the conflict and assign a limited-confidence priority band.
- Out-of-scope support: a synthetic support item references a case outside its declared `domain_validity_limits`. Correct behavior: exclude that signal from `ranking_basis`, record the exclusion reason, and rank the case only if other valid signals remain.

## rejection_criteria
- Reject with `ERR_MISSING_EPISTEMIC_FLAGS` when any support item used for ranking lacks `synthetic_support_flag=true` or `non_evidentiary_flag=true`.
- Reject with `ERR_CASE_NOT_ACTIVE` when a candidate ranked entry references an inference case that is closed, archived, missing, or not active.
- Reject with `ERR_UNRESOLVED_PROVENANCE` when a ranking signal, case, phase contract, or version reference cannot be resolved.
- Reject with `ERR_PHASE_CONTRACT_BLOCKS_PRIORITY` when the applicable phase contract does not permit preliminary prioritization for the case.
- Reject with `ERR_FINAL_DECISION_REQUESTED` when the caller requests TAD final, case closure, evidentiary validation, or decision-grade output from this motor.
