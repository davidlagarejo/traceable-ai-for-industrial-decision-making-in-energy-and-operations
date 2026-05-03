# Functional Contract — Minimum Evidence For Discrimination Engine

Motor ID: motor_046

## inputs
- `dominant_variable_register`
  Tipo: `list[dict]`
  Productor: `motor_038`
  Uso: hipótesis y variables rivales que deben discriminarse.
- `cross_layer_conflict_register`
  Tipo: `list[dict]`
  Productor: `motor_040`
  Uso: contradicciones que exigen evidencia discriminante.
- `problem_framing_register`
  Tipo: `list[dict]`
  Productor: `motor_041`
  Uso: problema correcto que la evidencia debe resolver.
- `conditional_redesign_register`
  Tipo: `list[dict]`
  Productor: `motor_044`
  Uso: vías de rediseño que sólo deberían desbloquearse con evidencia mínima suficiente.
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012` / `motor_007`
  Uso: escoger paquete discriminante building vs manufacturing.

## outputs
- `minimum_evidence_for_discrimination_register`
  Tipo: `list[dict]`
  Consumidores: `motor_033`, intake guidance, síntesis, reportes
  Contenido: `rival_hypotheses`, `minimum_evidence`, `source`, `what_it_confirms`, `what_it_falsifies`, `unlocks`.
- `minimum_evidence_for_discrimination_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: número total de paquetes discriminantes emitidos.

## limits
- no puede emitir checklist genérica;
- no puede pedir evidencia que no discrimine hipótesis reales;
- no puede desbloquear acción sin explicar qué confirma o falsifica;
- debe preferir sets mínimos de alto valor informativo.

## validations
- building debe poder pedir tenant metering map, topology y LL97 basis;
- manufacturing debe poder pedir throughput, bills, inventory y downtime logs;
- cada fila debe tener `what_it_confirms`, `what_it_falsifies` y `unlocks`;
- `minimum_evidence_for_discrimination_count` debe coincidir con el register.
