# Operational Rules — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## rule_1_missing_critical_fields_block_strong_claims

If critical identity, geometry or baseline variables are missing, strong claims must remain blocked. A canonical example is `GFA`: without it, the motor cannot allow strong numeric EUI or ROI claims.

## rule_2_benchmark_only_is_not_decision_grade

Benchmark-only signals may support screening and directional language, but they do not justify strong savings, ROI-scenario or technical-decision closure. This rule protects the runtime from turning benchmark hints into asset-specific promises.

## rule_3_declared_input_is_capped

Rows that come in as declared input only must remain capped at a lower maturity ceiling. The downgrade must survive all the way to `variable_maturity_register`, not disappear because the value itself looks plausible.

## rule_4_dataset_acceptance_needs_observed_field_support

Accepted datasets can strengthen maturity only when the relevant observed field value is actually present. Dataset acceptance by itself must not upgrade a blocking or empty field into a confirmed system fact.

## rule_5_regulatory_claims_are_jurisdiction_scoped

Jurisdiction-specific regulatory claims, especially LL97 pathways, are allowed only in the appropriate scope. Non-NYC contexts must fall back to generic compliance evidence packs and generic screening logic.

## rule_6_structural_lane_can_activate_without_overpromoting

Structural contradiction, dominant-variable and minimum-evidence signals can activate `canonical_problem_frame` and structural output modes. That activation does not automatically grant a stronger primary report type. Structural framing and report promotion are separate gates.

## rule_7_requested_report_type_can_be_clamped

The requested or inherited report type from `motor_007` is advisory. If the evidence base and substrate readiness do not support it, `motor_034` must downgrade the recommendation and explicitly show what remains prohibited.

## rule_8_claim_contracts_must_show_why

If a claim is allowed, conditional or prohibited, the output must preserve the evidence reasoning, required variables, missing evidence and upgrade path so downstream synthesis cannot flatten the logic into an unexplained label.
