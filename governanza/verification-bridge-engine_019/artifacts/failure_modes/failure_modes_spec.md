# Failure Modes Spec — Verification Bridge Engine

Motor ID: motor_019

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir claims y tensiones en rutas explícitas de endurecimiento de evidencia.
why_it_exists:  Sin este motor el sistema se queda en hipótesis y reporting, sin puente real a verificación.
key_inputs:     inference_records (motor_014), validation_data (motor_018), phase_contracts (motor_001)
key_outputs:    verification_path, hardening_agenda, evidence_gap_record
key_objects:    VerificationPath, HardeningAgenda, EvidenceGap
what_not_to_do: No cierra claims automáticamente. No puede ser reemplazado por synthetic_support.
design_notes:   Produce field_evidence level cuando completa verificación. Depende de motor_014, motor_018 y motor_001.

All placeholder markers in this file have been replaced with governed content.
-->

## failure_modes_list
- FM_019_CONTRACT_HANDOFF_BYPASS: `phase_contracts` are absent, stale, or not checked before output emission → `VerificationPath`, `HardeningAgenda`, or `EvidenceGap` records appear even though the active `motor_001` contract does not allow the required inputs or outputs → stop emission with `CONTRACT_MISMATCH`, discard partial objects, reload the active `phase_contract_id` plus `contract_version`, and rebuild the route only after the contract authorizes `verification_path`, `hardening_agenda`, and `evidence_gap_record`.
- FM_019_SYNTHETIC_SUPPORT_PROMOTION: `validation_data` or `inference_records.evidentiary_basis` include `synthetic_support`, `synthetic_data`, expert specification, capability demonstration, or `non_evidentiary_flag = true` → `linked_evidence_refs` contain non-real evidence or `current_evidence_level` is promoted above the strongest accepted real evidence → reject with `INVALID_EVIDENCE_LEVEL`, remove the invalid reference from all candidate evidence sets, and emit no verification-hardening outputs from that bundle until real `motor_018` validation data or authorized field evidence is supplied.
- FM_019_GAP_SUPPRESSION: an evidence requirement is missing, conflicting, stale, below threshold, or provenance-incomplete but no `EvidenceGap` is created → path status becomes `actionable` or `verified_evidence_ready` while `required_evidence[].is_satisfied = false`, `unresolved_gaps` remain upstream, or agenda actions omit the blocker → force path status to `blocked` or keep it below verified readiness, create one explicit `EvidenceGap` per unsatisfied requirement, and regenerate the `HardeningAgenda.blocking_gaps` and `prioritized_actions`.
- FM_019_LINEAGE_BREAK: source inference, validation data, phase contract, or emitted entity metadata lacks required lineage or version fields → emitted objects cannot be reconstructed from `source_inference_ref`, `phase_contract_id`, `contract_version`, `lineage_refs`, `version_id`, `version_hash`, `source_ref`, and `parent_id` → reject inference bundles with `MISSING_INFERENCE_LINEAGE`; for downstream object assembly failures, block emission and rebuild from immutable upstream references rather than filling lineage from labels or free text.
- FM_019_TARGET_REF_AMBIGUITY: an inference record has no explicit `claim_id` or `tension_id`, has both in an invalid combination, or supplies non-string target identifiers → route generation guesses a target from notes, labels, or natural-language text and produces unstable `path_id` values → reject with `UNSUPPORTED_TARGET_REF`, require exactly one supported target reference for the path, and derive identifiers only from canonical upstream ids.
- FM_019_CONFLICTING_EVIDENCE_AUTOPICK: multiple accepted validation records for the same target conflict under the phase contract threshold → the motor silently selects one record, suppresses the conflict, and raises `current_evidence_level` as if the evidence were reconciled → create a blocking `EvidenceGap` with `missing_evidence_type = "conflict_resolution"`, set `review_trigger` to an explicit conflict reason, and add a `reconcile_conflict` action to the agenda.
- FM_019_UPSTREAM_MUTATION_LEAK: implementation attempts to edit `motor_014` inference records, `motor_018` validation data, or `motor_001` phase contracts to make a route appear valid → upstream objects change without new upstream versions and the emitted lineage no longer matches the original records → abort the write path, preserve upstream inputs as read-only references, and represent corrections only as new upstream versions or as local `EvidenceGap` and agenda records.

