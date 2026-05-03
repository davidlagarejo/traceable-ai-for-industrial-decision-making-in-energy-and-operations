# Operational Rules — ML Experiment / Model Training & Evaluation Engine

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

## rules
1. The motor must process only `synthetic_dataset` inputs produced by motor_030 and tied to an approved `expert_problem_spec` from motor_029.
2. The motor must verify that `source_problem_ref`, `expert_spec_ref`, `generator_version` and `parameter_set` are present and aligned before any training begins.
3. Every emitted output must include `synthetic_support_flag=true` and `non_evidentiary_flag=true`; records derived directly from the dataset must also preserve `synthetic_data_flag=true`.
4. The `experiment_config` must declare `problem_class`, `primary_metric`, candidate model families, baseline model, split strategy, random seed, scenario bundle refs and model-selection thresholds.
5. Candidate model families must be selected from the `problem_class` mapping in `synthetic_epistemology_rules.md`; the baseline required by that mapping must be evaluated before any more complex model.
6. If a deterministic or statistical rule already satisfies the problem according to the expert spec, the motor must record that path and avoid unnecessary ML training.
7. A model may be selected only if it meets the primary metric threshold, scenario-stability criterion, generator-sensitivity criterion and simplicity criterion in that order.
8. If no candidate satisfies the selection criteria, `selected_model` must be null and the report must state that capability was not demonstrated under the synthetic conditions.
9. The `capability_demonstration_report` must explicitly state `gap_to_real_validation`, `gap_to_deployment`, `known_failure_modes`, `domain_validity_limits` and `limitations_note`.
10. All run records, metrics and reports must remain reproducible from recorded inputs, seeds, versions and parameters.

## invariants
- `source_problem_ref` is never empty on any accepted input or emitted output.
- `expert_spec_ref` is never empty on any accepted input or emitted output.
- `training_data_ref` always points to a motor_030 synthetic generation run and never to field evidence.
- `non_evidentiary_flag` is always true on every output.
- `synthetic_support_flag` is always true on every output exposed outside motor_031.
- No output from this motor changes the evidentiary level of a claim, inference case or decision record.
- Version refs and lineage refs are preserved without silent mutation.
- A higher metric on synthetic data never removes the required limitations note.

## forbidden_operations
- Producing production-ready models, serialized model binaries, deployment artifacts, model-serving endpoints or operational inference pipelines.
- Using `capability_demonstration_report` as evidence of field validation, verification, site truth or decision-grade support.
- Training on real field data, validation bridge data, verification bridge data or any dataset not emitted by motor_030 as synthetic.
- Running experiments on a draft expert spec or on a spec with unresolved critical ambiguity.
- Selecting complex models while skipping the baseline required by the model-selection policy.
- Promoting synthetic performance metrics to field evidence, validation data, causal proof or final TAD status.
- Modifying `expert_problem_spec`, `synthetic_dataset`, global version records or motor state as part of experiment execution.
- Hiding failed model-selection outcomes by forcing a best model when the criteria were not met.
