# Technical Schema — Global Public Data Routing Engine

Motor ID: motor_035

## entities
- `TargetClassificationResult`: normalized routing decision derived from upstream target classification plus subject gate status. It states whether the case is an operating asset, whether asset identity is confirmed enough for technical scraping, what report surface applies if blocked, and why the current route is admissible or blocked.
- `JurisdictionResolution`: normalized US routing context for one target. It carries the state/city/county anchor, utility territory, ASHRAE climate zone, jurisdiction class, and regulatory stack that control which public sources are relevant.
- `SourceRoutingEntry`: one routed public source option with its source key, layer, access method, expected fields, authority tier, routing priority, and substitution limits.
- `SourceRoutingPlan`: ordered public-source plan for one `(jurisdiction, asset_type, decision_type)` combination. It groups `mandatory_sources`, `high_priority_sources`, `optional_sources`, `disallowed_substitutions`, and routing notes.
- `CriticalFieldStatus`: one critical evidence requirement row returned in `critical_field_contract`. It records whether a required field family is currently covered, missing, or blocked given current observable clusters and subject-gate posture.
- `CriticalFieldSummary`: compact rollup of the critical-field contract with total required fields, number missing, and the maximum number of missing fields allowed before technical routing must degrade.
- `EvidenceGatingPlan`: static routing gate definition for one asset type. It defines which critical fields matter and which report types correspond to blocked, partial, or sufficient public evidence.
- `ReportTypeSwitchRecommendation`: deterministic recommendation for the visible report surface after combining target class, technical-substrate readiness, and missing critical fields.
- `RoutingEligibility`: compact runtime gate object summarizing whether technical scraping is currently allowed, which normalized decision type applies, and how ready the technical substrate is.
- `RoutingBundleSurface`: flattened adapter-facing output published by `motor_035`, combining nested bundle content with convenience fields like `routing_ready`, `asset_type`, `mandatory_sources`, `report_type_allowed`, and `missing_critical_fields`.

## fields
`TargetClassificationResult`
- `target_type: str` (required) — normalized target class such as `OPERATING_ASSET`, `CORPORATE_HEADQUARTERS`, or `INDUSTRIAL_FACILITY`.
- `classification_confidence: str` (required) — confidence inherited from upstream classification normalization.
- `asset_identity_confirmed: bool` (required) — whether the current route treats asset identity as sufficiently confirmed for technical routing.
- `technical_scraping_allowed: bool` (required) — hard gate for technical public discovery.
- `report_type_if_blocked: str` (required) — downgraded report surface when technical routing is not yet admissible.
- `reason: str` (required) — bounded explanation of why the route is allowed or blocked.

`JurisdictionResolution`
- `country: str` (required)
- `state: str` (required)
- `city: str` (required)
- `county: str` (required)
- `utility_territory: str` (required)
- `climate_zone_ashrae: str` (required)
- `jurisdiction_class: str` (required) — routing class such as `high_data_availability_building`, `utility_and_permit_building`, or `industrial_regulated`.
- `regulatory_stack: list[str]` (required) — ordered stack of governing public routing contexts.

`SourceRoutingEntry`
- `source_key: str` (required) — stable registry key such as `nyc_ll84_energy_benchmarking`.
- `source_name: str` (required) — human-readable source label.
- `layer: str` (required) — routing layer like `energy`, `property`, `permit`, `utility`, or `industrial_environment`.
- `access_method: str` (required) — route mechanism such as `api`, `portal`, `download`, or `web_page`.
- `fields: list[str]` (required) — field families expected from this source.
- `authority: str` (required) — source authority tier.
- `update_frequency: str` (required) — cadence expectation used for routing realism.
- `use: str` (required) — why this source matters in the current route.
- `limitations: str` (required) — bounded caveats or insufficiencies of the source.
- `priority: str` (required) — `mandatory`, `high_priority`, or `optional`.
- `disallowed_as_substitute_for: list[str]` (required) — source families this entry cannot replace.

`SourceRoutingPlan`
- `jurisdiction: str` (required) — jurisdiction routing key family such as `US-NY-NYC`.
- `asset_type: str` (required) — normalized routed asset type such as `commercial_building` or `industrial_facility`.
- `decision_type: str` (required) — normalized decision intent used by routing.
- `mandatory_sources: list[dict]` (required)
- `high_priority_sources: list[dict]` (required)
- `optional_sources: list[dict]` (required)
- `disallowed_substitutions: list[str]` (required)
- `routing_notes: list[str]` (required)

`CriticalFieldStatus`
- `field_name: str` (required)
- `required: bool` (required)
- `current_status: str` (required) — field coverage state under current observable clusters.
- `rationale: str` (required)
- `minimum_source_layer: str` (required)
- `prohibited_substitutions: list[str]` (required)
- `notes: str` (required)

`CriticalFieldSummary`
- `total_critical_fields: int` (required)
- `missing_critical_fields: int` (required)
- `max_missing_before_block: int` (required)

