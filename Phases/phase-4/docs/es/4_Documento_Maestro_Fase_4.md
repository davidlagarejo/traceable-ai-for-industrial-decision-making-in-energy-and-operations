# 4A — Constitución del Verification Bridge

> Nota canonica de gobernanza: este documento pertenece a una linea de trabajo anterior del framework. El documento constitucional autoritativo para la arquitectura integrada de 8 fases es `Phases/phase-0/docs/en/0_Phase_0_Master_Document.md`. Si este documento entra en conflicto con Fase 0 en numeracion, autoridad de fase, claims permitidos, techos semanticos o logica de boundaries, Fase 0 gobierna hasta que esta fase sea reconstituida formalmente.

## 1. Objetivo
Definir la constitución operativa de Fase 4 como la capa del framework que gobierna el paso desde claims preliminares hacia rutas explícitas de endurecimiento de evidencia. Su función no es verificar por deseo ni producir cierre terminal, sino tomar claims, tensiones, oportunidades candidatas, incertidumbres y evidence gaps ya estructurados upstream y convertirlos en una arquitectura disciplinada donde cada claim relevante pueda quedar ligado a evidencia local requerida, baseline hardening, contraste u observación necesaria, medición cuando aplique, dependencias instrumentales y operativas, condiciones de upgrade y causas explícitas de hold, degrade o block.

## 2. Por qué importa
Sin Fase 4 el framework queda expuesto a dos fallas simétricas. La primera es subir claims por plausibilidad, benchmark o presión de cierre sin arquitectura real de endurecimiento. La segunda es dejar el caso atrapado en provisionalidad indefinida, con claims relevantes, tensiones dominantes y oportunidades candidatas visibles, pero sin una estructura explícita que diga qué falta, qué evidencia sí importa y bajo qué condiciones un claim podría elevar su estatus de forma legítima.

Fase 4 importa porque no duplica la policía epistemológica general ya cerrada en Fase 0; la vuelve operativa para el intento de upgrade. Fase 0 fijó la ley del estatus del claim. Fase 4 fija el mecanismo práctico para intentar endurecerlo sin fingir verificación donde todavía no existe. Su valor no es volver el sistema tímido, sino organizar una economía de endurecimiento: reordenar claims por valor de validación y costo epistemológico, convertir tensiones, fricciones operativas, triggers regulatorios y oportunidades candidatas en arquitectura explícita de evidencia, baseline y observabilidad, y preparar el paso hacia verificación de campo sin falsos cierres.

## 3. Qué es Fase 4 y qué no es
Fase 4 es el Verification Bridge del framework. Es la capa que toma el universo upstream ya estructurado y decide qué claims merecen una ruta explícita de endurecimiento, qué evidencia local importa para ellos, qué baseline debe endurecerse, qué observación o contraste debe ocurrir, qué medición aplica si aplica, qué dependencia de instrumentación, acceso u operación condiciona el upgrade, y qué causa obliga a mantener el claim en hold, degrade, block o do_not_upgrade dentro de un dominio de validez delimitado.

Fase 4 no es auditoría final, compliance certification, savings verification cerrada ni una pila soberana de medición. Tampoco existe para rehacer Fase 2 ni para extender Fase 3 con lenguaje verificatorio. Su trabajo empieza exactamente donde el caso ya fue estructurado y vuelto legible, pero todavía no fue endurecido mediante rutas materiales de soporte local.

## 4. Qué entra en Fase 4 y qué no entra
La regla de entrada de Fase 4 es estricta: entra únicamente aquello que puede tratarse como candidato legítimo a endurecimiento de claim dentro de una arquitectura explícita de upgrade. No entra toda hipótesis visible ni toda oportunidad candidata. Entra lo que, por relevancia material, valor de validación y capacidad de cambiar la lectura del caso, merece quedar sujeto a una ruta gobernada de endurecimiento.

### 4.1 Entra en Fase 4
Entran en Fase 4:
- selección y priorización de `claim_upgrade_candidate` a partir de claims, tensiones, oportunidades candidatas, incertidumbres y evidence gaps ya estructurados upstream;
- explicitación de evidencia local requerida por claim;
- definición de baseline hardening cuando el claim dependa de una línea base que todavía no soporta upgrade;
- identificación de contraste, observación, captura documental o medición requerida cuando corresponda;
- explicitación de dependencias instrumentales, operativas, temporales y de acceso;
- fijación de condiciones de upgrade y de causas de hold, degrade, block o do_not_upgrade;
- delimitación del dominio de validez dentro del cual el claim podría elevar su estatus.

Entra, por ejemplo, un claim técnico derivado de una tensión dominante en refrigeración cuando Fase 2 ya mostró insuficiencia de evidencia local y alto valor de validación. En ese caso, Fase 4 puede tratarlo como `claim_upgrade_candidate` relevante y ligarlo a evidencia local requerida como setpoints, cycles, alarms y operating logs, a necesidad de baseline hardening, a un stub de observación o medición, y a una regla explícita de do_not_upgrade hasta confirmar la arquitectura real de control. El bridge no afirma que el claim ya endureció; hace visible qué tendría que ocurrir para que pudiera endurecerse.

Entra también un claim regulatorio cuando Fase 1 y 2 sugieren presión normativa plausible pero todavía falta trigger field real. En ese caso Fase 4 no afirma que “aplica”. Convierte esa lectura en evidencia local requerida, condición de upgrade, dependencia de campo específica y bloqueo explícito de elevación hasta confirmar el trigger.

### 4.2 Queda fuera del MVP
Queda fuera del MVP:
- compliance final y cualquier forma de certificación regulatoria terminal;
- savings verification cerrada;
- arquitectura nacional plena de verificación;
- diseño exhaustivo de sensores, medidores o instrumentación;
- M&V full-stack;
- monitoreo vivo o dashboards verificatorios;
- despliegue operativo completo de campo;
- simulación integral o modelado verificatorio a escala de producto final;
- reportes terminales autónomos de verificación.

También queda fuera del MVP tratar toda hipótesis visible como si mereciera bridge. Una oportunidad genérica en iluminación, con baja relevancia material, alta incertidumbre y bajo impacto sobre la lectura del caso, no necesita necesariamente entrar en Fase 4. Puede quedar fuera de priorización de endurecimiento, permanecer como backlog de baja prioridad o no recibir bridge todavía. El Verification Bridge no existe para dignificar todas las intuiciones con el mismo peso metodológico.

## 5. Unidad central de Fase 4
La unidad central de Fase 4 es el **`claim_upgrade_candidate`**. Esa unidad gobierna la fase porque preserva continuidad con la arquitectura centrada en claims, mantiene explícita la pregunta rectora de Fase 4 —si un claim puede o no intentar elevar su estatus— y obliga a tratar el endurecimiento como una operación gobernada sobre el claim y no como una colección dispersa de tareas técnicas.

### 5.1 Por qué esta es la unidad correcta
`claim_upgrade_candidate` es la unidad correcta porque:
- preserva la continuidad con el framework, donde el claim es la unidad gobernante;
- evita volver soberana la medición demasiado pronto;
- soporta rutas distintas de endurecimiento sin colapsar la fase a una sola técnica;
- permite gobernar explícitamente el cambio de estatus del claim;
- y permite tratar con la misma disciplina tanto claims prometedores como claims que deben mantenerse en hold, degrade, block o do_not_upgrade.

Esto es decisivo porque Fase 4 no trabaja sobre “mediciones en abstracto” ni sobre “evidencias sueltas”. Trabaja sobre intentos delimitados de upgrade de claim. La medición puede ser una ruta; el baseline hardening puede ser otra; la confirmación documental de arquitectura de control puede ser otra; la validación de un trigger de campo regulatorio puede ser otra. El centro no es la técnica elegida. El centro es el claim que intenta endurecerse bajo condiciones explícitas.

### 5.2 Por qué no son mejores las otras opciones
Las unidades centradas en medición son demasiado estrechas: vuelven soberana una ruta que en muchos casos no es la primera ni la más pertinente. Las unidades centradas en evidencia requerida son demasiado pequeñas: capturan faltantes, pero no gobiernan por sí mismas el cambio de estatus del claim. Las unidades centradas en paquetes verificatorios o workstreams son demasiado grandes y demasiado tardías: mezclan varios claims, pierden granularidad y vuelven opaco qué claim exacto está intentando endurecerse y bajo qué dominio de validez.

`claim_upgrade_candidate` evita esos desvíos. Mantiene el foco en la pregunta correcta: qué claim concreto merece arquitectura de endurecimiento, qué soporte le falta y bajo qué condiciones podría o no podría intentar upgrade.

## 6. Ley madre de Fase 4
La ley madre de Fase 4 queda fijada así:

**Ningún claim puede elevar su estatus en Fase 4 por conveniencia narrativa, necesidad de cierre, benchmark, proxy, presentación documental ni plausibilidad sectorial; solo puede intentar upgrade si existe una ruta explícita, trazable y materialmente pertinente de endurecimiento que aumente su soporte dentro de un dominio de validez delimitado.**

Esta ley hace tres cosas a la vez. Primero, prohíbe la elevación por retórica o presión de cierre. Segundo, obliga a que todo intento de upgrade esté ligado a una ruta concreta de endurecimiento y no a un deseo de verificación. Tercero, deja claro que incluso un upgrade exitoso sigue siendo válido solo dentro de un dominio delimitado y no como licencia de extrapolación irrestricta.

Un anti-ejemplo basta para fijar el punto: tratar benchmark como si fuera validación local, llamar `measurement requirement` a una intuición no delimitada o decir que un claim “ya puede subir” sin baseline, sin variable objetivo y sin evidencia local requerida constituye mal diseño de Fase 4. Ahí no hay bridge; hay salto epistemológico no gobernado.

## 7. Relación con Fase 2
La relación con Fase 2 es de continuidad estricta, no de reemplazo. Fase 2 ya produjo el universo estructurado de inferencias, hipótesis, tensiones, conflictos, oportunidades candidatas, incertidumbres, evidence gaps, validation queue y next best questions. Fase 4 no rediagnostica ese universo ni lo vuelve a razonar desde cero. Lo toma como base para decidir qué claims merecen una ruta explícita de endurecimiento y cuáles no.

Esto significa que Fase 4 no duplica el Decision Core. Fase 2 respondió qué está estructuralmente vivo en el caso y dónde se concentran tensión, incertidumbre y oportunidad. Fase 4 responde cuáles de esos frentes justifican inversión metodológica en endurecimiento, qué soporte local importa realmente y qué condición bloquea o habilita un intento de upgrade.

El caso de refrigeración lo muestra con claridad. Si Fase 2 detecta una tensión dominante en refrigeración, con evidencia local insuficiente y alto valor de validación, Fase 4 puede elevar ese frente a `claim_upgrade_candidate` relevante. A partir de ahí, la arquitectura de endurecimiento puede exigir setpoints, cycles, alarms, operating logs, baseline hardening y confirmación de arquitectura de control antes de cualquier intento de upgrade. Fase 2 identificó la tensión. Fase 4 diseña la ruta explícita para endurecer el claim sin fingir que la tensión ya quedó verificada.

El caso opuesto también es constitutivo. Si Fase 2 deja visible una oportunidad genérica en iluminación con baja relevancia material, alta incertidumbre y bajo impacto sobre la lectura global, Fase 4 no está obligada a dignificarla como bridge candidate. Puede dejarla fuera de priorización de endurecimiento o mantenerla como backlog de baja prioridad. El Verification Bridge no existe para tratar todo lo visible como igualmente endurecible.

## 8. Relación con Fase 3
La relación con Fase 3 también es estricta. Fase 3 materializó contenido upstream admisible en salidas visibles gobernadas, pero sin cerrar verificación, sin certificar cumplimiento y sin transformar oportunidad candidata en decisión terminal. Fase 4 empieza donde Fase 3 termina: cuando el caso ya es legible, pero todavía no tiene rutas explícitas de endurecimiento.

Fase 4 no usa `report_package`, `artifact_register` o `audience_view_register` como sustitutos de soporte verificatorio. La representación visible puede ayudar a ver qué claims importan más, qué tensiones dominan y dónde la agenda de validación tiene mayor peso. Pero ningún caption, tabla o artifact puede elevar por sí mismo el estatus de un claim. El reporting hace visible el caso. El bridge hace visible qué falta para endurecerlo.

El ejemplo regulatorio vuelve a fijar la frontera. Si Fase 3 mostró presión regulatoria plausible, Fase 4 no hereda esa visibilidad como si ya fuera aplicabilidad confirmada. Convierte esa lectura en evidencia local requerida, trigger de campo, condición de upgrade y bloqueo explícito de elevación hasta confirmación específica. Reporting no verifica. Verification Bridge no confunde visibilidad con soporte.

## 9. Producto positivo de Fase 4
El producto positivo de Fase 4 no es una afirmación más bonita ni un claim más fuerte por redacción. Es una **arquitectura explícita de endurecimiento**.

