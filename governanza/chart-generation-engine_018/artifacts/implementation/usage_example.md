# Usage Example — Chart Generation Engine

Motor ID: motor_018

## example

The runtime invokes `ChartGenerationEngine` once the case already has a report identity, bounded congruence surfaces and enough analytical structure to explain visually. In a structural screening case it should emit governed chart assets such as congruence binding state, fair-comparison gate and gap-taxonomy charts with taxonomy metadata and case stamping.

## inputs_used

```python
inputs = {
    "__pipeline__": {"case_title": "Congruence Chart Test"},
    "motor_007": {"report_identity_state": "Compliance / Investment Screening Brief"},
    "motor_047": {"report_mode": "Compliance / Investment Screening Brief"},
    "motor_049": {"gap_taxonomy_register": [{"gap_type": "missing_comparability"}]},
    "motor_051": {"invalid_comparison_risk_register": [{"risk_name": "warehouse_area_only_comparison"}]},
}
```

## expected_output

```python
{
    "chart_assets": [
        {
            "asset_id": "chart_gap_taxonomy_profile",
            "chart_category": "gap_taxonomy",
            "chart_lane": "validation",
            "chart_intent": "evidence_gap_diagnosis",
            "chart_curation_mode": "structural_support",
            "image_b64": "...",
            "chart_case_match_state": "same_case",
        }
    ],
    "total_charts": 1,
}
```

## notes

The governance-stage wrapper does not generate images itself. It only validates mapping-shaped input and delegates directly to `Motor018Adapter`, keeping governance reconciliation aligned with the runtime chart generator.
