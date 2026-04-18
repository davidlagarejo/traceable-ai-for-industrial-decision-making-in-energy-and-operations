# Re-Audit Verdict Prompt

Inputs:
- Previous audit artifacts.
- Current audit artifacts.
- Re-audit comparison.

Task:
Explain whether the revised report passed, improved, regressed, or introduced new issues.

Rules:
- Lead with gate status.
- Separate resolved, unresolved, and newly introduced findings.
- Do not collapse quality gaps into compliance violations.