Esa arquitectura hace visible, para cada `claim_upgrade_candidate`, qué evidencia local sí importa, qué baseline debe endurecerse, qué observación, contraste o medición aplica, qué dependencia instrumental u operativa condiciona el intento, qué dominio de validez limita el upgrade y qué causa obliga a mantener el claim en hold, degrade, block o do_not_upgrade. En términos industriales, eso significa convertir intuiciones sobre refrigeración, vapor, compressed air, BMS, power quality, electrificación o presión regulatoria en rutas gobernadas de soporte real y no en diagnósticos por inercia. También significa revelar la economía real de observabilidad del caso: dónde el sitio ya ofrece soporte suficiente, dónde la línea base sigue inestable y dónde el claim depende todavía de acceso, logging o boundary medible que el caso aún no tiene.

Ese es el aporte distintivo de Fase 4. No empobrece el framework; lo vuelve más fuerte donde el endurecimiento sí es pertinente. No existe para producir informes flacos ni para apagar ambición analítica. Existe para convertir ambición analítica en rutas legítimas de soporte, sin fingir cierre antes de tiempo.

## 10. MVP realista de Fase 4
El MVP realista de Fase 4 debe seguir siendo compacto. Debe ser suficiente para gobernar el intento de upgrade de claims relevantes sin colapsar en una infraestructura total de verificación.

Ese MVP mínimo debe poder sostener, al menos:
- selección disciplinada de `claim_upgrade_candidate`;
- explicitación de evidencia local requerida por claim;
- baseline hardening cuando corresponda;
- rutas mínimas de observación, contraste o medición cuando sean materialmente pertinentes;
- explicitación de dependencias instrumentales, operativas y de acceso;
- condiciones de upgrade y causas de hold, degrade, block o do_not_upgrade;
- y tratamiento honesto de sparse cases.

Esto implica que la medición no es soberana. Algunos claims se endurecerán por logs, triggers de campo, confirmación de arquitectura de control, evidencia documental local o contraste operativo. Otros requerirán medición acotada. Otros no deben entrar todavía en bridge. El MVP no necesita una ontología gigante de sensores ni un stack completo de M&V para ser constitutivamente válido.

El sparse case es decisivo para probar que el MVP está bien diseñado. Si el caso tiene pocos claims fuertes, muchos evidence gaps, poco material local e incertidumbre dominante, Fase 4 debe seguir siendo útil con menos `claim_upgrade_candidate`, más bloqueos, más hold y una arquitectura de endurecimiento más corta pero honesta. Si el bridge solo parece robusto cuando el caso ya viene casi endurecido, entonces no está bien constituido.

## 11. Qué sería sobre-ingeniería en 4A
Sería sobre-ingeniería en esta constitución:
- construir ontologías gigantes de sensores o instrumentación;
- introducir score decorativos de verificabilidad;
- colapsar Fase 4 a measurement design full-stack;
- intentar compliance final o verification reporting terminal dentro del MVP;
- diseñar despliegue operativo de campo a escala de producto final;
- abrir simulación nacional, monitoreo vivo o dashboards verificatorios;
- o convertir la fase en una capa exhaustiva de M&V antes de haber cerrado el bridge mínimo.

También sería sobre-ingeniería volver toda hipótesis visible un `claim_upgrade_candidate` por ansiedad metodológica. El MVP debe ser compacto precisamente para concentrar endurecimiento donde sí cambia la lectura del caso.

## 12. Errores típicos que 4A debe bloquear
- Tratar benchmark como si fuera validación local.
- Tratar proxy como si ya autorizara upgrade.
- Llamar `measurement requirement` a una intuición no delimitada.
- Permitir que un claim “suba” sin baseline, sin variable objetivo y sin evidencia local requerida.
- Volver soberana la medición y empobrecer otras rutas de endurecimiento.
- Duplicar Fase 0 en forma de advertencia general, sin convertirla en mecanismo práctico.
- Rehacer Fase 2 bajo lenguaje verificatorio.
- Usar `report_package` o artifacts como si fueran soporte suficiente para upgrade.
- Llevar al bridge hipótesis de baja materialidad solo por completitud o prestigio metodológico.
- Diseñar Fase 4 de forma tal que un sparse case solo pueda verse “robusto” mediante relleno o pseudo-rutas.

El anti-ejemplo de mal diseño es inequívoco: un sistema que toma una oportunidad plausible, la asocia a benchmark sectorial, inventa una “measurement requirement” no delimitada y concluye que el claim ya puede elevarse sin baseline endurecida, sin evidencia local requerida y sin dominio de validez. Eso no es Verification Bridge. Es un salto narrativo con vocabulario de medición.

## 13. Decisiones exactas que 4A deja cerradas
- Fase 4 queda definida como Verification Bridge y no como verificación terminal.
- Su función es gobernar el paso desde claims preliminares hacia rutas explícitas de endurecimiento.
- La unidad central correcta de Fase 4 es `claim_upgrade_candidate`.
- La medición queda reconocida como una ruta posible de endurecimiento, no como soberana de la fase.
- La ley madre de Fase 4 prohíbe todo upgrade por conveniencia narrativa, benchmark, proxy, plausibilidad sectorial o presión de cierre.
- Fase 4 no rehace Fase 2 ni extiende Fase 3 con lenguaje verificatorio.
- Su relación con Fase 2 es de continuidad sobre claims estructurados; su relación con Fase 3 es de continuidad sobre material ya vuelto legible, pero no verificado.
- El producto positivo de Fase 4 es una arquitectura explícita de endurecimiento y no un claim más fuerte por formulación.
- El MVP de Fase 4 debe permanecer compacto y no colapsar en M&V full-stack, compliance final ni despliegue nacional verificatorio.
- El sparse case es una configuración legítima del bridge y no una excepción defectuosa.

## 14. Criterio de terminado
La subfase 4A se considera cerrada cuando ya no queda ambigüedad sobre qué es Fase 4, qué no es, qué entra en el bridge, qué queda fuera del MVP, por qué `claim_upgrade_candidate` es su unidad central, cuál es su ley madre, cómo continúa a Fase 2 y Fase 3 sin duplicarlas, qué producto positivo aporta y qué constituye mal diseño.

En ese punto, la implementación futura ya no puede reinterpretar libremente Fase 4 como auditoría, reporting reforzado, measurement stack soberano o verificación terminal. Solo puede construirla como lo que aquí quedó cerrado: una arquitectura compacta, trazable y seria para intentar endurecer claims relevantes sin fingir soporte que todavía no existe.

# 4B — Selección y diseño de rutas de endurecimiento

## 1. Objetivo
Definir la operación central del Verification Bridge para el MVP: cómo se seleccionan los claims que sí merecen costo real de endurecimiento y cómo se diseñan sus rutas explícitas de evidencia, baseline, contraste, observación o medición. Su función es convertir un universo upstream ya estructurado en un conjunto gobernado de `claim_upgrade_candidate` y en pathways explícitos de endurecimiento, sin perseguir exhaustividad, sin colapsar a measurement design y sin introducir upgrade por deseo de cierre.

## 2. Por qué importa
La existencia de Fase 4 no se justifica por decir que “faltan datos”. Se justifica por saber distinguir entre lo que todavía es visible pero inmaduro y lo que ya merece inversión metodológica real de endurecimiento. Si 4B falla, el bridge se vuelve decorativo en cualquiera de dos formas: o persigue todo lo plausible y diluye foco, o se limita a producir listas vagas de faltantes sin claim, sin boundary y sin pathway.

4B importa porque aquí se vuelve operativa la capacidad nueva de Fase 4: organizar una economía de endurecimiento. Eso significa seleccionar qué claims sí merecen costo real de soporte, cuáles no deben consumir recursos del bridge y cómo convertir incertidumbre vaga en dependencias concretas de evidencia, baseline, observabilidad y bloqueo. Esa capacidad no agrega retórica; agrega estructura. Un sistema que solo pide “más datos” no tiene bridge. Un sistema que sabe decir qué claim importa, por qué importa, qué soporte local le falta, qué baseline necesita, qué variable debe observarse, contrastarse o medirse, qué dependencia instrumental existe y qué seguiría bloqueando el upgrade, sí lo tiene.

## 3. Qué toma Fase 4 como entrada operativa
La entrada operativa de 4B es estructurada, no narrativa. Nace de objetos upstream ya cerrados en Fase 2, principalmente:
- `hypothesis_register`
- `tension_map`
- `conflict_register`
- `opportunity_candidate_matrix`
- `uncertainty_register`
- `evidence_gap_register`
- `validation_queue`
- `next_best_questions`

También puede apoyarse en contexto estructurado heredado de Fase 1 cuando ese contexto sea necesario para delimitar claim, boundary, condición de referencia o dependencia de evidencia. Lo que no constituye intake operativo es el estilo documental de Fase 3, la sensación de importancia producida por un `report_package` o la fluidez de un `executive_view`. Fase 3 puede volver visible dónde parece concentrarse valor de validación, pero 4B no selecciona claims por impresión de lectura; selecciona desde registros estructurados y desde la gobernanza del claim ya cerrada upstream.

## 4. Qué entra a selección y qué queda fuera
Entran a selección los claims, tensiones, conflictos y oportunidades candidatas cuyo endurecimiento podría cambiar materialmente la lectura del caso, afectar priorización, viabilidad, juicio regulatorio o agenda de validación, y para los cuales existe una ruta plausible de endurecimiento que no dependa de magia analítica.

Quedan fuera:
- hipótesis de baja materialidad;
- oportunidades típicas del sector con impacto menor en la lectura global;
- frentes cuya única “ruta” sería benchmark, plausibilidad o intuición;
- claims cuya formulación todavía es demasiado vaga para delimitar boundary, evidencia requerida o dominio de validez;
- y cualquier candidato cuya persecución solo serviría para dar sensación de exhaustividad.

Esto implica una regla dura: Fase 4 no selecciona por completitud. Selecciona por relevancia material y por posibilidad realista de diseñar endurecimiento explícito.

## 5. Regla de elegibilidad para bridge
Un claim solo pasa elegibilidad hacia bridge si cumple simultáneamente cuatro condiciones:
- su endurecimiento puede cambiar de forma material la lectura del caso, la priorización, la viabilidad, el juicio regulatorio o la agenda de validación;
- el claim puede delimitarse con boundary suficientemente claro;
- existe una ruta plausible de endurecimiento basada en evidencia local, baseline, contraste, observación o medición;
- y el intento de upgrade no depende solo de benchmark, proxy, costumbre sectorial o deseo de cerrar el caso.

Esto excluye explícitamente la lógica de perseguir todo lo plausible. También excluye pathways abiertos por ansiedad metodológica. Si un claim no supera elegibilidad, el comportamiento correcto no es abrirle una ruta débil “por si acaso”, sino dejarlo fuera del bridge, degradarlo en prioridad o mantenerlo como backlog no priorizado.

En la práctica, esta elegibilidad suele concentrarse en cuatro familias de claims: claims de control o desempeño operativo, claims regulatorio-trigger, claims de oportunidad fuertemente dependientes de baseline y claims cuyo endurecimiento depende de infraestructura real de observabilidad. La utilidad de esta distinción no es ontológica; es operativa. Permite reconocer más rápido por qué ciertos frentes merecen costo metodológico y otros no.

## 6. Secuencia operativa de 4B
La operación central de 4B se organiza en cinco pasos no intercambiables: screening de claims candidatos, delimitación del claim y su boundary, diseño de evidencia requerida, diseño del pathway de endurecimiento y explicitación de dependencias y bloqueo. La secuencia importa porque evita diseñar rutas genéricas sobre claims todavía mal formulados o sin dominio de validez.

### 6.1 Screening de claims candidatos
El screening toma el universo estructurado upstream y pregunta qué claims merecen costo real de endurecimiento. No busca exhaustividad; busca concentración metodológica. En este paso se separan los frentes que solo son visibles o interesantes de aquellos cuyo upgrade podría cambiar materialmente el caso.

El screening correcto no pregunta “qué más podría revisarse”, sino “qué claim, si endurece o no endurece, cambia algo importante del caso”. Por eso una tensión dominante, un conflicto operativo central o un claim regulatorio de alta consecuencia pueden pasar elegibilidad, mientras que una oportunidad típica, de bajo impacto y alta incertidumbre, puede quedar fuera sin que el framework pierda fuerza.

### 6.2 Delimitación del claim y su boundary
Ningún pathway serio puede diseñarse sobre un claim mal delimitado. Una vez que un candidato pasa screening, 4B debe fijar qué afirma exactamente el claim, sobre qué sistema o condición afirma, en qué ventana temporal, bajo qué régimen operativo, con qué alcance espacial o funcional y dentro de qué dominio de validez podría endurecerse.

El boundary no puede ser excesivamente amplio. Un claim técnico sobre refrigeración no puede quedar formulado como “hay problema de refrigeración en el sitio” si lo que en realidad importa es una interacción concreta entre setpoints, secuencia de control y cycling de un subconjunto del sistema bajo ciertas condiciones operativas. Del mismo modo, un claim regulatorio no puede quedar formulado como “probablemente aplica la norma” si el verdadero boundary depende de trigger de jurisdicción, filing status, occupancy type o asset classification.

### 6.3 Diseño de evidencia requerida
Una vez delimitado el claim, 4B debe especificar qué evidencia local requerida importa realmente para intentar su upgrade. Aquí la regla no es pedir “más datos”, sino definir evidencia con función explícita.

