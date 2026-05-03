# Technical Schema — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## entities

- `DatasetCoverageRecord`
- `VariableMaturityRecord`
- `ClusterMaturityRecord`
- `ClusterReportReadinessProfile`
- `ClaimPermissionRecord`
- `StructuralClaimPermissionRecord`
- `ClaimContractRecord`
- `DecisionPermissionRecord`
- `ReportReadinessRecord`
- `ReportTypeClassifierRecord`
- `StructuralOutputModeClassifierRecord`
- `ReportOutputModeClassifierRecord`
- `CanonicalProblemFrameRecord`
- `StructuralPrimaryPromotionGate`
- `MaturitySummary`

## fields

- `produced_at: str`
- `motor_id: str`
- `target_classification_context: dict[str, Any]`
- `dataset_coverage_register: list[DatasetCoverageRecord]`
- `variable_maturity_register: list[VariableMaturityRecord]`
- `cluster_maturity_register: list[ClusterMaturityRecord]`
- `cluster_report_readiness_profile: ClusterReportReadinessProfile`
- `canonical_asset_context_summary: dict[str, Any]`
- `claim_permission_register: list[ClaimPermissionRecord]`
- `structural_claim_permission_register: list[StructuralClaimPermissionRecord]`
- `claim_contract_register: list[ClaimContractRecord]`
- `decision_permission_register: list[DecisionPermissionRecord]`
- `report_readiness_register: ReportReadinessRecord`
- `report_type_classifier_table: list[ReportTypeClassifierRecord]`
- `structural_output_mode_classifier_table: list[StructuralOutputModeClassifierRecord]`
- `structural_output_mode_summary: dict[str, Any]`
- `report_output_mode_classifier_table: list[ReportOutputModeClassifierRecord]`
- `canonical_problem_frame: CanonicalProblemFrameRecord`
- `structural_primary_promotion_gate: StructuralPrimaryPromotionGate`
- `maturity_summary: MaturitySummary`
- `DatasetCoverageRecord.dataset_key: str`
- `DatasetCoverageRecord.dataset_name: str`
- `DatasetCoverageRecord.status: str`
- `DatasetCoverageRecord.field_coverage: list[str]`
- `DatasetCoverageRecord.notes: str`
- `DatasetCoverageRecord.matched_sources: list[str]`
- `VariableMaturityRecord.variable_name: str`
- `VariableMaturityRecord.variable_family: str`
- `VariableMaturityRecord.value: Any`
- `VariableMaturityRecord.maturity_level: int | str`
- `VariableMaturityRecord.evidence_source: str`
- `VariableMaturityRecord.source_scope: str`
- `VariableMaturityRecord.authority_score: str`
- `VariableMaturityRecord.recency: str`
- `VariableMaturityRecord.uncertainty_reason: str`
- `VariableMaturityRecord.allowed_outputs: list[str]`
- `VariableMaturityRecord.prohibited_outputs: list[str]`
- `VariableMaturityRecord.upgrade_condition: str`
- `VariableMaturityRecord.downgrade_condition: str`
- `VariableMaturityRecord.decisions_unlocked: list[str]`
- `VariableMaturityRecord.dependent_claims: list[str]`
- `ClaimPermissionRecord.claim_name: str`
- `ClaimPermissionRecord.required_variables: list[str]`
- `ClaimPermissionRecord.minimum_maturity_level: int | str`
- `ClaimPermissionRecord.current_permission: str`
- `ClaimPermissionRecord.reason_if_blocked: str`
- `ClaimPermissionRecord.required_evidence: list[str]`
- `ClaimPermissionRecord.dependency_variables: list[str]`
- `ClaimPermissionRecord.upgrade_path: str`
- `DecisionPermissionRecord.decision_name: str`
- `DecisionPermissionRecord.required_variables: list[str]`
- `DecisionPermissionRecord.current_variable_bottleneck: str`
- `DecisionPermissionRecord.admissibility_state: str`
- `DecisionPermissionRecord.evidence_needed: list[str]`
- `DecisionPermissionRecord.allowed_action: str`
- `ClusterMaturityRecord.cluster_name: str`
- `ClusterMaturityRecord.maturity_level: int | str`
- `ClusterMaturityRecord.evidence: list[str]`
- `ClusterMaturityRecord.source: list[str]`
- `ClusterMaturityRecord.consequence: str`
- `ReportReadinessRecord.minimum_evidence_missing: list[str]`
- `ReportReadinessRecord.next_evidence_pack: list[str]`
- `ReportReadinessRecord.reason: str`
- `ReportReadinessRecord.report_type_allowed: list[str]`
- `ReportReadinessRecord.report_type_prohibited: list[str]`
- `CanonicalProblemFrameRecord.congruence_binding_state: str`
- `CanonicalProblemFrameRecord.dominant_conflict: str`
- `CanonicalProblemFrameRecord.dominant_variables: list[str]`
- `CanonicalProblemFrameRecord.evidence_state: str`
- `CanonicalProblemFrameRecord.leading_structural_output_mode: str`
- `CanonicalProblemFrameRecord.minimum_evidence_source: str`
- `CanonicalProblemFrameRecord.minimum_evidence_to_discriminate: str`
- `CanonicalProblemFrameRecord.minimum_evidence_unlocks: str`
- `CanonicalProblemFrameRecord.problem_frame_active: bool`
- `CanonicalProblemFrameRecord.reasoning_path: str`
- `CanonicalProblemFrameRecord.reframed_problem: str`
- `CanonicalProblemFrameRecord.stated_problem: str`
- `CanonicalProblemFrameRecord.target: str`
- `StructuralClaimPermissionRecord.claim: str`
- `StructuralClaimPermissionRecord.permission: str`
- `StructuralClaimPermissionRecord.evidence_required: list[str]`
- `StructuralClaimPermissionRecord.current_evidence: list[str]`
- `StructuralClaimPermissionRecord.allowed_language: list[str]`
- `StructuralClaimPermissionRecord.forbidden_language: list[str]`
- `StructuralOutputModeClassifierRecord.asset: str`
- `StructuralOutputModeClassifierRecord.recommended_output_mode: str`
- `StructuralOutputModeClassifierRecord.activation_state: str`
- `StructuralOutputModeClassifierRecord.activation_reason: str`
- `StructuralOutputModeClassifierRecord.required_claims: list[str]`
- `StructuralOutputModeClassifierRecord.primary_report_type_guard: str`
- `StructuralOutputModeClassifierRecord.why: str`
- `StructuralOutputModeClassifierRecord.primary_promotion_state: str`
- `StructuralOutputModeClassifierRecord.primary_promotion_reason: str`
- `ReportOutputModeClassifierRecord.asset: str`
- `ReportOutputModeClassifierRecord.canonical_output_mode: str`
- `ReportOutputModeClassifierRecord.visible_output_mode: str`
- `ReportOutputModeClassifierRecord.lane: str`
- `ReportOutputModeClassifierRecord.classification_state: str`
- `ReportOutputModeClassifierRecord.selected_for_publication: bool`
- `ReportOutputModeClassifierRecord.primary_eligible: bool`
- `ReportOutputModeClassifierRecord.request_basis: str`
- `ReportOutputModeClassifierRecord.requested_structural_primary_mode: str`
- `ReportOutputModeClassifierRecord.default_reasoning_path: str`
- `ReportOutputModeClassifierRecord.problem_frame_active: bool`
- `ReportOutputModeClassifierRecord.selection_basis: str`
- `ReportOutputModeClassifierRecord.why: str`
- `ReportOutputModeClassifierRecord.allowed_claims: list[str]`
- `ReportOutputModeClassifierRecord.blocked_claims: list[str]`
- `ReportOutputModeClassifierRecord.required_claims: list[str]`
- `ReportOutputModeClassifierRecord.activation_state: str`
- `ReportOutputModeClassifierRecord.primary_promotion_state: str`
- `MaturitySummary.counts_by_level: dict[str, int]`
- `MaturitySummary.key_bottlenecks: list[str]`
- `MaturitySummary.cluster_levels: dict[str, Any]`
- `MaturitySummary.screening_ready_clusters: list[str]`
- `MaturitySummary.nyc_domain_pack_active: bool`
- `MaturitySummary.allowed_report_types: list[str]`
- `MaturitySummary.prohibited_report_types: list[str]`
- `MaturitySummary.canonical_asset_context_state: str`
- `MaturitySummary.canonical_missing_clusters: list[str]`
- `MaturitySummary.canonical_supported_clusters: list[str]`
- `MaturitySummary.structural_claim_permission_count: int`
- `MaturitySummary.claim_contract_count: int`
- `MaturitySummary.structural_output_mode_count: int`
- `MaturitySummary.report_output_mode_classifier_count: int`
- `MaturitySummary.structural_output_mode_activation_count: int`
- `MaturitySummary.structural_output_mode_primary_eligibility_count: int`
- `MaturitySummary.canonical_problem_frame_active: bool`
- `MaturitySummary.structural_primary_promotion_state: str`

