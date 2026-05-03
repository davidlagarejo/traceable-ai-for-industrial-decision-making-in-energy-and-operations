# Test Spec — Problem Formalization / Expert Problem Spec Engine

Motor ID: motor_029

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir inference cases activados en especificaciones formales del problema: conocimiento experto, restricciones reales y supuestos explícitos del dominio.
why_it_exists:  Un dataset sintético sin especificación formal es ruido estructurado. Este motor produce el contrato del que depende toda la cadena sintética.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003)
key_outputs:    expert_problem_spec, ambiguity_register, parameter_constraints
key_objects:    ExpertProblemSpec, AmbiguityRegister, ParameterConstraint
what_not_to_do: No genera datos sintéticos. No corre ML. No puede ejecutarse sobre inference_cases con ambiguity_register crítico no resuelto.
design_notes:   Prerequisito obligatorio de toda la cadena sintética. No genera datos. No diseña modelos. Su output es non_evidentiary_flag=true.
epistemic_flags: non_evidentiary_flag=true, intended_use=exploration

All placeholder markers in this document have been replaced with concrete test content.
-->

## happy_path
Input bundle:
- `inference_cases` contains one active case:
  - `inference_case_id="IC-029-001"`
  - `status="activated"`
  - `phase_ref="PC-SYNTH-FORMALIZATION-v1"`
  - `problem_statement="Classify whether a facility scenario has failure_event=true from capacity_kw and inspection_interval_days."`
  - `problem_class_hint="classification_binary"`
  - `target_variable_ref="CT-FAILURE-EVENT"`
  - `expert_assumptions=["Inspection interval is measured in days.", "Capacity is measured in kW at the facility boundary."]`
  - `domain_terms=["facility", "capacity_kw", "inspection_interval_days", "failure_event"]`
  - `source_provenance_refs=["SRC-FIELD-PROTOCOL-17", "SRC-EXPERT-REVIEW-029-A"]`
  - `input_ambiguities=[]`
- `phase_contracts["PC-SYNTH-FORMALIZATION-v1"]` permits formalization for the synthetic chain and declares `motor_029` as the producer of expert problem specifications.
- `version_records` contains governed records for `IC-029-001`, `PC-SYNTH-FORMALIZATION-v1` and taxonomy snapshot `TAX-2026-04-01`.
- `canonical_taxonomy` maps `facility`, `capacity_kw`, `inspection_interval_days` and `failure_event` to canonical term ids `CT-FACILITY`, `CT-CAPACITY-KW`, `CT-INSPECTION-INTERVAL-DAYS` and `CT-FAILURE-EVENT`.

Expected behavior:
- The motor emits one `expert_problem_spec` with `spec_id="EPS-IC-029-001-v1"`, `source_problem_ref="IC-029-001"`, `phase_contract_ref="PC-SYNTH-FORMALIZATION-v1"`, `taxonomy_snapshot_ref="TAX-2026-04-01"`, `problem_class="classification_binary"`, `target_variable_ref="CT-FAILURE-EVENT"` and `handoff_allowed=true`.
- The spec includes non-empty `version_record_refs`, `lineage_refs`, `provenance_refs`, `domain_validity_limits`, `limitations_note`, `source_ref`, `produced_by_motor="motor_029"`, `produced_at`, `version_id`, `created_at`, `updated_at` and `version_hash`.
- The spec carries `non_evidentiary_flag=true` and `intended_use="exploration"` and does not claim field validation or decision-grade evidence.
- The motor emits one `ambiguity_register` for the same `spec_id` with `has_unresolved_critical=false`, `highest_unresolved_impact="none"`, `blocking_item_refs=[]`, `handoff_allowed=true`, `non_evidentiary_flag=true` and `intended_use="exploration"`.
- The motor emits three `parameter_constraints`: `capacity_kw` with a numeric range and unit `kW`, `inspection_interval_days` with an integer range and unit `days`, and `failure_event` with a boolean domain. Each constraint has `constraint_id`, `canonical_term_ref`, `value_type`, `allowed_domain`, `constraint_rationale`, `uncertainty_treatment`, `source_problem_ref`, `source_ref`, `produced_by_motor="motor_029"`, `non_evidentiary_flag=true` and `intended_use="exploration"`.