La evidencia requerida puede incluir, según el caso:
- logs operativos;
- historian trends;
- control sequences;
- alarm histories;
- schedules reconstruidos;
- field documents;
- trigger fields regulatorios;
- observación de operación;
- medición puntual;
- o evidencia instrumental preexistente con resolución suficiente.

Cada pieza de evidencia requerida debe justificarse por su capacidad de endurecer, degradar o bloquear el claim. Si la evidencia pedida no cambia nada relevante sobre el estatus potencial del claim, entonces no es evidencia requerida; es ruido metodológico.

### 6.4 Diseño de pathway de endurecimiento
El pathway de endurecimiento es la secuencia explícita por la cual un `claim_upgrade_candidate` podría aumentar su soporte dentro de su boundary. No es una lista vaga de tareas. Es una ruta gobernada que conecta claim, evidencia requerida, baseline hardening cuando aplique, observación, contraste o medición pertinente, condición de upgrade y posibles causas de bloqueo.

En algunos claims el pathway será principalmente documental y operativo: revisión de logs, historian review, confirmación de secuencia de control, reconstrucción de schedule, verificación de trigger field. En otros incluirá contraste delimitado entre estados operativos o medición puntual. En otros requerirá logging corto o resolución temporal que hoy no existe. Lo central es que el pathway diga qué operación endurece qué parte del claim y bajo qué condición sigue sin autorizar upgrade.

### 6.5 Explicitación de dependencias y bloqueo
Todo pathway serio debe hacer visibles sus dependencias y sus posibles bloqueos. Entre ellas pueden estar ausencia de sensor, historian sin resolución útil, boundary mal definido, falta de acceso a control sequences, imposibilidad operativa de observar cierto régimen, ausencia de período de referencia estable, estacionalidad crítica, restricciones de uptime o retrofit window, dependencia de intervención operatoria no estable o trigger de campo todavía no confirmado.

Explicitar estas dependencias no debilita el bridge; lo vuelve real. Un claim puede merecer pathway y, aun así, quedar en hold o block por falta de soporte instrumental u operativo. Ese resultado no es fallo del framework. Es una salida positiva de diseño porque muestra exactamente qué impide el endurecimiento.

## 7. Qué es una ruta de endurecimiento
Una ruta de endurecimiento es una secuencia explícita, trazable y materialmente pertinente de operaciones de soporte local mediante la cual un `claim_upgrade_candidate` podría aumentar su nivel de respaldo dentro de un boundary delimitado. Debe indicar:
- qué claim intenta endurecer;
- qué evidencia local requiere;
- qué baseline debe endurecerse, si el claim depende de referencia;
- qué contraste, observación o medición aplica;
- qué dependencia instrumental u operativa condiciona la ruta;
- qué condición habilitaría upgrade;
- y qué causa seguiría obligando hold, degrade o block.

Una ruta de endurecimiento no es sinónimo de campaña de sensores. Tampoco es sinónimo de “pedir más datos”. Si no puede decir qué variable importa, qué evidencia local le falta, qué boundary gobierna la lectura y qué bloquearía el upgrade incluso después de observar algo, entonces todavía no es pathway.

Para el MVP conviene pensar los pathways en familias mínimas. Hay pathways principalmente documentales y de trigger, típicos de claims regulatorios o de arquitectura del activo. Hay pathways de operación y logs, típicos de secuencias de control, BMS, refrigeración o compressed air. Hay pathways de contraste delimitado entre modos, estados o ventanas operativas, frecuentes en vapor, district energy o power quality cuando la clave es comparar regímenes y no solo capturar una variable. Y hay pathways asistidos por medición cuando la variable crítica no es observable de otra manera o cuando la resolución temporal actual es insuficiente, como ocurre a veces en electrificación, balance térmico o límites de submetering. La diferencia importa porque no todos los claims piden el mismo tipo de endurecimiento ni cargan el mismo costo operativo.

## 8. Distinción mínima entre tipos de evidencia
Para el MVP, 4B debe distinguir al menos entre estos tipos mínimos de evidencia:

La **evidencia documental local** incluye configuraciones, secuencias, registros del activo, filing status, asset classification, planos, listas de equipos y documentación equivalente. Sirve para confirmar arquitectura, trigger, alcance o condición base del claim.

La **evidencia operativa temporal** incluye logs, historian trends, alarms, cycles, schedules, secuencias observables y series de operación. Sirve para endurecer comportamiento, persistencia, repetición o régimen operativo.

La **evidencia observacional de campo** incluye walk-through dirigido, observación de operación, confirmación de estado real, revisión contextual del control y verificación situacional delimitada. Sirve cuando el claim depende de una condición visible que aún no está bien capturada en registros.

La **evidencia de contraste** incluye comparaciones delimitadas entre estados, modos, períodos o condiciones de operación, siempre dentro de boundary explícito. Sirve para separar causalidad aparente de comportamiento realmente discriminante.

La **evidencia de medición** incluye medición puntual, logging corto o captura instrumental específica cuando el claim requiere variable no observable de otra manera o resolución que el sistema actual no tiene.

Esta distinción mínima no convierte a la medición en soberana. Solo impide tratar toda necesidad de endurecimiento como si fuera igual.

## 9. Baseline hardening como parte del pathway
Cuando un claim depende de referencia operativa o cuantitativa, baseline hardening no es opcional. Es parte constitutiva del pathway. No puede hablarse de upgrade serio si sigue borrosa la condición de referencia contra la cual el claim se lee.

Por eso 4B debe hacer visibles, como mínimo, estas preguntas:
- cuál es la condición de referencia relevante;
- qué período importa;
- qué variable dominante debe estabilizarse;
- qué ajuste puede ser material;
- y qué hace que el baseline actual siga siendo demasiado débil.

Un claim sobre ineficiencia de operación, desviación de control, sobreconsumo o ahorro candidato no puede endurecerse con integridad si la referencia de operación sigue inestable, mezclada con cambios de schedule, contaminada por modos distintos o apoyada en trazas demasiado pobres. Abrir un pathway sin baseline hardening cuando el claim depende de baseline es simular método.

No todos los baseline needs son iguales. A veces el problema es de período de referencia demasiado corto; a veces de mezcla de regímenes operativos; a veces de schedule inestable; a veces de variable dominante no aclarada; a veces de boundary energético mal cerrado; y a veces de fuerte dependencia de operador o ventana de producción. Hacer visible esa diferencia aumenta potencia industrial porque evita tratar con la misma receta un claim de compressed air, uno de power quality, uno de steam balance y uno de electrificación térmica.

## 10. Instrumentation gap no es detalle secundario
El instrumentation gap no es un detalle secundario ni una nota técnica menor. Es una salida valiosa de 4B. Si un claim no puede endurecerse todavía por falta de sensor, por historian insuficiente, por boundary no medible, por resolución temporal pobre o por ausencia de variable observable, el framework debe decirlo explícitamente.

Eso no significa que toda brecha instrumental obligue a desplegar hardware. Puede significar también que el claim todavía no merece costo metodológico, que primero debe endurecerse baseline, que basta con recuperar logs existentes o que la ruta correcta es observación y no medición. Un sistema de compressed air sin perfil de carga confiable, un BMS con tags presentes pero poco confiables y un frente de power quality sin event data suficiente no tienen el mismo gap aunque los tres bloqueen endurecimiento. Lo importante es que 4B no trate la falta de instrumentación como detalle implícito. Debe tratarla como condición positiva de diseño: algo que explica por qué el claim todavía no puede subir.

Para el MVP, estos gaps pueden pensarse al menos en cuatro formas: gap de acceso, cuando la información existe pero no está disponible; gap de observabilidad, cuando la variable crítica no se captura; gap de resolución o calidad temporal, cuando historian, tags o logs no soportan el pathway; y gap de boundary medible, cuando el activo o subsistema no puede aislarse con integridad suficiente. Esta jerarquía mínima vuelve más útil el bridge sin inflarlo.

## 11. Ejemplos normativos

### 11.1 Claim técnico que sí merece bridge
Caso: Fase 2 detecta una tensión dominante en refrigeración, con alta relevancia material y evidencia local insuficiente.

El tratamiento correcto en 4B es hacerlo pasar elegibilidad porque su endurecimiento puede cambiar materialmente la lectura del caso, afectar priorización y reordenar validación. Pero no debe pasar como claim amplio del tipo “hay problema de refrigeración”. Debe delimitarse, por ejemplo, hacia un claim más gobernable sobre lógica de control, cycling anómalo, setpoints inconsistentes o respuesta deficiente bajo un régimen operativo específico.

El boundary no puede ser demasiado amplio porque entonces el pathway se vuelve trivial y metodológicamente pobre. “Refrigeración del sitio” no es un boundary útil. Sí puede serlo, por ejemplo, un subconjunto de unidades, un loop concreto, una secuencia específica o una condición operativa recurrente dentro de una ventana temporal delimitada.

La evidencia operativa local requerida puede incluir:
- setpoints;
- cycles;
- alarms;
- control sequences;
- operating logs;
- historian trends;
- logging corto cuando falte resolución suficiente.

Baseline hardening entra si el claim depende de comparar comportamiento esperado versus comportamiento real, o si la desviación solo puede leerse contra una referencia operativa que hoy no está estable. El pathway puede combinar revisión de historian, reconstrucción de secuencia de control, observación de transición entre modos y, si hace falta, logging corto. Aun así, el claim no debe subir hasta confirmar arquitectura de control. Sin esa confirmación, cualquier mejora aparente de soporte seguiría dejando abierta una dependencia estructural demasiado fuerte.

El tratamiento incorrecto sería: “hay problema de refrigeración, medir temperaturas y confirmar”. Eso es metodológicamente pobre porque no fija claim, no delimita boundary, no distingue si importa control, cycling, setpoint, carga o schedule, no aclara qué variable endurece qué parte del claim y confunde medición con pathway.

### 11.2 Hipótesis que no merece bridge todavía
Caso: oportunidad genérica en iluminación, de baja relevancia material, alta incertidumbre y poco impacto sobre la lectura global del caso.

El comportamiento correcto es no llevarla a bridge. No pasa elegibilidad porque, aun si endureciera, cambiaría poco la lectura estructural del caso y consumiría costo metodológico desproporcionado frente a claims de mayor peso. Perseguirla en este punto sería decorativo.

Puede quedar como backlog de baja prioridad o fuera del bridge sin que eso debilite el framework. Al contrario: demuestra que el bridge sabe concentrar esfuerzo donde el endurecimiento importa de verdad.

El tratamiento incorrecto sería activar un pathway solo porque “iluminación suele ser oportunidad fácil”. Eso mezcla costumbre sectorial con relevancia real del caso y erosiona la regla de elegibilidad.

### 11.3 Claim regulatorio
Caso: Fase 1 y Fase 2 sugieren presión regulatoria plausible, pero falta trigger field real.

El tratamiento correcto es definir el claim como lectura preliminar condicionada, no como aplicabilidad confirmada. El boundary del claim debe quedar ligado a los campos que realmente gobiernan la posible aplicabilidad, por ejemplo:
- GFA;
- occupancy type;
- filing status;
- asset classification;
- field de jurisdicción o equivalentes.

La evidencia documental local requerida importa aquí más que una retórica general sobre “presión regulatoria”. La condición legítima de upgrade no es que “todo indique que aplica”, sino que el trigger relevante quede confirmado dentro del boundary correcto. Mientras falte ese trigger, el claim debe seguir bloqueado para elevación.

El tratamiento incorrecto sería: “todo indica que aplica”. Eso mezcla plausibilidad con aplicabilidad confirmada y convierte presión normativa preliminar en claim más fuerte de lo que el soporte permite.

### 11.4 Sparse case
Caso: pocos claims fuertes, muchos evidence gaps, incertidumbre dominante y poca observabilidad local.

El comportamiento correcto de 4B es seguir siendo útil con menos `claim_upgrade_candidate`, pathways más cortos, más evidence discovery, más hold y más block. En un sparse case, el valor del bridge no está en producir muchos pathways, sino en identificar con honestidad dónde sí vale la pena intentar endurecimiento y dónde todavía falta incluso la base mínima para diseñarlo bien.

Inflar el caso con múltiples pathways débiles para que “se vea completo” sería una mala práctica. Dejaría la impresión de capacidad verificatoria donde solo existe ruido metodológico. Un sparse case bien tratado puede producir pocos candidates, varios instrumentation gaps explícitos y varios bloqueos, y aun así ser un buen output de 4B.

## 12. Qué produce exactamente 4B
El output de 4B es estructurado. No son notas de trabajo ni sugerencias sueltas. Esta subfase debe producir, como mínimo, cuatro registros gobernables.

### 12.1 claim_upgrade_candidate_register
Contiene los claims que sí pasaron elegibilidad a bridge. Para cada uno debe quedar explícito, como mínimo, el claim seleccionado, su relevancia material, su boundary, su justificación de entrada al bridge y su condición preliminar de prioridad.

### 12.2 verification_pathway_register
Contiene el pathway explícito de endurecimiento para cada `claim_upgrade_candidate`. Debe mostrar qué tipo de ruta se diseñó, qué secuencia mínima sigue, qué condición de upgrade podría habilitarse y qué bloqueos o dependencias podrían impedirla.

