# Usage Example — Fair Comparison and Congruence Engine

Motor ID: motor_051

## example
El runtime invoca `FairComparisonAndCongruenceEngine` después de `motor_050`, cuando ya existe family research y una lógica operacional mínima. En un caso tipo One Vanderbilt, el motor debe impedir comparaciones owner-capturable ingenuas si la frontera owner-vs-tenant sigue abierta, y además dejar trazadas las contradicciones entre regulación, control y framing aparente.

## inputs_used
```python
inputs = {
    "motor_049": {
        "asset_family_research_profile": {
            "asset_family": "commercial_building",
            "route_state": "operational_asset_candidate",
        },
        "operational_intake_pack": {},
        "local_evidence_binding_register": [],
        "gap_taxonomy_register": [],
        "rival_hypothesis_register": [],
        "hypothesis_discrimination_register": [],
        "claim_impact_register": [],
    },
    "motor_050": {
        "process_map": {
            "asset_family": "commercial_building",
            "process_map_state": "research_seeded",
        },
        "control_boundary_map": [
            {"boundary_name": "owner_vs_tenant_load_boundary"},
            {"boundary_name": "base_building_vs_occupant_behavior"},
        ],
        "subsystem_register": [],
        "maintenance_dependency_map": [],
    },
}
```

## expected_output
```python
{
    "comparison_validity_count": 2,
    "peer_requirement_count": 3,
    "cross_layer_congruence_count": 2,
    "fair_comparison_profile": {
        "asset_family": "commercial_building",
        "control_boundary_state": "not_yet_evidenced",
    },
}
```

## notes
El motor no cierra estrategia ni claim final. Si faltan normalizaciones o boundaries, debe devolver blockers, risks y problem frames inválidos, no una comparabilidad artificialmente limpia.
