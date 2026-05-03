# Failure Modes Spec — Synthetic Data Generation Engine

Motor ID: motor_030

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Generar datasets sintéticos condicionados por expert_problem_spec aprobado.
why_it_exists:  El framework necesita datos para ML exploratoria sin comprometer la separación entre evidencia real y soporte sintético.
key_inputs:     expert_problem_spec (motor_029), version_records (motor_002)
key_outputs:    synthetic_generation_run, synthetic_dataset, generation_manifest
key_objects:    SyntheticGenerationRun, SyntheticDataset, GenerationManifest
what_not_to_do: No puede citarse como evidencia de campo. No sustituye Validation Data Bridge.
design_notes:   Todo output lleva synthetic_data_flag=true y non_evidentiary_flag=true. No puede ejecutarse sobre specs en draft o con ambiguity_register crítico.
epistemic_flags: synthetic_data_flag=true, non_evidentiary_flag=true

All placeholder sections in this failure modes spec have been resolved with concrete technical content.
-->

## failure_modes_list
- `SPEC_STATUS_BYPASS`: `expert_problem_spec.status` is not `approved`, `handoff_allowed` is false, or the expert review evidence is missing, but generation is attempted -> observable symptom: `SyntheticGenerationRun` reaches `generated` state from an ineligible spec, or a dataset exists for a draft spec -> recovery path: reject before record generation with `rejection_code="SPEC_NOT_APPROVED"`, emit no usable `SyntheticDataset`, preserve `expert_spec_ref` and `source_problem_ref` in the rejection record, and require motor_029 to approve the spec before retry.
- `CRITICAL_AMBIGUITY_LEAK`: `expert_problem_spec.ambiguity_register` contains an unresolved item with `impact_if_unresolved="critical"` and that ambiguity is allowed into `parameter_set` or constraints -> observable symptom: generated records reflect contradictory ranges, missing domains, or scenario rules not traceable to the approved spec -> recovery path: reject with `rejection_code="CRITICAL_AMBIGUITY_UNRESOLVED"`, do not infer missing parameters, and send the spec back to motor_029 for explicit resolution.
- `GENERATOR_VERSION_UNRESOLVED`: `version_records` does not resolve a current semver `generator_version` for the synthetic generator -> observable symptom: outputs contain empty, ad hoc, timestamp-derived, or locally invented generator versions -> recovery path: reject with `rejection_code="GENERATOR_VERSION_UNRESOLVED"` and require a valid motor_002 version record before any dataset can be emitted.
- `EPISTEMIC_FLAG_MISSING`: any candidate `SyntheticGenerationRun`, `SyntheticDataset`, or `GenerationManifest` lacks `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `intended_use="exploration"`, `domain_validity_limits`, or `limitations_note` -> observable symptom: downstream consumers cannot mechanically distinguish synthetic data from evidentiary data -> recovery path: block registration, treat the candidate output as invalid rather than warning-only, and regenerate only after the complete required flags and limitation text are attached.
- `NON_REPRODUCIBLE_RUN`: the same `expert_spec_ref`, `source_problem_ref`, `version_record_refs`, `generator_version`, `parameter_set`, and `generation_seed` produce different IDs, hashes, records, or reproducibility fingerprints -> observable symptom: repeated runs disagree on `run_id`, `dataset_id`, `dataset_hash`, `manifest_id`, or normalized records while material inputs are unchanged -> recovery path: fail the quality check, mark the run rejected or non-emittable, inspect seed handling and hash canonicalization, and rerun only after deterministic normalization is restored.
- `CONSTRAINT_DRIFT`: generated records violate types, ranges, categories, cardinalities, scenario rules, or partition rules declared in the approved spec -> observable symptom: `quality_checks` report out-of-range values, category values outside the allowed set, record counts that do not match `parameter_set.sample_size`, or datasets covered by the wrong manifest -> recovery path: block the dataset, record the failed constraint in `quality_checks`, and regenerate from the same approved constraints after correcting generator logic.
- `LINEAGE_BREAK`: outputs for one run do not share the same `run_id`, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `version_record_refs`, or `parameter_set` -> observable symptom: a `GenerationManifest` documents one dataset while `SyntheticDataset.manifest_id` or `SyntheticDataset.run_id` points elsewhere -> recovery path: reject the inconsistent output set, do not patch references silently, and rebuild all three outputs as one atomic emission.
- `EVIDENTIARY_PROMOTION_LEAK`: a synthetic run, dataset, or manifest is labeled or routed as `validation_data`, `field_evidence`, Verification Bridge input, or Decision Core closure evidence -> observable symptom: `forbidden_uses` is missing or downstream logs show synthetic outputs used as primary support for a claim -> recovery path: quarantine the handoff, restore `non_evidentiary_flag=true` and explicit forbidden uses, invalidate the downstream consumption event, and require real evidence through motor_018 or motor_019 for validation.

## anti_patterns
- Generating synthetic records from a draft, partially reviewed, or critically ambiguous expert spec in order to keep the pipeline moving.
- Filling missing parameter domains, ranges, category sets, scenario definitions, or sample sizes from operator intuition, prompt output, defaults, or narrative convenience.
- Treating `synthetic_dataset` as evidence that a real-world phenomenon exists, is predictable, or is ready for decision-grade use.
- Combining generation with ML training, model selection, metric interpretation, feature ranking, or `capability_demonstration_report` production; those responsibilities belong downstream to motor_031 and later motors.
- Rewriting `expert_spec_ref`, `source_problem_ref`, `version_record_refs`, or `generator_version` into local aliases that break rebuild and lineage.
- Mutating an emitted dataset, manifest, flags, or parameter set in place instead of creating a governed new version with `parent_id`.
- Allowing output registration when `synthetic_data_flag`, `non_evidentiary_flag`, `intended_use`, `domain_validity_limits`, or `limitations_note` is absent or downgraded to optional metadata.
- Storing generated rows without the schema, quality checks, manifest reference, reproducibility fingerprint, and forbidden-use limitations needed to audit the run.
- Optimizing for larger or more realistic-looking datasets while bypassing deterministic reproducibility, constraint checks, or epistemic labeling.
- Coupling this motor directly to Validation Data Bridge, Verification Bridge, Decision Core closure, or TAD finalization paths as if synthetic data could substitute for field evidence.

## degradation_signals
- Rising count or rate of `SPEC_NOT_APPROVED`, `CRITICAL_AMBIGUITY_UNRESOLVED`, `GENERATOR_VERSION_UNRESOLVED`, or `INVALID_PARAMETER_CONSTRAINT` rejections by source problem; indicates upstream specs or version records are no longer precise enough for deterministic generation.
- Any successful run where `SyntheticGenerationRun`, `SyntheticDataset`, and `GenerationManifest` disagree on `run_id`, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `version_record_refs`, or `parameter_set`.
- `quality_checks.constraint_violations` greater than zero after generation, especially repeated violations of the same variable domain, category set, scenario rule, or record count.
- Repeated runs with identical material inputs and `generation_seed` producing different `dataset_hash`, `version_hash`, `reproducibility_fingerprint`, row order, or normalized record payload.
- Missing or empty `constraints_applied`, `forbidden_uses`, `domain_validity_limits`, or `limitations_note` in `GenerationManifest`.
- Nonzero count of output candidates blocked for missing `synthetic_data_flag=true`, `non_evidentiary_flag=true`, or `intended_use="exploration"`.
- Datasets whose `record_count` differs from actual rows or partition totals, or manifests whose `dataset_refs` include datasets from more than one `run_id`.
- Logs showing silent coercion of parameter types, such as string sample sizes converted to integers, missing numeric ranges replaced by defaults, or unseen categories accepted.
- Downstream events where synthetic outputs are consumed by Validation Data Bridge, Verification Bridge, final TAD assembly, or Decision Core as primary evidence rather than exploratory support.
- Increasing manual overrides, force runs, or local generator configuration changes that are not represented in `version_records` or `parameter_set`.

## expensive_errors
- Emitting a dataset from an unapproved or critically ambiguous spec. It is expensive because downstream experiments may be trained and interpreted against an invalid problem contract, requiring invalidation of datasets, manifests, training runs, and any support registers derived from them. Prevention: hard preflight checks for `status="approved"`, `handoff_allowed=true`, approved review evidence, and no unresolved critical ambiguity before any rows are generated.
- Registering outputs without complete epistemic flags and limitation text. It is expensive because the objects can be mistaken for real evidence, contaminating evidence hierarchy, reports, and decision records. Prevention: make `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `intended_use="exploration"`, `domain_validity_limits`, `limitations_note`, and `forbidden_uses` mandatory registration gates, not post-processing annotations.
- Losing deterministic reproducibility for a run. It is expensive because the framework can no longer rebuild, audit, compare, or explain downstream model behavior from the same spec and parameter set. Prevention: canonicalize input ordering, freeze `parameter_set`, require `generation_seed`, include version records in hashes, and test repeated execution for stable IDs and hashes.
- Allowing constraint drift into emitted records. It is expensive because bad synthetic rows can silently alter ML capability demonstrations and create false confidence in patterns that the approved spec never allowed. Prevention: validate every generated value against declared types, ranges, categories, scenario rules, and record counts before emitting the dataset.
- Breaking lineage between run, dataset, and manifest. It is expensive because conformance review, rebuild, stale detection, and downstream attribution cannot determine which generator, spec, parameters, or version records produced the data. Prevention: emit `SyntheticGenerationRun`, `SyntheticDataset`, and `GenerationManifest` atomically with identical core references and reject any cross-reference mismatch.
- Promoting synthetic data into evidentiary workflows. It is expensive because it undermines the constitutional separation between synthetic support and real validation, and correcting it may require retracting claims or reports. Prevention: include explicit `forbidden_uses`, block routes to motor_018 and motor_019, and require downstream consumers to reject objects where `non_evidentiary_flag=true`.
- Mutating an emitted dataset or manifest in place. It is expensive because historical comparisons, hashes, and model reproducibility become unreliable while stale downstream objects may appear current. Prevention: enforce immutable payloads, create new versions for material changes, preserve `parent_id`, and never update records or flags silently.
- Inventing a generator version when motor_002 cannot resolve one. It is expensive because audit and rebuild cannot identify the generator behavior that produced the dataset. Prevention: fail fast with `GENERATOR_VERSION_UNRESOLVED` and require a current `version_record_refs` entry before generation.
