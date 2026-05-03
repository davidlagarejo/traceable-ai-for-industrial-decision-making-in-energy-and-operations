# Design Done Criteria — Regulatory, Finance and Context Translation Engine

Motor ID: motor_053

## criteria
- Building y manufacturing generan superficies regulatorias y financieras distintas y defendibles.
- Toda hipótesis financiera conserva una dependencia física explícita.
- Los context registers exponen `allowed_use` y `prohibited_use`.
- Los counts principales permanecen sincronizados con sus registers.
- La salida sirve a `motor_054` y a la síntesis ejecutiva sin invadir decisión final.
- El motor distingue con claridad constraint, context, capital logic y exposure type.

## review_notes
- El diseño no está terminado si una fila financiera podría existir sin `physical_dependency`.
- Tampoco si clima o tarifa quedan presentados como prueba suficiente de pérdida o estrategia.
- El cierre formal requiere que un revisor pueda separar con facilidad regulación, finanzas y contexto, y entender cómo cada superficie limita la siguiente capa.
