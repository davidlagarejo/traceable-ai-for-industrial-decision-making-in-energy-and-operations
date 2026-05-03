# Report System Precision Hardening — Final Acceptance

## 1. System Diagnosis

| Problem | Owner motor(s) | Correction status | Notes |
|---|---|---|---|
| Good public-evidence cases were over-blocked | `motor_007`, `motor_034`, `motor_025` | Resolved | `One Vanderbilt` now upgrades from blocked to screening when strong public clusters exist. |
| Report type lacked graduation | `motor_007`, `motor_034`, `motor_025` | Resolved | Final trace now exposes early gate, maturity refinement, and final published identity. |
| Public source routing was insufficiently explicit per asset | `motor_035`, `motor_028`, `motor_016` | Resolved | Canonical `source_family_coverage_table` is emitted and rendered. |
| Claims, summary, and downstream gating could diverge | `motor_034`, `motor_024`, `motor_025` | Resolved | Contract completeness and count consistency now hard-block publication. |
| TAD was too flat | `motor_033`, `motor_014` | Resolved | Differentiated states now include `ACT NOW`, `VALIDATE FIRST`, `INVESTIGATE`, `DEFER`, `NO-GO`. |
| Minimum Evidence Pack duplicated items | `motor_014` | Resolved | Dedupe now uses semantic unlock-equivalence, not only literal text. |
| Financial section was not translating uncertainty to downside | `motor_014`, `motor_015`, `motor_016` | Resolved | `financial_exposure_register` is visible downstream. |
| Scenario rows floated without falsification or evidence links | `motor_014`, `motor_015`, `motor_016` | Resolved | Scenario contract now requires financial meaning, falsification, and evidence link. |
| Pipeline garbage and placeholders could leak into report | `motor_016`, `motor_024`, `motor_025` | Resolved | Critical lint now blocks PDF on context leakage, wrong jurisdiction, and blank-field presentation. |
| Template contamination was not checked comparatively | `motor_016`, `motor_024`, `motor_025` | Resolved | Case adaptation now compares structured fingerprints against comparable references. |
| No mandatory self-evaluation | `motor_024`, `pipeline_orchestrator` | Resolved | Every run now carries `phase_self_evaluation_summary`. |

## 2. Implementation Plan Executed

- Baseline freeze and failure fixtures
- Field-support semantics and cluster maturity
- Report-type graduation
- Jurisdiction/industry-aware routing hardening
- Claim contract completion and consistency gates
- TAD graduation
- Minimum Evidence Pack + value-of-information + scenario contracts
- Financial exposure translation
- Report preflight and template-contamination blocking
- Real full-run certification refresh
- Final acceptance packaging

Reference artifacts:
- [runtime_report_system_precision_hardening_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_report_system_precision_hardening_backlog.md>)
- [runtime_report_system_precision_hardening_completion_plan.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_report_system_precision_hardening_completion_plan.md>)

## 3. Files / Modules Modified

