# Design Done Criteria — Problem Framing Engine

Motor ID: motor_041

## criteria
- Building, manufacturing y logistics producen reformulaciones distintas y defendibles.
- Cada fila conserva explícitamente `stated_problem` y `reframed_problem`.
- El fallback de congruencia sólo entra cuando el framing estructural directo no es admisible.
- `problem_framing_count` permanece sincronizado.
- La salida sirve a `motor_044`, `motor_045` y `motor_046` sin adelantar rediseño, finanzas o discriminación final.
- El motor puede dejar un framing corto pero útil si el caso sólo permite una contradicción dominante.

## review_notes
- Un diseño terminado obliga a un revisor a ver con claridad cuál era el problema aparente y cuál es el problema que realmente debe probarse.
- La documentación no queda aceptable si la reformulación suena correcta pero no define evidencia mínima.
- El cierre formal requiere que el caso logistics conserve traducción válida desde `motor_051` y no colapse a una frase genérica de comparabilidad.
