# Design Done Criteria — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## criteria
- Building y manufacturing producen exposiciones financieras distintas y coherentes.
- Cada fila financiera conserva output permitido y output prohibido.
- `evidence_state_by_layer_register` cubre 12 capas con preguntas dominantes y riesgos si están mal.
- Los counts permanecen sincronizados.
- La salida sirve a `motor_034` y a la síntesis sin invadir ROI final o claim libre.

## review_notes
- El diseño no está terminado si una fila puede usarse directamente como ROI recommendation.
- Tampoco si el registro por capas no explica por qué finance, regulation o control/responsibility siguen abiertos.
- El cierre formal requiere que un revisor pueda reconstruir qué supuesto financiero se está protegiendo y qué evidencia lo desbloquearía.
