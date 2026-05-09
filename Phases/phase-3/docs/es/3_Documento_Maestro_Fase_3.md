# 3A — Alcance, unidad material principal y recorte MVP de Fase 3

> Nota canonica de gobernanza: este documento pertenece a una linea de trabajo anterior del framework. El documento constitucional autoritativo para la arquitectura integrada de 8 fases es `Phases/phase-0/docs/en/0_Phase_0_Master_Document.md`. Si este documento entra en conflicto con Fase 0 en numeracion, autoridad de fase, claims permitidos, techos semanticos o logica de boundaries, Fase 0 gobierna hasta que esta fase sea reconstituida formalmente.

## 1. Propósito exacto de la subfase
Definir la constitución de Fase 3 como la capa del framework que materializa, organiza y hace visible contenido ya soportado por objetos upstream, bajo disciplina epistemológica explícita. Su función es fijar qué es exactamente el Reporting Engine, cuál es su unidad material principal, cuál es su unidad superior de ensamblaje, qué entra y qué queda fuera del MVP, cuál es la separación mínima de audiencia y dónde termina su autoridad frente a una posible Fase 4.

## 2. Por qué esta subfase importa
Sin esta subfase, el sistema corre dos riesgos opuestos: que reporting se confunda con razonamiento terminal, o que por miedo a excederse se reduzca a una mecánica pobre de resúmenes y tablas. Fase 3 debe bloquear ambos errores.

El Reporting Engine no debe conformarse con producir salidas correctas. Debe aspirar a reportes técnicamente absorbentes, estructuralmente elegantes, sectorialmente finos y capaces de volver inteligible un caso complejo como sistema, sin exceder el soporte real del framework.

## 3. Qué es Fase 3 y qué no es
Fase 3 es una capa de materialización gobernada. Su autoridad consiste en seleccionar, articular, compactar y ensamblar objetos upstream admisibles en salidas visibles útiles para consumo humano, preservando conflicto, incertidumbre, supuestos, dependencia de validación y trazabilidad.

La ley madre de Fase 3 queda fijada desde aquí y gobierna todo el resto del documento: **ninguna salida visible de Fase 3 puede decir más de lo que soportan los objetos upstream de los que depende**. Las subfases posteriores no crean leyes paralelas; solo especializan esta ley en pipeline, ensamblaje, audiencia, compactación y circulación.

Fase 3 no es una capa de descubrimiento de hipótesis nuevas, ni una capa de validación empírica, ni una capa de compliance final, ni una capa de recomendación terminal. Tampoco es una licencia para sustituir estructura por storytelling ornamental, ni una fase cuyo valor dependa de diseño visual decorativo o de persuasión implícita.

## 4. Qué entra en Fase 3 y qué no entra
En Fase 3 entra la transformación visible y gobernada de contenido upstream admisible: ensamblaje material de outputs, compresión semántica proporcional, organización temática, vistas de audiencia, tablas disciplinadas, captions gobernados, agenda de validación visible, artifacts subordinados y export estructurado.

Queda fuera todo lo que suponga descubrir, verificar o cerrar el caso más allá del soporte disponible. Fase 3 puede organizar y volver legible contenido ya soportado, sin elevar su fuerza ni cerrar por presentación lo que sigue abierto upstream.

## 5. Unidad material principal
La unidad material principal de Fase 3 es el **`Output Block`**. Debe entenderse como la unidad mínima visible que puede ser trazada a objetos upstream, ensamblada en más de una vista, auditada, degradada, reasignada o bloqueada sin perder identidad material ni romper el reporte completo.

`Output Block` es la unidad correcta porque separa contenido gobernado de composición documental, porta límites explícitos, conserva linaje, tolera reutilización y sostiene control fino de circulación. También funciona bien en casos sparse, donde el sistema debe poder publicar poco sin inflar narrativa para compensar escasez material.

`report_object`, `report_section`, `artifact_object` y `delivery_package` no son adecuados como unidad principal porque mezclan niveles, dependen demasiado del layout final, cubren solo una porción de la superficie visible o pertenecen al nivel de ensamblaje y distribución.

## 6. Unidad superior de ensamblaje
La unidad superior de ensamblaje de Fase 3 es el **`Report Package`**. No es la unidad principal del sistema, sino la composición gobernada de `Output Blocks` ya admitidos.

El `Report Package` existe para volver inteligible el caso como sistema. Su valor no está solo en reunir piezas correctas, sino en ordenarlas, contrastarlas y articularlas para que el lector pueda leer tensiones, restricciones, dependencias y rutas de validación en una secuencia integrada.

Ese carácter integrador no le concede soberanía. Ningún `Report Package` puede contener contenido que no exista primero como bloque trazable. El paquete compone, organiza y proyecta; no inventa ni corrige el caso.

## 7. Política mínima de audiencia
El MVP admite solo dos vistas humanas: `technical_view` y `executive_view`. Esta separación es deliberadamente mínima. Permite responder a dos regímenes reales de lectura sin fragmentar prematuramente el sistema en taxonomías de stakeholder demasiado costosas de gobernar.

La diferencia entre vistas es documental, no epistemológica. `technical_view` explicita con mayor densidad relaciones, restricciones y trazas; `executive_view` reduce fricción, concentra frentes activos y mejora orientación. Ninguna de las dos puede alterar el estatus del caso ni hacer sonar más resuelto lo que sigue condicionado.

## 8. Recorte MVP realista
El MVP de Fase 3 debe ser compacto en arquitectura y profundo en capacidad documental. Lo compacto es el conjunto de unidades, vistas y outputs; lo profundo puede ser el documento cuando el caso lo amerita.

Ese recorte mínimo queda fijado en:
- `output_block_register`
- `audience_view_register`
- `artifact_register`
- `machine_export_bundle`
- `report_package`
- dos vistas humanas
- una taxonomía mínima de bloques ya alineada con el resto de la fase
- y reglas de circulación suficientes para gobernar publicación

La taxonomía mínima del MVP no debe introducir una ontología provisional distinta de la usada después. Desde 3A queda alineada con la gramática material que el resto del documento desarrolla. Como mínimo deben existir:
- `executive_summary_block`
- `technical_summary_block`
- `evidence_table_block`
- `uncertainty_block`
- `conflict_block`
- `opportunity_block`
- `validation_agenda_block`
- `next_steps_block`
- `artifact_caption_block`

Esta taxonomía es mínima, no exhaustiva. Su objetivo es dar una base suficiente para construir reportes serios sin abrir todavía una proliferación innecesaria de tipos.

## 9. Qué sería sobre-ingeniería en esta subfase
Constituye sobre-ingeniería en 3A toda expansión que aumente superficie sin aumentar capacidad real de materialización gobernada. Entran aquí theming visual sofisticado, layouts complejos, librerías amplias de charts, separación excesiva por stakeholder, dashboards, personalización avanzada, narrativa multimodal ambiciosa y reporting regulatorio final. También lo es multiplicar tipos de bloque, vistas u outputs antes de haber demostrado que el núcleo del MVP puede producir documentos fuertes con una arquitectura todavía compacta.

## 10. Frontera con Fase 4
Fase 3 termina cuando contenido upstream admisible queda convertido en salidas visibles gobernadas, legibles y exportables. Si luego existe una Fase 4, esa fase podrá manejar outputs de mayor peso terminal. Por definición, Fase 3 no puede comportarse como verification bridge, compliance engine ni final recommendation layer.

La frontera debe permanecer dura. Fase 3 puede mostrar conflicto, ordenar prioridades preliminares, hacer visible una agenda de validación y articular una lectura interna potente del caso. No puede cerrar verificación, certificar cumplimiento ni transformar oportunidad candidata en decisión terminal.

## 11. Errores típicos que esta subfase debe bloquear
- Confundir legibilidad con permiso para intensificar certeza.
- Reducir Fase 3 a una capa defensiva incapaz de producir documentos verdaderamente sólidos.
- Tratar `Report Package` como unidad primaria y perder control granular.
- Usar una ontología provisional de bloques distinta de la que luego gobierna la fase.
- Convertir audiencia en versiones con distinta verdad.
- Usar diseño o storytelling para compensar debilidad material upstream.
- Expandir vistas, layouts o outputs antes de cerrar el núcleo del MVP.

## 12. Decisiones exactas que 3A deja cerradas
- Fase 3 es una capa de materialización gobernada de contenido upstream admisible.
- La ley madre de la fase queda fijada desde 3A y gobierna el resto del documento.
- La unidad material principal es el `Output Block`.
- La unidad superior de ensamblaje es el `Report Package`.
- El MVP solo admite `technical_view` y `executive_view`.
- El MVP es compacto en arquitectura, pero puede producir documentos profundos cuando el caso lo exige.
- La taxonomía mínima de bloques queda alineada desde 3A con la gramática material desarrollada después.
- Quedan fuera del alcance de Fase 3 la validación empírica, el cierre terminal del caso y la proliferación ornamental de formatos o productos.
- La frontera con Fase 4 queda explícitamente cerrada.

