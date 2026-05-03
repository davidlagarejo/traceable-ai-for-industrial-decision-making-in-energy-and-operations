# Conceptual Schema — Problem Formalization / Expert Problem Spec Engine

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

## entities
- `ExpertProblemSpec`: formal, versioned problem contract derived from one activated inference case; it defines the problem question, class, assumptions, constraints, validity limits and epistemic flags for synthetic-chain use.
- `AmbiguityRegister`: controlled list of unresolved, resolved or deferred ambiguities discovered while formalizing the problem; it determines whether the spec can advance.
- `ParameterConstraint`: atomic constraint on one parameter, variable, category, unit or relationship that `motor_030` must respect during synthetic generation.

## relationships
- `InferenceCase` -> `ExpertProblemSpec` (one activated case may produce one current spec version when critical ambiguities are resolved).
- `ExpertProblemSpec` -> `AmbiguityRegister` (each spec owns exactly one ambiguity register for the same `source_problem_ref`).
- `ExpertProblemSpec` -> `ParameterConstraint` (each spec owns one or more constraints that define the valid generation space).
- `AmbiguityRegister` -> `ParameterConstraint` (an ambiguity may block or qualify a constraint when its unresolved impact is material).
- `ExpertProblemSpec` -> `motor_030` handoff (only specs with no unresolved critical ambiguity and complete epistemic flags are eligible for synthetic generation).
- `VersionRecord` -> `ExpertProblemSpec` (the spec references source object versions and can be rebuilt from those versions).
- `CanonicalTaxonomy` -> `ParameterConstraint` (each named parameter or category must reference a canonical term or be marked ambiguous).

## key_fields
`ExpertProblemSpec` minimum fields:
- `spec_id`: string
- `source_problem_ref`: string
- `spec_version`: string
- `problem_statement`: string
- `problem_class`: enum string
- `expert_assumptions`: list[string]
- `domain_constraints_ref`: list[string]
- `parameter_constraints_ref`: list[string]
- `lineage_refs`: list[string]
- `non_evidentiary_flag`: boolean, always `true`
- `intended_use`: enum string, always `exploration`
- `domain_validity_limits`: string
- `limitations_note`: string

`AmbiguityRegister` minimum fields:
- `register_id`: string
- `source_problem_ref`: string
- `spec_id`: string
- `items`: list[AmbiguityItem]
- `has_unresolved_critical`: boolean
- `non_evidentiary_flag`: boolean, always `true`
- `intended_use`: enum string, always `exploration`
- `domain_validity_limits`: string
- `limitations_note`: string

`AmbiguityItem` minimum fields:
- `ambiguity_id`: string
- `field_ref`: string
- `description`: string
- `severity`: enum string, one of `low`, `medium`, `high`, `critical`
- `resolution_status`: enum string, one of `open`, `resolved`, `deferred`
- `impact_if_unresolved`: enum string, one of `minor`, `material`, `critical`

`ParameterConstraint` minimum fields:
- `constraint_id`: string
- `source_problem_ref`: string
- `spec_id`: string
- `parameter_name`: string
- `canonical_term_ref`: string
- `value_type`: enum string, such as `integer`, `float`, `category`, `boolean`, `interval`
- `allowed_domain`: string or structured range
- `unit`: string or null
- `constraint_rationale`: string
- `uncertainty_treatment`: string
- `non_evidentiary_flag`: boolean, always `true`
- `intended_use`: enum string, always `exploration`
- `domain_validity_limits`: string
- `limitations_note`: string
