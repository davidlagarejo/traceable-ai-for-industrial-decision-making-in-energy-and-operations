# Failure Modes Spec — System Abstraction Engine

Motor ID: motor_037

## failure_modes_list
- `PRIOR_AS_FACT`: prior arquetipal emitido como hecho observado.
- `REGULATORY_OVERCLAIM`: exposición regulatoria observada sin coverage o source markers suficientes.
- `CONTROL_BOUNDARY_OVERCLAIM`: estructura de control observada sin evidence fields admisibles.
- `UNBOUNDED_TARGET_ABSTRACTION`: bundle útil emitido para target no bounded.

## anti_patterns
- copiar frases del arquetipo sin recalificar `evidence_state`;
- tratar cualquier field observado como prueba de proceso o control sin revisar tipo de field.

## degradation_signals
- demasiados `OBSERVED_FACT` en casos con screening pobre;
- `evidence_maturity` observado con `screening_supported=false`;
- bundles idénticos para familias building y manufacturing.

## expensive_errors
- cerrar `regulatory_exposure` erróneamente y contaminar benchmarking, framing o finanzas downstream;
- convertir `control_structure` en hecho observado y sesgar fairness o claim governance posteriores;
- permitir que un target inadmisible siga generando abstracción estructural “usable”.
