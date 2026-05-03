# Technical Schema — TAD Preliminary Prioritization Engine

Motor ID: motor_033

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ordenar preliminarmente inference cases activos usando señales sintéticas del motor_032.
why_it_exists:  Cuando hay múltiples inference cases activos compitiendo por recursos, se necesita una señal preliminar de orden de atención trazable y no arbitraria.
key_inputs:     synthetic_ml_support_register (motor_032), inference_cases (motor_013), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    preliminary_priority_register, ranking_basis, rank_uncertainty_record
key_objects:    PreliminaryPriorityRegister, RankingBasis, RankUncertaintyRecord
what_not_to_do: No puede ser TAD final. No puede usarse como evidencia para cerrar inference cases. Siempre requiere revisión con evidencia real.
design_notes:   Output es preliminary_priority_register, nunca TAD final. El ranking es exploratorio.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true, rank_is_preliminary=true

All schema sections below are completed with concrete content for this motor.
-->

## entities
PreliminaryPriorityRegister:
- Stage: `schema_technical` defines the persisted output shape; `implementation` instantiates it as the primary motor_033 output.
- Description: canonical register for one deterministic preliminary prioritization run. It contains the ordered active inference case entries, declares that the order is synthetic-support-only and non-evidentiary, links each entry to its ranking basis and uncertainty record, and states what real evidence is required before downstream decision-grade use.

RankingBasis:
- Stage: `schema_technical` defines the trace model; `implementation` instantiates one basis object per prioritization run.
- Description: traceable explanation object for how the register order was produced. It records source support references from motor_032, active inference case references from motor_013, phase contract constraints from motor_001, immutable version references from motor_002, deterministic weighting rules, exclusions, tie handling, and per-case rationale.

RankUncertaintyRecord:
- Stage: `schema_technical` defines the uncertainty model; `implementation` instantiates one uncertainty object per prioritization run.
- Description: uncertainty qualifier for the preliminary rank order. It records sparse support, unresolved provenance, weak rank separation, tie groups, conflicting synthetic signals, sensitivity notes, and the specific real evidence needed to confirm, revise, or invalidate the preliminary order.

## fields
PreliminaryPriorityRegister:
- `record_id`: string (required) — stable identifier for this register object.
- `motor_033_id`: string (required) — motor-scoped identifier for the prioritization run that produced this register.
- `version_id`: string (required) — immutable schema or artifact version identifier for this register instance.
- `created_at`: datetime string (required) — timestamp when the register object was first created.
- `updated_at`: datetime string (required) — timestamp when metadata for the register object was last updated without mutating source inputs.
- `version_hash`: string (required) — deterministic hash over the register payload, schema version, and input version references.
- `source_ref`: string (required) — canonical reference to the motor_032 `synthetic_ml_support_register` used as the source support set.
- `produced_by_motor`: string (required) — constant value `motor_033`.
- `produced_at`: datetime string (required) — timestamp when motor_033 emitted the register.
- `parent_id`: string or null (required) — previous register object superseded by this rebuild, or null for the first register for the same source problem.
- `source_problem_ref`: string (required) — inference case or problem reference required by the synthetic epistemology rules.
- `expert_spec_ref`: string (required) — reference to the expert problem spec associated with the source synthetic chain.
- `intended_use`: enum string (required) — constant value `preliminary_support`.
- `domain_validity_limits`: string (required) — explicit scope within which the preliminary ranking may be interpreted.
- `limitations_note`: string (required) — explicit non-evidentiary limitation statement for downstream consumers.
- `synthetic_support_flag`: boolean (required) — constant true; declares that the register is based on synthetic support.
- `non_evidentiary_flag`: boolean (required) — constant true; declares that the register cannot serve as field or validation evidence.
- `rank_is_preliminary`: boolean (required) — constant true; declares that rank order is exploratory and revisable.
- `ranking_basis_ref`: string (required) — foreign reference to the `RankingBasis.record_id` used by this register.
- `rank_uncertainty_ref`: string (required) — foreign reference to the `RankUncertaintyRecord.record_id` qualifying this register.
- `ranking_basis`: object (required) — embedded summary of ranking signals, weights, constraints, exclusions, and tie handling; must match the referenced RankingBasis.
- `ranked_cases`: list of objects (required) — ordered entries, each with `entry_id`, `inference_case_id`, `rank_position`, `priority_band`, `preliminary_score`, `ranking_basis_ref`, `rank_uncertainty_ref`, `source_support_refs`, `phase_contract_refs`, `version_record_refs`, `requires_real_evidence`, and `entry_limitations_note`.
- `requires_real_evidence`: list of strings (required) — evidence classes or observations needed to confirm, revise, or invalidate the register-level preliminary ranking.
- `cannot_substitute`: list of strings (required) — explicit list including `TAD_final`, `inference_case_closure`, `field_evidence`, `validation_data`, `Validation Data Bridge`, and `Verification Bridge`.
- `active_case_count`: integer (required) — number of active inference cases considered by the run.
- `ranked_case_count`: integer (required) — number of active inference cases emitted as ranked entries.
- `excluded_case_refs`: list of strings (required) — active cases excluded from ranking with corresponding reasons stored in the basis.
- `status`: enum string (required) — register processing status, one of `emitted`, `emitted_with_uncertainty`, or `rejected`.

