# Failure Modes Spec — Structural Benchmarking Engine

Motor ID: motor_042

## failure_modes_list
- `OVERCONFIDENT_BENCHMARK`: fila observada sin suficiente coverage.
- `MANUFACTURING_WASTE_SHORTCUT`: benchmark confundido con desperdicio probado.
- `INTERPRETATION_DROP`: fila sin guidance de uso.
- `COUNT_DRIFT`: count plano desincronizado.

## anti_patterns
- vender peer benchmark como verdict final;
- reutilizar la misma plantilla entre families distintas.

## degradation_signals
- evidencias observadas dominan incluso en casos con screening pobre;
- manufacturing sin ninguna advertencia de interpretación;
- todos los peers se ven genéricos e intercambiables.

## expensive_errors
- contaminar comparación competitiva y framing con benchmarks mal interpretados;
- inducir decisiones CAPEX sobre una base sólo arquetipal;
- ocultar la frontera entre screening y cierre técnico.
