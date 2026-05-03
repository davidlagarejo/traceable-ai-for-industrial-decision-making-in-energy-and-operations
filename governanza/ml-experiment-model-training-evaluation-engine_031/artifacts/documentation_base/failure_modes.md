# Failure Modes — ML Experiment / Model Training & Evaluation Engine

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

## failure_modes_list
- `EPISTEMIC_PROMOTION_LEAK`: a synthetic metric or capability report is described as validation evidence, decision-grade support or proof of real-world predictability.
- `LINEAGE_DRIFT`: a training run references a dataset, spec or generator version that does not match the supplied version records; reproduced runs cannot be traced to the same inputs.
- `BASELINE_POLICY_BYPASS`: a complex model is evaluated or selected without first running the baseline required for the declared `problem_class`.
- `SENSITIVITY_COLLAPSE`: model performance looks acceptable in one synthetic scenario but changes materially when generator parameters vary inside declared uncertainty ranges.
- `FORCED_MODEL_SELECTION`: the evaluation summary names a selected model even though no candidate satisfied metric, stability, sensitivity and simplicity criteria.
- `PRODUCTION_ARTIFACT_CONFUSION`: downstream consumers treat transient trained objects as deployable assets even though the motor is allowed to emit only records and reports.

## anti_patterns
- Treating the highest synthetic benchmark score as evidence that the real phenomenon is predictable.
- Skipping the baseline model because a more complex model is expected to perform better.
- Editing the expert spec or synthetic dataset inside this motor to make training easier.
- Reporting feature importance, SHAP values or variable rankings as causal findings.
- Omitting limitations because the capability demonstration produced a strong metric.

## degradation_signals
- Increasing share of reports with missing or generic `gap_to_real_validation`, `gap_to_deployment` or `limitations_note`.
- Repeated `selected_model` values without recorded baseline comparison or generator sensitivity results.
- Metric variance across scenario bundles above the allowed range while reports still state capability was demonstrated.
- Training records that cannot be reproduced from stored seeds, split strategy, version refs and parameter sets.
- Outputs missing `synthetic_support_flag=true`, `non_evidentiary_flag=true` or lineage references.
- Reports whose language no longer distinguishes synthetic support from field evidence.
