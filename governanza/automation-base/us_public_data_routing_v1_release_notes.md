# US Public Data Routing v1 Release Notes

Release date: `2026-04-28`

## What shipped

`USA v1` is the first production-grade routing layer that decides where the framework may look before technical scraping starts.

Delivered scope:

- target classification before technical discovery
- jurisdiction resolution for `NYC`, `California`, and `Texas`
- asset-type routing for:
  - `commercial_building`
  - `multifamily`
  - `warehouse_logistics`
  - `industrial_facility`
  - `manufacturing_facility` via the industrial process route
  - `data_center`
- source routing plan with:
  - `mandatory_sources`
  - `high_priority_sources`
  - `optional_sources`
  - `disallowed_substitutions`
- routing-linked contamination rejection
- routing-plan gate propagation into report publication
- visible routing metadata in dashboard/API/manifests

## Sovereign runtime path

- `motor_035` is the routing authority
- `motor_028` executes only the approved route
- `motor_012` converts routing gaps into evidence gaps
- `motor_024/025/027` can downgrade or block delivery when mandatory route execution fails

## Jurisdiction coverage in v1

### NYC

Strongest implemented route:

- `NYC DOF`
- `PLUTO`
- `LL84`
- `LL97 Covered Buildings List`
- `DOB permits`

### California

Implemented route:

- `San Francisco benchmarking`
- `San Francisco assessor`
- `San Francisco permits`
- `CEC guidance`
- `Title 24`
- `CALGreen`
- `PG&E routing context`

Industrial California route:

- `CARB mandatory GHG reporting context`
- `CalEPA Regulated Site Portal / Unified Program context`

This industrial California path is intentionally bounded as official regulatory context unless a facility-specific public match is observed.

### Texas

Implemented route:

- `county appraisal routing`
- `TCEQ permits and emissions`
- `state environmental permit routing`
- `ERCOT context`

Manufacturing subtype coverage:

- `manufacturing_facility` now has its own golden seed and certification path
- it now certifies as a full run, not only as a routing/evidence subgraph
- it remains intentionally routed through the industrial permit/emissions/process contract instead of generic building logic
- visible report content is now guarded against leasing/subletting leakage for manufacturing-family assets
- the golden manufacturing case is now anchored on `Wilsonart Temple North Laminate Facility`, which promotes `TCEQ` asset-level permit/emissions evidence into the field register

## Critical fix included in this release

`Prologis / PIER 1 BAY 1, San Francisco, CA` previously exposed a real routing leak: NYC `LL97` language could enter a non-NYC classification brief.

This release removes that failure mode:

- no `LL97` contamination in classification briefs outside NYC
- no `ll97_penalty_screening_claim` in non-NYC contexts
- routing bundle now reaches report package and delivery manifest

Validated full run:

- `run:6ec2b537806832ae`

## Release baseline

Frozen artifacts:

- `governanza/automation-base/us_public_data_routing_v1_release_baseline.md`
- `governanza/automation-base/us_public_data_routing_v1_release_baseline.json`
- `governanza/automation-base/us_public_data_routing_matrix.md`
- `governanza/automation-base/us_public_data_routing_onboarding_checklist.md`

## Re-certification

Use:

```bash
python3 runtime-orchestrator/scripts/certify_us_public_data_routing_v1.py
```

Outputs:

- `governanza/automation-base/us_public_data_routing_v1_certification_latest.json`
- `governanza/automation-base/us_public_data_routing_v1_certification_latest.md`

## Known bounded limitations

- California and Texas remain more case-match sensitive than NYC.
- `CA industrial` currently ships with strong official context, not guaranteed facility-specific public matching.
- county/property portals and city permit systems remain heterogeneous across USA jurisdictions.

## Classification

This release is classified as:

- `A) robusto y listo para implementación`

Reason:

- the routing/governance architecture is now complete and enforceable
- degradation works before technical overreach
- the critical HQ contamination case is fixed
- remaining gaps are mostly public-data coverage variance, not systemic design weakness
