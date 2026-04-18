---
name: compare-reference-reports
description: Compare audited reports against curated reference anchors as quality calibration, never as normative law.
---

# Compare Reference Reports

## Purpose

Use reference documents to benchmark quality dimensions such as technical density, methodology, uncertainty, finance, regulation, and senior-grade report maturity.

## Required Inputs

- `normalized_report.json`
- Normalized or raw reference documents.
- `reference_gap_report.json` when available.

## Operating Instructions

1. State clearly that reference anchors calibrate quality but do not define framework compliance.
2. Compare against dimensions, not superficial style.
3. Prefer concrete gaps: missing assumptions, weak financial logic, thin uncertainty treatment, weak regulatory specificity, shallow evidence discussion.
4. Write findings as quality gaps, not violations.
5. Connect every improvement suggestion to a dimension.

## Anti-Patterns

- Do not say "the report violates the framework because the reference does X."
- Do not overfit to one reference report's structure or voice.
- Do not reward verbosity unless it improves auditability.
- Do not confuse market comparison sharpness with marketing copy.

## Example Output

```json
{
  "dimension_name": "financial_seriousness",
  "gap_description": "The report is thinner than reference anchors in financial assumptions.",
  "severity": "medium",
  "targeted_improvement_suggestion": "Separate proxy economics, modeled savings, and validation requirements."
}
```

