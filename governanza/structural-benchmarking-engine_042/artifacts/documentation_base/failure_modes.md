# Failure Modes — Structural Benchmarking Engine

Motor ID: motor_042

## failure_modes_list
- `BENCHMARK_AS_DIAGNOSIS`: benchmark usado como diagnóstico final.
- `PROCESS_BENCHMARK_COLLAPSE`: manufacturing benchmark degradado a intensidad simplista.
- `MISSING_INTERPRETATION`: fila benchmark sin límite de uso.
- `COUNT_DRIFT`: count plano desincronizado.

## anti_patterns
- usar benchmark como sustituto de comparabilidad justa;
- mezclar benchmark estructural con narrativa competitiva final.

## degradation_signals
- todas las filas parecen iguales entre building y manufacturing;
- benchmarks sin matices de interpretación;
- evidencias observadas demasiado generosas con coverage pobre.
