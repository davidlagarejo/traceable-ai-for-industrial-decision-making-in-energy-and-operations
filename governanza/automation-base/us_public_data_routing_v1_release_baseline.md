# US Public Data Routing v1 Release Baseline

Frozen on: `2026-04-28`

## Scope

This baseline freezes the first production-grade release of the `Global Public Data Routing System (USA) v1`.

The system is considered frozen at the routing/governance level when these conditions hold:

- `motor_035` is the sovereign pre-scrape routing engine.
- `motor_028` executes discovery only from the approved routing plan.
- mandatory-source gaps propagate through `motor_012`, `motor_024`, `motor_025`, and `motor_027`.
- target classification can downgrade or block technical discovery before technical scraping begins.
- routing metadata is visible in dashboard/API/report manifests.
- contamination tied to routing context can reject mismatched sources before report generation.

## Frozen Runtime Surface

Core modules frozen in this baseline:

- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py`
- `runtime-orchestrator/dashboard.py`

Reference matrix:

- `governanza/automation-base/us_public_data_routing_matrix.md`
- `governanza/automation-base/us_public_data_routing_matrix.json`

## Golden Cases

The following cases are the canonical release checks for USA v1.

| Case | Seed | Jurisdiction | Target Class | Validation Scope | Expected Output |
|---|---|---|---|---|---|
| NYC bounded operating asset | `runtime-orchestrator/inputs/ova_inputs.json` | `US-NY-NYC` | `OPERATING_ASSET` | full run | NYC route active; `PLUTO/LL84/DOB/LL97/DOF` path available; technical report still allowed to downgrade on evidence bottlenecks |
| California bounded building | `runtime-orchestrator/inputs/sfb_inputs.json` | `US-CA-SF` | `OPERATING_ASSET` | routing/evidence subgraph | SF benchmarking/assessor/permits routing active; CA guidance and PG&E context visible; no non-CA contamination |
| Los Angeles bounded building | `runtime-orchestrator/inputs/lab_inputs.json` | `US-CA-LA` | `OPERATING_ASSET` | routing/evidence subgraph | LA assessor API route active; LA benchmarking and permit layers routed correctly; CA code and utility context remain bounded to Los Angeles |
| Texas bounded industrial facility | `runtime-orchestrator/inputs/txi_inputs.json` | `US-TX` | `OPERATING_ASSET` | routing/evidence subgraph | TCEQ + state environmental route active; ERCOT/property routing visible; industrial asset route never falls back to issuer context |
| Houston bounded building | `runtime-orchestrator/inputs/hou_inputs.json` | `US-TX-HOUSTON` | `OPERATING_ASSET` | routing/evidence subgraph | HCAD public-data route active; Houston permit and CenterPoint/ERCOT context visible; no fake asset-level parcel match is claimed |
| Texas bounded manufacturing facility | `runtime-orchestrator/inputs/mfg_wilsonart_inputs.json` | `US-TX` | `OPERATING_ASSET` | full run | Manufacturing subtype preserves the industrial route end-to-end; process/throughput/fuel critical fields stay explicit; visible brief remains free of leasing/subletting semantics; TCEQ asset-level permit/emissions evidence is promoted into the field register |
| HQ / issuer-address case | `runtime-orchestrator/inputs/pld_inputs.json` | `US-CA-SF` | `CORPORATE_HEADQUARTERS` | full run | `Target Classification Brief`; `routing_ready = false`; no technical energy/HVAC/retrofit analysis |
| Ambiguous target | `runtime-orchestrator/inputs/clar_inputs.json` | `US-NV` | `AMBIGUOUS_TARGET` | full run | `Target Clarification Brief`; no technical report; evidence request dominates |

## Canonical Validated Runs

These runs are the baseline references pinned at freeze time.

| Case | Run ID | Status | Notes |
|---|---|---|---|
| NYC bounded operating asset | `run:cadb81a9f1a55a27` | `completed` | `One Vanderbilt`; strong NYC public-data path; evidence maturity matrix visible |
| California bounded building | `run:c816bd67199380f8` | `completed` | routing/evidence subgraph; SF route active; CA guidance/utility context present |
| Los Angeles bounded building | `run:f0ceb4e7c0f52faf` | `completed` | routing/evidence subgraph; official LA assessor API now provides asset-specific parcel detail; LA utility/context layers stay bounded |
| Texas bounded industrial facility | `run:d0c7836f4d4444a1` | `completed` | routing/evidence subgraph; TCEQ/state environmental path active |
| Houston bounded building | `run:c06d085d8965f3cc` | `completed` | routing/evidence subgraph; HCAD public downloads channel, Houston permit route, and CenterPoint/ERCOT context all active without faking parcel-level hard match |
| Texas bounded manufacturing facility | `run:fef257fb569c510d` | `completed` | manufacturing-specific full-run golden case; preserves industrial routing while keeping visible brief language process-first and free of leasing leakage, with TCEQ asset-level permit/emissions evidence promoted into the field register |
| HQ / issuer-address case | `run:6ec2b537806832ae` | `completed` | full run; `PIER 1 BAY 1 / Prologis`; LL97 leakage removed; routing bundle visible |
| Ambiguous target | `run:979b11f2272cd1e2` | `completed` | canonical `Target Clarification Brief` run |

## Minimum Acceptance Contract

USA v1 is considered passing only if all eight golden cases satisfy:

- correct `target_type_classification`
- correct `report_type_switch_recommendation`
- no disallowed technical scraping for `HQ`, `mailing`, or `ambiguous`
- no entity-level or benchmark-only substitution into asset-level critical fields
- `routing_plan_compliance` visible downstream
- no cross-jurisdiction contamination in the visible report

## Known Bounded Limitations

These do not break the release classification, but they remain explicit:

- California and Texas still depend heavily on case-match quality; many real cases will remain `attempted_not_found` rather than fully populated.
- `CA industrial` currently has strong official regulatory context from `CARB` and `CalEPA`, but not guaranteed asset-level facility matching from public routing alone.
- `Los Angeles` is now materially stronger because the Assessor API is live and asset-specific, but route success still depends on public `AIN/address` match quality.
- `Houston` is materially stronger through `HCAD` public-data downloads, but direct structured parcel search remains Cloudflare-gated and therefore bounded as routing context rather than hard parcel extraction.
- Texas county-appraisal and city-permit coverage varies by county and portal quality.
- EPA/CARB/TCEQ routes are strong routing anchors, not universal proof of facility identity.

## Rules Frozen By This Baseline

These rules must not be weakened in maintenance releases:

- never run technical scraping when `target_type != OPERATING_ASSET/INDUSTRIAL_FACILITY`
- never use `SEC EDGAR` as asset-level truth
- never let benchmark layers substitute for local disclosure when local disclosure is mandatory
- never allow out-of-jurisdiction regulatory language into classification briefs
- always downgrade before assuming missing technical substrate
- block publication when routing-driven contamination is detected

## Maintenance Policy

Changes allowed without re-baselining:

- adding new official sources inside an existing jurisdiction route
- improving executor robustness for an already-approved source
- adding non-breaking visibility fields to API/dashboard/manifests

Changes that require re-baselining:

- changing target taxonomy
- changing report-type switching rules
- changing mandatory/disallowed substitution logic
- changing golden-case expected outcomes
- changing routing-plan gate semantics
