# Failure Modes Spec — ML Experiment / Model Training & Evaluation Engine

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

This failure-mode specification is complete for Gate 4 validation.
-->

## failure_modes_list
- `FM031_INPUT_SCHEMA_REJECTION_GAP`: synthetic dataset, expert spec or version records are accepted with missing required fields, wrong field types, or absent `synthetic_data_flag`, `synthetic_support_flag` or `non_evidentiary_flag` → training begins before contract validation, malformed objects produce partial metrics, or rejection lacks field paths → reject before experiment configuration with a structured schema error, emit no `TrainingRunRecord`, `ModelEvalSummary` or `CapabilityDemonstrationReport`, and report every invalid field path.
- `FM031_LINEAGE_VERSION_MISMATCH`: `source_problem_ref`, `expert_spec_ref`, `training_data_ref`, `generator_version`, `parameter_set` or motor_002 `version_refs` differ across the synthetic dataset, approved expert spec and version records → outputs cannot be reproduced from the claimed input bundle or point to the wrong expert assumptions → stop before training with `ERROR_INPUT_LINEAGE_MISMATCH`, preserve source inputs unchanged, and require a corrected aligned input bundle.
- `FM031_BASELINE_POLICY_BYPASS`: the candidate list skips the mandatory baseline for the declared `problem_class`, evaluates a complex model first, or uses a family outside the policy in `synthetic_epistemology_rules.md` → `baseline_evaluated_first=false`, absent baseline comparison, or unsupported model family appears in `candidate_models` → reject with a policy error before candidate training and rebuild `experiment_config` from the approved problem-class mapping.
- `FM031_GENERATOR_SENSITIVITY_COLLAPSE`: a candidate passes the primary metric threshold on one synthetic scenario but fails the generator sensitivity check or exceeds the allowed relative metric change under parameter variation → high metric is paired with unstable `generator_sensitivity_test` results or inconsistent scenario performance → set the candidate criterion to failed, keep `selected_model=null` unless another simpler candidate passes all criteria, and propagate the instability into `known_failure_modes`.
- `FM031_FORCED_MODEL_SELECTION`: no candidate satisfies primary metric threshold, scenario stability, generator sensitivity and simplicity precedence, but the evaluation still names a winner → `ModelEvalSummary.selected_model` is non-null while one or more selection criteria are false, and the report says `demonstration_status="demonstrated"` without adequate support → emit a valid non-selection summary with `selected_model=null`, set report status to `not_demonstrated` or `inconclusive`, and state that capability was not demonstrated under the synthetic assumptions.
- `FM031_EPISTEMIC_PROMOTION_LEAK`: metrics or report copy describe synthetic model performance as field validation, verification evidence, causal proof, production readiness or decision-grade support → `limitations_note`, `cannot_substitute`, `gap_to_real_validation` or `gap_to_deployment` is missing or contradicted by the report language → block report emission until non-evidentiary language and required flags are present, and include explicit exclusions for field evidence, Validation Data Bridge, Verification Bridge and production deployment review.
- `FM031_PRODUCTION_ARTIFACT_LEAK`: implementation persists serialized model binaries, serving configs, endpoints, inference pipelines or deployment credentials as output artifacts → files or refs outside run records, metric summaries and capability reports appear in the output surface → delete transient production-like outputs before publishing, fail conformance, and keep only reproducibility metadata and non-deployable training result references.
- `FM031_REPRODUCIBILITY_DRIFT`: run metadata omits deterministic seed, split strategy, scenario bundle refs, model parameters or canonical version hashes → repeated execution cannot reconstruct the same training and evaluation conditions, and audit records diverge without a parent chain → reject output registration, require complete reproducibility metadata, and create a new versioned object rather than mutating the prior record.
- `FM031_SILENT_INPUT_REPAIR`: implementation coerces invalid input values, fills missing confidence intervals, rewrites expert spec fields or modifies synthetic dataset metadata to make training proceed → accepted outputs contain fabricated optional metadata or changed source assumptions without lineage trail → fail before training, return a structured input error or metric limitation, and preserve the original source bundle untouched.

