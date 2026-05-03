# Failure Modes — Problem Formalization / Expert Problem Spec Engine

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

## failure_modes_list
- `CRITICAL_AMBIGUITY_LEAK`: a spec is marked eligible for `motor_030` while `ambiguity_register.has_unresolved_critical=true` or while an item has `impact_if_unresolved=critical`.
- `EPISTEMIC_FLAG_LOSS`: one or more outputs lack `non_evidentiary_flag=true`, `intended_use=exploration`, `domain_validity_limits` or `limitations_note`.
- `TAXONOMY_DRIFT`: parameter names or categories appear in the spec without canonical taxonomy references or ambiguity records.
- `SCOPE_INFLATION`: the spec starts prescribing synthetic data generation, ML model choice, validation claims or downstream decisions.
- `LINEAGE_BREAK`: the spec cannot be rebuilt because source problem, phase contract, taxonomy snapshot or version record references are missing.

## anti_patterns
- Treating expert judgment as measured field evidence instead of as a non-evidentiary generator contract.
- Collapsing ambiguous expert language into precise constraints without recording the ambiguity and its impact.
- Expanding this motor to generate synthetic data or choose ML models because the spec already contains parameters.
- Using free text problem descriptions without canonical taxonomy mapping and structured parameter constraints.

## degradation_signals
- More than 0 emitted objects in a run missing mandatory epistemic fields.
- Any handoff to `motor_030` where `ambiguity_register.has_unresolved_critical=true`.
- Rising count of parameter names without `canonical_term_ref`.
- Repeated specs with empty or generic `domain_validity_limits`.
- `limitations_note` text reused verbatim across unrelated problem classes.
- Increasing number of constraints with no `constraint_rationale` or no uncertainty treatment.
- Downstream synthetic generation failures caused by missing allowed domains or incompatible units.
