# GTM Brutal Audit

## 1. Scope reviewed

This audit is based on real artifacts from the current runtime:

- [One Vanderbilt manifest](/Users/davidlagarejo/ZLab_Reports/zlab-asset-commercial-building-one-vanderbilt-2026_decision_blocked_asset_brief_en_manifest.json)
- [Wilsonart manufacturing manifest](/Users/davidlagarejo/ZLab_Reports/zlab-asset-manufacturing-facility-wilsonart-temple-north-laminate-facility-2026_decision_blocked_asset_brief_en_manifest.json)
- [Prologis / Pier 1 Bay 1 manifest](/Users/davidlagarejo/ZLab_Reports/zlab-addr-warehouse-distribution-pier-1-bay-1-san-francisco-ca-94111-2026_entity_address_classification_brief_en_manifest.json)
- [Ambiguous target manifest](/Users/davidlagarejo/ZLab_Reports/zlab-addr-industrial-plant-123-test-access-road-elko-nv-89801-2026_target_clarification_brief_en_manifest.json)
- [One Vanderbilt executive / evidence / inference TeX](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp:385dd006/Chapters/C1.tex)
- [One Vanderbilt minimum evidence pack TeX](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp:385dd006/Chapters/C5.tex)
- [Wilsonart executive / evidence / inference TeX](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp:022da6f2/Chapters/C1.tex)
- [Wilsonart minimum evidence pack TeX](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp:022da6f2/Chapters/C5.tex)
- [Template abstract leakage](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp:385dd006/Chapters/00-Abstract.tex)

---

## 2. Brutal diagnosis

The current report is not GTM-ready because it still behaves like a governed runtime export, not like a capital-decision product.

The system is epistemically strong, but commercially weak.

It leaks internal ontology, template scaffolding, debug-like registers, redundant prose, and framework state language into the client experience.

A fund or bank will read it and conclude:

- the system is disciplined,
- but the artifact is too internal,
- too long,
- too repetitive,
- and too weakly translated into money and action.

The product currently feels safer than a normal AI report, but not yet strong enough to become a standard underwriting screen.

---

## 3. What makes the current report feel weak

### 3.1 It still looks like a downgraded technical report

Examples:

- `Decision-Blocked Asset Brief`
- `publication ceiling`
- `epistemic marker`
- `Technical Reference Data`
- `P/R/V`
- `LC-ASSET-01`

Those labels may be useful internally, but above the fold they signal:

- internal framework instrumentation,
- not a finished commercial product.

### 3.2 The first read does not translate uncertainty into money fast enough

The executive summary says the case is blocked, but it does not immediately tell the buyer:

- what capital action is unsafe,
- what downside the wrong assumption creates,
- what evidence is worth paying to get tomorrow.

### 3.3 The product repeats itself

Observed duplication:

- the same executive block appears in `00-Brief.tex` and `C1.tex`;
- evidence pack rows repeat within the same section;
- TAD, evidence pack, validation ranking, and inference register all restate the same blockers.

This makes the report feel longer and weaker than it is.

### 3.4 Internal framework codes crowd out buyer clarity

Observed examples:

- `geometry_size_cluster`
- `vintage_structure_cluster`
- `LC-ASSET-01`
- `DIRECT_EVIDENCE`
- `decision_grade`

A client should never need to parse ontology to understand the blocked decision.

### 3.5 The document still carries thesis-template leakage

Observed in [00-Abstract.tex](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp:385dd006/Chapters/00-Abstract.tex):

- Portuguese and English academic abstract instructions
- placeholder keywords
- generic project guide text

This is fatal for GTM credibility if it ever leaks to the final deliverable.

### 3.6 The minimum evidence pack is not yet a sharp commercial unlock list

Observed in One Vanderbilt and Wilsonart:

- duplicated items
- too many items
- mixed granularity
- mixed buyer intents

The current section still reads partly like diligence inventory, not like a short evidence-to-decision unlock map.

### 3.7 The inference register is useful internally but commercially noisy

The current `Inference Case Register` contains:

- too many rows,
- too much ontology,
- weak prioritization for a client,
- and finance / governance / ops items mixed together without commercial narrative control.

This is appendix material, not part of the product spine.

### 3.8 Some sections still drift away from asset-level decision discipline

Examples observed:

- finance-side items entering blocked asset briefs with insufficient asset substrate,
- manufacturing compliance language referencing generic `ASHRAE_90.1`,
- debt and revenue items surfacing before asset boundary and process evidence are commercially grounded.

That weakens trust in the section hierarchy.

---

## 4. Exact remove list

Remove from the commercial spine:

- `publication ceiling`
- `epistemic marker`
- `Technical Reference Data`
- `P/R/V`
- raw case codes such as `LC-ASSET-01`
- raw cluster labels such as `geometry_size_cluster`
- `Use / Not Use` blocks in current form
- debug-like source-state framing
- repeated “this brief does not conclude...” boilerplate
- academic abstract / keyword template content
- thesis-template chapter scaffolding

Move to appendix only:

- inference case register
- framework constraint boilerplate
- long validation rankings
- route/routing diagnostics
- internal evidence-state enums

---

## 5. Exact fix list

### Executive brief

Fix:

- lead with the blocked decision;
- name the dangerous assumption;
- translate that assumption into capital risk;
- end with the immediate admissible action.

Do not:

- lead with document type or framework labels.

### TAD

Fix:

- make it the clearest section in the document;
- enforce one row per real decision front;
- use only `ACT NOW / VALIDATE FIRST / INVESTIGATE / DEFER / NO-GO`.

### Investment uncertainty map

Fix:

- collapse to 4-6 rows max;
- rank by downside, not by ontology class;
- make every row legible to a lender or IC.

### Minimum evidence pack

Fix:

- dedupe aggressively;
- reduce to `7-10` items max;
- tie each item to a concrete unlocked decision.

### Scenario space

Fix:

- stop implying pseudo-probability;
- define scenarios by evidence split;
- connect each scenario to financial meaning.

### Financial exposure

Fix:

- show downside of acting under weak assumptions;
- do not drift into fake ROI closure.

### Regulatory screening

Fix:

- keep it route-specific by jurisdiction and asset type;
- remove generic normative filler once real route-specific sources exist.

---

## 6. Exact add list

Add explicitly:

- one-line capital-decision statement
- one-line “why it is dangerous to proceed”
- one-line “what changes the state”
- buyer-visible decision status table
- financial downside table by unsupported assumption
- evidence pack ranked by decision unlock value
- scenario table showing what evidence separates scenarios
- page-1 and page-2 read path for IC / lender use

---

## 7. Highest-severity structural errors

### Severity: critical

1. Template leakage from the LaTeX thesis skeleton.
2. Internal ontology above the fold.
3. Repetition between executive brief, chapter 1, evidence pack, and inference register.
4. Weak commercial translation of uncertainty into money.

### Severity: high

5. Duplicated evidence items in the minimum evidence pack.
6. Overlong sections that should be compressed or demoted to appendices.
7. Route-specific regulatory logic not always translated into route-specific client language.
8. Mixed asset-level and entity/finance logic in blocked cases before the report earns that complexity.

### Severity: medium

9. Client-facing language still too framework-native.
10. Buyer persona not explicit enough in row ordering and emphasis.

---

## 8. What a fund or bank would think today

Positive reaction:

- the system is more disciplined than most AI outputs;
- the evidence governance is real;
- the blocked posture appears legitimate.

Negative reaction:

- too much internal language,
- too much repetition,
- not enough immediate money translation,
- too much appendix logic leaking into the main report,
- and too much work required from the reader to locate the actual decision.

Commercial conclusion:

`Interesting engine, but the report still needs productization before it becomes a repeatable buying object.`

---

## 9. Decision

The core engine is commercially promising.
The current report is not yet commercially sharp enough.

The next GTM wave must focus on:

1. first-two-pages redesign,
2. section deduplication,
3. stronger capital-risk language,
4. evidence-pack compression,
5. appendix demotion of internal registers,
6. removal of template leakage and framework-debug residue.
