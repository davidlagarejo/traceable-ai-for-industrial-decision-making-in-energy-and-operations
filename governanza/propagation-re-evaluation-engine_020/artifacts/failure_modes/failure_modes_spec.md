# Failure Modes Spec — Propagation / Re-evaluation Engine

Motor ID: motor_020

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Re-evaluar objetos downstream cuando cambian fuentes, reglas, taxonomías, contratos o bibliotecas.
why_it_exists:  Versioning registra cambios, pero este motor decide qué debe re-evaluarse.
key_inputs:     version_records (motor_002), quality_records (motor_007), change_events (motor_009)
key_outputs:    re_evaluation_job, stale_set, propagation_log
key_objects:    ReEvaluationJob, StaleObject, PropagationRecord
what_not_to_do: No modifica objetos directamente. Encola y señaliza para re-evaluación.
design_notes:   Corre en respuesta a cambios detectados. Crea cadenas de re-evaluación.

Failure-modes-stage content is completed for Gate 4 review.
-->

## failure_modes_list
- INVALID_TRIGGER_ACCEPTANCE: `version_records`, `quality_records` or `change_events` arrive without stable primary identifiers, parseable timestamps, or evidence/lineage references -> observable symptom: `PropagationRecord` entries contain empty `input_refs`, missing `trigger_ref`, or jobs appear without reconstructible cause -> recovery path: reject the item or batch with `INVALID_PROPAGATION_INPUT`, preserve the rejected identifier in `rejected_input_refs`, and emit no active `ReEvaluationJob` or `StaleObject` for that trigger.
- UNTRACEABLE_PATH_PROPAGATION: a trigger is valid but an affected candidate cannot be connected through `lineage_refs`, `impact_set`, `subject_ref`, `source_id`, or declared dependency edge -> observable symptom: downstream objects are marked stale with empty `dependency_path`, invented lineage, or no `UNTRACEABLE_PROPAGATION_PATH` record -> recovery path: block only the untraceable branch, register `blocked_untraceable` in `PropagationRecord.decision` or `secondary_decisions`, keep the candidate out of active jobs, and continue with traceable branches.
- OVER_PROPAGATION_STORM: impact resolution ignores dependency boundaries, severity filtering, or deduplication keys -> observable symptom: a small source, contract, taxonomy, or library change emits jobs for objects outside the declared `impact_set` and the ratio of jobs per trigger rises sharply -> recovery path: constrain targets to declared dependency paths, deduplicate by `trigger_ref`, `target_object_ref`, `target_version_ref`, and `propagation_rule_version`, and record suppressed duplicates in `secondary_decisions`.
- UNDER_PROPAGATION_MISS: valid `impact_set`, `quality_records.subject_ref`, or lineage references are not evaluated when computing affected objects -> observable symptom: critical triggers produce `decision = no_affected_objects` while affected downstream objects remain absent from `stale_set` and `emitted_job_ids` -> recovery path: replay the trigger against the accepted inputs, recompute affected objects from version, quality, and change references, and emit missing stale markers/jobs with the original trigger evidence preserved.
- UNSAFE_JOB_EMISSION: a candidate job lacks `target_object_ref`, `reason_code`, `priority`, `dependency_path`, `evidence_refs`, or `propagation_record_id` -> observable symptom: queue consumers receive non-actionable `ReEvaluationJob` records or cannot link a job back to its audit decision -> recovery path: prevent queue emission, record `UNSAFE_REEVALUATION_JOB`, and keep the candidate in the propagation log as blocked or rejected until required fields are present.
- SILENT_DOWNSTREAM_MUTATION: implementation attempts to update downstream objects, quality scores, source records, versions, contracts, or taxonomy state while handling propagation -> observable symptom: upstream or downstream records change without a corresponding owner-motor action and `propagation_log` no longer explains the mutation -> recovery path: stop processing, discard side-effecting writes, restore inputs from authoritative sources, and restrict motor_020 outputs to `ReEvaluationJob`, `StaleObject`, and `PropagationRecord`.
- CHAIN_EXPANSION_WITHOUT_AUDIT: chained re-evaluation decisions are created without `parent_id`, `rule_version`, or complete `PropagationRecord` coverage -> observable symptom: stale chains cannot be reconstructed across triggers and repeated runs produce different job graphs for the same inputs -> recovery path: require every chained output to reference the parent propagation record or prior job, use deterministic identifiers, and reject chain steps that cannot be logged.

