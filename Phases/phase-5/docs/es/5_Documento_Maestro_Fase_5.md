# 5_Documento_Maestro_Fase_5
## Finanzas probabilísticas y riesgo

> Nota de espejo canónico: este documento es el reflejo en español de `Phases/phase-5/docs/en/5_Phase_5_Master_Document.md`. Debe mantenerse semánticamente alineado con ese documento. Si aparece una divergencia transitoria de traducción, la versión canónica en inglés gobierna hasta resincronización explícita.

## 1. Objetivo

Definir la Fase 5 como la capa que convierte la incertidumbre técnica, operativa, verificatoria y regulatoria en exposición financiera disciplinada, rangos económicos probabilísticos, estructura de escenarios y lógica de valor de la información, sin colapsar la incertidumbre en teatro determinista de ROI.

## 2. Por qué importa

Las decisiones industriales suelen enmarcarse financieramente antes de que el sistema físico esté suficientemente entendido. El modo de fallo habitual no es solo falta de números; es cierre falso mediante estimaciones de punto único, debilidad oculta de baseline, downside no valorizado y narrativas financieras que suenan invertibles antes de que el caso se haya ganado ese derecho.

La Fase 5 existe para mantener las finanzas útiles temprano sin dejar que las finanzas finjan estar cerradas temprano.

## 3. Qué es la Fase 5 y qué no es

La Fase 5 es:

- una capa de finanzas probabilísticas,
- una capa de traducción de riesgo,
- una capa de sensibilidad y escenarios,
- una capa de valor de la información,
- y una disciplina de exposición de capital.

La Fase 5 no es:

- una calculadora determinista de ROI,
- un memo de financiamiento por defecto,
- un motor de bancabilidad desde datos escasos,
- un sustituto del endurecimiento de baseline,
- un sustituto de la verificación,
- ni un dispositivo para forzar precisión cuando la evidencia es débil.

## 4. Unidad epistemológica central

La unidad central de la Fase 5 es el **`financial_exposure_case`**.

Esta es la unidad correcta porque el razonamiento financiero dentro del framework debe permanecer atado a:

- un frente técnico acotado,
- una postura de evidencia,
- un perfil de incertidumbre,
- una estructura de escenarios,
- y un uso decisional previsto.

El framework no debe emitir números económicos flotantes desconectados del linaje del claim.

## 5. Problemas que resuelve la Fase 5

La Fase 5 existe para resolver las siguientes fallas recurrentes:

- claims de payback de punto único construidos sobre supuestos técnicos no verificados;
- incapacidad para expresar downside si un claim prometedor luego se debilita;
- incapacidad para justificar por qué vale la pena pagar por validación adicional;
- incapacidad para separar economía de filtrado de economías más cercanas a cierre;
- e incapacidad para conectar la incertidumbre directamente con el riesgo de capital.

## 6. Inputs autorizados

La Fase 5 solo puede consumir objetos upstream gobernados y contexto de negocio acotado, incluyendo:

- priors físicos y rangos paramétricos de Fase 1;
- estructura de twin-state de Fase 2 cuando sea relevante;
- régimen operativo y restricciones de accionabilidad de Fase 3;
- información de baseline, medición y ruta de verificación de Fase 4;
- tarifas, bandas tarifarias y estructura de costo energético;
- librerías CAPEX, análogos de costo o estimaciones locales de costo;
- supuestos de mantenimiento y costo operativo;
- restricciones de financiamiento, hurdle rates, normas de payback y timing;
- apetito de riesgo, irreversibilidad y restricciones de presupuesto.

## 7. Outputs autorizados

La Fase 5 está autorizada a producir:

- `financial_range_register`
- `risk_exposure_map`
- `scenario_band_set`
- `sensitivity_register`
- `downside_upside_profile`
- `information_value_register`
- `decision_finance_posture`

Estos outputs son útiles incluso antes de la verificación completa, pero siguen acotados por el grado de evidencia.

### 7.1 Objetos operativos requeridos

Para mantener la Fase 5 operable tanto en low-data como en modo endurecido, deben existir los siguientes objetos operativos siempre que se abra un `financial_exposure_case` serio:

- `financial_assumption_register`
- `tariff_basis_record`
- `cost_basis_record`
- `benefit_driver_register`
- `range_provenance_record`
- `finance_readiness_state_register`

Cada `financial_exposure_case` debe declarar como mínimo:

- frente de decisión o acción objetivo;
- boundary de activo y subsistema;
- estado de dependencia de baseline;
- estado de base tarifaria;
- estado de base de costos;
- familia de impulsores de beneficio;
- base del horizonte temporal;
- regla de base de descuento;
- estado de dependencia regulatoria cuando corresponda;
- y techo de publicación.

