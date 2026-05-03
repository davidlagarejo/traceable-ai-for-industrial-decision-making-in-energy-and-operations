# Functional Contract — Fair Comparison and Congruence Engine

Motor ID: motor_051

## inputs
- `asset_family_research_profile`
  Tipo: `dict`
  Productor: `motor_049`
  Contenido mínimo: `asset_family`, `route_state` y framing de familia operativa.
- `operational_intake_pack`
  Tipo: `dict`
  Productor: `motor_049`
  Uso: packs, gaps, dynamic intake y superficie de evidence mode para validar comparabilidad.
- `local_evidence_binding_register`
  Tipo: `list[dict]`
  Productor: `motor_049`
  Uso: controlar madurez de boundary y fairness real.
- `gap_taxonomy_register`
  Tipo: `list[dict]`
  Productor: `motor_049`
  Uso: extender la taxonomía con riesgos de comparación.
- `rival_hypothesis_register`, `hypothesis_discrimination_register`, `claim_impact_register`
  Tipo: `list[dict]`
  Productor: `motor_049`
  Uso: preservar hipótesis y efectos de claim ya identificados.
- `process_map`
  Tipo: `dict`
  Productor: `motor_050`
  Uso: determinar basis de comparabilidad, service level, throughput y lógica operacional.
- `control_boundary_map`
  Tipo: `list[dict]`
  Productor: `motor_050`
  Uso: validar boundaries owner-vs-tenant, process-vs-support u otras.
- `subsystem_register`
  Tipo: `list[dict]`
  Productor: `motor_050`
  Uso: construir correlaciones estructurales.
- `maintenance_dependency_map`
  Tipo: `list[dict]`
  Productor: `motor_050`
  Uso: detectar contradicciones y correlaciones cross-layer.

## outputs
- `fair_comparison_profile`
  Tipo: `dict`
  Consumidores: `motor_052`, `motor_053`, `motor_054`
  Contenido: estado general de comparabilidad, normalizaciones requeridas y shortcuts prohibidos.
- registers de comparabilidad
  Tipo: `list[dict]`
  Consumidores: peers, benchmarks, claim governance
  Contenido: `normalization_requirements_register`, `peer_requirement_register`, `peer_candidate_family_register`, `comparison_validity_register`, `comparison_blocker_register`, `comparison_not_yet_valid_register`, `invalid_comparison_risk_register`.
- registers de correlación y congruencia
  Tipo: `list[dict]` y `dict`
  Consumidores: `motor_052`–`motor_054`
  Contenido: `structural_correlation_register`, `structural_correlation_graph`, `correlation_priority_register`, `gold_nugget_candidate_register`, `cross_layer_congruence_register`, `invalid_problem_frame_register`.
- registers extendidos de gap e hipótesis
  Tipo: `list[dict]`
  Consumidores: claim governance y síntesis
  Contenido: `gap_taxonomy_register`, `evidence_need_class_register`, `rival_hypothesis_register`, `hypothesis_discrimination_register`, `claim_impact_register`.
- señales derivadas planas
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: counts de cada register principal.

## limits
- no admite peers válidos sólo porque el activo “se parece” superficialmente a otro;
- no emite recomendaciones estratégicas finales ni gold nuggets ejecutivos finales;
- no suprime blockers o risks para hacer el caso comparable artificialmente;
- no convierte correlaciones en causalidad cerrada;
- no reemplaza la necesidad de normalización por intuición de experto.

## validations
- `comparison_validity_register` debe justificar por qué una comparación es o no comparable y qué normalización requiere;
- buildings deben exigir boundary owner-vs-tenant cuando corresponda;
- manufacturing no puede validar comparaciones area-based sin throughput normalization;
- logistics no puede validar comparaciones area-only sin service-level normalization;
- contradicciones cross-layer deben materializarse cuando regulación, control, proceso o framing aparente no encajan;
- los counts planos deben coincidir con el tamaño real de los registros.
