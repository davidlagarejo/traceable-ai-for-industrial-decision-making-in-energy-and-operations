# Acceptance Tests — Conditional Redesign Engine

Motor ID: motor_044

## acceptance_cases
- Building:
  Debe producir hipótesis sobre tenant-driven loads y control boundary con rediseño lease/submetering o green-lease.
- Manufacturing:
  Debe producir hipótesis sobre carga estructural vs soporte, y mostrar una falsificación ligada a compressed air u otros soportes.

## acceptance_threshold
- todas las filas tienen `trigger_hypothesis`, `economic_logic`, `kill_condition` y `next_evidence`;
- el rediseño se mantiene como hipótesis;
- `conditional_redesign_count` sincronizado.
