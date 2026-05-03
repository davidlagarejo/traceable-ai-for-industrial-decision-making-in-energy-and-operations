# Technical Schema — Problem Formalization / Expert Problem Spec Engine

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

All open placeholders in this file have been resolved with concrete technical schema content.
-->

## entities
- `ExpertProblemSpec`: primary versioned output of `motor_029`. It is the formal problem contract derived from one activated `motor_013.InferenceCase`, phase authority from `motor_001`, version records from `motor_002` and canonical terms from `motor_003`. It lives in the `schema_technical` stage as the canonical persisted shape for the runtime output consumed by `motor_030`; it is non-evidentiary and only supports exploration.
- `AmbiguityRegister`: versioned control record owned by one `ExpertProblemSpec`. It lists every ambiguity discovered while formalizing the inference case and records whether critical unresolved ambiguity blocks handoff to `motor_030`. It lives in the `schema_technical` stage as a persisted gate/audit object emitted with the spec.
- `AmbiguityItem`: structured child item inside an `AmbiguityRegister`. It records the field, source, severity, resolution state and impact of one ambiguity without silently collapsing it into a constraint. It lives in the `schema_technical` stage as an embedded or child record used to compute `has_unresolved_critical`.
- `ParameterConstraint`: versioned child output owned by one `ExpertProblemSpec`. It defines one parameter, variable, unit, category, interval or compatibility constraint that downstream synthetic generation must respect. It lives in the `schema_technical` stage as the deterministic constraint shape consumed by `motor_030`.

## fields
`ExpertProblemSpec`
- `spec_id: string` (required) — stable canonical identifier for the expert problem specification.
- `record_id: string` (required) — immutable storage identifier for this persisted spec version; equal to `spec_id` for first-version storage unless the persistence layer separates logical and version records.
- `source_problem_ref: string` (required) — `motor_013.InferenceCase.case_id` or compatible `inference_case_id` from which the spec was formalized.
- `phase_contract_ref: string` (required) — `motor_001` phase contract reference authorizing this formalization and its downstream synthetic-chain use.
- `taxonomy_snapshot_ref: string` (required) — `motor_003` taxonomy snapshot or canonical taxonomy version used to resolve terms.
- `version_record_refs: list[string]` (required) — `motor_002` version records for the inference case, phase contract, taxonomy snapshot and any other source object used.
- `spec_version: string` (required) — domain-level spec version label exposed to downstream motors.
- `problem_statement: string` (required) — formalized problem question or objective copied from the inference case and normalized only within canonical taxonomy limits.
- `problem_class: enum[classification_binary, classification_multiclass, regression_continuous, regression_interval, ranking, clustering_exploratory, anomaly_detection, survival_hazard, sensitivity_analysis]` (required) — allowed analytical class for downstream synthetic-chain planning.
- `target_variable_ref: string | null` (required) — canonical taxonomy reference for the target variable when the problem class has a target; null for exploratory classes that do not define one.
- `expert_assumptions: list[string]` (required) — explicit expert assumptions that condition the spec; empty only when the source case declares none.
- `domain_constraints_ref: list[string]` (required) — references to governing domain constraints, phase limits or source-case constraints used by the spec.
- `parameter_constraints_ref: list[string]` (required) — ordered `ParameterConstraint.constraint_id` values owned by this spec.
- `ambiguity_register_ref: string` (required) — `AmbiguityRegister.register_id` owned by this spec.
- `handoff_allowed: boolean` (required) — true only when required fields are present and the ambiguity register has no unresolved critical item.
- `handoff_block_reason: string | null` (required) — machine-readable reason when `handoff_allowed=false`; null when handoff is allowed.
- `lineage_refs: list[string]` (required) — complete upstream lineage references sufficient to rebuild the spec.
- `provenance_refs: list[string]` (required) — source provenance references copied from the inference case, phase contract, version records and taxonomy.
- `non_evidentiary_flag: boolean` (required) — constant `true`; the spec is a generator contract, not field evidence.
- `intended_use: enum[exploration]` (required) — constant `exploration`.
- `domain_validity_limits: string` (required) — explicit domain scope in which the formalized problem and constraints are valid.
- `limitations_note: string` (required) — explicit statement that the spec is expert formalization and cannot validate real-world claims.
- `source_ref: string` (required) — primary lineage anchor, normally `source_problem_ref`.
- `produced_by_motor: string` (required) — constant value `motor_029`.
- `produced_at: datetime` (required) — timestamp when the spec version was emitted.
- `parent_id: string | null` (required) — prior `ExpertProblemSpec.record_id` superseded for the same `source_problem_ref`; null for first emission.
- `version_id: string` (required) — stable version identifier for this persisted spec record.
- `created_at: datetime` (required) — timestamp when this spec record was first created.
- `updated_at: datetime` (required) — latest governed metadata update timestamp.
- `version_hash: string` (required) — deterministic hash over material spec content, source references, epistemic flags, lineage and version metadata.

