# motor_registry.md

## Propósito del archivo

Este archivo deja explícito el catálogo de motores del proyecto ZLab en su estado actual, para que un sistema automatizado no tenga que inferir por conversación:
- qué motores existen;
- cuáles ya están trabajados;
- cuáles faltan;
- cuáles son fundacionales;
- cuáles son posteriores;
- cuáles son confirmados;
- y cuáles siguen siendo recomendables pero todavía ambiguos como motores separados.

Este archivo no redefine la metodología. Solo consolida lo ya discutido.

---

## Reglas de interpretación

### Confirmado
- Las fases no son lo mismo que los motores.
- Los motores implementan capacidades.
- El núcleo del sistema debe funcionar principalmente con scripts, programación y lógica determinista.
- La IA no es el esqueleto del sistema.
- La IA solo entra como capa auxiliar subordinada, normalmente para:
  - clasificación semántica asistida;
  - resumen de contenido ya estructurado;
  - candidate matching asistido;
  - explicación de conflictos o warnings;
  - generación controlada de texto downstream;
  - apoyo en búsqueda y priorización de fuentes.
- La IA no debe ser el núcleo de contratos, versionado, lineage, normalización determinista, identity resolution final, quality gating final, gobernanza ni decisiones terminales.
- La integración de IA puede hacerse vía API o modelo local, según el caso, pero siempre como capacidad auxiliar invocable y no como motor soberano.

### Inferido con alta confianza
- Este registro debe servir como fuente operativa para automatización futura.
- El sistema no debería crear motores nuevos automáticamente fuera de este catálogo sin revisión humana.

### Pendiente o ambiguo
- No está cerrada todavía la lista final absoluta de todos los motores posibles del proyecto a largo plazo.
- Algunos motores recomendables siguen siendo ambiguos como motores separados y podrían terminar absorbidos por otros.

---

## Convenciones de estado

### Confirmado

Se usará esta semántica mínima:
- `documented`: el motor ya tiene trabajo documental explícito en este proyecto.
- `planned`: el motor ya fue identificado y justificado, pero no está documentado todavía al mismo nivel.
- `recommended`: el motor parece necesario para un sistema completo y robusto, pero todavía no está totalmente cerrado como motor separado.
- `ambiguous`: existe como posibilidad razonable, pero no debe tratarse todavía como decisión cerrada.
- `out_of_scope_for_now`: motor reconocido pero no prioritario en el estado actual.

### Confirmado
Estos estados describen el estado catalogal del motor dentro del registro. No sustituyen el estado operativo por etapa definido en `motor_schema.json`.

### Pendiente o ambiguo
- No está definido todavía si estos estados se convertirán luego a un esquema JSON formal o a un sistema más fino.

---

## Grupo A — Motores fundacionales ya trabajados

Estos son los motores que ya existen con trabajo explícito en esta conversación y deben tratarse como motores confirmados del sistema.

### 1. Phase Contract Registry
- `status`: documented
- `priority`: fundacional
- `group`: control estructural
- `purpose`: definir y hacer cumplir contratos de fase, inputs, outputs, límites y handoffs.
- `why_it_exists`: evita que los motores invadan fases o produzcan outputs indebidos.
- `notes`: motor ya trabajado documentalmente.

### 2. Versioning + Lineage Engine
- `status`: documented
- `priority`: fundacional
- `group`: trazabilidad estructural
- `purpose`: versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
- `why_it_exists`: sin esto no hay rebuild, stale detection ni auditoría seria.
- `notes`: motor ya trabajado documentalmente.

### 3. Taxonomy + Canonical Entity Service
- `status`: documented
- `priority`: fundacional
- `group`: semántica estructural
- `purpose`: gobernar taxonomías, términos canónicos, aliases y límites semánticos.
- `why_it_exists`: evita drift semántico, dialectos paralelos y joins inestables.
- `notes`: motor ya trabajado documentalmente.

### 4. Ingestion + Parsing Engine
- `status`: documented
- `priority`: fundacional
- `group`: adquisición y estructuración inicial
- `purpose`: capturar fuentes, preservar raw y extraer estructura parcial trazable.
- `why_it_exists`: permite que el mundo real entre al sistema sin contaminarlo.
- `notes`: motor ya trabajado documentalmente.

### 5. Canonical Normalization Engine
- `status`: documented
- `priority`: fundacional
- `group`: transformación determinista
- `purpose`: convertir extracción heterogénea en forma canónica mínima preservando valores originales y reglas aplicadas.
- `why_it_exists`: desacopla el sistema de la heterogeneidad de fuentes.
- `notes`: motor ya trabajado documentalmente.

### 6. Entity Identity / Resolution Engine
- `status`: documented
- `priority`: fundacional
- `group`: identidad semántica
- `purpose`: resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
- `why_it_exists`: evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
- `notes`: motor ya trabajado documentalmente.