## relationships

- `motor_012.asset_field_register` + `motor_028.source_register` + optional `motor_035` domain packs -> `dataset_coverage_register` and `variable_maturity_register`
- `variable_maturity_register` -> `cluster_maturity_register` -> `cluster_report_readiness_profile`
- `variable_maturity_register` + jurisdiction context -> `claim_permission_register`
- `claim_permission_register` + classification context -> `decision_permission_register`
- `claim_permission_register` + missing evidence + requested report type + substrate readiness -> `report_readiness_register`
- structural inputs from `motor_038`, `motor_040`, `motor_041`, `motor_042`, `motor_043`, `motor_044`, `motor_045`, `motor_046`, `motor_049`, `motor_051` -> `structural_claim_permission_register`, `claim_contract_register`, `structural_output_mode_classifier_table`, `canonical_problem_frame`, `structural_primary_promotion_gate`
- `report_readiness_register` + structural promotion surfaces -> `report_type_classifier_table` and `report_output_mode_classifier_table`
- `maturity_summary` is a compressed roll-up of the registers above and must remain derivable from them

## identifiers

- `motor_id = motor_034`
- variable rows are logically keyed by `variable_name`
- claim rows are logically keyed by `claim_name`
- decision rows are logically keyed by `decision_name`
- cluster rows are logically keyed by `cluster_name`
- dataset rows are logically keyed by `dataset_key`
- report classifier rows are logically keyed by the chosen asset or output mode identity

