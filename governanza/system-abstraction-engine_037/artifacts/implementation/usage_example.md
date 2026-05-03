# Usage Example — System Abstraction Engine

Motor ID: motor_037

## example
El runtime invoca `SystemAbstractionEngine` después de `motor_039`, cuando el arquetipo ya está seleccionado y hace falta traducirlo en statements estructurales auditables. En un caso tipo One Vanderbilt, el motor debe distinguir qué partes ya son observación pública y cuáles siguen siendo hipótesis condicionales.

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
        "canonical_asset_context_summary": {
            "screening_supported": True,
            "supported_field_register": [
                {"field": "GFA"},
                {"field": "floor_count"},
                {"field": "current_EUI"},
            ],
        },
        "facility_prior": {
            "asset_name": "One Vanderbilt",
            "target_definition": {
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
                "jurisdiction_scope": ["US-NY-NYC"],
            },
        },
        "asset_field_register": [
            {"field": "GFA", "value": "1700000"},
            {"field": "floor_count", "value": "73"},
            {"field": "current_EUI", "value": "72.1"},
        ],
        "dataset_coverage_register": [
            {"dataset_key": "nyc_pluto_property", "status": "accepted"},
            {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
            {"dataset_key": "nyc_ll97_covered_buildings_list", "status": "accepted"},
        ],
    },
    "motor_028": {
        "source_register": [
            {"source_type": "nyc_pluto_property", "accepted": True},
            {"source_type": "nyc_ll84_energy_benchmarking", "accepted": True},
        ],
    },
    "motor_039": {
        "archetype_resolution": {
            "selected_archetype_id": "commercial_office_tower_nyc",
            "selected_archetype_label": "Commercial Office Tower NYC",
            "match_confidence": "high",
            "resolver_state": "selected",
        },
        "archetype_library_register": [
            {
                "archetype_id": "commercial_office_tower_nyc",
                "business_function": "Multi-tenant office services delivery in a dense vertical asset.",
                "value_creation_mechanism": "Rent capture and service-level retention through high-rise office performance.",
                "dominant_process_type": "Vertical building services orchestration under occupancy and compliance constraints.",
                "control_structure": "Base-building systems interact with tenant-controlled end uses and schedules.",
            }
        ],
    },
}
```

## expected_output
```python
{
    "system_abstraction_fields": [
        "asset_type",
        "business_function",
        "value_creation_mechanism",
        "dominant_process_type",
        "dominant_physical_drivers",
        "dominant_operational_drivers",
        "control_structure",
        "constraint_structure",
        "economic_driver",
        "regulatory_exposure",
        "evidence_maturity",
    ],
    "system_abstraction_evidence_states": {
        "asset_type": "OBSERVED_FACT",
        "business_function": "ARCHETYPAL_PRIOR",
        "regulatory_exposure": "OBSERVED_FACT",
        "control_structure": "CONDITIONAL_HYPOTHESIS",
    },
}
```

## notes
El motor no decide todavía variables dominantes finales ni comparables. Si el target upstream deja de ser estructuralmente modelable, el bundle entero debe degradarse a `INADMISSIBLE_CLAIM`.