## sparse_case
Input bundle:
- `inference_case_id="IC-029-002"` is active, has phase `PC-SYNTH-FORMALIZATION-v1`, provenance refs, version records and taxonomy snapshot `TAX-2026-04-01`.
- The case has a clear target `failure_event` and one usable explanatory variable `inspection_interval_days`.
- Optional fields are absent: there is no secondary variable list, no expert owner, no prior `parent_id`, no compatibility rules and no resolved ambiguity notes.
- The source case declares `expert_assumptions=[]` rather than omitting the field.

Expected behavior:
- The motor emits a narrow `expert_problem_spec` with `source_problem_ref="IC-029-002"`, `problem_class="classification_binary"`, `target_variable_ref="CT-FAILURE-EVENT"`, `expert_assumptions=[]`, `parent_id=null`, `handoff_allowed=true`, complete lineage and the required epistemic flags.
- The motor emits `parameter_constraints` only for `inspection_interval_days` and `failure_event`; absent optional variables are not invented.
- The `ambiguity_register.items` list is empty when no ambiguity exists, or contains only non-critical items if the case explicitly signals limited domain coverage. In either case, `has_unresolved_critical=false`.
- The `domain_validity_limits` explicitly state that the spec is limited to the declared variable and target, rather than expanding the domain to all facility conditions.
- No synthetic rows, model names, model metrics, rankings or validation claims are produced.

## malformed_input
Malformed cases and required rejection:
- Missing required identifier: if the case omits `inference_case_id` or provides it as an empty string, reject the bundle with `ERR_MISSING_PROVENANCE`. No partial `ExpertProblemSpec` may be persisted.
- Wrong activation state: if `status="draft"` or `status="closed"` instead of an active state, reject with `ERR_INFERENCE_CASE_NOT_ACTIVE`.
- Missing version lineage: if `version_records` lacks records for the source case, phase contract or taxonomy snapshot, reject with `ERR_MISSING_PROVENANCE`.
- Invalid phase authority: if `phase_contracts["PC-SYNTH-FORMALIZATION-v1"]` does not permit synthetic formalization or does not authorize `motor_029`, reject with `ERR_PHASE_CONTRACT_VIOLATION`.
- Critical unresolved ambiguity: if an input ambiguity has `impact_if_unresolved="critical"` and `resolution_status` is `open` or `deferred`, reject with `ERR_CRITICAL_AMBIGUITY_UNRESOLVED`.
- Invalid field type: if `canonical_taxonomy` is provided as a list instead of a mapping keyed by canonical term or alias, reject with `ERR_INVALID_INPUT_TYPE`.
- Invalid problem class: if the derived or supplied problem class is `causal_inference`, `forecasting_unbounded` or any value outside the schema enum, reject with `ERR_INVALID_PROBLEM_CLASS`.
- Missing epistemic flags at output assembly: if the runtime cannot attach `non_evidentiary_flag=true`, `intended_use="exploration"`, `source_problem_ref`, `domain_validity_limits` and `limitations_note` to every emitted object, reject with `ERR_EPISTEMIC_FLAGS_MISSING`.

For every malformed case, the motor must leave upstream `inference_cases`, `phase_contracts`, `version_records` and `canonical_taxonomy` unchanged and must not silently coerce wrong types into accepted values.

