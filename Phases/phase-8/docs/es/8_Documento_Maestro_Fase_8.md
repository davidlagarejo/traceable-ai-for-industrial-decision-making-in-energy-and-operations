# 8_Documento_Maestro_Fase_8
## TAD como capa final de decisión y priorización

> Nota de espejo canónico: este documento es el reflejo en español de `Phases/phase-8/docs/en/8_Phase_8_Master_Document.md`. Debe mantenerse semánticamente alineado con ese documento. Si aparece una divergencia transitoria de traducción, la versión canónica en inglés gobierna hasta resincronización explícita.

## 1. Objetivo

Definir la Fase 8 como la capa final de admisibilidad de decisión y priorización del framework. Su función es convertir la postura actual de evidencia multi-fase en ordenamiento explícito de acciones, lógica de `defer / investigate / act`, lógica de no-go y, cuando el soporte realmente lo permita, afirmaciones finales de decisión acotadas.

## 2. Por qué importa

Todos los frameworks serios terminan enfrentando la misma pregunta práctica:

- qué debe hacerse primero,
- qué no debe hacerse todavía,
- qué requiere evidencia antes de comprometerse,
- y cuándo un caso es lo bastante fuerte para soportar peso real de decisión.

Sin Fase 8, el framework puede ser analíticamente rico pero operativamente indeciso. Con una Fase 8 mal diseñada, se convierte en un motor de recomendación que finge cierre que no se ganó.

La Fase 8 existe para resolver ambos problemas.

## 3. Qué es la Fase 8 y qué no es

La Fase 8 es:

- una capa de priorización,
- una capa de admisibilidad de decisión,
- una capa de secuenciación,
- y una capa final de acción acotada cuando existe soporte suficiente.

La Fase 8 no es:

- un motor de recomendación soberano,
- una capa de optimization theater,
- un reemplazo de la verificación,
- ni un mecanismo para forzar acción bajo evidencia débil.

## 4. Unidad epistemológica central

La unidad central de la Fase 8 es el **`decision_admissibility_case`**.

Esta es la unidad correcta porque cualquier postura seria de decisión debe permanecer atada a:

- una decisión objetivo o familia de acciones,
- la postura actual de evidencia,
- la carga de incertidumbre,
- downside e irreversibilidad,
- y blockers o requisitos de upgrade explícitos.

## 5. Problemas que resuelve la Fase 8

La Fase 8 existe para resolver:

- incapacidad para priorizar bajo incertidumbre;
- falsa decisividad a partir de evidencia incompleta;
- confusión entre validation priority e intervention priority;
- y falta de lógica explícita de no-go.

## 6. Inputs autorizados

La Fase 8 puede consumir:

- priors físicos y restricciones de Fase 1;
- estructura del twin y mapa de dependencias de Fase 2;
- regímenes operativos y restricciones de accionabilidad de Fase 3;
- postura de validación y verificación de Fase 4;
- rango financiero y riesgo de Fase 5;
- postura regulatoria de Fase 6;
- estado de creencias y registro de contradicción de Fase 7;
- objetivos de negocio, timing, irreversibilidad y apetito de riesgo.

## 7. Outputs autorizados

La Fase 8 está autorizada a producir:

- `priority_register`
- `validation_priority_register`
- `intervention_ordering_register`
- `decision_admissibility_register`
- `decision_burden_register`
- `no_go_register`
- `defer_investigate_act_map`

### 7.1 Objetos operativos requeridos

Para volver plenamente operable a TAD tanto en low-data como en casos endurecidos, se requieren los siguientes objetos operativos:

- `action_family_register`
- `decision_burden_record`
- `irreversibility_profile`
- `downside_profile`
- `sequencing_rule_set`
- `decision_rationale_record`
- `no_go_condition_register`

Cada `decision_admissibility_case` debe declarar como mínimo:

- familia de acción objetivo;
- alcance de acción;
- postura actual de soporte;
- clase de downside;
- clase de irreversibilidad;
- dependencia regulatoria;
- conjunto de blockers no resueltos;
- carga de evidencia requerida;
- y techo de publicación.

### 7.2 Familias canónicas de acción

La taxonomía mínima de familias de acción es:

- `inspect`
- `measure`
- `classify`
- `pilot`
- `design`
- `procure`
- `implement`
- `defer`
- `reject`
- `seek_regulatory_review`

La Fase 8 puede refinar esto después, pero no debe operar sin una taxonomía explícita de familias de acción.

### 7.3 Ladder de postura de decisión

El ladder mínimo de postura para TAD es:

