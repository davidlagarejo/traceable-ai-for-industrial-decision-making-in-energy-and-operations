# Technical Schema — ML Experiment / Model Training & Evaluation Engine

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

This schema is complete for Gate 2 validation.
-->

## entities
- `TrainingRunRecord`: immutable technical record for one reproducible ML experiment executed by motor_031 over a registered motor_030 synthetic dataset. It captures the experiment configuration, candidate model families, mandatory baseline, split strategy, random seed, run-level parameters, lineage references, version references and required synthetic-chain flags. Stage: produced by the implementation stage, specified in `schema_technical`, and verified by tests and conformance review.
- `ModelEvalSummary`: immutable technical summary of model evaluation for one experiment bundle. It compares candidate model metrics, baseline performance, scenario stability, generator sensitivity, selection outcome and rationale without promoting synthetic metrics to field evidence. Stage: produced by the implementation stage after one or more `TrainingRunRecord` objects, specified in `schema_technical`, and verified by tests and conformance review.
- `CapabilityDemonstrationReport`: immutable report object describing whether an analytical capability was demonstrated under synthetic assumptions, including limitations, gaps to real validation, gaps to deployment and known synthetic failure modes. It is consumable downstream only as non-evidentiary synthetic support. Stage: produced by the implementation stage after a `ModelEvalSummary`, specified in `schema_technical`, and verified by tests and conformance review.

## fields
### TrainingRunRecord
- `run_id: string` (required) — stable identifier for the training run record.
- `source_problem_ref: string` (required) — reference to the originating inference case or problem source shared by the spec, dataset and version records.
- `source_ref: string` (required) — canonical lineage reference for the source bundle used by the run; must resolve to the same `source_problem_ref`.
- `expert_spec_ref: string` (required) — `expert_problem_spec.spec_id` from motor_029.
- `training_data_ref: string` (required) — motor_030 `synthetic_generation_run.run_id` used as training input; never points to field evidence.
- `synthetic_dataset_ref: string` (required) — registered synthetic dataset identifier from motor_030.
- `version_refs: dict[string, string]` (required) — immutable references from motor_002 for dataset version, spec version, generator version and experiment configuration version.
- `experiment_config: dict` (required) — reproducible configuration containing `problem_class`, `primary_metric`, threshold, split strategy, candidate model families, baseline model, scenario bundle refs and model-selection constraints.
- `problem_class: string` (required) — problem class declared by the expert spec and used to select allowed model families.
- `primary_metric: string` (required) — primary metric declared by the expert spec or experiment config.
- `primary_metric_threshold: number` (required) — threshold that a model must satisfy before any selection is allowed.
- `candidate_models: list[dict]` (required) — ordered candidate model definitions selected from the policy for the declared `problem_class`.
- `baseline_model: string` (required) — mandatory baseline model or statistical baseline required by the model-selection policy.
- `baseline_evaluated_first: boolean` (required) — true only when the mandatory baseline was evaluated before more complex models.
- `deterministic_or_statistical_path: boolean` (required) — indicates that the run used the allowed non-ML baseline path because ML was unnecessary or disallowed.
- `random_seed: integer` (required) — seed used for reproducible training and splitting.
- `split_strategy: dict` (required) — train/test or scenario split definition, including proportions and stratification rules when applicable.
- `scenario_bundle_refs: list[string]` (required) — scenario or bundle identifiers from the synthetic generation run used for stability checks.
- `model_parameters: dict[string, dict]` (required) — candidate-specific hyperparameters actually used during training.
- `training_result_refs: list[string]` (required) — internal result references for candidate training outputs; these are not serialized production models.
- `generator_version: string` (required) — generator semantic version inherited from motor_030.
- `parameter_set: dict` (required) — exact generator and experiment parameters used by the run.
- `intended_use: enum[exploration, capability_demo, preliminary_support]` (required) — permitted synthetic-chain use for the record.
- `domain_validity_limits: string` (required) — domain scope within which the synthetic experiment is meaningful.
- `limitations_note: string` (required) — explicit non-evidentiary limitation statement.
- `synthetic_data_flag: boolean` (required) — must be true because the run derives from motor_030 synthetic data.
- `synthetic_support_flag: boolean` (required) — must be true for motor_031 outputs exposed as synthetic support.
- `non_evidentiary_flag: boolean` (required) — must be true; the record cannot be used as field validation evidence.
- `produced_by_motor: string` (required) — fixed value `motor_031`.
- `produced_at: datetime` (required) — timestamp when motor_031 produced the record.
- `parent_id: string | null` (required) — previous `TrainingRunRecord.run_id` when this is a controlled rerun; null for the first run in a chain.
- `version_id: string` (required) — immutable version identifier for this record.
- `created_at: datetime` (required) — creation timestamp for this record version.
- `updated_at: datetime` (required) — last update timestamp for this record version; equal to `created_at` for immutable first registration.
- `version_hash: string` (required) — deterministic hash over the canonicalized record content and version references.

