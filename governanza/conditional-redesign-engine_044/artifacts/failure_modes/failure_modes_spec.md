# Failure Modes Spec — Conditional Redesign Engine

Motor ID: motor_044

## failure_modes_list
- `FINAL_RECOMMENDATION_DRIFT`: hipótesis presentada como decisión.
- `KILL_CONDITION_ERASURE`: desaparece la condición de muerte.
- `NON_SPECIFIC_NEXT_EVIDENCE`: evidencia siguiente demasiado genérica.
- `ECONOMIC_PROMISE_LEAK`: la lógica económica se convierte en promesa de retorno.

## anti_patterns
- “redesign the system” sin causalidad bounded;
- usar peer superiority como justificación suficiente;
- matar la reversibilidad de la hipótesis.

## degradation_signals
- building y manufacturing generan filas casi idénticas;
- no aparece el conflicto resuelto;
- todas las filas se parecen a una recomendación final.

## expensive_errors
- priorizar CAPEX o rediseño temprano;
- inducir modelado innecesario;
- endurecer una dirección sin evidencia suficiente.
