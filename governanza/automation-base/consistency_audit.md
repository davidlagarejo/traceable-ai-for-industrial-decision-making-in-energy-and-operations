## 0. Estado posterior a ajustes mínimos

### Confirmado
Después de esta auditoría se agregaron documentos específicos para resolver cuatro puntos críticos del paquete:
- `document_authority.md`: jerarquía mínima de autoridad documental y semántica vinculante de etiquetas.
- `stage_artifact_semantics.md`: relación estable entre etapas y artefactos para `acceptance_tests`, `test_spec`, `failure_modes`, `failure_modes_spec` y `conformance_review_report`.
- `motor_state_semantics.md`: semántica mínima del estado del motor y significado exacto de `closed`.

### Inferido con alta confianza
Estos ajustes reducen el riesgo inmediato de automatización prematura o inconsistente, aunque no eliminan todos los huecos detectados en este archivo.

### Pendiente o ambiguo
El resto del documento sigue siendo válido como diagnóstico de riesgos que no han quedado completamente cerrados por esos ajustes.

---

# Consistency Audit

## 1. Contradicciones reales

### 1.1 `master_context.md` vs `framework_manifest.md` sobre el estado de cierre de motores

En ambos archivos se afirma que existen motores "ya priorizados" y motores "posteriores ya previstos", pero no queda totalmente claro si eso significa:
- que esos motores ya están oficialmente aceptados como parte del sistema;
- o solo que han sido discutidos en conversación.

No es una contradicción frontal de contenido, pero sí una contradicción de nivel de compromiso: a veces suenan como lista establecida; a veces como lista provisional.

### 1.2 `workflow_rules.md` vs `motor_schema.json` sobre el orden y granularidad de artefactos

`workflow_rules.md` define etapas separadas:
- documentación base;
- schema técnico;
- tests;
- failure modes;
- implementación;
- revisión.

Pero `motor_schema.json` modela `artifacts` por etapa con una estructura fija y mínima que en algunos casos mezcla cosas que en los textos aparecen como entregables separados o recursivos. Por ejemplo:
- `documentation_base` ya incluye `acceptance_tests` y `failure_modes`;
- mientras `workflow_rules.md` también los trata como etapas separadas posteriores.

Aquí sí hay una contradicción real de modelo:
- en un archivo parecen parte de la documentación base;
- en otro aparecen como etapas posteriores autónomas.

### 1.3 `quality_rules.md` vs `workflow_rules.md` sobre cuándo queda "cerrado" algo

`quality_rules.md` define criterios mínimos de aceptación y cierre muy ligados a conformidad arquitectónica. `workflow_rules.md` define cierre por etapa y cierre de motor con una lógica más secuencial-operativa.

No se contradicen en intención, pero sí hay una diferencia no resuelta entre:
- cierre operacional;
- y aceptación de calidad.

Eso puede generar que un motor aparezca como `closed` en el flujo pero todavía no esté aceptado bajo reglas de calidad si no se alinea mejor.

---

## 2. Ambigüedades peligrosas

### 2.1 Qué significa exactamente `cerrado`

Aparece en varios archivos:
- motor cerrado;
- etapa cerrada;
- arquitectura cerrada;
- documentación cerrada.

Pero no hay una distinción formal entre:
- `closed for current stage`;
- `closed for implementation`;
- `closed for integration`;
- `closed as stable reference`.

Esto es peligroso para automatización porque una herramienta podría interpretar `closed` como absoluto cuando aquí parece ser contextual.

### 2.2 Qué cuenta exactamente como `motor`

En `master_context.md` y `framework_manifest.md` está bien descrito conceptualmente, pero falta una regla operacional clara para distinguir entre:
- motor;
- submódulo;
- componente interno;
- artefacto;
- workflow interno.

Eso es peligroso porque Codex o Claude podrían empezar a tratar cualquier pieza auxiliar como motor independiente.

### 2.3 Profundidad obligatoria de documentación por motor

Se dice que todos los motores deben pasar por:
- documentación base;
- schema;
- tests;
- failure modes;
- implementación;
- revisión.

Pero también se dice que sigue ambiguo si todos los motores usarán el mismo nivel de profundidad documental o si algunos tendrán flujo abreviado.

Esta ambigüedad es peligrosa porque rompe la uniformidad del workflow justo donde quieres automatización.

### 2.4 Relación entre `tests` y `acceptance tests`

