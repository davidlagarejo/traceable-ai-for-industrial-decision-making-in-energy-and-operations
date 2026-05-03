# Failure Modes Spec — Epistemic Governance Layer

Motor ID: motor_025

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar tensiones estructurales, inflación de excepciones, insuficiencia taxonómica y distinguir cambio local, estructural o constitucional.
why_it_exists:  Evita que el framework crezca rompiendo su constitución en silencio.
key_inputs:     conformance_records (motor_022), governance_events (motor_024), phase_contracts (motor_001)
key_outputs:    epistemic_tension_record, constitutional_change_signal, governance_health_report
key_objects:    EpistemicTension, ConstitutionalSignal, GovernanceHealthReport
what_not_to_do: No modifica contratos ni políticas directamente. Solo detecta y señaliza tensiones estructurales.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Capa de gobernanza de más alto nivel.

All open content markers in this file have been resolved for Gate 4 validation.
-->

## failure_modes_list
TENSION_OVERCLASSIFICATION: isolated low-severity governance event, single conformance failure, or raw narrative explanation is treated as structural or constitutional pressure → `ConstitutionalSignal` count rises without recurrence, multi-motor scope, or authority conflict evidence → reject unsupported escalation, downgrade to local or no-signal classification, and require `classification_basis` to cite recurrence, severity, scope, or contract-authority rules.

EXCEPTION_INFLATION_BLINDNESS: three or more governance events share a valid `recurrence_key` and contract reference in the evaluation window but are processed only as independent local exceptions → `GovernanceHealthReport.exception_inflation_score` remains zero and no `EpistemicTension.tension_type="exception_inflation"` is emitted → regroup events by stable recurrence key and contract reference, re-evaluate the window, and emit one traceable tension with all evidence IDs preserved.

TAXONOMIC_GAP_COLLAPSE: structured upstream findings such as `taxonomy_gap`, `unknown_canonical_term`, or `semantic_boundary_conflict` are collapsed into generic conformance gaps → no `taxonomic_insufficiency` tension appears even though conformance evidence identifies semantic coverage failure → map only structured upstream taxonomy-gap findings to `taxonomic_insufficiency`, preserve the original finding record, and avoid creating any taxonomy term or alias.

CONSTITUTIONAL_SIGNAL_SPAM: every high-severity tension is escalated to `change_pressure="constitutional"` without documented conflict with authority hierarchy, workflow sequence, phase semantics, or contract semantics → review queue receives constitutional signals that do not identify affected contract authority or framework-level conflict → enforce the constitutional threshold before signal emission and route repeated but contract-local pressure to `structural_design_review`.

PROVENANCE_AND_LINEAGE_LOSS: aggregate health reporting drops `record_id`, `event_id`, `provenance_ref`, `lineage_ref`, or governing contract references when building tensions and reports → emitted objects cannot be reconstructed from `source_ref`, `evidence_refs`, and `governing_contract_refs` → block output production with structured rejection errors until the missing references are supplied.

AUTHORITY_SET_MISMATCH: conformance records or governance events cite contract references absent from supplied `phase_contracts` and not explicitly marked as historical versions → tensions are classified against an unknown or wrong authority boundary → reject the run with `UNKNOWN_CONTRACT_REF`, request the missing active or historical contract reference, and emit no partial outputs.

DUPLICATE_EVIDENCE_COLLAPSE: two upstream records share the same `record_id` or `event_id` with conflicting payloads and the motor silently keeps one copy → severity, recurrence, affected scope, and evidence counts become non-reproducible → reject the full run with `DUPLICATE_EVIDENCE_ID` and require upstream identity correction before re-evaluation.