## 13. Criterio de terminado de la subfase
La subfase 3A se considera cerrada cuando Fase 3 queda definida con claridad como capa de materialización gobernada; cuando la ley madre del documento queda instalada como principio central único; cuando `Output Block`, `Report Package`, la política mínima de audiencia y el recorte realista del MVP quedan fijados sin ambigüedad; y cuando la fase aparece como una arquitectura compacta capaz de producir documentación fuerte sin exceder el soporte del sistema.

# 3A.3 — Arquitectura temática transversal del Report Package

## 1. Propósito exacto de la subfase
Definir la arquitectura temática transversal del `Report Package` como la gramática que permite organizar múltiples frentes del caso sin convertir esa organización en invención libre. Su función es distinguir tipo material de bloque y capa temática transversal, fijar las capas mínimas del MVP y establecer cómo temas y subtemas emergen de objetos upstream trazables para producir lectura profunda, integrada y disciplinada.

## 2. Por qué esta subfase importa
Sin arquitectura temática transversal, el reporte cae en una de dos formas de pobreza. O bien se vuelve una sucesión de bloques correctos pero inconexos, incapaces de producir visión sistémica. O bien compensa esa debilidad con secciones prestigiosas, subtítulos decorativos y falsa sofisticación.

Esta subfase importa porque la arquitectura temática no solo disciplina qué puede mostrarse. También habilita verdadera potencia documental: capacidad de articular múltiples frentes del caso, mostrar dependencias cruzadas, ordenar tensiones no triviales y volver inteligible la estructura de restricciones, trade-offs y rutas de validación que definen el caso como sistema.

## 3. Qué significa que Fase 3 sí define la arquitectura temática del reporte
Que Fase 3 defina la arquitectura temática significa que sí puede decidir qué frentes del caso merecen visibilidad, cómo agruparlos, qué temas requieren mayor desarrollo y en qué secuencia conviene exponerlos. Esa autoridad es documental y estructural. No consiste en decidir libremente qué sería interesante decir, sino en organizar de forma legible contenido ya soportado.

Su autoridad consiste en organizar, articular y hacer visible contenido ya soportado, sin exceder el estado epistemológico del caso. La arquitectura temática existe para hacer el reporte más potente, no para volverlo más arbitrario.

## 4. Diferencia entre tipo material de bloque y capa temática transversal
La arquitectura de Fase 3 opera sobre dos dimensiones distintas.

La primera es el **tipo material del bloque**. Aquí pertenecen formas como:
- `executive_summary_block`
- `technical_summary_block`
- `evidence_table_block`
- `uncertainty_block`
- `conflict_block`
- `opportunity_block`
- `validation_agenda_block`
- `next_steps_block`
- `artifact_caption_block`

El tipo material define la función visible del bloque, su forma de compactación y el tipo de operación documental que puede cumplir.

La segunda es la **capa temática transversal**. Cada bloque puede pertenecer a una o más capas como:
- `technical_layer`
- `regulatory_layer`
- `financial_layer`
- `prioritization_layer`
- `validation_lineage_layer`

La capa temática no define qué clase de bloque es el bloque, sino desde qué frente del caso se lo está leyendo. Esta doble estructura permite profundidad sin inflar innecesariamente la ontología material.

## 5. Capas temáticas transversales mínimas del MVP
La **`technical_layer`** hace visible estructura técnica, tensiones operativas, mecanismos plausibles, restricciones materiales y dependencias funcionales del caso.

La **`regulatory_layer`** hace visible presión regulatoria plausible, régimen preliminar, flags aplicables, ventanas de exigencia y dependencia de validación para confirmar aplicabilidad.

La **`financial_layer`** hace visible lógica económica preliminar, restricciones CAPEX/OPEX, sensibilidad de viabilidad, exposición tarifaria, compatibilidad preliminar con mecanismos financieros y beneficios relevantes cuando el soporte existe.

La **`prioritization_layer`** hace visible orden preliminar de atención, razones de foco, urgencia relativa, bloqueos, secuencias y restricciones de acción.

La **`validation_lineage_layer`** hace visible cómo se sostiene el estado actual del caso, qué lo fortalece o lo debilita, qué depende de benchmark, prior, hipótesis o experiencia de campo y por qué la siguiente validación importa.

Estas cinco capas no agotan la realidad del caso, pero estabilizan una gramática transversal suficiente para que el documento pueda crecer sin perder estructura.

## 6. Cómo emergen temas y subtemas del documento
Los temas y subtemas no emergen solo del tipo de bloque, ni solo de la audiencia, ni de la prosa libre del LLM. Emergen de la combinación entre objetos upstream activos, bloques materialmente admisibles, capas temáticas activadas y relevancia real para comprensión, priorización o validación.

Se entiende por **tema** un frente material de lectura del caso. Se entiende por **subtema** un refinamiento material de ese frente cuando la lectura necesita más granularidad para seguir siendo fiel y útil. Se entiende por **narrativa técnica estructurada** la operación legítima que articula bloques, temas y dependencias para que el lector comprenda por qué un frente importa, qué lo condiciona y cómo se conecta con otros frentes del caso.

Esa narrativa técnica es admisible cuando ordena relaciones ya soportadas. Deja de ser admisible cuando rellena huecos, inventa causalidad o usa fluidez de lectura para simular cierre.

## 7. Profundidad documental sin inflación epistemológica
Fase 3 puede producir documentos amplios, detallados, técnicamente absorbentes, financieramente serios, regulatoriamente útiles y agradables de leer por su organización. Esa profundidad no es un lujo secundario; es parte de la razón de existir del Reporting Engine.

La profundidad documental debe aumentar articulación, trazabilidad e inteligibilidad sistémica, no fuerza epistemológica. Un documento puede volverse más rico porque separa mejor frentes, hace visibles dependencias cruzadas, organiza mejor sus tensiones y vuelve legible un sistema complejo. No por eso se vuelve más concluyente.

## 8. Uso admisible de documentos base y marcos metodológicos
Fase 3 puede usar documentos base, marcos metodológicos y referencias admitidas para enriquecer estructura, framing, taxonomía temática y orden de exposición. Ese uso es legítimo cuando vuelve el documento más maduro y mejor organizado.

Esos materiales no sustituyen evidencia local, no endurecen claims por sí solos y no activan temas sustantivos que el caso no sostenga materialmente. Su valor está en disciplinar la construcción documental, no en prestar autoridad epistemológica al caso.

## 9. Política de evaluación interna acotada
Dentro del MVP, el `Report Package` puede aspirar a verse como una **evaluación interna técnico-operativa-financiera-regulatoria acotada al caso**. Esa formulación debe leerse como una ambición válida de robustez documental, no como promesa de cierre terminal.

El reporte puede sentirse serio, profundo y estructuralmente maduro. Puede dar la sensación de estar leyendo el caso por dentro. Pero esa sensación debe provenir de densidad articulada y no de sobreafirmación.

## 10. Regla anti-decoración temática
Queda bloqueada la decoración temática. No deben entrar temas, subtemas ni secciones cuya principal función sea sonar sofisticados, llenar espacio o imitar estilo consultivo sin carga material real.

Si un frente no mejora comprensión, priorización, validación o trazabilidad, no debe entrar. La elegancia estructural es deseable; la ornamentación vacía no.

## 11. Errores típicos que esta subfase debe bloquear
- Confundir arquitectura temática con licencia para inventar contenido.
- Tratar profundidad documental como sinónimo de mayor verdad.
- Usar la audiencia para decidir por sí sola qué temas existen.
- Reemplazar linkage estructurado por prosa articulada pero no trazable.
- Convertir la `validation_lineage_layer` en narrativa decorativa.
- Multiplicar temas por prestigio sectorial o densidad superficial.

## 12. Decisiones exactas que 3A.3 deja cerradas
- Fase 3 sí define la arquitectura temática del reporte.
- Esa arquitectura existe tanto para disciplinar como para potenciar el documento.
- Tema, subtema y narrativa técnica estructurada quedan distinguidos como operaciones diferentes.
- Tipo material de bloque y capa temática transversal son dimensiones distintas y complementarias.
- Las capas mínimas del MVP quedan fijadas en `technical_layer`, `regulatory_layer`, `financial_layer`, `prioritization_layer` y `validation_lineage_layer`.
- La profundidad documental puede crecer por articulación y organización, no por aumento de fuerza epistemológica.
- Los documentos base pueden enriquecer estructura y framing, pero no sustituir soporte del caso.
- La política de evaluación interna queda autorizada en sentido acotado.
- Toda decoración temática sin función material queda bloqueada.

