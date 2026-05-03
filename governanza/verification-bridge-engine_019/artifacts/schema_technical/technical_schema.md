# Technical Schema — Verification Bridge Engine

Motor ID: motor_019

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir claims y tensiones en rutas explícitas de endurecimiento de evidencia.
why_it_exists:  Sin este motor el sistema se queda en hipótesis y reporting, sin puente real a verificación.
key_inputs:     inference_records (motor_014), validation_data (motor_018), phase_contracts (motor_001)
key_outputs:    verification_path, hardening_agenda, evidence_gap_record
key_objects:    VerificationPath, HardeningAgenda, EvidenceGap
what_not_to_do: No cierra claims automáticamente. No puede ser reemplazado por synthetic_support.
design_notes:   Produce field_evidence level cuando completa verificación. Depende de motor_014, motor_018 y motor_001.

Sections below define the completed technical schema for this motor.
-->

## entities
- `VerificationPath`: persisted route from one `motor_014` claim or tension to the explicit evidence required to harden it. It records the source inference, phase contract, current evidence level, target evidence level, linked real validation data, required evidence items, ordered verification steps, open gaps and status. Stage: `schema_technical` as the canonical output contract; instantiated during implementation as `verification_path`.
- `HardeningAgenda`: persisted prioritized worklist derived from one or more `VerificationPath` records and their open `EvidenceGap` records. It orders verification actions by severity, dependency and evidentiary impact without collecting evidence or closing the underlying claim. Stage: `schema_technical` as the planning output contract; instantiated during implementation as `hardening_agenda`.
- `EvidenceGap`: persisted blocker or weakness record for missing, conflicting, stale, below-threshold or non-actionable evidence on a single verification path. It identifies the missing evidence type, severity, reason, next action and lineage required to resolve the gap through real validation or field evidence. Stage: `schema_technical` as the gap output contract; instantiated during implementation as `evidence_gap_record`.

Embedded technical objects used inside the entities:
- `TargetRef`: embedded object identifying exactly one `claim_id` or `tension_id` from the source inference context.
- `RequiredEvidenceItem`: embedded object describing one evidence requirement needed to move a path toward `validation_data` or `field_evidence`.
- `VerificationStep`: embedded object describing one deterministic action or review step in a verification path.
- `LinkedEvidenceRef`: embedded object referencing accepted `motor_018` validation data or authorized field-evidence references.
- `HardeningAction`: embedded object describing one agenda action tied to a path and, when applicable, an evidence gap.

## fields
`VerificationPath`
- `path_id: string` (required) — stable identifier for the verification path emitted by `motor_019`.
- `motor_id: enum[motor_019]` (required) — producing motor identifier.
- `target_ref: TargetRef` (required) — exact claim or tension being routed for evidence hardening.
- `source_inference_ref: string` (required) — `motor_014.InferenceRecord.inference_id` that supplied the claim or tension.
- `source_tension_ref: string|null` (required) — `motor_014.Tension.tension_id` when the target is a tension; null for claim-only targets.
- `phase_contract_id: string` (required) — `motor_001.PhaseContract.contract_id` authorizing this route.
- `contract_version: string` (required) — phase contract version used to validate allowed inputs, outputs and handoffs.
- `current_evidence_level: enum[hypothesis, inference_result, validation_data, field_evidence]` (required) — strongest real evidence level currently linked to the path; synthetic support is never valid here.
- `target_evidence_level: enum[validation_data, field_evidence]` (required) — evidence level required by the phase contract for the target.
- `required_evidence: list[RequiredEvidenceItem]` (required) — ordered evidence requirements that must be satisfied or explicitly represented by gaps.
- `linked_evidence_refs: list[LinkedEvidenceRef]` (required) — accepted real validation or field evidence references used by this path; empty only when every unmet need has an `EvidenceGap`.
- `verification_steps: list[VerificationStep]` (required) — ordered deterministic steps for checking, collecting, reconciling or reviewing evidence.
- `evidence_gap_refs: list[string]` (required) — `EvidenceGap.gap_id` values blocking or qualifying this path.
- `agenda_ref: string|null` (required) — `HardeningAgenda.agenda_id` when this path contributes to an agenda; null only before agenda materialization.
- `status: enum[draft, actionable, blocked, verified_evidence_ready]` (required) — route state; it does not close the claim or emit a final decision.
- `review_trigger: string|null` (required) — explicit reason a human or governance review is required; null when no review is required.
- `rule_version: string` (required) — deterministic rule set version used to evaluate evidence and gaps.
- `lineage_refs: list[string]` (required) — upstream lineage references from the inference record, validation data, phase contract and linked evidence.
- `version_id: string` (required) — immutable version identifier for this path instance.
- `created_at: datetime` (required) — timestamp when this path version was first emitted.
- `updated_at: datetime` (required) — timestamp when metadata for this exact path version was last materialized; equals `created_at` unless a new version is emitted.
- `version_hash: string` (required) — deterministic hash over canonical path content, upstream references, rule version and lineage.
- `source_ref: string` (required) — canonical upstream source reference, normally `source_inference_ref` plus the target claim or tension id.
- `produced_by_motor: enum[motor_019]` (required) — fixed producer value.
- `produced_at: datetime` (required) — timestamp when `motor_019` emitted this object.
- `parent_id: string|null` (required) — previous `path_id` when this path supersedes an earlier version; null for first emission.

