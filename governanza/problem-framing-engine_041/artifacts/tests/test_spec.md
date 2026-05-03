# Test Spec — Problem Framing Engine

Motor ID: motor_041

## happy_path
- Building: reframe owner economics and compliance around owner-managed base-building systems.
- Manufacturing: reframe energy problem around structural process load, uptime and maintenance dependence.
- Logistics: when the legacy frame is inadmissible, translate the congruence fallback into a valid problem statement.

## sparse_case
- Con conflictos incompletos, el motor debe seguir emitiendo un framing bounded y evidencia_needed explícita.

## malformed_input
- Sin abstracción, variables o conflicto válido, el motor no debe inventar una raíz final ni una solución.

## edge_cases
- `asset_screening` o `INADMISSIBLE_CLAIM` pueden activar el fallback de `motor_051`.
- `linked_layers` debe sobrevivir en la traducción fallback.

## pass_criteria
- Cada fila preserva `stated_problem` y `reframed_problem`.
- `evidence_state` es válido.
- `problem_framing_count` coincide con el register.
- Aparece evidencia mínima utilizable downstream.

## fail_criteria
- Reframing genérico o retórico.
- Pérdida del problema original.
- Recomendación de solución final.
- Count desincronizado.
