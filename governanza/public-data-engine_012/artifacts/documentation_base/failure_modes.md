# Failure Modes — Public Data Engine

Motor ID: motor_012

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Materializar Fase 1 y producir facility_prior y bundles contextuales listos para Fase 2.
why_it_exists:  Convierte infraestructura base en output útil de Fase 1.
key_inputs:     library_objects (motor_011), source_registry (motor_008), quality_records (motor_007)
key_outputs:    facility_prior, contextual_bundle, phase1_package
key_objects:    FacilityPrior, ContextualBundle, Phase1Package
what_not_to_do: No hace inferencias. No produce TADs. Solo empaqueta el prior de Fase 1.
design_notes:   Materialización final de Fase 1. Depende de toda la infraestructura base.

All placeholder markers have been replaced with concrete content.
-->

## failure_modes_list
- `UNRESOLVED_REFERENCE_CHAIN`: emitted bundle or prior contains a library, source, or quality reference that cannot be resolved in the input snapshots.
- `PROVENANCE_LOSS`: output can no longer reconstruct which upstream objects, source registry snapshot, and quality records produced the package.
- `SCOPE_CREEP_TO_INFERENCE`: package includes conclusions, TAD-like statements, decision grades, or activation decisions instead of remaining a Fase 1 prior.
- `SILENT_ELIGIBILITY_OVERRIDE`: ineligible or low-fitness upstream records appear in output without an explicit rejection, exclusion, or upstream status change.
- `NONDETERMINISTIC_PACKAGING`: identical input snapshots produce different bundle membership, identifiers, or package references across runs.

## anti_patterns
- Using this motor as a cleanup layer for incomplete upstream records instead of rejecting missing provenance, unresolved sources, or absent quality references.
- Treating `facility_prior` as an analytical conclusion rather than as a deterministic package of curated Fase 1 material.
- Adding ad hoc scoring, ranking, or recommendation logic to compensate for sparse inputs.
- Allowing downstream motors to depend on undocumented local fields that are not declared in the package contract.

## degradation_signals
- Rising count of exclusions or rejections caused by `UNRESOLVED_SOURCE_REF`, `MISSING_PROVENANCE`, or `QUALITY_RECORD_TARGET_UNKNOWN`.
- Output packages with declining ratio of records carrying complete source, quality, version, and lineage references.
- Bundles whose membership changes across runs despite identical input snapshot identifiers and package configuration.
- Presence of decision language such as `conclusion`, `recommendation`, `TAD`, `inference`, or `decision_grade` in output fields.
- Increase in package fields with null provenance, null quality references, or local identifiers that do not map to upstream IDs.
