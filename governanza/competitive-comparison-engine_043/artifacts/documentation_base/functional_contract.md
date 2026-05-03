# Functional Contract — Competitive Comparison Engine

Motor ID: motor_043

## inputs
- `archetype_resolution`
  Tipo: `dict`
  Productor: `motor_039`
  Uso: escoger el tipo de peer o performer admisible.
- `structural_benchmark_register`
  Tipo: `list[dict]`
  Productor: `motor_042`
  Uso: base estructural sobre la que puede construirse una comparación.
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012` / `motor_007`
  Uso: distinguir building vs manufacturing y evitar peer drift.

## outputs
- `competitive_comparison_register`
  Tipo: `list[dict]`
  Consumidores: `motor_044`, `motor_047`, síntesis ejecutiva
  Contenido: `better_performer`, `what_they_do_better`, `structural_advantage`, `why_it_matters`, `transferability`, `peer_type`, `what_it_proves`, `what_it_does_not_prove`, `source_reference`, `evidence_needed`, `evidence_state`, `comparison_mode`.
- `competitive_comparison_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: número total de comparaciones emitidas.

## limits
- no usa comparación para probar waste por sí sola;
- no salta de benchmark a CAPEX;
- no mezcla peer estructural con peer financiero o estratégico;
- si la evidencia es arquetipal, debe decirlo como tal;
- no puede borrar límites de transferabilidad.

## validations
- cada fila debe decir qué hace mejor el peer y qué no prueba todavía;
- `comparison_mode` debe ser coherente con la evidencia disponible;
- manufacturing debe poder exponer proceso y uptime, no sólo “eficiencia” genérica;
- building debe poder exponer submetering, leases o BMS discipline;
- `competitive_comparison_count` debe coincidir con el register.
