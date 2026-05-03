# Usage Example — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## example
El runtime invoca `FinancialExposureUnderUncertaintyEngine` cuando ya existen conflicto, framing, comparación y rediseño condicional. En un building como One Vanderbilt, el motor debe dejar visible que el upside owner-controllable todavía depende de control boundary y que por eso ROI o payback siguen prohibidos.

## inputs_used
```python
inputs = {
    "motor_040": {
        "cross_layer_conflict_register": [
            {"conflict": "Regulation vs control boundary", "evidence_state": "OBSERVED_FACT"}
        ],
    },
    "motor_044": {
        "conditional_redesign_register": [
            {"hypothesis": "Tenant-driven loads and unresolved control boundary weaken owner-only retrofit economics."}
        ],
    },
}
```

## expected_output
```python
{
    "structural_financial_exposure_count": 2,
    "evidence_state_by_layer_count": 12,
    "structural_financial_exposure_register": [
        {
            "structural_assumption": "owner-controllable savings exist and can be captured by owner-side retrofit economics.",
            "prohibited_financial_output": "Do not issue ROI, payback or savings claim closure while the control boundary remains unresolved.",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
        }
    ],
}
```

## notes
El register por capas no es resumen decorativo; es la justificación de por qué la salida financiera sigue bounded. Si `finance` o `control/responsibility` siguen abiertos, el motor no puede endurecer outputs finales.