## 13. Criterio de terminado de la subfase
La subfase 3A.3 se considera cerrada cuando la arquitectura temática queda definida como capacidad positiva del Reporting Engine y no solo como mecanismo defensivo; cuando tipo material, capa temática, tema, subtema y narrativa técnica estructurada quedan diferenciados sin ruido conceptual; y cuando el documento puede aspirar a lectura integrada del caso sin apartarse de la ley madre fijada en 3A.

# 3A.4 — Biblioteca temática sectorial y reglas de activación de temas y subtemas por industria

## 1. Propósito exacto de la subfase
Definir la biblioteca temática sectorial como la capacidad del Reporting Engine para expandir cobertura, profundidad y diferenciación industrial sin deslizarse hacia arbitrariedad narrativa ni fabricación de contenido. Su función es fijar la arquitectura multinivel de módulos, temas y subtemas sectoriales y las reglas disciplinadas bajo las cuales se activan.

## 2. Por qué esta subfase importa
Un esquema temático demasiado corto empobrece el reporte, vuelve genérico el caso y pierde tensiones reales de segundo orden. Un esquema demasiado laxo convierte profundidad en teatro documental. Esta subfase importa porque habilita amplitud seria y, al mismo tiempo, impide exuberancia vacía.

La riqueza sectorial no es una concesión secundaria del sistema. Es una capacidad central del Reporting Engine. Sin ella, el reporte no podría capturar restricciones operativas reales, dependencias de infraestructura, fricciones regulatorias, estructuras de priorización ni conflictos sectoriales que un esquema genérico no alcanza a expresar.

## 3. Qué significa permitir amplitud y profundidad sectorial en Fase 3
Permitir amplitud y profundidad sectorial significa autorizar que el `Report Package` no se limite a un catálogo corto de temas generales. Puede abrir módulos industriales, temas especializados, subtemas de segundo orden y desarrollos documentales extensos cuando el caso lo amerita.

La amplitud documental puede crecer de forma agresiva cuando el caso lo exige, siempre que la activación permanezca trazable, materialmente pertinente y útil para comprensión, priorización o validación. La expansión sectorial no debe leerse como desviación del framework, sino como una condición para que el documento tenga verdadero valor técnico.

## 4. Arquitectura temática multinivel del Report Package
La arquitectura temática del `Report Package` opera en cuatro niveles:
- Nivel 1 — Capas transversales fijas
- Nivel 2 — Módulos sectoriales o industriales
- Nivel 3 — Temas sectoriales principales
- Nivel 4 — Subtemas activables por caso

Esta jerarquía es conceptual y normativa. Su trabajo es ordenar profundidad, no producir implementación técnica anticipada.

## 5. Capas transversales fijas del MVP
Las capas transversales del MVP son:
- `technical_layer`
- `regulatory_layer`
- `financial_layer`
- `prioritization_layer`
- `validation_lineage_layer`

Estas capas estabilizan la lectura del documento a través de industrias distintas y permiten que la profundidad sectorial crezca sobre un esqueleto común.

## 6. Módulos sectoriales e industriales
Sobre esas capas pueden activarse módulos sectoriales como:
- `manufacturing_module`
- `oil_gas_module`
- `buildings_module`
- `district_energy_module`
- `utilities_module`
- `commercial_real_estate_module`
- `water_wastewater_module`
- `thermal_networks_module`
- `process_industry_module`

La lista no es exhaustiva. Un módulo entra cuando la estructura del caso lo hace pertinente, no porque el sector resulte prestigioso o porque el documento “quede mejor” con más etiquetas.

## 7. Temas sectoriales y subtemas activables por caso
Dentro de cada módulo pueden activarse temas principales como:
- `steam systems`
- `compressed air`
- `process heat`
- `refrigeration`
- `HVAC and controls`
- `power quality`
- `electrical reliability`
- `tariff exposure`
- `maintenance maturity`
- `process criticality`
- `uptime constraints`
- `load profile structure`
- `water-energy coupling`
- `carbon exposure`
- `retrofit feasibility`
- `heat recovery feasibility`
- `electrification readiness`
- `district integration feasibility`
- `waste heat utilization`
- `pressure on compliance timeline`
- `financing structure sensitivity`
- `actionability constraints`

Y subtemas como:
- `steam trap failure patterns`
- `condensate recovery limitations`
- `insulation condition`
- `boiler staging logic`
- `variable speed drive applicability`
- `control architecture opacity`
- `pressure setpoint discipline`
- `production schedule variability`
- `seasonal thermal mismatch`
- `peak demand penalties`
- `transformer loading uncertainty`
- `chiller sequencing quality`
- `cooling tower interaction`
- `leak persistence in compressed air`
- `instrumentation gaps`
- `operator dependence`
- `metering sufficiency`
- `baseline instability`
- `bottlenecks to M&V hardening`
- `financing dependence on short payback`
- `regulatory trigger dates`
- `taxonomic eligibility constraints`
- `evidence weakness in emission claims`
- `conflict between electrification and grid capacity`
- `conflict between operational uptime and retrofit windows`

Estas listas son ilustrativas. Su función es mostrar amplitud esperada, no fijar un catálogo cerrado.

## 8. Qué define la activación de temas y subtemas
La activación temática no puede depender de gusto editorial ni de improvisación del LLM. Debe responder a la combinación de industria o familia de activo, objetos upstream activos, tensiones detectadas, conflictos, oportunidades candidatas, exposición regulatoria plausible, restricciones financieras visibles, criticidad operativa, vacíos de evidencia, agenda de validación y valor real para comprensión o priorización.

Un tema o subtema solo debe entrar si mejora comprensión material del caso, preserva conflicto relevante, altera priorización, fortalece la agenda de validación o aclara restricciones operativas, regulatorias o económicas. Si no cumple alguna de esas funciones, su activación es decorativa y debe bloquearse.

## 9. Relación entre Output Block y arquitectura temática
La arquitectura temática opera sobre `Output Blocks`; no los reemplaza. Un mismo tipo material puede participar en frentes temáticos muy distintos, y un mismo tema puede necesitar bloques de varios tipos.

Esta doble estructura permite variedad sin caos. Da profundidad sin inflar la ontología de bloques y permite documentos ricos sin renunciar a disciplina material.

## 10. Profundidad documental y límites epistemológicos
Fase 3 puede aspirar a producir documentos extensos, con múltiples secciones y subsecciones, varios frentes abiertos al mismo tiempo y fuerte densidad técnica, regulatoria, financiera y operativa. Esa profundidad es parte de la capacidad esperada del sistema.

La profundidad sectorial no constituye una expansión ornamental del sistema, sino una condición para que el reporte capture tensiones de segundo orden, restricciones operativas reales, dependencias de infraestructura, fricciones regulatorias y estructuras de priorización, y no solo riqueza descriptiva.

La amplitud del documento puede crecer; la fuerza epistemológica del caso no. La riqueza temática debe aumentar lectura sistémica, no fuerza del claim.

## 11. Uso admisible de documentos base y marcos metodológicos
Fase 3 puede usar literatura técnica, referencias sectoriales y marcos metodológicos admitidos para enriquecer taxonomía, orden de exposición y framing documental. Ese uso es legítimo cuando vuelve el reporte más fino y mejor estructurado.

No es legítimo usarlos para volver local lo que sigue siendo benchmark, endurecer claims ni fabricar subtemas que el caso no activa materialmente.

## 12. Ejemplos de amplitud y profundidad por industria
- `Manufacturing / process industry`: pueden activarse `steam systems`, `steam trap reliability`, `condensate return constraints`, `distribution losses`, `insulation condition`, `compressed air`, `leak persistence`, `pressure optimization`, `compressor staging`, `process heat`, `thermal integration opportunities`, `heat recovery conflicts`, `production-critical thermal loads`, `power quality`, `voltage events`, `harmonic exposure`, `losses due to poor power quality`, `low-capex fast-payback measures`, `operational shutdown constraints` y `sequencing of interventions`.
- `Buildings / smart buildings`: pueden activarse `HVAC controls`, `scheduling logic`, `setpoint discipline`, `economizer behavior`, `reheat conflicts`, `envelope and thermal demand`, `occupancy mismatch`, `retrofit constraints`, `tariff and peak exposure`, `peak demand penalties`, `control opportunities`, `comfort vs efficiency tension`, `maintenance maturity`, `BMS visibility gaps`, `preliminary regulatory pressure` y `readiness for retro-commissioning`.
- `Oil & Gas / industrial utility environment`: pueden activarse `hazardous-area constraints`, `instrumentation reliability`, `steam and thermal losses`, `uptime-critical systems`, `compliance pressure`, `maintenance access constraints`, `electrification conflicts`, `flare / vent / loss-related process considerations`, `asset integrity interaction` y `decision timing under operational risk`.
- `District energy / thermal networks`: pueden activarse `network topology relevance`, `generation mix`, `thermal storage logic`, `demand mismatch`, `solar integration feasibility`, `waste heat integration`, `hydraulic configuration constraints`, `expansion path dependence`, `capex intensity vs solar fraction` y `economic sensitivity under tariff scenarios`.

