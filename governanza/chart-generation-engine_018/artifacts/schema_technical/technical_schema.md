# Technical Schema — Chart Generation Engine

Motor ID: motor_018

## entities

- `ChartAsset`
- `ChartErrorRecord`
- `CaseNamespaceRegister`

## fields

- `chart_assets: list[ChartAsset]`
- `total_charts: int`
- `chart_errors: list[ChartErrorRecord]`
- `case_namespace_register: CaseNamespaceRegister`
- `ChartAsset.asset_id: str`
- `ChartAsset.asset_type: str`
- `ChartAsset.chart_category: str`
- `ChartAsset.chart_lane: str`
- `ChartAsset.chart_intent: str`
- `ChartAsset.chart_category_catalog_version: str`
- `ChartAsset.chart_taxonomy_catalog_version: str`
- `ChartAsset.title: str`
- `ChartAsset.description: str`
- `ChartAsset.title_en: str`
- `ChartAsset.title_es: str`
- `ChartAsset.description_en: str`
- `ChartAsset.description_es: str`
- `ChartAsset.chart_curation_mode: str`
- `ChartAsset.section_hint: str`
- `ChartAsset.data_source: str`
- `ChartAsset.epistemic_marker: str`
- `ChartAsset.support_state: str`
- `ChartAsset.data_dependencies: list[str]`
- `ChartAsset.chart_role: str`
- `ChartAsset.reader_takeaway: str`
- `ChartAsset.text_pairing_guidance: str`
- `ChartAsset.image_b64: str`
- `ChartAsset.width_mm: int`
- `ChartAsset.height_mm: int`
- `ChartAsset.produced_by_motor: str`
- `ChartAsset.chart_context: dict[str, Any]`
- `ChartAsset.chart_case_match_state: str`
- `ChartErrorRecord.id: str`
- `ChartErrorRecord.error: str`

## relationships

- governed upstream analytical surfaces -> chart_specs -> `chart_assets`
- `total_charts == len(chart_assets)`
- `chart_errors` captures generation exceptions without silently dropping the governance surface
- `case_namespace_register` is used to stamp `chart_context` and `chart_case_match_state` onto each chart asset

## identifiers

- `motor_id = motor_018`
- chart assets are keyed by `asset_id`
- chart errors are keyed by chart `id`

## versioning

- this schema documents the current wrapper surface around `Motor018Adapter`
- chart taxonomy metadata and case-stamping semantics must remain stable
- changes to emitted chart ids or section hints require downstream review

## lineage

- upstream lineage: `__pipeline__`, `motor_007`, `motor_012`, `motor_014`, `motor_028`, `motor_047`, `motor_049`, `motor_051`, `motor_052`, `motor_053`
- downstream lineage: package assembly, writing support, report conformance, final render

## input_dependencies

- `__pipeline__.case_title`
- `motor_007.report_identity_state`
- `motor_012.facility_prior`
- `motor_014.*` analytical surfaces
- `motor_028.*` enriched discovery surfaces
- `motor_047.report_mode`
- `motor_049.*` congruence intake and validation surfaces
- `motor_051.*` congruence comparison and peer-requirement surfaces
- `motor_052.*` measurement and hardware-minimality surfaces
- `motor_053.*` finance/physics dependency surfaces

## behavioral_constraints

- emitted chart assets must carry taxonomy and case context
- blocked/exploratory/structural modes must remain distinguishable where the runtime expects different copy
- chart generation may fail per asset, but failures must be surfaced in `chart_errors`
- the motor may not emit unstamped or uncategorized known charts
