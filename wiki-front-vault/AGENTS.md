# AGENTS.md
## Minimal Schema for the Wiki Front Vault

This vault follows the Karpathy pattern in a minimal form:

- raw sources are immutable
- the LLM maintains a persistent markdown wiki
- `index.md` is the navigation file
- `log.md` is the append-only history
- this file is the operating schema

The vault is governed by the framework but is not allowed to override framework truth.

## 1. Authority

Primary authority lives outside the vault:

- [`../Phases/phase-0/docs/en/0_Phase_0_Master_Document.md`](../Phases/phase-0/docs/en/0_Phase_0_Master_Document.md)

Inside the vault, use:

- [`03_Truth_Model/01_Phase_0_Bridge.md`](03_Truth_Model/01_Phase_0_Bridge.md)
- [`03_Truth_Model/03_Claim_Status_Bridge.md`](03_Truth_Model/03_Claim_Status_Bridge.md)

If a vault page says more than those sources allow, the vault page is wrong.

## 2. Minimal topology

- `01_Raw_Sources/`: immutable originals
- `02_Evidence_Base/`: admitted evidence, contradictions, validation traces
- `03_Truth_Model/`: bridge back to constitutional truth rules
- `04_Case_Wiki/`: the persistent interlinked wiki layer
- `06_GTM_Copy/`: downstream translation layer

## 3. Product frame

The initial product is a family of outputs such as:

- Pre-Verification Asset Brief
- Asset Decision Integrity Report
- Decision Exposure Memo

The product exists before:

- expensive audits
- heavy due diligence
- CAPEX commitment
- financing
- sensor integration

Its promise is not a final answer.

Its promise is:

- help avoid spending time and capital on a badly framed problem

## 4. Real buyers

Optimize for:

- funds
- banks
- project finance
- large ESCOs
- technical sponsors
- diligence teams
- physical-asset investors

Their real questions are:

- what is poorly understood
- what decision is exposed
- what assumption is fragile
- what should not be done yet
- what should be verified first
- what preliminary financial exposure exists
- how far the case is from verification-grade

Do not default to operator-dashboard language.

## 5. Page types

Use only these durable page types:

- `source_page`
- `evidence_page`
- `concept_page`
- `case_page`
- `tension_page`
- `verification_page`
- `gtm_translation_page`

Every material page should carry at least:

```yaml
---
page_type:
title:
support_state:
publication_state:
intended_use:
source_refs: []
evidence_refs: []
upstream_refs: []
downstream_refs: []
last_reviewed:
---
```

## 6. Core workflows

### Ingest

1. place the original in `01_Raw_Sources/`
2. create or update a `source_page` or registry entry
3. admit only what is supportable into `02_Evidence_Base/`
4. update affected case pages in `04_Case_Wiki/`
5. update `index.md`
6. append to `log.md`

### Query

1. search `index.md` first
2. read evidence and case pages before GTM pages
3. answer from the strongest available support
4. if the answer creates durable structure, file it back into the wiki

### Lint

Look for:

- contradictions not registered
- case pages that outrun evidence
- GTM pages that outrun case truth
- orphan pages
- stale statuses

### Update

When support changes:

1. update the evidence page first
2. update affected case pages
3. update affected GTM pages
4. append to `log.md`

## 7. Support states

Use this compact semantic ladder:

- `unsupported`
- `hypothesis`
- `indication`
- `decision_grade`
- `verification_grade`

Optional internal intermediate states may exist upstream, but do not let a page speak stronger than the nearest honest state.

## 8. Traceability

Minimum chain:

`gtm page` -> `case page` -> `evidence page` -> `source page/raw source`

or

`case page` -> `evidence page` -> `source page/raw source`

If that chain breaks, the page is not ready.

## 9. Default case spine

Each case should be able to answer:

1. what is the case
2. what is misunderstood
3. what decisions are at risk
4. what assumptions are fragile
5. what should not be done yet
6. what to verify first
7. what preliminary financial exposure exists
8. how far the case is from verification-grade

## 10. Obsidian rule

Use wikilinks aggressively.

The LLM writes and maintains the wiki. Humans read, inspect, and challenge it in Obsidian.

## 11. Never do this

- do not rewrite raw source content
- do not turn benchmarks into local proof
- do not smooth away contradictions
- do not turn hypothesis into evidence
- do not turn decision-grade into verification-grade
- do not let GTM copy outrun case truth
- do not let the LLM act as final physical authority
