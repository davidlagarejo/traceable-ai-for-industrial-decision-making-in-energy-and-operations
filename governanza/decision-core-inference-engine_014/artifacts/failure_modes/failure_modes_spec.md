# Failure Modes Spec — Decision Core / Inference Engine

Motor ID: motor_014

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
why_it_exists:  Es el corazón analítico de Fase 2.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001)
key_outputs:    inference_record, tension_record, gap_agenda, validation_agenda
key_objects:    InferenceRecord, Tension, ValidationAgenda
what_not_to_do: No produce reportes finales. No verifica claims. Solo infiere y registra con contratos explícitos.
design_notes:   Determinismo primero. La IA puede asistir pero no decide. Depende de motor_013 y motor_001.

All placeholder markers in this artifact have been replaced with stage-specific content.
-->

## failure_modes_list
- `CONTRACT_BYPASS`: matching `PhaseContract` is absent, does not allow `inference_cases`, or omits one of `inference_record`, `tension_record`, `gap_agenda`, or `validation_agenda` from `allowed_outputs` -> the motor emits analytical output outside the phase boundary or with an empty `phase_contract_ref` / `contract_version` -> reject the whole request with `PHASE_CONTRACT_MISSING` or `PHASE_CONTRACT_VIOLATION`, emit no partial outputs, and require a corrected contract from `motor_001`.
- `UNACTIVATED_CASE_PROCESSING`: an input case has `case_status` other than `activated`, lacks `activation_record_ref`, or lacks `trigger_log_ref` from `motor_013` -> an `InferenceRecord` is created for a draft, rejected, or ungoverned case -> reject with `INFERENCE_CASE_NOT_ACTIVATED`, preserve the input in diagnostics only, and require activation through `motor_013` before reprocessing.
- `PROVENANCE_LINEAGE_LOSS`: any accepted `EvidenceRef` or emitted top-level record lacks `provenance_ref`, `lineage_ref`, `lineage_refs`, `rule_version`, `source_ref`, `produced_by_motor`, `produced_at`, `version_id`, or `version_hash` -> downstream reconstruction cannot prove which case, evidence, contract, or deterministic rule produced the result -> reject with `PROVENANCE_REQUIRED` before emission, or quarantine the emitted batch if loss is detected after serialization.
- `SYNTHETIC_EVIDENCE_PROMOTION`: a case containing only `source_class = synthetic_support` or `evidence_level = synthetic` is assigned `bounded_inference`, `validation_data`, or `field_evidence` treatment -> synthetic support contaminates the evidentiary chain and may be consumed as decision-grade support downstream -> force `InferenceRecord.inference_state = hypothesis_only`, set `synthetic_support_present = true`, create a gap requesting `validation_data` or `field_evidence`, and block any stronger state until real evidence is present.
- `CONFLICT_COLLAPSE`: evidence references, trigger signals, or contract constraints conflict but deterministic rules choose a single stronger inference without creating a `Tension` -> `tension_record` is empty while source references point to incompatible conditions, and no validation item exists for the unresolved conflict -> emit `Tension.tension_type = conflict` or `inconsistency`, create a `GapItem.gap_type = unresolved_conflict`, and route a `ValidationItem` through the contract-authorized handoff target.
- `GAP_SUPPRESSION`: sparse contextual evidence, missing validation data, or contract-limited scope is treated as a complete inference with empty `gap_items` and empty `validation_items` -> downstream motors receive an inference that appears complete although required evidence is absent -> downgrade state to `blocked_by_gap` or `hypothesis_only`, create a concrete `GapItem.missing_condition`, and emit a validation agenda item with required evidence level and handoff target.
- `REPORTING_OR_VERIFICATION_LEAKAGE`: implementation adds report blocks, executive summaries, rendered views, verified claim flags, field evidence objects, or verification outcomes to the output payload -> `motor_014` starts performing `motor_015`, `motor_016`, `motor_018`, or `motor_019` responsibilities -> reject unknown output classes, strip no fields silently, fail conformance, and keep the payload limited to `inference_record`, `tension_record`, `gap_agenda`, and `validation_agenda`.
- `NONDETERMINISTIC_DECISION_TRACE`: stable canonical inputs, same `rule_version`, same `contract_version`, same parent reference, and same lineage set produce different identifiers, inference states, gap categories, validation targets, or `version_hash` values after excluding runtime timestamps -> reruns cannot be compared or reconstructed reliably -> canonicalize input ordering, derive IDs from stable parents and deterministic ordinals, and fail deterministic rerun tests before accepting implementation.

