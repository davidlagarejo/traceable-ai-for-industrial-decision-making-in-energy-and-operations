# Usage Example — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## example
El runtime invoca `IndustrialBuildingArchetypeLibraryResolver` cuando ya existe un target operacionalmente bounded y hace falta escoger un prior estructural gobernado antes de correr benchmarking, framing o redesign. En un caso tipo One Vanderbilt, el motor debe reconocer el arquetipo de torre comercial NYC y devolver hipótesis estructurales falsables, no hechos observados cerrados.

## inputs_used
```python
inputs = {
    "motor_007": {
        "target_definition_contract": {
            "target_type": "commercial_building",
            "target_name": "One Vanderbilt",
            "jurisdiction_scope": ["US-NY-NYC"],
        },
        "target_classification_object": {
            "target_type": "OPERATING_ASSET",
            "classification_confidence": "high",
        },
    },
    "motor_012": {
        "facility_prior": {
            "target_definition": {
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
                "jurisdiction_scope": ["US-NY-NYC"],
            },
            "asset_name": "One Vanderbilt",
        },
        "asset_field_register": [
            {"field": "GFA", "value": "1700000"},
            {"field": "floor_count", "value": "73"},
            {"field": "current_EUI", "value": "72.1"},
        ],
        "dataset_coverage_register": [
            {"dataset_key": "nyc_pluto_property", "status": "accepted"},
            {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
        ],
    },
    "motor_028": {
        "source_register": [
            {"source_type": "nyc_pluto_property", "accepted": True},
            {"source_type": "nyc_ll84_energy_benchmarking", "accepted": True},
        ],
    },
}
```

## expected_output
```python
{
    "selected_archetype_id": "commercial_office_tower_nyc",
    "selected_archetype_label": "Commercial Office Tower NYC",
    "match_confidence": "high",
    "resolver_state": "selected",
    "dominant_variable_count": 4,
    "anti_hallucination_contract": {
        "selected_archetype_evidence_state": "ARCHETYPAL_PRIOR",
    },
    "dominant_variable_hypotheses": [
        {"variable": "central_plant"},
        {"variable": "tenant_metering"},
        {"variable": "after_hours_occupancy"},
        {"variable": "LL97_pathway"},
    ],
}
```

## notes
Si el target upstream es `CORPORATE_HEADQUARTERS`, `REGISTERED_AGENT_OR_MAILING_ADDRESS` o `AMBIGUOUS_TARGET`, este motor debe degradar a `target_not_yet_structurally_modelable`. El motor no puede cerrar ROI, savings o redesign final; sólo emite priors estructurales con contrato anti-hallucination.