Core logic:
- [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
- [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- [motor_015.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_015.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)
- [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)
- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- [pipeline_orchestrator.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py>)
- [models.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/models.py>)
- [dashboard.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/dashboard.py>)

New helpers / artifacts:
- [cluster_scoring.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/cluster_scoring.py>)
- [claim_templates.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/claim_templates.py>)
- [dependency_rules.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/dependency_rules.py>)
- [report_system_precision_hardening_system_diagnosis.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/report_system_precision_hardening_system_diagnosis.md>)
- [report_system_precision_hardening_certification_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/report_system_precision_hardening_certification_latest.md>)
- [report_system_precision_hardening_certification_latest.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/report_system_precision_hardening_certification_latest.json>)

## 4. Changes by Phase

| Phase | Change Implemented | Result |
|---|---|---|
| A | Baseline fixtures for `One Vanderbilt`, `Wilsonart`, `HQ/mailing` | Locked the failure state before hardening |
| B | Field-support semantics | Identity support no longer implies operating substrate support |
| C | Cluster maturity scoring | Public L3 clusters now distinguish screening from hard block |
| D | Report-type graduation | `One Vanderbilt` no longer collapses into Wilsonart treatment |
| E | Claim contract completion | Claims now emit required evidence and dependency variables |
| F | TAD graduation | Decision fronts now carry differentiated admissibility states |
| G | Minimum Evidence Pack hardening | Duplicates removed and value-of-information improved |
| H | Financial exposure translation | Downside is explicit without fabricating ROI |
| I | Scenario contract hardening | Every scenario now needs financial meaning and falsification |
| J | Report preflight | Publication blocks on coherence, placeholder, and context failures |
| K | Comparative case adaptation | Near-clone reports now fail `TEMPLATE_CONTAMINATION_FAILURE` |
| L | Self-evaluation and final reruns | Per-run self-evaluation and end-to-end certification completed |

## 5. Tests Added / Strengthened

- [test_report_precision_hardening_baseline.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_report_precision_hardening_baseline.py>)
- [test_field_support_semantics.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_field_support_semantics.py>)
- [test_tad_graduation.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_tad_graduation.py>)
- [test_report_conformance.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_report_conformance.py>)
- [test_evidence_maturity_engine.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_evidence_maturity_engine.py>)
- [test_evidence_maturity_wiring.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_evidence_maturity_wiring.py>)
- [test_self_evaluation_register_is_present.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_self_evaluation_register_is_present.py>)
- [test_precision_hardening_certification.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_precision_hardening_certification.py>)

## 6. Before / After — Wilsonart vs One Vanderbilt

### Real full runs

| Case | Before | After | Run ID | Status |
|---|---|---|---|---|
| One Vanderbilt | `Decision-Blocked Asset Brief` | `Compliance / Investment Screening Brief` | `run:87a60ef55e9a5759` | `completed` |
| Wilsonart Temple North Laminate Facility | `Decision-Blocked Asset Brief` | `Decision-Blocked Asset Brief` | `run:0832a58b672af2ac` | `completed` |
| PIER 1 BAY 1 / HQ-mailing | `Entity Address Classification Brief` | `Entity Address Classification Brief` | `run:eb1597ca013b28bd` | `completed` |

### Functional differences now enforced

- `One Vanderbilt`
  - `numeric_eui_claim = allowed`
  - `ll97_penalty_screening_claim = allowed`
  - `compliance_investment = VALIDATE FIRST`
  - `seller_or_operator_evidence_request = ACT NOW`
- `Wilsonart`
  - `process_redesign_recommendation_claim = prohibited`
  - `environmental_or_permit_driven_investment = VALIDATE FIRST`
  - `process_efficiency_or_utility_support_capex = DEFER`
  - `process_redesign = NO-GO`

## 7. Final Self-Evaluation

From [report_system_precision_hardening_certification_latest.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/report_system_precision_hardening_certification_latest.json>):

- `total_cases = 3`
- `passed_cases = 3`
- `failed_cases = 0`
- `one_vanderbilt_vs_wilsonart_diverge = true`
- `overall_pass = true`

Latest real-run self-evaluation states:
- `One Vanderbilt`: `partially_resolved` with `8 resolved / 1 partially_resolved / 0 unresolved`
- `Wilsonart`: `partially_resolved` with `7 resolved / 2 partially_resolved / 0 unresolved`
- `HQ / mailing`: `partially_resolved` with `8 resolved / 0 partially_resolved / 1 unresolved`

## 8. Remaining Limitations

- Industry deepening is still stronger than before but not complete enough to call `RSH-C08` fully closed.
  - Manufacturing still needs deeper explicit handling of `NAICS/SIC`, `resin systems`, `presses`, `curing`, `dust collection`, `VOC`, `thermal oil / steam / boilers`, and `material handling`.
  - Office-tower logic still needs deeper explicit handling of `tenant metering`, `lease responsibility`, `central plant`, `use mix`, and `steam / gas / electrification exposure`.
- `phase_self_evaluation_summary` is visible in the run manifest and `/api/live` dashboard surface. It is not embedded into `motor_027` delivery manifest because that motor runs before `motor_024` in the DAG.
- The logic is still intentionally conservative. Cases without sufficient public or operator evidence will continue to stop at screening or blocked states.

## 9. What Must Not Be Weakened

- No hallucinated certainty
- No ROI without evidence
- No compliance closure without official filing or verified baseline
- No savings claim without utility, systems, and control-boundary evidence
- No benchmark as local truth
- No LLM-generated certainty overriding structured governance
- No final recommendation when evidence is missing
- No over-auditing before the minimum evidence request is defined
- No template-style report parameterization that ignores asset type, jurisdiction, sources, maturity, and decision front
