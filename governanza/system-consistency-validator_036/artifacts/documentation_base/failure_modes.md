# Failure Modes — System Consistency Validator

Motor ID: motor_036

## primary_failures

- `MODE_DRIFT`: visible report mode, outline mode and thesis mode no longer match.
- `CLAIM_TRACE_GAP`: visible claim sections exist without claim contracts or statement traces.
- `BODY_LEAKAGE`: appendix-grade or raw technical content leaks into the client-facing body.
- `SUMMARY_MATRIX_MISMATCH`: governance summaries disagree with the authoritative claim matrix.
- `BOUNDARY_FALSE_CERTAINTY`: structurally invalid comparisons, declared input or unresolved local-binding ambiguity are rendered as if they were resolved.
- `CASE_CONTAMINATION`: charts, entity labels or chapter inventory refer to a foreign case or template scaffold.

## why_these_failures_matter

This motor protects the last integrity boundary before rendering. A failure here means the report can still look polished while being systemically wrong. That is more dangerous than an obvious crash because it can ship confident incoherence.

## required_response

When a critical failure appears, the fix is not to suppress the warning. The fix is to restore alignment between:

- authoritative upstream registers;
- visible report sections;
- render inventory;
- and the bounded permission state.

If the package cannot satisfy that alignment, render must remain blocked.
