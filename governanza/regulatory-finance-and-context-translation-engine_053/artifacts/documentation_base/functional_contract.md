# Functional Contract — Regulatory, Finance and Context Translation Engine

Motor ID: motor_053

## inputs
- `facility_prior` / `asset_field_register`
  Tipo: `dict` + `list[dict]`
  Productor: `motor_012`
  Uso: target definition y contexto mínimo del activo.
- `source_register`
  Tipo: `list[dict]`
  Productor: `motor_028`
  Uso: señales de permisos, contexto local, tarifa y cultura ejecutiva observable.
- `asset_family_research_profile` y `operational_intake_pack`
  Tipo: `dict`
  Productor: `motor_049`
  Uso: familia del activo, identidad operacional e intake base.
- `subsystem_register` y `operational_value_flow_register`
  Tipo: `list[dict]`
  Productor: `motor_050`
  Uso: dominios físicos, mantenimiento y drivers de valor.
- `fair_comparison_profile`, `cross_layer_congruence_register`, `invalid_comparison_risk_register`, `comparison_not_yet_valid_register`, `structural_correlation_graph`
  Tipo: `dict` + `list[dict]`
  Productor: `motor_051`
  Uso: dependencias de comparabilidad y riesgo de mala lectura.
- `maintenance_reality_register`, `measurement_strategy_register`, `power_quality_hypothesis_register`, `hardware_minimality_register`
  Tipo: `list[dict]`
  Productor: `motor_052`
  Uso: dependencia física, gaps de medición y madurez de mantenimiento.

## outputs
- `regulatory_physics_register`
- `permit_signal_register`
- `regulatory_constraint_register`
- `finance_physics_dependency_register`
- `cost_driver_dependency_register`
- `capital_logic_register`
- `financial_exposure_type_register`
- `underwriting_misread_register`
- `value_leakage_register`
- `climate_location_context_register`
- `utility_tariff_context_register`
- `culture_execution_proxy_register`
- y sus count surfaces principales.

## limits
- no emite decisión final de underwriting;
- no usa contexto de tarifa, clima o cultura como prueba sustitutiva;
- no convierte maintenance plausibility en pérdida económica observada;
- no reemplaza la síntesis estratégica final;
- toda traducción financiera debe seguir atada a una dependencia física explícita.

## validations
- cada register debe mantener su vocabulario propio;
- los counts deben permanecer sincronizados;
- building debe poder ligar owner economics a control boundary y presión whole-building;
- manufacturing debe poder ligar costo a proceso, uptime y downtime;
- el motor debe distinguir allowed_use y prohibited_use en los context registers.