### ModelEvalSummary
- `eval_id: string` (required) — stable identifier for the evaluation summary.
- `source_problem_ref: string` (required) — reference to the originating inference case or problem source.
- `source_ref: string` (required) — canonical lineage reference for the evaluated experiment bundle.
- `expert_spec_ref: string` (required) — `expert_problem_spec.spec_id` used to define the experiment.
- `training_run_refs: list[string]` (required) — one or more `TrainingRunRecord.run_id` values included in the evaluation.
- `training_data_ref: string` (required) — motor_030 synthetic generation run used by the evaluated training records.
- `version_refs: dict[string, string]` (required) — immutable refs for all evaluated training records, dataset, spec, generator and evaluation configuration.
- `primary_metric: string` (required) — metric used for primary selection.
- `primary_metric_threshold: number` (required) — threshold applied before selection.
- `metric_results: dict[string, dict]` (required) — per-model metric values, confidence intervals if present and scenario-specific values.
- `baseline_comparison: dict` (required) — comparison of each candidate against the mandatory baseline.
- `scenario_stability: dict` (required) — stability measurements across synthetic scenarios or bundles.
- `generator_sensitivity_test: dict` (required) — measured model sensitivity to allowed generator parameter changes.
- `selection_criteria_results: dict` (required) — pass/fail values for metric threshold, scenario stability, generator sensitivity and simplicity precedence.
- `selected_model: string | null` (required) — selected model name when all criteria pass; null when capability cannot be demonstrated under the configured conditions.
- `selection_rationale: string` (required) — explanation of selection, non-selection or deterministic/statistical baseline outcome.
- `known_metric_limits: list[string]` (required) — limitations of metric interpretation on synthetic data.
- `generator_version: string` (required) — generator semantic version inherited from evaluated runs.
- `parameter_set: dict` (required) — exact generator and evaluation parameters summarized by this object.
- `intended_use: enum[exploration, capability_demo, preliminary_support]` (required) — permitted synthetic-chain use for the summary.
- `domain_validity_limits: string` (required) — domain scope within which the evaluation is meaningful.
- `limitations_note: string` (required) — explicit non-evidentiary limitation statement.
- `synthetic_data_flag: boolean` (required) — must be true because evaluation derives from motor_030 synthetic data.
- `synthetic_support_flag: boolean` (required) — must be true for motor_031 outputs exposed as synthetic support.
- `non_evidentiary_flag: boolean` (required) — must be true; the summary cannot be used as validation evidence.
- `produced_by_motor: string` (required) — fixed value `motor_031`.
- `produced_at: datetime` (required) — timestamp when motor_031 produced the summary.
- `parent_id: string | null` (required) — previous `ModelEvalSummary.eval_id` when this is a controlled reevaluation; null for the first evaluation in a chain.
- `version_id: string` (required) — immutable version identifier for this summary.
- `created_at: datetime` (required) — creation timestamp for this summary version.
- `updated_at: datetime` (required) — last update timestamp for this summary version; equal to `created_at` for immutable first registration.
- `version_hash: string` (required) — deterministic hash over the canonicalized summary content and referenced run versions.

