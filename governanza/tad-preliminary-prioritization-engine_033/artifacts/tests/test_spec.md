# Test Spec — TAD Preliminary Prioritization Engine

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

All test sections below are completed with concrete content for this motor.
-->

## happy_path
Scenario: three active inference cases have valid synthetic support from motor_032 and complete lineage.

Input:
- `synthetic_ml_support_register.register_id = "SMSR-033-HP-001"` with three support items:
  - `SUP-IC-200`: `source_problem_ref="IC-200"`, `expert_spec_ref="EPS-200"`, `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `intended_use="preliminary_support"`, `domain_validity_limits="synthetic scenario bundle SB-200 only"`, `limitations_note="Synthetic support only; requires real evidence."`, `priority_signal=0.86`, `support_quality="strong"`, `version_record_ref="VR-SUP-200"`.
  - `SUP-IC-100`: `source_problem_ref="IC-100"`, `expert_spec_ref="EPS-100"`, `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `intended_use="preliminary_support"`, `domain_validity_limits="synthetic scenario bundle SB-100 only"`, `limitations_note="Synthetic support only; requires real evidence."`, `priority_signal=0.63`, `support_quality="moderate"`, `version_record_ref="VR-SUP-100"`.
  - `SUP-IC-300`: `source_problem_ref="IC-300"`, `expert_spec_ref="EPS-300"`, `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `intended_use="preliminary_support"`, `domain_validity_limits="synthetic scenario bundle SB-300 only"`, `limitations_note="Synthetic support only; requires real evidence."`, `priority_signal=0.41`, `support_quality="limited"`, `version_record_ref="VR-SUP-300"`.
- `inference_cases` contains `IC-100`, `IC-200`, and `IC-300`, each with `status="active"` and stable `inference_case_id`.
- `phase_contracts` contains `PC-PRELIM-001` with `allows_preliminary_prioritization=true` and `forbids_final_decision=true`.
- `version_records` resolves `VR-SUP-100`, `VR-SUP-200`, `VR-SUP-300`, the three case version refs, `PC-PRELIM-001`, and the motor_033 schema version.

Expected behavior:
- The motor emits one `preliminary_priority_register`, one `ranking_basis`, and one `rank_uncertainty_record`.
- `ranked_cases` are ordered as `IC-200` at `rank_position=1`, `IC-100` at `rank_position=2`, and `IC-300` at `rank_position=3` using the deterministic rule recorded in `ranking_basis.weighting_rule`.
- The register, basis, and uncertainty record all contain `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`, `intended_use="preliminary_support"`, non-empty `source_problem_ref`, `expert_spec_ref`, `domain_validity_limits`, and `limitations_note`.
- Each ranked entry contains `ranking_basis_ref`, `rank_uncertainty_ref`, `source_support_refs`, `phase_contract_refs`, `version_record_refs`, `requires_real_evidence`, and `entry_limitations_note`.
- `cannot_substitute` includes `TAD_final`, `inference_case_closure`, `field_evidence`, `validation_data`, `Validation Data Bridge`, and `Verification Bridge`.
- The motor does not mutate the source support register, inference case records, phase contracts, or version records.

## sparse_case
Scenario: active cases exist, but synthetic support is incomplete or lacks optional explanatory detail.

Input:
- `inference_cases` contains `IC-410`, `IC-420`, and `IC-430`, all with `status="active"`.
- `synthetic_ml_support_register.register_id = "SMSR-033-SP-001"` contains:
  - `SUP-IC-410` with all mandatory epistemic fields and `priority_signal=0.72`, but no optional free-text analyst note.
  - `SUP-IC-420` with all mandatory epistemic fields and `priority_signal=0.71`, but no optional secondary scenario label.
  - No support item for `IC-430`.
- `phase_contracts` permits preliminary prioritization, and `version_records` resolves all provided support, case, contract, and schema references.

Expected behavior:
- The motor does not fail because optional descriptive fields are absent.
- The emitted register ranks `IC-410` and `IC-420`; because the score separation is weak, both entries receive a conservative `priority_band` and the weak separation is recorded in `rank_uncertainty_record.rank_separation_notes`.
- `IC-430` is not silently ranked as if support existed. It is recorded in `rank_uncertainty_record.insufficient_support_case_refs` and either appears in `excluded_case_refs` with reason `insufficient_synthetic_signal` or appears as an explicitly low-confidence entry, according to the deterministic rule in `ranking_basis`.
- `rank_uncertainty_record.uncertainty_level` is at least `moderate`, and `requires_real_evidence` names the real observations needed to resolve the sparse support condition.
- All emitted objects keep the mandatory synthetic epistemic flags and `rank_is_preliminary=true`.

## malformed_input
The motor must reject malformed or contract-violating input before emitting any register.

Cases:
- Missing epistemic flags: a support item for `IC-501` omits `synthetic_support_flag` or sets `non_evidentiary_flag=false`. Expected rejection: `ERR_MISSING_EPISTEMIC_FLAGS`; no `preliminary_priority_register` is emitted.
- Wrong type: `synthetic_ml_support_register` is supplied as a list instead of an object with `register_id`, support items, and lineage references. Expected rejection: `ERR_INVALID_SUPPORT_REGISTER_SHAPE`; no output objects are emitted.
- Inactive case: support item `SUP-IC-502` references `source_problem_ref="IC-502"`, but `inference_cases` marks `IC-502` as `status="closed"`. Expected rejection: `ERR_CASE_NOT_ACTIVE`; the motor must not rank the case.
- Unresolved provenance: support item `SUP-IC-503` references `version_record_ref="VR-MISSING-503"`, which is absent from `version_records`. Expected rejection: `ERR_UNRESOLVED_PROVENANCE`; no partial register is emitted.
- Phase contract blocks use: `phase_contracts` resolves but contains `allows_preliminary_prioritization=false` for the current phase. Expected rejection: `ERR_PHASE_CONTRACT_BLOCKS_PRIORITY`; no ranked output is emitted.
- Final decision requested: request metadata asks for `output_type="TAD_final"` or `close_inference_case=true`. Expected rejection: `ERR_FINAL_DECISION_REQUESTED`; the motor must not produce final decision artifacts.

## edge_cases
1. Exact tie between valid cases:
   - Input: `IC-610` and `IC-620` are active, have valid support, identical `priority_signal=0.80`, equivalent support quality, and matching phase permissions.
   - Expected behavior: the motor records `["IC-610", "IC-620"]` in `rank_uncertainty_record.tie_groups`. If the phase contract allows a deterministic tie-break, the applied rule is recorded in `ranking_basis.tie_break_rule`; otherwise both entries remain a tie group without false precision.

2. Conflicting synthetic signals for one case:
   - Input: `IC-630` has two valid support items, `SUP-IC-630-A` with high preliminary signal under scenario A and `SUP-IC-630-B` with low preliminary signal under scenario B. Both carry mandatory flags and resolvable lineage.
   - Expected behavior: the motor does not average the conflict into a confident score without explanation. `rank_uncertainty_record.conflicting_signal_notes` lists both support refs, the case receives a limited-confidence `priority_band`, and `requires_real_evidence` identifies the field or validation data needed to resolve the conflict.

3. Out-of-scope support:
   - Input: `SUP-IC-640` references active case `IC-640`, but its `domain_validity_limits` do not cover the case scope declared in `inference_cases`.
   - Expected behavior: that signal is excluded from scoring, `ranking_basis.excluded_signal_reasons` records `reason="domain_validity_mismatch"`, and the case is ranked only if another valid support signal remains. If no valid signal remains, the case is recorded as insufficiently supported.

4. Single active case:
   - Input: only `IC-650` is active and has valid support, phase permission, and resolved version records.
   - Expected behavior: the motor may emit a register with one ranked entry at `rank_position=1`, but the output still includes `rank_is_preliminary=true`, `cannot_substitute`, `requires_real_evidence`, and a limitation note stating that the register is not comparative across a broader active case set.

## pass_criteria
A test passes only when all applicable observable conditions are true:
- Required outputs exist when input is valid: `preliminary_priority_register`, `ranking_basis`, and `rank_uncertainty_record`.
- No output is emitted for malformed input cases that require rejection.
- Every emitted object contains `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`, `source_problem_ref`, `expert_spec_ref`, `intended_use="preliminary_support"`, `domain_validity_limits`, and `limitations_note`.
- Every ranked case references an active `inference_case_id`, at least one valid source support item or an explicit insufficient-support treatment, applicable phase contract refs, and resolvable version record refs.
- The order of `ranked_cases` matches the deterministic `ranking_basis.weighting_rule`, including documented tie handling and priority band assignment.
- Ties, sparse support, out-of-scope signals, weak rank separation, and conflicting support appear in `rank_uncertainty_record` or `ranking_basis.excluded_signal_reasons` rather than being hidden.
- `requires_real_evidence` is non-empty at register level and for each ranked entry.
- The source support register, inference cases, phase contracts, and version records are unchanged after the run.
- `cannot_substitute` explicitly prevents use as TAD final, inference case closure, field evidence, validation data, Validation Data Bridge, or Verification Bridge.

## fail_criteria
A test fails if any of the following are observed:
- A valid happy-path input does not emit all three required output objects.
- Any malformed input case emits a partial or complete `preliminary_priority_register` instead of rejecting with the expected structured error.
- Any output lacks `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`, `source_problem_ref`, `expert_spec_ref`, `intended_use`, `domain_validity_limits`, or `limitations_note`.
- A closed, archived, missing, or inactive inference case appears as a rankable entry.
- A support signal without required epistemic flags, outside domain validity, blocked by phase contract, or missing version lineage is used for scoring.
- The motor mutates source support records, inference case states, phase contracts, or version records.
- The output claims to be TAD final, decision-grade evidence, field evidence, validation data, or sufficient to close an inference case.
- Missing support, ties, weak separation, conflicting signals, or excluded signals are absent from both `rank_uncertainty_record` and `ranking_basis`.
- `requires_real_evidence` is empty or replaced by generic text that does not identify what real evidence would confirm, revise, or invalidate the preliminary order.