Ninguna superficie financiera material debe emitirse sin esos campos.

### 7.2 Estados de finance readiness

El `decision_finance_posture` debe usar como mínimo el siguiente ladder:

| Estado | Significado | Uso externo máximo |
| --- | --- | --- |
| `screening_only` | la exposición puede filtrarse, pero el caso sigue dominado por estructura proxy | screening y triage únicamente |
| `range_bound_preliminary` | existen rangos económicos acotados, pero la dependencia de proxies sigue siendo material | briefing temprano y discusión acotada del caso |
| `bounded_decision_grade` | el caso es económicamente útil para priorización y lógica de no-go | reporting decision-grade |
| `held_for_overstatement_risk` | existe razonamiento económico, pero una publicación más fuerte sería engañosa | hold / uso interno |
| `hardened_within_boundary` | baseline, tarifa, costo y límites de implementación son materialmente más estrechos | superficie financiera acotada más fuerte |

Ninguno de estos estados implica bancabilidad por defecto.

## 8. Outputs prohibidos

La Fase 5 no puede producir:

- cierre financiero determinista no soportado por evidencia;
- lenguaje de savings garantizados;
- bancabilidad por estilo;
- certeza de grado-financiamiento cuando falta soporte de Fase 4;
- razonamiento de escenario único oculto presentado como objetivo;
- ni una recomendación de capital desconectada de la incertidumbre upstream.

### 8.1 Controles anti-theater y anti-pseudo-bankability

La Fase 5 debe bloquear explícitamente:

- payback de punto único cuando tanto el lado de beneficios como el de costos siguen siendo materialmente basados en proxies;
- presentación de NPV o IRR de escenario único cuando la procedencia del rango no es explícita;
- promoción de la preparación financiera mientras la dependencia de baseline siga sin resolverse;
- monetización de savings que corre por delante del endurecimiento de Fase 4;
- y cualquier redacción que haga que un `financial_exposure_case` acotado suene listo para un lender por estilo.

## 9. Familias de claims permitidas

Las siguientes familias de claims son admisibles:

- `financial_range_claim`
- `sensitivity_claim`
- `downside_exposure_claim`
- `upside_candidate_claim`
- `value_of_information_claim`
- `capital_fragility_claim`
- `finance_readiness_state_claim`

Todas quedan acotadas por la postura de evidencia.

## 10. Familias de claims prohibidas

Las siguientes están prohibidas salvo que exista soporte más fuerte de verdad:

- `verified_savings_claim`
- `deterministic_roi_claim`
- `bankable_case_claim`
- `financing_closure_claim`
- `guaranteed_payback_claim`

## 11. Modo low-data

Con datos públicos, intake mínimo y estructura técnica preliminar únicamente, la Fase 5 puede legítimamente hacer lo siguiente:

- expresar familias de rangos en lugar de puntos;
- separar downside y upside;
- identificar qué supuestos dominan la fragilidad financiera;
- cuantificar por qué más evidencia importa económicamente;
- y filtrar casos que son demasiado frágiles para justificar compromiso inmediato de CAPEX.

En low-data, la Fase 5 pertenece principalmente a uso screening-grade y decision-grade temprano.

### 11.1 Techo de outputs en low-data

En low-data, la Fase 5 puede emitir:

- bandas financieras direccionales;
- estructura de downside/upside;
- ordenamiento de sensibilidades;
- lógica de valor de la información;
- y afirmaciones de fragilidad económica.

No puede emitir:

- payback de punto único;
- ROI determinista;
- implicación de preparación para project finance;
- ni superficies financieras separadas de una declaración explícita de proxies.

## 12. Modo local-evidence

Cuando entran bills, tarifas locales, perfiles operativos, condición de equipos, observaciones tempranas de sitio o evidencia parcial de baseline, la Fase 5 puede:

- estrechar bandas de escenario;
- apretar downside y upside;
- distinguir outcomes financieros dependientes del régimen operativo;
- e identificar qué frente cambia materialmente la exposición de capital.

Eso es más fuerte que screening, pero sigue sin ser un cierre bancable por defecto.

### 12.1 Lógica de fortalecimiento con evidencia local

En este modo, la Fase 5 puede estrechar legítimamente:

- base tarifaria;
- análogos de costo;
- estructura de rangos dependiente del régimen;
- y concentración de downside.

Pero todavía no puede:

- colapsar la incertidumbre restante en análisis económico de punto único;
- implicar cierre de financiamiento;
- ni esconder qué variables restantes siguen controlando el caso.

## 13. Modo endurecido

La Fase 5 solo puede moverse hacia una postura financiera más fuerte cuando:

