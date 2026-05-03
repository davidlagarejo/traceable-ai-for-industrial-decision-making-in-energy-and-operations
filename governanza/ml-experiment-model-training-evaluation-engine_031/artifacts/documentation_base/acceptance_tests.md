# Acceptance Tests — ML Experiment / Model Training & Evaluation Engine

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

## happy_path
Input: `synthetic_dataset.dataset_id="syn-031-demo-001"` from motor_030 contains 2,000 rows, `training_data_ref="sgr-030-441"`, `source_problem_ref="case-104"`, `expert_spec_ref="eps-029-104"`, `generator_version="1.4.0"`, `parameter_set={"scenario_bundle":"baseline_plus_stress"}`, `synthetic_data_flag=true` and `non_evidentiary_flag=true`. The matching `expert_problem_spec.spec_id="eps-029-104"` declares `problem_class="classification_binary"`, `primary_metric="roc_auc"`, threshold `0.78`, no unresolved critical ambiguity and valid domain limits. `version_records` contain immutable refs for the spec, generator and dataset.

Action: the motor validates matching refs, builds a reproducible experiment config, evaluates the required Logistic Regression baseline before Random Forest and Gradient Boosting, runs scenario stability checks and executes `generator_sensitivity_test`.

Expected output: a `training_run_record` records the run config, seeds, split strategy, candidate models and lineage; a `model_eval_summary` records metric results, baseline comparison, stability and sensitivity outcomes; a `capability_demonstration_report` states the demonstrated synthetic capability, includes `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes`, `synthetic_support_flag=true` and `non_evidentiary_flag=true`, and explicitly says it is not field validation evidence.

## edge_cases
- Small synthetic dataset: when a supervised ML experiment receives 49 rows, the motor rejects ML training with `ERROR_INSUFFICIENT_SYNTHETIC_SAMPLE` unless the configured path is the allowed deterministic/statistical baseline path; no model comparison report is emitted.
- No candidate meets selection criteria: when all candidate models fail the primary metric threshold or generator-sensitivity criterion, the motor emits a valid `model_eval_summary` with `selected_model=null` and a `capability_demonstration_report` stating that capability was not demonstrated under the synthetic assumptions.
- High metric but unstable generator sensitivity: when AUC is 0.91 on the baseline scenario but varies by more than the allowed sensitivity range under generator parameter perturbation, the motor records the instability and does not select the model.
- Unsupervised anomaly detection: when `problem_class="anomaly_detection"` without labels, the motor evaluates statistical control and unsupervised families allowed by policy, avoids supervised classifiers and records the absence of target labels as part of the evaluation context.

## rejection_criteria
- Reject with `ERROR_INPUT_LINEAGE_MISMATCH` when `synthetic_dataset.expert_spec_ref` is not equal to `expert_problem_spec.spec_id`, or when the supplied `version_records` do not match the dataset and spec versions.
- Reject with `ERROR_MISSING_EPISTEMIC_FLAGS` when required input flags are missing or false, including `synthetic_data_flag=true` and `non_evidentiary_flag=true` on the synthetic dataset.
- Reject with `ERROR_CRITICAL_AMBIGUITY` when the `expert_problem_spec.ambiguity_register` contains an item with `impact_if_unresolved="critical"`.
- Reject with `ERROR_UNSUPPORTED_PROBLEM_CLASS` when the `problem_class` is absent or outside the model-selection policy.
- Reject with `ERROR_PRODUCTION_MODEL_REQUESTED` when the requested output includes serialized model binaries, production deployment metadata or operational inference endpoints.
