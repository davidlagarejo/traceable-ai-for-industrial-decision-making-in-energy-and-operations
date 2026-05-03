# Technical Schema — Asset Operational Logic Engine

Motor ID: motor_050

## entities
- `OperationalLogicBundle`
  Resultado completo del motor.
- `ProcessMap`
  Mapa de proceso y valor operacional por familia.
- `SubsystemRecord`
  Subsistema relevante para la operación.
- `EquipmentDominanceRecord`
  Equipo o clase de equipo dominante.
- `MaintenanceDependencyRecord`
  Dependencia de mantenimiento vinculada a la operación.
- `ControlBoundaryRecord`
  Frontera de responsabilidad o control.
- `OperationalValueFlowRecord`
  Paso del flujo de valor derivado del proceso.

## fields
- `OperationalLogicBundle`
  `operational_logic_state: str (required)`
  `process_map: ProcessMap (required)`
  `subsystem_register: list[SubsystemRecord] (required)`
  `equipment_dominance_register: list[EquipmentDominanceRecord] (required)`
  `maintenance_dependency_map: list[MaintenanceDependencyRecord] (required)`
  `control_boundary_map: list[ControlBoundaryRecord] (required)`
  `operational_value_flow_register: list[OperationalValueFlowRecord] (required)`
  `subsystem_count: int (required)`
  `control_boundary_count: int (required)`
  `equipment_dominance_count: int (required)`
- `ProcessMap`
  `asset_family: str (required)`
  `process_map_state: str (required)`
  `inputs: list[dict] (required)`
  `transformations: list[dict] (required)`
  `support_systems: list[dict] (required)`
  `loss_points: list[dict] (required)`
  `outputs: list[dict] (required)`
  `market_value_link: list[dict] (required)`
  `human_control_points: list[dict] (required)`
  `automatic_control_points: list[dict] (required)`
  `regulatory_friction_points: list[dict] (required)`
- `SubsystemRecord`
  `subsystem_name: str (required)`
  `subsystem_role: str (required)`
  `primary_equipment_classes: list[str] (required)`
  `dominant_energy_forms: list[str] (required)`
  `control_mode: str (required)`
  `maintenance_dependency: str (required)`
  `evidence_state: str (required)`
  `why_it_may_matter: str (required)`
- `EquipmentDominanceRecord`
  `equipment_class: str (required)`
  `dominance_basis: str (required)`
  `binding_state: str (required)`
- `MaintenanceDependencyRecord`
  `dependency_name: str (required)`
  `affected_subsystem: str (required)`
  `failure_consequence: str (required)`
- `ControlBoundaryRecord`
  `boundary_name: str (required)`
  `boundary_logic: str (required)`
  `evidence_state: str (required)`
  `binding_state: str (required)`
- `OperationalValueFlowRecord`
  `stage: str (required)`
  `value_effect: str (required)`
  `boundary_dependency: str (required)`

## relationships
- `asset_family_research_profile` y `local_evidence_binding_register` → `ProcessMap`
- `ProcessMap` → `SubsystemRecord`, `OperationalValueFlowRecord`
- `SubsystemRecord` + binding state → `EquipmentDominanceRecord`, `MaintenanceDependencyRecord`
- `asset_family_research_profile` + binding state → `ControlBoundaryRecord`
- todas las anteriores → `OperationalLogicBundle`

## identifiers
- Identificador natural de `OperationalLogicBundle`: target bounded heredado de `motor_049.case_fingerprint`.
- Identificador natural de `SubsystemRecord`: `subsystem_name`.
- Identificador natural de `ControlBoundaryRecord`: `boundary_name`.
- Identificador natural de `EquipmentDominanceRecord`: `equipment_class`.

## versioning
- Un cambio en `asset_family`, `route_state` o binding state implica nueva versión lógica del bundle.
- Las counts planas deben regenerarse con cada nueva versión de registros estructurados.
- La estructura del `process_map` se versiona junto con la familia operacional resuelta.

## lineage
- `process_map` hereda lineage del `asset_family_research_profile` de `motor_049`.
- `control_boundary_map` y `equipment_dominance_register` heredan lineage adicional desde `local_evidence_binding_register`.
- `operational_value_flow_register` depende exclusivamente del `process_map`.
- Las counts planas dependen del bundle ya materializado, no de una fuente paralela.
