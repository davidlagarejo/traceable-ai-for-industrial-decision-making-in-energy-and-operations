# Functional Contract — Asset Operational Logic Engine

Motor ID: motor_050

## inputs
- `asset_family_research_profile`
  Tipo: `dict`
  Productor: `motor_049`
  Contenido mínimo: `asset_family`, `route_state`, y señales suficientes para mapear proceso y subsistemas.
- `local_evidence_binding_register`
  Tipo: `list[dict]`
  Productor: `motor_049`
  Uso: subir o degradar binding state para control boundaries, maintenance y process logic.
- `target_definition_contract`
  Tipo: `dict`
  Productor: `motor_007`, transitivamente presente en el bundle que alimenta a `motor_049`
  Uso: contexto semántico del activo cuando el perfil de research necesita fallback.

## outputs
- `operational_logic_state`
  Tipo: `str`
  Consumidores: `motor_051`, `motor_052`, `motor_053`, `motor_054`
  Valores: `research_seeded_operational_logic` o `inadmissible_until_asset_identity_bounded`.
- `process_map`
  Tipo: `dict`
  Consumidores: fairness, loss, finance
  Contenido: familia de activo, transformaciones, loss points, tradeoffs y market-value links.
- `subsystem_register`
  Tipo: `list[dict]`
  Consumidores: loss, redesign, evidence validators
  Contenido: subsistemas operativos dominantes del activo.
- `equipment_dominance_register`
  Tipo: `list[dict]`
  Consumidores: loss, redesign, finance
  Contenido: equipos o clases de equipo con peso operacional dominante.
- `maintenance_dependency_map`
  Tipo: `list[dict]`
  Consumidores: `motor_052`
  Contenido: dependencias de mantenimiento por subsistema y modo operativo.
- `control_boundary_map`
  Tipo: `list[dict]`
  Consumidores: fairness, finance, claim governance
  Contenido: fronteras owner vs tenant, process vs support, service-level vs cost u otras según familia.
- `operational_value_flow_register`
  Tipo: `list[dict]`
  Consumidores: finanzas y síntesis
  Contenido: pasos del flujo de valor operacional derivados del `process_map`.
- señales derivadas planas
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: `subsystem_count`, `control_boundary_count`, `equipment_dominance_count`.

## limits
- no emite lógica operacional válida si `route_state` no es `operational_asset_candidate`;
- no inventa subsistemas ajenos a la familia operativa ni a los bindings disponibles;
- no produce comparables, rankings o claims económicos finales;
- nunca usa este motor para tapar blockers de entity/boundary que siguen abiertos en `motor_049`;
- no declara control boundaries cerradas por intuición si binding state sigue débil.

## validations
- si `route_state` no es `operational_asset_candidate`, `operational_logic_state` debe ser inadmisible y `subsystem_register` y `control_boundary_map` deben salir vacíos;
- `process_map.asset_family` debe ser coherente con la familia resuelta por `motor_049`;
- toda familia operacional válida debe producir al menos un subsistema o una lógica de proceso identificable;
- `equipment_dominance_count`, `subsystem_count` y `control_boundary_count` deben coincidir con el largo real de sus registros;
- los boundaries emitidos deben corresponder a la familia: building, manufacturing o logistics no pueden compartir mapas genéricos vacíos.
