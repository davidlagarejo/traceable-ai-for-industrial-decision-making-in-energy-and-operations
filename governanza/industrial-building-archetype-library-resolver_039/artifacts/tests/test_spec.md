# Test Spec — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## happy_path
Input:
- `target_definition.target_type = commercial_building`;
- `target_definition.jurisdiction_scope = ["US-NY-NYC"]`;
- `target_definition.target_name` or `facility_prior.asset_name` implies a tower-scale commercial asset such as One Vanderbilt;
- `target_classification_object.target_type = OPERATING_ASSET`;
- `asset_field_register` contains tower-scale clues such as large `GFA`, high `floor_count`, and NYC energy-benchmark context;
- `dataset_coverage_register` or `source_register` contains accepted NYC public signals.

Expected output:
- `selected_archetype_id = commercial_office_tower_nyc`;
- `match_confidence = high`;
- `resolver_state = selected`;
- `dominant_variable_hypotheses` includes variables like `central_plant`, `tenant_metering`, `after_hours_occupancy`, and `LL97_pathway`;
- every dominant variable row remains bounded as `ARCHETYPAL_PRIOR`, not observed local truth;
- `anti_hallucination_contract` explicitly forbids decision closure and final redesign use.

## sparse_case
Input:
- `target_classification_object.target_type = OPERATING_ASSET`;
- target type is a generic operating family such as `warehouse_distribution` or `cold_chain_facility`;
- `asset_field_register`, `dataset_coverage_register`, and `source_register` are sparse and do not activate a narrower specific archetype.

Expected behavior:
- the motor still emits a complete structural prior bundle;
- selection falls back to a generic valid archetype such as `logistics_warehouse_generic` or `cold_chain_generic`;
- `match_confidence` degrades to `medium` instead of overstating certainty;
- `dominant_variable_hypotheses` remains non-empty for generic operating assets, but every row still carries archetypal evidence-state only.

## malformed_input
Malformed or weak input examples:
- `facility_prior` missing or empty, forcing the adapter to fall back to `motor_007.target_definition_contract`.
- `asset_field_register`, `dataset_coverage_register`, or `source_register` absent, empty, or structurally weak enough that no bounded specific archetype can be selected.
- `target_classification_object` indicates a non-operating or ambiguous target even though the target name sounds operational.

Expected behavior:
- the resolver does not crash when it has to use fallbacks or empty collections;
- if bounded structural modeling is not admissible, the output collapses to `target_not_yet_structurally_modelable`;
- `dominant_variable_count = 0` in that unresolved state;
- `selected_archetype_evidence_state = INADMISSIBLE_CLAIM`.

## edge_cases
- Laminate manufacturing case with public process clues such as `laminate`, `resin`, `curing`, or `pressing`. Expected result: `selected_archetype_id = manufacturing_laminate`, `match_confidence = high`, and hypotheses including `resin_curing_profile`.
- Utility-heavy industrial site with clues like `central utility`, `utility island`, `power factor`, or `large motors`. Expected result: `selected_archetype_id = utility_heavy_site_generic`.
- NYC commercial building with accepted NYC public sources but without tower-scale clues. Expected result: `selected_archetype_id = commercial_building_generic`, not the stronger NYC tower archetype.
- Headquarters or mailing-address target. Expected result: downgrade to `target_not_yet_structurally_modelable` regardless of prestige or naming cues.

## pass_criteria
- Output always includes `archetype_resolution`, `archetype_library_register`, `archetype_selection_basis_register`, `dominant_variable_hypotheses`, `archetype_minimum_evidence_register`, `system_abstraction_seed`, and `anti_hallucination_contract`.
- Flattened fields `selected_archetype_id`, `selected_archetype_label`, `match_confidence`, `resolver_state`, and `dominant_variable_count` stay consistent with the nested bundle.
- Specific archetypes activate only from the bounded resolver rules that exist in code.
- Unresolved or non-operating targets never emit a structurally modelable prior.
- The motor never upgrades an archetypal prior into observed local truth.

## fail_criteria
- `selected_archetype_id` suggests a specific narrow archetype without matching bounded clues in target type, jurisdiction, or hints.
- `dominant_variable_count` disagrees with the actual number of hypothesis rows.
- An unresolved target still emits non-empty `dominant_variable_hypotheses`.
- `anti_hallucination_contract` is missing, weakened, or contradicts `archetype_resolution.archetype_evidence_state`.
- The motor emits comparables, ROI, savings, CAPEX, or final redesign recommendations instead of only structural priors.
