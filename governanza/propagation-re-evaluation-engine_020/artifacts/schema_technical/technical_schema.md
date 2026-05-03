# Technical Schema — Propagation / Re-evaluation Engine

Motor ID: motor_020

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Re-evaluar objetos downstream cuando cambian fuentes, reglas, taxonomías, contratos o bibliotecas.
why_it_exists:  Versioning registra cambios, pero este motor decide qué debe re-evaluarse.
key_inputs:     version_records (motor_002), quality_records (motor_007), change_events (motor_009)
key_outputs:    re_evaluation_job, stale_set, propagation_log
key_objects:    ReEvaluationJob, StaleObject, PropagationRecord
what_not_to_do: No modifica objetos directamente. Encola y señaliza para re-evaluación.
design_notes:   Corre en respuesta a cambios detectados. Crea cadenas de re-evaluación.

Schema content is completed for Gate 2 review.
-->

## entities
- `ReEvaluationJob`: technical object emitted by the schema_technical and implementation stages to request downstream re-evaluation of one affected object. It is a queueable signal only; it does not modify, rebuild, score, or validate the target object.
- `StaleObject`: technical object emitted by the schema_technical and implementation stages to mark one object or object version as not safe to consume as current until the owning downstream motor performs its own re-evaluation.
- `PropagationRecord`: technical audit object emitted by the schema_technical and implementation stages to record accepted inputs, dependency paths, stale markings, emitted jobs, deduplication, and structured rejections for one propagation decision.
- `stale_set`: materialized collection of `StaleObject` records for a run or trigger. It is an output envelope, not a separate authority object; when persisted, it is referenced by `PropagationRecord.stale_set_ref`.

## fields
`ReEvaluationJob`
- `job_id`: string (required) -- stable identifier for the queued re-evaluation request.
- `target_object_ref`: string (required) -- stable reference to the downstream object that requires re-evaluation.
- `target_version_ref`: string|null (required) -- target version affected by the trigger when versioned; null when the target has no explicit version in the available inputs.
- `trigger_ref`: string (required) -- stable reference to the `VersionRecord`, `QualityRecord`, or `ChangeEvent` that caused the job.
- `trigger_type`: enum string (required) -- one of `version_record`, `quality_record`, `change_event`.
- `reason_code`: enum string (required) -- one of `version_change`, `quality_change`, `source_change`, `contract_change`, `taxonomy_change`, `library_change`.
- `priority`: enum string (required) -- one of `low`, `medium`, `high`, `urgent`; derived from severity, quality status, mutation type, and dependency depth.
- `dependency_path`: list[string] (required) -- ordered lineage, impact, source, or subject references connecting the trigger to the target object.
- `input_refs`: list[string] (required) -- accepted input identifiers used to justify this job.
- `evidence_refs`: list[string] (required) -- provenance, evidence, lineage, impact, or subject references sufficient to reconstruct the decision.
- `propagation_record_id`: string (required) -- reference to the `PropagationRecord` that authorized the job.
- `stale_object_id`: string|null (required) -- reference to the related `StaleObject` when a stale marker was produced; null only when the job is blocked or rejected before stale marking.
- `status`: enum string (required) -- one of `queued`, `blocked`, `rejected`.
- `blocking_reason`: string|null (required) -- structured explanation when `status` is `blocked` or `rejected`; null for queued jobs.
- `propagation_rule_version`: string (required) -- version of the deterministic propagation and deduplication rules used for this job.
- `version_id`: string (required) -- version identifier for this job record.
- `created_at`: datetime string (required) -- timestamp when the job record was created.
- `updated_at`: datetime string (required) -- timestamp of the last state-preserving update to this job record.
- `version_hash`: string (required) -- deterministic hash of the canonical serialized job fields.
- `source_ref`: string (required) -- primary upstream input reference that caused this job.
- `produced_by_motor`: string (required) -- constant value `motor_020`.
- `produced_at`: datetime string (required) -- timestamp when motor_020 produced this output object.
- `parent_id`: string|null (required) -- parent propagation record or prior job in a re-evaluation chain; null for a root job.

