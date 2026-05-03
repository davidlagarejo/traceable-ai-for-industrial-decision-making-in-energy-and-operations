# Runtime Report System Precision Hardening Completion Plan

## Status

The core hardening program is already materially advanced.

Already implemented:

- differentiated report readiness for strong public-evidence cases
- cluster maturity scoring
- field support semantics
- claim/governance consistency gates
- differentiated TAD states
- stronger Minimum Evidence Pack dedupe
- financial exposure register
- scenario-to-evidence / scenario-to-decision linkage
- pre-PDF critical preflight
- case adaptation memo
- template contamination failure
- per-run self-evaluation register
- certification snapshot proving:
  - `One Vanderbilt` no longer behaves like `Wilsonart`
  - `HQ / mailing` stays non-technical

This completion plan covers the remaining gaps needed to close the prompt more literally and more defensibly.

---

## Remaining Gaps

### P0 — Must Close

1. Formal `Phase 1` diagnosis artifact in the exact table format requested by the prompt
2. Claim-permission output contract still missing explicit:
   - `required_evidence`
   - `dependency_variables`
3. Public-source execution output not yet exposed in the exact asset-level table:
   - `Source Family | Queried | Found | Authority | Scope | Fields Extracted | Missing`
4. Pre-PDF lint does not yet cover every literal forbidden string / bad field case from the prompt
5. `Case Adaptation Memo` is still heuristic-per-case; it does not yet compare against similar cases
6. Full-run real certification after the latest logic changes is still missing as final closure artifact

### P1 — Strongly Recommended

7. Final report-type trace remains distributed across `motor_007`, `motor_034`, and `motor_025`
8. Industry adaptation is materially better, but not yet deep enough for:
   - manufacturing
   - office tower
9. Self-evaluation exists in governance/runtime, but is not yet visible everywhere it should be
10. Final delivery package for this prompt is still fragmented across tests, snapshots, and chat history

### P2 — Nice to Have

11. Richer dashboard/API surfacing of the new hardening layers
12. More live full-run canaries beyond the three mandatory cases

---

## Closure Strategy

The correct finish is not a rewrite.

It is:

1. close output-contract gaps
2. close lint / governance gaps
3. harden anti-template comparison
4. rerun real certification
5. freeze final acceptance package

---

## Ticket Format

Each ticket below includes:

- `Priority`
- `Owner motor(s)`
- `Files`
- `Objective`
- `Implementation`
- `Acceptance`

---

## Wave M — Formal Diagnosis Package

### Ticket RSH-C01

- `Priority`: P0
- `Owner motor(s)`: docs only
- `Files`:
  - `governanza/automation-base/report_system_precision_hardening_system_diagnosis.md`
- `Objective`:
  Emit the exact `Phase 1` diagnosis table requested by the prompt.
- `Implementation`:
  - build the final table:
    - `Problem`
    - `Motor responsible`
    - `Exists`
    - `Works`
    - `Observed failure`
    - `Correction type`
  - classify every row with:
    - `missing logic`
    - `weak logic`
    - `bad orchestration`
    - `prompt/template issue`
    - `source routing issue`
    - `report rendering issue`
    - `governance inconsistency`
- `Acceptance`:
  - diagnosis exists as a stable artifact
  - every remaining gap maps to a sovereign owner

---

## Wave N — Claim Output Contract Completion

### Ticket RSH-C02

