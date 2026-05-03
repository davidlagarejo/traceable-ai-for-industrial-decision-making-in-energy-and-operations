# Usage Example — System Consistency Validator

Motor ID: motor_036

## example

The runtime invokes `SystemConsistencyValidator` immediately before render. At that point the package may already have an executive thesis, client-facing body sections, appendix sections, claim contracts, output-mode classifiers, structural TAD actions and chart assets. The validator's job is to decide whether all of those surfaces still agree strongly enough to allow render.

## inputs_used

```python
inputs = {
    "motor_016": {
        "report_package": {
            "document_type": "Compliance / Investment Screening Brief",
            "executive_thesis": {"report_mode": "Compliance / Investment Screening Brief"},
            "main_report_outline": {"visible_report_mode": "Compliance / Investment Screening Brief"},
        }
    },
    "motor_014": {
        "claim_permission_summary": {
            "allowed_count": 2,
            "conditional_count": 0,
            "prohibited_count": 1,
        }
    },
    "motor_034": {
        "claim_permission_register": [
            {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
            {"claim_name": "compliance_screening_claim", "current_permission": "allowed"},
            {"claim_name": "roi_range_claim", "current_permission": "prohibited"},
        ],
        "report_type_classifier_table": [
            {"recommended_report_type": "Compliance / Investment Screening Brief"},
        ],
    },
    "motor_045": {
        "evidence_state_by_layer_register": [
            {"layer": "finance", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
        ],
    },
}
```

## expected_output

```python
{
    "consistency_register": [
        {"check_id": "report_mode_consistency_match", "passed": True, "severity": "critical"},
        {"check_id": "claim_summary_count_match", "passed": True, "severity": "critical"},
    ],
    "critical_failures": [],
    "blocking_reason_register": [],
    "canonical_report_state": {
        "document_visible_type": "Compliance / Investment Screening Brief",
        "canonical_asset_context_state": "asset_context_minimal",
        "screening_supported": True,
    },
    "critical_failure_count": 0,
    "can_render_pdf": True,
}
```

## notes

The governance-stage wrapper must remain a thin delegation layer. It validates only that inputs are mapping-shaped, then returns the `Motor036Adapter` surface unchanged so the governance artifact cannot drift away from the runtime validator.
