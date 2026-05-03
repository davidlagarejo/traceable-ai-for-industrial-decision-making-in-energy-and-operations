# Test Spec — Asset Operational Logic Engine

Motor ID: motor_050

## happy_path
- Caso NYC building bounded: `operational_logic_state=research_seeded_operational_logic`, la primera transformación es `building_services_delivery`, existe `HVAC / central plant` y el boundary `owner_vs_tenant_load_boundary`.
- Caso manufacturing bounded: `process_map.asset_family=industrial_manufacturing`, el primer loss point es `process_vs_waste_ambiguity`, existe `compressed air` y el boundary `process_load_vs_support_system_load`.
- Caso logistics bounded: `process_map.asset_family=logistics_warehouse`, existe `service_level_cost_tradeoff` y al menos un equipo dominante.

## sparse_case
- Con binding local limitado pero asset bounded, el motor debe seguir emitiendo lógica operacional seedada sin inventar boundaries más fuertes que la evidencia disponible.

## malformed_input
- Si el perfil de research no contiene una familia operacional usable o el target no es bounded, la salida debe degradar a estado inadmisible.
- Si los registros upstream están vacíos o mal formados, el motor no debe conservar subsistemas o boundaries fuertes por defecto.

## edge_cases
- Un target clasificado como mailing address o HQ debe salir con `subsystem_register=[]` y `control_boundary_map=[]`.
- Distintas familias operativas deben producir `process_map` y boundaries distintas; no puede existir una plantilla única indiferenciada.

## pass_criteria
- `subsystem_count`, `control_boundary_count` y `equipment_dominance_count` coinciden con el tamaño real de los registros.
- Building, manufacturing y logistics reproducen superficies distintas y coherentes con tests runtime.
- El estado inadmisible vacía las superficies operativas fuertes.

## fail_criteria
- Counts planos desincronizados.
- Boundaries activas en un target inadmisible.
- `process_map.asset_family` contradice la familia resuelta por `motor_049`.
