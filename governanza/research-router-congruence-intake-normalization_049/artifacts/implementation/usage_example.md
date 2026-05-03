# Usage Example — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## example
El runtime invoca `ResearchRouterCongruenceIntakeNormalization` después de discovery público para decidir qué familia de activo está realmente activa, qué evidencia local falta, qué claims siguen unbound y qué preguntas operatorias deben hacerse antes de permitir congruencia fuerte. En un caso de manufacturing con utility bills, tariff, equipment inventory, schedule, maintenance contract y permit detail, el motor debe promover el caso a `hybrid_diligence` pero todavía no a `operator_integrated_congruence`.

## inputs_used
```python
inputs = {
    "motor_007": {
        "target_definition_contract": {
            "address_raw": "TEMPLE, TX",
            "jurisdiction_scope": ["US-TX"],
            "target_type": "manufacturing_facility",
            "target_name": "Wilsonart Temple North Laminate Facility",
        },
        "target_classification_object": {
            "target_type": "OPERATING_ASSET",
            "classification_confidence": "high",
        },
    },
    "motor_012": {
        "facility_prior": {
            "target_definition": {
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart Temple North Laminate Facility",
                "jurisdiction_scope": ["US-TX"],
            },
        },
        "asset_field_register": [
            {
                "field": "industry_context",
                "value": "laminate manufacturing",
                "status": "OBSERVED",
                "scope": "ASSET_LEVEL",
                "authority_score": "high",
                "recency": "current",
                "admissibility": "CONFIRMED_ASSET_LEVEL",
                "notes": "",
                "source_id": "test::industry_context",
            },
            {
                "field": "process_signal",
                "value": "thermal-mechanical batch process",
                "status": "OBSERVED",
                "scope": "ASSET_LEVEL",
                "authority_score": "high",
                "recency": "current",
                "admissibility": "CONFIRMED_ASSET_LEVEL",
                "notes": "",
                "source_id": "test::process_signal",
            },
        ],
    },
    "motor_028": {
        "source_register": [
            {
                "source_id": "utility-bills::site",
                "title": "Utility bills",
                "url": "https://example.test/bills",
                "source_family": "utility_bill_record",
            },
            {
                "source_id": "utility-tariff::site",
                "title": "Utility tariff",
                "url": "https://example.test/tariff",
                "source_family": "utility_tariff_record",
            },
            {
                "source_id": "equipment::site",
                "title": "Equipment inventory",
                "url": "https://example.test/equipment",
                "source_family": "equipment_inventory_record",
            },
            {
                "source_id": "schedule::site",
                "title": "Shift schedule",
                "url": "https://example.test/schedule",
                "source_family": "schedule_record",
            },
            {
                "source_id": "maintenance-contract::site",
                "title": "Maintenance contract",
                "url": "https://example.test/maintenance-contract",
                "source_family": "maintenance_contract_record",
            },
            {
                "source_id": "permit::site",
                "title": "Permit detail",
                "url": "https://example.test/permit",
                "source_family": "permit_record",
            },
        ],
    },
}
```

## expected_output
```python
{
    "selected_asset_family": "industrial_manufacturing",
    "research_mode": "hybrid_diligence",
    "evidence_mode_state": "hybrid_diligence",
    "diligence_pack_count": 10,
    "partially_evidenced_pack_count": 5,
    "operational_bounding_scorecard": {
        "bounded_asset_gate_passed": True,
        "next_promotable_mode": "operator_integrated_congruence",
    },
    "local_evidence_binding_register": [
        {
            "claim_key": "industrial_process_duty",
        }
    ],
    "dynamic_intake_question_register": [
        {
            "question_id": "manufacturing_compressed_air_use",
        },
        {
            "question_id": "manufacturing_process_and_thermal_lane",
        }
    ],
}
```

## notes
Este motor no debe tratar mera presencia de `source_family` como evidencia local ya absorbida; varios packs pueden quedarse en `partially_evidenced` si `extended_sources.records` no existen. También debe convertir conflictos de alta autoridad y activos no bounded en `promotion_blocker_register`, no esconderlos para facilitar promoción.
