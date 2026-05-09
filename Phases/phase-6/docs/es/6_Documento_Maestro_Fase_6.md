# 6_Documento_Maestro_Fase_6
## Normatividad computable y cumplimiento

> Nota de espejo canónico: este documento es el reflejo en español de `Phases/phase-6/docs/en/6_Phase_6_Master_Document.md`. Debe mantenerse semánticamente alineado con ese documento. Si aparece una divergencia transitoria de traducción, la versión canónica en inglés gobierna hasta resincronización explícita.

## 1. Objetivo

Definir la Fase 6 como la capa que convierte complejidad regulatoria y normativa en lógica computable de triggers, screening de aplicabilidad, requerimientos de evidencia y estados acotados de compliance, sin confundir relevancia preliminar de regla con cierre legal o de cumplimiento.

## 2. Por qué importa

Los casos industriales con frecuencia esconden o clasifican mal la exposición regulatoria. La falla no es simplemente detalle legal faltante. Es usar descriptores parciales del activo, clasificaciones proxy o familiaridad regulatoria vaga para implicar:

- que una regla definitivamente aplica,
- que una regla definitivamente no aplica,
- o que la postura de compliance ya está entendida.

La Fase 6 existe para volver operativa la regulación desde el primer informe sin dejar que se convierta en pseudo-teatro legal.

## 3. Qué es la Fase 6 y qué no es

La Fase 6 es:

- una capa de screening y aplicabilidad,
- una capa de triggers computables,
- una capa de requerimientos de evidencia,
- y después, una capa de postura de compliance acotada.

La Fase 6 no es:

- un despacho de abogados,
- una autoridad certificadora,
- un motor final de compliance por defecto,
- un sustituto de clasificación de sitio,
- ni una forma de implicar cierre legal mediante wording confiado.

## 4. Unidad epistemológica central

La unidad central de la Fase 6 es el **`compliance_applicability_case`**.

Esta es la unidad correcta porque el razonamiento regulatorio debe permanecer atado a:

- una familia de reglas,
- una estructura de triggers,
- un boundary de caso,
- un estado de evidencia,
- y un techo semántico permitido.

## 5. Problemas que resuelve la Fase 6

La Fase 6 existe para resolver:

- exposición regulatoria oculta;
- incapacidad para triage de qué reglas importan primero;
- confusión entre aplicabilidad plausible y aplicabilidad real;
- falla para hacer visibles las evidencias necesarias para cierre de compliance;
- y sobreafirmación executive-facing sobre status regulatorio.

## 6. Inputs autorizados

La Fase 6 puede consumir:

- jurisdicción y contexto administrativo;
- tipo y tamaño del activo;
- clase de ocupación o proceso;
- clase de equipo y tipo de combustible;
- categoría de uso y patrón operativo cuando sea relevante;
- textos de código, standards, ordenanzas, filings y guía oficial;
- outputs contextuales y estructurales de Fases 1-3;
- evidencia medida o validada de Fase 4 cuando aplique.

## 7. Outputs autorizados

La Fase 6 está autorizada a producir:

- `regulatory_screening_register`
- `trigger_logic_map`
- `applicability_state_register`
- `required_regulatory_evidence_register`
- `computable_rule_check_register`
- `compliance_posture_register`

### 7.1 Objetos operativos requeridos

Para mantener la Fase 6 estable entre screening, evidencia parcial y endurecimiento más fuerte, cada `compliance_applicability_case` vivo debe poder referenciar:

- `rule_family_record`
- `jurisdiction_trace_record`
- `trigger_field_register`
- `threshold_register`
- `exception_register`
- `rule_conflict_record`
- `compliance_posture_state`

Como mínimo, cada caso debe declarar:

- jurisdicción;
- fuente de autoridad;
- familia de regla;
- versión de la regla o fecha de vigencia cuando exista;
- boundary del activo;
- boundary de subsistema cuando sea relevante;
- campos de trigger faltantes;
- dependencia de threshold;
- ruta de excepción si existe;
- y techo de publicación.

### 7.2 Ladder de aplicabilidad y postura

El ladder mínimo de estados para la Fase 6 es:

