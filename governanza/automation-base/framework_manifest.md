# framework_manifest.md

## 1. Qué es el proyecto

### Confirmado
Este proyecto busca convertir el framework ZLab en una arquitectura de software implementable, trazable y escalable, sin perder la disciplina epistemológica ya definida en las fases del framework.

El objetivo inmediato no es construir una aplicación final ni una interfaz. El objetivo es congelar el contexto útil del proyecto para poder automatizar después el diseño e implementación de motores con Claude, Codex u otra herramienta, reduciendo improvisación, retrabajo y ambigüedad.

### Inferido con alta confianza
La intención operativa es pasar de metodología cerrada a infraestructura real de software, de forma modular y con contratos explícitos.

### Pendiente o ambiguo
No está definido todavía el repositorio final, formato exacto de carpetas ni pipeline completo de automatización.

---

## 2. Qué se está construyendo

### Confirmado
Se está construyendo una arquitectura de motores de software para soportar todo el framework ZLab.

Estos motores no son las fases. Son componentes de software que materializan capacidades necesarias para que el framework opere con:
- contratos claros;
- trazabilidad;
- versionado;
- taxonomía controlada;
- ingesta disciplinada;
- normalización;
- resolución de identidad;
- evaluación de calidad;
- curación;
- inferencia;
- reporting;
- verificación;
- y gobernanza.

También se está construyendo una base documental para que cada motor pueda luego implementarse en código sin rediseñar la arquitectura en cada paso.

### Inferido con alta confianza
La construcción real se está enfocando primero en la columna vertebral de datos y gobernanza, antes de entrar en motores más downstream como reporting final o verification bridge operativo.

### Pendiente o ambiguo
No está cerrada todavía la lista final completa de todos los motores ni su nivel exacto de madurez para MVP versus fases posteriores.

---

## 3. Qué es un motor

### Confirmado
Un motor es una capacidad de software separada, con responsabilidad concreta, límites claros, inputs definidos, outputs definidos, contratos explícitos y posibilidad de crecimiento sin contaminar al resto del sistema.

Un motor:
- no equivale a una fase;
- no debe redefinir la fase que sirve;
- puede servir a una o varias fases;
- debe poder documentarse, testearse, versionarse y evaluarse por separado.

El objetivo de los motores dentro del framework es:
- implementar funciones transversales y operativas;
- preservar trazabilidad y lineage;
- evitar mezcla de responsabilidades;
- soportar handoffs entre fases;
- preparar outputs utilizables por fases posteriores;
- y permitir que el sistema escale sin convertirse en un conjunto caótico de scripts.

### Inferido con alta confianza
El motor debe existir como unidad de arquitectura real, no como etiqueta conceptual vaga ni como módulo que hace de todo.

### Pendiente o ambiguo
No está totalmente fijado si algunos motores se fusionarán temporalmente en el MVP por motivos prácticos, aunque la preferencia explícita ha sido evitar fusiones peligrosas.

---

## 4. Cómo fluye un motor

### Confirmado
Cada motor sigue un flujo secuencial y disciplinado. Un motor no nace en código. Nace como una definición arquitectónica y documental. Solo después de cerrar esa base pasa a schema técnico, tests, implementación y revisión.

La secuencia estándar de trabajo por motor es:

1. Documentación base  
2. Schema técnico  
3. Tests  
4. Failure modes  
5. Implementación  
6. Revisión de conformidad

### Objetivo de cada etapa

#### 4.1 Documentación base
Definir qué es el motor, qué hace, qué no hace, qué entra, qué sale, qué objetos mínimos necesita, cómo se valida y qué errores deben bloquearse.

#### 4.2 Schema técnico
Traducir la documentación base a una estructura técnica concreta: entidades, objetos, campos, relaciones, versionado, lineage y persistencia conceptual.

#### 4.3 Tests
Definir cómo se valida que el motor cumple su función mínima y cómo se detectan errores, casos sparse, malformed input y edge cases.

#### 4.4 Failure modes
Definir cómo puede degradarse el motor, qué anti-patterns lo dañan, qué errores serían costosos de corregir después y qué señales indican monolitización o exceso de responsabilidad.

