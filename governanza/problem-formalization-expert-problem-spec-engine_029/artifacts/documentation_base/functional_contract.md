# Functional Contract — Problem Formalization / Expert Problem Spec Engine

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

## inputs
- `inference_cases`: list[InferenceCase] -- source `motor_013`; activated inference cases with `inference_case_id`, phase reference, question, trigger context, open assumptions, current ambiguity status and provenance.
- `phase_contracts`: dict[str, PhaseContract] -- source `motor_001`; permitted phase boundaries, allowed handoffs, input/output classes and epistemic limits for the active case.
- `version_records`: list[VersionRecord] -- source `motor_002`; lineage, object version, dependency version and rebuild metadata for each source object used in the spec.
- `canonical_taxonomy`: dict[str, CanonicalTerm] -- source `motor_003`; canonical entity names, aliases, variable classes, units, allowed categories and semantic boundaries.

## outputs
- `expert_problem_spec`: ExpertProblemSpec markdown/json-compatible record -- consumed by `motor_030`; formal problem contract with `spec_id`, `source_problem_ref`, `problem_class`, expert assumptions, domain constraints, valid parameter space, lineage references, `non_evidentiary_flag=true`, `intended_use=exploration`, `domain_validity_limits` and `limitations_note`.
- `ambiguity_register`: AmbiguityRegister markdown/json-compatible record -- consumed by `motor_029` gate checks and downstream governance; list of ambiguities with severity, resolution status, owner, impact if unresolved and whether the spec can advance.
- `parameter_constraints`: list[ParameterConstraint] -- consumed by `motor_030`; deterministic constraints for synthetic generation including parameter name, type, allowed range or categories, unit, source rationale, compatibility rules and uncertainty notes.

## limits
- The motor never accepts an `inference_case` without `inference_case_id`, activation status, provenance and phase reference.
- The motor never processes an input whose current ambiguity state includes unresolved critical items.
- The motor never accepts taxonomy terms that cannot be mapped to `canonical_taxonomy` without emitting an ambiguity item.
- The motor never produces synthetic datasets, generated rows, trained models, metrics, rankings, report claims or validation evidence.
- The motor never emits an output without `non_evidentiary_flag=true`, `intended_use=exploration`, `source_problem_ref`, `domain_validity_limits` and `limitations_note`.
- The motor never changes source objects; any correction to source cases, contracts, versions or taxonomy must happen in the producing motor.

## validations
- Before processing, each `inference_case` must have status `activated` or equivalent active state, a non-empty `inference_case_id`, traceable provenance and a phase allowed by `phase_contracts`.
- Before processing, dependency versions from `version_records` must be present for the case, phase contract and taxonomy snapshot used by the spec.
- Before processing, any input ambiguity marked `critical` must have `resolution_status=resolved`; otherwise the motor emits `ERR_CRITICAL_AMBIGUITY_UNRESOLVED`.
- During formalization, every domain term, unit, category and parameter name must either resolve to `canonical_taxonomy` or be recorded in `ambiguity_register`.
- Before output, `expert_problem_spec.problem_class` must be one of the allowed problem classes for the synthetic chain, such as `classification_binary`, `classification_multiclass`, `regression_continuous`, `ranking`, `clustering_exploratory`, `anomaly_detection`, `survival_hazard` or `sensitivity_analysis`.
- Before output, every `ParameterConstraint` must include `constraint_id`, `parameter_name`, `value_type`, allowed domain, source rationale and uncertainty treatment.
- Before output, every emitted object must carry `non_evidentiary_flag=true`, `intended_use=exploration`, `source_problem_ref`, `domain_validity_limits` and `limitations_note`.
- Before handoff to `motor_030`, `ambiguity_register` must contain no unresolved item with `impact_if_unresolved=critical`.