## edge_cases
- Unknown required taxonomy term: input case `IC-029-003` uses `plant_size` as a required parameter while taxonomy snapshot `TAX-2026-04-01` has no approved alias for it. Correct behavior is to record an `AmbiguityItem` with `field_ref="parameter_constraints.plant_size.canonical_term_ref"`, `source_input_ref="IC-029-003.plant_size"`, `impact_if_unresolved="critical"`, `resolution_status="open"` and `blocks_handoff=true`; the owning register has `has_unresolved_critical=true`, `blocking_item_refs` containing that item and `handoff_allowed=false`. The spec either is not emitted for handoff or is emitted only as a blocked non-handoffable draft with `handoff_allowed=false` and `handoff_block_reason="critical_ambiguity_unresolved"`.
- Very wide numeric range: input case `IC-029-004` defines `inspection_interval_days` as `1..3650`. Correct behavior is to preserve the full allowed domain in the `ParameterConstraint`, attach an explicit `uncertainty_treatment` explaining that downstream generation must sample across a very broad expert range, and create a high-severity ambiguity item with `impact_if_unresolved="material"` unless the source case justifies the range. Handoff remains allowed only when no critical ambiguity exists.
- Exploratory class without target: input case `IC-029-005` declares `problem_class_hint="clustering_exploratory"` with no target variable. Correct behavior is to emit `target_variable_ref=null`, keep `problem_class="clustering_exploratory"`, require at least one canonical parameter constraint and set `handoff_allowed=true` only when lineage, provenance, taxonomy mappings and epistemic fields are complete.
- Rebuild with same material inputs: re-running `IC-029-001` with identical case content, phase contract, taxonomy snapshot and version records must reproduce the same canonical ids and `version_hash` values for material content. Timestamps may differ only where excluded from the material hash. No duplicate incompatible spec may be created for the same input version set.
- Rebuild after material source change: if `IC-029-001` receives a governed source update that changes `inspection_interval_days` from `7..90` to `14..180`, the motor emits a new spec version with a new `version_id`, new `version_hash` and `parent_id` referencing the prior `ExpertProblemSpec.record_id`. It must not overwrite the prior version or mutate existing constraints silently.

## pass_criteria
A test passes when all of these observable conditions hold:
- Every accepted run emits exactly one coherent `ExpertProblemSpec`, one owning `AmbiguityRegister` and the expected `ParameterConstraint` records for the source case.
- All emitted objects include `source_problem_ref`, `source_ref`, `produced_by_motor="motor_029"`, `produced_at`, `non_evidentiary_flag=true`, `intended_use="exploration"`, non-empty `domain_validity_limits` and non-empty `limitations_note`.
- `ExpertProblemSpec.version_record_refs`, `lineage_refs` and `provenance_refs` contain the source case, phase contract and taxonomy version records needed to rebuild the output.
- `ExpertProblemSpec.problem_class` is one of the allowed schema enum values and `target_variable_ref` is null only for a problem class that permits no target.
- Every `ParameterConstraint` has a canonical taxonomy reference, value type, structured `allowed_domain`, required flag, rationale, uncertainty treatment and consistent `spec_id`.
- Handoff is allowed only when `AmbiguityRegister.has_unresolved_critical=false` and no ambiguity item with `impact_if_unresolved="critical"` remains unresolved.
- Rejected malformed inputs return the specified structured error and persist no partial handoffable output.
- The motor does not generate synthetic datasets, train or select ML models, emit model metrics, validate claims against field data or mutate upstream source objects.

## fail_criteria
A test fails when any of these observable conditions are detected:
- Any emitted object lacks `non_evidentiary_flag=true`, `intended_use="exploration"`, `source_problem_ref`, `domain_validity_limits` or `limitations_note`.
- A spec is marked `handoff_allowed=true` while its ambiguity register has `has_unresolved_critical=true` or unresolved ambiguity items with `impact_if_unresolved="critical"`.
- A required taxonomy term, unit, category or parameter name is accepted without a `canonical_term_ref` and without a corresponding ambiguity item.
- The motor accepts an inactive case, a case without required provenance, missing dependency version records or a phase contract that does not authorize synthetic formalization.
- The motor silently coerces malformed input types, fills missing required source identifiers with generated placeholders, or rewrites upstream source objects.
- The output includes generated synthetic rows, sampling runs, ML model choices, performance metrics, rankings, causal conclusions, field-evidence claims or decision-grade validation.
- A rebuild with identical material inputs changes canonical identifiers or material `version_hash` values; or a rebuild after material change overwrites the prior version instead of using `parent_id` lineage.
- The implementation reports success while leaving `ExpertProblemSpec`, `AmbiguityRegister` or `ParameterConstraint` references inconsistent with each other.