## anti_patterns
- Direct coupling to downstream rendering, report package assembly, verification, or field evidence collection modules; this motor must emit structured inferential handoff objects, not downstream products.
- Treating `phase_contracts` as advisory metadata instead of hard authorization for accepted inputs, allowed outputs, handoff targets, and output limits.
- Accepting raw source material, analyst notes, unactivated ideas, or library records directly as cases instead of requiring `InferenceCase` objects activated by `motor_013`.
- Using an LLM, scoring prompt, or free-text rationale as the final authority for `inference_state`, severity, conflict resolution, or validation need.
- Mutating upstream `inference_cases`, `phase_contracts`, evidence records, validation data, provenance, or lineage to make the current inference easier to emit.
- Collapsing `Tension`, `GapAgenda`, and `ValidationAgenda` into optional narrative fields on `InferenceRecord`; each object has a distinct contract and downstream use.
- Inferring missing provenance, lineage, evidence level, or handoff target from naming conventions instead of requiring explicit fields.
- Using list position or current timestamp as the primary basis for stable identifiers or `version_hash`, causing reruns to drift.
- Treating empty `gap_items` or empty `validation_items` as proof that a claim is verified; this motor never verifies claims.
- Adding "confidence" or "decision-grade" labels that are not authorized by the schema and phase contract.

## degradation_signals
- Increase in `PHASE_CONTRACT_MISSING` or `PHASE_CONTRACT_VIOLATION` rejections, especially after contract version changes, indicating phase boundary drift.
- Any emitted top-level record with missing or empty `phase_contract_ref`, `contract_version`, `rule_version`, `lineage_refs`, `source_ref`, `produced_by_motor`, `produced_at`, `version_id`, or `version_hash`.
- `bounded_inference` rate rises while average evidence count, validation-data count, or field-evidence count does not rise, indicating possible evidence promotion.
- Synthetic-only cases appear in logs with `inference_state != hypothesis_only`, `required_evidence_level = field_evidence` without a gap, or `synthetic_support_present = false`.
- Tension rate approaches zero while input batches contain contradictory evidence classes, conflicting source references, or case signals tagged as conflict/inconsistency.
- Gap agenda count or validation item count drops sharply while sparse contextual-evidence cases continue to be accepted.
- Unknown output keys or classes appear in serialized payloads, especially report blocks, final claim fields, rendered views, verification flags, or field evidence objects.
- Deterministic rerun checks produce changed `inference_id`, `decision_trace`, `gap_type`, `handoff_target`, or `version_hash` for the same canonical input.
- Repeated identical `ValidationAgenda.validation_items` across unrelated cases, suggesting template copying instead of case-specific gap derivation.
- Logs show fallback defaults such as `unknown_contract`, `missing_lineage`, `auto_provenance`, `default_handoff`, or `llm_decided_state`.

## expensive_errors
- Emitting records without reconstructible lineage is expensive because downstream output blocks, validation plans, and re-evaluation runs cannot prove what produced an inference. Prevent it by blocking emission on missing provenance or lineage and by requiring all top-level versioning and lineage fields before serialization.
- Promoting synthetic or contextual support into stronger evidence is expensive because it can contaminate downstream validation, reporting, and governance decisions with non-evidentiary material. Prevent it by enforcing source-class and evidence-level rules before state assignment and by forcing synthetic-only cases to `hypothesis_only`.
- Processing unactivated cases is expensive because ungoverned analytical ideas can enter Fase 2 and later appear indistinguishable from authorized inference cases. Prevent it by requiring `case_status = activated`, `activation_record_ref`, and `trigger_log_ref` for every accepted case.
- Emitting outputs outside the phase contract is expensive because consumers may build dependencies on objects that the phase never authorized. Prevent it by validating `allowed_inputs`, `allowed_outputs`, `handoff_rules`, and `output_limits` before any inference logic runs.
- Silently resolving conflicts is expensive because the lost tension cannot be reconstructed once downstream validation or reporting has consumed the stronger inference. Prevent it by requiring every conflicting source set to create a `Tension`, an unresolved-conflict gap, and a validation item when the contract authorizes handoff.
- Letting identifiers or hashes depend on runtime ordering or timestamps is expensive because historical comparisons, supersession, and deterministic reprocessing become unreliable. Prevent it by canonicalizing inputs and deriving identifiers and hashes from stable IDs, rule version, contract version, content, lineage, and parent reference.
- Mixing report generation or verification into this codebase is expensive because later separation into `motor_015`, `motor_016`, `motor_018`, or `motor_019` would require untangling persisted outputs and consumer assumptions. Prevent it by rejecting unknown output classes and keeping this motor limited to inferential records and validation handoffs.
