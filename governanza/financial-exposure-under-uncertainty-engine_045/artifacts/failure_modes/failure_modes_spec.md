# Failure Modes Spec — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## failure_modes_list
- `ROI_SHORTCUT`: ROI liberado con evidencia insuficiente.
- `LAYER_MATRIX_COLLAPSE`: faltan capas o preguntas dominantes.
- `SAVINGS_CLAIM_DRIFT`: savings claim permitido donde debería estar prohibido.
- `TRANSFERABILITY_BLINDNESS`: la comparación bounded se usa como garantía financiera.

## anti_patterns
- usar compliance pressure como sustituto de captura económica;
- cerrar CAPEX logic sin throughput o control boundary;
- dejar el register por layer como simple checklist.

## degradation_signals
- las 12 capas no aparecen;
- finance sale `OBSERVED_FACT` demasiado pronto;
- `prohibited_financial_output` es vago o vacío.

## expensive_errors
- CAPEX mal priorizado;
- screening vendido como underwriting;
- claims financieros que luego el framework no puede defender.