## 13. Política de evaluación interna robusta pero acotada
Dentro del MVP, el `Report Package` puede aspirar a verse como una **evaluación interna técnico-operativa-financiera-regulatoria profunda y sectorialmente informada, acotada al caso**.

Debe sentirse seria, profunda y útil. También debe seguir siendo epistemológicamente honesta. Su valor está en organizar múltiples tensiones del caso en una lectura potente, no en imitar un cierre terminal que la fase no posee.

## 14. Regla anti-decoración temática
Queda bloqueada toda activación temática cuyo valor sea principalmente ornamental: subtemas vacíos, ramificaciones prestigiosas sin función, listas largas que no cambian la lectura, taxonomías hermosas pero inútiles y densidad sectorial usada como estética de expertise.

## 15. Errores típicos que esta subfase debe bloquear
- Confundir amplitud temática con aumento de verdad.
- Activar subtemas solo porque son típicos del sector.
- Usar profundidad sectorial para tapar incertidumbre o debilidad de evidencia.
- Tratar la expansión documental como sospechosa por defecto y empobrecer el reporte.
- Confundir referencias sectoriales con soporte específico del caso.

## 16. Decisiones exactas que 3A.4 deja cerradas
- La riqueza sectorial queda autorizada como capacidad central del Reporting Engine.
- La arquitectura temática multinivel queda formalmente fijada.
- Los módulos sectoriales son expandibles y no exhaustivos.
- Temas y subtemas solo se activan por pertinencia material, trazabilidad y utilidad real.
- La amplitud documental puede crecer agresivamente cuando el caso lo exige.
- La profundidad sectorial aumenta valor documental, no fuerza epistemológica.
- Los documentos base pueden enriquecer estructura sectorial, pero no sustituir soporte.
- Toda expansión ornamental queda bloqueada.

## 17. Criterio de terminado de la subfase
La subfase 3A.4 se considera cerrada cuando la biblioteca temática sectorial queda definida como capacidad amplia, profunda y disciplinada; cuando el sistema puede crecer documentalmente sin arbitrariedad; y cuando la expansión temática aparece ya no como concesión defensiva, sino como una condición positiva para producir reportes con verdadera textura industrial.

# 3B.1 — Pipeline de transformación: de objetos upstream a bloques renderizados

## 1. Propósito exacto de la subfase
Definir el pipeline mínimo mediante el cual Fase 3 transforma objetos estructurados upstream en `Output Blocks` visibles, verificables y registrables. Su función es cerrar la naturaleza de la entrada, la secuencia mínima de transformación del MVP, la unidad de control del pipeline, la separación entre selección, mapeo, construcción, verificación y registro, y el output formal intermedio sobre el que descansará el ensamblaje posterior.

## 2. Por qué esta subfase importa
Sin pipeline, el paso desde registros upstream hasta texto visible tendería a ocurrir por continuidad narrativa y no por transformación controlada. Eso debilita trazabilidad, borra función material de cada pieza y vuelve opaca la relación entre soporte y exposición.

El pipeline no existe solo para impedir sobreafirmación. Existe también para asegurar que cada bloque visible llegue al ensamblaje con función clara, soporte legible, ubicación temática coherente y potencial real de contribuir a una lectura sistémica fuerte del caso.

## 3. Naturaleza de la entrada de Fase 3
La entrada de Fase 3 no es texto libre. Fase 3 consume exclusivamente:
- objetos estructurados de Fase 1
- objetos estructurados de Fase 2
- reglas heredadas de Fase 0
- taxonomía de bloques y arquitectura temática ya cerradas
- y, cuando corresponde, documentos base admitidos solo como soporte estructural o contextual

Quedan fuera notas libres, intuiciones no registradas, borradores narrativos no gobernados y cualquier entrada que no sea trazable.

## 4. Pipeline mínimo de transformación del MVP
El pipeline mínimo del MVP contiene seis etapas:

1. **Intake gobernado.** Recibe el universo de objetos candidatos relevantes para el caso.
2. **Selección de material admisible.** Decide qué objetos merecen entrar al rendering por relevancia material y función real.
3. **Mapeo temático-material.** Asigna cada objeto seleccionado a tipo de bloque, capa temática, audiencia posible y función documental.
4. **Construcción disciplinada del bloque.** Genera el bloque visible usando solo el material autorizado por su tipo y propósito.
5. **Verificación de bloque.** Revisa linkage, límites, proporcionalidad verbal, compatibilidad con audiencia y función material.
6. **Registro para ensamblaje.** Incorpora los bloques aprobados al `output_block_register`.

La secuencia no es burocrática. Es la infraestructura mínima para que cada bloque llegue al ensamblaje con identidad clara, soporte reconocible y utilidad documental real.

## 5. Prohibición de salto directo a reporte final
Queda prohibido el patrón `objeto upstream -> reporte final`. La regla formal del pipeline es `objeto upstream -> bloque gobernado -> ensamblaje`.

Deben bloquearse, entre otros, flujos donde `hypothesis_register` alimente directamente un summary final, `opportunity_candidate_matrix` se convierta en recomendación visible, `validation_queue` se transforme sin mediación en roadmap o un artifact circule sin caption y sin control semántico.

## 6. Unidad de control del pipeline
La unidad de control del pipeline es el `Output Block`. El pipeline no opera sobre capítulos completos ni sobre paquetes terminados. Opera sobre unidades mínimas capaces de portar función, límites, trazabilidad y potencial de ensamblaje.

Una sección es demasiado grande para control fino. El bloque permite selección precisa, degradación localizada, bloqueo puntual y reasignación disciplinada.

## 7. Regla de selección versus inclusión
La selección no implica inclusión automática. Un objeto upstream válido no adquiere por ello derecho a aparecer en el reporte.

Solo debe avanzar si cambia la lectura del caso, preserva una tensión relevante, afecta priorización, explica un bloqueo, fortalece validación o evita sobrelectura. Exhaustividad por sí sola no es criterio suficiente.

## 8. Regla de mapeo antes de compactación
El mapeo debe ocurrir antes de cualquier compactación. Primero se fija linaje, tipo de bloque, capa temática, audiencia posible, límites y función documental. Solo después se resume o formula el bloque visible.

Resumir antes de clasificar suele producir distorsión: conflictos que suenan menores, hipótesis que parecen conclusiones o agendas de validación que ya parecen planes de acción.

## 9. Degradación, reubicación y bloqueo
El pipeline debe permitir degradar fuerza semántica, mover material hacia `uncertainty_block` o `conflict_block`, reubicarlo en agenda de validación o bloquear su circulación visible.

Estas salidas no indican fallo del sistema. Indican que la arquitectura conserva control cuando el caso no soporta exposición fuerte en la forma inicialmente considerada.

## 10. Uso restringido de documentos base
Los documentos base solo pueden intervenir para enriquecer mapeo temático, framing estructural u organización del bloque. No pueden cerrar hipótesis, sustituir soporte local ni endurecer claims.

## 11. Output formal de la subfase
La salida formal de 3B.1 es el **`output_block_register`**.

Contiene bloques ya seleccionados, mapeados, construidos, verificados y listos para ensamblaje o auditoría. Es el primer output material plenamente gobernado de Fase 3.

## 12. Errores típicos que esta subfase debe bloquear
- Tratar la entrada de Fase 3 como narrativa previa del caso.
- Convertir registros upstream directamente en texto final.
- Seleccionar por exhaustividad en vez de por función.
- Compactar antes de fijar linaje y función.
- Usar secciones como unidad de control del pipeline.
- Impedir degradación o bloqueo y forzar exposición por inercia.

## 13. Decisiones exactas que 3B.1 deja cerradas
- La entrada de Fase 3 es estructurada y trazable.
- El pipeline mínimo del MVP contiene exactamente seis etapas.
- La unidad de control del pipeline es el `Output Block`.
- Ningún objeto upstream puede saltar directamente al reporte final.
- La selección no equivale a inclusión obligatoria.
- El mapeo antecede a la compactación.
- El pipeline debe permitir degradación, reubicación y bloqueo.
- El output formal de la subfase es el `output_block_register`.

## 14. Criterio de terminado de la subfase
La subfase 3B.1 se considera cerrada cuando el recorrido desde objetos upstream hasta bloques gobernados resulta inequívoco, suficiente y no necesita reinterpretación silenciosa para producir material visible de alta calidad documental.