## versioning

- this schema documents the current runtime wrapper surface around `Motor034Adapter`
- additions may extend row payloads, but must preserve the top-level keys listed above
- downstream consumers depend on the presence of maturity, claim, decision and report-classifier surfaces together
- any change to canonical problem-frame keys or classifier row keys requires a downstream compatibility review

## lineage

- upstream core lineage: `motor_007`, `motor_012`, `motor_028`
- upstream structural lineage: `motor_035`, `motor_037`, `motor_038`, `motor_039`, `motor_040`, `motor_041`, `motor_042`, `motor_043`, `motor_044`, `motor_045`, `motor_046`, `motor_049`, `motor_051`
- downstream lineage: report selection, synthesis, claim governance, dashboarding and output packaging
- lineage intent: every allowed claim and recommended report must be traceable back to the evidence and maturity state that justified it

## input_dependencies

- target definition and classification contract from `motor_007`
- asset field register, missing evidence and compliance applicability from `motor_012`
- source register and optional dataset coverage from `motor_028`
- optional public routing enrichment from `motor_035`
- optional structural lane registers from `motor_037` through `motor_046`, plus congruence context from `motor_049` and `motor_051`

## behavioral_constraints

- `counts_by_level` must reconcile with the emitted `variable_maturity_register`
- `allowed_report_types` and `prohibited_report_types` must match `report_readiness_register`
- declared-input fields may not exceed the configured maturity ceiling
- NYC-only regulatory claims may not appear outside NYC scope
- dataset acceptance may not upgrade an unobserved blocking field into a confirmed strong system value
- structural output-mode activation must not bypass blocked claim permissions
- if `canonical_problem_frame.problem_frame_active` is true, the structural reasoning path must still remain consistent with the emitted promotion gate
