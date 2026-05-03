# Acceptance Tests — Asset Operational Logic Engine

Motor ID: motor_050

## happy_path
- Caso building bounded en NYC: `operational_logic_state=research_seeded_operational_logic`, `process_map.transformations[0].stage=building_services_delivery`, subsistemas incluyen `HVAC / central plant` y el boundary map incluye `owner_vs_tenant_load_boundary`.
- Caso manufacturing bounded: `process_map.asset_family=industrial_manufacturing`, `loss_points[0].stage=process_vs_waste_ambiguity`, subsistemas incluyen `compressed air` y el boundary map incluye `process_load_vs_support_system_load`.
- Caso logistics bounded: `process_map.asset_family=logistics_warehouse`, `market_value_link[0].stage=service_level_cost_tradeoff` y existe al menos un equipo dominante.

## edge_cases
- Si el target no está bounded como activo operacional, la salida debe degradar a inadmisible y vaciar subsistemas y boundaries.
- Si bindings locales son débiles, la lógica puede existir como seed, pero no debe inventar control boundaries más fuertes que la evidencia disponible.

## rejection_criteria
- Falla si `process_map.asset_family` contradice la familia resuelta por `motor_049`.
- Falla si el estado inadmisible conserva subsistemas o boundaries activos.
- Falla si los counts planos no coinciden con los registros emitidos.