En algunos lugares `tests` es una etapa. En otros, `acceptance_tests` aparece como artefacto dentro de documentación base.

No está claro si:
- los `acceptance tests` se definen primero y luego se refinan en una etapa de tests;
- o si la etapa `tests` solo implementa lo ya documentado.

Eso puede bloquear la automatización de estados y transiciones.

### 2.5 Relación entre `failure_modes` como etapa y como artefacto

Mismo problema que el punto anterior:
- a veces aparece como entregable documental;
- a veces como etapa independiente.

### 2.6 Qué es exactamente `conformance review`

Aparece como etapa final y como artefacto (`conformance_review_report`), pero no está formalizado:
- quién la ejecuta;
- qué inputs consume;
- si depende del futuro `Evaluation / Conformance Engine`;
- o si es revisión manual asistida.

Para automatización futura, esto es importante.

### 2.7 Nivel de formalidad del `motor_schema.json`

No está claro si el JSON:
- es solo un esquema conceptual para tracking;
- o si debe actuar como contrato operativo real del estado por motor.

Si el sistema lo toma como fuente de verdad y no solo como guía, algunas ambigüedades actuales se vuelven bloqueantes.

---

## 3. Duplicidades

### 3.1 Repetición fuerte entre `master_context.md` y `framework_manifest.md`

`framework_manifest.md` no solo consolida: en varios tramos reescribe casi literalmente contenido de `master_context.md` y `workflow_rules.md`.

Eso no es malo en sí, pero sí crea riesgo de deriva futura: si cambias un archivo base, tendrás que sincronizar varios textos casi idénticos.

### 3.2 Repetición de principios técnicos y epistemológicos

Los mismos principios aparecen en:
- `master_context.md`;
- `quality_rules.md`;
- `framework_manifest.md`.

No hay contradicción, pero sí duplicidad de autoridad textual. No está claro cuál archivo manda si luego hay pequeñas diferencias.

### 3.3 Repetición del flujo por motor

La secuencia estándar:
1. documentación base
2. schema técnico
3. tests
4. failure modes
5. implementación
6. revisión de conformidad

aparece varias veces en varios archivos. Eso aumenta consistencia narrativa, pero también aumenta riesgo de divergencia si luego se ajusta la secuencia.

### 3.4 Repetición de antipatrones

Muchos antipatrones aparecen primero en `workflow_rules.md` y luego se repiten en `quality_rules.md` y `framework_manifest.md`.

---

## 4. Huecos importantes

### 4.1 Falta una jerarquía de autoridad documental

No está definido cuál archivo manda sobre cuál en caso de conflicto.

Ahora mismo parece implícitamente:
- `framework_manifest.md` como consolidado,

pero no está dicho formalmente.

Sin jerarquía, la automatización no sabe cuál usar como source of truth si hay divergencias.

### 4.2 Falta una definición explícita de estados válidos por etapa

`motor_schema.json` tiene:
- `current_stage`
- `completed_stages`
- `status`
- `blocked`
- `paused`
- `waiting_on`
- `closure`

Pero no está definido con claridad qué combinaciones son válidas o inválidas.

Ejemplo:
- ¿puede estar `status = closed` y `current_stage = implementation`?
- ¿puede estar `blocked = true` y `status = ready_for_next_stage`?

Ese hueco es serio para automatización.

### 4.3 Falta una distinción explícita entre `artefacto definido` y `artefacto implementado`

Hoy `artifacts` solo dice si existen e incluye `items`, pero no distingue entre:
- especificado;
- borrador;
- aprobado;
- implementado;
- validado.

Eso limita mucho la automatización futura.

### 4.4 Falta una definición operativa de `validación`

`motor_schema.json` tiene `validations`, pero no está conectado formalmente con:
- tests;
- revisión de conformidad;
- criterios mínimos de aceptación;
- `acceptance tests` documentales.

Hay campo, pero falta semántica fuerte.

### 4.5 Falta una definición de dependencia entre motores

Los archivos hablan mucho de no mezclar responsabilidades, pero no existe todavía un esquema mínimo consolidado para:
- dependencias entre motores;
- prerequisites por motor;
- orden obligatorio de activación.

Eso puede bloquear automatización posterior si quieres orquestar generación de archivos o código.

### 4.6 Falta una política de versionado documental

