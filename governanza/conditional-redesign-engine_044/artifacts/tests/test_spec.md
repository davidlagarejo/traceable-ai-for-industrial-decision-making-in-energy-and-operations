# Test Spec — Conditional Redesign Engine

Motor ID: motor_044

## happy_path
- Building: hipótesis owner-vs-tenant con rediseño lease/submetering o green-lease.
- Manufacturing: hipótesis de carga estructural vs soporte con falsificación ligada a compressed air.

## sparse_case
- Con conflicto parcial, el motor puede seguir emitiendo rediseño bounded siempre que conserve kill condition.

## malformed_input
- Sin framing o sin conflicto, el motor no debe inventar una vía de rediseño fuerte.

## edge_cases
- `economic_logic` debe existir sin volverse ROI.
- `next_evidence` debe ser específica al conflicto.

## pass_criteria
- filas con `trigger_hypothesis`, `kill_condition` y `next_evidence`
- estados de evidencia válidos
- `conditional_redesign_count` sincronizado

## fail_criteria
- recomendación final disfrazada;
- falsificación vacía;
- count desincronizado.
