# Design Done Criteria — ML Experiment / Model Training & Evaluation Engine

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

## criteria
- `master_concept_doc.md` defines purpose, concrete operations, explicit non-responsibilities and separate-motor rationale for motor_031.
- `functional_contract.md` lists `synthetic_dataset`, `expert_problem_spec` and `version_records` as inputs with origins, and lists `training_run_record`, `model_eval_summary` and `capability_demonstration_report` as outputs with consumers.
- `functional_contract.md` and `operational_rules.md` require `synthetic_support_flag=true` and `non_evidentiary_flag=true` on emitted outputs and prohibit use as field validation evidence.
- `conceptual_schema.md` defines `TrainingRunRecord`, `ModelEvalSummary` and `CapabilityDemonstrationReport` with required lineage, versioning, experiment, metric and epistemic fields.
- `operational_rules.md` includes verifiable model-selection rules tied to `problem_class`, mandatory baselines, scenario stability and `generator_sensitivity_test`.
- `acceptance_tests.md` covers a happy path, insufficient sample size, no selected model, generator sensitivity instability and explicit rejection errors.
- `failure_modes.md` lists epistemic promotion, lineage drift, baseline bypass, sensitivity collapse, forced selection and production artifact confusion as observable risks.
- No documentation-base artifact contains open placeholder markers or unresolved design text.
