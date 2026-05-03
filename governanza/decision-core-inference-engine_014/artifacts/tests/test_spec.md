# Test Spec — Decision Core / Inference Engine

Motor ID: motor_014

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
why_it_exists:  Es el corazón analítico de Fase 2.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001)
key_outputs:    inference_record, tension_record, gap_agenda, validation_agenda
key_objects:    InferenceRecord, Tension, ValidationAgenda
what_not_to_do: No produce reportes finales. No verifica claims. Solo infiere y registra con contratos explícitos.
design_notes:   Determinismo primero. La IA puede asistir pero no decide. Depende de motor_013 y motor_001.

Sections below define the completed test specification for this motor.
-->

## happy_path
Input batch:
- `inference_cases` contains exactly one case:
  - `case_id = "IC-014-HP-001"`
  - `activation_record_ref = "AR-013-HP-001"`
  - `trigger_log_ref = "TL-013-HP-001"`
  - `phase_id = "phase_2"`
  - `case_status = "activated"`
  - `analysis_question = "Does facility FAC-123 require validation of backup power resilience?"`
  - `evidence_refs = [{"evidence_id": "EV-FAC-123-PRIOR", "source_class": "facility_prior", "evidence_level": "contextual", "provenance_ref": "PROV-FAC-123", "lineage_ref": "LIN-FAC-123"}, {"evidence_id": "EV-LIB-456", "source_class": "library_object", "evidence_level": "contextual", "provenance_ref": "PROV-LIB-456", "lineage_ref": "LIN-LIB-456"}]`
  - `lineage_refs = ["LIN-IC-014-HP-001", "LIN-FAC-123", "LIN-LIB-456"]`
- `phase_contracts` contains exactly one matching contract:
  - `contract_id = "PC-PHASE-2-v1"`
  - `phase_id = "phase_2"`
  - `allowed_inputs = ["inference_cases"]`
  - `allowed_outputs = ["inference_record", "tension_record", "gap_agenda", "validation_agenda"]`
  - `handoff_rules = {"validation": "motor_018"}`
  - `output_limits = {"may_verify_claims": false, "may_render_reports": false}`
  - `contract_version = "1.0.0"`

Expected output:
- Exactly one `InferenceRecord` is emitted with `motor_id = "motor_014"`, `case_id = "IC-014-HP-001"`, `activation_record_ref = "AR-013-HP-001"`, `trigger_log_ref = "TL-013-HP-001"`, `phase_contract_ref = "PC-PHASE-2-v1"`, `contract_version = "1.0.0"`, `inference_state = "bounded_inference"`, `synthetic_support_present = false`, `produced_by_motor = "motor_014"`, non-empty `decision_trace`, non-empty `lineage_refs`, and `parent_id = null`.
- `InferenceRecord.evidence_refs` preserves both input evidence references with their `provenance_ref` and `lineage_ref`.
- `tension_record` contains one `Tension` with `tension_type = "missing_evidence"`, `severity = "medium"`, `requires_validation = true`, and `source_refs` containing `EV-FAC-123-PRIOR` and `EV-LIB-456`.
- `gap_agenda` contains one `GapItem` with `gap_type = "missing_validation_data"`, `affected_ref` equal to the emitted `inference_id`, `missing_condition = "site-level backup power validation data"`, `required_downstream_action = "request validation data through motor_018"`, and `priority = "medium"`.
- `validation_agenda` contains one `ValidationItem` derived from that gap, with `required_evidence_level = "validation_data"`, `handoff_target = "motor_018"`, `priority = "medium"`, and `source_refs` preserving the gap and evidence references.

## sparse_case
Input batch:
- `inference_cases` contains one activated case `IC-014-SP-001` with all required identifiers, a matching `phase_id = "phase_2"`, a bounded `analysis_question`, one evidence reference, and one lineage reference.
- The case omits non-required enrichment fields such as precomputed tension hints, prior validation routes, synthetic-assist notes, analyst comments, and confidence labels.
- The single evidence reference is `{"evidence_id": "EV-SP-001", "source_class": "facility_prior", "evidence_level": "contextual", "provenance_ref": "PROV-SP-001", "lineage_ref": "LIN-SP-001"}`.
- The matching phase contract authorizes `inference_cases` as input and all four motor outputs.

Expected behavior:
- The motor accepts the case because every required contract and lineage field is present.
- The motor does not infer omitted enrichment fields and does not create placeholder values for analyst comments, confidence labels, or validation routes.
- The emitted `InferenceRecord.inference_state` is `blocked_by_gap` when the single contextual evidence reference is insufficient for `bounded_inference`.
- The emitted `GapAgenda` includes one `GapItem` with `gap_type = "missing_validation_data"` or `gap_type = "missing_evidence"` and a concrete `missing_condition` tied to `IC-014-SP-001`.
- The emitted `ValidationAgenda.validation_items` contains a corresponding item with a non-empty `reason` and an authorized `handoff_target` from the phase contract.

## malformed_input
The motor must reject the whole processing request and emit no analytical outputs for each malformed input below:

