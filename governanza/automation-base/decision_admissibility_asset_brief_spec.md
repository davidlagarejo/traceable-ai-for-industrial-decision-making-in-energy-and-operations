# Decision-Admissibility Asset Brief Spec

## 1. Product objective

The `Decision-Admissibility Asset Brief` is a capital-decision screen.

Its purpose is to answer:

- what decision is blocked,
- why acting now is dangerous,
- what unsupported assumption creates downside,
- what evidence changes the state,
- and what the buyer can do now.

It is not a technical dump and not a consultant-style pre-read.

---

## 2. Primary reader

Primary reader:

- fund partner
- lender / bank underwriter
- asset manager / IC reader

Secondary reader:

- industrial operator

Rule:

- the first reading path must work for a capital allocator in under five minutes.

---

## 3. Report identity rules

### Commercial title

- `Decision-Admissibility Asset Brief`

### Commercial subtitle

- `Minimum Evidence to Commit Capital`

### Runtime truth states underneath

- `Decision-Blocked Asset Brief`
- `Target Classification Brief`
- `Entity Address Classification Brief`
- `Minimum Evidence Report`

Rules:

- The commercial surface leads with product value.
- The runtime state remains visible in metadata or appendix, not as the main product identity.
- Classification cases must still use separate classification-brief products.

---

## 4. Final section order

1. Cover Page
2. Executive Decision-Admissibility Brief
3. Decision Layer (TAD)
4. Investment Uncertainty Map
5. Minimum Evidence Pack
6. Scenario Space
7. Financial Exposure
8. Regulatory Screening
9. Technical Appendices

Rule:

- no section may appear above these if it does not help the buyer decide what to do next.

---

## 5. Page-one contract

Page one must answer:

1. what decision is blocked;
2. why proceeding now creates structural error;
3. what unsupported assumption matters most;
4. what the next admissible action is.

Allowed elements:

- one short headline
- one short paragraph
- one 4-5 line decision facts box

Forbidden:

- framework disclaimers
- ontology codes
- publication ceiling language
- route diagnostics
- internal evidence-state taxonomy

---

## 6. Page-two contract

Page two must make four things obvious:

- the decision table,
- the key uncertainties,
- the minimum evidence pack,
- and the scenario split.

If the buyer has to search beyond page two to know what evidence to request next, the document failed.

---

## 7. Section contracts

### 7.1 Executive Decision-Admissibility Brief

**Purpose**

- state the blocked decision and the immediate action

**Inputs**

- `motor_014`
- `motor_033`
- `motor_034`
- `motor_012`

**Required structure**

- sentence 1: blocked decision
- sentence 2: dangerous assumption
- sentence 3: why it matters financially or operationally
- sentence 4: next admissible action

**Allowed content**

- one concrete blocked decision
- one dominant dangerous assumption
- one direct next action

**Forbidden content**

- repeated disclaimers
- long epistemic caveats
- ontology labels
- more than one paragraph

**Max length**

- 120-160 words

### 7.2 Decision Layer (TAD)

**Purpose**

- show what can and cannot be done now

**Columns**

- `Decision`
- `Status`
- `Why`
- `Required Evidence`
- `Action`

**Allowed statuses**

- `ACT NOW`
- `VALIDATE FIRST`
- `INVESTIGATE`
- `DEFER`
- `NO-GO`

**Row logic**

- top rows must be highest capital or operational relevance

**Max rows**

- 5

**Forbidden**

- generic recommendations
- action queues without decision fronts

### 7.3 Investment Uncertainty Map

**Purpose**

- connect uncertainty directly to money or commitment risk

**Columns**

- `Uncertainty`
- `Financial Impact`
- `Decision Blocked`
- `Evidence Needed`
- `Priority`

**Max rows**

- 6

**Forbidden**

- generic uncertainty prose
- repeated evidence items
- ontology language

### 7.4 Minimum Evidence Pack

**Purpose**

- tell the buyer exactly what to request next

**Columns**

- `Evidence`
- `Source`
- `Why It Matters`
- `Unlocks`
- `Effort`

**Max rows**

- 7 to 10

**Rules**

- dedupe across all sections
- each row must unlock a decision, not just “improve confidence”

**Forbidden**

- duplicates
- low-signal requests
- evidence not tied to a decision front

### 7.5 Scenario Space

**Purpose**

- show bounded scenario alternatives under current evidence

**Columns**

- `Scenario`
- `Plausibility`
- `Financial Meaning`
- `What Makes It True`
- `What Falsifies It`
- `Evidence Needed`

**Max rows**

- 3 to 5

**Rules**

- no invented probabilities
- plausibility states only
- each scenario must differ by evidence boundary

### 7.6 Financial Exposure

**Purpose**

- show downside of acting under weak assumptions

**Columns**

- `Assumption`
- `Current Support`
- `Downside Risk`
- `Evidence Needed`
- `Impact`

**Max rows**

- 5

**Rules**

- no exact ROI if maturity is insufficient
- show downside before upside

### 7.7 Regulatory Screening

**Purpose**

- show route-specific regulatory exposure relevant to the current asset

**Required behavior**

- NYC must render NYC-specific screening
- California must render CA / city / utility-specific screening
- Texas industrial must render TCEQ / ERCOT / permit logic

**Forbidden**

- generic ASHRAE-only filler when route-specific sources exist
- jurisdiction leakage from other cities or states

### 7.8 Technical Appendices

**Purpose**

- retain framework rigor without contaminating the product spine

**Allowed appendix items**

- inference register
- full evidence maturity registers
- routing bundle
- source register
- contamination log
- detailed field admissibility

**Rule**

- appendix detail must never dominate pages 1-3.

---

## 8. Content priority rules

### Must be above the fold

- blocked decision
- dangerous assumption
- next action
- top evidence request

### Must be below the fold or appendix

- internal case codes
- raw routing artifacts
- evidence-state enums
- full source lineage
- internal governance text

---

## 9. Language contract

The language must sound like:

- risk committee
- investment memo
- disciplined diligence screen

The language must not sound like:

- internal framework debug
- AI explanation
- consultant filler
- academic template

Examples of preferred phrasing:

- `Proceeding with CAPEX or underwriting decisions under current evidence would introduce structural error.`
- `The current evidence supports screening only, not commitment.`
- `The next value-creating step is not more analysis; it is targeted evidence acquisition.`

---

## 10. Runtime mapping

### Main runtime owners

- `motor_016`:
  report assembly and section ordering
- `motor_019`:
  section packet content and writer controls
- `motor_014`:
  uncertainty, scenarios, evidence unlock logic
- `motor_033`:
  TAD
- `motor_034`:
  maturity ceiling and claim permissions
- `motor_012`:
  field register and missing evidence
- `motor_017`:
  final render
- `motor_024/025/027`:
  GTM quality gating and delivery blocking

---

## 11. Commercial quality gates

The report must fail GTM certification if any of these are true:

- duplicated evidence items remain in the commercial spine
- the blocked decision is not explicit on page one
- TAD rows do not name real decision fronts
- route-specific regulation collapses to generic filler
- financial exposure implies ROI closure without maturity support
- appendix/debug language leaks above the fold
- template residue is visible

---

## 12. Definition of done

The spec is correctly implemented when:

- a fund can read the first two pages and know whether to proceed;
- the buyer can identify the most dangerous unsupported assumption;
- the evidence request list is short and obviously ranked;
- the report sounds deliberate and commercial;
- the product visibly differs from AI summaries, ESG dashboards, and generic diligence memos.