`StaleObject`
- `stale_object_id`: string (required) -- stable identifier for the stale marker.
- `object_ref`: string (required) -- stable reference to the downstream object that is stale.
- `version_ref`: string|null (required) -- affected object version when available; null when the input only identifies the object.
- `stale_reason`: enum string (required) -- one of `upstream_version_changed`, `quality_degraded`, `source_changed`, `contract_changed`, `taxonomy_changed`, `library_changed`.
- `trigger_ref`: string (required) -- stable reference to the trigger that made the object stale.
- `trigger_type`: enum string (required) -- one of `version_record`, `quality_record`, `change_event`.
- `lineage_refs`: list[string] (required) -- lineage, impact, source, or subject references used to connect the trigger to the stale object.
- `dependency_path`: list[string] (required) -- ordered path from trigger to stale object.
- `severity`: enum string (required) -- one of `info`, `warning`, `critical`.
- `detected_at`: datetime string (required) -- trigger detection or evaluation timestamp used for stale marking.
- `propagation_record_id`: string (required) -- reference to the `PropagationRecord` that created the stale marker.
- `job_id`: string|null (required) -- queued job created from this stale marker; null when no job is emitted because the branch is blocked, rejected, or not eligible.
- `version_id`: string (required) -- version identifier for this stale marker record.
- `created_at`: datetime string (required) -- timestamp when the stale marker was created.
- `updated_at`: datetime string (required) -- timestamp of the last state-preserving update to this stale marker.
- `version_hash`: string (required) -- deterministic hash of the canonical serialized stale marker fields.
- `source_ref`: string (required) -- primary upstream input reference that caused stale marking.
- `produced_by_motor`: string (required) -- constant value `motor_020`.
- `produced_at`: datetime string (required) -- timestamp when motor_020 produced this output object.
- `parent_id`: string|null (required) -- parent propagation record or upstream stale marker in a propagation chain; null for a root stale marker.

`PropagationRecord`
- `propagation_record_id`: string (required) -- stable identifier for the propagation audit record.
- `input_refs`: list[string] (required) -- identifiers of accepted `version_records`, `quality_records`, and `change_events` considered by this decision.
- `trigger_ref`: string (required) -- primary trigger used for the propagation decision.
- `trigger_type`: enum string (required) -- one of `version_record`, `quality_record`, `change_event`.
- `affected_object_refs`: list[string] (required) -- downstream objects found through lineage, impact, source, or subject references.
- `emitted_job_ids`: list[string] (required) -- `ReEvaluationJob.job_id` values emitted by the decision; empty when no job is emitted.
- `stale_object_ids`: list[string] (required) -- `StaleObject.stale_object_id` values produced by the decision; empty when no object is stale.
- `stale_set_ref`: string|null (required) -- reference to the materialized stale set for this decision, if one is persisted.
- `rejected_input_refs`: list[string] (required) -- input identifiers rejected during validation.
- `dependency_paths`: list[list[string]] (required) -- dependency paths evaluated for affected objects.
- `decision`: enum string (required) -- one of `jobs_emitted`, `no_affected_objects`, `blocked_untraceable`, `rejected_invalid_input`, `deduplicated`.
- `secondary_decisions`: list[string] (required) -- additional structured outcomes observed in the same decision, such as `deduplicated` or `blocked_untraceable`.
- `error_code`: enum string|null (required) -- one of `INVALID_PROPAGATION_INPUT`, `UNTRACEABLE_PROPAGATION_PATH`, `UNSAFE_REEVALUATION_JOB`, or null when the decision is valid without rejection.
- `rule_version`: string (required) -- deterministic propagation rule version used for evaluation.
- `evaluated_at`: datetime string (required) -- timestamp when this propagation decision was evaluated.
- `version_id`: string (required) -- version identifier for this propagation audit record.
- `created_at`: datetime string (required) -- timestamp when the propagation record was created.
- `updated_at`: datetime string (required) -- timestamp of the last state-preserving update to this propagation record.
- `version_hash`: string (required) -- deterministic hash of the canonical serialized propagation record fields.
- `source_ref`: string (required) -- primary upstream input reference for this propagation decision.
- `produced_by_motor`: string (required) -- constant value `motor_020`.
- `produced_at`: datetime string (required) -- timestamp when motor_020 produced this output object.
- `parent_id`: string|null (required) -- parent propagation record when this is a chained decision; null for a root decision.

