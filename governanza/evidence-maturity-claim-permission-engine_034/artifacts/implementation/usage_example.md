# Usage Example — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## example

The runtime invokes `EvidenceMaturityClaimPermissionEngine` once there is enough target context, asset fields and optional structural intelligence to decide what the system is actually allowed to say. A typical building case may already have `GFA`, operating schedule, a requested report type and structural signals around control boundaries or benchmarking conflicts, but still need the maturity engine to decide whether the result is only a screening brief, an exploratory prior or a full technical report.

## inputs_used

```python
inputs = {
    "motor_007": {
        "target_definition_contract": {
            "address_raw": "350 FIFTH AVENUE, NEW YORK, NY, 10118",
            "jurisdiction_scope": ["US-NY-NYC"],
            "target_type": "commercial_building",
        },
        "target_classification_object": {
            "target_type": "OPERATING_ASSET",
            "classification_confidence": "high",
        },
        "technical_substrate_readiness": "partial",
        "recommended_report_type": "Decision-Blocked Asset Brief",
    },
    "motor_012": {
        "asset_field_register": [
            {"field": "address", "value": "350 FIFTH AVENUE, NEW YORK, NY, 10118", "status": "OBSERVED"},
            {"field": "asset_class", "value": "commercial_building", "status": "OBSERVED"},
            {"field": "GFA", "value": "250000", "status": "OBSERVED"},
            {"field": "current_EUI", "value": "71", "status": "OBSERVED", "scope": "BENCHMARK_LEVEL"},
        ],
        "missing_evidence_register": [],
        "compliance_applicability_case": {
            "applicability_state": "trigger_partially_supported",
            "compliance_posture_state": "trigger_plausible",
        },
    },
    "motor_028": {
        "source_register": [
            {"source_id": "nyc_pluto::350-fifth", "accepted": True},
            {"source_id": "nyc_ll84::350-fifth", "accepted": True},
        ],
    },
    "motor_038": {
        "dominant_variable_register": [
            {"variable": "tenant_metering", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
        ],
    },
    "motor_040": {
        "cross_layer_conflict_register": [
            {"conflict": "Regulation vs control boundary"},
        ],
    },
    "motor_041": {
        "problem_framing_register": [
            {
                "stated_problem": "Need retrofit decision",
                "reframed_problem": "Need to distinguish owner-controlled upside from tenant-driven load.",
            }
        ],
    },
    "motor_046": {
        "minimum_evidence_for_discrimination_register": [
            {
                "minimum_evidence": "utility bills + tenant metering map",
                "source": "operator request",
                "unlocks": "bounded redesign path",
            }
        ],
    },
}
```

## expected_output

```python
{
    "dataset_coverage_register": [...],
    "variable_maturity_register": [
        {"variable_name": "GFA", "maturity_level": 3},
        {"variable_name": "EUI", "maturity_level": 1},
    ],
    "claim_permission_register": [
        {"claim_name": "numeric_eui_claim", "current_permission": "conditional"},
        {"claim_name": "energy_savings_claim", "current_permission": "prohibited"},
    ],
    "report_readiness_register": {
        "report_type_allowed": ["Compliance / Investment Screening Brief"],
        "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
    },
    "canonical_problem_frame": {
        "problem_frame_active": True,
        "reasoning_path": "structural_first",
        "dominant_conflict": "Regulation vs control boundary",
    },
}
```

## notes

The governance-stage wrapper must not reimplement maturity logic. It only validates that inputs are mapping-shaped and delegates directly to `Motor034Adapter`, so the governance artifact stays aligned with the runtime behavior.