#### 4.5 Implementación
Construir el núcleo de código del motor respetando exactamente la documentación base, el schema técnico y los límites ya definidos.

#### 4.6 Revisión de conformidad
Verificar que la implementación:
- respeta el contrato;
- no mezcla responsabilidades;
- preserva metadatos críticos;
- y no excede el rol del motor.

### Reglas de transición entre etapas

#### De documentación base a schema técnico
Solo se pasa cuando el motor ya tiene definidos:
- propósito;
- límites;
- contrato funcional;
- objetos mínimos;
- reglas de validación;
- acceptance tests;
- failure modes.

#### De schema técnico a tests y failure modes finales
Solo se pasa cuando ya existe una representación técnica suficientemente clara de entidades, campos, relaciones y metadatos obligatorios.

#### De tests y failure modes a implementación
Solo se pasa cuando:
- el contrato ya no está ambiguo;
- el schema técnico está cerrado;
- los tests mínimos ya están definidos;
- y los failure modes principales están explícitos.

#### De implementación a revisión de conformidad
Solo se pasa cuando ya existe:
- código del motor;
- tests mínimos;
- ejemplo de uso;
- y una estructura suficientemente clara para revisar cumplimiento.

### Criterios de cierre de etapa

#### Cierre de documentación base
La documentación base se considera cerrada cuando:
- el motor está definido con claridad;
- sus límites están explícitos;
- no quedan ambiguos inputs/outputs principales;
- se conocen sus objetos mínimos;
- y está listo para pasar a schema técnico.

#### Cierre de schema técnico
El schema técnico se considera cerrado cuando:
- entidades u objetos están definidos;
- campos mínimos están cerrados;
- relaciones y versionado están definidos;
- y el motor ya puede ser testeado sin inventar estructura.

#### Cierre de tests
La etapa de tests se considera cerrada cuando:
- están cubiertos los casos mínimos exigidos;
- los criterios observables de éxito y fallo son claros;
- y los edge cases críticos del motor están explícitos.

#### Cierre de failure modes
La etapa se considera cerrada cuando:
- ya se conocen los modos principales de degradación;
- ya están listados los anti-patterns;
- y ya están marcados los errores de arquitectura más caros de corregir.

#### Cierre de implementación
La implementación se considera cerrada cuando:
- respeta el contrato;
- respeta límites;
- preserva metadatos críticos;
- y existe una base mínima usable del motor.

#### Cierre de revisión de conformidad
La revisión se considera cerrada cuando:
- no hay violaciones materiales del contrato;
- no hay mezcla grave de responsabilidades;
- no hay pérdida de trazabilidad o lineage esenciales;
- y el motor puede considerarse listo para integrarse o pasar al siguiente.

### Criterios de cierre de motor

Un motor se considera cerrado cuando:
- su documentación base está cerrada;
- su schema técnico está cerrado;
- sus tests mínimos existen;
- sus failure modes están documentados;
- su implementación existe;
- su revisión de conformidad no muestra violaciones materiales;
- y el motor ya puede existir como unidad separada sin depender de reinterpretaciones continuas.

### Posibles bucles de corrección

El flujo admite correcciones, pero no debe convertirse en un ciclo caótico de rediseño permanente.

Los bucles de corrección esperados son:
1. de schema técnico hacia documentación base, si el schema revela una ambigüedad real no resuelta;
2. de tests hacia schema técnico, si los tests descubren falta de estructura mínima;
3. de implementación hacia schema técnico o tests, si el código revela inconsistencia objetiva con el diseño aprobado;
4. de revisión de conformidad hacia implementación, para corregir desviaciones del contrato, mezcla de responsabilidades o pérdida de metadatos críticos.

### Qué debe evitarse en el flujo

Durante el flujo de un motor debe evitarse:
- empezar por código;
- mezclar fases con motores;
- usar IA como sustituto de arquitectura explícita;
- redefinir el motor durante la implementación;
- mezclar responsabilidades de varios motores en uno;
- corregir silenciosamente contratos o metadatos;
- introducir features por si acaso;
- hacer sobre-ingeniería ornamental;
- producir documentación vaga;
- asumir que prompts de implementación equivalen a arquitectura cerrada;
- saltarse tests o failure modes;
- confundir un output funcional con un motor correctamente diseñado;
- usar narrativa o conveniencia como sustituto de trazabilidad y límites.