# 3B.2 — Ensamblaje del Report Package y relación entre vistas, bloques y artifacts

## 1. Propósito exacto de la subfase
Definir el ensamblaje del `Report Package` como una operación de composición gobernada a partir de bloques ya admitidos, proyectados en vistas específicas y complementados por artifacts subordinados. Su función es cerrar qué es exactamente el paquete, cómo se compone, qué relación guarda con las vistas del MVP, qué reglas mínimas de composición debe obedecer, cómo tratar casos sparse y cuál es el output formal de esta etapa.

## 2. Por qué esta subfase importa
Sin esta subfase, el ensamblaje tendería a comportarse como redacción libre del documento final. Las vistas se volverían motores paralelos de escritura, los artifacts pasarían a ser canales persuasivos y el paquete perdería su vínculo fino con los bloques que lo sostienen.

Esta subfase importa porque el `Report Package` no solo debe componer bloques admisibles. Debe ser capaz de volver inteligible el caso como sistema, donde secuencia, contraste entre frentes, articulación temática y subordinación de artifacts contribuyan a comprensión sistémica y no solo a acumulación correcta de piezas.

## 3. Naturaleza del Report Package
El `Report Package` no es un documento monolítico ni una pieza narrativa soberana. Es una composición gobernada de bloques previamente admitidos, ordenados para producir lectura integrada del caso.

Su valor reside en la totalidad organizada. Puede contrastar frentes, mostrar dependencias, agrupar materiales que revelen trade-offs y construir progresiones que vayan desde estructura técnica hacia implicaciones de validación y priorización. Esa sofisticación compositiva es legítima cuando sigue subordinada al soporte real del caso.

## 4. Fuente exclusiva de ensamblaje
El `Report Package` solo puede componerse desde el **`output_block_register`**. Queda bloqueado cualquier ensamblaje directo desde registros upstream, texto suelto, notas libres o formulaciones ad hoc generadas durante composición.

La razón es estructural: si el paquete pudiera incorporar contenido por fuera del registro de bloques, el ensamblaje se convertiría de hecho en una segunda instancia analítica.

## 5. Naturaleza de las vistas de audiencia
`technical_view` y `executive_view` no crean contenido. Son proyecciones disciplinadas del universo de bloques disponible.

Pueden seleccionar, reorganizar, compactar o excluir bloques admitidos, pero no introducir semántica nueva. Su trabajo es modular acceso y densidad de lectura sin producir otra versión del caso.

## 6. Relación entre technical_view y executive_view
Para el MVP, `technical_view` es la vista base estructuralmente más completa. `executive_view` deriva de ella por compactación controlada.

Esta jerarquía importa porque la vista ejecutiva debe simplificar acceso, no gobernar primero el caso y dejar que la técnica lo matice después. La lectura ejecutiva no puede sonar más concluyente, borrar conflicto material ni esconder incertidumbre crítica.

## 7. Relación entre Report Package y artifact_register
Los artifacts son subordinados al `Report Package`. Solo pueden circular si mejoran comprensión material del caso y si su lectura puede mantenerse fiel al soporte de los bloques que los sostienen.

Todo artifact visible debe ir acompañado por `artifact_caption_block` o control semántico equivalente. El artifact no reemplaza al bloque ni crea un canal paralelo de verdad; amplifica comprensión cuando permanece dentro de los mismos límites que el resto del paquete.

## 8. Reglas mínimas de composición
El ensamblaje debe obedecer al menos estas reglas:
- **Cobertura mínima.** El paquete debe cubrir, cuando el caso lo demande, estado técnico, incertidumbre relevante, conflictos materiales, agenda de validación y lógica preliminar de prioridad o siguiente paso.
- **No teatralidad.** No se agregan piezas solo para que el paquete “se vea completo”.
- **No duplicación vacía.** El mismo contenido no debe repetirse salvo que cambie de función o de audiencia.
- **Balance.** No puede haber sobreexposición de oportunidad con subexposición de incertidumbre o conflicto si el caso sigue abierto.
- **Jerarquía semántica.** El orden debe obedecer comprensión, no persuasión.

Además, la composición puede usar contraste entre frentes, secuencias que muestren dependencia y agrupaciones que revelen trade-offs cuando eso mejore lectura sistémica.

## 9. Casos sparse y asimetría válida
Un `Report Package` válido puede ser corto, asimétrico, dominado por incertidumbre, con poca o ninguna oportunidad visible, con agenda de validación dominante y sin artifacts.

La validez del paquete no depende de simetría ni de apariencia de completitud. Un sparse case debe poder circular como lectura breve, honesta y útil, incluso cuando su principal valor sea clarificar incertidumbre y orientar validación.

## 10. Inclusión condicional y ley de compresibilidad por vista
Un bloque admitido no necesariamente entra en ambas vistas. La ley de compresibilidad queda fijada así: **si un bloque no puede compactarse sin perder límites críticos, no debe entrar en `executive_view`**.

La exclusión por vista no es pérdida de cobertura. Es una decisión legítima de fidelidad.

## 11. Secuencia lógica de lectura del paquete
Aunque aquí no se diseña UI ni layout final, sí debe existir una lógica mínima de lectura. La secuencia del paquete debe favorecer orientación del caso, estructura técnica, conflicto e incertidumbre, oportunidad candidata cuando aplique, agenda de validación y siguientes pasos.

Quedan bloqueados paquetes que abren con propuesta de acción o con artifact persuasivo antes de haber orientado la lectura.

## 12. Output formal de la subfase
La salida formal de 3B.2 es el **`view_assembly_manifest`**.

Este manifiesto determina qué bloques entran en qué vista, en qué orden, con qué grado de compresión, con qué artifacts asociados y bajo qué restricciones de circulación.

## 13. Errores típicos que esta subfase debe bloquear
- Tratar el paquete como texto monolítico redactado desde cero.
- Ensamblarlo desde fuentes externas al `output_block_register`.
- Usar vistas como motores paralelos de escritura.
- Diseñar primero la vista ejecutiva y luego colgarle la técnica.
- Tratar artifacts como persuasión visual y no como ayuda subordinada de comprensión.
- Forzar simetría y densidad en casos sparse.

## 14. Decisiones exactas que 3B.2 deja cerradas
- El `Report Package` es una composición gobernada e integradora.
- Su fuente exclusiva de ensamblaje es el `output_block_register`.
- `technical_view` es la vista base y `executive_view` deriva de ella.
- Los artifacts son subordinados y no autónomos.
- La composición puede ser sofisticada cuando mejora comprensión sistémica.
- Los casos sparse son válidos.
- La compresibilidad por vista gobierna inclusión o exclusión.
- La salida formal de la subfase es el `view_assembly_manifest`.

## 15. Criterio de terminado de la subfase
La subfase 3B.2 se considera cerrada cuando el ensamblaje del `Report Package` queda definido como operación disciplinada, integradora y no soberana; cuando la relación entre bloques, vistas y artifacts resulta inequívoca; y cuando la composición puede producir lectura holística del caso sin romper la ley madre de Fase 3.

# 3B.3 — Reglas de herencia epistemológica durante el rendering

## 1. Propósito exacto de la subfase
Definir cómo la ley madre de Fase 3 gobierna el rendering. Su función es fijar tres principios: toda salida visible hereda límites además de contenido; ninguna operación de rendering puede endurecer el caso; y, si un formato pierde soporte visible o desacopla restricciones críticas, la semántica debe degradarse.

## 2. Por qué esta subfase importa
Un output puede estar bien escrito, bien ordenado y visualmente claro, y aun así traicionar el caso si durante rendering perdió conflicto, incertidumbre, supuestos o dependencia de validación. Esta subfase importa porque el principal riesgo de Fase 3 no es solo inventar contenido, sino endurecer silenciosamente contenido real por cambio de formato.

## 3. Qué significa heredar límites además de contenido
Toda superficie interpretativa del paquete hereda límites además de contenido. La regla cubre bloques, vistas, artifacts, captions, títulos, headers, labels, tablas, orden de exposición y cualquier otra señal que oriente lectura.

La herencia incluye tanto lo que el material permite decir como lo que impide decir. Un output fiel conserva el contorno epistemológico que define la fuerza real de lo que materializa.

## 4. Regla de no aumento de fuerza epistemológica
Ninguna operación de rendering puede aumentar la fuerza epistemológica del material que procesa. Esto aplica a redacción, resumen, titulación, orden, visualización, compactación, reasignación de vista y ensamblaje.

Una hipótesis no se vuelve confirmación por estar mejor escrita. Un conflicto no se vuelve reconciliación por ser compactado. Una oportunidad candidata no se convierte en decisión por cambiar de posición o de vista.

