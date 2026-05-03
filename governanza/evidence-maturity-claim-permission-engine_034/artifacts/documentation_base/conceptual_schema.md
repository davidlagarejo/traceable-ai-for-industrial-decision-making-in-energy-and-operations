# Conceptual Schema — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## maturity_model

The engine works with a five-level maturity ladder:

- `L0`: missing, blocked or not observed;
- `L1`: weak or declared-only support;
- `L2`: usable but still conditional support;
- `L3`: strong public or confirmed asset-level support;
- `L4`: highest-confidence decision-grade support where the runtime has enough direct grounding.

The exact numeric threshold is less important than the discipline: stronger claims require stronger maturity.

## core_objects

- `VariableMaturityRecord`: one row per tracked variable, including value, maturity level, source scope, authority, uncertainty and unlocked decisions.
- `ClaimPermissionRecord`: one row per potential claim, with the minimum maturity needed and the upgrade path if blocked.
- `DecisionPermissionRecord`: one row per decision family, exposing the current bottleneck and the allowed action.
- `ClusterMaturityRecord`: one row per cluster such as identity, geometry, systems or regulatory context.
- `CanonicalProblemFrame`: the structural framing record that becomes active once the evidence and contradiction state are sufficiently bounded.

## permission_layers

The motor evaluates permission on four layers at once:

1. variable maturity;
2. claim permission;
3. decision admissibility;
4. report/output-mode eligibility.

Each layer must become more restrictive, not less. A blocked variable may not leak into an allowed decision or full technical report through a side channel.

## structural_extension

When structural motors are present, `motor_034` extends beyond generic screening:

- it creates `structural_claim_permission_register`;
- it packages cross-layer claim contracts;
- it classifies structural output modes;
- it decides whether a structural mode can be primary or must remain secondary.

This means the motor is both a maturity engine and a governed promotion gate between baseline asset context and structural intelligence.
