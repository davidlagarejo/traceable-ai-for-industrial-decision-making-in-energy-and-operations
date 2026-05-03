# Runtime GTM Decision-Admissibility Brief Backlog

## 1. Purpose

This backlog converts the current report layer from a technically correct but commercially weak artifact into a sellable product:

- `Decision-Admissibility Asset Brief`
- `Minimum Evidence to Commit Capital`

It does **not** change the epistemic constitution of ZLab.
It does **not** turn the framework into an auditor, verifier, or ROI closer.

It operationalizes the existing framework as a GTM-facing product so the final artifact:

- feels like a capital-decision tool,
- states clearly what decision is blocked,
- translates uncertainty into financial and operational risk,
- shows what evidence changes the state,
- avoids AI/template perception,
- and gives the buyer an immediate next action.

This backlog complements:

- [runtime_decision_admissibility_report_ticket_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_decision_admissibility_report_ticket_backlog.md>)
- [runtime_global_public_data_routing_v1_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_global_public_data_routing_v1_backlog.md>)
- [runtime_evidence_maturity_nyc_execution_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_evidence_maturity_nyc_execution_backlog.md>)

Those documents harden admissibility, routing, and evidence.
This document turns that system into a product a fund, lender, asset manager, or industrial operator can buy.

---

## 2. Governing GTM standard

The document must make the reader feel:

`This prevented a capital allocation error.`

It must **not** make the reader feel:

- `This is an incomplete report.`
- `This is an AI-generated summary.`
- `This is a generic diligence template.`
- `This is interesting but not actionable.`

The product must behave like a high-discipline decision screen for capital under uncertainty, not like a degraded technical memo.

---

## 3. Buyer priority

The first commercial target is:

1. funds
2. lenders / banks
3. asset managers

The secondary overlay is:

4. industrial operators

Rules:

- The core report spine must optimize first for capital allocators.
- Operator-specific framing may be added as an overlay, but cannot dominate the core product.

---

## 4. Non-goals

This GTM backlog must **not**:

- turn the brief into a full audit,
- imply verified savings when evidence is weak,
- imply decision-grade ROI when evidence is insufficient,
- add decorative narrative,
- add more pages without increasing decision clarity,
- or soften blocked decisions to make the report feel more complete.

---

## 5. Product identity the runtime must support

The outward product identity must center on:

- `Decision-Admissibility Asset Brief`
- `Minimum Evidence to Commit Capital`

Internal runtime states may still include:

- `Target Classification Brief`
- `Decision-Blocked Asset Brief`
- `Minimum Evidence Report`
- `Asset Decision-Admissibility Brief`

Rules:

- `Decision-Blocked Asset Brief` is a runtime truth state, not necessarily the commercial title line.
- The commercial artifact must lead with buyer value, not internal degradation language.
- The report title and executive framing must read like a product for capital decisions.

---

## 6. Mandatory commercial report spine

The GTM-ready document must render this order:

1. Cover Page
2. Executive Decision-Admissibility Brief
3. Decision Layer (TAD)
4. Investment Uncertainty Map
5. Minimum Evidence Pack
6. Scenario Space
7. Financial Exposure
8. Regulatory Screening
9. Technical Appendices

Rules:

- The first two pages must answer whether the client can act now.
- Scenario and evidence sections must be short and ranked.
- Appendices must hold evidence detail, not pollute the commercial spine.

---

## 7. Execution order

The implementation order is strict:

1. GTM thesis freeze
2. brutal audit of current report outputs
3. commercial information architecture
4. section contracts
5. visible runtime rewrite
6. financial and regulatory translation
7. buyer overlays
8. GTM certification

Motor order inside runtime:

1. `motor_016`
2. `motor_019`
3. `motor_014`
4. `motor_033`
5. `motor_034`
6. `motor_012`
7. `motor_017`
8. `motor_024`
9. `motor_025`
10. `motor_027`

Reason:

- first fix what the client sees,
- then harden the section logic,
- then tie that logic back to decision, evidence, and governance,
- then certify GTM-readiness.

---

## 8. Ticket format

Each ticket includes:

- `Ticket ID`
- `Priority`
- `Owner motor(s)`
- `Primary file(s)`
- `Objective`
- `Required changes`
- `Dependencies`
- `Acceptance criteria`

---

## 9. Wave A — GTM thesis and brutal audit

### Ticket GTM-001

- `Priority`: P0
- `Owner motor(s)`: documentation / product contract
- `Primary file(s)`:
  - [gtm_report_thesis.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/gtm_report_thesis.md>)
- `Objective`:
  Freeze the external product thesis and ICP before touching the report.
- `Required changes`:
  - Define product promise.
  - Define primary buyer.
  - Define non-goals.
  - Define what the artifact must cause the client to do next.
- `Dependencies`:
  - none
- `Acceptance criteria`:
  - One page can explain what is being sold, to whom, and why it is not a generic report.

### Ticket GTM-002

- `Priority`: P0
- `Owner motor(s)`: report audit
- `Primary file(s)`:
  - [gtm_brutal_audit.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/gtm_brutal_audit.md>)
- `Objective`:
  Create an exact kill-list of what makes current reports commercially weak.
- `Required changes`:
  - Audit at least:
    - one NYC building brief
    - one CA building brief
    - one TX industrial/manufacturing brief
    - one HQ brief
    - one ambiguous brief
  - Mark:
    - duplicated text
    - weak phrasing
    - generic narrative
    - AI/template perception
    - sections with poor money linkage
- `Dependencies`:
  - GTM-001
- `Acceptance criteria`:
  - The audit yields a precise remove/fix/add list with no generic commentary.

---

## 10. Wave B — Commercial information architecture

### Ticket GTM-003

- `Priority`: P0
- `Owner motor(s)`: report architecture
- `Primary file(s)`:
  - [decision_admissibility_asset_brief_spec.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/decision_admissibility_asset_brief_spec.md>)
- `Objective`:
  Redesign the report spine around decision clarity and capital risk.
- `Required changes`:
  - Define final section order.
  - Define page-1 and page-2 reading logic.
  - Define what moves to appendices.
  - Define what never appears above the fold.
- `Dependencies`:
  - GTM-001
  - GTM-002
- `Acceptance criteria`:
  - The final index reads like a product for decision-makers, not like an internal framework dump.

### Ticket GTM-004

- `Priority`: P0
- `Owner motor(s)`: report architecture
- `Primary file(s)`:
  - [buyer_overlay_contracts.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/buyer_overlay_contracts.md>)
- `Objective`:
  Define overlay logic by buyer without duplicating the core report.
- `Required changes`:
  - Add contracts for:
    - `capital_allocator`
    - `industrial_operator`
  - Define:
    - section emphasis
    - row ordering
    - language preferences
    - action framing
- `Dependencies`:
  - GTM-003
- `Acceptance criteria`:
  - The same evidence core can produce different buyer emphasis without changing epistemic truth.

---

## 11. Wave C — Section contracts

### Ticket GTM-005

- `Priority`: P0
- `Owner motor(s)`: `motor_016`, `motor_019`
- `Primary file(s)`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Make the Executive Brief read like a product statement to capital, not like an internal analysis stub.
- `Required changes`:
  - Add executive section contract:
    - blocked decision
    - why advancing is dangerous
    - what evidence changes the state
    - what can be done now
  - Remove defensive or repetitive disclaimer tone.
  - Cap length aggressively.
- `Dependencies`:
  - GTM-003
- `Acceptance criteria`:
  - The executive section can be read standalone by a fund partner or lender and still communicate product value.

### Ticket GTM-006

