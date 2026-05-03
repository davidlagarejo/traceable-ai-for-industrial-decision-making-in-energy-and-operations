# Failure Modes Spec — Validation Data Bridge

Motor ID: motor_018

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Conectar datos estructurados del framework con evidencia local, medición y datos de sitio.
why_it_exists:  La verificación necesita anclarse al sistema completo de Fase 1.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    validation_data_set, bridge_manifest, evidentiary_record
key_objects:    ValidationDataSet, BridgeRecord, EvidentiaryLink
what_not_to_do: No puede ser sustituido por datos sintéticos. No produce field_evidence. Solo estructura datos reales para validación.
design_notes:   Produce evidencia de nivel validation_data (no synthetic_support). Requiere pipeline completo de Fase 1.

All failure-mode sections below are filled with concrete gate-ready content.
-->

## failure_modes_list
- UNREGISTERED_SOURCE_LEAK: a candidate normalized record references a `source_id` absent from the SourceRegistrySnapshot or tied to a missing `rights_profile_id` -> `BridgeRecord` is created without enforceable source authority and the `BridgeManifest.source_ids` cannot be reconciled to motor_008 -> quarantine the candidate, emit `SOURCE_NOT_REGISTERED`, rebuild the dataset from a current source registry snapshot, and verify that every included and excluded candidate has a registered source reference.
- RIGHTS_PROFILE_BYPASS: a source exists but `validation_use=false`, the destination policy conflicts with restrictions, or `restriction_refs` are dropped during bridge construction -> records become eligible despite source rights forbidding the declared validation use or redistribution path -> exclude affected candidates with `RIGHTS_PROFILE_DENIES_VALIDATION` or `RIGHTS_RESTRICTION_CONFLICT`, propagate the original restrictions into the manifest, and rerun after motor_008 rights metadata is corrected upstream.
- LINEAGE_BREAK: candidate data lacks `ingestion_record_id`, `raw_record_ref`, ingestion lineage, `normalized_record_id`, original value reference, canonical value reference, normalization rule reference, or `quality_record_id` -> reviewers cannot reconstruct the path from validation_data back to raw source, normalization trace and quality assessment -> reject the candidate with the specific missing-lineage code, include it in `BridgeManifest.exclusion_reasons`, and require upstream motors 004, 005 or 007 to re-emit complete records.
- SYNTHETIC_CONTAMINATION: any input candidate, upstream artifact, support register or replacement value carries `synthetic_data_flag=true`, `synthetic_support_flag=true`, `source_type=synthetic`, or equivalent synthetic provenance -> the output appears to be real `validation_data` while being backed by non-evidentiary synthetic support -> reject the affected lot with `SYNTHETIC_INPUT_NOT_ALLOWED`, do not emit substitute records, and preserve the rejection in the manifest audit trail.
- QUALITY_OVERRIDE: a candidate with `quality_record.disqualification_reason` is emitted as `eligible` or a low-fitness candidate is included without the declared warning or exclusion policy -> downstream consumers receive data that motor_007 already marked unfit or degraded -> exclude disqualified candidates with `QUALITY_DISQUALIFIED`, preserve low-fitness warnings or exclusions according to the dataset policy, and rebuild summaries from quality records without recalculating score.
- IDENTITY_AMBIGUITY_COLLAPSE: an `identity_record` with `ambiguity_flag=true` is converted to a resolved identity state, or `identity_record_id` is omitted while still claiming resolved identity -> unresolved entity ambiguity is hidden from Verification Bridge and later claims can attach to the wrong entity -> set `identity_ambiguity_flag=true`, emit `validation_status=eligible_with_warning`, add `identity_ambiguous` to warning codes, and never mutate or force a motor_006 identity resolution.
- MANIFEST_DATASET_DIVERGENCE: `ValidationDataSet.bridge_record_ids` and `BridgeManifest.included_record_ids` differ, excluded candidates are missing from `excluded_record_refs`, or exclusion counts do not match reasons -> the bridge output cannot be rebuilt or audited from its manifest -> stop publication, regenerate the manifest from the same candidate classification table, and compare included ids, excluded refs, warning reasons, restriction refs and rebuild inputs before release.
- EVIDENCE_LEVEL_ESCALATION: output objects declare `field_evidence`, `decision_grade`, `synthetic_support`, or any evidence level other than `validation_data` -> motor_018 exceeds its authority and downstream systems may treat bridged data as verified field evidence -> fail schema validation, reset all emitted objects to the fixed `validation_data` enum only through a new materialization, and route field verification decisions to the Verification Bridge.
- VERSION_MUTATION: content changes in source snapshot, candidate ids, warnings, exclusions, restrictions or lineage refs while existing ids or `version_hash` values are reused -> historical bridge outputs become non-reconstructible and comparisons across runs are corrupted -> emit new ids and hashes derived from canonicalized content, preserve `parent_id` to the prior version, and reject in-place edits of persisted objects.
- RIGHTS_RESTRICTION_LOSS: license, access, redistribution, destination policy or internal-use limits exist upstream but are absent from one or more of `ValidationDataSet`, `BridgeRecord`, `EvidentiaryLink`, `BridgeManifest` or `EvidentiaryRecord` -> downstream handoffs can accidentally over-distribute or over-cite restricted data -> halt handoff emission, copy restriction refs from motor_008 into every affected entity, and re-run manifest consistency checks.

