# Test Spec — Verification Bridge Engine

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

## happy_path
Input bundle:
- `inference_records`: one motor_014 record with `inference_id = "inf_014_power_001"`, `claim_id = "claim_facility_power_gap"`, `tension_id = null`, `confidence_state = "hypothesis_with_real_indicators"`, `evidentiary_basis = ["val_018_meter_031"]`, `unresolved_gaps = ["maintenance_log_confirmation"]`, `lineage_refs = ["lin_014_power_001"]`, and `version_id = "motor_014:v:inf_014_power_001"`.
- `validation_data`: one motor_018 record with `validation_data_id = "val_018_meter_031"`, `evidence_level = "validation_data"`, `measured_value = {"metric": "power_draw_kw", "value": 187.4, "unit": "kW"}`, `source_provenance = "site_meter_export"`, `quality_status = "accepted"`, `lineage_refs = ["lin_018_meter_031"]`, and `version_id = "motor_018:v:val_018_meter_031"`.
- `phase_contracts`: one motor_001 contract with `contract_id = "phase4_verification_v2"`, `contract_version = "2.0.0"`, `allowed_inputs = ["inference_records", "validation_data"]`, `allowed_outputs = ["verification_path", "hardening_agenda", "evidence_gap_record"]`, `evidence_thresholds = {"claim_facility_power_gap": "field_evidence"}`, and `handoff_rules = {"requires_lineage": true, "allow_synthetic_support": false}`.

Expected output:
- One `VerificationPath` is emitted with `target_ref.target_type = "claim"`, `target_ref.claim_id = "claim_facility_power_gap"`, `source_inference_ref = "inf_014_power_001"`, `source_tension_ref = null`, `phase_contract_id = "phase4_verification_v2"`, `contract_version = "2.0.0"`, `current_evidence_level = "validation_data"`, `target_evidence_level = "field_evidence"`, `status = "actionable"`, and non-empty `lineage_refs` containing both upstream lineage values.
- The path includes one `LinkedEvidenceRef` for `val_018_meter_031` with `upstream_motor_id = "motor_018"`, `evidence_level = "validation_data"`, and `quality_status = "accepted"`.
- The path includes at least two `RequiredEvidenceItem` records: the meter reading item is satisfied by `val_018_meter_031`, while the maintenance confirmation item has `is_satisfied = false` and a non-null `gap_ref`.
- One `EvidenceGap` is emitted for the unsatisfied maintenance confirmation with `missing_evidence_type = "source_confirmation"`, `gap_severity = "blocking"`, `status = "open"`, `resolved_by_ref = null`, and a concrete `recommended_next_action`.
- One `HardeningAgenda` is emitted with the path id in `path_refs`, the gap id in `blocking_gaps`, `review_trigger = "blocking_evidence_gap"`, `status = "partially_blocked"`, and prioritized actions that place source confirmation after the accepted meter validation check.
- No output contains `claim_closed`, `final_decision`, `report_package`, `output_block`, `synthetic_support`, or mutation of any upstream input record.

## sparse_case
Input bundle:
- `inference_records`: one valid motor_014 record with `inference_id = "inf_014_site_002"`, `claim_id = "claim_roof_leak_source"`, `tension_id = null`, `target_label` absent, `confidence_state = "hypothesis_only"`, `evidentiary_basis = []`, `unresolved_gaps = ["site_observation_required"]`, `lineage_refs = ["lin_014_site_002"]`, and `version_id = "motor_014:v:inf_014_site_002"`.
- `validation_data`: an empty list.
- `phase_contracts`: one valid contract allowing `verification_path`, `hardening_agenda`, and `evidence_gap_record`, with target evidence threshold `validation_data` for `claim_roof_leak_source`.

Expected behavior:
- The motor does not raise a fatal error only because optional `target_label` is absent or because no matching validation data exists.
- One `VerificationPath` is emitted with `current_evidence_level = "hypothesis"`, `target_evidence_level = "validation_data"`, `linked_evidence_refs = []`, `status = "blocked"`, and non-empty `required_evidence`.
- One `EvidenceGap` is emitted with `missing_evidence_type = "site_validation"`, `gap_severity = "blocking"`, `related_validation_data_refs = []`, `resolved_by_ref = null`, and lineage back to the inference record and phase contract.
- One `HardeningAgenda` is emitted with an action of type `obtain_observation` or `collect_measurement`, `priority = "blocking"`, and `expected_evidence_level = "validation_data"`.
- The motor still preserves `source_inference_ref`, `phase_contract_id`, `contract_version`, `source_ref`, `produced_by_motor = "motor_019"`, and `parent_id = null` on first emitted versions.

## malformed_input
Case A: missing inference lineage.
- Input has `inference_id = "inf_014_bad_lineage"`, `claim_id = "claim_missing_lineage"`, valid phase contract, and valid validation data, but `lineage_refs = []` or `version_id` is absent on the inference record.
- Expected result: reject the whole bundle with `MISSING_INFERENCE_LINEAGE`; emit no `VerificationPath`, `HardeningAgenda`, or `EvidenceGap`.