- `Priority`: P0
- `Owner motor(s)`: `motor_034`
- `Files`:
  - [schemas.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/schemas.py>)
  - [claim_templates.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/claim_templates.py>)
  - [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- `Objective`:
  Make claim outputs match the prompt literally.
- `Implementation`:
  - extend `ClaimPermissionRecord` with:
    - `required_evidence`
    - `dependency_variables`
  - populate them directly from claim template + resolved variable bottlenecks
  - keep:
    - `current_permission`
    - `reason_if_blocked`
    - `upgrade_path`
- `Acceptance`:
  - every claim row exposes all requested fields
  - no duplication between `required_variables` and `dependency_variables`

### Ticket RSH-C03

- `Priority`: P0
- `Owner motor(s)`: `motor_024`
- `Files`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - tests
- `Objective`:
  Extend preflight to validate the enriched claim contract.
- `Implementation`:
  - add preflight checks for:
    - missing `required_evidence`
    - missing `dependency_variables`
    - empty `upgrade_path` where a claim is `conditional`
- `Acceptance`:
  - PDF blocks if claim contract is incomplete

---

## Wave O — Public Data Coverage Table

### Ticket RSH-C04

- `Priority`: P0
- `Owner motor(s)`: `motor_028`, `motor_035`
- `Files`:
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
  - [motor_035.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py>)
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- `Objective`:
  Emit the exact source-coverage table requested by the prompt.
- `Implementation`:
  - add canonical `source_family_coverage_table` rows with:
    - `source_family`
    - `queried`
    - `found`
    - `authority`
    - `scope`
    - `fields_extracted`
    - `missing`
  - ensure wording preserves the rule:
    - identity-only source != physical substrate support
  - expose it:
    - in runtime output
    - in report appendix
    - in manifest
- `Acceptance`:
  - `NYC` and `Texas manufacturing` both render the table correctly
  - no field is marked supported when the source only confirmed identity

---

## Wave P — Lint Completion

### Ticket RSH-C05

- `Priority`: P0
- `Owner motor(s)`: `motor_024`, `motor_025`
- `Files`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- `Objective`:
  Close the remaining literal lint checks from the prompt.
- `Implementation`:
  - add critical checks for:
    - `Use the chart`
    - `The prose should`
    - `This section should`
    - `Reader takeaway` when not allowed
    - placeholders
    - wrong asset name
    - wrong jurisdiction
    - wrong regulation
    - `0 sqft`
    - blanks rendered as facts
- `Acceptance`:
  - any critical hit forces `hold_for_validation`

---

## Wave Q — Comparative Anti-Template Guard

### Ticket RSH-C06

- `Priority`: P0
- `Owner motor(s)`: `motor_016`, `motor_024`
- `Files`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - helper module under `runtime_orchestrator/reporting/`
- `Objective`:
  Move `Case Adaptation Memo` from heuristic-only to comparative anti-template logic.
- `Implementation`:
  - compare current case fingerprint against:
    - at least one building case
    - at least one manufacturing case
    - at least one classification-only case
  - compute similarity across:
    - asset type
    - jurisdiction
    - source families found
    - cluster maturity
    - dominant bottlenecks
    - decision fronts
    - scenario family
  - if substantive divergence is too low:
    - raise `TEMPLATE_CONTAMINATION_FAILURE`
- `Acceptance`:
  - `One Vanderbilt` vs `Wilsonart` pass divergence
  - two near-identical parameterized outputs fail

---

## Wave R — Unified Report-Type Trace

### Ticket RSH-C07

- `Priority`: P1
- `Owner motor(s)`: `motor_007`, `motor_034`, `motor_025`
- `Files`:
  - [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
  - [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- `Objective`:
  Keep sovereignty distributed but expose one canonical trace of final report identity.
- `Implementation`:
  - emit:
    - `early_report_type_gate`
    - `maturity_refined_report_type`
    - `final_published_report_type`
    - `report_type_override_reason`
- `Acceptance`:
  - every case shows exactly how it moved from early gate to final identity

---

## Wave S — Industry Deepening

### Ticket RSH-C08

- `Priority`: P1
- `Owner motor(s)`: `motor_012`, `motor_014`, `motor_035`, `motor_028`
- `Files`:
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - [motor_035.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py>)
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- `Objective`:
  Deepen industry logic to the level requested by the prompt.
- `Implementation`:
  - manufacturing:
    - `NAICS/SIC`
    - `resin systems`
    - `presses`
    - `curing / thermal process`
    - `compressed air`
    - `dust collection`
    - `VOC`
    - `steam / boilers / thermal oil`
    - `material handling`
    - `wastewater / air permits`
  - office tower:
    - `tenant metering`
    - `lease responsibility`
    - `central plant`
    - `occupancy / use mix`
    - `steam / gas / electrification exposure`
- `Acceptance`:
  - manufacturing no longer reads as industrial generic
  - office tower no longer reads as simple benchmark case

---

## Wave T — Surface the Self-Evaluation Everywhere

### Ticket RSH-C09

- `Priority`: P1
- `Owner motor(s)`: `motor_027`, dashboard/API
- `Files`:
  - [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)
  - [dashboard.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/dashboard.py>)
- `Objective`:
  Make self-evaluation visible outside raw run artifacts.
- `Implementation`:
  - expose `phase_self_evaluation_summary` in:
    - manifest
    - dashboard summary
    - API live/status surfaces
- `Acceptance`:
  - user can see run self-evaluation without opening raw artifact JSON

---

## Wave U — Full-Run Real Certification Refresh

### Ticket RSH-C10

- `Priority`: P0
- `Owner motor(s)`: end-to-end
- `Files`:
  - `runtime-orchestrator/scripts/`
  - `governanza/automation-base/`
- `Objective`:
  Re-run the three mandatory real cases after the latest logic changes.
- `Implementation`:
  - full-run:
    - `One Vanderbilt`
    - `Wilsonart`
    - `HQ / mailing`
  - capture:
    - final report type
    - claim counts
    - TAD states
    - financial exposure visible
    - adaptation memo status
    - preflight status
- `Acceptance`:
  - real runs match the certification intent already proven in fixtures

---

## Wave V — Final Acceptance Package

### Ticket RSH-C11

- `Priority`: P1
- `Owner motor(s)`: docs + scripts
- `Files`:
  - `governanza/automation-base/report_system_precision_hardening_final_acceptance.md`
  - `governanza/automation-base/report_system_precision_hardening_final_acceptance.json`
- `Objective`:
  Produce the final delivery package that the prompt requested as one coherent artifact.
- `Implementation`:
  - compile:
    1. system diagnosis
    2. implementation plan
    3. files/modules modified
    4. changes by phase
    5. tests added
    6. Wilsonart vs One Vanderbilt before/after
    7. final self-evaluation
    8. remaining limitations
    9. explicit list of what must not be weakened
- `Acceptance`:
  - no need to reconstruct the state from chat history

---

## Recommended Execution Order

1. `RSH-C01`
2. `RSH-C02`
3. `RSH-C03`
4. `RSH-C04`
5. `RSH-C05`
6. `RSH-C06`
7. `RSH-C07`
8. `RSH-C08`
9. `RSH-C09`
10. `RSH-C10`
11. `RSH-C11`

---

## Completion Standard

This prompt can be considered fully closed only if all of the following are true:

1. final diagnosis artifact exists in the exact requested format
2. claim outputs include `required_evidence` and `dependency_variables`
3. public routing table exists in the exact requested structure
4. pre-PDF lint covers all critical forbidden cases from the prompt
5. case adaptation compares against similar cases, not just internal heuristics
6. real full-run certification is refreshed after the latest logic changes
7. final acceptance package exists as a single coherent artifact

---

## What Must Not Be Weakened

- no hallucinated certainty
- no ROI without evidence
- no compliance closure without official filing / verified baseline
- no savings claim without utility/system/control evidence
- no benchmark as local truth
- no LLM-generated certainty
- no final recommendation when evidence is missing
- no report promotion just to look stronger
- no template parametrization disguised as case adaptation