`HardeningAgenda`
- `agenda_id: string` (required) — stable identifier for the agenda emitted by `motor_019`.
- `motor_id: enum[motor_019]` (required) — producing motor identifier.
- `path_refs: list[string]` (required) — ordered `VerificationPath.path_id` values included in the agenda.
- `prioritized_actions: list[HardeningAction]` (required) — ordered action records for collection, reconciliation, review or field confirmation.
- `dependency_order: list[string]` (required) — action ids or path ids sorted so prerequisites precede dependent actions.
- `blocking_gaps: list[string]` (required) — `EvidenceGap.gap_id` values that prevent paths from reaching their target evidence level.
- `owner_role: string` (required) — accountable operational role for executing or coordinating the agenda.
- `review_trigger: string` (required) — explicit trigger that caused agenda creation, such as open blocking gaps, conflicting validation data or required field confirmation.
- `generated_from_version: string` (required) — content or batch version of the path and gap set used to generate the agenda.
- `phase_contract_id: string` (required) — `motor_001.PhaseContract.contract_id` governing allowed agenda outputs.
- `contract_version: string` (required) — contract version evaluated for the agenda.
- `status: enum[open, partially_blocked, ready_for_execution, superseded]` (required) — operational agenda state without implying claim closure.
- `lineage_refs: list[string]` (required) — combined lineage references from included paths, gaps, validation data and phase contract.
- `version_id: string` (required) — immutable version identifier for this agenda instance.
- `created_at: datetime` (required) — timestamp when this agenda version was first emitted.
- `updated_at: datetime` (required) — timestamp when metadata for this exact agenda version was last materialized; equals `created_at` unless a new version is emitted.
- `version_hash: string` (required) — deterministic hash over included path refs, action ordering, gap refs, contract version and lineage.
- `source_ref: string` (required) — canonical source reference for the agenda, normally the sorted included `path_refs` plus `generated_from_version`.
- `produced_by_motor: enum[motor_019]` (required) — fixed producer value.
- `produced_at: datetime` (required) — timestamp when `motor_019` emitted this object.
- `parent_id: string|null` (required) — previous `agenda_id` when this agenda supersedes an earlier version; null for first emission.

