# Conceptual Schema — ML Experiment / Model Training & Evaluation Engine

Motor ID: motor_031

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Entrenar, comparar y documentar modelos de ML sobre datasets sintéticos, produciendo capability_demonstration_report.
why_it_exists:  Demuestra capacidades analíticas antes de que exista evidencia real.
key_inputs:     synthetic_dataset (motor_030), expert_problem_spec (motor_029), version_records (motor_002)
key_outputs:    training_run_record, model_eval_summary, capability_demonstration_report
key_objects:    TrainingRunRecord, ModelEvalSummary, CapabilityDemonstrationReport
what_not_to_do: No produce modelos listos para producción. No puede ser usado como evidencia de validación de campo.
design_notes:   No produce modelos de producción. La política de selección de modelos en synthetic_epistemology_rules.md es vinculante.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true

Complete all sections with real motor-specific content before gate validation.
-->

## entities
- `TrainingRunRecord`: immutable record of one reproducible ML experiment over a registered synthetic dataset, including candidate models, configuration, seeds, splits, lineage and epistemic flags.
- `ModelEvalSummary`: structured comparison of candidate model results, baseline performance, stability across synthetic scenarios and generator sensitivity outcomes.
- `CapabilityDemonstrationReport`: non-evidentiary report that states what capability was or was not demonstrated under synthetic assumptions and what real validation would still be required.

## relationships
- `expert_problem_spec` -> `TrainingRunRecord`: one approved spec constrains the `problem_class`, target, metric, candidate model families and domain limits for each training run.
- `synthetic_dataset` -> `TrainingRunRecord`: one registered dataset supplies the synthetic observations used by a run; the run must preserve `training_data_ref`.
- `version_records` -> `TrainingRunRecord`: version records provide immutable references for dataset version, generator version, spec version and experiment configuration.
- `TrainingRunRecord` -> `ModelEvalSummary`: one or more training runs feed one evaluation summary for a specific experiment bundle and problem spec.
- `ModelEvalSummary` -> `CapabilityDemonstrationReport`: exactly one evaluation summary supports the report conclusions for the experiment bundle.
- `CapabilityDemonstrationReport` -> motor_032: the report may be consumed downstream only as subordinate synthetic support, never as validation evidence.

## key_fields
`TrainingRunRecord`
- `run_id`: string
- `source_problem_ref`: string
- `expert_spec_ref`: string
- `training_data_ref`: string
- `experiment_config`: dict
- `candidate_models`: list[dict]
- `baseline_model`: string
- `random_seed`: integer
- `split_strategy`: dict
- `generator_version`: string
- `parameter_set`: dict
- `version_refs`: dict
- `synthetic_data_flag`: boolean
- `synthetic_support_flag`: boolean
- `non_evidentiary_flag`: boolean

`ModelEvalSummary`
- `eval_id`: string
- `training_run_refs`: list[string]
- `primary_metric`: string
- `metric_results`: dict
- `baseline_comparison`: dict
- `scenario_stability`: dict
- `generator_sensitivity_test`: dict
- `selected_model`: string or null
- `selection_rationale`: string
- `source_problem_ref`: string
- `expert_spec_ref`: string
- `synthetic_support_flag`: boolean
- `non_evidentiary_flag`: boolean

`CapabilityDemonstrationReport`
- `report_id`: string
- `model_eval_summary_ref`: string
- `capability_statement`: string
- `intended_use`: enum[`exploration`, `capability_demo`, `preliminary_support`]
- `domain_validity_limits`: string
- `limitations_note`: string
- `gap_to_real_validation`: string
- `gap_to_deployment`: string
- `known_failure_modes`: list[string]
- `source_problem_ref`: string
- `expert_spec_ref`: string
- `generator_version`: string
- `parameter_set`: dict
- `synthetic_support_flag`: boolean
- `non_evidentiary_flag`: boolean