- `Priority`: P0
- `Owner motor(s)`: `motor_033`, `motor_019`
- `Primary file(s)`:
  - [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Make TAD the clearest section in the document.
- `Required changes`:
  - Enforce table contract:
    - `Decision`
    - `Status`
    - `Why`
    - `Required Evidence`
    - `Action`
  - Restrict statuses to:
    - `ACT NOW`
    - `VALIDATE FIRST`
    - `INVESTIGATE`
    - `DEFER`
    - `NO-GO`
  - Rank rows by capital impact and immediacy.
- `Dependencies`:
  - existing TAD hardening
- `Acceptance criteria`:
  - No row reads like a generic recommendation.
  - Every row names a real decision front.

### Ticket GTM-007

- `Priority`: P0
- `Owner motor(s)`: `motor_014`, `motor_019`
- `Primary file(s)`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Redesign the Investment Uncertainty Map and Scenario Space as short, money-linked decision tools.
- `Required changes`:
  - Enforce uncertainty table columns:
    - `Uncertainty`
    - `Financial Impact`
    - `Decision Blocked`
    - `Evidence Needed`
    - `Priority`
  - Enforce scenario table columns:
    - `Scenario`
    - `Plausibility`
    - `Financial Meaning`
    - `What Makes It True`
    - `What Falsifies It`
    - `Evidence Needed`
  - Add dedupe and ranking logic.
- `Dependencies`:
  - GTM-002
  - GTM-003
- `Acceptance criteria`:
  - No redundant rows.
  - No invented probabilities.
  - Every row connects to money or decision posture.

### Ticket GTM-008

- `Priority`: P0
- `Owner motor(s)`: `motor_014`, `motor_034`, `motor_012`
- `Primary file(s)`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- `Objective`:
  Turn the Minimum Evidence Pack into a short commercial unlock list.
- `Required changes`:
  - Enforce max `7-10` items.
  - Enforce table columns:
    - `Evidence`
    - `Source`
    - `Why It Matters`
    - `Unlocks`
    - `Effort`
  - Merge duplicates across missing evidence, TAD, and uncertainty.
- `Dependencies`:
  - evidence maturity and missing evidence registers
- `Acceptance criteria`:
  - The evidence pack is actionable, short, deduped, and directly tied to unlocked decisions.

---

## 12. Wave D — Financial and regulatory translation

### Ticket GTM-009

- `Priority`: P0
- `Owner motor(s)`: `motor_014`, `motor_034`, `motor_019`
- `Primary file(s)`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Translate uncertainty into downside without faking ROI closure.
- `Required changes`:
  - Add financial exposure table contract:
    - `Assumption`
    - `Current Support`
    - `Downside Risk`
    - `Evidence Needed`
    - `Impact`
  - Prohibit exact ROI posture where maturity is insufficient.
  - Prefer downside framing over pseudo-precision.
- `Dependencies`:
  - evidence maturity engine
- `Acceptance criteria`:
  - The financial section explains the cost of acting under weak assumptions without pretending verified returns.

### Ticket GTM-010

- `Priority`: P0
- `Owner motor(s)`: `motor_019`, `motor_028`, `motor_035`
- `Primary file(s)`:
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
  - [motor_035.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py>)
- `Objective`:
  Make regulatory screening read jurisdiction-specific and commercially relevant.
- `Required changes`:
  - Render route-specific screening blocks:
    - NYC
    - California
    - Texas
    - industrial cross-state
  - Remove generic normative filler where route-specific sources exist.
  - Align visible output to routing and evidence maturity state.
- `Dependencies`:
  - routing and evidence maturity already wired
- `Acceptance criteria`:
  - Texas industrial does not read like NYC.
  - NYC does not read like generic ASHRAE-only compliance language.

---

## 13. Wave E — Report assembly and visible rewrite

### Ticket GTM-011

- `Priority`: P0
- `Owner motor(s)`: `motor_016`, `motor_017`, `motor_019`
- `Primary file(s)`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Rebuild the visible report package around the GTM spine.
- `Required changes`:
  - Reorder sections to commercial sequence.
  - Push low-signal technical narrative to appendices.
  - Add section max-length and row-count guards.
  - Remove template-like filler and repeated transition language.
- `Dependencies`:
  - GTM-005 through GTM-010
- `Acceptance criteria`:
  - The report reads like a coherent decision product and not like a stitched technical export.

### Ticket GTM-012

- `Priority`: P0
- `Owner motor(s)`: `motor_024`, `motor_025`, `motor_027`
- `Primary file(s)`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
  - [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)
- `Objective`:
  Prevent commercially weak reports from shipping.
- `Required changes`:
  - Add GTM quality gates:
    - duplicate row thresholds
    - filler phrase detection
    - missing decision clarity
    - missing evidence/action linkage
  - Hold export when commercial quality falls below threshold.
- `Dependencies`:
  - GTM-011
- `Acceptance criteria`:
  - A technically valid but commercially weak report can be held for revision.

---

## 14. Wave F — Buyer overlays

### Ticket GTM-013

- `Priority`: P1
- `Owner motor(s)`: `motor_016`, `motor_019`
- `Primary file(s)`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Add buyer-specific emphasis without forked reports.
- `Required changes`:
  - Add overlay selection:
    - `capital_allocator`
    - `industrial_operator`
  - Re-rank sections, rows, and framing accordingly.
- `Dependencies`:
  - GTM-004
  - GTM-011
- `Acceptance criteria`:
  - The same case can emphasize underwriting risk or operational disruption without changing the underlying truth.

---

## 15. Wave G — GTM certification

### Ticket GTM-014

- `Priority`: P0
- `Owner motor(s)`: tests / certification
- `Primary file(s)`:
  - [test_report_gtm_contract.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_report_gtm_contract.py>)
  - [test_tad_decision_clarity.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_tad_decision_clarity.py>)
  - [test_uncertainty_map_dedup.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_uncertainty_map_dedup.py>)
  - [test_minimum_evidence_pack_max_rows.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_minimum_evidence_pack_max_rows.py>)
  - [test_financial_exposure_no_fake_roi.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_financial_exposure_no_fake_roi.py>)
  - [test_regulatory_screening_by_route.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_regulatory_screening_by_route.py>)
- `Objective`:
  Certify the report commercially, not just technically.
- `Required changes`:
  - Add GTM-quality contract tests.
  - Add fixture cases:
    - NYC building
    - CA building
    - TX industrial/manufacturing
    - HQ
    - ambiguous
  - Verify:
    - no duplicate evidence rows
    - no fake ROI closure
    - route-specific regulation
    - clear TAD action framing
    - short evidence pack
- `Dependencies`:
  - GTM-005 through GTM-013
- `Acceptance criteria`:
  - The report can pass a commercial-readiness contract with no weak filler and no decision ambiguity.

---

## 16. GTM-ready checklist

The product is GTM-ready only if it passes all of these:

- the blocked decision is explicit,
- the reason for the block is explicit,
- the financial downside of weak assumptions is explicit,
- the minimum evidence pack is short and deduped,
- the next admissible action is explicit,
- the report sounds product-native, not AI-native,
- the report does not repeat itself,
- the regulatory section is jurisdiction-specific,
- the scenario section distinguishes cases by evidence,
- the report can be read quickly by a capital allocator.

---

## 17. Rules that must never be weakened

- Never fake decision-grade certainty.
- Never present blocked evidence posture as product failure.
- Never use benchmarks as if they were local truth.
- Never let issuer context dominate asset-level decision framing.
- Never let TAD drift into generic recommendations.
- Never let the evidence pack exceed actionable size.
- Never let financial language outrun evidence maturity.
- Never let route-specific regulation collapse back into generic compliance filler.
- Never ship a report that reads like an internal template dump.

---

## 18. Final success criterion

This backlog is complete when a target buyer can read the report and say:

`This stopped us from committing capital under structural uncertainty, and it told us exactly what evidence to request next.`

It is not complete when the buyer merely says:

`This is a sophisticated report.`