## anti_patterns
- Treating the bridge as a second ingestion, parsing, normalization, identity resolution or quality scoring engine. Motor_018 may copy and cross-reference upstream results, but it must not recalculate or repair them.
- Filling gaps with synthetic data, synthetic model outputs, manually invented values or `synthetic_support` objects so the validation dataset appears more complete.
- Coupling directly to mutable upstream storage without a source registry snapshot, stable upstream ids, version hashes or explicit rebuild inputs.
- Emitting a `ValidationDataSet` without a `BridgeManifest` that exactly reconstructs included records, excluded records, warning reasons, restrictions and source snapshot.
- Treating source rights as advisory metadata after ingestion instead of hard eligibility constraints from motor_008.
- Collapsing identity ambiguity into a resolved state because a downstream consumer wants a single entity id.
- Hiding exclusions, warnings or restrictions to improve apparent coverage, quality, or usability of the validation dataset.
- Promoting `validation_data` to `field_evidence`, claim closure, verification decision, ranking or truth assertion inside this motor.
- Mutating upstream `raw_record`, `parsed_record`, `normalized_record`, `identity_record`, `quality_record` or `rights_profile` objects from bridge code.
- Reusing persisted object ids after content changes instead of creating a new deterministic version and parent link.

## degradation_signals
- `source_registry_miss_rate` above zero: any candidate references a `source_id` that is not present in the selected SourceRegistrySnapshot.
- `rights_denial_rate` or `rights_restriction_conflict_rate` rises sharply compared with recent runs for the same validation scope.
- `lineage_completeness_ratio` drops below 1.0 for required links to source rights, ingestion lineage, normalization trace and quality assessment.
- `synthetic_input_rejection_count` above zero, or logs containing `SYNTHETIC_INPUT_NOT_ALLOWED`.
- `manifest_dataset_diff_count` above zero when comparing `ValidationDataSet.bridge_record_ids` with `BridgeManifest.included_record_ids`.
- `undocumented_exclusion_count` above zero: any excluded candidate lacks an explicit reason in `BridgeManifest.exclusion_reasons`.
- `restriction_propagation_miss_count` above zero across dataset, bridge records, links, manifest or evidentiary record.
- `eligible_with_ambiguity_without_warning_count` above zero: identity ambiguity exists but warning code `identity_ambiguous` is missing.
- `quality_override_count` above zero: records with `disqualification_reason` appear as eligible, or low-fitness records lack the declared warning or exclusion behavior.
- `evidence_level_violation_count` above zero: any emitted entity has evidence level other than `validation_data`.
- `version_hash_instability_count` above zero: repeated runs with identical canonical inputs produce different hashes, or changed inputs keep old hashes.
- Log patterns such as `SOURCE_NOT_REGISTERED`, `MISSING_INGESTION_LINEAGE`, `MISSING_NORMALIZATION_TRACE`, `MISSING_QUALITY_RECORD`, `RIGHTS_PROFILE_DENIES_VALIDATION`, `RIGHTS_RESTRICTION_CONFLICT`, `QUALITY_DISQUALIFIED`, `MANIFEST_MISMATCH`, or `EVIDENCE_LEVEL_INVALID`.

## expensive_errors
- Silent rights relaxation. Expensive because restricted source data can propagate into reports, verification paths or external handoffs before anyone notices the license or access violation. Prevent by treating motor_008 rights profiles and destination policy checks as hard gates, preserving `restriction_refs` on every output entity, and failing any run with a restriction propagation miss.
- Broken lineage accepted as valid. Expensive because downstream verification cannot later prove which raw, normalized or quality artifact supported a record, forcing manual forensic reconstruction or full dataset rebuild. Prevent by rejecting candidates missing source rights, ingestion lineage, normalization trace or quality assessment links before creating eligible `BridgeRecord` objects.
- Synthetic contamination in validation_data. Expensive because once synthetic support is labeled as real validation data, claims, reports and verification agendas can be contaminated epistemically and must be audited across all consumers. Prevent by scanning all inputs for synthetic provenance flags and rejecting the affected lot with a manifest entry instead of substituting data.
- Identity ambiguity hidden. Expensive because downstream claims can attach to the wrong facility, asset, site or entity, and later correction requires claim-by-claim impact review. Prevent by preserving `identity_ambiguity_flag`, emitting `eligible_with_warning`, adding `identity_ambiguous`, and never resolving identity inside motor_018.
- Quality disqualification overridden. Expensive because unfit records enter validation workflows and may trigger false confidence or unnecessary field work. Prevent by copying `disqualification_reason` from motor_007, excluding disqualified candidates, and recording the exclusion in both summary counts and candidate-level reasons.
- Manifest and dataset divergence. Expensive because the dataset can no longer be rebuilt, audited or compared across runs, undermining conformance review and propagation logic. Prevent by generating both objects from the same deterministic classification table and verifying exact equality between included ids and complete coverage of exclusions.
- Evidence-level escalation. Expensive because consumers may treat structured validation data as direct field evidence or final truth, crossing a phase boundary that this motor is not authorized to cross. Prevent with enum validation that permits only `validation_data` for emitted entities and with `limits_of_use` stating that the output cannot close claims alone.
- In-place version mutation. Expensive because historical outputs become unrecoverable, rebuild hashes lose meaning and downstream impact analysis cannot identify which consumers saw which version. Prevent by computing deterministic `version_hash` values from canonical content, issuing new ids on material change, and preserving `parent_id` links.
- Opaque exclusion cleanup. Expensive because removing inconvenient or low-quality candidates without explicit reasons inflates apparent coverage and hides structural data gaps. Prevent by requiring every excluded candidate to appear in `BridgeManifest.excluded_record_refs` with an explicit reason and by failing `undocumented_exclusion_count > 0`.