`EvidenceGap`
- `gap_id: string` (required) — stable identifier for the evidence gap emitted by `motor_019`.
- `motor_id: enum[motor_019]` (required) — producing motor identifier.
- `path_id: string` (required) — owning `VerificationPath.path_id`.
- `target_ref: TargetRef` (required) — claim or tension affected by the gap.
- `source_inference_ref: string` (required) — `motor_014.InferenceRecord.inference_id` that supplied the target.
- `phase_contract_id: string` (required) — `motor_001.PhaseContract.contract_id` whose evidence rule or handoff boundary is not yet satisfied.
- `contract_version: string` (required) — phase contract version evaluated when the gap was emitted.
- `missing_evidence_type: enum[measurement, observation, source_confirmation, site_validation, conflict_resolution, provenance]` (required) — specific evidence class missing or requiring reconciliation.
- `gap_severity: enum[low, medium, high, blocking]` (required) — deterministic severity assigned from impact on the verification path.
- `blocking_reason: string` (required) — concise structured reason the path cannot advance without resolving this gap.
- `recommended_next_action: string` (required) — specific next action for the agenda or validation workflow.
- `related_validation_data_refs: list[string]` (required) — `motor_018` validation data refs involved in the gap; empty when evidence is absent.
- `resolved_by_ref: string|null` (required) — validation data or field evidence reference that resolves the gap; null while unresolved.
- `status: enum[open, assigned, resolved_by_validation_data, deferred_with_reason]` (required) — lifecycle state of the gap without mutating upstream records.
- `lineage_refs: list[string]` (required) — upstream lineage references from the source inference, phase contract, linked validation data and path.
- `version_id: string` (required) — immutable version identifier for this gap instance.
- `created_at: datetime` (required) — timestamp when this gap version was first emitted.
- `updated_at: datetime` (required) — timestamp when metadata for this exact gap version was last materialized; equals `created_at` unless a new version is emitted.
- `version_hash: string` (required) — deterministic hash over target, missing evidence type, severity, status, source refs and lineage.
- `source_ref: string` (required) — canonical source reference, normally `path_id` plus the affected evidence requirement.
- `produced_by_motor: enum[motor_019]` (required) — fixed producer value.
- `produced_at: datetime` (required) — timestamp when `motor_019` emitted this object.
- `parent_id: string|null` (required) — previous `gap_id` when this gap supersedes an earlier version; null for first emission.

`TargetRef`
- `target_type: enum[claim, tension]` (required) — target class routed by the path.
- `claim_id: string|null` (required) — claim identifier from the inference record when target_type is `claim`; null for pure tension targets.
- `tension_id: string|null` (required) — tension identifier from `motor_014` when target_type is `tension`; null for claim-only targets.
- `target_label: string|null` (optional) — short stable label copied from upstream metadata when available; not used as an identifier.

`RequiredEvidenceItem`
- `evidence_requirement_id: string` (required) — stable id for the requirement within a path.
- `evidence_type: enum[measurement, observation, source_confirmation, site_validation, conflict_resolution, provenance]` (required) — required evidence class.
- `required_level: enum[validation_data, field_evidence]` (required) — evidence level required for the item.
- `satisfied_by_refs: list[string]` (required) — linked evidence refs satisfying the item; empty when unsatisfied.
- `is_satisfied: bool` (required) — deterministic satisfaction flag derived from real linked evidence.
- `gap_ref: string|null` (required) — `EvidenceGap.gap_id` created for the unsatisfied item; null when satisfied.

`VerificationStep`
- `step_id: string` (required) — stable id for the step within a path.
- `step_type: enum[check_validation_data, collect_field_evidence, reconcile_conflict, confirm_source, governance_review]` (required) — allowed step category.
- `depends_on_step_ids: list[string]` (required) — prerequisite step ids within the same path.
- `input_refs: list[string]` (required) — inference, validation data, field evidence or contract refs used by the step.
- `expected_output: string` (required) — structured expected artifact or state transition for the step.
- `step_status: enum[pending, ready, blocked, completed]` (required) — step execution readiness; completion does not close the claim.

`LinkedEvidenceRef`
- `evidence_ref_id: string` (required) — stable reference id inside the path.
- `upstream_motor_id: enum[motor_018, external_field_evidence]` (required) — source of the evidence reference.
- `upstream_artifact_ref: string` (required) — `motor_018` validation data object or authorized field-evidence artifact reference.
- `evidence_level: enum[validation_data, field_evidence]` (required) — accepted real evidence level; synthetic support is invalid.
- `quality_status: enum[accepted, accepted_with_warning]` (required) — copied or mapped quality state that permits use as evidence.
- `lineage_ref: string` (required) — upstream lineage reference needed to reconstruct the evidence.