RankingBasis:
- `record_id`: string (required) — stable identifier for this ranking basis object.
- `motor_033_id`: string (required) — motor-scoped identifier linking this basis to the producing prioritization run.
- `version_id`: string (required) — immutable schema or artifact version identifier for this basis instance.
- `created_at`: datetime string (required) — timestamp when the basis object was first created.
- `updated_at`: datetime string (required) — timestamp when metadata for the basis object was last updated without mutating source inputs.
- `version_hash`: string (required) — deterministic hash over basis content and input version references.
- `source_ref`: string (required) — canonical reference to the source support set used to build the basis.
- `produced_by_motor`: string (required) — constant value `motor_033`.
- `produced_at`: datetime string (required) — timestamp when motor_033 emitted the basis.
- `parent_id`: string or null (required) — previous basis object superseded by this rebuild, or null for the first basis for the same source problem.
- `source_problem_ref`: string (required) — inference case or problem reference required by the synthetic epistemology rules.
- `expert_spec_ref`: string (required) — reference to the expert problem spec associated with the source synthetic chain.
- `intended_use`: enum string (required) — constant value `preliminary_support`.
- `domain_validity_limits`: string (required) — explicit scope within which this basis may be interpreted.
- `limitations_note`: string (required) — explicit non-evidentiary limitation statement for this basis.
- `synthetic_support_flag`: boolean (required) — constant true.
- `non_evidentiary_flag`: boolean (required) — constant true.
- `rank_is_preliminary`: boolean (required) — constant true.
- `preliminary_priority_register_ref`: string (required) — foreign reference to the `PreliminaryPriorityRegister.record_id` that uses this basis.
- `source_support_refs`: list of strings (required) — motor_032 support item identifiers used as subordinate ranking signals.
- `source_case_refs`: list of strings (required) — motor_013 active inference case identifiers considered by the run.
- `phase_contract_refs`: list of strings (required) — motor_001 phase contract identifiers that allowed or constrained preliminary prioritization.
- `version_record_refs`: list of strings (required) — motor_002 version records required to rebuild the run.
- `signal_fields_used`: list of strings (required) — names of support fields used in scoring or ordering.
- `weighting_rule`: string (required) — deterministic weighting or ordering rule applied to the eligible signals.
- `priority_band_rule`: string (required) — deterministic rule mapping preliminary score ranges into priority bands.
- `tie_break_rule`: string (required) — deterministic tie handling rule, including when ties remain unresolved.
- `excluded_signal_reasons`: list of objects (required) — entries with `signal_ref`, `inference_case_id`, and `reason` for each excluded support signal.
- `case_rationales`: list of objects (required) — entries with `inference_case_id`, `rank_position`, `signal_summary`, `phase_constraint_summary`, and `rationale`.
- `rebuild_notes`: string (required) — instructions for reconstructing the ranking from recorded source and version references.

