# Failure Modes Spec — System Consistency Validator

Motor ID: motor_036

## failure_modes_list

- `REPORT_MODE_DRIFT`
- `CLAIM_TRACE_GAP`
- `SUMMARY_MATRIX_MISMATCH`
- `BODY_SECTION_LEAKAGE`
- `OUTPUT_MODE_CLASSIFIER_INCOMPLETE`
- `DECLARED_INPUT_OVERPROMOTION`
- `ENTITY_CONFLICT_UNRESOLVED`
- `FOREIGN_CASE_ASSET_CONTAMINATION`
- `INVALID_COMPARISON_AS_FACT`
- `PREMATURE_HARDWARE_ESCALATION`
- `FINANCE_WITHOUT_PHYSICS_DEPENDENCY`
- `CHAPTER_INVENTORY_TEMPLATE_CONTAMINATION`

## anti_patterns

- treating the validator as cosmetic QA instead of a hard render gate;
- fixing the visible report while ignoring the authoritative registers;
- suppressing a critical check instead of restoring upstream coherence;
- letting strong surface language stand because the package "looks finished".

## degradation_signals

- many checks still pass, but one family of critical checks repeatedly fails for every package;
- render succeeds while claim summaries and matrices disagree;
- foreign charts or declared input stop triggering blocks;
- body sections slowly accumulate appendix-grade content.

## expensive_errors

- shipping a polished report that contradicts its own evidence or claim permissions;
- rendering the wrong case or the wrong target identity;
- letting bounded structural hypotheses be interpreted as decision-grade fact;
- losing the final integrity gate between runtime truth and delivered artifact.
