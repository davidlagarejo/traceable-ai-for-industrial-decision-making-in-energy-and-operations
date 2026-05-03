# US Public Data Routing Matrix v1

Release baseline frozen on `2026-04-28`.

Companion baseline artifacts:
- `governanza/automation-base/us_public_data_routing_v1_release_baseline.md`
- `governanza/automation-base/us_public_data_routing_v1_release_baseline.json`
- `governanza/automation-base/us_public_data_routing_onboarding_checklist.md`

This file is the human-readable snapshot of the `Global Public Data Routing System (USA) v1`.

The authoritative runtime structures live under:

- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/`

The matrix below captures the highest-signal routes that must exist before generic search or weak scraping is allowed.

| Jurisdiction | Asset Type | Source | Layer | Access Method | Fields | Authority | Update Frequency | Use | Limitations |
|---|---|---|---|---|---|---|---|---|---|
| US | industrial_facility | EPA GHGRP facility emissions | Industrial Environment | API | facility_name, co2e_emissions, reporting_year | High | Annual | large-facility emissions anchor | covered emitters only |
| US | industrial_facility | EIA MECS sector benchmark | Benchmark | Download | sector_energy_intensity, fuel_mix | High | Multi-year | sector plausibility only | never site truth |
| US | industrial_facility | DOE IAC database | Benchmark | Download | measure_family, typical_savings | Medium | Periodic | hypothesis generation | not asset-specific |
| US | industrial_facility | OpenEI industrial combustion context | Benchmark | Web page | combustion_archetype, fuel_context | Medium | Periodic | combustion archetype context | not plant truth |
| US | commercial_building | ENERGY STAR public profile | Energy | Web page | energy_star_score, current_EUI | Medium | Annual or irregular | optional benchmarking clue | not a substitute for local disclosure |
| US | commercial_building | SEC EDGAR company filings | Entity Finance | API | issuer_name, debt_schedule, portfolio_metrics | High | Quarterly and annual | issuer context only | never asset-level physical truth |
| US | commercial_building | Federal IRA / tax credit guidance | Regulatory | Web page | incentive_family, tax_credit_context | High | Programmatic | macro incentive context | not project eligibility |
| US-NY-NYC | commercial_building | NYC Department of Finance / BBL property record | Property | Portal | address, owner, parcel_id, building_id | High | Continuous | parcel and address anchor | no energy or systems truth |
| US-NY-NYC | commercial_building | NYC PLUTO property dataset | Property | API | GFA, year_built, use, owner | High | Periodic | official building scale and use context | no utility billing or systems truth |
| US-NY-NYC | commercial_building | NYC LL84 benchmarking dataset | Energy | API | current_EUI, emissions, electricity_consumption, gas_consumption | High | Annual | asset-specific public energy baseline | covered buildings only |
| US-NY-NYC | commercial_building | NYC LL97 Covered Buildings List | Regulatory | File export | building_id, regulated_floor_area, compliance_period | High | Periodic | covered-building applicability screening | not certified filing |
| US-NY-NYC | commercial_building | NYC DOB permits and filings | Permit | API | permit_types, major_renovations, systems_clues | High | Continuous | systems clues and capital activity | not verified systems inventory |
| US-NY-NYC | commercial_building | NYC ENERGY STAR annual score extract | Energy | API | energy_star_score, current_EUI | Medium | Annual | secondary NYC benchmarking clue | secondary to LL84 |
| US-CA | commercial_building | California Energy Commission benchmarking guidance | Energy | Web page | benchmarking_requirement, disclosure_context | High | Periodic | state benchmarking route context | guidance only |
| US-CA | commercial_building | California Title 24 energy code guidance | Regulatory | Web page | applicable_rule_family, energy_code_context | High | Periodic | state code context | not building-level compliance proof |
| US-CA | commercial_building | California CALGreen guidance | Regulatory | Web page | green_building_rule_family, compliance_context | High | Periodic | green-building code context | not asset-level status |
| US-CA-SF | commercial_building | San Francisco local benchmarking disclosure | Energy | API | current_EUI, energy_use, emissions | High | Annual | local building energy baseline | ordinance coverage dependent |
| US-CA-SF | commercial_building | San Francisco assessor property record | Property | Portal | address, owner, parcel_id, GFA_or_assessed_area | High | Continuous | property anchor | no local energy truth |
| US-CA-LA | commercial_building | Los Angeles local benchmarking disclosure | Energy | API | current_EUI, energy_use, emissions | High | Annual | local building energy baseline | ordinance coverage dependent |
| US-CA-LA | commercial_building | Los Angeles County assessor property record | Property | Portal | address, owner, parcel_id, GFA_or_assessed_area | High | Continuous | property anchor | no local energy truth |
| US-TX | industrial_facility | Texas county appraisal district property record | Property | Portal | address, owner, parcel_id, assessed_area_or_improvement_value | High | Annual or continuous | primary Texas property anchor | no energy or systems truth |
| US-TX | industrial_facility | TCEQ permits and emissions records | Industrial Environment | Portal | permit_ids, emissions, facility_name | High | Continuous | Texas industrial permit anchor | not a complete energy baseline |
| US-TX | industrial_facility | ERCOT market and load-zone context | Utility | Web page | utility_territory, load_zone, market_context | High | Continuous | utility and market routing context | not a tariff or bill |
| US-TX-HOUSTON | industrial_facility | Harris County Appraisal District property record | Property | Portal | address, owner, parcel_id, building_area | High | Annual or continuous | Houston-area property anchor | property anchor only |
| US-TX-HOUSTON | industrial_facility | Houston permitting portal | Permit | Portal | permit_types, renovations, systems_clues | High | Continuous | Houston permitting context | not verified systems truth |
| US-INDUSTRIAL | industrial_facility | State environmental agency permits and emissions records | Industrial Environment | Portal | permit_ids, regulated_equipment, emissions | High | Continuous | cross-state permit and emissions anchor | not full process map |

## Disallowed substitutions

- If `nyc_ll84_energy_benchmarking` exists or is mandatory, `CBECS` or `ENERGY STAR public profile` may not substitute for local EUI.
- `SEC EDGAR` may never substitute for asset-level physical, energy, systems, or compliance truth.
- `EIA MECS`, `DOE IAC`, and `OpenEI` are benchmark or case-library layers only, never plant truth.
- `ERCOT market context` and generic utility territory may not substitute for tariff class or bill-derived energy cost.
- Permit datasets provide clues, not verified current systems inventories.
