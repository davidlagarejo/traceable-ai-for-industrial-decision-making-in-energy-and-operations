# Failure Modes Spec — Problem Formalization / Expert Problem Spec Engine

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

## failure_modes_list
- `FM029_CRITICAL_AMBIGUITY_BYPASS`: `AmbiguityRegister.has_unresolved_critical=true` or any ambiguity item has `impact_if_unresolved=critical` with `resolution_status` other than `resolved` while `ExpertProblemSpec.handoff_allowed=true` -> a non-handoffable problem definition can enter `motor_030`, causing synthetic generation from unresolved assumptions -> set `handoff_allowed=false`, set `handoff_block_reason=critical_ambiguity_unresolved`, emit `ERR_CRITICAL_AMBIGUITY_UNRESOLVED`, and rebuild only after the ambiguity is resolved through the governed source or expert review path.
- `FM029_EPISTEMIC_FLAG_OMISSION`: any emitted `ExpertProblemSpec`, `AmbiguityRegister` or `ParameterConstraint` lacks `non_evidentiary_flag=true`, `intended_use=exploration`, `source_problem_ref`, `domain_validity_limits` or `limitations_note` -> downstream systems may treat expert formalization as field evidence or decision-grade support -> abort output assembly with `ERR_EPISTEMIC_FLAGS_MISSING`, reject registration, and regenerate the object only after all mandatory epistemic fields are present.
- `FM029_TAXONOMY_UNMAPPED_TERM_ACCEPTED`: a required parameter, unit, category or target variable is not mapped to `canonical_taxonomy` but is accepted as a local label -> `ParameterConstraint.canonical_term_ref` is empty or unstable, creating incompatible downstream generation domains -> create an `AmbiguityItem` with `field_ref`, `source_input_ref`, impact, owner where available and `blocks_handoff` based on severity; do not create a handoffable constraint until the canonical mapping exists or the ambiguity is explicitly resolved.
- `FM029_LINEAGE_VERSION_GAP`: version records or provenance references are missing for the source inference case, phase contract, taxonomy snapshot or prior parent version -> `version_hash`, `lineage_refs` and rebuild semantics cannot be trusted -> reject with `ERR_MISSING_PROVENANCE`, request the missing `motor_002` records, and emit no partial handoffable output.
- `FM029_SCOPE_CREEP_INTO_GENERATION_OR_ML`: the motor emits synthetic rows, sampling runs, generator versions, trained model references, model metrics, rankings, validation claims or decision recommendations -> `motor_029` mixes responsibilities belonging to `motor_030`, `motor_031`, `motor_032`, `motor_033` or real-evidence bridges -> fail conformance, remove out-of-scope fields, and restrict output to `expert_problem_spec`, `ambiguity_register` and `parameter_constraints`.
- `FM029_DETERMINISM_BREAK_ON_REBUILD`: identical material inputs, phase contract, taxonomy snapshot and version records produce different `spec_id`, `constraint_id`, `register_id` or material `version_hash` values -> duplicate or incompatible specs appear for the same source version set -> normalize identifier and hash derivation from declared material fields, exclude non-material timestamps from material hashes, and use `parent_id` only for governed material source changes.
- `FM029_PARAMETER_CONSTRAINT_UNDER_SPECIFICATION`: a `ParameterConstraint` is emitted without `value_type`, structured `allowed_domain`, canonical unit when applicable, `constraint_rationale` or `uncertainty_treatment` -> `motor_030` must invent ranges, units or sampling behavior locally -> reject the incomplete constraint, record the missing element as an ambiguity when it comes from the source case, and allow handoff only after all required constraint fields are explicit.

## anti_patterns
- Treating `ExpertProblemSpec` as measured field evidence, validation data or a decision-grade claim instead of as a non-evidentiary generator contract.
- Collapsing expert ambiguity into precise-looking constraints without an `AmbiguityItem`, severity, impact and resolution state.
- Building the motor around free-text prompt output instead of deterministic validation of structured fields, canonical taxonomy references, lineage and epistemic flags.
- Coupling the output directly to `motor_030` generator internals, `motor_031` model selection or downstream ranking logic instead of publishing the bounded contract objects only.
- Mutating upstream `inference_cases`, `phase_contracts`, `version_records` or `canonical_taxonomy` inside this motor to make formalization pass.
- Generating placeholder identifiers, units, taxonomy terms or version references when required upstream metadata is missing.
- Sharing one `AmbiguityRegister` across multiple specs or allowing a `ParameterConstraint` to be reassigned to another `spec_id` by mutation.
- Storing constraints only in narrative prose, making `allowed_domain`, `value_type`, `canonical_term_ref` and uncertainty handling non-machine-checkable.
- Allowing output payloads to contain synthetic datasets, generation manifests, training runs, model metrics, causal conclusions or field-validation language.