## anti_patterns
- Coupling motor_031 directly to motor_032 decision logic instead of emitting only `training_run_record`, `model_eval_summary` and `capability_demonstration_report` as subordinate synthetic support.
- Treating the highest synthetic benchmark score as evidence of real-world predictability, field validation, site truth, causal effect or decision-grade support.
- Selecting model families by implementation convenience or perceived sophistication instead of the `problem_class` policy and baseline sequence defined in `synthetic_epistemology_rules.md`.
- Training first and validating lineage, version refs and epistemic flags afterward; validation must precede experiment configuration and candidate execution.
- Mutating `expert_problem_spec`, `synthetic_dataset`, motor_002 version records or motor state to repair bad inputs locally.
- Emitting serialized production models, deployment configs, serving endpoints, feature stores or operational inference outputs from this motor.
- Collapsing `TrainingRunRecord`, `ModelEvalSummary` and `CapabilityDemonstrationReport` into one monolithic artifact that hides selection criteria, limitations or lineage.
- Reporting feature importance, SHAP values, ranking outputs or model coefficients as causal findings about the real domain.
- Forcing a best model when all candidates fail criteria instead of preserving a null selection and a bounded non-demonstration report.
- Omitting `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes` or `cannot_substitute` because the synthetic metric is strong.

## degradation_signals
- Rising count of rejected or emitted objects missing `synthetic_data_flag=true`, `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `source_problem_ref`, `expert_spec_ref`, `training_data_ref`, `generator_version` or `parameter_set`.
- Any accepted run where `baseline_evaluated_first` is false, `baseline_comparison` is empty, or the mandatory baseline for the declared `problem_class` is absent from `candidate_models`.
- `generator_sensitivity_test.max_relative_metric_change` above the configured threshold while `selected_model` remains non-null or the report still claims demonstrated capability.
- Scenario stability variation above the allowed bound, especially when `demonstration_status` remains `demonstrated` without a limitation or known failure mode.
- Repeated generic limitation text across reports, such as missing concrete `gap_to_real_validation`, missing real-data requirements or empty `cannot_substitute` entries.
- Training runs whose `random_seed`, `split_strategy`, `scenario_bundle_refs`, `model_parameters`, `version_refs` or `version_hash` are absent, unstable or inconsistent between reruns.
- Output directories or artifact manifests containing model binaries, serving files, deployment configs, endpoint descriptors or operational prediction outputs.
- Logs showing automatic coercion, default filling or source-object rewrites for malformed input instead of structured rejection.
- Increase in `selected_model` values that prefer complex candidates while simpler candidates also satisfy metric, stability and sensitivity criteria.
- Report language containing validation, verification, production-ready, causal or decision-grade claims without field evidence from the proper downstream bridges.

## expensive_errors
- `EPISTEMIC_LABEL_OMISSION`: Missing synthetic-chain flags are cheap to block at object construction but expensive after downstream systems ingest the report, because consumers may treat synthetic support as evidence and derived records may need audit-wide quarantine. Prevention: enforce required flags and non-evidentiary limitation text before output registration.
- `WRONG_LINEAGE_ACCEPTED`: Accepting mismatched spec, dataset, generator or version refs is expensive because every metric, selection rationale and report becomes unreproducible and cannot be tied back to the governing assumptions. Prevention: compare lineage refs across all inputs before training and fail closed on any mismatch.
- `BASELINE_SKIPPED`: Skipping the mandatory baseline is expensive because all later model comparisons become invalid and rerunning experiments can change selected models, reports and downstream prioritization. Prevention: derive candidate order from the policy table and require `baseline_evaluated_first=true` before evaluating complex candidates.
- `SENSITIVITY_NOT_RECORDED`: Omitting generator sensitivity is expensive because a high synthetic metric may propagate even though it collapses under declared uncertainty, requiring retroactive reinterpretation of capability reports. Prevention: make `generator_sensitivity_test` required for `ModelEvalSummary` and `CapabilityDemonstrationReport`.
- `FORCED_SYNTHETIC_WINNER`: Naming a model when no candidate passed all criteria is expensive because downstream consumers may rank or prioritize based on a false demonstrated capability. Prevention: preserve `selected_model=null`, record failed criteria explicitly, and allow `not_demonstrated` as a valid report outcome.
- `PRODUCTION_OUTPUT_CREATED`: Persisting deployable model artifacts is expensive because it blurs governance boundaries, introduces security and lifecycle obligations, and may invite real-world use without validation. Prevention: keep trained objects transient, publish only records and reports, and fail conformance when deployable artifacts appear.
- `SILENT_OPTIONAL_METADATA_FABRICATION`: Fabricating absent confidence intervals, feature descriptions or review notes is expensive because later audit cannot distinguish real metadata from implementation defaults. Prevention: record missing optional data as metric limitations and never synthesize provenance-bearing fields.
- `MUTATED_SOURCE_ASSUMPTIONS`: Editing the expert spec or synthetic dataset inside this motor is expensive because it destroys the separation between motor_029, motor_030 and motor_031 and breaks version reconstruction. Prevention: treat inputs as immutable, require corrected upstream versions for material changes, and create new versioned outputs only from registered inputs.
