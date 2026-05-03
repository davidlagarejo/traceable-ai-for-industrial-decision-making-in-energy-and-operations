# Functional Contract — Problem Framing Engine

Motor ID: motor_041

## inputs
- `system_abstraction`
  Tipo: `dict[str, dict]`
  Productor: `motor_037`
  Uso: control, regulación, load drivers y límites del sistema.
- `dominant_variable_register`
  Tipo: `list[dict]`
  Productor: `motor_038`
  Uso: variables que podrían dominar la explicación real del caso.
- `cross_layer_conflict_register`
  Tipo: `list[dict]`
  Productor: `motor_040`
  Uso: contradicciones que fuerzan el reencuadre.
- `invalid_problem_frame_register`
  Tipo: `list[dict]`
  Productor: `motor_051`
  Uso: fallback cuando el framing legado es inadmisible o demasiado genérico.
- `cross_layer_congruence_register`
  Tipo: `list[dict]`
  Productor: `motor_051`
  Uso: capas ligadas al problema traducido desde el fallback.
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012` / `motor_007`
  Uso: escoger framing building, manufacturing o logistics.

## outputs
- `problem_framing_register`
  Tipo: `list[dict]`
  Consumidores: `motor_044`, `motor_045`, `motor_046`, síntesis ejecutiva
  Contenido: `stated_problem`, `reframed_problem`, `why_original_framing_may_be_wrong`, `evidence_needed`, `strategic_risk`, `evidence_state`, `linked_layers`.
- `problem_framing_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: número total de filas emitidas.

## limits
- no convierte un conflicto en solución;
- no transforma benchmark en prueba final;
- no omite el framing original: siempre debe quedar visible qué se está corrigiendo;
- puede usar fallback desde `motor_051`, pero sólo cuando el framing estructural no sea admisible o quede hueco;
- no puede emitir un problema genérico si la contradicción real ya está localizada.

## validations
- cada fila debe exponer el problema original y el problema corregido;
- `evidence_needed` debe permanecer explícito;
- `linked_layers` debe sobrevivir cuando el framing venga del fallback de congruencia;
- buildings deben poder aterrizar owner control y compliance pressure;
- manufacturing debe poder aterrizar process load, uptime o maintenance dependence;
- `problem_framing_count` debe coincidir con el largo del register.
