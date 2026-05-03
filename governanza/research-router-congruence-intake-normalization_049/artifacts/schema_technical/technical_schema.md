# Technical Schema — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## entities
- `AssetFamilyResearchProfile`: primary routing profile for the case. It names the selected asset family, route state, observed research mode, authoritative source families, and family-typical process / subsystem / loss / measurement expectations.
- `AssetFamilyResearchDossier`: versioned library snapshot for the selected asset family. It is emitted from the congruence research library and acts as the stable family-level seed for downstream congruence logic.
- `SourceGovernanceRegister`: family of source-normalization outputs built after merging public, structured-local, and raw-local sources. It includes `structured_local_source_register`, `raw_local_source_register`, `authority_precedence_register`, `source_conflict_register`, and `conflict_resolution_outcome_register`.
- `EntityResolutionRegister`: family of identity-and-boundary outputs describing asset-name resolution, owner/operator/tenant resolution, asset-boundary status, and the derived `entity_resolution_state`.
- `OperationalIntakePack`: canonical intake envelope for the case. It combines asset identity, process/subsystem seeds, finance/control/maintenance packs, and the ten canonical diligence packs used for promotion logic.
- `DiligencePack`: one canonical local-evidence pack such as `utility_bill_pack`, `metering_boundary_pack`, `lease_responsibility_pack`, `cmms_or_workorder_pack`, or `permit_detail_pack`.
- `LocalEvidenceBindingRecord`: one claim-specific local-binding row stating what research claim exists, what local evidence is still needed, what limited uses are allowed if unbound, the current binding state, and the concrete basis for any upgrade.
- `OperationalBoundingScorecard`: promotion gate object that converts pack coverage and bounded asset identity into `public_only_screening`, `hybrid_diligence`, or `operator_integrated_congruence`.
- `PromotionBlocker`: explicit blocker row preventing promotion when identity, source conflict, pack coverage, or operator evidence is still inadequate.
- `DynamicIntakeQuestion`: one discriminating operator-intake question emitted to close a concrete evidence gap, together with who must answer it and what rival hypotheses it discriminates.
- `GapTaxonomyEntry`: one structured gap row created from dynamic intake questions or blockers, expressing gap class, next action type, blocked claims, linked needs, and linked diligence packs.

## fields
`AssetFamilyResearchProfile`
- `asset_family: str` (required) — normalized family such as `commercial_building`, `industrial_manufacturing`, `logistics_warehouse`, `cold_chain`, `utility_heavy_site`, or `infrastructure_node`.
- `route_state: str` (required) — `operational_asset_candidate`, `target_not_yet_operationally_bounded`, or `target_unresolved`.
- `research_mode: str` (required) — observed mode inferred from present source families: `public_only_screening`, `hybrid_diligence`, or `operator_integrated_congruence`.
- `target_type_hint: str` (required)
- `authoritative_source_families: list[str]` (required)
- `rejected_source_families: list[str]` (required)
- `typical_processes: list[str]` (required)
- `typical_subsystems: list[str]` (required)
- `typical_loss_patterns: list[str]` (required)
- `typical_regulatory_signals: list[str]` (required)
- `typical_measurement_paths: list[str]` (required)
- `typical_invalid_comparisons: list[str]` (required)
- `jurisdiction_scope: list[str]` (required)

`AssetFamilyResearchDossier`
- `asset_family: str` (required)
- `productization_state: str` (required) — expected to be `versioned_seeded_dossier` for library-backed families.
- `research_library_version: str` (required)
- `valid_normalization_bases: list[str]` (required)
- `minimum_local_evidence_classes: list[str]` (required)
- additional family-specific dossier content is allowed, but must remain subordinate to the selected asset family.

`SourceGovernanceRegister`
- `structured_local_source_register: list[dict]` (required) — sources emitted from structured intake.
- `raw_local_source_register: list[dict]` (required) — sources emitted from raw document / text intake.
- `authority_precedence_register: list[dict]` (required) — precedence ordering across merged sources.
- `source_conflict_register: list[dict]` (required) — claim-domain or authority conflicts across sources.
- `conflict_resolution_outcome_register: list[dict]` (required) — whether a conflict resolves to a higher-precedence source or remains blocking.
- `augmented_source_register_count: int` (required)
- `structured_local_source_count: int` (required)
- `raw_local_source_count: int` (required)