| Estado | Significado |
| --- | --- |
| `validation_first` | el movimiento de mayor valor es reducir incertidumbre antes de comprometerse |
| `investigate_then_decide` | todavía hace falta trabajo de caso acotado adicional |
| `bounded_candidate_action` | una ruta de acción acotada es admisible, pero todavía no hay cierre final |
| `defer` | el timing o la postura de evidencia no justifican acción ahora |
| `no_go` | la ruta no debe avanzar bajo el caso actual |
| `final_admissible_decision` | la postura de acción se ganó lenguaje final acotado de decisión |

### 7.4 Regla de carga de evidencia e irreversibilidad

La lógica de carga por defecto es:

| Tipo de acción | Lógica mínima de carga |
| --- | --- |
| acciones diagnósticas reversibles | carga menor, si el downside es bajo y el alcance está acotado |
| pilots acotados o acciones pequeñas reversibles | carga moderada, con contención explícita de downside |
| compromisos de diseño o procurement | carga mayor, porque empieza a subir el lock-in |
| implementación o compromiso irreversible de capital | carga máxima, con mayor endurecimiento upstream requerido |
| acciones de revisión regulatoria | pueden subir temprano en prioridad cuando el downside de no actuar es alto |

## 8. Outputs prohibidos

La Fase 8 no puede producir:

- lenguaje final de decisión no soportado por fases upstream;
- supuestos ocultos de optimización;
- órdenes de implementación desconectadas de la postura de evidencia;
- ni claims de recomendación de alto peso que se salten los requisitos de endurecimiento.

### 8.1 Lógica explícita de no-go

La Fase 8 debe poder emitir `no_go` o `defer` cuando cualquiera de los siguientes siga materialmente vivo:

- lógica de acción físicamente incoherente;
- contradicción no resuelta con consecuencia seria aguas abajo;
- blocker regulatorio abierto que cambia la admisibilidad de acción;
- downside materialmente mayor de lo que la postura actual de evidencia puede justificar;
- o irreversibilidad materialmente mayor de lo que la postura actual de evidencia puede justificar.

## 9. Familias de claims permitidas

Las siguientes son admisibles:

- `preliminary_priority_claim`
- `validation_first_claim`
- `defer_claim`
- `no_go_claim`
- `bounded_action_candidate_claim`
- `final_admissible_decision_claim` solo cuando el soporte realmente lo permite

## 10. Familias de claims prohibidas

Las siguientes están prohibidas salvo que el soporte claramente las permita:

- `best_decision_claim`
- `implementation_must_claim`
- `final_capex_commitment_claim` bajo evidencia escasa
- `certainty_weighted_priority_claim` construido sobre confianza falsa

## 11. Modo low-data

En low-data, la Fase 8 sigue teniendo un rol serio.

Puede:

- priorizar qué validar primero;
- bloquear rutas de acción obviamente frágiles;
- identificar qué incertidumbre es más costosa de dejar sin resolver;
- y secuenciar diligence, medición o revisión de campo.

En este modo, la Fase 8 debe entenderse como **priorización consciente de incertidumbre**, no como cierre final de decisión.

### 11.1 Techo de acción en low-data

En low-data, la Fase 8 puede elevar legítimamente:

- `inspect`
- `measure`
- `classify`
- `seek_regulatory_review`
- `defer`
- y `no_go`

Debe ser muy reacia a elevar:

- `procure`
- `implement`
- o cualquier ruta de compromiso irreversible.

## 12. Modo local-evidence

Cuando la evidencia local empieza a endurecer el caso, la Fase 8 puede:

- separar con más confianza `investigate-first` de `act-first`;
- priorizar familias de intervención con alcance más claro y menor downside;
- y hacer downgrade o block de prioridades cuya lógica de soporte se debilita.

### 12.1 Lógica de secuenciación con evidencia local

En este modo, la Fase 8 puede empezar a separar:

- pilotos candidatos acotados frente a acciones que todavía requieren `validation_first`;
- pasos reversibles de diseño de compromisos irreversibles;
- y rutas de decisión que solo están retrasadas de rutas que ya son no-go activo.

## 13. Modo endurecido

Una postura final de decisión más fuerte solo se vuelve legítima cuando:

- los frentes técnicos upstream están suficientemente endurecidos;
- la exposición financiera está aceptablemente acotada;
- la postura regulatoria está suficientemente conocida;
- las contradicciones mayores están resueltas o explícitamente manejadas;
- y el downside residual es compatible con el tipo de decisión.

Incluso entonces, la admisibilidad de decisión sigue acotada al domain real de soporte.

### 13.1 La admisibilidad final sigue siendo condicional

Incluso en modo endurecido, `final_admissible_decision` sigue prohibido cuando:

- una contradicción material sigue sin resolverse y no está explícitamente gestionada;
- el cierre regulatorio sigue siendo decisivo y permanece abierto;
- el downside sigue siendo materialmente asimétrico respecto a la postura de evidencia;
- o la acción excede el alcance acotado del caso endurecido.

## 14. Relación con Decision-grade y Verification-grade

La Fase 8 es la expresión externa principal de `Decision-grade`. Convierte análisis en ordenamiento de acción.

La Fase 8 no crea `Verification-grade`. Lo consume donde existe y se niega a simularlo donde no.

## 15. Relación con las otras fases

**Con Fase 1**  
La Fase 8 depende de plausibilidad física para impedir malas acciones sobre lecturas imposibles o incoherentes.

**Con Fase 2**  
La Fase 8 depende de dependencia estructural para entender consecuencias a nivel sistema.

**Con Fase 3**  
La Fase 8 depende de realidad operativa para distinguir acciones técnicamente atractivas de acciones operativamente admisibles.

**Con Fase 4**  
La Fase 8 usa postura de validación y verificación para decidir si medir, pilotear, diferir o implementar.

**Con Fase 5**  
La Fase 8 usa rango financiero y downside para determinar si la incertidumbre es tolerable.

**Con Fase 6**  
La Fase 8 usa exposición regulatoria para subir urgencia, crear lógica de no-go o apretar el orden de acción.

**Con Fase 7**  
La Fase 7 determina cuándo las prioridades de TAD deben revisarse, degradarse o bloquearse.

## 16. TAD preliminar versus TAD más fuerte

TAD preliminar significa:

- ordenamiento bajo incertidumbre,
- priorización de validación,
- y secuenciación acotada de acciones.

TAD más fuerte significa:

- ordenamiento de intervención con mayor confianza,
- postura de go / no-go más fuerte,
- y en ciertos casos, soporte final de decisión acotado.

El framework nunca debe confundir lo primero con lo segundo.

## 17. Reglas de upgrade

La Fase 8 solo puede subir cuando:

- el soporte upstream se fortalece materialmente;
- el downside se estrecha materialmente;
- los blockers son removidos o acotados;
- y la postura de acción puede hacerse más fuerte sin sobreafirmar certeza.

### 17.1 Triggers canónicos de decisión

Los siguientes eventos son triggers canónicos de repriorización para la Fase 8:

- validación tiene éxito o falla;
- downside financiero se estrecha o se ensancha;
- blocker regulatorio se abre o se cierra;
- una contradicción se preserva, se divide o se resuelve;
- la irreversibilidad sube porque cambian procurement o timing;
- o una nueva familia de acción se vuelve factible dentro de un alcance acotado.

## 18. Reglas de downgrade, hold y block

`degrade` aplica cuando:

- una prioridad antes atractiva descansa sobre soporte que se debilita;
- el downside se ensancha;
- o blockers regulatorios / operativos se vuelven más serios.

`hold` aplica cuando:

- la acción sigue siendo potencialmente importante,
- pero una incertidumbre decisiva todavía impide una priorización o fuerza de decisión más fuerte.

`block` aplica cuando:

- la ruta es demasiado frágil;
- la evidencia es demasiado débil en relación con el downside;
- o la acción ya no merece espacio de decisión.

### 18.1 Reglas de secuenciación

La Fase 8 debe aplicar la siguiente lógica mínima de secuenciación:

- validation priority no es lo mismo que intervention priority;
- acciones reversibles de recolección de evidencia pueden avanzar antes que intervenciones más fuertes;
- acciones de revisión regulatoria pueden superar en prioridad a optimización técnica cuando el timing de exposición es material;
- y acciones irreversibles deben cargar una exigencia mayor que acciones diagnósticas reversibles.

## 19. Techo de lenguaje

El lenguaje preferido incluye:

- priorizar validación de
- no comprometer todavía
- acción candidata acotada
- la evidencia actual soporta secuenciación, no cierre
- no-go hasta
- diferir a la espera de

El lenguaje bloqueado incluye:

- la mejor decisión es
- implementar inmediatamente
- recomendación final
- elección óptima confirmada

## 20. Criterio de completitud

La Fase 8 se considera epistemológicamente cerrada cuando el framework puede:

- priorizar bajo incertidumbre sin fingir cierre;
- distinguir validation priority de intervention priority;
- exponer lógica de no-go honestamente;
- hacer upgrade y downgrade de postura de decisión cuando cambia la evidencia;
- aplicar carga proporcional a downside e irreversibilidad;
- y reservar lenguaje final de decisión para casos que realmente se lo ganan.