| Estado | Significado | Uso externo máximo |
| --- | --- | --- |
| `rule_family_relevant` | esta familia de reglas merece atención | superficie de screening |
| `trigger_plausible` | los hechos disponibles hacen creíble un trigger | screening y flag de riesgo |
| `trigger_partially_supported` | algunos campos de trigger están soportados, pero faltan campos decisivos | screening técnico y decision-grade |
| `trigger_confirmed` | una condición decisiva de trigger está materialmente confirmada | manejo más fuerte de aplicabilidad |
| `applicability_likely` | la aplicabilidad es materialmente probable bajo la clasificación acotada actual | uso bounded decision-grade |
| `applicability_confirmed` | la aplicabilidad está acotada y materialmente soportada | trabajo de postura de compliance más fuerte |
| `compliance_open` | la aplicabilidad está viva y el cierre de compliance sigue abierto | superficies técnicas y decision-grade |
| `bounded_compliance_posture` | el caso tiene una postura de compliance acotada y basada en evidencia | superficie regulatoria acotada más fuerte |

El cierre de compliance sigue siendo una cosa distinta de este ladder y nunca debe implicarse por él.

## 8. Outputs prohibidos

La Fase 6 no puede producir:

- cierre legal por implicación;
- certificación final de compliance sin evidencia;
- claims ocultos de no-compliance basados solo en evidencia proxy;
- ni wording ejecutivo que suene final cuando los rule triggers siguen abiertos.

### 8.1 Regla de threshold, exception y conflict

La Fase 6 debe preservar explícitamente tres cosas siempre que importen:

- dependencia de threshold;
- dependencia de exception o exemption;
- y dependencia de conflicto entre reglas.

Si cualquiera de esas tres sigue materialmente sin resolverse, el lenguaje externo de compliance debe seguir pendiente o acotado.

## 9. Familias de claims permitidas

Las siguientes son admisibles:

- `regulatory_screening_claim`
- `trigger_plausibility_claim`
- `applicability_pending_claim`
- `evidence_required_for_compliance_claim`
- `bounded_compliance_state_claim`

## 10. Familias de claims prohibidas

Las siguientes están prohibidas salvo que el soporte realmente las permita:

- `final_compliance_claim`
- `certified_non_compliance_claim`
- `rule_inapplicability_claim` basado en inferencia débil
- `legal_opinion_claim`

## 11. Modo low-data

Con datos públicos e información de caso escasa, la Fase 6 puede legítimamente:

- identificar familias de reglas relevantes;
- detectar estructuras de trigger plausibles;
- marcar ventanas de timing y exposición potencial;
- pedir los campos faltantes necesarios para cierre;
- y mostrar dónde la presión regulatoria puede afectar materialmente la priorización.

En este modo, los outputs correctos son salidas de screening-grade y decision-grade, no cierre de compliance.

### 11.1 Techo de outputs en low-data

En low-data, la Fase 6 puede emitir:

- familias de reglas relevantes;
- trigger plausibility;
- pedidos de evidencia;
- flags de timing o exposición.

No puede emitir:

- inapplicability confirmada basada en razonamiento proxy débil;
- postura de compliance que suene cerrada;
- ni certeza legal oculta.

## 12. Modo local-evidence

Cuando entran descriptores de sitio, clases de equipos, datos de ocupación, confirmación de tamaño, confirmación de combustible, clasificación de proceso u observaciones de campo, la Fase 6 puede:

- estrechar aplicabilidad;
- quitar familias de reglas irrelevantes;
- elevar ciertos frentes de regla desde plausible a materialmente probable;
- y distinguir triggers abiertos de triggers confirmados.

### 12.1 Lógica de fortalecimiento con evidencia local

En este modo, la Fase 6 puede legítimamente:

- colapsar parte de la incertidumbre de triggers;
- separar aplicabilidad asset-wide de aplicabilidad por subsistema;
- y estrechar la carga de evidencia por familia de regla.

Todavía no puede:

- implicar certificación;
- implicar opinión legal;
- ni borrar dependencia no resuelta de exception o threshold.

## 13. Modo endurecido

Una postura de compliance más fuerte solo se vuelve legítima cuando:

- los campos de trigger están materialmente confirmados;
- la clasificación del activo y del sistema está suficientemente acotada;
- la evidencia relevante está ligada localmente al boundary de la regla;
- y, cuando haga falta, existe evidencia de medición o presentación regulatoria.