### 12.3 required_site_evidence_register
Contiene la evidencia local requerida por claim. Su trabajo es impedir la vaguedad de “faltan datos” y convertirla en lista disciplinada de soporte local relevante, con función explícita dentro del pathway.

### 12.4 baseline_hardening_register
Contiene las necesidades de baseline hardening allí donde el claim depende de referencia operativa o cuantitativa. Debe dejar visible qué baseline importa, por qué el baseline actual no alcanza y qué tendría que endurecerse antes de intentar upgrade.

## 13. Qué sería sobre-ingeniería en 4B
Sería sobre-ingeniería en 4B:
- abrir pathways para todo lo visible;
- introducir score decorativos de elegibilidad o verificabilidad;
- construir una taxonomía gigante de sensores;
- diseñar campañas de hardware antes de delimitar claim y boundary;
- convertir toda brecha de observabilidad en proyecto instrumental pesado;
- intentar cerrar M&V completo dentro del MVP;
- o multiplicar tipos de pathway sin necesidad material.

También sería sobre-ingeniería diseñar registros tan complejos que la fase pierda legibilidad operativa antes de demostrar su núcleo: seleccionar bien y diseñar rutas explícitas.

## 14. Errores típicos que 4B debe bloquear
- Seleccionar por exhaustividad y no por relevancia material.
- Pedir “más datos” sin claim ni boundary definidos.
- Abrir measurement pathway sin aclarar qué variable importa, para qué función y para qué claim.
- Tratar benchmark como si endureciera un claim local.
- Activar baseline hardening sin decir qué baseline importa.
- Llevar claims de bajo impacto a rutas instrumentales pesadas.
- Usar Fase 3 como si su forma visible bastara para justificar eligibilidad o upgrade.
- Diseñar pathways que no dicen qué seguiría bloqueando el claim aun después de observar algo.

Estos errores deforman el bridge de maneras distintas, pero convergen en lo mismo: sustituyen arquitectura explícita de endurecimiento por movimiento metodológico aparente.

## 15. Decisiones exactas que 4B deja cerradas
- El intake de 4B es estructurado y nace del universo upstream ya cerrado en Fase 2, no de narrativa libre ni de impresión documental.
- Fase 4 no selecciona por exhaustividad; selecciona solo claims cuyo endurecimiento puede cambiar materialmente la lectura del caso y para los que existe ruta plausible de endurecimiento.
- La elegibilidad al bridge exige relevancia material, boundary delimitable y pathway plausible no dependiente de benchmark, proxy o deseo de cierre.
- La operación central de 4B queda fijada en cinco pasos: screening, delimitación del claim y su boundary, diseño de evidencia requerida, diseño del pathway y explicitación de dependencias y bloqueo.
- Una ruta de endurecimiento no es sinónimo de medición; puede incluir contraste documental, revisión de logs, historian review, observación de campo, reconstrucción de schedule, comparación delimitada o medición puntual.
- Baseline hardening es constitutivo del pathway cuando el claim depende de referencia operativa o cuantitativa.
- Instrumentation gap es una salida positiva de diseño y no un detalle menor.
- El output de 4B es estructurado y se materializa, como mínimo, en `claim_upgrade_candidate_register`, `verification_pathway_register`, `required_site_evidence_register` y `baseline_hardening_register`.

## 16. Criterio de terminado
La subfase 4B se considera cerrada cuando ya no queda ambigüedad sobre qué claims sí merecen costo real de endurecimiento, qué claims deben quedar fuera, qué significa pathway, qué significa evidencia requerida, cuándo baseline hardening es obligatorio, por qué instrumentation gap es una salida valiosa y qué registros estructurados mínimos debe producir el bridge.

En ese punto, la implementación futura ya no puede reinterpretar 4B como una lista genérica de pasos de auditoría, como measurement design indiscriminado ni como una fábrica de faltantes vagos. Solo puede construirla como lo que aquí quedó cerrado: el corazón operativo del Verification Bridge para seleccionar claims relevantes y diseñar rutas explícitas de endurecimiento sin teatro metodológico.

# 4C — Gobierno del cambio de estatus del claim

## 1. Objetivo
Definir cómo el framework gobierna el cambio o no cambio de estatus de un claim después de haber pasado por una ruta explícita de endurecimiento. Su función es convertir los pathways diseñados en 4B en consecuencias formales de estatus para cada `claim_upgrade_candidate`, impedir que mejoras parciales del soporte se conviertan en upgrade injustificado y evitar que todo quede en una ambigüedad técnicamente elegante pero metodológicamente indecidida.

## 2. Por qué importa
Sin 4C, Fase 4 podría diseñar pathways plausibles y aun así fracasar en su función principal. El fracaso aparecería de dos formas opuestas. La primera sería que cualquier ganancia parcial de soporte terminara inflando el claim por inercia narrativa. La segunda sería que, aun después del trabajo de endurecimiento, el sistema no pudiera decir con precisión si el claim avanzó, se debilitó, quedó pendiente, debe dejar de perseguirse o solo conserva el mismo estatus.

4C importa porque convierte rutas de endurecimiento en consecuencias explícitas de estatus. No agrega una teoría nueva del claim; ejecuta la gobernanza ya heredada sobre el momento decisivo del bridge: qué outcome corresponde después del intento de endurecimiento y qué techo semántico queda permitido a partir de ahí.

## 3. Qué gobierna exactamente 4C
4C gobierna la consecuencia de estatus que corresponde a un `claim_upgrade_candidate` una vez examinados su pathway, su evidencia local, su baseline, sus dependencias metodológicas, su boundary y su dominio de validez. No rediscute la gobernanza general del claim ya fijada en Fase 0, no rediseña pathways y no realiza verificación terminal. Su función es más acotada y más dura: decidir qué outcome corresponde y cuánto lenguaje soporta el claim después de ese intento de endurecimiento.

Eso implica gobernar la relación entre:
- claim;
- pathway ejecutado o parcialmente ejecutado;
- evidencia local obtenida o faltante;
- baseline endurecida o todavía débil;
- dependencias metodológicas resueltas o no resueltas;
- restricciones conservadas o perdidas;
- y valor material del claim para la lectura del caso.

## 4. Outcomes permitidos
Los outcomes permitidos de 4C son exactamente cinco:
- `maintain`
- `degrade`
- `hold`
- `block`
- `upgrade`

No existen outcomes adicionales, subestados ornamentales, escalas largas de madurez ni score continuos de verification readiness. El MVP necesita pocos outcomes, duros y útiles.

### 4.1 maintain
`maintain` significa que el claim conserva su estatus previo porque el trabajo de endurecimiento no aumentó materialmente su soporte, pero tampoco lo debilitó de manera suficiente como para exigir degradación. El claim sigue vivo en el caso y conserva su techo semántico previo. No avanza, pero tampoco retrocede.

### 4.2 degrade
`degrade` significa que el trabajo de endurecimiento reveló que el claim estaba formulado con más fuerza de la que su soporte permite. El claim no desaparece necesariamente, pero debe volver a una forma más débil, más condicionada o más estrecha en boundary y en lenguaje.

### 4.3 hold
`hold` significa que el claim sigue siendo material y merece permanecer vivo, pero el bridge no puede asignarle upgrade, degrade o maintain definitivo porque falta una dependencia metodológica decisiva. El claim no está cancelado; está suspendido en espera de una condición de endurecimiento todavía no resuelta.

### 4.4 block
`block` significa que el claim ya no debe seguir activo como candidato de endurecimiento en el bridge. Puede deberse a baja materialidad, costo metodológico desproporcionado, ruta injustificable, boundary ingobernable o ausencia de valor real para cambiar la lectura del caso. `block` protege recursos epistemológicos; no expresa frustración analítica.

### 4.5 upgrade
`upgrade` significa que el soporte del claim aumentó materialmente y de forma trazable, sin borrar restricciones críticas, de modo que el claim puede elevarse a una formulación más fuerte y todavía acotada. No significa verificación total, ni ahorro confirmado, ni compliance final, ni causalidad cerrada, ni recomendación terminal.

## 5. Regla general de no-upgrade por defecto
El sistema opera bajo una regla simple y dura: **no-upgrade por defecto**. Ningún claim sube salvo prueba suficientemente estructurada a favor. El bridge no premia esfuerzo metodológico con ascenso automático; exige una mejora material del soporte que sobreviva a boundary, baseline, dependencia metodológica y restricción crítica.

Si esa mejora no aparece, el claim no sube. Debe mantenerse, degradarse, quedar en hold o bloquearse según corresponda. El default no es ascenso; el default es contención.

## 6. Qué exige un upgrade legítimo
Un upgrade legítimo no se reconoce por tono técnico ni por mejora parcial de evidencia. Se reconoce por acumulación de condiciones duras que aumentan materialmente el soporte del claim sin borrar sus límites. El claim solo puede subir si se mantienen simultáneamente las condiciones constitutivas del bridge.

### 6.1 Claim delimitado
El claim debe estar formulado con precisión suficiente para saber qué intenta afirmarse y qué parte exacta del caso intenta endurecerse. Un claim amplio, ambivalente o narrativamente cómodo no puede subir con legitimidad porque no está claro qué ganó soporte realmente.

### 6.2 Boundary explícito
El boundary debe permanecer explícito y gobernable. El upgrade solo puede ocurrir dentro de un sistema, subsistema, período, régimen operativo o condición delimitada. Si la mejora del soporte solo existe dentro de un boundary estrecho, el outcome no autoriza extrapolación automática fuera de él.

### 6.3 Evidencia local material
Debe existir evidencia local material y no solo plausibilidad reforzada. Benchmark, proxy, costumbre sectorial, lenguaje técnico mejorado o consistencia narrativa no sustituyen evidencia local. El upgrade exige que el soporte nuevo afecte el claim desde el sitio, el activo, la operación o el trigger de campo pertinentes.

### 6.4 Dependencia metodológica visible
El claim no puede subir ocultando dependencias metodológicas. Si el pathway siguió dependiendo de una variable decisiva no observada, de una secuencia no confirmada, de una instrumentación insuficiente o de un trigger no verificado, el upgrade no es legítimo. Un claim solo puede subir si las dependencias críticas quedaron resueltas o explícitamente reducidas a un nivel compatible con el nuevo estatus.

### 6.5 Restricciones conservadas
El upgrade legítimo no borra restricciones críticas. Si la nueva formulación necesita esconder conflicto, perder condicionalidad, diluir incertidumbre o relajar límites operativos para sonar más fuerte, entonces no hay upgrade; hay endurecimiento por presentación.

### 6.6 Dominio de validez delimitado
El claim solo puede subir dentro de un dominio de validez delimitado. Incluso cuando el soporte mejora, el sistema no adquiere licencia para universalizarlo. El dominio de validez debe permanecer visible: bajo qué condiciones el claim sube, en qué alcance, con qué límites y sin qué extrapolaciones.

## 7. Diferencia entre upgrade legítimo y endurecimiento por presentación
Un upgrade legítimo cambia soporte. El endurecimiento por presentación solo cambia la forma visible del claim: el orden, la densidad técnica, la apariencia de coherencia o la comodidad con la que se lo narra.

Si el boundary sigue borroso, el baseline sigue débil o las restricciones críticas desaparecen para que el claim suene mejor, no hay upgrade. Hay presentación endurecida. Ninguna mejora formal del package, de la prosa o del framing técnico aumenta por sí misma el estatus del claim.

## 8. maintain, hold, degrade, block y upgrade no son sinónimos de confianza subjetiva
Los outcomes de 4C no representan estados psicológicos del analista ni impresiones blandas de confianza. No significan “suena bien”, “parece fuerte”, “me convence” o “todavía no me cierra”.

Cada outcome es una decisión estructural sobre la relación entre claim, pathway, evidencia local, baseline, boundary, dependencias metodológicas y valor material para el caso. Esa es la capacidad positiva de la subfase: convertir trabajo de endurecimiento en consecuencias comparables, trazables y semánticamente gobernadas. Operativamente, la lectura correcta sigue una secuencia corta: primero se decide si el claim aún merece recursos del bridge o debe salir de él; después si falta una dependencia crítica que impide cerrar su estado; y solo entonces si el soporte se mantuvo, cayó o subió. Tratar los outcomes como estados de ánimo metodológicos destruye la utilidad del bridge y lo reemplaza por una estética de juicio experto sin reglas duras.

## 9. Reglas de degrade
Corresponde `degrade` cuando el trabajo de endurecimiento revela que el claim estaba apoyado en supuestos demasiado fuertes, en baseline demasiado débil, en boundary demasiado amplio o en una lectura operativa menos estable de lo supuesto inicialmente.

`degrade` es correcto cuando:
- el soporte nuevo contradice parcialmente la intensidad anterior del claim;
- la referencia operativa se debilita;
- el claim solo sigue siendo sostenible en una formulación más estrecha o más condicional;
- o la información obtenida reduce el alcance legítimo del claim sin eliminarlo por completo.

`degrade` no equivale a desechar automáticamente el claim. Devuelve el claim a proporcionalidad. Es el outcome correcto cuando el bridge aprendió algo relevante que obliga a hablar con menos fuerza, pero no con silencio total.

