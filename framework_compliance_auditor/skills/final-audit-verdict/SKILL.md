---
name: final-audit-verdict
description: Produce the final human-readable pass/fail explanation from structured audit artifacts.
---

# Final Audit Verdict

## Purpose

Build a concise human-readable audit summary from machine artifacts while preserving role boundaries and gate logic.

## Required Inputs

- `phase_compliance_report.json`
- `claim_violation_register.json`
- `reference_gap_report.json`
- `audit_scorecard.json`
- `revision_packet.json`

## Operating Instructions

1. Lead with compliance gate and quality gate.
2. Separate contract violations from reference quality gaps.
3. List highest-severity findings first.
4. Explain whether revisions are blocked, recommended, or optional.
5. Use exact phase IDs and finding IDs.
6. Include the next action needed for re-audit.

## Anti-Patterns

- Do not bury critical compliance failures under quality discussion.
- Do not treat style improvements as compliance fixes.
- Do not claim the report is verified unless the audit artifacts support that conclusion.
- Do not omit unresolved high-severity findings.

## Example Output

```markdown
Compliance gate: fail

The report fails Phase 1 and Phase 4 because several executive-facing claims imply verification-grade closure without a hardening route. Reference comparison also shows a medium financial seriousness gap, but that is a quality issue rather than a contract violation.
```