### CapabilityDemonstrationReport
- `report_id: string` (required) — stable identifier for the capability demonstration report.
- `source_problem_ref: string` (required) — reference to the originating inference case or problem source.
- `source_ref: string` (required) — canonical lineage reference for the evaluated synthetic experiment bundle.
- `expert_spec_ref: string` (required) — `expert_problem_spec.spec_id` whose problem class and assumptions governed the demonstration.
- `model_eval_summary_ref: string` (required) — `ModelEvalSummary.eval_id` supporting this report.
- `training_run_refs: list[string]` (required) — `TrainingRunRecord.run_id` values summarized by the report.
- `training_data_ref: string` (required) — motor_030 synthetic generation run used by the demonstration.
- `version_refs: dict[string, string]` (required) — immutable refs for the report, evaluation summary, training runs, dataset, spec and generator.
- `capability_statement: string` (required) — bounded statement of what was or was not demonstrated under synthetic assumptions.
- `demonstration_status: enum[demonstrated, not_demonstrated, inconclusive]` (required) — observable outcome of the capability demonstration.
- `selected_model: string | null` (required) — selected model from the evaluation summary, or null when no candidate met criteria.
- `primary_metric: string` (required) — primary metric used in the supporting evaluation.
- `primary_metric_value: number | null` (required) — selected model metric value, or null when no model was selected.
- `summary_metric_results: dict` (required) — compact metric and baseline comparison values needed to audit the report.
- `generator_sensitivity_test: dict` (required) — sensitivity result propagated from the evaluation summary.
- `gap_to_real_validation: string` (required) — real data or validation bridge evidence required to test the capability outside synthetic assumptions.
- `gap_to_deployment: string` (required) — additional engineering, validation, monitoring and governance work required for any production model.
- `known_failure_modes: list[string]` (required) — synthetic-context failure modes observed or expected for the evaluated configuration.
- `intended_use: enum[exploration, capability_demo, preliminary_support]` (required) — permitted downstream use; default for this report is `capability_demo`.
- `domain_validity_limits: string` (required) — domain scope within which the report can be interpreted.
- `limitations_note: string` (required) — explicit statement that the report is non-evidentiary and cannot validate field behavior.
- `cannot_substitute: list[string]` (required) — explicit list of artifacts or stages this report cannot replace, including field evidence, validation bridge, verification bridge and production deployment review.
- `generator_version: string` (required) — generator semantic version inherited from the evaluated dataset.
- `parameter_set: dict` (required) — exact generator and experiment parameters covered by the report.
- `synthetic_data_flag: boolean` (required) — must be true because the report derives exclusively from synthetic data.
- `synthetic_support_flag: boolean` (required) — must be true because the report is synthetic support only.
- `non_evidentiary_flag: boolean` (required) — must be true; the report cannot be used as field validation evidence.
- `produced_by_motor: string` (required) — fixed value `motor_031`.
- `produced_at: datetime` (required) — timestamp when motor_031 produced the report.
- `parent_id: string | null` (required) — previous `CapabilityDemonstrationReport.report_id` when this is a controlled rereport; null for the first report in a chain.
- `version_id: string` (required) — immutable version identifier for this report.
- `created_at: datetime` (required) — creation timestamp for this report version.
- `updated_at: datetime` (required) — last update timestamp for this report version; equal to `created_at` for immutable first registration.
- `version_hash: string` (required) — deterministic hash over the canonicalized report content and referenced evaluation versions.