## 10. Reglas de hold
Corresponde `hold` cuando el claim sigue siendo material y la ruta de endurecimiento sigue siendo pertinente, pero falta una dependencia metodológica decisiva para asignar un outcome más definitivo.

`hold` es correcto cuando:
- no hubo acceso al historian relevante;
- las alarms no pudieron exportarse;
- la secuencia real de control no pudo confirmarse;
- el trigger de campo sigue ausente;
- o una dependencia instrumental u operativa clave impide cerrar el intento de endurecimiento.

`hold` no es indecisión. Es gobierno correcto del estado cuando el claim sigue vivo, el pathway sigue justificado y el problema no es de valor material sino de dependencia todavía no resuelta.

## 11. Reglas de block
Corresponde `block` cuando el claim ya no debe seguir activo como objetivo de endurecimiento. El bridge debe bloquear cuando perseguir el claim no cambia materialmente el caso, cuando la ruta es metodológicamente desproporcionada, cuando el claim carece de boundary gobernable o cuando el pathway ya no tiene justificación real.

`block` es correcto cuando:
- el claim es de bajo impacto material;
- su endurecimiento no cambiaría priorización, viabilidad, juicio regulatorio ni agenda de validación;
- la ruta exigida sería costosa o pesada sin retorno epistemológico relevante;
- o el claim depende de supuestos tan débiles que no merece seguir consumiendo recursos del bridge.

`block` no debilita el framework. Protege recursos epistemológicos y evita completitud artificial.

## 12. Reglas de maintain
Corresponde `maintain` cuando el trabajo de endurecimiento deja al claim esencialmente donde estaba: sin ganancia material de soporte y sin pérdida material de proporcionalidad. El claim conserva su lugar, su relevancia y su formulación semántica previa.

`maintain` es correcto cuando:
- la revisión no encontró evidencia suficiente para upgrade;
- tampoco apareció evidencia suficientemente fuerte para degrade;
- el claim sigue siendo válido como lectura preliminar o condicionada;
- y no existe una dependencia crítica nueva que obligue a hold.

`maintain` no es una versión elegante de no decidir. Es el outcome correcto cuando la consecuencia metodológica real es continuidad proporcional.

## 13. Reglas de upgrade
Corresponde `upgrade` solo cuando el soporte del claim aumentó materialmente y sobrevive a todas las exigencias de la subfase:
- claim delimitado;
- boundary explícito;
- evidencia local material;
- dependencias metodológicas visibles y suficientemente resueltas;
- restricciones críticas conservadas;
- dominio de validez delimitado.

Además, `upgrade` solo es correcto si el claim puede volverse más fuerte sin transformarse en verificación terminal, ahorro confirmado, compliance final, causalidad cerrada o recomendación terminal. El outcome eleva el claim a una forma más fuerte y todavía acotada; no lo convierte en verdad irrestricta.

## 14. Do-not-upgrade flags
Los `do_not_upgrade_flags` son condiciones explícitas que prohíben upgrade aunque exista alguna mejora parcial del soporte. Su función es impedir que el sistema premie evidencia incompleta con un ascenso semántico que todavía no corresponde.

Entre los flags mínimos que 4C debe poder reconocer están:
- boundary no explícito;
- evidencia local decisiva aún faltante;
- baseline no endurecida cuando el claim depende de referencia;
- dependencia metodológica crítica no resuelta;
- instrumentation gap sobre variable decisiva;
- trigger field no confirmado;
- soporte solo testimonial;
- pérdida de restricción crítica en la nueva formulación;
- mejora de presentación sin mejora material del soporte.

Un `do_not_upgrade_flag` no decide por sí solo si el outcome final será `maintain`, `hold`, `degrade` o `block`, pero sí impide `upgrade`.

## 15. Relación entre outcome y lenguaje permitido
4C no solo decide estado interno. También fija el techo semántico permitido después del bridge. Cada outcome gobierna cuánto lenguaje soporta el claim y qué tipo de formulación ya no es admisible.

### 15.1 Si el outcome es maintain
Si el outcome es `maintain`, el lenguaje permitido conserva el techo previo del claim. Puede sostener la lectura provisional o condicionada que ya existía, pero no intensificarla. No puede sonar más fuerte solo porque hubo trabajo metodológico alrededor del claim.

### 15.2 Si el outcome es degrade
Si el outcome es `degrade`, el lenguaje debe bajar con él. Debe explicitar menor fuerza, mayor condicionalidad, boundary más estrecho o baseline más débil. Toda formulación que mantenga la intensidad anterior después de una degradación es semánticamente inadmisible.

### 15.3 Si el outcome es hold
Si el outcome es `hold`, el lenguaje puede mantener vivo el claim como frente material y como pathway pendiente, pero debe hacer visible la dependencia no resuelta. No puede sonar como hallazgo endurecido. Debe sonar como claim todavía suspendido en espera de soporte decisivo.

### 15.4 Si el outcome es block
Si el outcome es `block`, el lenguaje permitido ya no puede tratar el claim como frente activo de endurecimiento. Puede mencionarlo como claim bloqueado, no priorizado o metodológicamente no perseguido, pero no como lectura material aún en ascenso.

### 15.5 Si el outcome es upgrade
Si el outcome es `upgrade`, el lenguaje puede ser más fuerte, pero solo dentro del boundary y del dominio de validez explicitados. Debe conservar restricciones críticas y no puede deslizarse a lenguaje de verificación total, cumplimiento final, ahorro confirmado o decisión terminal.

## 16. Ejemplos normativos

### 16.1 Claim técnico que sí puede subir de forma acotada
Caso: Fase 2 detectó tensión dominante en refrigeración. 4B diseñó un pathway con alarms, control sequences, cycles e historian review. La evidencia local confirma comportamiento anómalo consistente con secuenciación deficiente en un subsistema delimitado.

El outcome correcto aquí puede ser `upgrade`, pero solo de forma acotada. No corresponde verificación terminal porque el soporte nuevo no autoriza afirmar ahorro confirmado, causalidad cerrada sobre todo el sistema HVAC ni extrapolación automática al sitio completo. Lo que sí autoriza es una lectura más fuerte sobre desempeño deficiente de control en el subsistema delimitado bajo condiciones operativas observadas.

Ese upgrade es legítimo porque:
- el claim quedó delimitado;
- el boundary es explícito;
- la evidencia local es material y no solo testimonial;
- la secuencia real fue suficientemente corroborada;
- y las restricciones se conservan visibles.

Una formulación incorrecta sería: `falla principal del sistema HVAC confirmada`. Esa frase viola boundary, extrapola fuera del dominio de validez y convierte soporte técnico local en cierre terminal.

Una formulación proporcional sería: una lectura más fuerte de desempeño deficiente de control en el subsistema delimitado, todavía condicionada y no extrapolable automáticamente al sistema HVAC completo. Eso expresa upgrade sin teatro.

### 16.2 Claim técnico que debe quedar en hold
Mismo caso técnico, pero ahora no hubo acceso al historian, solo existe testimonio operativo, las alarms no pudieron exportarse y la secuencia real no se confirmó suficientemente.

El outcome correcto es `hold`. No corresponde `upgrade` porque falta dependencia metodológica decisiva. Tampoco corresponde `block`, porque el claim sigue siendo material y el pathway sigue teniendo sentido. Y no corresponde `degrade` automáticamente, porque no apareció todavía evidencia que reduzca la proporcionalidad previa del claim; simplemente falta el soporte crítico para moverlo.

Aquí el claim sigue vivo. El `hold` no expresa indecisión del analista. Expresa una decisión dura: el claim no puede avanzar mientras historian, export de alarms o confirmación suficiente de secuencia real sigan ausentes. El bridge hizo su trabajo al convertir esa carencia en outcome explícito.

### 16.3 Hipótesis genérica que debe bloquearse
Caso: oportunidad genérica de iluminación, de bajo impacto material, con ruta de endurecimiento costosa o irrelevante y sin capacidad real de cambiar priorización del caso.

El outcome correcto es `block`. Seguir persiguiendo el claim solo porque es típico del sector sería una mala práctica. El bridge no existe para demostrar cobertura total; existe para concentrar recursos metodológicos donde el endurecimiento importa.

`block` no debilita el framework. Lo protege. Evita consumir esfuerzo en un claim cuyo eventual endurecimiento no alteraría materialmente la lectura del caso. El anti-ejemplo aquí es claro: seguir persiguiendo iluminación “porque suele ser una oportunidad fácil” desplaza foco desde claims más relevantes hacia completitud artificial.

### 16.4 Claim regulatorio que debe mantenerse o quedar en hold
Caso: presión regulatoria plausible, pero aún falta trigger field.

Aquí `upgrade` no corresponde. La aplicabilidad confirmada sigue fuera de alcance mientras falte el trigger relevante. Lo correcto puede ser `maintain` o `hold`, según la posición exacta del claim.

Corresponde `maintain` cuando la revisión conserva la lectura preliminar existente sin fortalecerla ni debilitarla. Por ejemplo, si GFA, occupancy type o asset classification siguen siendo compatibles con la presión regulatoria plausible ya identificada, pero todavía no aparece soporte nuevo suficiente para elevar el claim.

Corresponde `hold` cuando el pathway ya depende de un trigger específico todavía ausente o inaccesible, por ejemplo:
- GFA no confirmada;
- occupancy type no cerrada;
- filing status no disponible;
- asset classification ambigua;
- matching jurisdiccional todavía no confirmado.

En ambos casos se evita la deformación central: convertir plausibilidad regulatoria en aplicabilidad confirmada. `maintain` conserva la lectura preliminar. `hold` deja el claim vivo, pero suspendido por dependencia no resuelta. Ninguno autoriza `upgrade`.

### 16.5 Degradación legítima
Caso: una opportunity candidate parecía fuerte porque descansaba sobre un supuesto operativo; el trabajo de endurecimiento revela que el operating schedule real era mucho más variable o inestable y que el baseline asociado queda debilitado.

El outcome correcto es `degrade`. No corresponde desechar automáticamente el claim, porque puede seguir habiendo señal material. Pero sí corresponde devolverlo a proporcionalidad: menor fuerza, mayor condicionalidad, baseline explícitamente debilitada y menor capacidad para sostener priorización fuerte.

`degrade` es correcto precisamente porque distingue entre pérdida parcial de soporte y anulación total. Bloquearlo de inmediato sería excesivo. Mantenerlo igual sería inflacionario. Degradarlo devuelve el claim a una forma compatible con lo que ahora sí se sabe.

## 17. Qué produce exactamente 4C
4C produce outputs estructurados y gobernables. No produce impresiones técnicas vagas ni cierres retóricos.

### 17.1 claim_upgrade_decision_map
Contiene, para cada `claim_upgrade_candidate`, el outcome asignado, la base estructural de la decisión, el boundary relevante, el dominio de validez, las restricciones activas y el techo semántico permitido a partir del outcome.

### 17.2 do_not_upgrade_register
Contiene los `do_not_upgrade_flags` activos por claim y las razones estructurales por las que el upgrade queda explícitamente prohibido aunque haya habido alguna mejora parcial de soporte.

## 18. Qué sería sobre-ingeniería en 4C
Sería sobre-ingeniería en 4C:
- introducir escalas largas de confianza o madurez;
- crear subestados como `almost-upgrade`, `soft-hold` o equivalentes;
- diseñar score continuos de verification readiness;
- multiplicar outcomes para capturar matices que pueden resolverse con boundary, restricciones y lenguaje permitido;
- o convertir la subfase en psicología del analista en vez de gobierno de outcomes.

El MVP necesita pocos outcomes y consecuencias claras. Todo lo demás erosiona claridad decisional sin mejorar gobierno real.

## 19. Errores típicos que 4C debe bloquear
- Tratar cualquier mejora parcial de evidencia como justificación suficiente para `upgrade`.
- Usar mejor presentación, mejor orden o mejor narrativa como si aumentaran soporte.
- Tratar los outcomes como estados subjetivos de confianza.
- No distinguir `hold` de `block`.
- No distinguir `maintain` de `degrade`.
- Permitir que un claim suba sin preservar restricciones críticas.
- Endurecer lenguaje visible sin outcome formal correspondiente.

Cada uno de estos errores produce la misma deformación de fondo: confundir cambio de soporte con cambio de impresión. 4C existe precisamente para impedir esa sustitución.

## 20. Decisiones exactas que 4C deja cerradas
- 4C gobierna la consecuencia de estatus del claim después del intento de endurecimiento, no la gobernanza general del claim ni el diseño del pathway.
- Los únicos outcomes permitidos son `maintain`, `degrade`, `hold`, `block` y `upgrade`.
- El sistema opera bajo no-upgrade por defecto.
- `upgrade` requiere claim delimitado, boundary explícito, evidencia local material, dependencias metodológicas visibles y suficientemente resueltas, restricciones conservadas y dominio de validez delimitado.
- `upgrade` no significa verificación total, ahorro confirmado, compliance final, causalidad cerrada ni recomendación terminal.
- Los outcomes no son estados subjetivos ni score blandos.
- Cada outcome fija un techo semántico permitido para el claim.
- Los `do_not_upgrade_flags` son prohibiciones explícitas de upgrade ante carencias estructurales todavía activas.
- 4C produce como mínimo `claim_upgrade_decision_map` y `do_not_upgrade_register`.

