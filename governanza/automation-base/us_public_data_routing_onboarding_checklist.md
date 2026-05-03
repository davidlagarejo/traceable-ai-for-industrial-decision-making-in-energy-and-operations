# USA Public Data Routing Onboarding Checklist

Use this checklist when adding a new USA jurisdiction, city route, or asset-family route to `Global Public Data Routing v1`.

## 1. Jurisdiction Definition

- define `country`, `state`, `city`, and `county`
- define `utility_territory`
- define `climate_zone_ashrae`
- define `jurisdiction_class`
- define `regulatory_stack`

Acceptance:
- the jurisdiction resolver can emit a stable `JurisdictionResolution` object from address-level input

## 2. Asset-Type Fit

- decide which asset families are truly supported:
  - `commercial_building`
  - `multifamily`
  - `warehouse_logistics`
  - `industrial_facility`
  - `data_center`
- define route-specific critical field families
- define prohibited shortcuts for that asset family

Acceptance:
- the asset-type router emits a route that changes source priorities and evidence expectations

## 3. Source Registry Rows

- add `mandatory_sources`
- add `high_priority_sources`
- add `optional_sources`
- add `disallowed_substitutions`
- classify each source by:
  - `layer`
  - `access_method`
  - `authority`
  - `update_frequency`
  - `fields`
  - `limitations`

Acceptance:
- the route resolves a non-empty `SourceRoutingPlan`

## 4. Executor Policy

For every routed source, choose one and document it explicitly:

- `real asset-capable executor`
- `bounded official context executor`
- `not yet implemented`

Rules:
- do not label guidance pages as asset-level evidence
- do not label portal shells as matched facility evidence
- do not use unofficial mirrors when an official source exists

Acceptance:
- no source remains ambiguous about whether it is asset-level or context-only

## 5. Scope and Authority

- map `source_scope`
- map `source_family`
- map `authority_score`
- map `applicability`

Acceptance:
- `ENTITY_LEVEL`, `PORTFOLIO_LEVEL`, `JURISDICTION_LEVEL`, and `BENCHMARK_LEVEL` cannot silently fill `ASSET_LEVEL` critical fields

## 6. Contamination Rules

- define expected city/state
- define expected utility territory
- define expected regulatory stack
- define expected asset class
- define foreign-jurisdiction tokens that should be rejected

Acceptance:
- mismatched source payloads are rejected before they contaminate `motor_012` or visible reporting

## 7. Critical Field Contract

At minimum, define how the route will attempt:

- `address_confirmed`
- `size_or_gfa`
- `use_or_occupancy`
- `year_built` or physical vintage clue
- `energy_baseline_or_proxy`
- `fuel_type`
- `system_presence`
- `regulatory_applicability`

Acceptance:
- if more than 3 remain missing, the route downgrades to `Decision-Blocked`

## 8. Golden Seed

- create one bounded-asset seed
- create one degraded seed if possible:
  - HQ
  - ambiguous
  - mailing

Acceptance:
- both the strong and degraded path can be exercised deterministically

## 9. Tests

Minimum required:

- registry test
- routing-engine test
- executor test for every new official source
- contamination test for foreign city/state or wrong route
- certification test with one live or curated route case

Acceptance:
- new route cannot merge without routing and contamination coverage

## 10. Release Decision

A route is ready to freeze only if:

- classification is correct
- routing is visible downstream
- mandatory-source gaps can degrade/block
- no foreign-jurisdiction leakage appears in classification briefs
- official-context sources are not overstated as matched asset evidence

If any of the above fails:

- do not freeze
- keep the route marked as bounded or partial