`AmbiguityRegister`
- `register_id: string` (required) — stable canonical identifier for the ambiguity register.
- `record_id: string` (required) — immutable storage identifier for this register version.
- `spec_id: string` (required) — owning `ExpertProblemSpec.spec_id`.
- `source_problem_ref: string` (required) — inference case reference shared with the owning spec.
- `items: list[AmbiguityItem]` (required) — structured ambiguity items; empty only when no ambiguity was found.
- `has_unresolved_critical: boolean` (required) — true when any item has `impact_if_unresolved=critical` and `resolution_status` is not `resolved`.
- `highest_unresolved_impact: enum[none, minor, material, critical]` (required) — highest impact among unresolved items.
- `handoff_allowed: boolean` (required) — false whenever `has_unresolved_critical=true`; mirrors the spec handoff decision for audit.
- `blocking_item_refs: list[string]` (required) — `AmbiguityItem.ambiguity_id` values that block handoff; empty when none block.
- `non_evidentiary_flag: boolean` (required) — constant `true`.
- `intended_use: enum[exploration]` (required) — constant `exploration`.
- `domain_validity_limits: string` (required) — scope inherited from or consistent with the owning spec.
- `limitations_note: string` (required) — limitation note inherited from or consistent with the owning spec.
- `source_ref: string` (required) — primary lineage anchor, normally `source_problem_ref`.
- `produced_by_motor: string` (required) — constant value `motor_029`.
- `produced_at: datetime` (required) — timestamp when the register version was emitted.
- `parent_id: string | null` (required) — prior `AmbiguityRegister.record_id` superseded for the same spec lineage; null for first emission.
- `version_id: string` (required) — stable version identifier for this persisted register record.
- `created_at: datetime` (required) — timestamp when this register record was first created.
- `updated_at: datetime` (required) — latest governed metadata update timestamp.
- `version_hash: string` (required) — deterministic hash over register items, handoff status, source references, epistemic flags and lineage.

`AmbiguityItem`
- `ambiguity_id: string` (required) — stable identifier for one ambiguity item within a register.
- `register_id: string` (required) — owning `AmbiguityRegister.register_id`.
- `spec_id: string` (required) — owning `ExpertProblemSpec.spec_id`.
- `source_problem_ref: string` (required) — inference case reference shared with the owning register.
- `field_ref: string` (required) — dotted path or field name affected by the ambiguity, such as `problem_class`, `parameter_constraints.capacity_kw.allowed_domain` or `target_variable_ref`.
- `source_input_ref: string` (required) — source object or field that introduced the ambiguity.
- `description: string` (required) — concise description of the unresolved, resolved or deferred ambiguity.
- `severity: enum[low, medium, high, critical]` (required) — severity assigned during formalization.
- `resolution_status: enum[open, resolved, deferred]` (required) — current resolution state.
- `impact_if_unresolved: enum[minor, material, critical]` (required) — impact on spec correctness or handoff eligibility if the ambiguity remains unresolved.
- `resolution_note: string | null` (required) — explicit resolution rationale when resolved or deferred; null while open.
- `owner_ref: string | null` (required) — accountable reviewer, source authority or governance role when known; null only when no owner is available in the source context.
- `blocks_handoff: boolean` (required) — true when the item prevents handoff to `motor_030`.
- `created_at: datetime` (required) — timestamp when the item was first recorded.
- `updated_at: datetime` (required) — latest governed metadata update timestamp.