### Inferido con alta confianza
El flujo por motor está pensado para que Claude, Codex u otra herramienta puedan intervenir después sin rediseñar el motor en cada etapa.

### Pendiente o ambiguo
No está definido todavía si todos los motores usarán exactamente el mismo nivel de profundidad documental o si algunos motores menores tendrán un flujo abreviado.

---

## 5. Qué estado mínimo debe conservarse por motor

### Confirmado
El esquema mínimo de estado por motor debe permitir:

- identificar el motor;
- saber en qué etapa está;
- saber qué etapas ya completó;
- saber qué artefactos existen;
- saber cuáles faltan;
- registrar validaciones;
- registrar correcciones;
- registrar estado general;
- registrar bloqueo, pausa o espera si aplica;
- registrar cierre del motor.

### Estructura mínima confirmada

- `motor_id`
- `motor_name`
- `purpose`
- `current_stage`
- `stage_sequence`
- `completed_stages`
- `artifacts`
- `missing_artifacts`
- `validations`
- `corrections`
- `status`
- `blocked`
- `paused`
- `waiting_on`
- `closure`
- `notes`
- `updated_at`

### Artefactos mínimos por etapa

#### Documentación base
- `master_concept_doc`
- `functional_contract`
- `conceptual_schema`
- `operational_rules`
- `acceptance_tests`
- `failure_modes`
- `design_done_criteria`

#### Schema técnico
- `technical_schema`

#### Tests
- `test_spec`

#### Failure modes
- `failure_modes_spec`

#### Implementación
- `codebase`
- `usage_example`

#### Revisión de conformidad
- `conformance_review_report`

### Inferido con alta confianza
Este estado mínimo existe para que un sistema pueda seguir el progreso del motor sin perder contexto y sin depender de memoria conversacional implícita.

### Pendiente o ambiguo
- `purpose` es útil, pero su nivel exacto de detalle no quedó totalmente fijado.
- `waiting_on` está implícito por bloqueos, pausas o dependencias, pero no fue desarrollado más allá de eso.
- Los nombres concretos de artefactos podrían variar levemente según cómo se nombren los archivos reales.
- No se fijó un formato único obligatorio para timestamps.

---

## 6. Qué reglas de calidad son obligatorias

### Confirmado

#### Principios obligatorios

1. La arquitectura debe ser deterministic-first.  
   El LLM no puede sustituir contratos, trazabilidad, versionado, taxonomía ni lógica estructural.

2. Cada motor debe tener límites duros.  
   Debe quedar claro qué hace, qué no hace, qué entra y qué sale.

3. La documentación base precede al código.  
   Ningún motor debe pasar a implementación sin documentación base, schema técnico, tests y failure modes.

4. Todo debe ser trazable y reconstruible.  
   Deben preservarse provenance, lineage, versionado y posibilidad de rebuild.

5. No silent mutation.  
   No se deben corregir datos, contratos, taxonomías u outputs silenciosamente.

6. La prioridad del MVP no es capturar todo.  
   La prioridad es separar responsabilidades, preservar metadatos correctos y evitar retrabajo futuro.

7. No monolitos.  
   Los motores no deben crecer como módulos gigantes que mezclan responsabilidades.

8. Escalabilidad sin sobre-ingeniería ornamental.  
   Cada motor debe nacer con estructura suficiente para crecer sin rehacerse, pero sin complejidad gratuita.

9. La separación entre fases y motores es obligatoria.  
   Las fases definen autoridad. Los motores implementan capacidades.

10. La implementación no es un espacio de rediseño.  
    El código debe obedecer lo ya cerrado en documentación.

#### Reglas estructurales

1. Una pieza nueva solo debe existir si tiene una responsabilidad separable.
2. Cada motor debe existir como unidad de arquitectura real.
3. No mezclar responsabilidades entre captura, normalización, identidad, curación, reporting o gobernanza.
4. Cada motor debe tener contratos explícitos.
5. Toda pieza debe preservar metadatos críticos.
6. Toda pieza debe poder ser evaluada por separado.
7. Evitar dependencia opaca entre piezas.
8. No usar prompts de implementación como sustituto de arquitectura cerrada.

