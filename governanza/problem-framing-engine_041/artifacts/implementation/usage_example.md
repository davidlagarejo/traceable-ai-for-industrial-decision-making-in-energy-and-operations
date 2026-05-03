# Usage Example — Problem Framing Engine

Motor ID: motor_041

## example
El runtime invoca `ProblemFramingEngine` después de identificar variables dominantes y conflictos cross-layer. En un building como One Vanderbilt, el motor no debe aceptar “alto EUI” o “retrofit CAPEX” como framing suficiente: debe reformular el problema hacia control boundary, separación tenant-owner y presión LL97.

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
    "motor_040": {
        "cross_layer_conflict_register": [
            {"conflict": "Regulation vs control boundary", "evidence_state": "OBSERVED_FACT"},
            {"conflict": "Finance assumes owner-capturable savings before control is proven", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
        ],
    },
}
```

## expected_output
```python
{
    "problem_framing_count": 2,
    "problem_framing_register": [
        {
            "stated_problem": "high energy use",
            "reframed_problem": "Need to determine whether owner-managed base-building systems, tenant-driven loads, or LL97 exposure actually dominate value and capital logic.",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
        }
    ],
}
```

## notes
Si el framing estructural queda inadmisible o cae a `asset_screening`, el motor puede traducir `motor_051.invalid_problem_frame_register`. Esa traducción debe preservar `linked_layers` y nunca saltar directamente a solución o CAPEX.
