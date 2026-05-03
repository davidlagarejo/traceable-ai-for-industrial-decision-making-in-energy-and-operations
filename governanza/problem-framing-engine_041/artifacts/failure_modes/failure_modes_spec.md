# Failure Modes Spec — Problem Framing Engine

Motor ID: motor_041

## failure_modes_list
- `SYMPTOM_LOCK_IN`: el motor conserva el framing aparente sin corregirlo.
- `FALLBACK_OVERWRITE`: el fallback pisa un framing estructural válido.
- `LAYER_TRACE_LOSS`: desaparecen `linked_layers` o `evidence_needed`.
- `SOLUTION_LEAKAGE`: el registro ya actúa como recomendación.

## anti_patterns
- convertir “high energy use” en framing suficiente;
- usar lenguaje de solución en lugar de problema;
- traducir fallback de congruencia sin conservar el porqué del invalid frame.

## degradation_signals
- todas las filas se parecen entre familias de activos;
- no aparece control boundary en building;
- no aparece process/uptime en manufacturing;
- logistics deja de exponer comparabilidad justa.

## expensive_errors
- invertir tiempo de rediseño en el problema equivocado;
- abrir TAD o CAPEX prematuros;
- llevar una tesis ejecutiva a una narrativa fuerte pero mal planteada.
