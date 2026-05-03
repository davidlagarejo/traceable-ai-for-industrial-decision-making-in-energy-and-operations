# Failure Modes Spec — Global Public Data Routing Engine

Motor ID: motor_035

## failure_modes_list
- `HQ_PROMOTION_TO_TECHNICAL_ROUTE`: a headquarters, mailing-address, or otherwise non-operating target exits as technically routable -> the discovery layer begins scraping and benchmarking as if the case were a bounded operating asset -> clear routed source lists, downgrade the report surface, and force classification-first handling.
- `JURISDICTION_COLLAPSE`: distinct city/county routing contexts produce the same source plan -> mandatory local property, permit, or utility routes are lost -> preserve jurisdiction resolution before source-plan assembly and fail any shortcut that replaces local portals with a generic state or national route.
- `BENCHMARK_SUBSTITUTION_LEAK`: benchmark or entity-level context is allowed to stand in for a source family explicitly marked as non-substitutable -> later motors interpret weak public context as if it were property-, permit-, or utility-grade evidence -> keep `disallowed_substitutions` explicit and suppress technical routing when critical field rules are not satisfied.
- `CRITICAL_FIELD_GATE_MISREAD`: missing critical fields are counted incorrectly or ignored -> the report surface and routing readiness no longer match the actual observable context -> recompute `critical_field_contract` and `critical_field_summary` deterministically from the asset-type-specific gate rules.
- `REPORT_SURFACE_DRIFT`: `report_type_switch_recommendation` contradicts `target_classification_result` or upstream report prohibitions -> the runtime can advertise a stronger output surface than the case deserves -> keep report switching downstream of classification and gating, and preserve upstream prohibitions without silent override.

## anti_patterns
- Designing routing around what is easy to scrape instead of around what the jurisdiction and asset type require.
- Treating `subject_gate_passed` as a soft hint instead of a hard routing boundary.
- Promoting any postal address with a plausible building name into an operating-asset route without respecting upstream classification.
- Flattening city-specific California or Texas routing into a single state-level public-data recipe.
- Mutating upstream contracts or trying to “repair” missing identity context inside this motor instead of publishing a degraded route.

## degradation_signals
- repeated cases with `routing_ready = true` but empty or obviously generic mandatory source sets;
- multiple jurisdictions returning the same `mandatory_sources` and `high_priority_sources` ordering despite different local portals in the source registry;
- rising `missing_critical_fields` without any corresponding degradation of `report_type_allowed`;
- frequent appearance of `disallowed_substitutions` in output while downstream still behaves as if the prohibited substitution were admissible;
- mismatch between flattened fields like `routing_ready` or `report_type_allowed` and their nested source objects.

## expensive_errors
- Scraping a non-operating target as if it were a real asset. It is expensive because downstream search, public data materialization, and reporting all need rollback. Prevent it by honoring `target_classification_result.technical_scraping_allowed` as a hard stop.
- Losing jurisdiction specificity early. It is expensive because later debugging looks like “bad discovery” when the actual fault was route selection. Prevent it by treating `jurisdiction_resolution` as the first-class selector for source plans.
- Treating benchmark context as local truth. It is expensive because it contaminates multiple downstream lanes with inadmissible evidence posture. Prevent it by enforcing `disallowed_substitutions` and critical-field minimum layers.
- Publishing a stronger report type than the evidence gate permits. It is expensive because visible deliverables outrun admissible support and force cross-lane cleanup. Prevent it by keeping report switching downstream of both classification and missing-critical-field counts.