Incluso en modo endurecido, el cierre de compliance sigue acotado a la regla, el alcance y la evidencia que realmente se endureció.

### 13.1 Regla de trazabilidad por jurisdicción

Cualquier postura regulatoria endurecida debe seguir preservando:

- jurisdicción fuente;
- autoridad emisora;
- contexto de versión o fecha de vigencia cuando exista;
- alcance de activo y subsistema;
- dependencia de medición o presentación regulatoria si existe;
- y si la postura sigue condicionada por manejo de exception.

## 14. Relación con Decision-grade y Verification-grade

La Fase 6 contribuye a `Decision-grade` muy temprano porque la exposición regulatoria cambia urgencia, secuencia y lógica de no-go mucho antes de que el compliance final esté cerrado.

La Fase 6 contribuye a `Verification-grade` solo cuando la confirmación de triggers y la evidencia soporte son materialmente suficientes. La regulación puede volverse más fuerte sin estar “verificada” exactamente igual que el desempeño, pero igual requiere disciplina de evidencia.

## 15. Relación con las otras fases

**Con Fase 0**  
La Fase 0 gobierna el techo semántico e impide inflación legal.

**Con Fase 1**  
Los priors físicos y de uso pueden abrir familias de reglas, pero no cerrarlas.

**Con Fase 2**  
La estructura del twin puede aclarar qué sistemas o clases de equipos son relevantes.

**Con Fase 3**  
Los regímenes operativos pueden afectar si una regla se dispara materialmente.

**Con Fase 4**  
Medición o validación pueden ser necesarias para cerrar ciertas condiciones de trigger o threshold.

**Con Fase 5**  
La postura regulatoria puede afectar materialmente exposición económica y timing.

**Con Fase 7**  
La gobernanza del estado de creencias determina cuándo la aplicabilidad sube, se debilita o queda en hold.

**Con Fase 8**  
TAD consume la postura regulatoria para reordenar validación y acción.

## 16. Reglas de upgrade

La Fase 6 solo puede subir cuando:

- se confirman campos de trigger decisivos;
- el alcance de la regla se estrecha materialmente;
- evidencia local reemplaza supuestos proxy;
- clasificación de equipo o proceso se vuelve explícita;
- o evidencia de presentación regulatoria o medición cambia materialmente la aplicabilidad.

### 16.1 Triggers regulatorios canónicos

Los siguientes eventos son triggers canónicos de upgrade o re-evaluación para la Fase 6:

- trigger field confirmado;
- trigger field refutado;
- threshold medido;
- exception evidenciada;
- exception retirada;
- conflicto entre familias de reglas aclarado;
- cambia la guía oficial;
- llega evidencia de presentación regulatoria;
- o cambia la clasificación de subsistema.

## 17. Reglas de downgrade, hold y block

`degrade` aplica cuando:

- la aplicabilidad previa dependía de una clasificación que luego se debilita;
- el boundary de la regla se estrecha materialmente;
- o cae la certeza sobre el trigger.

`hold` aplica cuando:

- todavía falta evidencia decisiva de trigger;
- la aplicabilidad sigue siendo materialmente relevante;
- y un lenguaje externo más fuerte sería engañoso.

`block` aplica cuando:

- una familia de reglas ya no es materialmente relevante;
- el frente de exposición no justifica superficie de reporte;
- o el caso carece de conexión suficiente con la regla incluso para screening serio.

## 18. Techo de lenguaje

El lenguaje preferido incluye:

- el screening regulatorio sugiere
- trigger plausible
- la aplicabilidad sigue pendiente
- todavía hace falta evidencia para cerrar
- probablemente relevante bajo la definición actual del caso
- todavía no certificable

El lenguaje bloqueado incluye:

- cumple
- viola
- definitivamente no aplica
- certificado
- legalmente cerrado

## 19. Criterio de completitud

La Fase 6 se considera epistemológicamente cerrada cuando el framework puede:

- exponer relevancia regulatoria temprano;
- separar screening de cierre;
- atar toda postura regulatoria a lógica de regla y estado de evidencia;
- preservar linaje de umbrales, excepciones y jurisdicción;
- e impedir que el lenguaje de compliance corra por delante del soporte.
