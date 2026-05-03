# artifact_layout.md

## 1. Objetivo del layout de artefactos

### Confirmado
Este layout existe para definir la estructura mínima de artefactos necesaria para automatizar la construcción de motores sin perder orden, trazabilidad ni contexto.

Debe permitir que una herramienta sepa, como mínimo:
- qué artefactos existen por motor;
- qué tipo de artefactos produce cada etapa;
- cómo se relacionan esos artefactos;
- cuáles son obligatorios para avanzar;
- y cómo seguir el estado de un motor sin depender de memoria conversacional implícita.

No diseña todavía un repositorio final complejo. Solo fija la organización mínima útil ya respaldada por los archivos base actuales.

### Inferido con alta confianza
El layout debe servir como puente entre documentación, tracking de estado y futura implementación automatizada.

### Pendiente o ambiguo
No está definido todavía el formato final exacto de carpetas, nombres de archivos o repositorios por motor.

---

## 2. Principios de organización

### Confirmado
- La organización de artefactos debe seguir el workflow por motor.
- La documentación base precede al código.
- El schema técnico deriva de la documentación base.
- Los tests y failure modes forman parte del flujo antes de implementación.
- La implementación no debe reinterpretar lo ya cerrado en documentación.
- La revisión de conformidad ocurre después del código.
- Deben preservarse trazabilidad, versionado, lineage y posibilidad de reconstrucción.
- No debe haber desorden entre definición, schema, tests, código y revisión.

### Inferido con alta confianza
- La agrupación correcta es primero lógica por etapa, no necesariamente física por carpetas definitivas.
- Un layout útil para automatización debe separar artefactos de contenido del motor de artefactos de seguimiento del estado.

### Pendiente o ambiguo
- No está cerrada una jerarquía documental formal entre todos los archivos base del proyecto.
- No está cerrado si todos los motores usarán exactamente la misma profundidad documental o si algunos tendrán flujo abreviado.

---

## 3. Artefactos mínimos por motor

### Confirmado
Los artefactos mínimos actualmente respaldados por el contexto son estos.

### 3.1 Documentación base
- `master_concept_doc`
- `functional_contract`
- `conceptual_schema`
- `operational_rules`
- `acceptance_tests`
- `failure_modes`
- `design_done_criteria`

### 3.2 Schema técnico
- `technical_schema`

### 3.3 Tests
- `test_spec`

### 3.4 Failure modes
- `failure_modes_spec`

### 3.5 Implementación
- `codebase`
- `usage_example`

### 3.6 Revisión de conformidad
- `conformance_review_report`

### Inferido con alta confianza
Estos son artefactos mínimos por motor. No constituyen todavía un diseño final de nombres físicos ni de árbol de carpetas definitivo.

### Inferido con alta confianza
La semántica mínima entre `acceptance_tests` y `test_spec`, y entre `failure_modes` y `failure_modes_spec`, queda fijada por `stage_artifact_semantics.md`.

### Pendiente o ambiguo
No está definido todavía si esos refinamientos tendrán siempre el mismo nivel de formalidad en todos los motores.

---

## 4. Agrupación lógica de artefactos

### Confirmado
La agrupación lógica mínima que ya está justificada es esta:

### 4.1 Artefactos de referencia del proyecto
Son artefactos de contexto general, no artefactos mínimos de un motor individual:
- `master_context.md`
- `workflow_rules.md`
- `quality_rules.md`
- `framework_manifest.md`
- `consistency_audit.md`
- `motor_registry.md`
- `document_authority.md`
- `stage_artifact_semantics.md`
- `motor_state_semantics.md`
- `motor_schema.json`

### 4.2 Artefactos propios de cada motor por etapa
Son los artefactos listados en la sección anterior y se agrupan por:
- documentación base;
- schema técnico;
- tests;
- failure modes;
- implementación;
- revisión de conformidad.

### 4.3 Artefactos de seguimiento de estado
El seguimiento del avance de un motor se expresa mediante los campos de `motor_schema.json`, especialmente:
- `current_stage`
- `completed_stages`
- `artifacts`
- `missing_artifacts`
- `validations`
- `corrections`
- `status`
- `closure`

### Inferido con alta confianza
La agrupación correcta para automatización es separar:
- referencias maestras del proyecto;
- artefactos propios del motor;
- y tracking de estado del motor.

### Pendiente o ambiguo
No está definido todavía si esta agrupación lógica se convertirá después en carpetas físicas fijas o en otro tipo de layout operativo.

---

## 5. Relación entre artefactos y etapas del workflow

### Confirmado
La relación mínima entre etapas y artefactos es esta:

1. `documentation_base`  
   Produce los artefactos conceptuales mínimos del motor y debe existir antes de pasar a `schema_technical`.

2. `schema_technical`  
   Produce `technical_schema` y solo debe empezar cuando ya existen propósito, límites, contrato funcional, objetos mínimos, reglas de validación, acceptance tests y failure modes documentales.

3. `tests`  
   Produce `test_spec` y se apoya en una representación técnica ya suficientemente clara.

4. `failure_modes`  
   Produce `failure_modes_spec` y se apoya también en una representación técnica ya suficientemente clara.

5. `implementation`  
   Produce como mínimo `codebase` y `usage_example`, y solo debe empezar cuando contrato, schema técnico, tests mínimos y failure modes principales ya están explícitos.

6. `conformance_review`  
   Produce `conformance_review_report` y solo debe empezar cuando ya existe código, tests mínimos y una estructura suficientemente clara para revisar cumplimiento.

