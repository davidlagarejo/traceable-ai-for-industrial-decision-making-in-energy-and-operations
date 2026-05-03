# Usage Example — Global Public Data Routing Engine

Motor ID: motor_035

## example
El orquestador invoca `GlobalPublicDataRoutingEngine` cuando ya existe una definición de sujeto y target suficientemente normalizada, pero antes de que `motor_028` empiece discovery público. En un caso de edificio comercial en Nueva York, el motor debe decidir si la ruta técnica es admisible, qué portales públicos son obligatorios y si el caso sigue mereciendo un brief técnico o debe degradarse.

## inputs_used
```python
inputs = {
    "motor_001": {
        "subject_definition_contract": {
            "address_raw": "350 FIFTH AVENUE, NEW YORK, NY 10118",
            "asset_anchor_type": "postal_address",
        },
        "target_definition_contract": {
            "address_raw": "350 FIFTH AVENUE, NEW YORK, NY 10118",
            "jurisdiction_scope": ["US-NY-NYC"],
            "target_type": "commercial_building",
            "decision_intent": "acquisition_underwriting",
            "target_scope": "asset",
        },
    },
    "motor_006": {
        "asset_identity_resolution": {
            "subject_definition_contract": {
                "address_raw": "350 FIFTH AVENUE, NEW YORK, NY 10118",
                "asset_anchor_type": "postal_address",
            },
            "target_definition_contract": {
                "address_raw": "350 FIFTH AVENUE, NEW YORK, NY 10118",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "decision_intent": "acquisition_underwriting",
                "target_scope": "asset",
            },
            "intake_observables": {
                "observable_clusters": {
                    "location_cluster": {"populated": True},
                    "jurisdiction_cluster": {"populated": True},
                    "geometry_size_cluster": {"populated": True},
                    "vintage_structure_cluster": {"populated": True},
                    "use_program_cluster": {"populated": True},
                    "operating_regime_cluster": {"populated": False},
                    "fuel_energy_cluster": {"populated": True},
                    "systems_cluster": {"populated": True},
                    "regulatory_cluster": {"populated": True},
                    "benchmark_mapping_cluster": {"populated": True},
                },
            },
        },
    },
    "motor_007": {
        "subject_definition_contract": {
            "address_raw": "350 FIFTH AVENUE, NEW YORK, NY 10118",
            "asset_anchor_type": "postal_address",
        },
        "target_definition_contract": {
            "address_raw": "350 FIFTH AVENUE, NEW YORK, NY 10118",
            "jurisdiction_scope": ["US-NY-NYC"],
            "target_type": "commercial_building",
            "decision_intent": "acquisition_underwriting",
            "target_scope": "asset",
        },
        "subject_gate_passed": True,
        "technical_substrate_readiness": "partial",
        "recommended_report_type": "Decision-Blocked Asset Brief",
        "prohibited_report_types": ["Full Technical Decision Intelligence Report"],
        "target_classification_object": {
            "target_type": "OPERATING_ASSET",
            "classification_confidence": "high",
        },
        "observable_cluster_register": {
            "location_cluster": {"populated": True},
            "jurisdiction_cluster": {"populated": True},
            "geometry_size_cluster": {"populated": True},
            "vintage_structure_cluster": {"populated": True},
            "use_program_cluster": {"populated": True},
            "operating_regime_cluster": {"populated": False},
            "fuel_energy_cluster": {"populated": True},
            "systems_cluster": {"populated": True},
            "regulatory_cluster": {"populated": True},
            "benchmark_mapping_cluster": {"populated": True},
        },
    },
}
```

## expected_output
```python
{
    "routing_ready": True,
    "target_type_classification": "OPERATING_ASSET",
    "jurisdiction_class": "high_data_availability_building",
    "mandatory_sources": [
        {"source_key": "nyc_dob_permits"},
        {"source_key": "nyc_dof_property_record"},
        {"source_key": "nyc_ll84_energy_benchmarking"},
        {"source_key": "nyc_ll97_covered_buildings_list"},
        {"source_key": "nyc_pluto_property"},
    ],
    "high_priority_sources": [
        {"source_key": "nyc_ll97_filing_guidance"},
    ],
    "report_type_allowed": "Minimum Evidence Report",
    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
    "missing_critical_fields": 0,
}
```

## notes
Este motor no ejecuta scraping ni materializa datasets; sólo fija el contrato de routing público y la degradación de superficie de reporte. Si la clasificación upstream cambia a `CORPORATE_HEADQUARTERS` o falla `subject_gate_passed`, el output debe vaciar las listas de fuentes técnicas y degradar el caso a clasificación.
