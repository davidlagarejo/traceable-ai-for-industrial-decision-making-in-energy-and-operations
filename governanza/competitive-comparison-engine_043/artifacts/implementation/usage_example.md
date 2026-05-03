# Usage Example — Competitive Comparison Engine

Motor ID: motor_043

## example
El runtime invoca `CompetitiveComparisonEngine` después de que el benchmark estructural ya fue delimitado. En un building tipo One Vanderbilt, el motor puede comparar contra torres NYC con mejor disciplina de submetering, green-lease y ajuste BMS, pero no debe convertir esa comparación en “prueba final” de desperdicio o de ROI retrofit.

## inputs_used
```python
inputs = {
    "motor_039": {
        "archetype_resolution": {
            "selected_archetype_id": "commercial_office_tower_nyc",
        },
    },
    "motor_042": {
        "structural_benchmark_register": [
            {
                "dimension": "compliance and public screening context",
                "peer_or_benchmark": "Class A NYC LL97-covered office towers",
                "evidence_state": "OBSERVED_FACT",
            }
        ],
    },
}
```

## expected_output
```python
{
    "competitive_comparison_count": 1,
    "competitive_comparison_register": [
        {
            "what_they_do_better": "Uses submetering and green-lease discipline to separate tenant and owner loads...",
            "comparison_mode": "conditional_comparison",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
        }
    ],
}
```

## notes
La fila debe incluir `what_it_does_not_prove` y `transferability`. Si el caso cae a best practice arquetipal, eso debe quedar dicho; no puede maquillarse como peer observado fuerte.
