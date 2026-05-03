# Buyer Overlay Contracts

## 1. Purpose

These overlays do not change epistemic truth.
They change emphasis, ordering, and language for the commercial reader.

The core report remains:

- evidence-governed,
- decision-admissibility first,
- and capital-risk aware.

---

## 2. Overlay set

The runtime must support two overlays:

- `capital_allocator`
- `industrial_operator`

If no overlay is explicitly requested, the default is:

- `capital_allocator`

---

## 3. Capital allocator overlay

### Primary audience

- fund partner
- IC member
- lender / bank underwriter
- asset manager

### Reading priority

1. blocked decision
2. dangerous assumption
3. downside if wrong
4. evidence needed to commit capital
5. next admissible action

### Section emphasis

- Executive Brief: highest
- TAD: highest
- Investment Uncertainty Map: highest
- Minimum Evidence Pack: highest
- Financial Exposure: high
- Regulatory Screening: medium
- Technical appendices: low

### Preferred language

- underwriting
- downside
- defendability
- diligence scope
- evidence path

### Avoid

- operator jargon unless it changes capital risk
- long systems descriptions above the fold

---

## 4. Industrial operator overlay

### Primary audience

- plant operator
- engineering manager
- technical asset lead
- operations executive

### Reading priority

1. blocked operational decision
2. controllability boundary
3. systems / process unknowns
4. operational downside
5. evidence needed to validate process or asset behavior

### Section emphasis

- Executive Brief: high
- TAD: highest
- Minimum Evidence Pack: highest
- Scenario Space: high
- Regulatory Screening: high if permit-driven
- Financial Exposure: medium

### Preferred language

- control boundary
- load driver
- process bottleneck
- outage / downtime
- operator-held evidence

### Avoid

- finance-heavy framing before operational constraints are stated
- generic ESG or portfolio narrative

---

## 5. Overlay invariants

The following cannot change across overlays:

- target classification
- source admissibility
- evidence maturity
- claim permissions
- decision permissions
- blocked decision truth state
- report-type switching

---

## 6. Runtime implementation rule

Overlay logic may change:

- row ordering
- section emphasis
- wording
- examples
- call-to-action phrasing

Overlay logic may not change:

- what the evidence supports
- what is blocked
- what is prohibited
- what evidence is still missing