## 5. Compactación con conservación de límite crítico
Compactar no significa suavizar. Toda compactación válida debe conservar condicionalidad, conflicto material, incertidumbre crítica, dependencia de validación y cualquier límite sin el cual el bloque cambiaría de significado.

Si un bloque no puede compactarse conservando esos límites críticos, esa compactación no es admisible.

## 6. Herencia por dependencia material
La herencia opera por dependencia material y no por cercanía textual. Un bloque hereda límites de todos los objetos upstream necesarios para sostenerlo, no solo del último objeto mencionado ni del fragmento más próximo.

Esto importa especialmente en bloques compuestos, summaries, opportunities y vistas que condensan varios bloques. La fragmentación documental no puede usarse para soltar límites incómodos.

## 7. Herencia de límites en vistas de audiencia
`technical_view` y `executive_view` heredan el mismo contorno epistemológico aunque no expongan el mismo volumen de texto. La vista ejecutiva puede reducir densidad, pero no puede reducir restricciones sustantivas del caso.

Menos texto no significa menos límites.

## 8. Herencia epistemológica en artifacts y captions
Artifacts y captions quedan sometidos a la misma regla general. Si no pueden hacer visible, o al menos no contradecir, conflicto, incertidumbre y dependencia de validación, no deben circular.

## 9. Prohibición de endurecimiento por omisión o reordenamiento
La omisión solo es válida si no altera interpretación sustantiva del caso. Del mismo modo, el reordenamiento no puede usarse para inducir más cierre del que el soporte permite.

## 10. Herencia en títulos, encabezados y labels
Títulos, encabezados, labels y captions no constituyen una excepción; forman parte de las superficies interpretativas ya cubiertas por la regla general. Muchas sobreafirmaciones nacen ahí y no en el cuerpo del texto.

## 11. Degradación semántica obligatoria
Si durante rendering o ensamblaje un bloque pierde soporte visible, cambia de vista, se compacta fuertemente o queda desacoplado de parte de sus restricciones, puede volverse obligatorio degradar su intensidad semántica.

La degradación no es un refinamiento estilístico opcional. Es un deber de fidelidad cuando el nuevo formato ya no soporta la formulación anterior.

## 12. Herencia como criterio de circulación
La herencia epistemológica no es una buena práctica editorial. Es un criterio de circulación. Si falla, la salida no debe publicar, no debe exportarse o debe reescribirse y degradarse antes de circular.

## 13. Errores típicos que esta subfase debe bloquear
- Suponer que rendering correcto equivale a fidelidad epistemológica.
- Heredar contenido pero no límites.
- Usar compactación, orden o señales de lectura para endurecer el caso.
- Tratar la vista ejecutiva como si pudiera exponer menos restricciones sustantivas.
- Pensar que la degradación es opcional cuando baja el soporte visible.

## 14. Decisiones exactas que 3B.3 deja cerradas
- Toda superficie interpretativa de Fase 3 hereda límites además de contenido.
- Ninguna operación de rendering puede endurecer el caso.
- La compactación exige conservación de límites críticos.
- La herencia opera por dependencia material.
- Las vistas heredan el mismo contorno epistemológico aunque difieran en densidad.
- Artifacts, captions, títulos y labels también quedan sometidos a la misma disciplina.
- La degradación semántica se vuelve obligatoria cuando el formato pierde soporte.
- Una falla de herencia es causa de no circulación.

## 15. Criterio de terminado de la subfase
La subfase 3B.3 se considera cerrada cuando la herencia epistemológica queda expresada de forma central, compacta y suficiente; cuando gobierna toda superficie interpretativa del paquete; y cuando la degradación obligatoria queda establecida como respuesta normal ante pérdida de soporte.

# 3C — Contrato de salida del MVP

## 1. Propósito exacto de la subfase
Definir el contrato formal de salida del MVP de Fase 3. Su trabajo es fijar qué outputs existen realmente, cuál es la función mínima de cada uno, qué relación estructural guardan entre sí y qué queda fuera del alcance actual.

## 2. Por qué esta subfase importa
Sin contrato de salida, Fase 3 termina en una noción vaga de “reporte”. Con contrato, termina en un conjunto pequeño, suficiente y epistemológicamente honesto de outputs gobernados.

## 3. Outputs formales autorizados del MVP
El MVP autoriza exactamente:
- `report_package`
- `output_block_register`
- `audience_view_register`
- `artifact_register`
- `machine_export_bundle`

Este set es suficiente. Todo output adicional en esta etapa sería proliferación prematura salvo necesidad futura explícitamente justificada.

## 4. Naturaleza y función de cada output
- `report_package`: salida documental principal para consumo humano.
- `output_block_register`: registro formal y auditable de bloques ya gobernados.
- `audience_view_register`: registro formal de `technical_view` y `executive_view`.
- `artifact_register`: registro subordinado de artifacts elegibles.
- `machine_export_bundle`: salida técnica mínima para trazabilidad, interoperabilidad y handoff estructurado.

## 5. Contenido mínimo de cada output
- `report_package`: al menos una vista válida, bloques trazables, secuencia disciplinada y límites heredados preservados.
- `output_block_register`: bloques seleccionados, mapeados, construidos, verificados y listos para ensamblaje o auditoría.
- `audience_view_register`: bloques incluidos por vista, orden de lectura, nivel de compresión, restricciones de circulación y artifacts permitidos cuando aplique.
- `artifact_register`: solo artifacts con soporte en bloques admitidos y con caption o control semántico equivalente.
- `machine_export_bundle`: estructura suficiente para reconstruir la relación entre paquete, vistas, bloques y artifacts.

## 6. Relación de dependencia entre outputs
- `output_block_register` precede y soporta todo lo demás.
- `audience_view_register` deriva de bloques ya admitidos.
- `artifact_register` depende de bloques y vistas.
- `report_package` compone vistas, bloques y artifacts elegibles.
- `machine_export_bundle` refleja estructuralmente esa relación.

Estas dependencias no son opcionales.

## 7. Outputs explícitamente fuera del MVP
Quedan fuera del MVP, como outputs autónomos:
- `regulatory_report`
- `financial_report`
- `investment_memo`
- `compliance_packet`
- `verification_report`
- `presentation_deck`
- `dashboard_runtime`
- `multi-stakeholder package`

Si alguno de esos contenidos aparece, debe vivir dentro del `report_package`, no como producto independiente.

## 8. Qué no promete el contrato de salida
Ninguna salida del MVP promete diagnóstico final, compliance final, ROI final, savings verification, recomendación terminal ni verificación empírica cerrada. `executive_view` no promete “resumen bonito de todo”, `artifact_register` no promete cobertura visual completa y `machine_export_bundle` no promete integración universal inmediata.

## 9. Casos sparse y asimetría válida
Un caso sparse puede producir legítimamente un `report_package` corto, una `executive_view` mínima, un `artifact_register` vacío y fuerte peso de validación. Eso no constituye falla del sistema.

## 10. Errores típicos que esta subfase debe bloquear
- Tratar “reporte” como único output totalizante.
- Crear outputs nuevos para cada necesidad documental marginal.
- Reducir `output_block_register` a residuo interno.
- Tratar `artifact_register` como canal autónomo de verdad.
- Exigir simetría entre casos y outputs.

## 11. Decisiones exactas que 3C deja cerradas
- El MVP autoriza exactamente cinco outputs formales.
- Cada output tiene función mínima y dependencia estructural definidas.
- El contrato de salida es pequeño, suficiente y honesto.
- Los outputs autónomos de tipo regulatorio, financiero, verificatorio o presentation-driven quedan fuera del MVP.
- Los casos sparse son configuraciones válidas del contrato.

## 12. Criterio de terminado de la subfase
La subfase 3C se considera cerrada cuando el final de Fase 3 deja de ser una idea vaga de “reporte” y queda fijado como un contrato breve, preciso y suficiente de outputs gobernados.

# 3D — Política de audiencia y compactación

## 1. Propósito exacto de la subfase
Definir cómo Fase 3 adapta la misma base material a dos audiencias distintas sin alterar conflicto, incertidumbre, supuestos relevantes, dependencia de validación ni fuerza semántica proporcional. Su función es cerrar qué diferencia formal existe entre `technical_view` y `executive_view`, qué puede compactarse y qué no, cuándo un material debe excluirse de la vista ejecutiva y qué límites de lenguaje y tono rigen cada vista.

## 2. Por qué esta subfase importa
Sin política de audiencia, la búsqueda de claridad tendería a comprar legibilidad al precio de pérdida epistemológica. Esta subfase importa porque Fase 3 no debe producir dos verdades, sino dos accesos distintos al mismo caso.

La compactación bien hecha no empobrece el caso; lo vuelve más legible sin romper su complejidad sustantiva.

## 3. Política mínima de audiencia del MVP
El MVP solo admite:
- `technical_view`
- `executive_view`

