# Failure Modes Spec — Dominant Variable Engine

Motor ID: motor_038

## failure_modes_list
- `OBSERVATION_INFLATION`: demasiadas variables observadas con poca evidencia.
- `REGULATORY_FALSE_POSITIVE`: `LL97_pathway` observado sin coverage suficiente.
- `BOUNDARY_GAP`: falta `owner_control_boundary`.
- `MANUFACTURING_SIGNAL_DRIFT`: process clues débiles promueven variables equivocadas o no relacionadas.

## anti_patterns
- usar el register como cierre ejecutivo y no como superficie intermedia;
- derivar dominancia sólo del tipo de activo sin mirar fields ni datasets.

## degradation_signals
- todos los records salen como `ARCHETYPAL_PRIOR` aunque haya evidence fields claros;
- building cases sin variable regulatoria ni de control;
- manufacturing cases sin variables de throughput o compressed air.

## expensive_errors
- contaminar benchmarking y framing con variables observadas falsas;
- perder la variable de control boundary y sesgar fairness o claim governance posteriores;
- declarar pathways regulatorios observados y empujar decisiones erróneas downstream.
