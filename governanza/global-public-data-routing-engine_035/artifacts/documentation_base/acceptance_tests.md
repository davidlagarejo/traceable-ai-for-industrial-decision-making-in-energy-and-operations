# Acceptance Tests — Global Public Data Routing Engine

Motor ID: motor_035

## happy_path
1. NYC office tower with bounded operating-asset context.
   Input: dirección NYC, `OPERATING_ASSET`, subject gate aprobado, readiness parcial y clusters regulatorios / benchmark poblados.
   Expected output: `routing_ready=true`, `jurisdiction_class=high_data_availability_building`, `nyc_ll84_energy_benchmarking` y `nyc_pluto_property` en `mandatory_sources`, y recomendación de `Minimum Evidence Report`.
2. Houston industrial or manufacturing facility with process intent.
   Input: target industrial, intención `process_change`, subject gate aprobado y señales de operating regime.
   Expected output: promoción a `industrial_facility`, `tceq_permits_and_emissions` en obligatorias y fuentes de proceso industrial en `high_priority_sources`.

## edge_cases
1. HQ / mailing-address case in San Francisco.
   Input: clasificación `CORPORATE_HEADQUARTERS`, subject gate no aprobado y clusters mínimos.
   Correct output: `routing_ready=false`, `mandatory_sources=[]`, surface degradada a `Target Classification Brief`, y prohibición de `Full Technical Report`.
2. California building routed to city- and county-specific portals.
   Input: Oakland o Los Angeles con clasificación operativa válida.
   Correct output: property record local en `mandatory_sources`, permits y utility-territory context en `high_priority_sources`, sin colapsar todo a un portal estatal genérico.
3. Texas building with incomplete but sufficient routing context.
   Input: Houston downtown asset screening con clusters regulatorios básicos.
   Correct output: property record HCAD como obligatorio, permit context y utility territory como prioritarios, aun si no existe benchmark urbano tan rico como NYC.

## rejection_criteria
1. Rechazar o degradar si no existe `target_definition_contract` mínimamente enrutable y el motor sólo recibe issuer context ambiguo.
2. Rechazar promoción técnica si `subject_gate_passed=false` y el caso intenta reclamar ruta de scraping técnico fuerte.
3. Rechazar rutas que pretendan sustituir property record o permit context por benchmarks agregados cuando la política de routing lo prohíbe.