### Inferido con alta confianza
La automatización debería tratar estas relaciones como precedencias mínimas entre tipos de artefacto, no como pipeline físico ya cerrado.

### Pendiente o ambiguo
- No está definido todavía si todos los motores exigirán el mismo nivel de detalle en esos refinamientos.
- No está definido todavía si habrá gates automatizados obligatorios entre etapas.

---

## 6. Artefactos fuente de verdad vs artefactos derivados

### Confirmado
A nivel de un motor, lo más sólido hoy es esto:
- la documentación base funciona como autoridad de implementación;
- el schema técnico deriva de la documentación base;
- la implementación debe obedecer lo ya cerrado en documentación y schema;
- la revisión de conformidad verifica el resultado de la implementación.

Por tanto, para cada motor:
- `master_concept_doc`, `functional_contract`, `conceptual_schema`, `operational_rules`, `acceptance_tests`, `failure_modes` y `design_done_criteria` actúan como base de definición;
- `technical_schema` deriva de esa base;
- `test_spec` y `failure_modes_spec` refinan validación previa al código;
- `codebase` y `usage_example` son derivados implementados;
- `conformance_review_report` es derivado de revisión.

### Inferido con alta confianza
- `motor_schema.json` no reemplaza estos artefactos; describe estado y existencia de artefactos.
- `validations`, `missing_artifacts`, `corrections`, `status` y `closure` son metadatos de seguimiento, no artefactos maestros de contenido.

### Confirmado
La jerarquía mínima de autoridad documental queda formalizada en `document_authority.md`.

### Pendiente o ambiguo
No está definido todavía si aparecerán después nuevos documentos con autoridad superior sobre áreas específicas.

---

## 7. Artefactos obligatorios vs opcionales

### Confirmado
Para un motor, los artefactos mínimos listados por etapa deben tratarse como obligatorios si el motor quiere avanzar correctamente por el workflow.

Eso incluye:
- todos los artefactos mínimos de documentación base;
- `technical_schema`;
- `test_spec`;
- `failure_modes_spec`;
- `codebase`;
- `usage_example`;
- `conformance_review_report`.

### Inferido con alta confianza
- Los archivos de contexto general del proyecto son necesarios para automatización del sistema, pero no son artefactos obligatorios de cada motor individual.
- `consistency_audit.md` actúa como artefacto útil de diagnóstico, pero no está respaldado como requisito mínimo por motor.

### Pendiente o ambiguo
- No existe todavía una lista formal cerrada de artefactos opcionales por motor.
- Tampoco existe una semántica formal cerrada para distinguir `artefacto definido`, `artefacto en borrador`, `artefacto aprobado` o `artefacto validado`.

---

## 8. Relación con el estado del motor (`motor_schema.json`)

### Confirmado
`motor_schema.json` modela el estado mínimo del motor y debe permitir, como mínimo:
- identificar el motor;
- saber en qué etapa está;
- saber qué etapas ya completó;
- saber qué artefactos existen;
- saber cuáles faltan;
- registrar validaciones;
- registrar correcciones;
- registrar estado general;
- registrar bloqueo, pausa o espera;
- registrar cierre del motor.

Los campos ya respaldados para eso son:
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

### Inferido con alta confianza
La relación correcta entre layout de artefactos y `motor_schema.json` es:
- los artefactos viven fuera del estado;
- `motor_schema.json` describe su existencia, faltantes y avance;
- y debe servir como tracking operativo del motor, no como sustituto del contenido de los artefactos.

### Confirmado
La semántica mínima de `motor_schema.json` como tracking operativo y las combinaciones mínimas válidas de estado quedan fijadas por `motor_state_semantics.md`.

### Pendiente o ambiguo
No está definido todavía si después existirá una validación automática formal de ese esquema de estado.

---

## 9. Qué debe evitarse en la organización

### Confirmado
Debe evitarse:
- mezclar artefactos de distintas etapas sin distinguir su función;
- usar tracking de estado como sustituto del contenido real del motor;
- tratar prompts de implementación como si fueran artefactos maestros;
- saltarse artifacts mínimos antes de pasar de etapa;
- perder trazabilidad entre documentación, schema, tests, código y revisión;
- corregir silenciosamente artefactos sin dejar rastro;
- mezclar responsabilidades de varios motores en el mismo paquete documental;
- asumir un árbol final de carpetas no cerrado todavía.

### Inferido con alta confianza
También debe evitarse:
- duplicar autoridad textual innecesariamente entre archivos;
- dejar que una herramienta automática infiera por su cuenta qué archivo manda sobre otro;
- y convertir `Inferido con alta confianza` en regla obligatoria de ejecución.

### Pendiente o ambiguo
No existe todavía una política cerrada para resolver automáticamente conflictos entre artefactos duplicados o desalineados.

---

## 10. Qué partes siguen abiertas o ambiguas

### Confirmado
Siguen abiertas o ambiguas, y no deben cerrarse automáticamente, las siguientes partes del layout:
- formato final exacto de carpetas y nombres de archivos;
- formalización exacta de `conformance_review` como proceso;
- distinción formal entre artefactos persistentes, derivados, transitorios o validados;
- política exacta de versionado documental de los propios artefactos.

### Inferido con alta confianza
El layout mínimo ya permite organizar artefactos de forma disciplinada, pero todavía no alcanza para automatización completamente autónoma sin reglas adicionales de autoridad, estado y transición.

### Pendiente o ambiguo
No está definido todavía si el siguiente ajuste deberá hacerse en:
- `framework_manifest.md`;
- `motor_schema.json`;
- un archivo específico de autoridad documental;
- o un archivo específico de semántica operativa de estados.