## anti_patterns
- Coupling job emission directly to downstream motor internals instead of producing queueable `ReEvaluationJob` records with explicit target, trigger, priority, and evidence.
- Treating `change_events` from motor_009 as direct orders to refresh, recapture, rebuild, or modify data rather than as triggers that require deterministic impact evaluation.
- Deriving affected objects from text similarity, filename conventions, or free-form descriptions instead of stable references such as lineage, impact, source, subject, or dependency edges.
- Suppressing `PropagationRecord` details to keep logs small; this breaks auditability because rejected inputs, dependency paths, deduplication, and rule version disappear.
- Allowing a single propagation routine to also perform quality scoring, version creation, contract repair, taxonomy updates, or downstream rebuild completion.
- Retrying untraceable candidates by inventing a dependency path or copying a neighboring object's lineage.
- Disabling deduplication because duplicate jobs are assumed to be harmless; duplicates become competing operational truth about the same trigger and target.
- Updating `StaleObject` or `ReEvaluationJob` identifiers with random values on each run, which prevents deterministic replay and comparison.

## degradation_signals
- `blocked_untraceable` share rises for triggers whose inputs contain non-empty `lineage_refs`, `impact_set`, or `subject_ref`.
- Job count per trigger exceeds the size of the declared affected set without corresponding `secondary_decisions` explaining chained propagation.
- Repeated `decision = no_affected_objects` appears for `critical` change events while related version records declare an `impact_set`.
- Deduplication suppressions increase for the same logical key: `trigger_ref`, `target_object_ref`, `target_version_ref`, `propagation_rule_version`.
- Any `PropagationRecord` is emitted without `input_refs`, `trigger_ref`, `affected_object_refs`, `decision`, `rule_version`, `evaluated_at`, or `produced_by_motor = motor_020`.
- Difference between `stale_object_ids` and `emitted_job_ids` grows without explicit `blocked_untraceable`, `rejected_invalid_input`, or `deduplicated` decisions.
- Latency between trigger timestamp (`created_at`, `evaluated_at`, or `detected_at`) and job `created_at` grows beyond the operational threshold for high or urgent priorities.
- Queue consumers report jobs without matching `PropagationRecord`, or stale markers appear without matching `trigger_ref` and `stale_reason`.
- Re-running the same accepted inputs with the same rule version produces different identifiers, priorities, or target sets.

## expensive_errors
- Emitting jobs without reconstructible evidence: expensive because downstream motors may spend work on targets that cannot be justified or reversed cleanly; prevented by requiring `evidence_refs`, `input_refs`, `dependency_path`, and `propagation_record_id` before queue emission.
- Marking too many objects stale from an over-broad trigger: expensive because it creates unnecessary re-evaluation cascades, operator noise, and stale-state distrust; prevented by constraining propagation to declared lineage, impact, source, subject, and dependency references plus deterministic deduplication.
- Missing a real affected object: expensive because consumers may continue using an object whose upstream source, contract, taxonomy, library, version, or quality basis changed; prevented by evaluating all three input families and testing `impact_set`, `quality_records.subject_ref`, and `change_events.lineage_refs` together.
- Mutating downstream objects from this motor: expensive because ownership, version history, and quality authority become ambiguous after the side effect propagates; prevented by treating motor_020 as signal-only and failing any implementation path that writes outside `ReEvaluationJob`, `StaleObject`, and `PropagationRecord` outputs.
- Losing rejected-input detail during validation: expensive because later rebuild or conformance review cannot distinguish invalid input from no affected objects; prevented by preserving `rejected_input_refs`, structured `error_code`, and the evaluated trigger in every rejection record.
- Generating nondeterministic identifiers: expensive because duplicate suppression, replay, and audit comparison fail across runs; prevented by deriving IDs from canonical trigger, target, version, and rule-version fields.
- Advancing chained propagation without parent linkage: expensive because multi-step stale chains become impossible to audit and cannot be selectively replayed; prevented by requiring `parent_id`, `rule_version`, and complete `PropagationRecord` coverage for each chain step.
