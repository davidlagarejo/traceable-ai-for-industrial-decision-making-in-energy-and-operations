# Failure Modes Spec — Asset Operational Logic Engine

Motor ID: motor_050

## failure_modes_list
- `OPERATING_LOGIC_WITHOUT_BOUNDING`: lógica operacional emitida para target no bounded.
- `FAMILY_TEMPLATE_COLLAPSE`: misma plantilla de proceso para building, manufacturing y logistics.
- `BOUNDARY_SUPPRESSION`: desaparición de fronteras críticas owner-vs-tenant o process-vs-support.
- `COUNT_DRIFT`: counts planos diferentes de los registros estructurados.

## anti_patterns
- intentar cerrar fairness, finance o strategy dentro de este motor;
- ignorar el binding state y devolver boundaries máximas por defecto.

## degradation_signals
- building, manufacturing y logistics comparten casi el mismo `process_map`;
- `equipment_dominance_count=0` en casos bounded que deberían tener dominancia clara;
- estado inadmisible con subsistemas o boundaries todavía activas.

## expensive_errors
- propagar boundaries equivocadas hacia fairness, loss o finanzas downstream;
- construir value flow sobre una familia operativa mal resuelta;
- usar lógica operacional fuerte para apoyar claims finales cuando el activo ni siquiera está bounded.
