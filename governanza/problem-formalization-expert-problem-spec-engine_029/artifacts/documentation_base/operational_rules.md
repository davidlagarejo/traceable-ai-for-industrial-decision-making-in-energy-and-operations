# Operational Rules — Problem Formalization / Expert Problem Spec Engine

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

## rules
1. The motor processes only activated `inference_cases` with explicit provenance, phase reference and dependency version records.
2. The motor must reject processing when any input ambiguity with `impact_if_unresolved=critical` remains unresolved.
3. Every output object must include `non_evidentiary_flag=true`, `intended_use=exploration`, `source_problem_ref`, `domain_validity_limits` and `limitations_note`.
4. Every term used as a parameter, entity, unit or category must map to `canonical_taxonomy`; unmapped terms must be recorded in `ambiguity_register`.
5. Every `expert_problem_spec` must declare one problem class before handoff to `motor_030`.
6. Every `parameter_constraints` entry must include a value type, allowed domain, source rationale and uncertainty treatment.
7. The motor must preserve lineage references to the input case, phase contract, taxonomy snapshot and version records.
8. The motor must emit a blocking error instead of an output when required fields are missing or when epistemic flags cannot be attached.
9. Handoff to `motor_030` is permitted only when `ambiguity_register.has_unresolved_critical=false`.

## invariants
- `source_problem_ref` is never null on any object produced by this motor.
- `non_evidentiary_flag` is always `true` on `ExpertProblemSpec`, `AmbiguityRegister` and `ParameterConstraint`.
- `intended_use` is always `exploration` for every object produced by this motor.
- `domain_validity_limits` and `limitations_note` are never empty on emitted objects.
- The motor never mutates the source `inference_case`, `phase_contract`, `version_record` or `canonical_taxonomy` objects.
- A spec eligible for synthetic generation never has unresolved critical ambiguity.
- Lineage references remain sufficient to reconstruct which input versions produced the spec.

## forbidden_operations
- Generating synthetic data, simulated rows, sampling plans or generation runs.
- Running ML, selecting models, training models, evaluating models or reporting model metrics.
- Executing on `inference_cases` with unresolved critical ambiguity.
- Treating an `expert_problem_spec` as field evidence, validation data or decision-grade proof.
- Replacing `Validation Data Bridge`, `Verification Bridge` or any field-evidence workflow.
- Promoting, reclassifying or silently editing epistemic flags after output registration.
- Correcting taxonomy, phase contracts, version records or inference cases inside this motor.
- Creating a handoff to `motor_030` when mandatory flags or lineage references are missing.
