# Master Concept Document — Asset Operational Logic Engine

Motor ID: motor_050

## purpose
Asset Operational Logic Engine transforma el perfil de investigación de familia de activo y el estado de local binding producido por `motor_049` en una lógica operacional explícita. Su trabajo es modelar cómo fluye el valor operativo del activo, qué subsistemas importan, dónde están las fronteras de control, qué equipos dominan y qué dependencias de mantenimiento deben existir para pensar congruencia de manera físicamente defendible. No emite comparables ni tesis finales; organiza la estructura operacional sobre la que los motores `051` a `054` pueden razonar.

## what_it_does
- consume `asset_family_research_profile` y `local_evidence_binding_register` para derivar `route_state`, binding state y familia operativa efectiva;
- construye `process_map` con transformaciones, puntos de pérdida, tradeoffs de mercado y lógica de creación de valor;
- emite `subsystem_register` y `equipment_dominance_register` alineados a la familia de activo observada;
- produce `maintenance_dependency_map`, `control_boundary_map` y `operational_value_flow_register`;
- degrada a `inadmissible_until_asset_identity_bounded` cuando el caso no es todavía un activo operacional bounded.

## what_it_does_not_do
- no decide fairness entre peers ni construye comparables finales;
- no traduce regulación, finanzas o contexto estratégico final; eso pertenece a `motor_053` y `motor_054`;
- no convierte bindings parciales en conclusión fuerte de causalidad;
- no calcula ahorro, ROI, CAPEX ni priorización ejecutiva;
- no corrige el `route_state` upstream ni reabre clasificación básica del target.

## why_it_exists
Existe como motor separado porque la lane de congruencia necesitaba una frontera entre “qué evidencia tengo” y “cómo opera el activo si esa evidencia es cierta”. `motor_049` organiza research mode, packs y blockers; `motor_050` convierte ese bundle en proceso, subsistemas, maintenance dependencies y fronteras de control sin todavía entrar a comparación, finanzas o claim governance final.