`ParameterConstraint`
- `constraint_id: string` (required) — stable canonical identifier for one parameter constraint.
- `record_id: string` (required) — immutable storage identifier for this persisted constraint version.
- `spec_id: string` (required) — owning `ExpertProblemSpec.spec_id`.
- `source_problem_ref: string` (required) — inference case reference shared with the owning spec.
- `parameter_name: string` (required) — canonical parameter, variable, unit or category name exposed to downstream generation.
- `canonical_term_ref: string` (required) — `motor_003.CanonicalEntity.canonical_id` or compatible canonical taxonomy reference; an unmapped required term must be represented by an ambiguity item instead of a silent local label.
- `value_type: enum[integer, float, category, boolean, interval, datetime, string]` (required) — technical value type allowed for the parameter.
- `allowed_domain: object` (required) — structured domain definition, such as `{min, max, inclusive_min, inclusive_max}`, `{categories}`, `{pattern}` or `{interval_start, interval_end}` depending on `value_type`.
- `unit: string | null` (required) — canonical unit reference or null only when the value is unitless or categorical.
- `constraint_kind: enum[range, category_set, equality, inequality, compatibility_rule, required_presence, exclusion_rule]` (required) — deterministic constraint category.
- `required: boolean` (required) — whether downstream generation must include this parameter.
- `compatibility_refs: list[string]` (required) — other `ParameterConstraint.constraint_id` values this constraint depends on or restricts; empty when independent.
- `constraint_rationale: string` (required) — source rationale from the expert case, phase contract or taxonomy boundary.
- `uncertainty_treatment: string` (required) — how uncertainty is represented, preserved or bounded for this parameter.
- `ambiguity_item_refs: list[string]` (required) — ambiguity items that qualify this constraint; empty when none apply.
- `non_evidentiary_flag: boolean` (required) — constant `true`.
- `intended_use: enum[exploration]` (required) — constant `exploration`.
- `domain_validity_limits: string` (required) — scope inherited from or consistent with the owning spec.
- `limitations_note: string` (required) — limitation note inherited from or consistent with the owning spec.
- `source_ref: string` (required) — primary lineage anchor for the constraint, normally the source field or inference case reference that supplied it.
- `produced_by_motor: string` (required) — constant value `motor_029`.
- `produced_at: datetime` (required) — timestamp when the constraint version was emitted.
- `parent_id: string | null` (required) — prior `ParameterConstraint.record_id` superseded for the same spec and parameter lineage; null for first emission.
- `version_id: string` (required) — stable version identifier for this persisted constraint record.
- `created_at: datetime` (required) — timestamp when this constraint record was first created.
- `updated_at: datetime` (required) — latest governed metadata update timestamp.
- `version_hash: string` (required) — deterministic hash over parameter identity, allowed domain, rationale, uncertainty treatment, source references, epistemic flags and lineage.

## relationships
- `ExpertProblemSpec.source_problem_ref` references one activated `motor_013.InferenceCase.case_id` or compatible `inference_case_id`. The reference is read-only; this motor never mutates the inference case.
- `ExpertProblemSpec.phase_contract_ref` references the `motor_001` phase contract that permits synthetic-chain formalization for the source case.
- `ExpertProblemSpec.version_record_refs[]` references `motor_002` records that identify the exact input versions used for rebuild.
- `ExpertProblemSpec.taxonomy_snapshot_ref` and `ParameterConstraint.canonical_term_ref` reference `motor_003` canonical taxonomy objects used to constrain terminology.
- `ExpertProblemSpec.ambiguity_register_ref` references exactly one `AmbiguityRegister.register_id` for the same `source_problem_ref`.
- `AmbiguityRegister.spec_id` references exactly one `ExpertProblemSpec.spec_id`; a register cannot be shared across specs.
- `AmbiguityRegister.items[]` embeds or references `AmbiguityItem` records whose `register_id` equals the owning register.
- `AmbiguityItem.spec_id` and `AmbiguityItem.register_id` must reference the same owning spec/register pair.
- `ExpertProblemSpec.parameter_constraints_ref[]` references one or more `ParameterConstraint.constraint_id` values owned by the same `spec_id`; the list may be empty only for a rejected or non-handoffable draft output that records blocking ambiguity.
- `ParameterConstraint.spec_id` references the owning `ExpertProblemSpec.spec_id`; a constraint cannot be reassigned to another spec by mutation.
- `ParameterConstraint.compatibility_refs[]` references other constraints in the same `spec_id`; cross-spec compatibility references are invalid.
- `ParameterConstraint.ambiguity_item_refs[]` references ambiguity items in the owning register when a constraint is qualified by unresolved or deferred ambiguity.
- `parent_id` fields reference only prior records of the same entity type. They must not point to upstream inference cases, phase contracts, taxonomy terms or downstream synthetic generation records.
- `ExpertProblemSpec` is the only object eligible for handoff to `motor_030`, and only when `handoff_allowed=true`, `AmbiguityRegister.has_unresolved_critical=false` and all required epistemic fields are present.