### 7. Quality / Fitness Evaluation Engine
- `status`: documented
- `priority`: fundacional
- `group`: evaluación estructural
- `purpose`: evaluar calidad estructural, completitud, trazabilidad y aptitud de uso por fase u objeto.
- `why_it_exists`: evita que objetos defectuosos o no aptos contaminen fases posteriores.
- `notes`: motor ya trabajado documentalmente.

---

## Grupo B — Motores confirmados y necesarios para un sistema completo

Estos motores no están todavía al mismo nivel documental que los siete anteriores, pero ya fueron identificados como necesarios para una arquitectura completa, robusta y bien recortada.

### 8. Source Registry + Rights Engine
- `status`: planned
- `priority`: alta
- `group`: control de fuentes
- `purpose`: registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
- `why_it_exists`: sin esto no hay control serio de fuentes públicas, premium o restringidas.

### 9. Source Change Detection / Refresh Intelligence Engine
- `status`: planned
- `priority`: alta
- `group`: refresh y obsolescencia
- `purpose`: detectar cambios de fuente, metodología, estructura, disponibilidad y prioridad de recaptura.
- `why_it_exists`: sin esto los datasets quedan stale sin que el sistema lo sepa.

### 10. Duplicate / Similarity Control Engine
- `status`: planned
- `priority`: media-alta
- `group`: higiene documental
- `purpose`: detectar duplicados exactos y near-duplicates a nivel raw, parsed y otros niveles.
- `why_it_exists`: no es lo mismo que identity resolution; controla repetición documental y dataset inflation.

### 11. Library Curation Engine
- `status`: planned
- `priority`: alta
- `group`: conocimiento reusable
- `purpose`: convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
- `why_it_exists`: evita que cada fase arme su propia pseudo-biblioteca local.

### 12. Public Data Engine
- `status`: planned
- `priority`: alta
- `group`: Fase 1
- `purpose`: materializar Fase 1 y producir facility_prior y bundles contextuales.
- `why_it_exists`: convierte infraestructura base en output útil de Fase 1.

### 13. Inference Case Activation Engine
- `status`: planned
- `priority`: alta
- `group`: activación analítica
- `purpose`: activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
- `why_it_exists`: separa selección de casos del análisis del Decision Core.

### 14. Decision Core / Inference Engine
- `status`: planned
- `priority`: alta
- `group`: Fase 2
- `purpose`: producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
- `why_it_exists`: es el corazón analítico de Fase 2.

### 15. Output Block Composition Engine
- `status`: planned
- `priority`: alta
- `group`: reporting estructurado
- `purpose`: construir bloques visibles trazables para Fase 3.
- `why_it_exists`: separa contenido visible gobernado del ensamblaje documental final.

### 16. Report Package Assembly Engine
- `status`: planned
- `priority`: alta
- `group`: reporting estructurado
- `purpose`: ensamblar Output Blocks en Report Package y vistas como technical_view y executive_view.
- `why_it_exists`: un bloque no equivale a un reporte integrado.

### 17. Document Rendering / LaTeX Report Compilation Engine
- `status`: planned
- `priority`: alta
- `group`: rendering documental
- `purpose`: convertir Report Package aprobado en documento técnico formal reproducible.
- `why_it_exists`: el documento final no es accesorio; es parte del output serio.

### 18. Chart Generation Engine
- `status`: planned
- `priority`: alta
- `group`: visualización analítica gobernada
- `purpose`: generar charts asset-first desde objetos analíticos del pipeline, con copy y curation subordinados al estado epistemológico del caso.
- `why_it_exists`: el reporte necesita visuales útiles para leer la lógica del caso, pero esos visuales no pueden transformarse en motores de verdad ni en decoración genérica.

### 19. LLM Writing Engine
- `status`: planned
- `priority`: alta
- `group`: narrativa gobernada
- `purpose`: convertir paquetes analíticos gobernados en prosa profesional y acotada para el reporte, sin introducir conocimiento ni claims nuevos.
- `why_it_exists`: el framework necesita narrativa legible, pero esa narrativa debe quedar subordinada al pipeline y nunca actuar como analista ni autoridad de decisión.

### 20. Propagation / Re-evaluation Engine
- `status`: planned
- `priority`: alta
- `group`: impacto y rebuild
- `purpose`: re-evaluar objetos downstream cuando cambian fuentes, reglas, taxonomías, contratos o bibliotecas.
- `why_it_exists`: versioning registra cambios, pero este motor decide qué debe re-evaluarse.

