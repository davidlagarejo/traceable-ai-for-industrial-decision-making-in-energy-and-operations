# Failure Modes Spec — Loss Pattern and Maintenance Reality Engine

Motor ID: motor_052

## failure_modes_list
- `PARTIAL_TO_OBSERVED_DRIFT`: evidence parcial convertida en observación fuerte.
- `DOWNTIME_GAP_ERASURE`: falta de dependencia de downtime cuando debería existir.
- `MEASUREMENT_STRATEGY_HOLLOW`: estrategia de medición sin hipótesis real detrás.
- `HARDWARE_TRIGGER_OVERUSE`: hardware activado demasiado pronto.

## anti_patterns
- usar maintenance sources como prueba de “mal maintenance”;
- saltar directamente a hardware o CAPEX.

## degradation_signals
- maintenance reality demasiado categórica;
- no aparecen proof gaps aunque la maintenance state siga parcial;
- estrategias de medición idénticas para familias o casos distintos.

## expensive_errors
- inducir intervenciones de hardware innecesarias;
- traducir síntomas en causas equivocadas;
- sesgar strategy final con una lectura falsa de maintenance maturity.