## 21. Criterio de terminado
La subfase 4C se considera cerrada cuando ya no existe ambigüedad sobre qué outcome corresponde a un claim después del bridge, qué exige un upgrade legítimo, qué diferencia `maintain` de `hold`, qué diferencia `hold` de `block`, qué diferencia `degrade` de `maintain` y cómo cada outcome gobierna el lenguaje posterior permitido.

En ese punto, la implementación futura ya no puede reinterpretar 4C como una escala blanda de confianza ni como una capa elegante de opiniones técnicas. Solo puede construirla como lo que aquí quedó cerrado: la capa decisional del Verification Bridge para determinar, con disciplina y sin inflación semántica, qué claims avanzan, cuáles no y por qué.

# 4D — Contrato de salida del MVP

## 1. Objetivo
Definir el contrato de salida del Verification Bridge MVP como un conjunto pequeño, suficiente y gobernable de outputs estructurados. Su función es dejar sin ambigüedad qué sale realmente de Fase 4, cuál es la función mínima de cada output, cómo se relacionan entre sí y qué queda explícitamente fuera del contrato actual.

## 2. Por qué importa
Sin contrato de salida, Fase 4 corre dos riesgos simétricos. El primero es quedar metodológicamente atractiva pero operativamente difusa: claims endurecidos en teoría, sin objetos concretos que permitan construir, revisar y gobernar el bridge. El segundo es inflarse con pseudo-outputs redundantes que multiplican superficie sin cambiar ninguna decisión real.

4D importa porque cierra la traducción de candidate, pathway, baseline, instrumentation y outcome en objetos formales mínimos. Gracias a ellos el bridge no solo queda descrito; queda construible, auditable y capaz de mover decisiones de claim sin perder granularidad. El valor del MVP no se mide por cuántos outputs tiene, sino por si esos outputs cambian decisiones reales, sostienen rutas explícitas de endurecimiento o protegen una transición semántica real.

## 3. Qué debe producir Fase 4 y qué no
Fase 4 debe producir una cadena gobernada de registros estructurados que haga explícitos:
- qué claims fueron admitidos al bridge;
- qué pathway de endurecimiento corresponde a cada uno;
- qué evidencia local importa realmente;
- qué baseline debe endurecerse cuando aplica;
- qué gaps de instrumentación o observabilidad limitan el pathway;
- qué outcome final corresponde;
- y qué barreras hacen inadmisible el upgrade.

No debe producir reportes finales ni blobs agregados que mezclen candidate, pathway, evidence, baseline, instrumentation y decisión en un único objeto opaco. El contrato fija contenido mínimo exigible y dependencias de gobierno entre outputs, no diseño final de software, persistencia ni formatos de exportación.

## 4. Outputs formales autorizados del MVP
Los outputs formales autorizados del MVP son exactamente siete:
- `claim_upgrade_candidate_register`
- `verification_pathway_register`
- `required_site_evidence_register`
- `baseline_hardening_register`
- `instrumentation_gap_register`
- `claim_upgrade_decision_map`
- `do_not_upgrade_register`

No existen outputs adicionales dentro del contrato actual. No hay `verification summary`, `confidence pack`, `readiness note`, `verification package` agregado ni variantes por stakeholder.

## 5. Naturaleza y función mínima de cada output

### 5.1 claim_upgrade_candidate_register
Es el output maestro de la subfase y el ancla del contrato completo. Contiene los claims que sí fueron admitidos al Verification Bridge y sobre los cuales el sistema reconoce costo metodológico legítimo de endurecimiento. No es un output más entre varios; es el registro del que dependen pathway, evidencia, baseline, instrumentation y decisión.

### 5.2 verification_pathway_register
Contiene la ruta explícita de endurecimiento asociada a cada candidate. Su función es hacer visible cómo podría aumentar el soporte del claim y bajo qué lógica material: contraste documental, review de logs, historian review, observación de campo, confirmación de trigger, comparación delimitada o medición cuando corresponda.

### 5.3 required_site_evidence_register
Contiene la evidencia local requerida por claim. Su función es impedir que el bridge se diluya en fórmulas vagas del tipo “faltan más datos”. Aquí debe quedar visible qué evidencia del sitio sí importa para el claim y por qué esa evidencia tiene valor material para el pathway.

### 5.4 baseline_hardening_register
Contiene los trabajos de endurecimiento de baseline cuando el claim depende de una referencia operativa o cuantitativa todavía demasiado débil. Su función es separar con claridad el problema del claim del problema de la referencia sobre la que el claim pretende apoyarse.

### 5.5 instrumentation_gap_register
Contiene los gaps de sensor, historian, resolución temporal, acceso, observabilidad o boundary instrumental que limitan o bloquean el pathway. Su función no es decorar el caso con faltantes técnicos, sino dejar explícito cuándo el bridge no puede endurecer un claim porque la infraestructura de observación no soporta todavía ese intento.

### 5.6 claim_upgrade_decision_map
Contiene la consecuencia formal de estatus por claim después del trabajo de bridge. Su función es fijar el outcome correspondiente, el techo semántico permitido y la base estructural de la decisión. Es el punto donde el pathway deja de ser solo diseño y se convierte en consecuencia gobernada.

### 5.7 do_not_upgrade_register
Contiene los flags que prohíben upgrade aunque exista alguna mejora parcial de soporte. Su función es proteger la transición semántica del framework y evitar que evidencia incompleta, baseline débil, trigger ausente o dependencia crítica no resuelta se conviertan en ascenso narrativo.

## 6. Relación estructural entre outputs
La relación estructural del contrato no es opcional. `claim_upgrade_candidate_register` precede y sostiene a todos los demás outputs. Sin candidate admitido no existe pathway legítimo, ni evidencia requerida pertinente, ni baseline a endurecer, ni instrumentation gap relevante, ni decisión de outcome gobernable.

`verification_pathway_register` deriva del candidate y organiza la lógica material del endurecimiento. `required_site_evidence_register` y `baseline_hardening_register` dependen del pathway y no deben disolverse en notas genéricas. `instrumentation_gap_register` también depende del candidate y del pathway, pero su función es distinta: explicita límites de observabilidad que pueden bloquear, estrechar o condicionar el intento de endurecimiento.

`claim_upgrade_decision_map` depende de la lectura conjunta de candidate, pathway, evidencia local, baseline e instrumentation gap. `do_not_upgrade_register` depende de esa misma estructura, pero no duplica la decisión: protege contra upgrades inadmisibles y puede coexistir con outcomes como `maintain`, `hold`, `degrade` o `block`.

Por la misma razón, un `claim_upgrade_decision_map` sin candidate anclado, un `do_not_upgrade_register` sin claim identificable o un `instrumentation_gap_register` desligado del pathway no constituyen salidas válidas del bridge. El contrato no define solo objetos; define dependencias obligatorias entre ellos.

## 7. Contenido mínimo exigible de cada output
El contrato fija mínimos conceptuales exigibles. No fija todavía schemas técnicos exhaustivos ni diseño de base de datos.

### 7.1 Mínimos de claim_upgrade_candidate_register
Debe contener, como mínimo:
- claim identificable y trazable a su origen upstream;
- razón material por la que entra al bridge;
- boundary preliminar del claim;
- valor esperado del endurecimiento para la lectura del caso;
- y vínculo explícito con el frente técnico, regulatorio u operativo que justifica su admisión.

### 7.2 Mínimos de verification_pathway_register
Debe contener, como mínimo:
- claim al que responde;
- lógica explícita del pathway;
- tipo de endurecimiento requerido;
- dependencias metodológicas visibles;
- y condiciones de bloqueo relevantes.

### 7.3 Mínimos de required_site_evidence_register
Debe contener, como mínimo:
- claim y pathway a los que sirve;
- evidencia local requerida de forma concreta;
- razón por la que esa evidencia importa materialmente;
- locus operativo, documental o instrumental de obtención;
- y relación entre esa evidencia y el posible cambio de estatus del claim.

### 7.4 Mínimos de baseline_hardening_register
Debe contener, como mínimo:
- claim para el que el baseline importa;
- naturaleza de la referencia a endurecer;
- período, condición o régimen operativo relevante;
- variable dominante que debe estabilizarse o aclararse;
- y razón por la que el baseline actual no soporta todavía el claim.

### 7.5 Mínimos de instrumentation_gap_register
Debe contener, como mínimo:
- claim o pathway afectados;
- gap concreto de sensor, historian, resolución, acceso u observabilidad;
- explicación de por qué ese gap es material;
- y efecto del gap sobre el pathway: limitación, hold, block o prohibición de upgrade.

### 7.6 Mínimos de claim_upgrade_decision_map
Debe contener, como mínimo:
- claim evaluado;
- outcome asignado;
- base estructural de la decisión;
- boundary y dominio de validez pertinentes;
- restricciones activas conservadas;
- y techo semántico permitido a partir del outcome.

### 7.7 Mínimos de do_not_upgrade_register
Debe contener, como mínimo:
- claim afectado;
- flag o flags activos;
- razón estructural de cada prohibición;
- y condición faltante que tendría que resolverse para levantar la barrera de no-upgrade.

## 8. Regla de compacidad del contrato
Todo output del MVP de Fase 4 debe cumplir al menos una de estas tres funciones:
- cambiar una decisión real;
- sostener una ruta explícita de endurecimiento;
- o proteger una transición semántica real.

Si un output no hace alguna de esas tres cosas, no merece existir en el MVP. Esta regla de compacidad bloquea tanto la vaguedad como la proliferación. El bridge no necesita más objetos; necesita objetos que gobiernen consecuencias reales.

## 9. Sparse cases y asimetría válida
Un sparse case no debilita el contrato. Lo prueba. El contrato sigue siendo correcto aunque produzca:
- muy pocos entries en `claim_upgrade_candidate_register`;
- pocos pathways realmente justificables;
- mucha evidencia requerida concentrada en discovery básica;
- baseline hardening dominante;
- varios instrumentation gaps centrales;
- outcomes mayoritariamente `hold` o `block`;
- y un `do_not_upgrade_register` más cargado que el `claim_upgrade_decision_map` en upgrades.

No existe obligación de simetría entre outputs ni entre casos. Un caso rico puede poblar con densidad casi todo el contrato. Un sparse case puede dejar algunos registros muy delgados o incluso vacíos sin que eso constituya falla. Lo incorrecto sería inflarlo con contenido repetido o especulativo para que “se vea completo”.

## 10. Ejemplos normativos

### 10.1 Caso rico con varios candidates
Caso: un sistema industrial muestra tensiones materiales en refrigeración y secuenciación; existe presión regulatoria plausible; hay oportunidades candidatas en compressed air y power quality; parte del sitio tiene buena observabilidad.

La salida correcta aquí no es un único `verification package` agregado. Ese objeto borraría granularidad entre claims con distinto boundary, distinto pathway, distinta observabilidad y distinto outcome probable. El contrato correcto exige varios entries en `claim_upgrade_candidate_register`: por ejemplo, un candidate técnico de refrigeración, otro de secuenciación, uno regulatorio plausible y candidates separados para compressed air y power quality si realmente pasaron elegibilidad.

`verification_pathway_register` debe diferenciarlos. Refrigeración puede requerir historian review, control sequences, alarms y cycles; compressed air puede depender de leakage observation y profile logging; power quality puede requerir contraste delimitado sobre eventos o condiciones de carga; el frente regulatorio puede descansar sobre confirmación documental de trigger field y matching jurisdiccional. Mezclarlos en un pathway único degradaría gobernabilidad.

`required_site_evidence_register` también debe quedar separado por claim. Setpoints, alarms, control sequences y tendencias del historian no cumplen la misma función que GFA, occupancy type, filing status o asset classification. `baseline_hardening_register` aparecerá solo donde exista una referencia operativa o cuantitativa que endurecer. Puede ser central en compressed air o power quality y secundaria o irrelevante en el claim regulatorio. `instrumentation_gap_register` puede concentrarse en ciertos frentes y ser casi nulo en otros; eso es una virtud del contrato, no un defecto.

El `claim_upgrade_decision_map` puede terminar con outcomes mixtos: `upgrade` acotado para un subsistema de refrigeración bien observado, `hold` para compressed air si falta resolución temporal, `maintain` o `hold` en el claim regulatorio mientras no aparezca el trigger y `block` para algún candidate débil que no justifique más costo metodológico. `do_not_upgrade_register` debe existir para claims que siguen demasiado débiles aunque el caso, en conjunto, sea rico. Esa es justamente la razón por la que un blob agregado sería incorrecto: escondería que el bridge decide por claim y no por paquete.

### 10.2 Sparse case
Caso: pocos claims relevantes, evidencia local muy débil, historian inexistente e incertidumbre dominante.

El contrato sigue siendo correcto aunque produzca muy pocos entries en `claim_upgrade_candidate_register`, uno o dos pathways mínimos, evidencia requerida muy focalizada, baseline hardening dominante, instrumentation gaps centrales, varios `hold` o `block` en el `claim_upgrade_decision_map` y un `do_not_upgrade_register` claro y pesado.

