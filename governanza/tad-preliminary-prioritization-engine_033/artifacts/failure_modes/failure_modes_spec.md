# Failure Modes Spec — TAD Preliminary Prioritization Engine

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

All sections below are completed with concrete content for this motor.
-->

## failure_modes_list
FM-033-001_MISSING_SYNTHETIC_FLAGS: a motor_032 support item lacks `synthetic_support_flag=true`, lacks `non_evidentiary_flag=true`, or arrives with `intended_use` other than `preliminary_support` -> the motor may ingest unlabelled synthetic material and emit a register whose epistemic status is ambiguous -> reject the run with `ERR_MISSING_EPISTEMIC_FLAGS`, emit no `preliminary_priority_register`, and require corrected source support records before rebuild.

FM-033-002_RANK_PROMOTION_LEAK: a caller requests `output_type=TAD_final`, `close_inference_case=true`, decision-grade output, or downstream logic treats `preliminary_priority_register` as field evidence -> the rank order appears to close or validate an inference case even though it is synthetic support only -> reject with `ERR_FINAL_DECISION_REQUESTED`, keep `cannot_substitute` populated with `TAD_final`, `inference_case_closure`, `field_evidence`, `validation_data`, `Validation Data Bridge`, and `Verification Bridge`, and route any decision use to real-evidence review.

FM-033-003_UNRESOLVED_LINEAGE: a support signal, inference case, phase contract, schema version, or version record cannot be resolved through motor_002 lineage -> ranked entries lose rebuildability and audit trail, or `version_record_refs` are empty while scores still appear authoritative -> reject with `ERR_UNRESOLVED_PROVENANCE`, emit no partial register, and require complete `version_records` before rerun.

FM-033-004_INACTIVE_CASE_RANKED: `source_problem_ref` points to a closed, archived, missing, or inactive inference case in motor_013 -> the output allocates attention to cases outside the active case set or reopens a case implicitly -> reject the affected input with `ERR_CASE_NOT_ACTIVE`, exclude the case from ranking, and rebuild only from active cases with stable `inference_case_id` values.

FM-033-005_PHASE_CONTRACT_BYPASS: the applicable motor_001 phase contract does not permit preliminary prioritization, or the ranking basis omits phase constraints -> the register crosses phase authority boundaries and may be consumed where exploratory synthetic support is not allowed -> reject with `ERR_PHASE_CONTRACT_BLOCKS_PRIORITY`, record the blocking phase contract reference, and require a valid phase contract before emission.

FM-033-006_UNCERTAINTY_SUPPRESSION: sparse support, exact ties, weak score separation, out-of-scope signals, or conflicting synthetic signals are collapsed into a clean rank order without `RankUncertaintyRecord` detail -> output overstates certainty and hides the real evidence needed to revise or invalidate the order -> emit only with `status=emitted_with_uncertainty`, populate `tie_groups`, `rank_separation_notes`, `conflicting_signal_notes`, `insufficient_support_case_refs`, and non-empty `requires_real_evidence`; otherwise fail conformance.

FM-033-007_DOMAIN_VALIDITY_MISMATCH: a synthetic support item is used although its `domain_validity_limits` do not cover the case scope -> the preliminary score reflects a synthetic scenario outside the case's declared domain -> exclude the signal, add `domain_validity_mismatch` to `RankingBasis.excluded_signal_reasons`, and rank the case only if another valid support item remains.

FM-033-008_NONDETERMINISTIC_RANKING: the weighting rule, tie break, or priority band assignment depends on mutable iteration order, unstated heuristics, current analyst preference, or random behavior -> repeated runs over unchanged input versions produce rank churn with no lineage explanation -> block emission until `RankingBasis.weighting_rule`, `priority_band_rule`, and `tie_break_rule` are deterministic and recorded with the input version set.