## anti_patterns
- Coupling `motor_019` directly to mutable internals of `motor_014`, `motor_018`, or `motor_001` instead of consuming explicit records and immutable references.
- Treating `VerificationPath` as a final decision object that closes claims, resolves tensions, produces reports, or emits `claim_closed` / `final_decision` fields.
- Accepting synthetic support, expert assumptions, ML capability demonstrations, or non-evidentiary records as substitutes for real validation data or authorized field evidence.
- Collapsing `VerificationPath`, `HardeningAgenda`, and `EvidenceGap` into one narrative note or free-text checklist, which removes structured ids, dependency order, gap ownership, and auditability.
- Silently correcting missing lineage, missing provenance, invalid target references, or contract mismatches by inferring values from labels, prose, timestamps, or list order.
- Allowing `current_evidence_level` to be calculated from confidence language instead of from linked accepted real evidence refs.
- Generating agenda priorities from generic severity prose rather than from path status, `EvidenceGap.gap_severity`, dependency order, and phase-contract requirements.
- Reusing old agenda or gap ids after business content changes, instead of emitting new versions with updated `version_hash` and same-type `parent_id` linkage.
- Making the motor responsible for raw field capture, validation-data creation, report packaging, governance adjudication, or propagation/re-evaluation work assigned to other motors.

## degradation_signals
- `verification_paths_without_lineage / total_verification_paths > 0`: any missing `source_ref`, `lineage_refs`, `produced_by_motor`, `produced_at`, `version_id`, or `version_hash` indicates immediate degradation.
- `paths_verified_without_real_evidence_count > 0`: any path in `verified_evidence_ready` without accepted `motor_018` validation data or authorized field-evidence refs is a critical signal.
- Rising `INVALID_EVIDENCE_LEVEL` rejections from the same upstream source, especially when rejected refs contain `synthetic_support`, `synthetic_data`, `capability_demo`, or `non_evidentiary_flag`.
- High `unresolved_gaps` in source inference records while `EvidenceGap` creation remains near zero, indicating gap suppression or over-optimistic routing.
- Repeated `CONTRACT_MISMATCH` logs for the same `phase_contract_id` or missing `contract_version` on emitted paths and agendas.
- Increase in `HardeningAgenda` actions with empty `gap_ref`, empty `depends_on_action_ids`, generic `recommended_next_action`, or no concrete `expected_evidence_level`.
- Hash instability on repeated runs with identical inputs, rule version, and contract version, indicating non-deterministic identifiers, timestamp-dependent hashes, or list-order dependence.
- Growing count of paths that jump from `hypothesis` or `inference_result` directly to `field_evidence` without explicit linked validation or field-evidence lineage.
- Review-trigger backlog dominated by conflict, provenance, or contract issues, which indicates upstream evidence is not being converted into actionable gap records early enough.

## expensive_errors
- Promoting non-evidentiary support to verification evidence. Expensive because downstream agendas, reports, and governance reviews may treat unsupported claims as evidence-hardened, requiring manual trace audits and object retraction. Prevent it by rejecting synthetic or non-evidentiary refs before path materialization and by validating every `LinkedEvidenceRef.evidence_level`.
- Emitting paths without reconstructible lineage. Expensive because later reviewers cannot prove which inference, validation data, contract version, or rule version produced the route, so every dependent agenda must be rebuilt or discarded. Prevent it by making lineage and version fields mandatory preconditions for all persisted objects.
- Suppressing missing or conflicting evidence gaps. Expensive because operational teams receive an agenda that hides blockers, collect the wrong evidence, or execute steps out of order. Prevent it by requiring one `EvidenceGap` for each unsatisfied, conflicting, stale, below-threshold, or provenance-incomplete requirement before an agenda can be marked ready.
- Closing or deciding claims inside this motor. Expensive because it violates the motor boundary and contaminates downstream decision, reporting, and governance layers with unauthorized terminal states. Prevent it by schema-level rejection of `claim_closed`, `final_decision`, `report_package`, and equivalent fields in `motor_019` outputs.
- Mutating upstream inference, validation, or phase-contract records to make routes pass. Expensive because historical comparability and lineage are destroyed, and the error propagates outside this motor's audit boundary. Prevent it by treating all upstream inputs as read-only and representing needed corrections as upstream new versions or local gap records.
- Reusing identifiers across changed path, gap, or agenda content. Expensive because caches, lineage, and conformance reviews cannot distinguish old and new evidence states. Prevent it by hashing canonical content, emitting new `version_id` values for material changes, and setting `parent_id` only to the prior same-type entity.
- Inferring target identity from labels or prose. Expensive because later validation may attach evidence to the wrong claim or tension and require manual disentanglement of path, gap, and agenda history. Prevent it by rejecting unsupported target references and deriving `path_id` only from canonical `claim_id` or `tension_id` values.
