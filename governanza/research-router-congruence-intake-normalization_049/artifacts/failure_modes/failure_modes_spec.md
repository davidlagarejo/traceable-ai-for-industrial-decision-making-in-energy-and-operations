# Failure Modes Spec — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## failure_modes_list
- `PUBLIC_ONLY_OVERPROMOTION`: a case with only public context or weakly bounded identity is promoted into `hybrid_diligence` or `operator_integrated_congruence` -> downstream congruence logic starts treating seed context as if local evidence had been absorbed -> keep scorecard thresholds strict and tie promotion to canonical pack states plus bounded asset identity.
- `DILIGENCE_PACK_STATE_DRIFT`: the individual pack states and `diligence_pack_register` diverge -> scorecards, blockers, dashboards, and intake questions stop talking about the same reality -> synchronize pack rows after every pack-state update and never let the register go stale.
- `SOURCE_CONFLICT_SUPPRESSION`: high-authority source conflicts or foreign-asset conflicts are detected but do not become blockers -> the case advances on contradictory or mis-scoped evidence -> preserve `source_conflict_register`, `entity_conflict_register`, and `promotion_blocker_register` as explicit outputs.
- `BINDING_UPGRADE_WITHOUT_BASIS`: a claim reaches `partially_bound` or `sufficiently_bound` without real evidence in boundary, maintenance, utility, tariff, or operator registers -> congruence outputs acquire false local truth confidence -> bind only from concrete register counts, pack states, and `extended_sources.records`.
- `QUESTION_LIBRARY_NONDISCRIMINATION`: dynamic intake questions become generic and stop discriminating rival hypotheses -> operators provide data without changing admissibility or comparison validity -> keep every question linked to pack names, need IDs, rival hypotheses, and claim impact if missing.
- `FAMILY_MISROUTING`: the selected asset family is wrong -> the wrong dossier, packs, questions, and downstream loss/comparison logic activate -> preserve family inference discipline from target context and merged source signals.

## anti_patterns
- Treating source-family presence as equivalent to parsed local evidence.
- Using `research_mode` as if it were the final evidence-mode truth instead of just observed source posture.
- Dropping blockers or conflicts to make the case look cleaner for later packaging.
- Writing one generic intake workflow for every asset family instead of using family-specific discriminating questions.
- Upgrading local-binding claims from narrative intuition rather than from explicit `binding_basis`.

## degradation_signals
- cases marked `operator_integrated_congruence` while key packs such as metering, lease, maintenance, or CMMS remain absent or merely public context;
- `partially_evidenced_pack_count` increasing without corresponding `extended_sources.records` or concrete local-source payloads;
- `binding_gap_count` collapsing to zero on obviously weak cases;
- `dynamic_intake_question_count` high but `required_from_register`, `claim_impact_register`, or `gap_taxonomy_register` too thin to support it;
- unresolved source conflicts or entity conflicts appearing in raw registers without blocker propagation;
- family selection that disagrees with the evidence family actually used in the positive-path runtime tests.

## expensive_errors
- Promoting a weak case too early. It is expensive because every downstream congruence, comparison, and claim-governor artifact inherits a false evidence posture. Prevent it with strict operational-bounding thresholds and blocker propagation.
- Losing synchronization between pack states and the diligence-pack register. It is expensive because the system becomes internally inconsistent and hard to debug. Prevent it by synchronizing the register immediately after pack-state mutation.
- Upgrading local truth confidence without real basis. It is expensive because executive outputs become epistemically unsafe even if runtime tests still pass superficially. Prevent it by making `binding_basis` the mandatory evidence bridge for every upgrade.
- Suppressing source or identity conflicts. It is expensive because later remediation requires unwinding decisions built on the wrong asset or contradictory tariff/control narratives. Prevent it by treating high-authority conflicts as first-class promotion blockers.
