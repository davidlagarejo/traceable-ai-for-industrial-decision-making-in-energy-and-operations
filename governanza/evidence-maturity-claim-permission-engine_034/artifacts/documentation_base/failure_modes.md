# Failure Modes — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## primary_failures

- `PREMATURE_PERMISSION`: strong claims or decisions become allowed before maturity actually supports them.
- `DOWNGRADE_LOSS`: declared or weak evidence stops being capped and silently inflates downstream permission.
- `DATASET_INFLATION`: accepted public datasets upgrade maturity without a corresponding observed field value.
- `JURISDICTION_LEAKAGE`: LL97 or other jurisdiction-specific claim logic appears outside the valid geography.
- `STRUCTURAL_OVERPROMOTION`: structural framing exists, so the engine wrongly upgrades the primary report type.
- `CANONICAL_FRAME_SUPPRESSION`: the structural lane is sufficiently bounded, but the canonical problem frame never activates.
- `READINESS_DRIFT`: `report_readiness_register`, classifier tables and `maturity_summary` disagree with each other.

## why_these_failures_matter

This motor sits on the permission boundary. A small mistake here propagates everywhere:

- reports become overstated;
- economic claims become unsafe;
- compliance framing becomes jurisdictionally wrong;
- structural intelligence may be suppressed or over-amplified.

## required_response

When one of these failures appears, the fix must preserve two properties:

- keep the runtime conservative under weak evidence;
- preserve utility under bounded but real evidence.

The correct answer is usually not "make it more permissive" or "make it always block". The correct answer is to restore the exact maturity-to-permission mapping.