- la baseline está materialmente endurecida;
- los claims técnicos se han estrechado materialmente;
- los costos de implementación están mejor acotados;
- la exposición regulatoria se conoce mejor;
- y la Fase 4 tiene al menos una arquitectura seria de validación, si no soporte más fuerte aún.

Incluso entonces, la Fase 5 sigue acotada por su dominio de validez y no puede universalizar evidencia estrecha.

### 13.1 Regla de domain-of-validity

Cualquier caso financiero materialmente endurecido debe seguir declarando:

- alcance del régimen operativo;
- alcance del régimen tarifario;
- alcance de implementación;
- alcance del horizonte temporal;
- categorías de beneficios incluidas;
- y categorías de beneficios excluidas o aún provisionales.

Un caso financiero endurecido que no cargue esos límites sigue sin ser admisible como superficie externa fuerte.

## 14. Relación con Decision-grade y Verification-grade

La Fase 5 contribuye fuertemente a `Decision-grade` porque las decisiones de capital nunca son puramente técnicas.

La Fase 5 contribuye a `Verification-grade` solo de manera indirecta y condicional:

- no verifica desempeño por sí misma,
- pero se endurece materialmente cuando entra desempeño verificado o verification-supported.

Las finanzas no crean verificación. Reaccionan a ella.

## 15. Relación con las otras fases

**Con Fase 1**  
La Fase 5 hereda incertidumbre física y no puede borrarla mediante economía.

**Con Fase 2**  
La Fase 5 puede usar la estructura del twin para modelar alcance afectado, dependencia y exposición, pero no como prueba de savings realizados.

**Con Fase 3**  
La Fase 5 depende fuertemente del régimen operativo porque muchos outcomes económicos son régimen-sensibles.

**Con Fase 4**  
La Fase 4 es el puente principal de endurecimiento para claims de desempeño que luego aprietan finanzas.

**Con Fase 6**  
La Fase 6 puede inyectar costo regulatorio, riesgo, deadline o exposición de compliance al caso financiero.

**Con Fase 7**  
La Fase 7 gobierna cuándo un caso financiero se fortalece, se debilita o debe permanecer en hold.

**Con Fase 8**  
La Fase 8 consume la Fase 5 para decidir si actuar, diferir, validar o bloquear.

## 16. Reglas de upgrade

La Fase 5 solo puede subir cuando:

- un nuevo evento de evidencia estrecha materialmente la incertidumbre técnica;
- datos tarifarios o de costo locales reemplazan proxies más débiles;
- se reduce la debilidad de baseline;
- el alcance de implementación se vuelve más gobernable;
- o un factor de downside mayor queda eliminado o confirmado.

### 16.1 Triggers financieros canónicos

Los siguientes eventos son triggers canónicos de upgrade o re-evaluación para la Fase 5:

- una tarifa local reemplaza una tarifa proxy;
- una cotización local reemplaza un costo análogo;
- la baseline se estrecha materialmente;
- la baseline se debilita materialmente;
- cambia la clasificación del impulsor de beneficio;
- se abre o se cierra un frente de costo regulatorio;
- se estrecha el boundary de implementación;
- o desempeño medido cambia materialmente la estructura de rangos.

## 17. Reglas de downgrade, hold y block

`degrade` aplica cuando:

- se debilitan supuestos técnicos centrales;
- se ensanchan materialmente los supuestos de costo;
- el valor esperado se vuelve más frágil;
- o estimaciones previas de punto deben retroceder a bandas de escenario más amplias.

`hold` aplica cuando:

- una tarifa clave, CAPEX, baseline o variable operativa sigue sin resolverse;
- y una postura financiera más fuerte sería engañosa sin ese input.

`block` aplica cuando:

- el frente económico está demasiado débilmente ligado al caso como para justificar su publicación como superficie seria de decisión;
- o el aparente caso financiero depende casi por completo de supuestos técnicos no verificados o inestables.

## 18. Techo de lenguaje

En low-data y evidencia parcial, el lenguaje preferido incluye:

- financieramente plausible
- económicamente frágil
- acotado por rangos
- condicionado a
- altamente sensible a
- todavía no listo para endurecimiento financiero
- validación adicional tiene valor económico

El lenguaje bloqueado incluye:

- garantizado
- bankable
- business case cerrado
- payback confirmado
- ROI verificado

## 19. Criterio de completitud

La Fase 5 se considera epistemológicamente cerrada cuando el framework puede:

- producir exposición financiera acotada bajo evidencia escasa;
- distinguir economía de filtrado de cierre económico más fuerte;
- atar cada número material a un estado de soporte;
- propagar upgrades y downgrades explícitamente;
- impedir que la precisión económica corra por delante del soporte técnico;
- y preservar una diferencia clara entre endurecimiento financiero acotado y pseudo-bankability.