## anti_patterns
- Treating `motor_025` as a policy editor that modifies phase contracts, workflow rules, governance policies, taxonomies, exception approvals, conformance decisions, or motor states.
- Coupling tension classification directly to mutable motor implementation details instead of the supplied `phase_contracts`, `conformance_records`, and `governance_events`.
- Using free-form notes, chat summaries, or LLM explanations as direct evidence for local, structural, or constitutional classification.
- Collapsing recurrence by human-readable titles instead of stable `recurrence_key`, contract reference, affected motor, and evidence ID.
- Emitting `ConstitutionalSignal` objects without first emitting traceable `EpistemicTension` records that cite non-empty `evidence_refs` and `governing_contract_refs`.
- Recomputing conformance results owned by `motor_022` or creating primary governance events owned by `motor_024`.
- Making the health report a prose-only summary instead of a deterministic aggregate with explicit counts, unresolved signal IDs, evidence coverage, and evaluated contract references.
- Allowing malformed inputs to produce partial reports while silently dropping invalid records.

## degradation_signals
- `governance_events` with valid recurring keys increase across windows while `EpistemicTension.tension_type="exception_inflation"` remains flat or zero.
- More than one `ConstitutionalSignal` in a window lacks originating tensions, affected contract references, or a rule-based `escalation_reason`.
- `GovernanceHealthReport.governance_status="stable"` appears in a window that contains high-severity repeated exception overrides or repeated conformance failures against the same contract boundary.
- `evidence_coverage.rejected_records_count` rises after new phase contracts are introduced, especially with `UNKNOWN_CONTRACT_REF` or `PROVENANCE_REQUIRED` errors.
- `exception_inflation_score` changes between rebuilds even when the canonical input records and evaluation window are unchanged.
- Tension records have empty `source_ref`, empty `governing_contract_refs`, empty `classification_basis`, or affected scopes with no motor, phase, or contract identifiers.
- Ratio of constitutional signals to structural signals rises sharply without a matching increase in documented authority-hierarchy or workflow-sequence conflicts.
- Logs show repeated malformed-input repairs, dropped evidence records, or warnings such as `partial_output_emitted_after_rejection`.

## expensive_errors
1. Silent constitutional escalation drift.
   - Why expensive: once unsupported constitutional signals enter review queues, downstream governance may spend time evaluating framework-level change requests that should have remained local or structural.
   - Prevention: require each constitutional signal to reference originating tensions, affected contract refs, and a classification basis tied to documented authority hierarchy, workflow sequence, phase semantics, or contract semantics.

2. Lost evidence lineage in aggregate reports.
   - Why expensive: a health report without `source_ref`, `evidence_refs`, and evaluated contract refs cannot be rebuilt or audited after later governance decisions rely on it.
   - Prevention: block output when upstream IDs, provenance refs, lineage refs, timestamps, or governing contract refs are missing; never summarize away the source identifiers.

3. Recurrence-key misuse.
   - Why expensive: grouping by prose labels hides repeated exceptions under multiple names or merges unrelated events, corrupting exception inflation trends across review windows.
   - Prevention: group recurrence only by stable `recurrence_key` plus contract and affected-scope checks, and reject conflicting duplicate evidence IDs before scoring.

4. Treating taxonomy gaps as generic conformance failures.
   - Why expensive: semantic coverage defects propagate into design reviews without being visible as taxonomic insufficiency, forcing later reconstruction across conformance records and governance events.
   - Prevention: preserve structured upstream taxonomy-gap findings as their own `taxonomic_insufficiency` tension type while leaving taxonomy creation to the taxonomy motor.

5. Classifying against incomplete authority.
   - Why expensive: tensions classified without the active or historical phase contract set can recommend the wrong review path and contaminate governance health history.
   - Prevention: require non-empty `phase_contracts`, resolve every asserted `contract_ref`, and reject unknown authority references before emitting any tension, signal, or report.

6. Partial output after malformed input.
   - Why expensive: partial tensions or reports from rejected runs create split-brain governance state where some downstream consumers see a failed window as if it were valid.
   - Prevention: perform validation before classification, return structured errors for malformed input, and emit no governance outputs when a blocking rejection is raised.