## relationships
- `TrainingRunRecord.expert_spec_ref` references `expert_problem_spec.spec_id` from motor_029. The reference is required and must match the `expert_spec_ref` carried by the synthetic dataset.
- `TrainingRunRecord.training_data_ref` references `synthetic_generation_run.run_id` from motor_030. The reference is required and must never point to field, validation bridge or verification bridge data.
- `TrainingRunRecord.version_refs` references motor_002 version records for the expert spec, synthetic dataset, generator version and experiment configuration.
- `ModelEvalSummary.training_run_refs[]` references one or more `TrainingRunRecord.run_id` values. All referenced runs must share `source_problem_ref`, `expert_spec_ref`, `training_data_ref`, `generator_version` and compatible `parameter_set`.
- `ModelEvalSummary.training_data_ref` references the same motor_030 synthetic generation run used by its training runs.
- `ModelEvalSummary.version_refs` references motor_002 version records and the version IDs of the included `TrainingRunRecord` objects.
- `CapabilityDemonstrationReport.model_eval_summary_ref` references exactly one `ModelEvalSummary.eval_id`.
- `CapabilityDemonstrationReport.training_run_refs[]` references the training runs included in the referenced evaluation summary.
- `CapabilityDemonstrationReport.training_data_ref` references the motor_030 synthetic generation run used by the referenced evaluation summary.
- `CapabilityDemonstrationReport.version_refs` references motor_002 version records plus the `version_id` values of the supporting evaluation summary and training runs.
- Downstream consumption by motor_032 may reference `CapabilityDemonstrationReport.report_id` only as subordinate synthetic support; it does not create evidence, deployment readiness or decision-grade status.

## identifiers
- `TrainingRunRecord`: canonical stable ID is `run_id`. The ID must be unique within motor_031 and stable across reads. Controlled reruns produce a new `run_id` and point `parent_id` to the prior run.
- `ModelEvalSummary`: canonical stable ID is `eval_id`. The ID must be unique within motor_031 and stable across reads. Controlled reevaluations produce a new `eval_id` and point `parent_id` to the prior summary.
- `CapabilityDemonstrationReport`: canonical stable ID is `report_id`. The ID must be unique within motor_031 and stable across reads. Controlled rereports produce a new `report_id` and point `parent_id` to the prior report.
- Cross-entity references must use canonical IDs only: `training_run_refs[]` contains `run_id`, `model_eval_summary_ref` contains `eval_id`, and downstream report references contain `report_id`.
- External references remain external IDs: `expert_spec_ref` contains motor_029 `spec_id`, `training_data_ref` contains motor_030 `synthetic_generation_run.run_id`, and `version_refs` contains motor_002 version identifiers.

## versioning
- Every `TrainingRunRecord`, `ModelEvalSummary` and `CapabilityDemonstrationReport` must include `version_id`, `created_at`, `updated_at` and `version_hash`.
- `version_id` is required and identifies the immutable version of the object emitted by motor_031.
- `created_at` is required and records when the object version was first registered.
- `updated_at` is required and records the last metadata update for the same object version; because emitted objects are immutable, it normally equals `created_at` unless an allowed metadata registration event occurs without changing semantic content.
- `version_hash` is required and is computed from canonicalized object content, including IDs, lineage refs, version refs, epistémic flags, experiment configuration, metrics and report limitation fields.
- Any material change to fields, metrics, lineage, flags, configuration, selected model or report text requires a new object version with a new `version_id` and `version_hash`; silent mutation is not allowed.
- `version_refs` is required on every entity to preserve motor_002 references for the spec, dataset, generator, configuration and parent artifacts used to produce the object.

## lineage
- Every `TrainingRunRecord`, `ModelEvalSummary` and `CapabilityDemonstrationReport` must include `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref` is required and must resolve to the same `source_problem_ref` carried by `expert_spec_ref`, `training_data_ref` and `version_refs`.
- `produced_by_motor` is required and must be the literal value `motor_031` for all objects emitted by this motor.
- `produced_at` is required and records the timestamp of object production by motor_031.
- `parent_id` is required and is null for first-generation objects; it contains the prior canonical object ID only when the object is a controlled rerun, reevaluation or rereport.
- `expert_spec_ref`, `training_data_ref`, `generator_version`, `parameter_set` and `version_refs` are required lineage-supporting fields on all emitted objects.
- Lineage validation fails when any emitted object lacks `source_problem_ref`, lacks required synthetic-chain flags, references mismatched spec/dataset/version records, or points to real field evidence instead of motor_030 synthetic data.
