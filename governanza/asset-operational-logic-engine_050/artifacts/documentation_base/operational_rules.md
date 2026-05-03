# Operational Rules — Asset Operational Logic Engine

Motor ID: motor_050

## rules
1. Si `route_state` no es `operational_asset_candidate`, el motor debe degradar a `inadmissible_until_asset_identity_bounded`.
2. La familia operativa resuelta controla la forma del `process_map`, del `subsystem_register` y del `control_boundary_map`.
3. `local_evidence_binding_register` puede fortalecer fronteras y dominancia, pero no reemplaza el gating básico de identidad operacional.
4. Toda lógica building debe exponer service delivery y owner-vs-tenant boundary cuando aplica.
5. Toda lógica manufacturing debe distinguir proceso principal de cargas de soporte y pérdidas de proceso.
6. Toda lógica logistics debe exponer tradeoff entre service level y costo operativo.

## invariants
- `subsystem_count`, `control_boundary_count` y `equipment_dominance_count` deben igualar el tamaño real de sus registros;
- `operational_value_flow_register` debe derivarse del `process_map` y no de una fuente paralela;
- un estado inadmisible implica `subsystem_register=[]` y `control_boundary_map=[]`;
- `process_map.asset_family` debe permanecer consistente con la familia resuelta upstream.

## forbidden_operations
- emitir lógica operacional fuerte para targets que siguen siendo mailing address o HQ;
- colapsar process load y support load en manufacturing cuando la frontera es precisamente el problema;
- borrar boundaries de responsabilidad para simplificar comparaciones downstream;
- usar este motor para cerrar fairness, finanzas o estrategia;
- producir counts que no coinciden con los registros reales.