- Missing required identifier: `case_id = ""` or `case_id = null` in any case. Expected error code: `CASE_ID_REQUIRED`.
- Duplicate identifier: two accepted input objects both use `case_id = "IC-014-DUP-001"`. Expected error code: `CASE_ID_REQUIRED`.
- Non-activated case: `case_status = "draft"`, `case_status = "rejected"`, or any value other than `activated`. Expected error code: `INFERENCE_CASE_NOT_ACTIVATED`.
- Missing phase contract: an activated case has `phase_id = "phase_missing"` and no `PhaseContract` with the same `phase_id`. Expected error code: `PHASE_CONTRACT_MISSING`.
- Contract output violation: matching contract exists but `allowed_outputs` omits `validation_agenda` or `gap_agenda`. Expected error code: `PHASE_CONTRACT_VIOLATION`.
- Evidence reference without provenance or lineage: an evidence entry includes `evidence_id = "EV-BAD-001"` and `source_class = "source_record"` but has an empty `provenance_ref` or empty `lineage_ref`. Expected error code: `PROVENANCE_REQUIRED`.
- Wrong type: `inference_cases` is an object instead of a list, `phase_contracts` is a string instead of a list, or `evidence_refs` is a string instead of a list of evidence reference objects. Expected error code: `INVALID_INPUT_TYPE`.

## edge_cases
1. Synthetic-only support:
   - Input: activated case `IC-014-EDGE-SYN-001` with one evidence reference whose `source_class = "synthetic_support"` and `evidence_level = "synthetic"`, plus valid provenance, lineage, activation, trigger, and phase contract references.
   - Correct behavior: emit an `InferenceRecord` with `synthetic_support_present = true` and `inference_state = "hypothesis_only"`; emit a `GapAgenda` and `ValidationAgenda` requiring `validation_data` or `field_evidence`; do not promote the synthetic reference to validation data or field evidence.

2. Conflicting real evidence:
   - Input: activated case `IC-014-EDGE-CONFLICT-001` with evidence `EV-CONFLICT-A` indicating adequate backup power and evidence `EV-CONFLICT-B` indicating a possible backup power failure condition. Both references include provenance and lineage.
   - Correct behavior: preserve both source references, emit a `Tension` with `tension_type = "conflict"` and `requires_validation = true`, create a gap item with `gap_type = "unresolved_conflict"`, and create a validation item for the authorized downstream handoff. The motor must not silently choose one evidence reference as the winner.

3. No detected tension:
   - Input: activated case `IC-014-EDGE-CLEAN-001` with consistent contextual or validation-data evidence, valid lineage, and a matching contract authorizing all output classes.
   - Correct behavior: emit one `InferenceRecord` and empty `tension_record`, `gap_agenda.gap_items`, and `validation_agenda.validation_items` lists when no gap or validation need remains. Empty lists are valid only when lineage and contract metadata are still present.

4. Deterministic rerun:
   - Input: the same canonical case, contract, evidence references, `rule_version`, and parent reference are processed twice.
   - Correct behavior: stable identifiers, `decision_trace`, `inference_state`, gap categories, validation targets, and `version_hash` are identical across both runs after excluding runtime-only timestamp fields.

## pass_criteria
A test passes only when all applicable observable conditions are true:
- Valid input produces only the four authorized output classes: `inference_record`, `tension_record`, `gap_agenda`, and `validation_agenda`.
- Every emitted top-level record has `motor_id = "motor_014"`, `produced_by_motor = "motor_014"`, non-empty `lineage_refs`, `phase_contract_ref`, `contract_version`, `rule_version`, `created_at`, `updated_at`, `version_id`, `version_hash`, `source_ref`, `produced_at`, and an explicit `parent_id` value.
- Every emitted `InferenceRecord` preserves `case_id`, `activation_record_ref`, `trigger_log_ref`, `analysis_question`, all accepted evidence references, and all required provenance and lineage references.
- Every emitted `Tension.inference_id`, `GapAgenda.inference_id`, and `ValidationAgenda.inference_id` references the emitted `InferenceRecord.inference_id`.
- Every gap item has `gap_item_id`, `gap_type`, `affected_ref`, `missing_condition`, `required_downstream_action`, `priority`, and non-empty `source_refs`.
- Every validation item has `validation_item_id`, `gap_item_id`, `required_evidence_level`, `reason`, `handoff_target`, `priority`, and non-empty `source_refs`.
- Malformed input returns the specified structured error code and emits no partial `InferenceRecord`, `Tension`, `GapAgenda`, or `ValidationAgenda`.
- Synthetic-only cases remain `hypothesis_only`, and conflicting evidence produces an explicit `Tension` and validation need.

## fail_criteria
A test fails when any observable condition below occurs:
- The motor emits output for a case whose `case_status` is not `activated`.
- The motor emits output without a matching phase contract or with a contract that does not authorize one of the four output classes.
- Any accepted evidence reference lacks `provenance_ref` or `lineage_ref`, or any emitted output drops those references.
- A malformed input produces a partial analytical output instead of a structured rejection.
- A synthetic-only case receives `inference_state = "bounded_inference"` or a `required_evidence_level` stronger than the documented evidence supports.
- Conflicting source references are collapsed into a single stronger inference without a `Tension` and validation agenda item.
- The motor creates final reports, output blocks, rendered views, verified claims, field evidence, source ingestion records, or mutated upstream objects.
- Re-running the same canonical input changes stable identifiers, deterministic decision trace, inference state, gap categories, validation targets, or `version_hash` after runtime-only timestamp fields are excluded.
