# Structural Default Non-Override Certification — Latest

Generated on: `2026-04-30`

Status: `accepted`

## Scope

This certification closes `SIEC-10` for the structural-intelligence expansion.

It certifies that once structural reasoning became sovereign by default, the framework still does **not** overpromote visible output modes in normal cases.

## What Was At Risk

After the sovereignty shift, the main failure mode was:

- structural reasoning becomes the default path
- and the system accidentally upgrades ordinary cases into structural-primary outputs

The certification target was:

1. `One Vanderbilt` normal must remain `Compliance / Investment Screening Brief`
2. `Wilsonart` normal must remain `Decision-Blocked Asset Brief`
3. `address/HQ` style cases must remain `Target Classification Brief`

## Runtime Proof

Normal NYC building case:

- `run:964a10d6cb1bcdb1`
- pipeline: `ova-siec01-2026`
- confirmed in manifest:
  - `structural_primary_promotion_state = structural_first_default_active`
  - `default_reasoning_path = structural_first`
  - `structural_sovereignty_state = structural_first_default`
  - `final_published_report_type = Compliance / Investment Screening Brief`

Interpretation:

- the system now reasons structurally first by default
- but still does **not** overpromote the visible output into a false structural-primary mode

## Non-Regression Fix Closed

During `SIEC-10`, one real gap appeared:

- non-operating `address/HQ` cases did not overpromote the final visible type
- but they were still incorrectly flagged as `structural_first_default`

That is now fixed in:

- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)

The canonical problem frame now vetoes structural-first activation when:

- `motor_039.selected_archetype_id = target_not_yet_structurally_modelable`

This keeps the structural lane from claiming sovereignty over cases that are explicitly not yet structurally modelable.

## Test Bundle

Certification bundle:

- `pytest -q runtime-orchestrator/tests/test_structural_intelligence_sovereign_integration.py -k "default_reasoning_path_for_nyc_screening_case or default_reasoning_path_for_manufacturing_case or non_operating_address_case_does_not_overpromote_after_structural_sovereignty_shift"`

Result:

- `3 passed, 12 deselected`

## Certified Cases

| Case | Evidence | Expected | Certified result |
|---|---|---|---|
| `One Vanderbilt` normal | real runtime manifest | `Compliance / Investment Screening Brief` | passed |
| `Wilsonart` normal | sovereign integration regression test | `Decision-Blocked Asset Brief` | passed |
| `PLD / address-HQ` style non-operating target | sovereign integration regression test | `Target Classification Brief` | passed |

## Files Hardened

- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- [test_structural_intelligence_sovereign_integration.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_structural_intelligence_sovereign_integration.py>)

## Final Determination

`SIEC-10` is now closed:

- structural reasoning may remain sovereign by default for normal modelable asset cases
- visible output modes still remain bounded by the canonical classifier
- `One Vanderbilt` normal does not become false structural-primary
- `Wilsonart` normal does not become false redesign-primary
- non-operating address/HQ cases no longer present themselves as structurally sovereign

## Must Not Be Weakened

- do not allow `target_not_yet_structurally_modelable` cases to inherit `structural_first_default`
- do not allow structural sovereignty to bypass the canonical output-mode classifier
- do not allow normal manufacturing blocked cases to drift into redesign-primary without explicit eligible election
- do not allow normal screening cases to drift into `Full Technical Decision Intelligence Report`
