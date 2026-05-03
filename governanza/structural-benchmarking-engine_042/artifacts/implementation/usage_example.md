# Usage Example — Structural Benchmarking Engine

Motor ID: motor_042

## example
El runtime invoca `StructuralBenchmarkingEngine` después de fijar arquetipo, abstracción y variables dominantes. En un caso tipo One Vanderbilt, el motor debe devolver un benchmark structuralmente bounded contra office towers NYC cubiertas por LL97, pero dejar claro que eso sólo soporta screening y no cierre económico.

## inputs_used
```python
inputs = {
    "motor_039": {
        "archetype_resolution": {
            "selected_archetype_id": "commercial_office_tower_nyc",
        },
    },
    "motor_037": {
        "system_abstraction": {
            "regulatory_exposure": {"evidence_state": "OBSERVED_FACT"},
        },
    },
    "motor_038": {
        "dominant_variable_register": [
            {"variable": "LL97_pathway", "evidence_state": "OBSERVED_FACT"},
        ],
    },
    "motor_012": {
        "dataset_coverage_register": [
            {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
            {"dataset_key": "nyc_ll97_covered_buildings_list", "status": "accepted"},
        ],
    },
}
```

## expected_output
```python
{
    "structural_benchmark_count": 3,
    "structural_benchmark_register": [
        {
            "dimension": "compliance and public screening context",
            "peer_or_benchmark": "Class A NYC LL97-covered office towers",
            "evidence_state": "OBSERVED_FACT",
        }
    ],
}
```

## notes
El motor no convierte benchmark en diagnóstico final. Si el caso es manufacturing, el benchmark debe seguir siendo bounded al contexto thermal-process y no mapear intensidad directamente a waste.