RankUncertaintyRecord:
- `record_id`: string (required) — stable identifier for this uncertainty object.
- `motor_033_id`: string (required) — motor-scoped identifier linking this uncertainty record to the producing prioritization run.
- `version_id`: string (required) — immutable schema or artifact version identifier for this uncertainty instance.
- `created_at`: datetime string (required) — timestamp when the uncertainty record was first created.
- `updated_at`: datetime string (required) — timestamp when metadata for the uncertainty record was last updated without mutating source inputs.
- `version_hash`: string (required) — deterministic hash over uncertainty content and input version references.
- `source_ref`: string (required) — canonical reference to the source support set whose limitations produced this uncertainty record.
- `produced_by_motor`: string (required) — constant value `motor_033`.
- `produced_at`: datetime string (required) — timestamp when motor_033 emitted the uncertainty record.
- `parent_id`: string or null (required) — previous uncertainty record superseded by this rebuild, or null for the first record for the same source problem.
- `source_problem_ref`: string (required) — inference case or problem reference required by the synthetic epistemology rules.
- `expert_spec_ref`: string (required) — reference to the expert problem spec associated with the source synthetic chain.
- `intended_use`: enum string (required) — constant value `preliminary_support`.
- `domain_validity_limits`: string (required) — explicit scope within which the uncertainty notes may be interpreted.
- `limitations_note`: string (required) — explicit non-evidentiary limitation statement for this uncertainty record.
- `synthetic_support_flag`: boolean (required) — constant true.
- `non_evidentiary_flag`: boolean (required) — constant true.
- `rank_is_preliminary`: boolean (required) — constant true.
- `preliminary_priority_register_ref`: string (required) — foreign reference to the `PreliminaryPriorityRegister.record_id` qualified by this uncertainty record.
- `ranking_basis_ref`: string (required) — foreign reference to the `RankingBasis.record_id` whose signals produced the uncertainty notes.
- `affected_case_refs`: list of strings (required) — inference case identifiers affected by uncertainty.
- `missing_signal_refs`: list of strings (required) — expected or referenced synthetic signals that were missing or unusable.
- `conflicting_signal_notes`: list of objects (required) — entries with `inference_case_id`, `signal_refs`, and `conflict_description`.
- `tie_groups`: list of lists of strings (required) — grouped inference case identifiers with unresolved or explicitly retained ties.
- `rank_separation_notes`: list of objects (required) — entries with `case_refs`, `separation_assessment`, and `effect_on_priority_band`.
- `generator_sensitivity_notes`: list of strings (required) — notes inherited from synthetic-support sensitivity conditions that affect preliminary ranking confidence.
- `insufficient_support_case_refs`: list of strings (required) — active inference cases lacking enough valid synthetic support to rank confidently.
- `requires_real_evidence`: list of strings (required) — real evidence needed to resolve the uncertainty conditions.
- `uncertainty_level`: enum string (required) — one of `low`, `moderate`, `high`, or `blocking`.

## relationships
- `PreliminaryPriorityRegister.ranking_basis_ref` references `RankingBasis.record_id`; cardinality is many registers over time to one basis per register version.
- `PreliminaryPriorityRegister.rank_uncertainty_ref` references `RankUncertaintyRecord.record_id`; cardinality is one uncertainty record per register version.
- `PreliminaryPriorityRegister.ranked_cases[].inference_case_id` references active `inference_cases.inference_case_id` from motor_013; closed, archived, missing, or inactive cases are invalid targets.
- `PreliminaryPriorityRegister.ranked_cases[].source_support_refs[]` references support item identifiers inside the motor_032 `synthetic_ml_support_register`; every referenced support item must carry `synthetic_support_flag=true` and `non_evidentiary_flag=true`.
- `PreliminaryPriorityRegister.ranked_cases[].phase_contract_refs[]` references motor_001 phase contract identifiers that permit preliminary prioritization as a subordinate analytic signal.
- `PreliminaryPriorityRegister.ranked_cases[].version_record_refs[]` references motor_002 version records for source support, inference cases, phase contracts, and schema versions.
- `RankingBasis.preliminary_priority_register_ref` references `PreliminaryPriorityRegister.record_id`, providing reverse traceability from the explanation object to the emitted register.
- `RankingBasis.source_support_refs[]` references motor_032 support records used in scoring, ordering, exclusion, or tie handling.
- `RankingBasis.source_case_refs[]` references motor_013 active inference case records considered by the ranking run.
- `RankingBasis.phase_contract_refs[]` references motor_001 phase contracts that constrain allowable use and handoff.
- `RankingBasis.version_record_refs[]` references motor_002 records needed for deterministic rebuild and audit.
- `RankUncertaintyRecord.preliminary_priority_register_ref` references `PreliminaryPriorityRegister.record_id`, binding uncertainty notes to the emitted rank order.
- `RankUncertaintyRecord.ranking_basis_ref` references `RankingBasis.record_id`, binding uncertainty notes to the signals, weights, exclusions, and tie rules that produced them.
- `RankUncertaintyRecord.affected_case_refs[]`, `tie_groups[][]`, and `insufficient_support_case_refs[]` reference motor_013 `inference_case_id` values and must not introduce case identifiers absent from the active case set.
- `source_ref`, `parent_id`, and all `version_record_refs` are immutable references; rebuilding produces a new object version rather than mutating the referenced source objects.