## anti_patterns
- Coupling motor_033 directly to Decision Core state changes, TAD final generation, case closure, or claim validity scoring. This breaks the motor boundary because motor_033 may only emit subordinate preliminary support.
- Treating `priority_signal` or rank position as evidence strength, truth probability, causal proof, or validation outcome. The register is a non-evidentiary ordering signal, not a claim adjudication artifact.
- Accepting synthetic support records without checking `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `source_problem_ref`, `expert_spec_ref`, `intended_use`, `domain_validity_limits`, and `limitations_note`.
- Generating a rank order without a separate `RankingBasis` object and `RankUncertaintyRecord`, or embedding unexplained scoring logic only in implementation code.
- Mutating motor_032 support registers, motor_013 inference case state, motor_001 phase contracts, or motor_002 version records to make ranking easier.
- Silently filling missing support with zero scores, average scores, inferred case relevance, or LLM judgment instead of recording `insufficient_support_case_refs` and real-evidence requirements.
- Hiding exact ties, weak separation, excluded signals, or conflicting scenario signals to produce a cleaner ordered list.
- Merging motor_032 support integration, motor_033 ranking, and downstream decision authority into one monolithic module.
- Reusing stale `version_record_refs` after source support, active case set, phase contracts, ranking rules, or schema version change.
- Emitting generic limitation text that does not name what real evidence would confirm, revise, or invalidate the preliminary order.

## degradation_signals
- Metric `motor_033.rejected_missing_epistemic_flags.count` increases, or any accepted support item lacks `synthetic_support_flag=true`, `non_evidentiary_flag=true`, or `intended_use=preliminary_support`.
- Metric `motor_033.unresolved_provenance.count` rises above zero for support, case, phase contract, schema, or version references.
- Log pattern `ERR_FINAL_DECISION_REQUESTED`, `output_type=TAD_final`, `close_inference_case=true`, or downstream use of `preliminary_priority_register` for case closure appears in request or audit logs.
- Ratio `rank_uncertainty_record.empty / emitted_registers` approaches 1.0 while inputs include sparse support, ties, conflicting signals, or weak rank separation.
- Metric `motor_033.rank_churn_same_input_version.count` is nonzero: the rank order changes across runs with identical `source_ref`, `version_record_refs`, `weighting_rule`, and `phase_contract_refs`.
- `RankingBasis.excluded_signal_reasons` is empty while domain validity mismatches, inactive cases, or missing support are present in validation logs.
- `requires_real_evidence` is empty, duplicated as generic boilerplate across all entries, or omits evidence needed for priority groups affected by uncertainty.
- `ranked_case_count` exceeds active eligible cases, or ranked entries contain closed, archived, missing, or inactive `inference_case_id` values.
- `version_hash` or `parent_id` changes without a corresponding recorded change in source versions, ranking basis, uncertainty record, or schema version.
- Repeated outputs have `status=emitted` despite `RankUncertaintyRecord.uncertainty_level` being `moderate`, `high`, or `blocking`.

## expensive_errors
EP-033-001_EPIS_TAD_PROMOTION: allowing a `preliminary_priority_register` to be interpreted as TAD final, field evidence, validation data, or inference case closure authority. It is expensive because downstream decisions, audit records, and case histories may need to be unwound after synthetic support contaminates the evidentiary chain. Prevention: enforce `non_evidentiary_flag=true`, `rank_is_preliminary=true`, `cannot_substitute`, and rejection of final-decision request metadata before emission.

EP-033-002_LINEAGE_GAP_AFTER_RANKING: emitting ranked cases without complete support, case, phase contract, schema, and version references. It is expensive because the rank order cannot be reconstructed after it influences prioritization, making later audits unable to distinguish valid preliminary ordering from implementation drift. Prevention: require resolvable `version_record_refs`, fail closed with `ERR_UNRESOLVED_PROVENANCE`, and compute `version_hash` from payload plus input version set.

EP-033-003_HIDDEN_UNCERTAINTY: omitting tie groups, weak separation, sparse support, conflicting synthetic signals, or domain exclusions. It is expensive because analysts may spend resources according to false precision, and later correction requires reconstructing the ignored uncertainty from old inputs. Prevention: make `RankUncertaintyRecord` mandatory, require non-empty uncertainty fields when validation detects sparse or conflicting inputs, and set `status=emitted_with_uncertainty` when uncertainty is material.

EP-033-004_SOURCE_MUTATION: rewriting motor_032 support records, motor_013 cases, motor_001 phase contracts, or motor_002 version records during prioritization. It is expensive because the source-of-truth chain loses immutability and downstream rebuilds cannot prove what input produced each rank. Prevention: treat all source inputs as read-only, emit derived motor_033 objects only, and create new versions through `parent_id` rather than editing prior artifacts.

EP-033-005_PHASE_AUTHORITY_LEAK: ranking cases where the phase contract blocks preliminary prioritization or where the current phase forbids synthetic support handoff. It is expensive because the output can cross governance boundaries and later force manual review of every consumer that touched the invalid register. Prevention: validate `allows_preliminary_prioritization=true`, preserve `phase_contract_refs` in every ranked entry, and reject with `ERR_PHASE_CONTRACT_BLOCKS_PRIORITY` when authority is absent.

EP-033-006_NONDEREPRODUCIBLE_ORDER: using unstated heuristics, mutable ordering, random tie breaks, or LLM preference to assign rank positions. It is expensive because unchanged source inputs can produce different priorities, making the audit trail and resource allocation history unreliable. Prevention: record deterministic `weighting_rule`, `priority_band_rule`, and `tie_break_rule` in `RankingBasis`, and test repeated runs over identical version references for identical output.