#### Reglas para escribir nuevas piezas

1. No crear una pieza nueva por comodidad local.
2. No escribir código antes de cerrar la documentación base.
3. No introducir features por si acaso.
4. No introducir complejidad decorativa.
5. Toda nueva pieza debe nacer con criterio de escalabilidad real.
6. Toda nueva pieza debe poder explicar qué problema resuelve y cuál no.
7. Toda nueva pieza debe definir qué no hace.

#### Reglas para modificar piezas existentes

1. No reabrir una pieza cerrada por hallazgos menores.
2. No usar implementación como excusa para rediseñar el motor completo.
3. Solo volver de una etapa posterior a una anterior cuando exista inconsistencia objetiva.
4. No corregir piezas existentes con silent mutation.
5. No mezclar corrección con expansión de alcance.
6. No romper la separación entre objeto vigente, historial y derivados.

#### Antipatrones prohibidos

- empezar por código;
- confundir fases con motores;
- usar IA como sustituto de arquitectura explícita;
- redefinir el motor durante la implementación;
- mezclar responsabilidades de varios motores en uno;
- corregir silenciosamente contratos o metadatos;
- introducir features por si acaso;
- hacer sobre-ingeniería ornamental;
- producir documentación vaga;
- asumir que prompts de implementación equivalen a arquitectura cerrada;
- saltarse tests o failure modes;
- confundir un output funcional con un motor correctamente diseñado;
- usar narrativa o conveniencia como sustituto de trazabilidad y límites;
- construir scripts monolíticos;
- permitir que el LLM se vuelva núcleo soberano;
- construir piezas que obliguen a rehacer el resto al crecer;
- pensar que más datos equivale a mejor sistema;
- confundir calidad estructural con verdad epistemológica final;
- suponer que benchmarks o contexto público equivalen a verificación de sitio;
- rellenar huecos con intuiciones no confirmadas;
- tomar deseos futuros como decisiones ya tomadas.

#### Criterios mínimos de aceptación

Una pieza o motor no debe considerarse aceptable si no cumple, como mínimo, con lo siguiente:
- respeta su contrato;
- respeta sus límites;
- no mezcla responsabilidades;
- preserva metadatos críticos;
- tiene tests mínimos;
- tiene failure modes explícitos;
- puede revisarse por conformidad;
- puede existir como unidad separada sin reinterpretaciones continuas;
- está lista para escalar sin rehacerse estructuralmente.

### Inferido con alta confianza
- Hay preferencia fuerte por modularidad, tipado claro, interfaces explícitas, validación explícita, errores estructurados y tests como parte central del diseño.
- También es antipatrón esconder lógica importante en helpers genéricos o abstracciones bonitas sin necesidad real.

### Pendiente o ambiguo
- No está fijado un stack técnico único.
- No hay todavía reglas operativas suficientemente detalladas para performance por motor específico.
- La eficiencia de CPU, RAM, disco e I/O está deseada de forma implícita por el rechazo a monolitos, scripts caóticos y sobre-ingeniería, pero no está desarrollada todavía como política detallada por motor.

---

## 7. Qué límites existen actualmente

### Confirmado
Los límites actuales del proyecto son:

- no se está construyendo todavía UI;
- no se está construyendo todavía producto final;
- no se está construyendo todavía marketing;
- no se está construyendo todavía un chatbot;
- no se está construyendo todavía una solución genérica de data lake más dashboard;
- no se está permitiendo que los motores improvisen razonamiento libre;
- no se está autorizando a los motores a redefinir fases ni epistemología.

Además:
- el foco actual está en diseño documental y arquitectónico;
- el código viene después;
- y la automatización posterior con Claude, Codex u otra herramienta debe apoyarse en archivos base congelados.

### Inferido con alta confianza
El objetivo inmediato es consolidar contexto y luego usarlo como base para generar archivos, prompts y código con menos riesgo.

### Pendiente o ambiguo
No está definido todavía el momento exacto en el que se pasará de documentación a implementación efectiva de cada motor.

---

