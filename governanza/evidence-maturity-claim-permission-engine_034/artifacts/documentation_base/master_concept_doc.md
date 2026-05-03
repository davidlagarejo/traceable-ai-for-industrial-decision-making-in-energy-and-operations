# Master Concept Doc — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## core_job

`motor_034` is the permission boundary between raw asset context and admissible downstream output. It converts observed, benchmarked, declared or archetypal evidence into explicit maturity levels, then uses those levels to decide which claims, decisions and report types are actually allowed.

This motor does not ask whether an output would be useful. It asks whether the system has earned the right to say it.

## why_it_exists

By the time this motor runs, the framework may already know several things:

- the target appears to be an asset, facility or headquarters;
- some fields exist in `asset_field_register`;
- public datasets may have been accepted;
- structural reasoning may already expose a contradiction, a dominant variable or a reframed problem;
- the user may even request a stronger report type than the evidence base deserves.

Without an explicit maturity and permission layer, the runtime can drift into premature claims. `motor_034` prevents that drift by translating evidence quality into bounded output permission.

## behavioral_contract

- assign every tracked variable a maturity level instead of leaving evidence quality implicit;
- distinguish observed public evidence, benchmark-only evidence, declared input and missing evidence;
- expose claim permission as `allowed`, `conditional` or `prohibited`;
- expose decision admissibility separately from claim permission;
- determine what report types are allowed now and which are still blocked;
- activate structural problem framing when the structural lane is sufficiently bound, even if the primary report stays conservative.

## non_goals

- it does not fetch sources;
- it does not create the structural contradiction itself;
- it does not compute a final ROI or a full technical recommendation on its own;
- it does not override missing evidence with user confidence or desired narrative.

## downstream_role

The outputs of `motor_034` become the language governor for downstream synthesis, report selection, structural promotion and claim compression. If this motor is too permissive, the rest of the framework becomes overconfident. If it is too conservative, the system loses decision usefulness. Its job is to stay strict but not blind.