No existen todavía vistas separadas para regulatorio, financiero, inversionista, operaciones o auditoría externa. Esos frentes aparecen dentro de las dos vistas permitidas como capas temáticas.

## 4. Diferencia legítima entre technical_view y executive_view
La diferencia legítima entre vistas solo puede darse en densidad de exposición, volumen visible, granularidad de trazas, explicitación de dependencias y tolerancia al detalle técnico.

No pueden diferir en estatus epistemológico del caso, conflicto material, incertidumbre crítica, dependencia de validación, dirección semántica de los claims ni interpretación sustantiva.

## 5. Rol de technical_view
`technical_view` es la vista base de máxima explicitación permitida en el MVP. Su función es exponer con mayor densidad estructura del caso, tensiones, restricciones, dependencias entre bloques y agenda de validación.

Mayor explicitación no significa mayor verdad. Significa menor compresión.

## 6. Rol de executive_view
`executive_view` existe para reducir fricción de lectura, condensar frentes activos, mejorar ritmo documental y disminuir carga cognitiva.

No existe para suavizar el caso, esconder límites duros ni convertir el paquete en pieza de persuasión. Puede y debe hacer el documento más elegante y accesible, siempre que no cambie la interpretación sustantiva.

## 7. Reglas de compactación admisible
Compactar significa reducir volumen visible sin reducir restricciones sustantivas. Toda compactación válida debe preservar condicionalidad, conflicto material, incertidumbre crítica, dependencia de validación, bloqueos relevantes y función real del bloque.

Si un bloque no puede compactarse conservando sus límites críticos, esa compactación no es admisible.

La compactación válida mejora orientación, ritmo y legibilidad. No reescribe el caso.

## 8. Diferente compresibilidad por tipo de bloque
No todos los bloques son igualmente compresibles.

**Alta compresibilidad admisible**
- `executive_summary_block`
- partes de `technical_summary_block`
- `next_steps_block` cuando los pasos ya son acotados

**Compresibilidad media y condicionada**
- `opportunity_block`
- `validation_agenda_block`
- ciertas tablas simples de evidencia estabilizada

**Baja compresibilidad o compresibilidad riesgosa**
- `conflict_block`
- `uncertainty_block`
- captions con alta carga limitante
- tablas complejas cuyo resumen induciría sobrelectura

## 9. Regla de exclusión por incompresibilidad
Si un bloque no puede compactarse sin daño, debe quedar solo en `technical_view`, degradarse semánticamente o salir de `executive_view`.

Ningún bloque tiene derecho automático a presencia en la vista ejecutiva.

## 10. Límites de lenguaje y tono por vista
La vista ejecutiva no puede usar lenguaje terminal si el bloque base no lo soporta. La vista técnica tampoco puede inflar certeza por densidad o tecnicismo. Ambas vistas deben preferir gramática condicional cuando el caso lo exige.

También están sometidos a estas reglas títulos, encabezados, subtítulos, labels y captions.

Quedan bloqueadas formulaciones como:
- “el problema principal es...”
- “la mejor medida es...”
- “el sistema confirmó que...”
- “el sitio incumple...”
- “el ahorro esperado será...”

cuando el soporte siga siendo preliminar, conflictivo, condicional o dependiente de validación.

## 11. Adaptación legítima versus deformación
La adaptación legítima reduce fricción, mejora orden, compacta repetición y hace más elegante el acceso al caso, preservando complejidad sustantiva sin perder legibilidad. La deformación endurece lenguaje, borra límites, oculta conflicto o presenta madurez que el caso no tiene.

La regla es explícita: **la claridad es admisible; la simplificación que altera interpretación no lo es**.

## 12. Ejemplos normativos
- **Ejemplo 1 — Compactación correcta de summary técnico a ejecutivo**
- `Incorrecto:` “El sitio requiere intervención inmediata en HVAC.”
- `Correcto:` “La lectura actual prioriza HVAC/controls como frente principal de validación, bajo restricciones todavía visibles sobre lógica de control y operación real.”

- **Ejemplo 2 — Compactación incorrecta de conflicto**
- `Incorrecto:` “La electrificación es la vía preferida.”
- `Correcto:` “La electrificación permanece condicionada por conflicto entre oportunidad candidata, capacidad eléctrica no validada y restricciones operativas del sitio.”

- **Ejemplo 3 — Incompresibilidad legítima**
- Un `conflict_block` que depende de restricción de uptime, incertidumbre sobre capacidad eléctrica y ventana de retrofit no debe entrar en `executive_view` si la compactación elimina alguna de esas condiciones.

- **Ejemplo 4 — Título engañoso versus título proporcional**
- `Incorrecto:` “Main problem detected”
- `Correcto:` “Primary validation focus under current analytical structure”

- **Ejemplo 5 — Próximos pasos correctos**
- `Incorrecto:` “Implement VFDs across all motors.”
- `Correcto:` “Confirm drive applicability, operating profile stability and control feasibility before elevating variable-speed intervention beyond candidate status.”

## 13. Errores típicos que esta subfase debe bloquear
- Tratar `executive_view` como versión más simple y por eso más concluyente.
- Usar claridad como justificación para borrar conflicto o incertidumbre.
- Diseñar la vista ejecutiva para persuadir y la técnica para matizar después.
- Mantener en `executive_view` bloques cuya compresión elimina límites críticos.
- Confundir adaptación al lector con derecho a suavizar el caso.

## 14. Decisiones exactas que 3D deja cerradas
- El MVP solo admite `technical_view` y `executive_view`.
- La diferencia entre vistas es de densidad y compresión, no de verdad.
- `technical_view` es la vista base de máxima explicitación.
- `executive_view` existe para mejorar acceso y legibilidad sin alterar interpretación.
- La compresibilidad es diferencial por tipo de bloque.
- La exclusión por incompresibilidad es una decisión legítima de fidelidad.
- La claridad es admisible; la simplificación que altera lectura no lo es.

## 15. Criterio de terminado de la subfase
La subfase 3D se considera cerrada cuando la política de audiencia deja de sonar como restricción defensiva y pasa a operar como una disciplina de legibilidad: capaz de reducir fricción y mejorar el documento sin degradar la complejidad sustantiva del caso.

# 3E — Control epistemológico y circulación visible

## 1. Propósito exacto de la subfase
Fijar la barrera final de circulación de Fase 3 mediante una ley central breve y suficiente, capaz de decidir si una salida visible puede circular sin proliferación de microcontroles.

## 2. Por qué esta subfase importa
Fase 3 no necesita una burocracia de publicación. Necesita una barrera final clara contra circulación engañosa.

## 3. Regla madre de circulación
Opera aquí como barrera final la ley madre fijada en 3A: **ningún output visible de Fase 3 puede decir más de lo que soportan los objetos upstream de los que depende**.

## 4. Consecuencias operativas mínimas
De esa ley se desprenden exactamente tres consecuencias:
- **No inventar contenido.** Nada puede circular si no puede mapearse a objetos upstream trazables o a framing estructural admitido.
- **No ocultar límites materiales.** Nada puede circular si borra o diluye conflicto, incertidumbre, supuestos críticos o dependencia de validación todavía materiales.
- **No endurecer por presentación.** Nada puede circular si resumen, orden, compactación, visualización, caption o vista inducen una lectura más fuerte que la soportada por el caso.

## 5. Outcomes permitidos ante falla
Cuando una salida no puede circular como está, Fase 3 solo puede producir:
- `publish`
- `degrade`
- `reassign`
- `hold_for_validation`
- `block`

`publish` significa que la salida puede circular tal como está.

`degrade` significa que solo puede circular con menor fuerza semántica.

`reassign` significa que no debe circular en esa vista o forma y debe reubicarse.

`hold_for_validation` significa que no debe circular como hallazgo visible, pero debe permanecer vivo en agenda de validación.

`block` significa que no puede circular.

## 6. Sparse cases y publicación honesta
Un sparse case no es un fracaso del sistema. Puede producir una salida corta, asimétrica y dominada por incertidumbre o validación, y debe poder circular así si eso representa honestamente el caso.

Quedan bloqueadas completitud artificial, secciones de relleno, artifacts vacíos y summaries genéricos usados para disimular debilidad estructural.

## 7. Publicación engañosa y causas de no circulación
Publicación honesta hace visible el caso con la fuerza exacta que soporta, incluso si eso produce una salida incómoda, breve o frágil.

Publicación engañosa es toda salida que aparenta más cierre, más madurez o más claridad decisional de la que el soporte realmente permite, ya sea por omisión, compactación, orden, artifact, título o tono.

## 8. Ejemplos normativos
- **Ejemplo 1 — `degrade`**
- `Incorrecto:` “La mejor medida es electrificar el sistema térmico.”
- `Correcto tras degrade:` “La electrificación permanece como ruta candidata condicionada a validación de capacidad eléctrica, compatibilidad operativa y secuencia real de carga.”