## relationships
- `version_records.VersionRecord.version_id` -> `PropagationRecord.input_refs`: external reference from motor_002; a version mutation can trigger one or more propagation decisions.
- `quality_records.QualityRecord.quality_record_id` -> `PropagationRecord.input_refs`: external reference from motor_007; a quality degradation or conditional status can trigger propagation.
- `change_events.ChangeEvent.event_id` -> `PropagationRecord.input_refs`: external reference from motor_009; a source, schema, staleness, contract, taxonomy, or library change can trigger propagation.
- `PropagationRecord.propagation_record_id` -> `StaleObject.propagation_record_id`: one propagation decision can produce zero or many stale markers.
- `PropagationRecord.propagation_record_id` -> `ReEvaluationJob.propagation_record_id`: one propagation decision can emit zero or many re-evaluation jobs.
- `StaleObject.stale_object_id` -> `ReEvaluationJob.stale_object_id`: one stale marker can produce zero or one active job for the same `trigger_ref`, target object, target version, and propagation rule version.
- `ReEvaluationJob.job_id` -> `PropagationRecord.emitted_job_ids`: each emitted job is listed in the audit record that justified it.
- `StaleObject.stale_object_id` -> `PropagationRecord.stale_object_ids`: each stale marker is listed in the audit record that produced it.
- `PropagationRecord.stale_set_ref` -> `stale_set`: optional persisted collection reference containing the stale markers for the decision.
- `ReEvaluationJob.parent_id`, `StaleObject.parent_id`, and `PropagationRecord.parent_id` -> prior `PropagationRecord.propagation_record_id` or prior same-type record: optional chain references used only when a propagation decision creates downstream re-evaluation chains.
- Deduplication reference: `ReEvaluationJob` has a unique logical key over `trigger_ref`, `target_object_ref`, `target_version_ref`, and `propagation_rule_version`.

## identifiers
- `ReEvaluationJob.job_id`: canonical stable ID. It is generated deterministically from `motor_020`, `trigger_ref`, `target_object_ref`, `target_version_ref`, and `propagation_rule_version`.
- `StaleObject.stale_object_id`: canonical stable ID. It is generated deterministically from `motor_020`, `trigger_ref`, `object_ref`, `version_ref`, and `propagation_rule_version` or `rule_version`.
- `PropagationRecord.propagation_record_id`: canonical stable ID. It is generated deterministically from `motor_020`, `trigger_ref`, ordered `input_refs`, ordered `affected_object_refs`, and `rule_version`.
- `record_id`: optional storage alias permitted for systems that require a generic record key. When present, it must equal the entity canonical ID and must not replace `job_id`, `stale_object_id`, or `propagation_record_id`.
- External identifiers are never rewritten by this motor: `version_id` from motor_002, `quality_record_id` from motor_007, `event_id` from motor_009, `object_ref`, `source_ref`, `lineage_refs`, and `evidence_refs` remain references to upstream authority.

## versioning
Each `ReEvaluationJob`, `StaleObject`, and `PropagationRecord` carries the following required versioning fields:
- `version_id`: string (required) -- stable version identifier for the emitted record. It versions the motor_020 output record, not the upstream object itself.
- `created_at`: datetime string (required) -- creation timestamp for the emitted record.
- `updated_at`: datetime string (required) -- timestamp for the latest state-preserving update to the emitted record; must equal `created_at` when no later update exists.
- `version_hash`: string (required) -- deterministic hash over the canonical serialized record after excluding non-semantic transport metadata.

Versioning rules:
- `version_id` on motor_020 outputs does not create or mutate upstream versions managed by motor_002.
- `version_hash` must change when any semantic field in the emitted record changes.
- For deduplicated jobs, the surviving `job_id` remains stable and the `PropagationRecord.secondary_decisions` records `deduplicated`.
- `target_version_ref` and `version_ref` point to upstream or downstream object versions; they are references, not versions created by this motor.

## lineage
Each `ReEvaluationJob`, `StaleObject`, and `PropagationRecord` carries the following required lineage fields:
- `source_ref`: string (required) -- primary upstream source of the decision, normally the `trigger_ref` or the source object referenced by that trigger.
- `produced_by_motor`: string (required) -- constant value `motor_020`.
- `produced_at`: datetime string (required) -- timestamp when motor_020 emitted the record.
- `parent_id`: string|null (required) -- parent propagation record or prior same-type record in a re-evaluation chain; null for root emissions.

Lineage rules:
- `input_refs`, `evidence_refs`, `lineage_refs`, `dependency_path`, and `dependency_paths` must be sufficient to reconstruct why the record exists.
- A `ReEvaluationJob` must never exist without `propagation_record_id`; this preserves the audit link between a queued job and its decision.
- A `StaleObject` must never exist without `trigger_ref`, `stale_reason`, `object_ref`, and `propagation_record_id`.
- A `PropagationRecord` with `decision = blocked_untraceable` or `decision = rejected_invalid_input` must preserve rejected input references and error codes even when no stale marker or job is emitted.
- This motor records lineage and propagation decisions only; it does not create new upstream lineage nodes, mutate source records, or mark a re-evaluation as completed.
