# Technical Schema — System Consistency Validator

Motor ID: motor_036

## entities

- `ConsistencyCheckRecord`
- `BlockingReasonRecord`
- `CanonicalReportState`
- `ConsistencyRegister`
- `CriticalFailureRegister`

## fields

- `consistency_register: list[ConsistencyCheckRecord]`
- `critical_failures: list[BlockingReasonRecord]`
- `blocking_reason_register: list[BlockingReasonRecord]`
- `canonical_report_state: CanonicalReportState`
- `critical_failure_count: int`
- `can_render_pdf: bool`
- `ConsistencyCheckRecord.check_id: str`
- `ConsistencyCheckRecord.passed: bool`
- `ConsistencyCheckRecord.severity: str`
- `ConsistencyCheckRecord.message: str`
- `ConsistencyCheckRecord.location: str`
- `BlockingReasonRecord.check_id: str`
- `BlockingReasonRecord.message: str`
- `BlockingReasonRecord.location: str`
- `CanonicalReportState.document_visible_type: str`
- `CanonicalReportState.canonical_asset_context_state: str`
- `CanonicalReportState.screening_supported: bool`

## relationships

- authoritative governance and render inputs from `motor_014`, `motor_016`, `motor_034` and the structural/congruence lane -> `consistency_register`
- `critical_failures` is the subset of `consistency_register` where `passed=false` and `severity=critical`
- `blocking_reason_register` mirrors the same blocking set for render-facing consumers
- `critical_failure_count == len(critical_failures)`
- `can_render_pdf == (critical_failure_count == 0)`
- `canonical_report_state` is derived from the visible report package and canonical asset-context summary, not from ad hoc local state

## identifiers

- `motor_id = motor_036`
- each row in `consistency_register` is keyed by `check_id`
- each row in `critical_failures` and `blocking_reason_register` is keyed by the corresponding failed `check_id`
- `canonical_report_state` is keyed implicitly by the current package under validation

## versioning

- this schema documents the current wrapper surface around `Motor036Adapter`
- new checks may extend `consistency_register`, but the existing top-level keys must remain stable
- downstream render gating depends on the binary `can_render_pdf` contract staying unchanged
- any change to `critical_failures` projection semantics requires explicit downstream review

## lineage

- upstream packaging lineage: `motor_016`
- upstream governance lineage: `motor_014`, `motor_034`, `motor_033`
- upstream structural and congruence lineage: `motor_037`, `motor_043`, `motor_044`, `motor_045`, `motor_046`, `motor_049`, `motor_051`, `motor_052`, `motor_053`, `motor_054`
- upstream asset/source lineage: `motor_012`, `motor_028`
- downstream lineage: PDF render gate, operator review, observability, report release controls

## input_dependencies

- `motor_016.report_package`
- `motor_014.claim_permission_register`
- `motor_014.claim_permission_summary`
- `motor_014.scenario_evidence_link_register`
- `motor_034.claim_permission_register`
- `motor_034.claim_contract_register`
- `motor_034.report_type_classifier_table`
- `motor_034.report_output_mode_classifier_table`
- `motor_034.structural_claim_permission_register`
- `motor_034.structural_output_mode_classifier_table`
- `motor_034.structural_output_mode_summary`
- `motor_034.structural_primary_promotion_gate`
- `motor_034.canonical_asset_context_summary`
- `motor_012.asset_field_register`
- `motor_012.dataset_coverage_register`
- `motor_012.declared_input_downgrade_register`
- `motor_028.source_register`
- `motor_028.search_attempt_ledger`
- `motor_033.decision_front_actions`
- `motor_033.expanded_structural_tad_action_register`
- structural and congruence registers from `motor_037`, `motor_043`, `motor_044`, `motor_045`, `motor_046`, `motor_049`, `motor_051`, `motor_052`, `motor_053`, `motor_054`

## behavioral_constraints

- every blocking reason must correspond to a failed critical check in `consistency_register`
- `can_render_pdf` may only become true when `critical_failure_count` is zero
- visible report mode, outline mode and thesis mode must remain aligned
- unresolved entity conflicts, promoted declared inputs and foreign chart assets must remain render-blocking when present
- structurally invalid peer comparison, premature hardware escalation and finance claims without physical dependency must remain render-blocking when present
- the validator may not emit repaired or invented content to make a package pass
