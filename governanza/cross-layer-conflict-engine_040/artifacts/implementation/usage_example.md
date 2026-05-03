# Usage Example — Cross-Layer Conflict Engine

Motor ID: motor_040

## example
El runtime invoca `CrossLayerConflictEngine` cuando ya existen abstracción estructural y variables dominantes, pero antes de reencuadrar el problema o benchmarkear. En un caso building como One Vanderbilt, el motor debe hacer explícito si la lógica regulatoria, la frontera owner-vs-tenant y el supuesto financiero owner-capturable chocan entre sí.

## inputs_used
```python
inputs = {
    "motor_037": {
        "system_abstraction": {
            "regulatory_exposure": {"evidence_state": "OBSERVED_FACT"},
            "control_structure": {"evidence_state": "CONDITIONAL_HYPOTHESIS"},
        },
    },
    "motor_038": {
        "dominant_variable_register": [
            {"variable": "LL97_pathway", "evidence_state": "OBSERVED_FACT"},
            {"variable": "owner_control_boundary", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
        ],
    },
    "motor_014": {
        "financial_exposure_register": [
            {"assumption": "Owner-controllable energy upside exists"},
        ],
    },
    "motor_034": {
        "claim_permission_register": [
            {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
        ],
    },
    "motor_033": {
        "decision_front_actions": [
            {"decision_front": "Energy retrofit CAPEX", "current_status": "DEFER"},
        ],
    },
}
```

## expected_output
```python
{
    "cross_layer_conflict_count": 3,
    "cross_layer_conflict_register": [
        {"conflict": "Regulation vs control boundary"},
        {"conflict": "Finance assumes owner-capturable savings before control is proven"},
    ],
}
```

## notes
Si el registro estructural queda vacío, el motor puede traducir conflictos desde `motor_051.cross_layer_congruence_register`. No reencuadra todavía el problema ni decide la solución final.
