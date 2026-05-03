# Usage Example — Asset Operational Logic Engine

Motor ID: motor_050

## example
El runtime invoca `AssetOperationalLogicEngine` una vez que `motor_049` ya resolvió la familia del activo y produjo señales de local binding. Incluso con un bundle mínimo, el motor ya debe fijar el estado operacional y las fronteras básicas; con bundles más ricos, la superficie se expande a subsistemas y dominancia de equipo más detallados.

## inputs_used
```python
inputs = {
    "motor_049": {
        "asset_family_research_profile": {
            "asset_family": "commercial_building",
            "route_state": "operational_asset_candidate",
        },
        "local_evidence_binding_register": [
            {"claim_key": "owner_control_boundary"},
            {"claim_key": "tenant_metering_structure"},
        ],
    },
}
```

## expected_output
```python
{
    "operational_logic_state": "research_seeded_operational_logic",
    "process_map": {
        "asset_family": "commercial_building",
    },
    "subsystem_count": 0,
    "control_boundary_count": 2,
    "equipment_dominance_count": 0,
}
```

## notes
Si el bundle upstream de `motor_049` es más rico, building cases como One Vanderbilt ya expanden `subsystem_register`, `equipment_dominance_register` y `control_boundary_map` con superficie detallada. Si `route_state` deja de ser `operational_asset_candidate`, la salida debe degradar a `inadmissible_until_asset_identity_bounded` y vaciar las superficies operativas fuertes. Este motor no decide fairness, finanzas ni estrategia.