El proyecto insiste mucho en versionado de motores y trazabilidad del sistema, pero los archivos base no definen cómo se versionan ellos mismos ni cómo se actualizan sin romper coherencia.

### 4.7 Falta una regla clara para distinguir presente vs futuro

Varios archivos mezclan:
- lo ya decidido;
- lo previsto;
- lo probable;
- lo aún no cerrado.

Aunque usas etiquetas `Confirmado / Inferido / Pendiente`, todavía faltan reglas operativas para que una herramienta no tome un `inferido con alta confianza` como decisión cerrada.

---

## 5. Riesgos para automatización futura

### 5.1 Riesgo de usar múltiples archivos como autoridad concurrente

Si Claude o Codex consumen todos estos archivos a la vez sin jerarquía clara, pueden:
- mezclar contenido duplicado;
- tomar frases equivalentes como reglas separadas;
- o priorizar una formulación menos precisa.

### 5.2 Riesgo de interpretar mal el workflow por conflicto etapa/artefacto

La ambigüedad entre:
- `tests` como etapa
- `acceptance_tests` como artefacto dentro de documentación base

y entre:
- `failure_modes` como etapa
- `failure_modes` como artefacto documental

puede romper automatización de seguimiento, generación de tareas o estados.

### 5.3 Riesgo de estados imposibles o inconsistentes en `motor_schema.json`

Como no están definidas las combinaciones válidas entre:
- `current_stage`,
- `status`,
- `blocked`,
- `paused`,
- `waiting_on`,
- `closure`,

un sistema podría producir estados incoherentes.

### 5.4 Riesgo de proliferación de motores por falta de criterio operativo duro

Aunque el principio general de `responsabilidad separable` está claro, no hay aún un criterio operacional suficientemente concreto para que una herramienta automática decida si algo:
- debe ser motor;
- submódulo;
- o artefacto interno.

### 5.5 Riesgo de cierre prematuro

Como `closed` no está suficientemente tipificado, una automatización podría considerar terminado un motor cuando solo terminó una etapa o cuando aún faltan validaciones sustantivas.

### 5.6 Riesgo de drift documental

Por duplicidad alta entre archivos, cualquier cambio manual posterior puede dejar:
- un archivo actualizado;
- otro semiactualizado;
- y otro obsoleto.

Eso es especialmente delicado si automatizas prompts o generación de código contra documentos distintos.

### 5.7 Riesgo de convertir `inferido con alta confianza` en regla obligatoria

Tus documentos separan etiquetas, pero no hay todavía una instrucción operativa tipo:
- `las herramientas solo deben tratar como binding lo marcado como Confirmado`.

Sin esa regla, la automatización puede cerrar ambigüedades por su cuenta.

---

## 6. Recomendaciones mínimas de ajuste, solo donde sea necesario

### 6.1 Definir jerarquía documental mínima

Necesitas dejar explícito cuál archivo es fuente de verdad principal.
Lo mínimo sería establecer si:
- `framework_manifest.md` consolida y manda;
- o si `master_context.md` + `workflow_rules.md` + `quality_rules.md` siguen siendo fuentes primarias y el manifiesto solo resume.

### 6.2 Resolver la tensión entre etapas y artefactos para tests/failure modes

Debes elegir una sola semántica estable:
- o `tests` y `failure_modes` son etapas separadas;
- o son subartefactos de documentación base y luego tienen refinamiento técnico.

Ahora mismo están en ambos niveles.

### 6.3 Tipificar mejor el estado por motor

Añadir una especificación breve de combinaciones válidas entre:
- `current_stage`
- `status`
- `blocked`
- `paused`
- `waiting_on`
- `closure`

No hace falta una base de datos completa; solo una semántica mínima.

### 6.4 Definir qué etiquetas son vinculantes para automatización

Necesitas una regla explícita:
- `Confirmado` = binding
- `Inferido con alta confianza` = usable con cautela
- `Pendiente o ambiguo` = no cerrable automáticamente

### 6.5 Reducir duplicidad de autoridad

No hace falta borrar contenido, pero sí conviene que uno de los archivos deje de repetir tanto y pase a referenciar más claramente a los demás.

### 6.6 Definir mejor qué significa `cerrado`

Mínimo distinguir entre:
- etapa cerrada;
- motor cerrado para implementación;
- motor cerrado para integración.

Sin eso, el tracking y la automatización seguirán siendo frágiles.