## 8. Qué ambigüedades siguen abiertas y no deben cerrarse automáticamente

### Confirmado
Lo siguiente sigue abierto o ambiguo y no debe cerrarse automáticamente:

- lista final definitiva de todos los motores;
- posibles fusiones temporales de algunos motores en el MVP;
- stack técnico exacto de implementación;
- repositorio y estructura final de archivos;
- automatización exacta con Codex, Claude u otra herramienta;
- orden final detallado después del motor 7;
- especificación final de todos los archivos base necesarios.

### Inferido con alta confianza
También siguen abiertos:
- el detalle completo de motores de reporting downstream;
- la forma exacta del motor de evaluación/conformance;
- el nivel de granularidad de algunos objetos internos de motores todavía no documentados;
- el formato exacto final de todos los archivos por etapa;
- si todos los motores tendrán exactamente el mismo número de artefactos;
- qué gates automáticos existirán entre etapas;
- y el protocolo exacto de cierre final cuando varios motores ya estén integrados.

### Pendiente o ambiguo
- No se puede afirmar todavía que el otro chat de construcción de motores haya dejado cerrados todos los motores uno por uno.
- No está definido todavía el umbral formal entre corrección menor y cambio estructural.
- No existe todavía una matriz única y formal de scoring de calidad para todos los motores.
- No está claro todavía qué partes del contexto del otro chat requerirán revalidación manual antes de pasarse a archivos ejecutables o a automatización masiva.

---

## 9. Posibles contradicciones o tensiones detectadas entre los archivos base

### Confirmado

1. Profundidad uniforme del flujo vs variabilidad real por motor.  
   `workflow_rules.md` presenta un flujo estándar único por motor, pero también deja abierto si algunos motores menores podrían tener un flujo abreviado. No es contradicción dura, pero sí una tensión operativa.

2. Artefactos mínimos fijos vs nombres finales de archivos aún no cerrados.  
   `motor_schema.json` fija artefactos mínimos por etapa, mientras `workflow_rules.md` deja abierto el formato final exacto de carpetas y nombres de archivos. La estructura está clara, pero el naming final aún no.

3. Escalabilidad real deseada vs stack técnico no definido.  
   `master_context.md` y `quality_rules.md` exigen escalabilidad, modularidad y trazabilidad desde el inicio, pero el stack técnico sigue abierto. No es contradicción conceptual, pero sí una tensión práctica que puede afectar implementación.

4. Deterministic-first y tests fuertes vs ausencia de gates automáticos definidos.  
   Los archivos base exigen disciplina alta, pero todavía no está definido si habrá gates automatizados entre etapas. Hay coherencia en principios, pero falta mecanismo cerrado.

5. Estado mínimo por motor suficientemente claro vs cierre final aún ambiguo.  
   `motor_schema.json` permite seguir el progreso de un motor, pero `workflow_rules.md` deja ambiguo si el cierre final requerirá integración obligatoria con otros motores. El estado local del motor está bien definido; el criterio de cierre sistémico aún no.

### Inferido con alta confianza

Estas tensiones no invalidan los archivos base actuales. Funcionan como puntos de vigilancia para que la automatización futura no cierre prematuramente decisiones que todavía están abiertas.

### Pendiente o ambiguo

No está definido todavía si estas tensiones se resolverán como:
- normalización documental adicional;
- reglas operativas nuevas;
- gates automáticos;
- o convenciones técnicas más cerradas en una etapa posterior.

---

## 10. Ajustes operativos posteriores

### Confirmado
Para reducir ambigüedad operativa del paquete base, se agregaron estos documentos complementarios:
- `document_authority.md`
- `stage_artifact_semantics.md`
- `motor_state_semantics.md`

Su función es cerrar, sin rediseñar el framework:
- la jerarquía mínima de autoridad documental;
- la relación estable entre etapa y artefacto;
- y la semántica mínima del estado del motor y de `closed`.

### Inferido con alta confianza
`framework_manifest.md` debe seguir tratándose como consolidado útil, pero no como sustituto de esos documentos más específicos cuando exista conflicto.

### Pendiente o ambiguo
No está definido todavía si estos ajustes deberán absorberse luego dentro de un manifiesto único más formal.
