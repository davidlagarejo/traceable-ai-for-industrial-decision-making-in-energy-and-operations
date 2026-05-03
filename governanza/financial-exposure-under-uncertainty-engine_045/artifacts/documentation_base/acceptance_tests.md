# Acceptance Tests — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## acceptance_cases
- Building:
  Debe bloquear outputs de ROI y payback cuando el upside owner-controllable siga atado a control boundary y tenant-driven loads.
- Manufacturing:
  Debe traducir la hipótesis de waste estructural a riesgo de CAPEX si el problema real es carga de proceso o downtime.
- Layer matrix:
  Debe emitir un `evidence_state_by_layer_register` de 12 filas con capas explícitas y preguntas dominantes abiertas.

## acceptance_threshold
- todas las filas financieras muestran supuestos y consecuencias si están mal;
- el registro por capas cubre las 12 capas previstas;
- los counts están sincronizados;
- la salida no cruza a underwriting o ROI cerrados.