`EntityResolutionRegister`
- `entity_resolution_register: list[dict]` (required)
- `entity_conflict_register: list[dict]` (required)
- `asset_boundary_resolution_register: list[dict]` (required)
- `owner_operator_tenant_resolution_register: list[dict]` (required)
- `entity_resolution_state: str` (required) — bounded summary such as `resolved`, `partially_resolved`, or `critical_conflict`.

`OperationalIntakePack`
- `asset_family: str` (required)
- `research_mode: str` (required)
- `asset_identity_pack: dict` (required) — contains `target_name`, `target_identifier`, `target_type`, `jurisdiction_scope`, `classification_state`, and `classification_confidence`.
- `process_overview_pack: dict` (required)
- `subsystem_inventory_pack: dict` (required)
- `equipment_dominance_pack: dict` (required)
- `schedule_and_utilization_pack: dict` (required)
- `control_boundary_pack: dict` (required)
- `maintenance_maturity_pack: dict` (required)
- `measurement_and_metering_pack: dict` (required)
- `utility_and_tariff_pack: dict` (required)
- `regulatory_and_permit_pack: dict` (required)
- `finance_driver_pack: dict` (required)
- `logistics_pack: dict` (required)
- `procurement_pack: dict` (required)
- `culture_execution_pack: dict` (required)
- `climate_location_pack: dict` (required)
- `diligence_pack_register: list[dict]` (required)
- `diligence_pack_state_summary: dict` (required)

`DiligencePack`
- `pack_name: str` (required) — one of the canonical names in `DILIGENCE_PACK_NAMES`.
- `current_state: str` (required) — expected values include `not_primary`, `public_context_only`, `requested_but_absent`, `partially_evidenced`, or `evidenced`.
- `decision_relevance: str` (required)
- `expected_local_sources: list[str]` (required)
- `present_source_families: list[str]` (required)
- `binding_needed: list[str]` (required)
- `family_specific_focus: str` (required)
- `allowed_without_local_binding: list[str]` (required)

`LocalEvidenceBindingRecord`
- `claim_key: str` (required) — stable claim identifier such as `commercial_building_control_boundary` or `logistics_service_complexity`.
- `research_claim: str` (required)
- `local_binding_needed: list[str]` (required)
- `if_unbound_then_only_allow: list[str]` (required)
- `current_local_binding_state: str` (required) — states include `inadmissible_until_asset_identity_bounded`, `public_context_only_unbound`, `partially_bound`, and `sufficiently_bound`.
- `binding_basis: list[str]` (required)
- `binding_sufficiency_reason: str` (required)

`OperationalBoundingScorecard`
- `asset_family: str` (required)
- `route_state: str` (required)
- `research_mode_observed: str` (required)
- `bounded_asset_gate_passed: bool` (required)
- `evidence_mode_state: str` (required)
- `next_promotable_mode: str` (required)
- `hybrid_core_packs: list[str]` (required)
- `operator_core_packs: list[str]` (required)
- `hybrid_hits: list[str]` (required)
- `operator_hits: list[str]` (required)
- `hybrid_score: int` (required)
- `operator_score: int` (required)
- `required_hybrid_count: int` (required)
- `required_operator_count: int` (required)
- `score_explanation: str` (required)

`PromotionBlocker`
- `blocker_code: str` (required)
- `severity: str` (required)
- `blocks_mode: str` (required)
- `conflict_domain: str` (optional in some blockers)
- `why: str` (required)

`DynamicIntakeQuestion`
- `question_id: str` (required)
- `need_ids: list[str]` (required)
- `pack_names: list[str]` (required)
- `priority: str` (required)
- `required_from: str` (required)
- `intake_question: str` (required)
- `why_needed: str` (required)
- `hypothesis_it_discriminates: str` (required)
- `rival_hypotheses: list[str]` (required)
- `claim_impact_if_missing: str` (required)
- `priority_score: int` (derived, required in ranked output)