## identifiers
- `ExpertProblemSpec`: canonical identifier is `spec_id`; persisted version identity is `record_id` plus `version_id`. The deterministic identifier should be derived from `motor_029`, `source_problem_ref`, `phase_contract_ref`, `taxonomy_snapshot_ref`, `problem_class`, material constraint set and source version references.
- `AmbiguityRegister`: canonical identifier is `register_id`; persisted version identity is `record_id` plus `version_id`. The deterministic identifier should be derived from `motor_029`, `spec_id`, `source_problem_ref` and the register content hash.
- `AmbiguityItem`: canonical identifier is `ambiguity_id`. It should be derived from `register_id`, `field_ref`, `source_input_ref`, normalized description and impact fields so repeated detection of the same ambiguity is idempotent.
- `ParameterConstraint`: canonical identifier is `constraint_id`; persisted version identity is `record_id` plus `version_id`. The deterministic identifier should be derived from `motor_029`, `spec_id`, `parameter_name`, `canonical_term_ref`, `constraint_kind`, normalized allowed domain and source reference.
- `record_id` identifies one immutable persisted version and must not be reused for incompatible content.
- Natural-language labels, timestamps alone, list position and display names are not valid stable identifiers.
- Upstream identifiers from `motor_001`, `motor_002`, `motor_003` and `motor_013` are preserved as references and are never replaced with locally invented identifiers.

## versioning
- Every persisted `ExpertProblemSpec`, `AmbiguityRegister` and `ParameterConstraint` includes `version_id`, `created_at`, `updated_at` and `version_hash`.
- `AmbiguityItem` includes `created_at` and `updated_at`; when stored as a standalone persisted child record it must also inherit the register version envelope or carry its own `version_id` and `version_hash`.
- `version_id` identifies one governed version of the entity. It changes when material content changes, including problem class, formal problem statement, target variable, expert assumptions, domain constraints, ambiguity states, parameter allowed domains, uncertainty treatment, epistemic flags or lineage references.
- `created_at` is set once when the version is first emitted.
- `updated_at` changes only for governed metadata correction or supersession bookkeeping that preserves audit history; silent mutation of prior content is invalid.
- `version_hash` is computed deterministically from normalized material payload, stable identifiers, source references, epistemic flags, lineage fields and parent linkage, excluding non-material transport metadata.
- `ExpertProblemSpec.version_hash` includes `source_problem_ref`, `phase_contract_ref`, `taxonomy_snapshot_ref`, sorted `version_record_refs`, `problem_statement`, `problem_class`, `target_variable_ref`, sorted `expert_assumptions`, sorted `domain_constraints_ref`, sorted `parameter_constraints_ref`, `ambiguity_register_ref`, handoff fields, epistemic flags and lineage.
- `AmbiguityRegister.version_hash` includes `spec_id`, `source_problem_ref`, normalized ambiguity items, `has_unresolved_critical`, `highest_unresolved_impact`, `blocking_item_refs`, handoff status, epistemic flags and lineage.
- `ParameterConstraint.version_hash` includes `spec_id`, `source_problem_ref`, `parameter_name`, `canonical_term_ref`, `value_type`, normalized `allowed_domain`, `unit`, `constraint_kind`, `required`, sorted `compatibility_refs`, `constraint_rationale`, `uncertainty_treatment`, `ambiguity_item_refs`, epistemic flags and lineage.
- A material rebuild for the same `source_problem_ref` creates a new `version_id`, new `version_hash` and `parent_id` linkage rather than rewriting the previous record.
- Re-running the motor with identical accepted inputs, rule versions and taxonomy versions must reproduce the same canonical identifiers and version hashes, excluding timestamps that are explicitly outside material hashing.

## lineage
- Every persisted motor_029 output includes `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref` is the primary lineage anchor. For `ExpertProblemSpec` and `AmbiguityRegister` it is normally `source_problem_ref`; for `ParameterConstraint` it is the source field, taxonomy term or inference case reference that supplied the constraint.
- `produced_by_motor` is always `motor_029` for `ExpertProblemSpec`, `AmbiguityRegister` and `ParameterConstraint`.
- `produced_at` records when `motor_029` emitted the output version and must remain stable after persistence.
- `parent_id` is null for first emission and otherwise references the prior persisted record of the same entity type superseded by a governed rebuild or correction.
- `lineage_refs` and `provenance_refs` must preserve enough information to reconstruct the output from the source inference case, phase contract, version records, taxonomy snapshot, formalization rules and prior parent record when applicable.
- Missing `source_ref`, missing `produced_by_motor`, missing `produced_at`, missing required parent linkage for supersession, missing dependency version references or missing upstream provenance makes the entity invalid rather than silently repairable.
- Lineage metadata does not authorize this motor to generate synthetic data, run ML, validate real-world claims, mutate source objects or promote expert formalization above non-evidentiary exploratory status.
