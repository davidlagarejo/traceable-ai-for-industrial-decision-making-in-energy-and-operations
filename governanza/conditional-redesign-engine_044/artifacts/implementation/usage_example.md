# Usage Example — Conditional Redesign Engine

Motor ID: motor_044

## example
El runtime invoca `ConditionalRedesignEngine` después de conflicto, problem framing y comparación bounded. En un building como One Vanderbilt, el motor debe proponer una vía de rediseño lease/submetering o control-boundary sólo como hipótesis falsable, no como cierre final de retrofit.

## inputs_used
```python
inputs = {
    "motor_041": {
        "problem_framing_register": [
            {"reframed_problem": "Need to determine whether owner-managed base-building systems or tenant-driven loads dominate value logic."}
        ],
    },
    "motor_043": {
        "competitive_comparison_register": [
            {"what_they_do_better": "Uses submetering and green-lease discipline."}
        ],
    },
}
```

## expected_output
```python
{
    "conditional_redesign_count": 2,
    "conditional_redesign_register": [
        {
            "hypothesis": "Tenant-driven loads and unresolved control boundary weaken owner-only retrofit economics.",
            "redesign_direction": "Lease / submetering redesign before owner-only retrofit CAPEX.",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
        }
    ],
}
```

## notes
Cada fila debe incluir `kill_condition` y `next_evidence`. Si el caso no sostiene la hipótesis, el motor no puede convertirla en recomendación.
