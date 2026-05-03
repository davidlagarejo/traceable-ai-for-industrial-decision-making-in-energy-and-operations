# Test Spec — Global Public Data Routing Engine

Motor ID: motor_035

## happy_path
Input:
- `subject_definition_contract` and `target_definition_contract` both point to a bounded operating asset in New York City, with `target_type = commercial_building`, `decision_intent = acquisition_underwriting`, and `jurisdiction_scope = ["US-NY-NYC"]`.
- `target_classification_object.target_type = OPERATING_ASSET`.
- `subject_gate_passed = true`.
- `technical_substrate_readiness = partial`.
- `observable_clusters` includes populated jurisdiction, geometry, use-program, regulatory, systems, and benchmark-mapping clusters.

Expected output:
- `target_type_classification = OPERATING_ASSET`.
- `routing_ready = true`.
- `jurisdiction_class = high_data_availability_building`.
- `mandatory_sources` includes `nyc_ll84_energy_benchmarking` and `nyc_pluto_property`.
- `report_type_allowed = Minimum Evidence Report`.
- `report_type_prohibited` preserves any incompatible strong-report surface passed from upstream.

## sparse_case
Input:
- bounded building case in Oakland or another permitted public-routing city;
- only the minimum routing clusters are populated: location, jurisdiction, use-program, and regulatory;
- `subject_gate_passed = true`;
- `target_classification_object.target_type = OPERATING_ASSET`.

Expected behavior:
- the motor still emits a complete routing bundle rather than failing for low context density;
- `routing_ready = true` as long as the classification and gate still admit technical routing;
- local property / permit sources remain jurisdiction-specific instead of collapsing to a generic national route;
- `missing_critical_fields` may be non-zero, but the output still contains `mandatory_sources`, `high_priority_sources`, `critical_field_contract`, `critical_field_summary`, and `report_type_switch_recommendation`.

## malformed_input
Malformed or degraded input examples:
- `motor_007` missing or non-dict, so the adapter must fall back to `motor_006.asset_identity_resolution` or `motor_001` rather than crashing.
- `observable_cluster_register` absent or empty, so routing must still emit a bundle but with a higher `missing_critical_fields` count and a weaker report recommendation.
- `subject_gate_passed = false` with `target_classification_object.target_type = CORPORATE_HEADQUARTERS`, even if a postal address is present.

Expected behavior:
- the motor normalizes through fallbacks and emits a bounded degraded result instead of raising;
- technical routing is suppressed when upstream identity/classification does not admit asset-level scraping;
- `mandatory_sources`, `high_priority_sources`, and `optional_sources` are cleared when the case is not technically routable;
- the recommended report surface degrades to a classification-oriented brief instead of a technical report.

## edge_cases
- Houston industrial / process case: `target_type = industrial_plant`, strong operating regime, regulatory, and fuel-energy clusters. Expected result: `target_type_classification = INDUSTRIAL_FACILITY`, `asset_type = industrial_facility`, `tceq_permits_and_emissions` in `mandatory_sources`, and industrial process sources in `high_priority_sources`.
- San Francisco or other HQ-address case: `target_classification_object.target_type = CORPORATE_HEADQUARTERS`, `subject_gate_passed = false`. Expected result: `routing_ready = false`, empty source lists, and a downgraded report type.
- California city routing differentiation: Oakland and Los Angeles must not emit identical mandatory source lists; the route must reflect city/county-specific portals and utility-territory context.
- Jurisdiction ambiguity: if state/city cannot be cleanly resolved from the subject/target contracts, the motor must emit `jurisdiction_class = ambiguous_jurisdiction` or another weak class, not fabricate a high-data route.

## pass_criteria
- Output always contains the nested bundle objects: `target_classification_result`, `jurisdiction_resolution`, `source_routing_plan`, `critical_field_contract`, `critical_field_summary`, `evidence_gating_plan`, `report_type_switch_recommendation`, and `routing_eligibility`.
- The adapter-facing flattened surface is internally consistent with the nested objects: `routing_ready` mirrors `technical_scraping_allowed`, flattened source lists mirror the routed plan after any suppression, and `missing_critical_fields` matches the summary.
- Source routing remains jurisdiction-specific and asset-type-specific.
- Non-technical cases are degraded explicitly rather than silently half-routed.
- The motor does not fetch data, scrape, infer local truth, or mutate upstream contracts.

## fail_criteria
- A headquarters, mailing-address, or otherwise blocked case exits with `routing_ready = true`.
- A technically blocked case still carries non-empty routed source lists after suppression should have happened.
- Two materially different jurisdictions collapse to the same routing plan when the registry and tests expect city/county distinction.
- `report_type_switch_recommendation` contradicts `target_classification_result` or the critical-field gate.
- The motor invents local evidence, emits scraped facts, or upgrades the case beyond what upstream identity and readiness allow.
