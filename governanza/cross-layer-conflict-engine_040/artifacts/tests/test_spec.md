# Test Spec — Cross-Layer Conflict Engine

Motor ID: motor_040

## happy_path
- Building: conflicto regulación vs control y conflicto financiero owner-capturable.
- Manufacturing: conflicto de framing energético vs carga de proceso y conflicto de maintenance/uptime.

## sparse_case
- Si faltan finanzas o claim permissions, el motor puede seguir emitiendo conflictos desde abstracción y variables.

## malformed_input
- Si los inputs vienen parciales, el motor no debe devolver un falso “no conflict” por defecto.

## edge_cases
- Logistics: fallback desde `motor_051` produce al menos un conflicto traducido.

## pass_criteria
- Todas las filas tienen capas, importancia y dirección de rediseño.
- El fallback conserva `evidence_state`.
- El count plano coincide con el register.

## fail_criteria
- Conflictos esperables ausentes.
- Register vacío en casos conflictivos.
- Traducción fallback demasiado pobre o sin campos requeridos.