### 21. Dataset / Object Test Harness Engine
- `status`: planned
- `priority`: media-alta
- `group`: aseguramiento transversal
- `purpose`: correr pruebas sobre datasets, handoffs, contratos y objetos del sistema.
- `why_it_exists`: los motores pueden pasar solos y aun así fallar juntos.

### 22. Evaluation / Conformance Engine
- `status`: planned
- `priority`: alta
- `group`: aseguramiento transversal
- `purpose`: verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
- `why_it_exists`: evita degradación silenciosa del sistema con el tiempo.

### 23. Pipeline Orchestration + Observability Engine
- `status`: planned
- `priority`: alta
- `group`: operación del sistema
- `purpose`: orquestar ejecuciones, logs, retries, métricas, alertas y visibilidad operativa.
- `why_it_exists`: si el sistema será automatizado, necesita operación continua y auditable.

### 24. Governance Event & Exception Registry
- `status`: planned
- `priority`: media-alta
- `group`: soporte de gobernanza
- `purpose`: registrar anomalías, overrides, excepciones recurrentes y tensiones relevantes.
- `why_it_exists`: la gobernanza necesita señales explícitas y no solo intuición.

### 25. Epistemic Governance Layer
- `status`: planned
- `priority`: alta
- `group`: gobernanza transversal
- `purpose`: detectar tensiones estructurales, inflación de excepciones, insuficiencia taxonómica y distinguir cambio local, estructural o constitucional.
- `why_it_exists`: evita que el framework crezca rompiendo su constitución en silencio.

---

## Grupo B — Cadena sintética y ML (motores 029–033)

Estos motores forman la cadena de formalización de problemas, generación de datos sintéticos y soporte de decisión preliminar basado en ML. Son motores confirmados del sistema. Sus outputs son siempre no evidentiary. No reemplazan evidencia real, gobernanza de claims ni decisiones terminales. La semántica de sus outputs queda fijada por `synthetic_epistemology_rules.md`.

### 29. Problem Formalization / Expert Problem Spec Engine
- `status`: planned
- `priority`: alta
- `group`: formalización analítica
- `purpose`: convertir inference cases activados en especificaciones formales del problema, construidas desde conocimiento experto, restricciones reales y supuestos explícitos del dominio.
- `why_it_exists`: un dataset sintético sin especificación formal es ruido estructurado. Este motor produce el contrato del que depende toda la cadena.
- `notes`: prerequisito obligatorio de motor_030. No genera datos. No diseña modelos.

### 30. Synthetic Data Generation Engine
- `status`: planned
- `priority`: alta
- `group`: infraestructura de datos sintéticos
- `purpose`: generar datasets sintéticos condicionados por expert_problem_spec aprobado, representando de forma disciplinada el espacio del problema formalizado.
- `why_it_exists`: el framework necesita datos para ML exploratoria sin comprometer la separación entre evidencia real y soporte sintético.
- `notes`: todo output lleva synthetic_data_flag=true y non_evidentiary_flag=true. No genera desde especificaciones en borrador.

### 31. ML Experiment / Model Training & Evaluation Engine
- `status`: planned
- `priority`: alta
- `group`: capacidad analítica exploratoria
- `purpose`: entrenar, comparar y documentar modelos de ML sobre datasets sintéticos, produciendo capability_demonstration_report que muestra qué puede hacerse analíticamente bajo condiciones controladas.
- `why_it_exists`: demuestra capacidades analíticas antes de que exista evidencia real, permitiendo diseñar mejor la recolección de datos y la investigación de campo.
- `notes`: no produce modelos de producción. Toda métrica es sobre datos sintéticos. La política de selección de modelos es vinculante y está definida en el diseño del motor.

### 32. Synthetic ML Decision Support Integration
- `status`: planned
- `priority`: alta
- `group`: integración a decisión
- `purpose`: integrar capability_demonstration_report al Decision Core como señal subordinada etiquetada, estructurando el espacio de hipótesis sin elevar claims.
- `why_it_exists`: el Decision Core necesita recibir soporte sintético de forma trazable, etiquetada y epistemológicamente limitada, sin contaminar la cadena evidentiary.
- `notes`: no puede sustituir evidencia real ni gobernanza de claims. synthetic_support_flag=true en todo output.

### 33. TAD Preliminary Prioritization Engine
- `status`: planned
- `priority`: media-alta
- `group`: priorización exploratoria
- `purpose`: ordenar preliminarmente inference cases activos usando señales sintéticas del motor_032, produciendo un pre-filtro que oriente el esfuerzo analítico.
- `why_it_exists`: cuando hay múltiples inference cases activos compitiendo por recursos, se necesita una señal preliminar de orden de atención que sea trazable y no arbitraria.
- `notes`: output es preliminary_priority_register, nunca TAD final. El ranking es exploratorio y debe revisarse cuando exista evidencia real.

---

## Grupo C — Motores recomendables pero aún no totalmente cerrados como separados

