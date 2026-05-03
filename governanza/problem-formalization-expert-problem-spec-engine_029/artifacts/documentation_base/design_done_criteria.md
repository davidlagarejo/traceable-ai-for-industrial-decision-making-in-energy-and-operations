# Design Done Criteria — Problem Formalization / Expert Problem Spec Engine

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

## criteria
- `master_concept_doc.md`, `functional_contract.md`, `conceptual_schema.md`, `operational_rules.md`, `acceptance_tests.md`, `failure_modes.md` and `design_done_criteria.md` exist and are each larger than 500 bytes.
- `functional_contract.md`, `conceptual_schema.md` and `operational_rules.md` contain no open placeholder markers and define inputs, outputs, limits, entities, relationships, rules, invariants and forbidden operations.
- The contract lists `inference_cases`, `phase_contracts`, `version_records` and `canonical_taxonomy` as inputs, and lists `expert_problem_spec`, `ambiguity_register` and `parameter_constraints` as outputs.
- All documented outputs include mandatory epistemic fields: `non_evidentiary_flag=true`, `intended_use=exploration`, `source_problem_ref`, `domain_validity_limits` and `limitations_note`.
- The rules explicitly prohibit synthetic data generation, ML execution and processing of cases with unresolved critical ambiguity.
- Acceptance tests include one happy path, at least two edge cases and explicit rejection criteria with named error signals.
- Failure modes include ambiguity leakage, epistemic flag loss, taxonomy drift, scope inflation and lineage break.
- The design is ready for `schema_technical` without inventing additional motors, changing dependencies or modifying any `motor_state.json` file.
