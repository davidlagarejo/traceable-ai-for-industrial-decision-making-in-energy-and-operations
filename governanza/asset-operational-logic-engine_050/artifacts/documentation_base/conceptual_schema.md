# Conceptual Schema — Asset Operational Logic Engine

Motor ID: motor_050

## entities
- `OperationalLogicBundle`: resultado completo del motor para un activo.
- `ProcessMap`: lógica de transformación, pérdida y tradeoff operacional.
- `SubsystemRecord`: subsistema operativo relevante.
- `EquipmentDominanceRecord`: equipo o clase dominante dentro del activo.
- `MaintenanceDependencyRecord`: dependencia de mantenimiento asociada a subsistemas y operación.
- `ControlBoundaryRecord`: frontera de control o responsabilidad.
- `OperationalValueFlowRecord`: tramo del flujo de valor operacional.

## relationships
- `asset_family_research_profile` + `local_evidence_binding_register` → `ProcessMap`
- `ProcessMap` → `SubsystemRecord`
- `SubsystemRecord` + binding state → `EquipmentDominanceRecord`
- `SubsystemRecord` + binding state → `MaintenanceDependencyRecord`
- `asset_family_research_profile` + binding state → `ControlBoundaryRecord`
- `ProcessMap` → `OperationalValueFlowRecord`
- todas las anteriores → `OperationalLogicBundle`

## key_fields
- `OperationalLogicBundle`: `operational_logic_state`, `process_map`, `subsystem_register`, `equipment_dominance_register`, `maintenance_dependency_map`, `control_boundary_map`, `operational_value_flow_register`
- `ProcessMap`: `asset_family`, `transformations`, `loss_points`, `market_value_link`
- `SubsystemRecord`: `subsystem_name`, `role`, `dominance_reason`, `evidence_state`
- `EquipmentDominanceRecord`: `equipment_class`, `dominance_basis`, `binding_state`
- `MaintenanceDependencyRecord`: `dependency_name`, `affected_subsystem`, `failure_consequence`
- `ControlBoundaryRecord`: `boundary_name`, `boundary_type`, `why_it_matters`
- `OperationalValueFlowRecord`: `stage`, `value_effect`, `boundary_dependency`
