# Usage Example — Minimum Evidence For Discrimination Engine

Motor ID: motor_046

## example
El runtime invoca `MinimumEvidenceForDiscriminationEngine` cuando ya sabe cuál es el framing correcto y qué rediseño bounded está en juego. En un building como One Vanderbilt, el motor no debe pedir una due diligence amplia; debe pedir el paquete mínimo que separa control owner-side de carga tenant-driven.

## inputs_used
```python
inputs = {
    "motor_041": {
        "problem_framing_register": [
            {"reframed_problem": "Need to determine whether owner-managed base-building systems or tenant-driven loads dominate value logic."}
        ],
    },
    "motor_044": {
        "conditional_redesign_register": [
            {"redesign_direction": "Lease / submetering redesign before owner-only retrofit CAPEX."}
        ],
    },
}
```

## expected_output
```python
{
    "minimum_evidence_for_discrimination_count": 1,
    "minimum_evidence_for_discrimination_register": [
        {
            "minimum_evidence": "Utility bills + tenant metering map + BMS / central plant topology + LL97 filing basis",
            "unlocks": "bounded redesign path and capital sequencing under the correct control boundary",
        }
    ],
}
```

## notes
La fila tiene que decir qué confirma y qué falsifica. Si sólo dice “more data needed”, el motor está fallando su función.