## identifiers
PreliminaryPriorityRegister:
- Canonical identifier: `record_id`.
- Motor-scoped run identifier: `motor_033_id`.
- Ranked entry identifier: `ranked_cases[].entry_id`, unique within the register.
- External case identifier: `ranked_cases[].inference_case_id`, inherited from motor_013 and not generated by motor_033.
- Identifier rule: `record_id` remains stable for the emitted register version; rebuilds with changed input versions create a new `record_id` and link back through `parent_id`.

RankingBasis:
- Canonical identifier: `record_id`.
- Motor-scoped run identifier: `motor_033_id`.
- External support identifiers: `source_support_refs[]`, inherited from motor_032 and not generated by motor_033.
- External contract identifiers: `phase_contract_refs[]`, inherited from motor_001 and not generated by motor_033.
- Identifier rule: one `RankingBasis.record_id` is referenced by exactly one register version; modified basis content requires a new `record_id` and `version_hash`.

RankUncertaintyRecord:
- Canonical identifier: `record_id`.
- Motor-scoped run identifier: `motor_033_id`.
- External case identifiers: `affected_case_refs[]`, `tie_groups[][]`, and `insufficient_support_case_refs[]`, inherited from motor_013 and not generated by motor_033.
- Identifier rule: one `RankUncertaintyRecord.record_id` is referenced by exactly one register version; changed uncertainty content requires a new `record_id` and `version_hash`.

## versioning
All three entities include the following required versioning fields:
- `version_id`: string (required) — immutable version identifier for the artifact instance. It must change when the schema version, source version set, ranking basis, rank order, uncertainty record, or required epistémic flags change.
- `created_at`: datetime string (required) — object creation timestamp. It is set once for the object version.
- `updated_at`: datetime string (required) — metadata update timestamp for the same object version. It must not be used to rewrite source references, rank positions, or epistémic labels.
- `version_hash`: string (required) — deterministic digest over the object payload, schema identifier, source references, `version_record_refs`, and mandatory epistémic flags.

Versioning rules:
- Source inputs from motor_032, motor_013, motor_001, and motor_002 are immutable for this motor; motor_033 records references and emits derived objects only.
- Any change in source support records, active case set, phase contracts, version records, weighting rule, exclusion reason, tie handling, uncertainty note, or required real-evidence statement creates a new object version.
- A rebuild must preserve the previous object through `parent_id`; it must not silently mutate the prior register, basis, or uncertainty record.
- `version_record_refs` in `RankingBasis` and `ranked_cases` must be sufficient to reconstruct the same preliminary order and explain why each signal was included or excluded.

## lineage
All three entities include the following required lineage fields:
- `source_ref`: string (required) — reference to the source `synthetic_ml_support_register` or source support subset used by the object.
- `produced_by_motor`: string (required) — constant value `motor_033`.
- `produced_at`: datetime string (required) — timestamp when the object was emitted by motor_033.
- `parent_id`: string or null (required) — prior object version from which this object was rebuilt, or null for an initial emission.

Lineage rules:
- `source_ref` must resolve to motor_032 support material marked with `synthetic_support_flag=true` and `non_evidentiary_flag=true`.
- Every ranked case must be traceable through `ranked_cases[].inference_case_id` to motor_013, through `phase_contract_refs` to motor_001, and through `version_record_refs` to motor_002.
- `RankingBasis` must preserve enough lineage to rebuild inclusion, exclusion, weighting, priority-band assignment, and tie handling without consulting mutable state.
- `RankUncertaintyRecord` must preserve lineage from each uncertainty note to the affected case references and source signal references that caused the uncertainty.
- Lineage fields do not grant evidentiary authority. Every lineage path remains subordinate to the mandatory flags `synthetic_support_flag=true`, `non_evidentiary_flag=true`, and `rank_is_preliminary=true`.
- If any required lineage reference cannot be resolved, the motor must reject emission rather than produce a partial register.
