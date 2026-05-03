# Test Spec — ML Experiment / Model Training & Evaluation Engine

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

This test specification is complete for Gate 3 validation.
-->

## happy_path
Input:
- `synthetic_dataset.dataset_id="syn-031-demo-001"` with 2,000 rows, feature columns `["pressure_delta", "cycle_time", "ambient_temp"]`, target column `failure_within_window`, `training_data_ref="sgr-030-441"`, `source_problem_ref="case-104"`, `expert_spec_ref="eps-029-104"`, `generator_version="1.4.0"`, `parameter_set={"scenario_bundle":"baseline_plus_stress","noise_profile":"nominal"}`, `synthetic_data_flag=true` and `non_evidentiary_flag=true`.
- `expert_problem_spec.spec_id="eps-029-104"` with `source_problem_ref="case-104"`, `status="approved"`, `problem_class="classification_binary"`, `primary_metric="roc_auc"`, `primary_metric_threshold=0.78`, target definition `failure_within_window`, `domain_validity_limits="synthetic compressor telemetry generated from approved expert assumptions only"` and no unresolved ambiguity with critical impact.
- `version_records` with immutable refs `{"spec_version":"ver-eps-029-104-003","dataset_version":"ver-syn-031-demo-001-001","generator_version":"ver-gen-030-1.4.0","experiment_config_version":"ver-exp-031-104-001"}`.

Expected behavior:
- The motor validates aligned `source_problem_ref`, `expert_spec_ref`, `generator_version`, `parameter_set` and version refs before training.
- The motor creates an experiment config for `classification_binary` that evaluates the required Logistic Regression baseline before Random Forest and Gradient Boosting.
- The motor uses a deterministic `random_seed`, records a train/test split strategy, evaluates scenario stability across `["baseline","stress"]` and executes `generator_sensitivity_test`.

