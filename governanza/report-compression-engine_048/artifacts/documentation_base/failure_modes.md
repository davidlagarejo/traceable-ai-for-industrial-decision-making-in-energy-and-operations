# Failure Modes — Report Compression Engine

Motor ID: motor_048

## primary_failures

- `BODY_REEXPANSION`: the engine reopens too many body sections and loses compression discipline.
- `FALSE_STRUCTURAL_BODY`: inadmissible cases still emit a structural body.
- `CONGRUENCE_BODY_SPLIT`: congruence support creates a second technical report inside the body.
- `TRACEABILITY_LOSS`: prompt-block or authority lineage disappears during compression.
- `UNEXPLAINED_DEMOTION`: body-to-appendix moves happen without explicit justification.

## why_these_failures_matter

This motor shapes what the client actually sees. If it fails, the report can still be correct in substance but unusable, bloated or non-traceable. Worse, it can quietly reintroduce structural claims in formats the runtime had already bounded.

## required_response

The fix is to restore compression discipline, not to hide the evidence. The primary body stays small, the appendix stays explicit, and every demotion or embedded congruence signal remains auditable.