`HardeningAction`
- `action_id: string` (required) — stable identifier for the agenda action.
- `path_ref: string` (required) — `VerificationPath.path_id` that requires the action.
- `gap_ref: string|null` (required) — `EvidenceGap.gap_id` addressed by the action; null only for non-blocking confirmation steps.
- `action_type: enum[collect_measurement, obtain_observation, confirm_source, reconcile_conflict, complete_provenance, request_governance_review]` (required) — allowed action category.
- `priority: enum[low, medium, high, blocking]` (required) — action priority derived from path status and gap severity.
- `depends_on_action_ids: list[string]` (required) — agenda action dependencies that must be completed first.
- `expected_evidence_level: enum[validation_data, field_evidence]` (required) — evidence level the action is intended to obtain or confirm.
- `owner_role: string` (required) — role responsible for executing the action.
- `action_status: enum[pending, ready, blocked, completed, deferred]` (required) — action state inside the agenda.

## relationships
- `VerificationPath.source_inference_ref` references `motor_014.InferenceRecord.inference_id` with cardinality many paths over time to one source inference version. The source inference is read-only.
- `VerificationPath.source_tension_ref` references `motor_014.Tension.tension_id` when `target_ref.target_type = tension`; it is null for claim targets.
- `VerificationPath.phase_contract_id` plus `VerificationPath.contract_version` references `motor_001.PhaseContract.contract_id` plus contract version. The contract must allow `verification_path`, `hardening_agenda` and `evidence_gap_record` outputs for this phase.
- `VerificationPath.linked_evidence_refs[].upstream_artifact_ref` references real `motor_018` validation data objects or authorized field-evidence artifacts. References tagged as synthetic support, non-evidentiary support, expert specification or capability demonstration are invalid.
- `VerificationPath.evidence_gap_refs[]` references `EvidenceGap.gap_id` values owned by the same `path_id`.
- `VerificationPath.agenda_ref` references `HardeningAgenda.agenda_id` when the path is included in an agenda.
- `EvidenceGap.path_id` references `VerificationPath.path_id` with cardinality one path to zero or more gaps.
- `EvidenceGap.source_inference_ref` references the same source inference used by the owning path; gaps cannot point to unrelated inference records.
- `EvidenceGap.related_validation_data_refs[]` references validation data involved in absence, conflict, staleness, provenance or threshold failure.
- `EvidenceGap.resolved_by_ref` references the validation data or field-evidence artifact that resolves the gap; it remains null while status is `open`, `assigned` or `deferred_with_reason`.
- `HardeningAgenda.path_refs[]` references `VerificationPath.path_id` with cardinality one agenda to one or more paths.
- `HardeningAgenda.blocking_gaps[]` references `EvidenceGap.gap_id` values that belong to the included paths.
- `HardeningAgenda.prioritized_actions[].path_ref` references an included `VerificationPath.path_id`; `HardeningAgenda.prioritized_actions[].gap_ref` references a blocking or qualifying `EvidenceGap.gap_id` when the action addresses a gap.
- `parent_id` on each persisted entity references only the prior emitted entity of the same type when superseded; it must not point to upstream inference records, validation data, phase contracts or unrelated agenda objects.
- No relationship in this schema grants authority to close claims, mutate upstream records, collect raw field data, redefine phase contracts, produce reports or promote synthetic support to evidence.

## identifiers
- `VerificationPath`: canonical identifier is `path_id`. Recommended deterministic form: `motor_019:verification_path:{source_inference_ref}:{target_type}:{claim_or_tension_id}:{contract_version}:{version_hash_prefix}`.
- `HardeningAgenda`: canonical identifier is `agenda_id`. Recommended deterministic form: `motor_019:hardening_agenda:{generated_from_version}:{version_hash_prefix}`.
- `EvidenceGap`: canonical identifier is `gap_id`. Recommended deterministic form: `motor_019:evidence_gap:{path_id}:{evidence_requirement_id_or_gap_type}:{version_hash_prefix}`.
- Embedded `TargetRef` has no independent persisted id; it is identified by `target_type` plus `claim_id` or `tension_id` inside the owning object.
- Embedded `RequiredEvidenceItem` stable id is `evidence_requirement_id`, scoped by `path_id`.
- Embedded `VerificationStep` stable id is `step_id`, scoped by `path_id`.
- Embedded `LinkedEvidenceRef` stable id is `evidence_ref_id`, scoped by `path_id` and the referenced upstream artifact.
- Embedded `HardeningAction` stable id is `action_id`, scoped by `agenda_id`.
- `record_id` is not the canonical id for this motor unless an implementation storage layer aliases it to `path_id`, `agenda_id` or `gap_id` for persistence. The canonical entity ids remain `path_id`, `agenda_id` and `gap_id`.
- Identifier stability rule: ids are derived from canonical upstream identifiers, contract version, deterministic requirement or action ids and version hash prefixes. Display labels, timestamps alone, list order alone and natural-language descriptions are not valid stable identifiers.

