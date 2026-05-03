# Canonical Output Modes Certification — Latest

Generated on: `2026-04-30`

Status: `accepted`

## Scope

This certification closes the last open tranche for the structural-intelligence expansion prompt:

- structural-first reasoning is now the default interpretation path for operating cases
- statement-level claim traces are now attached to visible report sections
- the render contract is now first-class by canonical output mode
- the system now has one final certification package across all **nine** canonical output modes

## Runtime Refresh After Structural-First Body Promotion

Fresh normal operating run:

- `One Vanderbilt`
- pipeline: `ova-2026-structural-final`
- run: `run:6781927334ea6d94`
- final published report type: `Compliance / Investment Screening Brief`
- `default_reasoning_path = structural_first`
- `structural_primary_promotion_state = structural_first_default_active`

This confirms that the framework now uses structural-first reasoning by default **without** accidentally overpromoting the visible output mode.

## Certified Canonical Output Modes

| Canonical Output Mode | Certification Basis | Evidence | Status |
|---|---|---|---|
| `Target Classification Brief` | synthetic regression fixture | `test_non_operating_address_case_does_not_overpromote_after_structural_sovereignty_shift` | `PASS` |
| `Decision-Blocked Asset Brief` | synthetic regression fixture + bounded manufacturing reasoning path | `test_structural_lane_is_default_reasoning_path_for_manufacturing_case` | `PASS` |
| `Exploratory Prior Brief` | synthetic maturity fixture | `test_partial_bounded_asset_can_resolve_to_exploratory_prior_brief` | `PASS` |
| `Compliance / Investment Screening Brief` | fresh real run + regression tests | `run:6781927334ea6d94`; `test_structural_lane_is_default_reasoning_path_for_nyc_screening_case`; `test_one_vanderbilt_expected_behavior_supports_screening_but_blocks_roi_and_closure` | `PASS` |
| `Structural Contradiction Brief` | official real structural fixture | `run:e7b00d86892eff7b` | `PASS` |
| `System Redesign Hypothesis Brief` | official real structural fixture | `run:0f03dca923d6c0e8` | `PASS` |
| `Competitive Positioning Brief` | official real structural fixture | `run:78de69709ab66030` | `PASS` |
| `TAD Action Priority Brief` | official real structural fixture | `run:edc92a97b3f0cbd3` | `PASS` |
| `Full Technical Decision Intelligence Report` | synthetic maturity fixture | `test_sufficient_technical_substrate_unlocks_full_technical_report` | `PASS` |

Interpretation:

- all nine canonical modes are now covered by either real runtime or explicit fixture certification
- the four structural-primary modes remain certified from official persisted inputs
- `Exploratory Prior Brief` and `Full Technical Decision Intelligence Report` remain intentionally certified by fixture because public-data-only runtime does not always produce those states naturally

## Statement-Level Claim Traceability

Closed in:

- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)

What is now enforced:

- visible claim-bearing sections must have statement-level traces
- traces must include `claim_id`, `evidence_state`, `supporting_sources`, `assumptions`, `falsification_condition`, `minimum_evidence_required`, `allowed_use`, and `prohibited_use`
- missing or incomplete statement traces block render

## Structural-First Render Contract

Closed in:

- [render_section_contract.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/render_section_contract.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)
- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)

What is now enforced:

- each canonical output mode has explicit body/appendix policy
- hybrid operating modes now render structural-first body sections in normal runtime
- structural-primary modes fail if required sections are missing or misplaced
- render inventory must match the contract exactly

## Validation Bundles

Core structural/render/claim validator bundle:

- `pytest -q runtime-orchestrator/tests/test_system_consistency_validator.py runtime-orchestrator/tests/test_structural_intelligence_sovereign_integration.py runtime-orchestrator/tests/test_report_conformance.py -k "output_mode or structural or claim or render_section_contract or motor_016_exposes_structural_lane_as_governed_appendices or motor_036"`
- Result: `37 passed, 31 deselected`

Exploratory/full-technical bundle:

- `pytest -q runtime-orchestrator/tests/test_evidence_maturity_engine.py -k "test_partial_bounded_asset_can_resolve_to_exploratory_prior_brief or test_sufficient_technical_substrate_unlocks_full_technical_report"`
- Result: `2 passed, 11 deselected`

Default bounded-mode sovereignty bundle:

- `pytest -q runtime-orchestrator/tests/test_structural_intelligence_sovereign_integration.py -k "test_non_operating_address_case_does_not_overpromote_after_structural_sovereignty_shift or test_structural_lane_is_default_reasoning_path_for_manufacturing_case or test_structural_lane_is_default_reasoning_path_for_nyc_screening_case or test_motor_025_can_elect_structural_primary_mode_when_explicitly_requested"`
- Result: `4 passed, 11 deselected`

Screening/blocked regression bundle:

- `pytest -q runtime-orchestrator/tests/test_precision_hardening_certification.py -k "test_one_vanderbilt_expected_behavior_supports_screening_but_blocks_roi_and_closure or test_wilsonart_expected_behavior_stays_blocked_but_graduates_tad_and_industrial_evidence_requests"`
- Result: `2 passed, 2 deselected`

## Files Hardened In Final Closure

- [render_section_contract.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/render_section_contract.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)
- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)
- [test_system_consistency_validator.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_system_consistency_validator.py>)
- [test_report_conformance.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_report_conformance.py>)

## Final Determination

The large structural-intelligence prompt is now closed at the framework level:

- the structural lane is sovereign by default for operating cases
- the canonical output-mode classifier is unified
- visible output taxonomy is canonical
- the report body now obeys structural-first policy by mode
- statement-level claim traceability is enforced
- the validator blocks missing structural sections, missing claim traces, and cross-lane inconsistencies
- all nine canonical output modes are certified

## Must Not Be Weakened

- no regression to legacy-only body architecture for normal operating screening modes
- no visible claim-bearing section without statement-level traceability
- no structural-primary render without required body sections
- no accidental overpromotion of non-operating targets into structural-first visible outputs
- no downgrade of the unified canonical output-mode classifier back into split legacy/structural decision paths