Estos motores parecen útiles para un sistema completo, pero todavía no deben tratarse como decisión totalmente cerrada.

### 26. Access Control / Execution Policy Layer
- `status`: recommended
- `priority`: media
- `group`: control operativo
- `purpose`: controlar qué motores o procesos pueden operar sobre qué fuentes, datasets o outputs.
- `why_it_exists`: puede volverse necesario si se mezclan fuentes premium, automatización multi-herramienta o distintos niveles de acceso.
- `notes`: recomendable, pero todavía no 100% obligatorio como motor separado.

### 27. Artifact Export / Delivery Engine
- `status`: recommended
- `priority`: media
- `group`: entrega downstream
- `purpose`: empaquetar y entregar outputs hacia destinos concretos como PDF, JSON, machine bundle u otros.
- `why_it_exists`: podría separar entrega de composición si reporting crece mucho.
- `notes`: podría quedar absorbido temporalmente por reporting/rendering.

### 28. Search / Discovery Intelligence Layer
- `status`: ambiguous
- `priority`: media
- `group`: búsqueda continua
- `purpose`: sostener búsqueda continua y disciplinada de nuevas fuentes.
- `why_it_exists`: responde a la necesidad ya expresada de mejorar búsqueda y refresco continuo de datasets.
- `notes`: todavía ambiguo como motor autónomo; podría modelarse como workflow del Source Registry + Refresh Intelligence.

---

## Motores que no deben inferirse automáticamente todavía

### Confirmado

No deben crearse automáticamente como motores separados, salvo decisión posterior explícita:
- PDF engine separado del Document Rendering / LaTeX Engine;
- benchmark engine separado del Library Curation Engine y Public Data Engine;
- compliance engine separado del Evidence Maturity / Claim Permission stack y Governance Layer;
- matching engine separado del Entity Identity / Resolution Engine si duplica lógica;
- monitoring engine separado del Pipeline Orchestration + Observability Engine.

### Inferido con alta confianza

Si el sistema crece mucho, algunas de estas piezas podrían recortarse luego como motores autónomos, pero hoy no deben tratarse como cerradas.

---

## Resumen operativo

### Confirmado

En el estado actual del proyecto:
- motores ya trabajados explícitamente: 7
- motores confirmados y necesarios para un sistema completo: 30 en total contando los 7 ya trabajados
- motores recomendables pero todavía no totalmente cerrados como separados: 3

### Cálculo actual

#### Motores ya trabajados
1. Phase Contract Registry
2. Versioning + Lineage Engine
3. Taxonomy + Canonical Entity Service
4. Ingestion + Parsing Engine
5. Canonical Normalization Engine
6. Entity Identity / Resolution Engine
7. Quality / Fitness Evaluation Engine

#### Motores confirmados del sistema completo
8. Source Registry + Rights Engine
9. Source Change Detection / Refresh Intelligence Engine
10. Duplicate / Similarity Control Engine
11. Library Curation Engine
12. Public Data Engine
13. Inference Case Activation Engine
14. Decision Core / Inference Engine
15. Output Block Composition Engine
16. Report Package Assembly Engine
17. Document Rendering / LaTeX Report Compilation Engine
18. Chart Generation Engine
19. LLM Writing Engine
20. Propagation / Re-evaluation Engine
21. Dataset / Object Test Harness Engine
22. Evaluation / Conformance Engine
23. Pipeline Orchestration + Observability Engine
24. Governance Event & Exception Registry
25. Epistemic Governance Layer
26. Problem Formalization / Expert Problem Spec Engine
27. Synthetic Data Generation Engine
28. ML Experiment / Model Training & Evaluation Engine
29. Synthetic ML Decision Support Integration
30. TAD Preliminary Prioritization Engine

#### Motores recomendables o ambiguos como separados
31. Access Control / Execution Policy Layer
32. Artifact Export / Delivery Engine
33. Search / Discovery Intelligence Layer

---

## Qué sigue abierto o ambiguo

### Confirmado

No debe cerrarse automáticamente lo siguiente:
- lista final absoluta de todos los motores posibles a largo plazo;
- si los motores 26, 27 y 28 vivirán como motores autónomos o como parte de otros;
- si algunos motores confirmados se fusionarán temporalmente en el MVP;
- prioridad final exacta entre motores posteriores al 7;
- granularidad interna final de varios motores todavía no documentados.

### Inferido con alta confianza

Este archivo debe tratarse como catálogo operativo actual, no como catálogo eterno e inmutable.

### Pendiente o ambiguo

No está fijado todavía un campo formal por motor para:
- dependencia exacta;
- orden de diseño;
- orden de implementación;
- estado detallado por etapa.
Eso podría añadirse luego si se decide construir un registro más operativo.
