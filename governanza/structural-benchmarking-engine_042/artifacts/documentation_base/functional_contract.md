# Functional Contract — Structural Benchmarking Engine

Motor ID: motor_042

## inputs
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012.facility_prior.target_definition`, con fallback a `motor_007.target_definition_contract`
- `archetype_resolution`
  Tipo: `dict`
  Productor: `motor_039`
- `system_abstraction`
  Tipo: `dict[str, dict]`
  Productor: `motor_037`
- `dominant_variable_register`
  Tipo: `list[dict]`
  Productor: `motor_038`
- `dataset_coverage_register`
  Tipo: `list[dict]`
  Productor: `motor_012`

## outputs
- `structural_benchmark_register`
  Tipo: `list[dict]`
  Consumidores: `motor_043`, framing, redesign
  Contenido: `dimension`, `subject_asset`, `peer_or_benchmark`, `difference`, `evidence_state`, `interpretation`.
- `structural_benchmark_count`
  Tipo: `int`
  Consumidores: observabilidad

## limits
- no acepta benchmark como prueba de waste o upside final;
- no produce peers competitivos específicos ni ranking;
- no usa benchmark genérico fuera del arquetipo y coverage disponibles;
- nunca omite la interpretación acotada del benchmark.

## validations
- buildings NYC deben poder producir benchmark sobre contexto LL84/LL97 y screening público;
- manufacturing debe poder producir benchmark thermal-process bounded, no area-only desperdicio directo;
- todas las filas deben incluir interpretación explícita;
- `structural_benchmark_count` debe coincidir con el register.