`GapTaxonomyEntry`
- `gap_id: str` (required)
- `gap_class: str` (required)
- `source_type: str` (required)
- `source_id: str` (required)
- `why_blocked: str` (required)
- `evidence_needed: list[str]` (required)
- `next_action_type: str` (required)
- `blocked_claims: list[str]` (required)
- `linked_need_ids: list[str]` (required)
- `linked_pack_names: list[str]` (required)

## relationships
- `AssetFamilyResearchProfile.asset_family` selects exactly one `AssetFamilyResearchDossier`.
- `SourceGovernanceRegister` is built only after merging public, structured-local, and raw-local sources into one augmented source universe.
- `EntityResolutionRegister` consumes the merged source universe plus target definition to derive owner/operator/tenant and boundary status.
- `OperationalIntakePack.diligence_pack_register[]` contains exactly the canonical `DiligencePack` rows for the current case.
- `LocalEvidenceBindingRecord` depends on `AssetFamilyResearchProfile`, target classification, pack states, and extracted local-evidence registers such as control-boundary, maintenance, utility, tariff, and responsibility registers.
- `OperationalBoundingScorecard` reads `AssetFamilyResearchProfile.route_state` plus the canonical pack states in `OperationalIntakePack` to compute `evidence_mode_state`.
- `PromotionBlocker` rows can be produced from asset-boundary failure, missing hybrid/operator core packs, or unresolved high-authority source conflicts.
- `DynamicIntakeQuestion.pack_names[]` and `need_ids[]` must point to the specific diligence packs and discovery needs whose absence blocks bounded congruence.
- `GapTaxonomyEntry` is built from either `DynamicIntakeQuestion` or `PromotionBlocker`, and its `blocked_claims` feed later congruence and comparison governors.

## identifiers
- `case_fingerprint` is the stable runtime identity of the case as seen by this motor.
- `asset_family` is the canonical selector for research-library routing and dossier lookup.
- `pack_name` is the canonical identifier for each diligence pack and must remain within `DILIGENCE_PACK_NAMES`.
- `claim_key` is the canonical identifier for each local-binding claim row.
- `question_id` is the canonical identifier for each dynamic intake question and is reused by `required_from_register`, `intake_priority_register`, `claim_impact_register`, and `gap_taxonomy_register`.
- `gap_id` is the canonical identifier for each gap row; it is usually a `question_id` or `blocker_code`.
- `source_id` remains the stable identifier of merged source rows; this motor does not re-mint source IDs for already identified evidence.

## versioning
- Unlike earlier motors, this motor does emit one explicit version anchor in runtime output: `research_library_version`, which versions the family-dossier layer.
- Most other emitted objects are recomputed dicts and lists rather than versioned records; they do not currently expose `version_id`, `version_hash`, or `parent_id`.
- Stable identity therefore comes from the tuple of `case_fingerprint`, `research_library_version`, canonical `pack_name` / `claim_key` / `question_id` keys, and the merged source universe.
- Material changes to family dossiers, pack libraries, local-binding templates, dynamic-intake question libraries, or operational-bounding thresholds must be treated as schema-significant even when output keys stay the same.
- `OperationalBoundingScorecard` and `LocalEvidenceBindingRecord` are deterministic for the same target context, merged sources, and family-library state.

## lineage
- The motor’s lineage begins with `target_definition`, `target_classification_object`, `facility_prior`, `asset_field_register`, and all upstream search/discovery registers from `motor_007`, `motor_012`, and `motor_028`.
- `SourceGovernanceRegister` preserves lineage by keeping public, structured-local, and raw-local sources visible as separate but merged components before conflicts are resolved.
- `authority_precedence_register`, `source_conflict_register`, and `conflict_resolution_outcome_register` preserve why one source can dominate another or why a conflict remains blocking.
- `EntityResolutionRegister` preserves lineage from source-level name/role claims into bounded asset, owner, operator, and tenant conclusions.
- `LocalEvidenceBindingRecord.binding_basis` is the primary lineage surface for any upgrade from screening-only to partially or sufficiently bound local truth.
- `DynamicIntakeQuestion`, `required_from_register`, and `GapTaxonomyEntry` preserve the lineage from missing evidence to concrete next-action requests rather than letting gaps remain implicit.
- `OperationalBoundingScorecard.score_explanation` preserves the lineage from pack coverage and route state to the final `evidence_mode_state`.
