# Failure Modes — Global Public Data Routing Engine

Motor ID: motor_035

## failure_modes_list
1. `HQ_promotion_error`
   Síntoma: una sede corporativa o dirección administrativa recibe ruta técnica de activo operativo.
   Riesgo: discovery público falso, benchmarking inválido y reportes técnicos prematuros.
2. `jurisdiction_collapse`
   Síntoma: el motor enruta a fuentes genéricas y omite property / permit portals locales que eran obligatorios.
   Riesgo: pérdida de especificidad territorial y falsa sensación de cobertura.
3. `benchmark_substitution_leak`
   Síntoma: benchmarks o issuer context aparecen como sustitutos de registros locales obligatorios.
   Riesgo: inferencias técnicas construidas sobre evidencia inadecuada.
4. `report_surface_misalignment`
   Síntoma: el motor deja `routing_ready=true` pero recomienda una superficie degradada inconsistente, o viceversa.
   Riesgo: downstream contradictorio entre discovery, governance y packaging.

## anti_patterns
1. Tratar cualquier dirección postal corporativa como si ya fuera un activo operativo físicamente acotado.
2. Diseñar la ruta pública alrededor de lo que es fácil scrapear, en lugar de alrededor de lo que es obligatorio para el caso.
3. Usar un único paquete de fuentes para todos los inmuebles o instalaciones sin distinguir jurisdicción ni tipo de activo.

## degradation_signals
- aumento de `missing_critical_fields` sin cambio correspondiente en la degradación de superficie de reporte;
- `mandatory_sources` vacías en casos que sí deberían enrutar a property, permits o benchmarking local;
- aparición repetida de `disallowed_substitutions` pero sin bloqueo efectivo downstream;
- discrepancias entre `target_type_classification`, `asset_type` y `routing_ready`;
- rutas multi-ciudad que siempre devuelven la misma familia de portales, señal de colapso jurisdiccional.
