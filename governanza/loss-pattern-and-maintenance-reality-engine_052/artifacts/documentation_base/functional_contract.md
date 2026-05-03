# Functional Contract — Loss Pattern and Maintenance Reality Engine

Motor ID: motor_052

## inputs
- `asset_family_research_profile`
  Tipo: `dict`
  Productor: `motor_049`
- `operational_intake_pack`
  Tipo: `dict`
  Productor: `motor_049`
- `dynamic_intake_question_register`
  Tipo: `list[dict]`
  Productor: `motor_049`
- `subsystem_register`
  Tipo: `list[dict]`
  Productor: `motor_050`
- `maintenance_dependency_map`
  Tipo: `list[dict]`
  Productor: `motor_050`
- `peer_requirement_register`
  Tipo: `list[dict]`
  Productor: `motor_051`

## outputs
- registers de pérdida
  Tipo: `list[dict]`
  Consumidores: `motor_053`, `motor_054`
  Contenido: `loss_pattern_hypothesis_register`, `activated_pattern_register`, `pattern_discrimination_register`, `industrial_common_sense_register`.
- registers de mantenimiento
  Tipo: `list[dict]`
  Consumidores: strategy y claim governance
  Contenido: `maintenance_reality_register`, `maintenance_proof_gap_register`, `downtime_dependency_register`.
- registers de medición y prudencia hardware
  Tipo: `list[dict]`
  Consumidores: redesign y strategy
  Contenido: `measurement_strategy_register`, `hardware_minimality_register`, `power_quality_hypothesis_register`, `leakage_hypothesis_register`.
- señales derivadas planas
  Tipo: `int`
  Consumidores: observabilidad

## limits
- no convierte evidencia parcial de mantenimiento en prueba de mala práctica observada;
- no define pérdida final ni asigna causalidad cerrada;
- no pide hardware si no existe hipótesis y estrategia mínima que lo justifiquen;
- no suprime downtime risk cuando maintenance evidence es débil;
- no colapsa maintenance maturity, leakage y power quality en una sola narrativa.

## validations
- manufacturing sin fuentes locales de mantenimiento debe producir `maintenance maturity not evidenced`;
- manufacturing con maintenance sources debe subir a `maintenance maturity partially evidenced`;
- deben existir gaps de prueba y dependencias de downtime cuando la evidencia sigue incompleta;
- `measurement_strategy_register` y `hardware_minimality_register` deben seguir hipótesis reales;
- todos los counts planos deben coincidir con sus registers.
