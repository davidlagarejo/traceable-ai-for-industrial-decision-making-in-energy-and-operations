# Structural Primary Output Modes Certification — Latest

Generated on: `2026-04-30`

Status: `accepted`

## Scope

This certification closes the current tranche of the structural-intelligence expansion that allows **opt-in sovereign promotion** of structural output modes into the primary published report type.

It certifies this behavior from **official persisted input fixtures**, not only from inline test dictionaries or `/tmp`-only experiments.

## Runtime Fix Closed

The last blocker was real:

- `Structural Contradiction Brief` could be promoted in synthetic tests
- but failed in real runtime because [motor_040.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_040.py>) runs before `motor_014`, `motor_033`, and `motor_034`

That is now fixed in:

- [cross_layer_conflicts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/cross_layer_conflicts.py>)

The conflict engine now derives contradiction signals directly from:

- `system_abstraction`
- `dominant_variable_register`

without depending on future-motor outputs to activate the contradiction lane.

## Official Fixtures

Persisted fixtures now live in:

- [ova_structural_contradiction_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/ova_structural_contradiction_inputs.json>)
- [ova_competitive_positioning_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/ova_competitive_positioning_inputs.json>)
- [ova_tad_action_priority_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/ova_tad_action_priority_inputs.json>)
- [mfg_wilsonart_system_redesign_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/mfg_wilsonart_system_redesign_inputs.json>)

## Certified Real Runs

| Fixture | Run ID | Pipeline | Requested Mode | Final Published Type | Status |
|---|---|---|---|---|---|
| `ova_structural_contradiction_inputs.json` | `run:e7b00d86892eff7b` | `ova-contradiction-2026` | `Structural Contradiction Brief` | `Structural Contradiction Brief` | `partial` |
| `ova_competitive_positioning_inputs.json` | `run:78de69709ab66030` | `ova-competitive-official-2026` | `Competitive Positioning Brief` | `Competitive Positioning Brief` | `partial` |
| `ova_tad_action_priority_inputs.json` | `run:edc92a97b3f0cbd3` | `ova-tad-2026` | `TAD Action Priority Brief` | `TAD Action Priority Brief` | `partial` |
| `mfg_wilsonart_system_redesign_inputs.json` | `run:0f03dca923d6c0e8` | `wilsonart-redesign-2026` | `System Redesign Hypothesis Brief` | `System Redesign Hypothesis Brief` | `partial` |

Interpretation:

- all four official fixtures triggered the requested structural primary mode
- all four runs completed `46` motors
- `partial` status still reflects broader preflight behavior, not failure of the primary-promotion contract

## Tests

Fixture-contract bundle:

- `pytest -q runtime-orchestrator/tests/test_structural_intelligence_sovereign_integration.py -k "official_structural_primary_input_fixtures_encode_explicit_requests or official_ova_competitive_fixture_promotes_competitive_positioning_brief or official_ova_tad_fixture_promotes_tad_action_priority_brief or official_ova_structural_contradiction_fixture_promotes_structural_contradiction_brief"`
- Result: `4 passed, 6 deselected`

Contradiction runtime-fix bundle:

- `pytest -q runtime-orchestrator/tests/test_structural_intelligence_conflicts_and_framing.py runtime-orchestrator/tests/test_structural_intelligence_sovereign_integration.py -k "contradiction or official_ova_structural_contradiction_fixture_promotes_structural_contradiction_brief or official_structural_primary_input_fixtures_encode_explicit_requests"`
- Result: `2 passed, 12 deselected`

## Files Hardened

- [cross_layer_conflicts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/cross_layer_conflicts.py>)
- [test_structural_intelligence_sovereign_integration.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_structural_intelligence_sovereign_integration.py>)
- [ova_structural_contradiction_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/ova_structural_contradiction_inputs.json>)
- [ova_competitive_positioning_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/ova_competitive_positioning_inputs.json>)
- [ova_tad_action_priority_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/ova_tad_action_priority_inputs.json>)
- [mfg_wilsonart_system_redesign_inputs.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/mfg_wilsonart_system_redesign_inputs.json>)

## Final Determination

This tranche is now closed:

- the structural lane remains opt-in
- default report identity still holds when no structural primary mode is requested
- requested structural modes only promote when eligible
- the contradiction lane no longer depends on future motors to become visible in real runtime
- all four structural primary modes are now certified from official fixtures

## Must Not Be Weakened

- no accidental structural primary override without explicit request
- no structural primary promotion when the requested mode is not eligible
- no dependence on downstream future-motor outputs for contradiction activation inside `motor_040`
- no structural mode override of claim-permission ceilings
- no loss of canonical trace fields for requested mode, promotion state, and final published type
