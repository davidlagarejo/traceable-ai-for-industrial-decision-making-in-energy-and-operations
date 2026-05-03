# Failure Modes — Cross-Layer Conflict Engine

Motor ID: motor_040

## failure_modes_list
- `CONFLICT_SUPPRESSION`: contradicciones relevantes no emitidas.
- `FINANCE_EARLY_ACTION_DRIFT`: supuestos económicos prematuros no marcados como conflicto.
- `FALLBACK_INFORMATION_LOSS`: traducción desde `motor_051` pierde detalle crítico.
- `EMPTY_CONFLICT_REGISTER_FALSE_CLEANNESS`: register vacío interpretado como coherencia real.

## anti_patterns
- usar este motor como simple logger decorativo;
- tratar conflictos como warnings blandos aunque bloqueen claims o CAPEX.

## degradation_signals
- building cases complejos sin conflicto regulación-control;
- manufacturing con proceso ambiguo pero register vacío;
- fallback rows con muy poca semántica comparadas contra el registro directo.
