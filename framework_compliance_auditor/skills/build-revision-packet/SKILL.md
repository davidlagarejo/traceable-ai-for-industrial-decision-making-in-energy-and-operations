---
name: build-revision-packet
description: Convert audit findings into precise revision instructions another AI can execute safely.
---

# Build Revision Packet

## Purpose

Turn compliance findings and reference quality gaps into minimally ambiguous edits for a revision agent.

## Required Inputs

- `claim_violation_register.json`
- `phase_compliance_report.json`
- `reference_gap_report.json`
- `compiled_contract.json`

## Operating Instructions

1. Group fixes by section.
2. Identify the exact problematic claim or section.
3. Explain why the issue matters in phase-boundary terms.
4. Include normative source for compliance issues.
5. Include comparative source only for reference quality gaps.
6. Assign one explicit action: keep, remove, soften, qualify, split, relocate, defer, block, add traceability, add caveat, or add hardening path.
7. Provide safer language only when it reduces ambiguity without inventing evidence.

## Anti-Patterns

- Do not ask the revision agent to "make it better" without exact instructions.
- Do not let the revision agent invent missing citations.
- Do not collapse multiple incompatible fixes into one instruction.
- Do not preserve unsupported executive-facing overclaims.

## Example Output

```json
{
  "section_id": "Executive Summary",
  "claim_id": "claim-00003",
  "action": "soften",
  "explicit_rewrite_instruction": "Replace verification-grade closure with Decision-grade public-data language.",
  "safer_language_examples": ["Public-data indicators suggest this risk may be present."]
}
```

