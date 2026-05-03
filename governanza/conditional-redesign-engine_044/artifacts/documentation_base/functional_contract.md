# Functional Contract — Conditional Redesign Engine

Motor ID: motor_044

## inputs
- `dominant_variable_register`
  Tipo: `list[dict]`
  Productor: `motor_038`
  Uso: variables que disparan o bloquean hipótesis de rediseño.
- `cross_layer_conflict_register`
  Tipo: `list[dict]`
  Productor: `motor_040`
  Uso: contradicciones que el rediseño intenta resolver.
- `problem_framing_register`
  Tipo: `list[dict]`
  Productor: `motor_041`
  Uso: problema reformulado que delimita el rediseño admisible.
- `competitive_comparison_register`
  Tipo: `list[dict]`
  Productor: `motor_043`
  Uso: prácticas o configuraciones estructurales comparables.
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012` / `motor_007`
  Uso: escoger redesign building vs manufacturing.

## outputs
- `conditional_redesign_register`
  Tipo: `list[dict]`
  Consumidores: `motor_045`, `motor_046`, síntesis ejecutiva, reportes
  Contenido: `hypothesis`, `evidence_state`, `if_confirmed`, `redesign_direction`, `if_falsified`, `trigger_hypothesis`, `conflict_resolved`, `economic_logic`, `evidence_needed`, `kill_condition`, `next_evidence`.
- `conditional_redesign_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: número total de hipótesis de rediseño emitidas.

## limits
- no presenta redesign como recomendación final;
- no cierra ahorro, payback o ROI;
- no emite una hipótesis si no existe conflicto o framing que la sostenga;
- toda fila debe poder morir si la evidencia la falsifica.

## validations
- cada fila necesita `trigger_hypothesis`, `kill_condition` y `next_evidence`;
- building debe poder producir rediseño lease/submetering o control-boundary;
- manufacturing debe poder producir rediseño ligado a process load o support systems;
- `conditional_redesign_count` debe coincidir con el register.