## versioning
- Every persisted `VerificationPath`, `HardeningAgenda` and `EvidenceGap` must include `version_id`, `created_at`, `updated_at` and `version_hash`.
- `version_id: string` (required) — immutable version identifier for a materialized entity instance. Recommended format: `motor_019:v:{entity_name}:{version_hash_prefix}`.
- `created_at: datetime` (required) — timestamp when the entity version was first emitted by `motor_019`.
- `updated_at: datetime` (required) — timestamp when metadata for the exact entity version was last materialized. If business content changes, a new `version_id` and `version_hash` are required instead of silent mutation.
- `version_hash: string` (required) — deterministic hash over canonicalized entity content, including canonical id, target ref, source inference ref, phase contract id, contract version, linked evidence refs, gap refs, action ordering, status, rule version, lineage refs and parent reference. Volatile transport metadata is excluded from the hash input.
- `VerificationPath.version_hash` changes when the source inference version, target ref, required evidence set, linked evidence refs, current or target evidence level, verification steps, gap refs, status, rule version, contract version or lineage changes.
- `HardeningAgenda.version_hash` changes when included paths, prioritized action content or order, dependency order, blocking gaps, owner role, review trigger, generated source version, contract version or lineage changes.
- `EvidenceGap.version_hash` changes when the owning path, missing evidence type, severity, blocking reason, recommended action, related validation data, resolving evidence ref, status, contract version or lineage changes.
- `parent_id` links a new materialized version to the prior canonical id of the same entity type. Prior versions remain reconstructible and are never overwritten to make a path appear complete.
- Re-running `motor_019` with the same accepted inputs, rule version and contract version must reproduce the same canonical ids and version hashes, excluding only non-material runtime envelope details.

## lineage
- Every persisted `VerificationPath`, `HardeningAgenda` and `EvidenceGap` must include `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref: string` (required) — reconstructible pointer to the source context that caused the entity to exist.
- `produced_by_motor: enum[motor_019]` (required) — fixed producer value for all objects emitted by this motor.
- `produced_at: datetime` (required) — timestamp when `motor_019` emitted the object; it must not be copied from upstream inference or validation timestamps.
- `parent_id: string|null` (required) — previous same-type entity id when the current entity supersedes an earlier version; null for first emission.
- `VerificationPath.source_ref` points to `source_inference_ref` plus the exact `TargetRef`; its lineage must also include the evaluated phase contract, rule version and any linked validation or field-evidence references.
- `HardeningAgenda.source_ref` points to the sorted `path_refs` plus `generated_from_version`; its lineage must include every included path, blocking gap, action dependency and phase contract used to order the agenda.
- `EvidenceGap.source_ref` points to the owning `path_id` plus the affected evidence requirement; its lineage must include the source inference, contract version, related validation data when present and the rule that classified the missing or conflicting evidence.
- `lineage_refs` must preserve all upstream references required to reconstruct the route from `motor_014` inference or tension, through `motor_018` validation data and `motor_001` phase contract, to the emitted path, agenda or gap.
- Missing `source_ref`, missing `produced_by_motor`, missing `produced_at`, missing required parent linkage on supersession, empty `lineage_refs` or lineage that points to synthetic support makes the object invalid rather than partially acceptable.
- Lineage fields are audit metadata only. They do not authorize `motor_019` to mutate inference records, validation data, phase contracts, source records, raw field data or reporting artifacts.
