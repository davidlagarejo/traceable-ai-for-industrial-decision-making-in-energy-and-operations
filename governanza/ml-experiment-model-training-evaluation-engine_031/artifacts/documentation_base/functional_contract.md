# Functional Contract — ML Experiment / Model Training & Evaluation Engine

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

## inputs
- `synthetic_dataset`: structured dataset object - produced by motor_030; includes `synthetic_generation_run.run_id`, feature matrix, target field when supervised, scenario bundle metadata, `source_problem_ref`, `expert_spec_ref`, `generator_version`, `parameter_set`, `synthetic_data_flag=true` and `non_evidentiary_flag=true`.
- `expert_problem_spec`: structured problem specification - produced by motor_029; includes `spec_id`, `source_problem_ref`, `problem_class`, `primary_metric`, target definition or unsupervised objective, domain validity limits, ambiguity register status and allowed model-selection constraints.
- `version_records`: lineage and version reference set - produced by motor_002; includes immutable references for the dataset, spec, generator version, experiment configuration template and artifact version chain.

## outputs
- `training_run_record`: structured run record - stored as the motor_031 training artifact and consumed by later schema, tests, conformance review and audit flows; records candidate models, seeds, split strategy, training parameters, source refs, version refs, `synthetic_data_flag=true`, `synthetic_support_flag=true` and `non_evidentiary_flag=true`.
- `model_eval_summary`: structured evaluation summary - consumed by `capability_demonstration_report` and downstream motor_032 only as subordinate synthetic support; records metrics, baseline comparison, stability by scenario, generator sensitivity result, selected model name or null, source refs, version refs, `synthetic_data_flag=true`, `synthetic_support_flag=true` and `non_evidentiary_flag=true`.
- `capability_demonstration_report`: structured report object - consumed by motor_032 as labeled preliminary support; records demonstrated capability under synthetic assumptions, limitations, `gap_to_real_validation`, `gap_to_deployment`, known synthetic failure modes, source refs, version refs, `synthetic_support_flag=true` and `non_evidentiary_flag=true`.

## limits
- The motor never accepts real field datasets, validation bridge datasets, verification bridge datasets, production telemetry or manually pasted data outside a registered `synthetic_dataset`.
- The motor never accepts an `expert_problem_spec` in draft status, a spec with unresolved critical ambiguity, a dataset whose `expert_spec_ref` differs from the supplied spec, or inputs missing lineage/version references.
- The motor never accepts a dataset missing synthetic and non-evidentiary labeling, including `synthetic_data_flag=true` and `non_evidentiary_flag=true` inherited from motor_030.
- The motor never produces production-ready models, serialized model binaries, deployment configurations, API endpoints or operational inference outputs.
- The motor never produces field validation evidence, verification claims, causal claims, decision-grade inference records or final TAD outputs.
- The motor never promotes synthetic metrics above `synthetic_support`; all outputs remain non evidentiary even when model metrics are high.

## validations
- Reject input with `ERROR_INPUT_LINEAGE_MISMATCH` when `source_problem_ref`, `expert_spec_ref`, generator references or version records do not align across `synthetic_dataset`, `expert_problem_spec` and `version_records`.
- Reject input with `ERROR_MISSING_EPISTEMIC_FLAGS` when required synthetic-chain flags are absent or false; outputs must include `synthetic_support_flag=true` and `non_evidentiary_flag=true`, and training/evaluation records must also preserve `synthetic_data_flag=true` because they derive directly from synthetic data.
- Reject input with `ERROR_UNSUPPORTED_PROBLEM_CLASS` when `problem_class` is missing or not covered by the model-selection policy in `synthetic_epistemology_rules.md`.
- Reject input with `ERROR_CRITICAL_AMBIGUITY` when the expert spec contains unresolved ambiguity with critical impact.
- Reject input with `ERROR_INSUFFICIENT_SYNTHETIC_SAMPLE` when the dataset has fewer than 50 rows for an ML experiment that is not explicitly covered by a deterministic or statistical baseline path.
- Before training, require a baseline model or deterministic/statistical baseline mandated for the declared `problem_class`.
- Before selecting any model, require that metric threshold, scenario stability, `generator_sensitivity_test` and interpretability precedence are evaluated in that order.
- Emit `selected_model=null` rather than forcing a winner when no candidate satisfies the four model-selection criteria.
- Before emitting output, require every object to include `source_problem_ref`, `expert_spec_ref`, `generator_version`, `parameter_set`, `intended_use`, `domain_validity_limits`, `limitations_note`, lineage refs and immutable version refs.
- Before emitting `capability_demonstration_report`, require explicit `gap_to_real_validation`, `gap_to_deployment` and `known_failure_modes`.