Lo correcto aquí es que `required_site_evidence_register` sea más importante que cualquier ilusión de upgrade. El bridge puede decir que el primer trabajo real es confirmar schedule, arquitectura de control, presencia o ausencia de historian y variables mínimas observables. `baseline_hardening_register` puede llevar gran parte del peso si la referencia operativa del caso sigue siendo demasiado frágil. `instrumentation_gap_register` puede convertirse en la salida más informativa del caso sin que eso degrade el contrato.

Lo incorrecto sería generar múltiples outputs llenos de contenido repetido o especulativo para dar apariencia de completitud. Duplicar pathways sin evidencia, multiplicar candidates de bajo valor o disfrazar incertidumbre con texto ornamental degradaría la utilidad del bridge. Un sparse case honesto puede ser corto, asimétrico y metodológicamente fuerte.

### 10.3 Claim regulatorio
Caso: presión regulatoria plausible, trigger field aún no confirmado.

Este caso exige outputs diferenciados y no una nota agregada porque cada función del contrato resuelve una pregunta distinta. En `claim_upgrade_candidate_register` debe aparecer el claim regulatorio como candidate explícito si su endurecimiento puede cambiar juicio regulatorio o agenda de validación del caso. El candidate no afirma aplicabilidad; afirma relevancia material del frente.

En `verification_pathway_register`, el pathway correcto será principalmente documental y de confirmación de trigger: revisión de GFA, occupancy type, filing status, asset classification, matching jurisdiccional u otros equivalentes del caso. `required_site_evidence_register` debe listar exactamente esa evidencia local requerida. Ahí se ve por qué una nota agregada es insuficiente: el claim necesita evidencia precisa y no una sensación general de plausibilidad.

`baseline_hardening_register` puede ser irrelevante o claramente secundario aquí si el claim no depende de referencia operativa cuantitativa. `instrumentation_gap_register` también puede ser irrelevante o lateral si el cuello de botella es documental y no instrumental. Esa asimetría es correcta y el contrato debe soportarla. En `claim_upgrade_decision_map`, el outcome probablemente será `maintain` o `hold`, según si la revisión conserva la lectura preliminar o si ya depende de un trigger específico todavía ausente. Y en `do_not_upgrade_register` debe constar la barrera explícita: no puede haber `upgrade` mientras el trigger field no esté confirmado. Un único comentario tipo “todo indica que aplica” destruiría la gobernabilidad del caso.

## 11. Qué queda explícitamente fuera del contrato del MVP
Queda explícitamente fuera del contrato actual:
- `verification report` final;
- compliance packet;
- savings verification report;
- investment memo terminal;
- dashboard continuo;
- paquete multi-stakeholder;
- vistas separadas por audiencia;
- summary outputs ornamentales;
- bundles complejos de exportación;
- y cualquier pseudo-output creado solo para presentar mejor el bridge.

Ninguno de los siete outputs autorizados es un documento final para usuarios finales. Son objetos estructurados de gobierno del bridge, auditabilidad interna y construcción disciplinada del camino hacia endurecimiento real.

## 12. Qué sería sobre-ingeniería en 4D
Sería sobre-ingeniería en 4D:
- crear un output agregado que mezcle candidate, pathway, evidence, baseline, instrumentation y decision en un solo objeto;
- introducir outputs nuevos por ansiedad de completitud, como `verification summary`, `readiness note` o `confidence pack`;
- duplicar outputs por stakeholder demasiado pronto;
- exigir simetría entre caso rico y sparse case;
- convertir los outputs del bridge en pseudo-reportes finales;
- o deslizar la subfase hacia schemas exhaustivos, APIs o bundles de export antes de cerrar el contrato mínimo.

El MVP necesita un contrato pequeño, gobernable y suficiente. Todo lo demás es inflación ontológica o software adelantado a semántica todavía no necesaria.

## 13. Errores típicos que 4D debe bloquear
- Crear un solo output agregado que borre la diferencia entre candidate, pathway, evidencia, baseline, instrumentation y decisión. Ese error vuelve opaco qué cambió realmente y destruye granularidad de gobierno.
- Crear outputs nuevos por ansiedad de completitud. `Verification summary`, `readiness note` o equivalentes añaden superficie, no decisión.
- Duplicar outputs por stakeholder demasiado pronto. Esa proliferación transforma un bridge metodológico en una taxonomía de empaques.
- Exigir que un sparse case tenga la misma densidad de outputs que un caso rico. Esa exigencia produce relleno y especulación.
- Convertir outputs del bridge en pseudo-reportes finales. Eso borra la frontera con reporting terminal y con verificación fuerte posterior.
- Tratar `do_not_upgrade_register` como residuo decorativo. Si pierde fuerza, el contrato deja de proteger la transición semántica que 4C ya cerró.

Cada uno de estos errores degrada la gobernabilidad del framework al cambiar objetos con función real por objetos con función aparente.

## 14. Decisiones exactas que 4D deja cerradas
- Fase 4 termina el bridge del MVP en exactamente siete outputs formales.
- `claim_upgrade_candidate_register` es el output maestro del contrato y los demás dependen estructuralmente de él.
- `verification_pathway_register`, `required_site_evidence_register`, `baseline_hardening_register`, `instrumentation_gap_register`, `claim_upgrade_decision_map` y `do_not_upgrade_register` existen porque cumplen funciones distintas y no redundantes.
- El contrato fija contenido mínimo exigible, no implementación técnica detallada.
- Ningún output del contrato equivale a verification report final, compliance packet, dashboard continuo ni documento terminal para usuario final.
- Todo output del MVP debe cambiar una decisión real, sostener una ruta explícita de endurecimiento o proteger una transición semántica real.
- La asimetría entre casos ricos y sparse cases es válida y no exige compensación ornamental.
- El contrato existe para impedir tanto la vaguedad operativa como la proliferación ontológica.

## 15. Criterio de terminado
La subfase 4D se considera cerrada cuando ya no existe ambigüedad sobre qué sale de Fase 4 al terminar el Verification Bridge MVP, cuál es la función mínima de cada output, por qué `claim_upgrade_candidate_register` es el output maestro, cómo se relacionan los siete objetos entre sí, qué mínimos debe soportar cada uno y qué queda fuera del contrato actual.

En ese punto, la implementación futura ya no puede reinterpretar el bridge como un blob agregado, un pseudo-reporte final o una colección abierta de outputs opcionales. Solo puede construirlo como lo que aquí quedó cerrado: un contrato pequeño, suficiente y gobernable para materializar claims, pathways, evidencia requerida, baseline, instrumentation, decisiones de outcome y barreras explícitas de no-upgrade.

# 4E — Criterio de terminado y handoff

## 1. Objetivo
Definir el punto exacto en el que Fase 4 puede considerarse cerrada como MVP serio, construible y metodológicamente completo. Su función es fijar qué queda congelado para implementación, qué puede variar técnicamente sin romper la fase, cuál es la prueba mínima que debe poder sostener el Verification Bridge y cómo continúa el framework después del MVP bajo condiciones más exigentes, especialmente cuando el siguiente escalón ya requiere datos de campo reales.

## 2. Por qué importa
Sin una subfase de cierre, Fase 4 queda expuesta a dos errores opuestos. El primero es declararse terminada por volumen escrito, sofisticación conceptual o cantidad de objetos definidos, sin haber demostrado integridad operativa real. El segundo es no cerrarse nunca porque la visión verificatoria final del proyecto todavía no existe en el MVP.

4E importa porque resuelve esa tensión con una regla dura: Fase 4 se cierra cuando el Verification Bridge ya existe como contrato metodológico estable, compacto y construible. No necesita agotar la verificación fuerte futura para ser una fase completa. Sí necesita cerrar semántica, outputs, outcomes, relaciones estructurales y prueba mínima de funcionamiento honesto sobre más de un tipo de caso.

## 3. Qué debe quedar congelado al cerrar Fase 4
Al cerrar Fase 4 deben quedar congeladas, y por tanto fuera de reinterpretación silenciosa en implementación, las siguientes decisiones:
- que Fase 4 es una capa de endurecimiento epistemológico y no verificación total;
- que su unidad central es `claim_upgrade_candidate`;
- que no toda hipótesis merece bridge;
- que el bridge trabaja mediante pathways explícitos con claim, boundary, evidencia requerida, baseline need cuando aplica, instrumentation gap y condiciones de bloqueo;
- que los outcomes permitidos son exactamente `maintain`, `degrade`, `hold`, `block` y `upgrade`;
- que el sistema opera bajo no-upgrade por defecto;
- que `upgrade` exige aumento material de soporte local, boundary explícito, restricciones conservadas y dominio de validez delimitado;
- que el MVP termina en exactamente siete outputs formales y no en reportes finales;
- que `claim_upgrade_candidate_register` es el output maestro;
- y que los sparse cases son configuraciones válidas y necesarias del bridge.

También debe quedar congelada una tesis de continuidad: el MVP del bridge no equivale a verificación con datos de campo reales, pero sí define de forma irreversible el puente mínimo serio antes de entrar en ese terreno.

## 4. Qué puede variar en implementación sin romper la fase
Puede variar, sin romper Fase 4:
- el formato de serialización;
- la tecnología de persistencia;
- el paso desde tablas o registros simples hacia estructuras relacionales o de grafo;
- el orden interno de orquestación;
- la separación entre procesos síncronos, batch o checkpoints manuales;
- y el grado de automatización con el que se construyan y mantengan los siete outputs.

Lo que no puede variar es el significado metodológico de la fase. Implementación no puede redefinir candidate, pathway, baseline hardening, instrumentation gap, outcome ni do-not-upgrade. Tampoco puede colapsar varios outputs en notas libres, convertir outcomes distintos en un solo estado cómodo o reinterpretar `upgrade` como “casi verificado”. El cierre congela semántica; no obliga a una sola implementación.

## 5. Prueba mínima de integridad del MVP
Fase 4 solo puede declararse cerrada si puede sostener, al menos conceptualmente y de forma construible, un recorrido completo desde inputs estructurados upstream hasta los siete outputs formales del bridge. Esa prueba mínima debe mostrar que el framework puede:
- seleccionar claims elegibles al bridge;
- diseñar pathways explícitos;
- separar evidencia requerida, baseline hardening e instrumentation gaps;
- asignar outcomes formales;
- activar `do_not_upgrade_flags` cuando corresponda;
- y materializar todo ello en el contrato de salida sin perder granularidad por claim.

Esta prueba no exige todavía campañas reales de campo, historian integrado, medición ejecutada ni verificación fuerte. Exige algo distinto y previo: que el bridge ya pueda construirse sin ambigüedad y que su lógica soporte casos reales sin inflarse ni diluirse.

## 6. Prueba mínima con caso relativamente rico
La prueba con caso relativamente rico es obligatoria porque el bridge debe demostrar que puede gobernar complejidad sin colapsar en un objeto agregado. Debe existir al menos un caso donde convivan múltiples claims elegibles, pathways distintos, evidencia local heterogénea, baseline hardening selectivo, instrumentation gaps parciales y outcomes mixtos.

Un caso rico prueba que Fase 4 puede sostener varios frentes a la vez sin perder disciplina. También prueba que el contrato de salida no existe solo para casos delgados, sino para organizar complejidad real: claims técnicos con buena observabilidad, frentes regulatorios con trigger aún no confirmado, oportunidades candidatas que merecen bridge y otras que deben bloquearse o quedar en hold.

Sin esta prueba, el MVP podría parecer correcto solo porque nunca fue exigido a discriminar entre varios frentes materiales dentro del mismo caso.

## 7. Prueba mínima con sparse case
La prueba con sparse case es igualmente obligatoria. Un framework serio no puede validar su bridge solo sobre casos ricos. Debe demostrar que también puede comportarse de forma honesta y útil cuando predominan evidence gaps, observabilidad débil, historian inexistente, baseline frágil y pocos claims realmente endurecibles.

El sparse case prueba que Fase 4 no depende de completitud artificial para parecer robusta. Si el sistema solo luce bien cuando el caso ya trae observabilidad abundante y candidates densos, entonces el bridge no está bien cerrado. Debe poder producir pocos candidates, muchos holds o blocks, instrumentation gaps centrales y baseline hardening dominante sin rellenar el caso con pathways débiles o pseudo-salidas ornamentales.

## 8. Cierre por suficiencia y no por exhaustividad
Fase 4 se cierra por suficiencia, no por exhaustividad. Esto significa que el MVP no necesita agotar toda la visión verificatoria del framework para quedar metodológicamente completo. Necesita solo lo suficiente para que el Verification Bridge ya exista como capa seria de endurecimiento epistemológico, con unidad central, pathways explícitos, baseline hardening, instrumentation gaps, outcomes formales y contrato de salida gobernable.

No se exige, para cerrar la fase:
- verificación fuerte ejecutada con datos de campo;
- integración plena con historian o metering del sitio;
- compliance final;
- paquetes auditables para terceros;
- reproducción nacional estandarizada;
- engine verificatorio continuo;
- ni una capa institucional completa de entregables externos.

La suficiencia no empobrece el framework. Lo vuelve construible sin fingir que el puente ya es la verificación final.

