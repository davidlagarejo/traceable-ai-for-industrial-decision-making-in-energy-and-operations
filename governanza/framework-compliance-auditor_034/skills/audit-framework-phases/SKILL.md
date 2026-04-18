---
name: audit-framework-phases
description: Apply compiled framework phase contracts to report claims and sections without redesigning the framework.
---

# Audit Framework Phases

## Purpose

Guide an AI auditor through applying already-compiled phase contracts to normalized report claims.
The phase contracts are normative. The report is the object under review. Reference documents are not part of this skill.

## Required Inputs

- `compiled_contract.json`
- `normalized_report.json`
- Claim or section objects with source location metadata.

## Operating Instructions

1. Read the phase contract rule before judging the report claim.
2. Identify the rule role: required, forbidden, hard boundary, caution, conditional, example, note, reporting constraint, traceability expectation, certainty constraint, or verification boundary.
3. Treat examples and notes as interpretive aids, not as standalone hard rules.
4. Separate each phase verdict. Do not merge Phase 0, Phase 1, Phase 3, and Phase 4 into one generic report score.
5. Flag claims that overstate certainty, hide uncertainty, weaken traceability, or imply verification/compliance closure without authorization.
6. Use source locations in every finding.
7. Return structured findings with severity, why flagged, recommended action, and rewrite guidance.

## Anti-Patterns

- Do not invent new epistemic rules.
- Do not treat good prose as compliance.
- Do not treat a table as evidence unless provenance and relevance are visible.
- Do not upgrade Decision-grade claims into Verification-grade claims.
- Do not use reference reports as normative authority.

## Example Input

```json
{
  "claim_id": "claim-00012",
  "raw_text": "The site is verified compliant and will achieve 18% savings.",
  "phase_id": "phase1",
  "rule_kind": "verification_boundary"
}
```

## Example Output

```json
{
  "claim_id": "claim-00012",
  "phase_id": "phase1",
  "violation_type": "verification_language_without_authorization",
  "severity": "high",
  "recommended_fix_type": "soften",
  "rewrite_guidance": "Remove verified/compliant language or add an explicit hardening route."
}
```