## degradation_signals
- Metric `motor_029.output_epistemic_flag_missing_count > 0` for any emitted object.
- Log pattern `ERR_EPISTEMIC_FLAGS_MISSING` appearing after output assembly has already begun, indicating flag validation is too late in the pipeline.
- Metric `motor_029.handoff_critical_conflict_count > 0`, where `handoff_allowed=true` coexists with `has_unresolved_critical=true` or a critical unresolved ambiguity item.
- Rising `motor_029.unmapped_required_term_count` or repeated ambiguity items for the same `canonical_term_ref` gap across runs.
- Any `ParameterConstraint` with empty `allowed_domain`, empty `constraint_rationale`, missing `uncertainty_treatment` or local labels in place of canonical taxonomy references.
- Repeated generic `domain_validity_limits` or `limitations_note` text across unrelated `problem_class` values, suggesting copy-forward rather than domain-specific formalization.
- Downstream `motor_030` rejection logs caused by missing units, incompatible value types, unbounded numeric ranges or absent compatibility rules.
- Rebuild drift where identical material inputs produce different canonical identifiers or material hashes outside the fields explicitly excluded from hashing.
- Payload scan finds forbidden field names such as `synthetic_dataset`, `generation_manifest`, `training_run_record`, `selected_model`, `metric_auc`, `ranking_basis` or `field_validation_result`.
- Increasing ratio of specs blocked for missing provenance or version records, indicating upstream handoff validation is not enforced before formalization.
- `lineage_refs` or `version_record_refs` counts lower than the required source case, phase contract and taxonomy version references.

## expensive_errors
- Critical ambiguity leaked into handoff: expensive because every synthetic dataset, model experiment and support register derived from the spec must be invalidated or rebuilt. Prevent it by computing `handoff_allowed` from `AmbiguityRegister.has_unresolved_critical` and blocking any item with `impact_if_unresolved=critical` until resolved.
- Missing epistemic flags: expensive because it contaminates the evidence hierarchy and can make expert formalization appear stronger than `expert_spec` level. Prevent it with schema-level required fields for `non_evidentiary_flag=true`, `intended_use=exploration`, `domain_validity_limits`, `limitations_note` and `source_problem_ref` on every output object.
- Silent taxonomy drift: expensive because downstream synthetic data can be generated on non-canonical parameters that cannot join, compare or rebuild against system terms. Prevent it by requiring `canonical_term_ref` for every parameter, unit, category and target variable, with unmapped terms recorded as ambiguities instead of accepted labels.
- Lineage or version gap: expensive because the spec cannot be reconstructed, compared or superseded correctly after source changes. Prevent it by rejecting inputs without governed `version_records`, `provenance_refs`, `source_ref`, `produced_by_motor`, `produced_at`, `version_id`, `version_hash` and required `parent_id` linkage when superseding.
- Silent mutation of prior specs or upstream objects: expensive because audit history and rebuild semantics are destroyed, making later corrections impossible to localize. Prevent it by treating prior records as immutable, emitting new versions for material changes and routing upstream corrections back to the owning motor.
- Scope creep into generation, ML or decision support: expensive because it creates cross-motor artifacts that fail conformance and may need removal from multiple downstream stores. Prevent it with an output whitelist limited to `ExpertProblemSpec`, `AmbiguityRegister`, `AmbiguityItem` and `ParameterConstraint`, plus forbidden-field scans before persistence.
- Under-specified parameter domains: expensive because `motor_030` would need to invent ranges, units or uncertainty behavior, producing synthetic data that cannot be defended as derived from the expert contract. Prevent it by requiring structured `allowed_domain`, `value_type`, unit handling, rationale and uncertainty treatment before handoff.
