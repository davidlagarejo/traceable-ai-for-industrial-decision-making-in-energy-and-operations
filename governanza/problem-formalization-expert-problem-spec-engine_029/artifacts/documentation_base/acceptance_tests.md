# Acceptance Tests — Problem Formalization / Expert Problem Spec Engine

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

All placeholder markers in this document have been replaced with concrete content.
-->

## happy_path
Input: `inference_case_id="IC-029-001"` is active, references phase `"synthetic_formalization_allowed"`, has no unresolved critical ambiguity, and uses taxonomy terms `facility`, `capacity_kw`, `failure_event` and `inspection_interval_days` that exist in `canonical_taxonomy`. Version records exist for the inference case, phase contract and taxonomy snapshot.

Action: the motor formalizes the case as a `classification_binary` problem: predict whether a synthetic facility scenario belongs to class `failure_event=true` under declared capacity and inspection interval constraints.

Expected output: one `expert_problem_spec` with `spec_id="EPS-IC-029-001-v1"`, `source_problem_ref="IC-029-001"`, lineage refs to all input versions, `non_evidentiary_flag=true`, `intended_use=exploration`, explicit `domain_validity_limits` and `limitations_note`; one `ambiguity_register` with `has_unresolved_critical=false`; and `parameter_constraints` for `capacity_kw`, `inspection_interval_days` and `failure_event`.

## edge_cases
- Sparse but valid case: the inference case contains only one usable domain variable plus a clear binary target. Correct behavior is to emit a narrow `expert_problem_spec`, record limited `domain_validity_limits`, emit minimal constraints for the known variable and target, and mark unresolved non-critical gaps in `ambiguity_register`.
- Unknown taxonomy alias: the inference case uses `"plant_size"` while `canonical_taxonomy` contains only `"facility_capacity_kw"` and no approved alias. Correct behavior is to emit an ambiguity item for the unmapped term and block handoff if the term is required for the target or parameter constraints.
- Wide parameter range: the expert input gives `inspection_interval_days` as `1..3650`. Correct behavior is to preserve the range, attach an uncertainty treatment, and record a high-severity ambiguity if the range makes the generation domain too broad for a meaningful synthetic run.

## rejection_criteria
- Reject with `ERR_CRITICAL_AMBIGUITY_UNRESOLVED` when the input case or derived register has any item with `impact_if_unresolved=critical` and `resolution_status` not equal to `resolved`.
- Reject with `ERR_MISSING_PROVENANCE` when the inference case lacks `inference_case_id`, source provenance, phase reference or required version records.
- Reject with `ERR_PHASE_CONTRACT_VIOLATION` when `phase_contracts` do not permit synthetic formalization for the case's current phase.
- Reject with `ERR_EPISTEMIC_FLAGS_MISSING` when the motor cannot attach `non_evidentiary_flag=true`, `intended_use=exploration`, `source_problem_ref`, `domain_validity_limits` or `limitations_note` to every output object.
