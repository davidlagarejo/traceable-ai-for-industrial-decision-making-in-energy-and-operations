# Usage Example — Loss Pattern and Maintenance Reality Engine

Motor ID: motor_052

## example
El runtime invoca `LossPatternAndMaintenanceRealityEngine` después de construir la lógica operacional y la comparabilidad justa. En un caso manufacturing con logs y contrato de mantenimiento locales, el motor debe subir la madurez de mantenimiento a parcialmente evidenciada, pero seguir dejando gaps de prueba y dependencia de downtime.

## inputs_used
```python
inputs = {
    "motor_049": {
        "asset_family_research_profile": {
            "asset_family": "industrial_manufacturing",
        },
        "operational_intake_pack": {},
        "dynamic_intake_question_register": [],
    },
    "motor_050": {
        "subsystem_register": [],
        "maintenance_dependency_map": [],
    },
    "motor_051": {
        "peer_requirement_register": [],
    },
}
```

## expected_output
```python
{
    "loss_pattern_count": 6,
    "maintenance_reality_count": 3,
    "measurement_strategy_count": 4,
    "maintenance_reality_register": [
        {
            "reality_claim": "maintenance maturity partially evidenced",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
        }
    ],
}
```

## notes
Este motor no declara todavía la causa final de la pérdida ni “poor maintenance” como hecho observado. Si la evidencia de mantenimiento desaparece, la salida debe degradarse a `maintenance maturity not evidenced`.