## 9. Qué queda explícitamente fuera del MVP
Queda explícitamente fuera del MVP de Fase 4:
- campañas de campo ejecutadas de punta a punta;
- instrumentación completa desplegada;
- historian integration operativa como requisito constitutivo del cierre;
- logging real sostenido o submetering ejecutado;
- comparación pre/post verificatoria fuerte;
- savings verification report;
- compliance final;
- paquetes terminales de evidencia para terceros;
- verificación continua;
- y una capa verificatoria nacional o plenamente institucionalizada.

Todo eso puede formar parte del escalamiento posterior. Nada de eso es condición para declarar cerrada la fase como MVP serio.

## 10. Lo que sigue después del MVP
Lo que sigue después del MVP no es simplemente “más de lo mismo”. El siguiente escalón serio del framework entra en un terreno donde la arquitectura del bridge ya no basta por sí sola y comienza a ser indispensable la evidencia real del sitio. El puente mínimo del MVP organiza cómo un claim podría endurecerse; el escalamiento posterior exige empezar a materializar ese endurecimiento sobre observabilidad, datos y operación real. En términos de maduración, el claim pasa aquí de claim plausible a claim con pathway gobernado; el siguiente salto serio ya es un claim contrastado sobre datos de campo suficientes.

### 10.1 Escalamiento operacional
El escalamiento operacional introduce condiciones de observabilidad real que el MVP no necesita tener resueltas para cerrar, pero que sí son necesarias para subir a una verificación más fuerte. Esto incluye, según el caso:
- historian accesible;
- logging de variables relevantes;
- boundarys de medición más claros;
- campañas cortas o puntuales de captura;
- ventanas operativas útiles;
- acceso a operación real;
- lectura de secuencias efectivas de control;
- y, cuando haga falta, submetering o instrumentación adicional.

También introduce fricciones muy concretas de sitio: tags incompletos o mal nombrados, historian con profundidad insuficiente, export parcial por restricciones de tercero, ventanas de mantenimiento estrechas, restricciones de uptime, boundarys compartidos entre cargas y pérdida de contexto operacional sobre overrides o modos manuales. Este escalamiento resuelve un problema concreto: pasar de pathways plausibles y bien diseñados a pathways apoyados en observación real suficiente.

### 10.2 Escalamiento metodológico
El escalamiento metodológico endurece la forma en que el framework trata baseline, comparación, ajuste, incertidumbre y cuantificación. Aquí aparecen necesidades que el MVP no tiene que agotar:
- baseline más robustos;
- mejor delimitación temporal y operativa;
- ajustes más serios sobre variables dominantes;
- comparación pre/post más fuerte;
- pathways más cuantitativos;
- e incertidumbre más explícita y más trabajada.

Este escalamiento resuelve otro problema: no solo observar más, sino observar de modo que permita una inferencia más dura y cuantitativamente más defendible.

### 10.3 Escalamiento institucional y verificatorio
El escalamiento institucional y verificatorio convierte la arquitectura del bridge en paquetes más auditables, más externalizables y eventualmente más exigibles frente a terceros. Ese terreno puede incluir:
- evidence packages más robustos;
- entregables verificatorios utilizables por terceros;
- endurecimiento regulatorio;
- compliance más duro cuando aplique;
- y, más adelante, una capa verificatoria más continua, más reproducible o más estandarizada.

Ese bloque no pertenece al MVP porque exige algo que el MVP todavía no promete: evidencia de campo suficientemente fuerte, metodología más dura y, en muchos casos, mayor institucionalización del uso del output.

## 11. Qué necesita el siguiente escalón para existir de verdad
El siguiente escalón del framework no existe por voluntad arquitectónica. Existe solo cuando aparece evidencia real suficiente para poner a prueba el pathway sobre operación del sitio. Eso exige, según el claim y el caso:
- datos de campo reales;
- observabilidad local mejorada;
- variables dominantes efectivamente observadas;
- historian, logging o export operativo cuando el pathway lo requiera;
- triggers de campo confirmados;
- evidencia documental fuerte del sitio;
- ventanas operativas relevantes;
- baseline más robustos;
- acceso más estable a la operación;
- y, en muchos frentes, medición puntual, campaña corta o submetering delimitado.

Dicho de otro modo: después del MVP del Verification Bridge, el siguiente escalón serio ya no se consigue con más arquitectura solamente. Se consigue cuando la arquitectura diseñada puede encontrarse con evidencia de campo suficientemente fuerte como para endurecer aún más el claim, su baseline y su dominio de validez. En vapor y district energy eso suele exigir boundarys térmicos y de medición mejor cerrados; en compressed air, perfiles de carga y persistencia de fugas; en power quality, resolución y event data suficientes; en BMS y controls, secuencias efectivas, overrides y trends confiables. Ese escalamiento no reemplaza candidate, pathway, evidence, baseline, instrumentation y decision; los somete a un régimen más duro de observación, contraste y trazabilidad real.

## 12. Relación entre cierre de Fase 4 e implementación futura
El cierre de Fase 4 y el handoff a implementación no exigen que la siguiente etapa esté construida. Exigen que la semántica del bridge ya no pueda ser reinterpretada libremente. Implementación recibe una fase cerrada en sus unidades centrales, outcomes, outputs, relaciones estructurales y prueba mínima.

Eso permite dos cosas a la vez. Primero, construir el MVP sin reabrir candidate, pathway, baseline, instrumentation o decision. Segundo, preparar un punto de continuidad razonable hacia escalamiento posterior cuando haya acceso a datos de campo reales. El handoff correcto no congela una única solución de software; congela la semántica y deja espacio para una implementación capaz de crecer sin traicionar el bridge.

## 13. Ejemplos normativos

### 13.1 Variación técnica admisible
Una variación técnica admisible sería comenzar con registros simples serializados o tablas básicas para los siete outputs del bridge y, más adelante, migrar a una base relacional o a una estructura de grafo sin cambiar la semántica de candidate, pathway, baseline hardening, instrumentation gap, decision map o do-not-upgrade. También es admisible cambiar el orden interno de orquestación siempre que el resultado siga preservando los mismos objetos y relaciones estructurales.

Esto no rompe Fase 4 porque cambia implementación, no significado. El bridge sigue teniendo la misma unidad central, los mismos outcomes, el mismo contrato de salida y la misma disciplina de no-upgrade. La tecnología puede cambiar; la fase no.

### 13.2 Reapertura indebida en implementación
Sería una reapertura indebida:
- convertir `hold` y `block` en un único estado `pending` por comodidad de UI o simplicidad técnica;
- eliminar `do_not_upgrade_register` bajo la excusa de que “se puede inferir”;
- fusionar evidencia requerida, baseline hardening e instrumentation gap en notas libres;
- o reinterpretar `upgrade` como “prácticamente verificado”.

Cada uno de esos cambios rompe la fase aunque el software funcione. El problema no es tecnológico, sino semántico. Si implementación borra diferencias duras entre outcomes, outputs o barreras de upgrade, deja de construir el bridge que la fase cerró y empieza a construir otra cosa.

### 13.3 Prueba mínima con caso rico
Un caso relativamente rico puede incluir tensiones técnicas en refrigeración y secuenciación, presión regulatoria plausible, observabilidad razonable en parte del sitio y algunos frentes candidatos adicionales. La prueba mínima correcta no consiste en producir un demo bonito, sino en demostrar integridad estructural:
- varios claims pasan a `claim_upgrade_candidate_register`;
- cada uno obtiene pathway propio;
- la evidencia requerida se separa por claim;
- baseline hardening aparece solo donde realmente importa;
- instrumentation gaps son parciales, no uniformes;
- el `claim_upgrade_decision_map` termina con outcomes mixtos;
- y `do_not_upgrade_register` sigue vivo para claims que aún no pueden subir.

Si el caso rico no puede poblar coherentemente esos siete outputs sin mezclar frentes ni perder granularidad, Fase 4 no está cerrada de verdad.

### 13.4 Prueba mínima con sparse case
Un sparse case puede tener pocos claims elegibles, predominio de evidence gaps, historian inexistente, baseline débil y alta incertidumbre operativa. La prueba mínima correcta muestra justamente eso:
- pocos candidates legítimos;
- pathways cortos y honestos;
- evidencia requerida muy focalizada;
- baseline hardening más importante que la posibilidad inmediata de upgrade;
- instrumentation gaps centrales;
- varios `hold` o `block`;
- y un `do_not_upgrade_register` con peso real.

Esto no representa falla del sistema. Representa honestidad estructural. Si para pasar la prueba el sparse case tuviera que llenarse con claims blandos, pathways decorativos o pseudo-upgrades, entonces el bridge no sería confiable.

### 13.5 Escalamiento posterior hacia verificación con datos de campo
Supóngase un claim técnico sobre control o desempeño térmico cuyo pathway quedó bien definido en el MVP. El bridge ya pudo hacer varias cosas:
- delimitar el claim;
- fijar su boundary;
- listar evidencia requerida;
- explicitar baseline need;
- señalar instrumentation gaps;
- y quizás dejar el claim en `hold` o producir un `upgrade` acotado si el soporte local fue suficiente.

Pero existe un punto a partir del cual el bridge ya no puede avanzar solo con mejor arquitectura. Para endurecer más ese claim o entrar en una verificación más fuerte hacen falta:
- historian accesible;
- logging de operación real;
- submetering o medición puntual cuando corresponda;
- observación en ventanas operativas específicas;
- comparación contra un baseline más duro;
- y confirmación de variables dominantes bajo condiciones reales del sitio.

En muchos casos aparecerán además problemas de sitio que el MVP solo puede anticipar, no resolver: tags con mala calidad, export incompleto, equipos operando en manual, imposibilidad de aislar un subsistema durante producción, restricciones de uptime o falta de sincronización temporal entre fuentes. En compressed air eso puede implicar no distinguir carga útil de fugas persistentes; en steam balance, no cerrar suficientemente retornos o condensado; en power quality, no contar con waveform o event data en la ventana correcta. Ese ejemplo muestra la frontera correcta. El MVP puede diseñar y gobernar el puente. No puede reemplazar la evidencia de campo que la siguiente capa necesita para existir de verdad.

## 14. Qué sería sobre-ingeniería en 4E
Sería sobre-ingeniería en 4E:
- exigir una integración full-stack con historian, logging y campañas de campo antes de poder cerrar la fase;
- diseñar desde ahora la siguiente capa verificatoria completa;
- convertir la sección “lo que sigue” en una wishlist larga y sin jerarquía;
- exigir cumplimiento terminal, M&V pleno o verificación continua como condición del cierre actual;
- o congelar detalles técnicos de implementación que no hacen falta para proteger la semántica del bridge.

4E debe cerrar el MVP con disciplina. No debe forzarlo a resolver hoy lo que solo puede existir mañana con datos de campo reales, más observabilidad y mayor rigor cuantitativo.

## 15. Errores típicos que 4E debe bloquear
- Declarar cerrada la fase por volumen escrito y no por cierre conceptual y prueba mínima real.
- Exigir historian integration plena antes de poder cerrar 4E.
- Validar el bridge solo con casos ricos y no con sparse cases honestos.
- Convertir “lo que sigue” en una wishlist abierta sin condiciones claras de escalamiento.
- Dejar a implementación redefinir candidate, pathway, outcomes u outputs.
- Cerrar Fase 4 como si ya incluyera verificación de campo, compliance final o paquetes terminales.

Cada uno de estos errores distorsiona el handoff. O bien cierra demasiado pronto y deja la semántica abierta, o bien retrasa artificialmente el cierre al exigir capacidades que ya pertenecen al siguiente escalón verificatorio.

## 16. Decisiones exactas que 4E deja cerradas
- Fase 4 queda cerrada cuando el Verification Bridge ya existe como contrato metodológico estable, compacto y construible.
- El cierre congela semántica, no una única implementación técnica.
- La prueba mínima del MVP debe incluir un caso relativamente rico y un sparse case.
- El cierre es por suficiencia y no por exhaustividad.
- La siguiente capa seria del framework ya exige datos de campo reales, mayor observabilidad y baseline más robustos.
- Esa continuidad posterior no forma parte del MVP actual, pero sí queda explícitamente delimitada.
- Implementación no puede reabrir unidades centrales, outcomes, outputs, relaciones estructurales ni significado de upgrade.
- Fase 4 no se considera cerrada por volumen documental ni por aspiración futura, sino por integridad metodológica construible.

## 17. Criterio de terminado
La subfase 4E se considera cerrada cuando ya no existe ambigüedad sobre:
- qué queda congelado al cerrar Fase 4;
- qué puede variar técnicamente sin romperla;
- cuál es la prueba mínima de integridad del MVP;
- por qué esa prueba exige caso rico y sparse case;
- qué queda fuera del MVP;
- y cómo continúa el framework después, bajo condiciones más duras que ya requieren datos de campo reales.

En ese punto, Fase 4 puede entregarse a implementación sin reinterpretación silenciosa. Queda suficientemente congelada para construirse, suficientemente compacta para gobernarse y suficientemente honesta para dejar claro que el siguiente escalón serio ya no se consigue con más arquitectura solamente, sino con verificación apoyada en observabilidad y evidencia real del sitio.