Expected output:
- `training_run_record.run_id="trr-031-case-104-v1"` includes the candidate model order, `baseline_model="Logistic Regression"`, `baseline_evaluated_first=true`, `training_data_ref="sgr-030-441"`, `source_problem_ref="case-104"`, `expert_spec_ref="eps-029-104"`, version refs, `synthetic_data_flag=true`, `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `produced_by_motor="motor_031"` and no serialized production model.
- `model_eval_summary.eval_id="mes-031-case-104-v1"` records `metric_results` where Logistic Regression has `roc_auc=0.76`, Random Forest has `roc_auc=0.84` and Gradient Boosting has `roc_auc=0.85`; Random Forest and Gradient Boosting pass the threshold, both pass scenario stability with relative variation no greater than `0.15`, both pass generator sensitivity with maximum relative metric change no greater than `0.20`, and `selected_model="Random Forest"` because it is the simpler passing candidate after the baseline fails the metric threshold.
- `capability_demonstration_report.report_id="cdr-031-case-104-v1"` has `demonstration_status="demonstrated"`, `selected_model="Random Forest"`, `primary_metric_value=0.84`, `intended_use="capability_demo"`, explicit `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes`, `cannot_substitute` entries for field evidence, Validation Data Bridge, Verification Bridge and production deployment review, plus `synthetic_data_flag=true`, `synthetic_support_flag=true` and `non_evidentiary_flag=true`.

## sparse_case
Input:
- `synthetic_dataset.dataset_id="syn-031-sparse-001"` has all required lineage fields and 120 rows but omits optional feature descriptions, confidence interval metadata, human review notes and scenario display labels.
- `expert_problem_spec.spec_id="eps-029-205"` is approved, declares `problem_class="regression_continuous"`, `primary_metric="rmse"`, `primary_metric_threshold=8.0`, target `remaining_useful_life_days`, domain limits and an empty `ambiguity_register`.
- `version_records` contains the required spec, dataset, generator and experiment config refs but does not contain optional previous-version refs because this is the first run.

Expected behavior:
- The motor must not fail because optional descriptive metadata is absent.
- The motor records `parent_id=null` on first-generation `TrainingRunRecord`, `ModelEvalSummary` and `CapabilityDemonstrationReport`.
- The motor selects only model families allowed for `regression_continuous`, evaluates the Linear Regression baseline first and records missing optional confidence intervals as a metric limitation instead of fabricating them.
- Outputs still include complete lineage, version refs, `generator_version`, `parameter_set`, `intended_use`, `domain_validity_limits`, `limitations_note`, `synthetic_data_flag=true`, `synthetic_support_flag=true` and `non_evidentiary_flag=true`.

## malformed_input
Malformed input example:
- `synthetic_dataset.dataset_id="syn-031-bad-001"` has `synthetic_data_flag="true"` as a string instead of boolean `true`, omits required `training_data_ref`, and carries `expert_spec_ref="eps-029-other"`.
- The supplied `expert_problem_spec.spec_id="eps-029-301"` has `problem_class=17` instead of a string.
- `version_records` is provided as a list instead of a mapping keyed by required version ref names.

Expected behavior:
- The motor rejects the request before building `experiment_config` or training any candidate model.
- The rejection is structured as `ERROR_INVALID_INPUT_SCHEMA` with field paths for `synthetic_dataset.synthetic_data_flag`, `synthetic_dataset.training_data_ref`, `expert_problem_spec.problem_class` and `version_records`.
- No `training_run_record`, `model_eval_summary`, `capability_demonstration_report`, training result ref, model binary or partial metric artifact is emitted.

## edge_cases
- Insufficient synthetic sample: if a supervised ML experiment receives 49 synthetic rows and is not explicitly configured for an allowed deterministic or statistical baseline path, reject with `ERROR_INSUFFICIENT_SYNTHETIC_SAMPLE`; the test passes only if no model comparison report is emitted.
- No candidate satisfies selection criteria: if all candidates fail the primary metric threshold, scenario stability or generator sensitivity, emit a valid `model_eval_summary` with `selected_model=null` and a `capability_demonstration_report` with `demonstration_status="not_demonstrated"` and a capability statement explaining that the capability was not demonstrated under the synthetic assumptions.
- High metric but unstable generator sensitivity: if Random Forest reaches `roc_auc=0.91` on the baseline scenario but `generator_sensitivity_test.max_relative_metric_change=0.27`, the motor must mark the sensitivity criterion as failed, set `selected_model=null` unless another simpler candidate passes all criteria, and preserve the instability in `known_failure_modes`.
- Input lineage mismatch: if `synthetic_dataset.expert_spec_ref` differs from `expert_problem_spec.spec_id`, or if `version_records.dataset_version` does not match the dataset version, reject with `ERROR_INPUT_LINEAGE_MISMATCH` before training.
- Unsupported or unsafe model policy: if `problem_class="classification_binary"` but the experiment config requests only Gradient Boosting and skips Logistic Regression, reject with `ERROR_BASELINE_NOT_EVALUATED` or an equivalent policy error before candidate training proceeds.
- Unsupervised anomaly detection: if `problem_class="anomaly_detection"` has no target labels, the motor must follow the unlabeled policy path using statistical control as baseline plus allowed unsupervised families; the test fails if a supervised classifier is evaluated.

## pass_criteria
A test passes when the observable result matches the expected contract for its case:
- Accepted cases emit exactly the required objects for this stage output surface: `training_run_record`, `model_eval_summary` and `capability_demonstration_report`.
- Every emitted object includes stable canonical IDs, `source_problem_ref`, `source_ref`, `expert_spec_ref`, `training_data_ref` where required, `version_refs`, `generator_version`, `parameter_set`, `intended_use`, `domain_validity_limits`, `limitations_note`, `produced_by_motor="motor_031"`, `produced_at`, `parent_id`, `version_id`, `created_at`, `updated_at` and `version_hash`.
- Every emitted object includes `synthetic_support_flag=true` and `non_evidentiary_flag=true`; records and reports derived from the synthetic dataset include `synthetic_data_flag=true`.
- The mandatory baseline for the declared `problem_class` is evaluated before more complex candidates, and `baseline_evaluated_first=true` is present in the training run record.
- Model selection follows the ordered criteria: primary metric threshold, scenario stability, generator sensitivity and simplest adequate model. If no candidate satisfies those criteria, `selected_model=null` is preserved and the report status is not forced to `demonstrated`.
- `capability_demonstration_report` includes `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes` and `cannot_substitute`, and the limitation text explicitly states that the report is synthetic, non-evidentiary and not field validation evidence.
- Rejection cases return the specified structured error and emit no partial output artifacts.

## fail_criteria
A test fails if any of these observable violations occur:
- The motor accepts malformed input, missing required lineage, mismatched `expert_spec_ref`, mismatched version refs, missing required synthetic-chain flags or wrong field types.
- The motor trains or evaluates a candidate before validating input lineage, version refs and epistemic flags.
- The motor skips the mandatory baseline, evaluates model families outside the `problem_class` policy or selects a complex model when a simpler candidate satisfies all ordered selection criteria.
- The motor emits production model binaries, deployment configuration, serving endpoints, operational inference outputs, causal claims, field validation claims or decision-grade support.
- Any output lacks `synthetic_support_flag=true`, `non_evidentiary_flag=true`, required `synthetic_data_flag=true`, lineage refs, immutable version refs, `generator_version`, `parameter_set`, `domain_validity_limits` or `limitations_note`.
- The motor promotes synthetic metrics to field evidence, omits `gap_to_real_validation`, omits `gap_to_deployment`, omits `known_failure_modes`, or fails to state what the report cannot substitute.
- The motor silently repairs bad input, fabricates missing optional confidence intervals, mutates source inputs or global version records, or emits partial artifacts after a rejection.
