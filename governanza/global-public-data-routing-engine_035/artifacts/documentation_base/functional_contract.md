# Functional Contract — Global Public Data Routing Engine

Motor ID: motor_035

## inputs
- `subject_definition_contract`
  Tipo: `dict`
  Productor: `motor_001`, con fallback desde `motor_006` o `motor_007`
  Contenido mínimo: `address_raw` y ancla básica del sujeto.
- `target_definition_contract`
  Tipo: `dict`
  Productor: `motor_001`, con fallback desde `motor_006` o `motor_007`
  Contenido mínimo: `jurisdiction_scope`, `target_type`, `decision_intent`, `target_scope`.
- `target_classification_object`
  Tipo: `dict`
  Productor: `motor_007`
  Contenido mínimo: `target_type`, `classification_confidence`, `reason`.
- `subject_gate_passed`
  Tipo: `bool`
  Productor: `motor_007`
  Uso: bloquear rutas técnicas cuando el sujeto ni siquiera pasó el gate básico.
- `technical_substrate_readiness`
  Tipo: `str`
  Productor: `motor_007`
  Valores esperados: niveles como `partial` o `insufficient`.
- `observable_clusters`
  Tipo: `dict`
  Productor: `motor_007`, con fallback a `motor_006.asset_identity_resolution.intake_observables`
  Uso: medir si hay suficiente contexto para routing físico, regulatorio y benchmark.
- `upstream_recommended_report_type` y `upstream_prohibited_report_types`
  Tipo: `str` y `list[str]`
  Productor: `motor_007`
  Uso: preservar restricciones de superficie de reporte ya detectadas upstream.

## outputs
- `source_routing_plan`
  Tipo: `dict`
  Consumidores: `motor_028`, `motor_012`, auditoría
  Contenido: `mandatory_sources`, `high_priority_sources`, `optional_sources`, `disallowed_substitutions`, `routing_notes`.
- `report_type_switch_recommendation`
  Tipo: `dict`
  Consumidores: `motor_016`, capas de gobernanza
  Contenido: tipo recomendado, tipos prohibidos y justificación del switch.
- `target_classification_result`
  Tipo: `dict`
  Consumidores: `motor_028`, validadores, packaging
  Contenido: clase operacional efectiva y si la ruta técnica está permitida.
- `jurisdiction_resolution`
  Tipo: `dict`
  Consumidores: `motor_028`, `motor_012`
  Contenido: estado, ciudad, clase jurisdiccional, stack regulatorio enrutable.
- `critical_field_summary`
  Tipo: `dict`
  Consumidores: `motor_028`, monitoreo
  Contenido: conteo y lista de campos críticos faltantes.
- señales derivadas planas
  Tipo: escalares y listas
  Consumidores: runtime y reporting
  Contenido: `routing_ready`, `asset_type`, `decision_type`, `jurisdiction_class`, `regulatory_stack`, `mandatory_sources`, `high_priority_sources`, `optional_sources`, `disallowed_substitutions`, `missing_critical_fields`, `report_type_allowed`, `report_type_prohibited`.

## limits
- no acepta evidencia local como sustituto de routing público; sólo enruta discovery público;
- no acepta que un caso con `subject_gate_passed=false` sea promovido a ruta técnica fuerte;
- nunca produce resultados de scraping, facts finales ni datasets materializados;
- nunca reemplaza fuentes locales obligatorias por benchmarks genéricos cuando la ruta las declara inadmisibles;
- nunca degrada ni promueve el caso por intuición narrativa: sólo por contratos, clasificación, jurisdicción y clusters observables;
- nunca modifica contratos upstream; sólo los interpreta para routing.

## validations
- debe existir una definición mínima de target con `jurisdiction_scope` y `target_type`, aunque sea degradada;
- la clasificación del target y el estado del subject gate deben ser coherentes con la superficie de reporte recomendada;
- la clase jurisdiccional resuelta debe mapear a un set consistente de fuentes obligatorias y prioritarias;
- si el caso no es técnicamente enrutable, `mandatory_sources` debe vaciarse o reducirse de forma compatible con la degradación del caso;
- las `disallowed_substitutions` deben explicitar qué shortcuts quedan prohibidos para discovery y benchmarking;
- el output debe preservar listas planas listas para downstream además del bundle estructurado completo.