- **Ejemplo 2 — `reassign`**
- Caso: un bloque técnicamente válido no puede entrar en `executive_view` sin perder límites críticos.
- `Correcto:` reubicarlo a `technical_view` y dejar en la vista ejecutiva solo una formulación breve que conserve el bloqueo real.

- **Ejemplo 3 — `hold_for_validation`**
- Caso: existe una hipótesis con valor analítico, pero todavía no soporta exposición como hallazgo visible.
- `Correcto:` moverla a agenda de validación o a dependencia crítica en lugar de presentarla como insight maduro.

- **Ejemplo 4 — `sparse case`**
- `Correcto:` paquete corto, con incertidumbre dominante, agenda de validación visible, poca oportunidad candidata y sin artifacts.
- `Incorrecto:` rellenarlo con summary genérico, subtítulos vacíos o tablas irrelevantes para que “se vea completo”.

## 9. Errores típicos que esta subfase debe bloquear
- Convertir el control final en una lista extensa de gates menores sin criterio central.
- Permitir circulación de contenido no trazable por “sentido general”.
- Usar omisión u orden para producir lectura más madura del caso.
- Tratar el sparse case como defecto a corregir con relleno.
- Mantener estados ambiguos en lugar de decidir entre los outcomes autorizados.

## 10. Decisiones exactas que 3E deja cerradas
- La circulación visible de Fase 3 queda gobernada por una sola regla madre.
- De esa regla derivan exactamente tres consecuencias operativas.
- Ante falla, solo existen cinco outcomes permitidos.
- El sparse case es una configuración legítima.
- La diferencia entre publicación honesta y publicación engañosa queda fijada como barrera final de circulación.

## 11. Criterio de terminado de la subfase
La subfase 3E se considera cerrada cuando el control final de circulación queda reducido a una ley inequívoca, un conjunto mínimo de consecuencias y outcomes no ambiguos, y una distinción clara entre publicación honesta y publicación engañosa.

# 3F — Criterio de terminado y handoff técnico

## 1. Propósito exacto de la subfase
Definir el criterio de terminado de Fase 3 y el punto exacto a partir del cual su diseño puede entregarse a implementación sin reinterpretación silenciosa. Su función es fijar qué queda congelado, qué puede variar técnicamente sin romper la fase, cuál es la prueba mínima de integridad del MVP, por qué esa prueba debe incluir un sparse case y qué queda explícitamente fuera del cierre actual.

## 2. Por qué esta subfase importa
Fase 3 no se cierra por volumen escrito ni por aspiración de completitud. Se cierra cuando su lógica documental ya no depende de que implementación termine de decidir qué significa la fase.

El cierre por suficiencia no es pobreza del sistema. Es una condición de implementabilidad seria. Garantiza que la capa técnica podrá construir el Reporting Engine sin reabrir su alcance epistemológico, su gramática material ni su contrato de outputs.

## 3. Qué debe quedar congelado al cerrar Fase 3
Al cerrar Fase 3, implementación no puede reinterpretar:
- el alcance epistemológico de la fase
- la prohibición de convertir Fase 3 en motor de inferencia, verificación, compliance final o recomendación terminal
- la definición de `Output Block`
- la definición de `Report Package`
- las dos vistas humanas del MVP
- el contrato mínimo de outputs del MVP
- y las tres leyes semánticas centrales ya consolidadas:
- no inventar contenido
- no ocultar límites materiales
- no endurecer por presentación

Estas decisiones son no negociables para implementación.

## 4. Qué puede variar en implementación sin romper la fase
Sí pueden variar:
- formatos de serialización
- persistencia
- estructura interna de registros
- layout final
- `PDF`, `DOCX` o `HTML`
- estilo visual
- paginación
- microformato tabular
- grado de automatización de renderers, exporters, validadores o ensambladores
- y riqueza visual efectiva del MVP

Ninguna de esas variaciones puede reabrir el contrato conceptual, alterar herencia epistemológica, borrar límites visibles, crear vistas no autorizadas ni sustituir estructura por improvisación libre.

## 5. Prueba mínima de integridad del MVP
Fase 3 solo puede declararse cerrada si puede sostener, al menos conceptualmente, un recorrido completo que incluya:
- objetos upstream admisibles
- selección y mapeo
- construcción de bloques
- `output_block_register`
- ensamblaje en `technical_view`
- derivación controlada de `executive_view`
- artifacts subordinados cuando apliquen
- `report_package`
- `machine_export_bundle`
- y aplicación de la regla de circulación visible

Esta prueba no exige implementación completa todavía. Exige coherencia estructural suficiente para que implementación ya no tenga que reinterpretar la fase para hacerla existir.

## 6. Prueba mínima con sparse case
Además del caso relativamente rico, la fase debe poder sostener una prueba mínima con un sparse case donde:
- el paquete sea corto
- la incertidumbre domine
- la agenda de validación pese más que la oportunidad
- existan pocos o ningún artifact
- y la salida siga siendo publicable sin relleno artificial

Esta segunda prueba no es opcional. Protege al MVP contra la falsa completitud.

## 7. Cierre por suficiencia y no por exhaustividad
Fase 3 se cierra por suficiencia del MVP, no por agotamiento de posibilidades. No se exige cobertura máxima de industrias, biblioteca exhaustiva de subtemas, librería visual amplia, vistas extra por stakeholder, formatos perfectos ni personalización avanzada.

Se exige solo lo suficiente para que el Reporting Engine tenga su lógica cerrada, pueda materializar un caso de forma seria y no dependa de reinterpretación posterior para existir. Ese cierre por suficiencia no reduce ambición; la vuelve implementable como disciplina de producto.

## 8. Qué queda explícitamente fuera del MVP
Queda explícitamente fuera del MVP, aunque sea deseable más adelante:
- nuevas vistas por stakeholder
- paquetes regulatorios autónomos
- memos financieros terminales
- compliance reporting final
- verification reports
- dashboards vivos
- presentaciones automáticas
- bibliotecas visuales extensas
- personalización por cliente o industria al nivel de producto final

Estas expansiones pertenecen al backlog futuro y no condicionan el cierre constitutivo de Fase 3.

## 9. Ejemplos normativos
- **Ejemplo 1 — Variación técnica admisible**
- `Correcto:` implementar primero export en `Markdown` o `HTML` simple y después `PDF`, sin cambiar el contrato conceptual del `Report Package`.
- `Incorrecto:` introducir una nueva vista `investor_view` en implementación porque “sería útil”, sin autorización documental previa.

- **Ejemplo 2 — Prueba mínima con caso relativamente rico**
- `Correcto:` caso con múltiples bloques, conflicto visible, oportunidad candidata, agenda de validación, `technical_view`, `executive_view`, uno o dos artifacts subordinados y export estructurado consistente.

- **Ejemplo 3 — Prueba mínima con sparse case**
- `Correcto:` caso corto, con incertidumbre dominante, agenda de validación visible, casi sin `opportunity`, sin artifacts y con publicación honesta.
- `Incorrecto:` completarlo con summary genérico, subtítulos vacíos y tablas irrelevantes para “demostrar robustez”.

- **Ejemplo 4 — Reapertura indebida en implementación**
- `Incorrecto:` cambiar `Output Block` por “sección editable libre” porque es más cómodo para el renderer.
- `Incorrecto:` dejar que la implementación use prompts abiertos para “mejorar” el tono del paquete sin respetar reglas de circulación ya cerradas.

## 10. Errores típicos que esta subfase debe bloquear
- Declarar cerrada la fase por volumen documental y no por cierre conceptual.
- Dejar a implementación decidir qué es un bloque, qué es una vista o qué puede circular.
- Reabrir leyes semánticas por comodidad del renderer.
- Aceptar prueba mínima solo con casos ricos y no con sparse cases.
- Exigir exhaustividad sectorial o visual como condición de cierre del MVP.

## 11. Decisiones exactas que 3F deja cerradas
- Fase 3 se considera cerrada cuando su núcleo epistemológico, material y contractual queda congelado para implementación.
- Existe una zona de variación técnica legítima que no rompe la fase.
- El MVP debe sostener una prueba mínima de recorrido completo.
- Esa prueba debe existir tanto para un caso relativamente rico como para un sparse case.
- El cierre por suficiencia constituye disciplina de producto, no renuncia.
- Las expansiones de producto futuro quedan explícitamente fuera del MVP.

## 12. Criterio de terminado de la subfase
La subfase 3F se considera cerrada cuando implementación ya puede tomar Fase 3 como contrato documental estable: suficientemente congelado para construirse, suficientemente compacto para ser gobernable y suficientemente potente para producir reportes serios sin reabrir su significado en la capa técnica.