Case B: invalid evidence level.
- Input has a validation record referenced by the inference record, but the validation record has `evidence_level = "synthetic_support"` or `non_evidentiary_flag = true`.
- Expected result: reject with `INVALID_EVIDENCE_LEVEL`; emit no evidence-hardening output that treats the record as validation evidence.

Case C: contract mismatch.
- Input has a valid inference record and real validation data, but the only phase contract has `allowed_outputs = ["report_package"]` and omits `verification_path`, `hardening_agenda`, or `evidence_gap_record`.
- Expected result: reject with `CONTRACT_MISMATCH`; do not create route, agenda, or gap objects outside the authorized handoff.

Case D: unsupported target reference.
- Input inference record has neither `claim_id` nor `tension_id`, or supplies non-string values such as `claim_id = 8127`.
- Expected result: reject with `UNSUPPORTED_TARGET_REF`; do not infer a target from labels, notes, or natural-language text.

## edge_cases
1. Conflicting accepted validation data.
   - Input contains `val_018_meter_a` and `val_018_meter_b` for the same claim, both with `quality_status = "accepted"` and real provenance, but their observations cannot both be true under the phase contract threshold.
   - Correct behavior: the motor does not choose one silently. It emits or updates a `VerificationPath` with `current_evidence_level` no higher than the strongest non-conflicting real evidence, creates an `EvidenceGap` with `missing_evidence_type = "conflict_resolution"` and `gap_severity = "blocking"`, sets `review_trigger` to a conflict review reason, and creates a `HardeningAgenda` action with `action_type = "reconcile_conflict"`.

2. Already authorized field evidence.
   - Input contains an inference record and a phase contract requiring `field_evidence`; linked evidence includes an authorized field-evidence reference with real provenance, accepted quality, lineage, and a contract-allowed source.
   - Correct behavior: the motor emits a `VerificationPath` with `current_evidence_level = "field_evidence"`, `target_evidence_level = "field_evidence"`, `status = "verified_evidence_ready"`, no open `EvidenceGap` for already satisfied requirements, and preserved lineage. It still does not emit `claim_closed`, `final_decision`, or any report artifact.

3. Multiple unresolved gaps on one target.
   - Input has one valid claim with accepted validation data for measurement, but unresolved evidence needs for provenance completion, source confirmation, and site observation.
   - Correct behavior: the path remains a single path for the claim, while separate `EvidenceGap` records are emitted for each unsatisfied evidence requirement. The `HardeningAgenda.dependency_order` places provenance completion before source confirmation when the source confirmation depends on provenance.

4. Tension target instead of claim target.
   - Input has `claim_id = null`, `tension_id = "tension_cost_vs_quality_004"`, lineage, version, and a contract that allows tension verification routes.
   - Correct behavior: the motor emits `target_ref.target_type = "tension"`, `target_ref.tension_id = "tension_cost_vs_quality_004"`, `source_tension_ref = "tension_cost_vs_quality_004"`, and creates evidence requirements and gaps against the tension without inventing a claim id.

## pass_criteria
The test passes when all applicable output objects satisfy these observable conditions:
- Required outputs are present for valid inputs: at least one `VerificationPath`, one `HardeningAgenda` when actions or gaps exist, and one `EvidenceGap` for each unsatisfied, conflicting, missing, stale, below-threshold, or provenance-incomplete requirement.
- Every emitted object includes stable ids, `motor_id = "motor_019"`, `produced_by_motor = "motor_019"`, `source_ref`, `produced_at`, `parent_id`, `version_id`, `version_hash`, and non-empty `lineage_refs`.
- Every `VerificationPath` preserves `source_inference_ref`, `phase_contract_id`, `contract_version`, `target_ref`, `required_evidence`, `verification_steps`, `current_evidence_level`, `target_evidence_level`, and a valid route status.
- `current_evidence_level` never exceeds the strongest accepted real evidence linked to the path, and synthetic or non-evidentiary inputs are never present in `linked_evidence_refs`.
- Missing or conflicting evidence is represented by explicit `EvidenceGap` records and agenda actions rather than being ignored.
- Rejected malformed bundles return the expected structured error code and emit no partial route, agenda, or gap objects.
- Outputs contain no upstream mutation and no terminal claim disposition fields.

## fail_criteria
The test fails when any of these observable conditions occurs:
- A valid sparse input raises a fatal error instead of emitting a blocked path with explicit gaps.
- A malformed input emits any `VerificationPath`, `HardeningAgenda`, or `EvidenceGap` instead of returning `MISSING_INFERENCE_LINEAGE`, `INVALID_EVIDENCE_LEVEL`, `CONTRACT_MISMATCH`, or `UNSUPPORTED_TARGET_REF` as applicable.
- Any output accepts `synthetic_support`, `synthetic_data`, `expert_spec`, `capability_demo`, or `non_evidentiary_flag` content as verification evidence.
- A path reaches `verified_evidence_ready` without real validation or field-evidence references allowed by the phase contract.
- Missing, conflicting, stale, below-threshold, or provenance-incomplete evidence is not represented by an `EvidenceGap`.
- Output includes `claim_closed`, `final_decision`, `report_package`, `output_block`, raw field capture, phase contract edits, or mutated upstream inference and validation records.
- Any emitted object lacks required lineage, versioning, stable identifiers, producer metadata, or reconstructible upstream references.