`EvidenceGatingPlan`
- `critical_fields: list[dict]` (required)
- `max_missing_critical_fields: int` (required)
- `blocked_report_type: str` (required)
- `partial_report_type: str` (required)
- `sufficient_report_type: str` (required)

`ReportTypeSwitchRecommendation`
- `recommended_report_type: str` (required)
- `prohibited_report_types: list[str]` (required)
- `reason: str` (required)

`RoutingEligibility`
- `technical_scraping_allowed: bool` (required)
- `decision_type: str` (required)
- `technical_substrate_readiness: str` (required)

`RoutingBundleSurface`
- `target_type_classification: str` (required)
- `asset_type: str` (required)
- `decision_type: str` (required)
- `routing_ready: bool` (required)
- `jurisdiction_class: str` (required)
- `regulatory_stack: list[str]` (required)
- `mandatory_sources: list[dict]` (required)
- `high_priority_sources: list[dict]` (required)
- `optional_sources: list[dict]` (required)
- `disallowed_substitutions: list[str]` (required)
- `missing_critical_fields: int` (required)
- `report_type_allowed: str` (required)
- `report_type_prohibited: list[str]` (required)

## relationships
- `RoutingBundleSurface.target_type_classification` is a flattened projection of `TargetClassificationResult.target_type`.
- `RoutingEligibility.technical_scraping_allowed` must match `TargetClassificationResult.technical_scraping_allowed`.
- `SourceRoutingPlan` is selected from `JurisdictionResolution` plus normalized `asset_type` and `decision_type`.
- `SourceRoutingPlan.mandatory_sources[]`, `high_priority_sources[]`, and `optional_sources[]` contain serialized `SourceRoutingEntry` rows.
- `CriticalFieldStatus[]` is derived from asset-type-specific rules plus the current `observable_clusters` passed in by upstream motors.
- `CriticalFieldSummary` is a rollup over the emitted `CriticalFieldStatus[]`.
- `EvidenceGatingPlan` governs how `CriticalFieldSummary.missing_critical_fields` affects `ReportTypeSwitchRecommendation`.
- `ReportTypeSwitchRecommendation` depends on `TargetClassificationResult`, `EvidenceGatingPlan`, technical-substrate readiness, and upstream report prohibitions.
- When `TargetClassificationResult.technical_scraping_allowed` is false, the adapter must suppress all routed source lists even if the underlying `SourceRoutingPlan` exists.

## identifiers
- This motor does not mint persistent object-level record IDs in runtime output.
- `SourceRoutingEntry.source_key` is the stable registry identifier for individual routed sources.
- `SourceRoutingPlan` is logically identified by the composite `(jurisdiction, asset_type, decision_type)`.
- `TargetClassificationResult` is logically identified by the routed target instance and its normalized target class.
- `JurisdictionResolution` is logically identified by `(country, state, city, county, asset_type routing context)`.
- `CriticalFieldStatus.field_name` is the stable selector for each critical requirement row.
- `RoutingBundleSurface` is logically keyed by the upstream target/subject definition pair plus the current routing rule set; it is recomputed, not stored as a persistent registry record.

## versioning
- Runtime output from `motor_035` is emitted as recomputed dictionaries and dataclass serializations; it does not currently carry explicit `version_id`, `version_hash`, or `parent_id` fields.
- Version identity is therefore inherited from three bounded sources: the upstream classification contracts, the static public-routing registries, and the rule modules that define jurisdiction resolution, source routing, and evidence gating.
- Material changes to `ALL_SOURCE_REGISTRY`, asset-type critical-field rules, target-taxonomy normalization, or report-switching logic should be treated as schema-significant changes even though the runtime bundle itself does not expose a version field.
- `SourceRoutingEntry.source_key` remains stable across routing-bundle rebuilds; priority placement may change only when routing rules or jurisdiction interpretation change.
- `RoutingBundleSurface` should be considered deterministic for the same upstream contracts, observable clusters, and routing-rule code state.

## lineage
- The motor consumes upstream `subject_definition_contract`, `target_definition_contract`, `target_classification_object`, subject-gate state, technical-substrate readiness, and observable clusters from `motor_001`, `motor_006`, and `motor_007`.
- `TargetClassificationResult.reason` and `ReportTypeSwitchRecommendation.reason` provide the primary human-readable lineage for why routing was allowed, degraded, or blocked.
- `SourceRoutingEntry.source_key` and `SourceRoutingPlan.routing_notes` preserve lineage back to the static public-routing registry and jurisdiction-router rules rather than to scraped evidence.
- `CriticalFieldStatus` and `CriticalFieldSummary` preserve lineage to the observable-cluster state that was actually present at run time.
- This motor does not fetch public evidence, mutate upstream contracts, or attach `source_ref`/`produced_at` fields to output rows; lineage remains interpretive and rule-based, not evidence-materializing.
