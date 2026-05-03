# Master Concept Doc — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## core_job

`motor_045` traduce el caso estructural en exposición financiera bounded. No calcula ROI ni payback. Expone qué supuesto financiero está en riesgo, qué evidencia falta y cómo se ve la incertidumbre por capa antes de que alguien convierta la narrativa en economics cerrados.

## why_it_exists

Después de `motor_044`, el framework ya tiene:

- conflicto estructural;
- problema reformulado;
- comparación bounded;
- y posibles vías de rediseño condicionadas.

Lo que todavía falta es disciplina financiera: distinguir qué parte del caso puede sostener screening y qué parte sigue bloqueando outputs como ahorro capturable, ROI o payback.

## behavioral_contract

- Building: debe poder bloquear economía owner-side cuando la frontera de control sigue abierta.
- Manufacturing: debe poder traducir la hipótesis de waste estructural a riesgo de CAPEX mal secuenciado.
- En ambos casos debe emitir una matriz `evidence_state_by_layer` para mostrar dónde está realmente abierto el caso.

## non_goals

- no calcula payback;
- no calcula ROI final;
- no abre savings claims fuertes;
- no sustituye la capa de evidencia mínima discriminante.
