# Usage Example — Dominant Variable Engine

Motor ID: motor_038

## example
El runtime invoca `DominantVariableEngine` después de `motor_037` y `motor_039`, cuando ya existe abstracción estructural y una lista inicial de hipótesis dominantes. En un caso tipo One Vanderbilt, el motor debe promover `LL97_pathway` a observado por coverage pública y mantener `central_plant` o `tenant_metering` como variables condicionadas salvo evidencia más directa.

## inputs_used
```python
inputs = {
    "motor_007": {
        "target_definition_contract": {
            "target_type": "commercial_building",
            "target_name": "One Vanderbilt",
            "jurisdiction_scope": ["US-NY-NYC"],
        },
    },
    "motor_012": {
        "asset_field_register": [
            {"field": "GFA", "value": "1700000"},
            {"field": "floor_count", "value": "73"},
            {"field": "current_EUI", "value": "72.1"},
        ],
        "dataset_coverage_register": [
            {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
            {"dataset_key": "nyc_ll97_covered_buildings_list", "status": "accepted"},
        ],
    },
    "motor_037": {
        "system_abstraction": {
            "regulatory_exposure": {"evidence_state": "OBSERVED_FACT"},
        },
    },
    "motor_039": {
        "dominant_variable_hypotheses": [
            {"variable": "central_plant", "layer": "systems"},
            {"variable": "tenant_metering", "layer": "control"},
            {"variable": "after_hours_occupancy", "layer": "operations"},
            {"variable": "LL97_pathway", "layer": "regulation"},
        ],
    },
}
```

## expected_output
```python
{
    "dominant_variable_count": 5,
    "observed_or_conditional_variable_count": 4,
    "dominant_variable_register": [
        {"variable": "central_plant", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
        {"variable": "LL97_pathway", "evidence_state": "OBSERVED_FACT"},
        {"variable": "owner_control_boundary", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
    ],
}
```

## notes
El motor puede inyectar `owner_control_boundary` aunque no venga en las hipótesis iniciales. No produce comparables, contradicciones ni estrategia; sólo deja la capa de variables dominantes lista para downstream.
