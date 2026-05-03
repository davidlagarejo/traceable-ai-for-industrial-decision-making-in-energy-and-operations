# Failure Modes — Asset Operational Logic Engine

Motor ID: motor_050

## failure_modes_list
- `UNBOUNDED_OPERATIONAL_FICTION`: emitir proceso y subsistemas para un activo no bounded.
- `FAMILY_COLLAPSE`: usar la misma lógica operacional para building, manufacturing y logistics.
- `BOUNDARY_ERASURE`: omitir owner-vs-tenant o process-vs-support boundaries cuando son centrales al activo.
- `COUNT_SURFACE_DRIFT`: devolver counts planos inconsistentes con los registros estructurados.

## anti_patterns
- construir comparables o claims financieros dentro de este motor;
- tratar el `local_evidence_binding_register` como decoración y no como condicionante de fronteras y dominancia.

## degradation_signals
- `operational_logic_state` seedado con `subsystem_register` vacío en casos claramente bounded;
- boundaries genéricas repetidas en familias distintas;
- warehouse o manufacturing saliendo sin tradeoffs o loss points específicos.
