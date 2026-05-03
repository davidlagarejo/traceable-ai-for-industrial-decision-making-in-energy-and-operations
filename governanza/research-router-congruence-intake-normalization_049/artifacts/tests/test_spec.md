# Test Spec — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## happy_path
Input:
- bounded operating-asset case with `target_classification_object.target_type = OPERATING_ASSET`;
- commercial building or similar target with public source context plus local operator evidence such as utility bills, lease matrix, BMS trends, CMMS, and operator input;
- `enriched_data.extended_sources.records` populated for at least boundary- and maintenance-relevant local source families.

Expected output:
- `selected_asset_family` resolves to the correct family for the case;
- `research_mode = operator_integrated_congruence` when operator-integrated source families are observed;
- `operational_bounding_scorecard.evidence_mode_state = operator_integrated_congruence`;
- `control_boundary_pack`, `lease_responsibility_pack`, `metering_boundary_pack`, `maintenance_maturity_pack`, and other relevant packs reach `partially_evidenced` or `evidenced` as appropriate;
- `local_evidence_binding_register` upgrades the relevant claim rows from public-only to `partially_bound` or `sufficiently_bound`;
- `promotion_blocker_register` is empty or materially reduced once the necessary core packs are satisfied.

## sparse_case
Input:
- bounded public-only building case with only public source families like assessor, benchmarking, or property records;
- no structured-local intake, no raw-local intake, and no `extended_sources.records`.

Expected behavior:
- the motor still emits a full canonical bundle, including all ten diligence packs;
- `research_mode = public_only_screening`;
- `evidence_mode_state = public_only_screening`;
- `utility_bill_pack`, `lease_responsibility_pack`, `metering_boundary_pack`, and other local packs remain in `requested_but_absent` or `public_context_only`;
- `local_evidence_binding_register` remains screening-only and does not fabricate local truth;
- dynamic intake, gap taxonomy, and blockers point clearly to the next missing evidence rather than pretending the case is already operator-integrated.

## malformed_input
Malformed or weak input examples:
- `motor_028.source_register` absent or empty while the case is still bounded enough to emit a public-only screening bundle.
- `facility_prior` missing, forcing target-definition fallback from `motor_007` or pipeline context.
- `extended_sources` present but without usable `records`, meaning a source family exists but the pack cannot truthfully be marked `evidenced`.
- source rows that conflict across high-authority domains or point to a foreign asset relative to the target definition.

Expected behavior:
- the motor does not crash on empty or sparse source collections;
- pack states degrade conservatively instead of overpromoting;
- unresolved authority conflicts or foreign-asset conflicts are surfaced in `source_conflict_register`, `entity_conflict_register`, and `promotion_blocker_register`;
- the motor never equates source-family presence with sufficient local binding when parsed records are missing.

## edge_cases
- Manufacturing hybrid case: utility bills, tariff, equipment inventory, schedule, maintenance contract, and permit record are present. Expected result: `research_mode = hybrid_diligence`, multiple packs `partially_evidenced`, and scorecard promotion to hybrid but not yet operator-integrated.
- Weak warehouse candidate with `REGISTERED_AGENT_OR_MAILING_ADDRESS`. Expected result: `route_state = target_not_yet_operationally_bounded`, `evidence_mode_state = public_only_screening`, and blocker `asset_not_operationally_bounded`.
- Unresolved high-authority tariff conflict between utility bill and utility tariff. Expected result: conflict register row with critical severity and blocker `unresolved_source_authority_conflict`.
- Raw-local-only or structured-local-only positive paths. Expected result: the merged source universe still allows `operator_integrated_congruence` when the required packs and binding bases are genuinely satisfied.

## pass_criteria
- Output includes the research-family layer, merged-source governance layer, entity-resolution layer, canonical `operational_intake_pack`, local-binding layer, dynamic-intake layer, gap-taxonomy layer, and operational-bounding layer.
- `diligence_pack_register` contains all ten canonical pack names and stays synchronized with the states of the corresponding individual packs.
- `research_mode` reflects observed source-family posture, while `evidence_mode_state` reflects scorecard truth; the two must be consistent but not conflated.
- `local_evidence_binding_register`, `binding_upgrade_register`, and `local_truth_confidence_register` only upgrade claims when there is real basis in packs or extracted local-evidence registers.
- Blockers, questions, and gaps remain explicit, machine-readable, and linked to the missing evidence that would actually change admissibility.

## fail_criteria
- A public-only or weakly bounded case is promoted to `hybrid_diligence` or `operator_integrated_congruence` without satisfying the scorecard thresholds.
- `diligence_pack_register` omits canonical packs or drifts out of sync with individual pack states.
- A claim reaches `partially_bound` or `sufficiently_bound` without a concrete `binding_basis`.
- Authority conflicts, foreign-asset conflicts, or missing core packs are observed but do not produce the expected blockers.
- The motor fabricates local truth, closes ROI/savings claims, or skips explicit gap / intake / blocker emission in favor of narrative inference.
