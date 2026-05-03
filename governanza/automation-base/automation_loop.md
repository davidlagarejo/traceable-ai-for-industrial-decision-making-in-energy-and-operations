# automation_loop.md

## 1. Objetivo del loop de automatización

### Confirmado
El loop de automatización debe documentar el ciclo mínimo necesario para construir motores de forma repetible, trazable y controlada, usando los archivos base ya definidos y sin depender de memoria conversacional implícita.

Debe permitir, como mínimo:
- leer el estado actual de los motores;
- decidir qué motor puede avanzar;
- saber qué etapa sigue;
- saber qué artefactos necesita para avanzar;
- saber cuándo detenerse;
- saber cuándo pedir intervención humana;
- y actualizar estado sin perder trazabilidad.

Este loop no diseña todavía un sistema distribuido complejo ni la ejecución runtime del sistema final.

### Inferido con alta confianza
El loop funciona como capa de construcción disciplinada sobre los artefactos base, no como sustituto de la arquitectura ya documentada.

### Pendiente o ambiguo
No está definido todavía si este loop se implementará luego como script único, conjunto de scripts, workflow asistido o sistema más formal de orquestación.

---

## 2. Unidad mínima de trabajo

### Confirmado
La unidad mínima de trabajo es un motor tratado como unidad separada de arquitectura, observado en su etapa actual dentro del workflow.

Operativamente, una iteración del loop debe trabajar sobre:
- un motor identificado;
- su estado actual;
- su etapa actual o siguiente etapa posible;
- los artefactos requeridos para esa transición.

### Inferido con alta confianza
La iteración mínima razonable del loop es: un motor, una decisión de avance o detención, y una actualización explícita de estado.

### Pendiente o ambiguo
No está definido todavía si el loop podrá procesar varios motores en paralelo o si debe operar siempre uno por vez.

---

## 3. Archivos base que el loop debe consultar

### Confirmado
El loop debe consultar, como mínimo, estos archivos base del proyecto:
- `master_context.md`
- `workflow_rules.md`
- `quality_rules.md`
- `framework_manifest.md`
- `consistency_audit.md`
- `motor_registry.md`
- `document_authority.md`
- `stage_artifact_semantics.md`
- `motor_state_semantics.md`
- `artifact_layout.md`
- `motor_schema.json`

### Inferido con alta confianza
La consulta mínima correcta separa:
- contexto general y límites del sistema;
- reglas del workflow;
- reglas de calidad;
- catálogo actual de motores;
- semántica de autoridad documental;
- semántica etapa/artefacto;
- semántica de estado del motor;
- layout mínimo de artefactos;
- y estado operativo del motor.

### Confirmado
La jerarquía mínima de autoridad entre estos archivos queda definida por `document_authority.md`.

### Pendiente o ambiguo
No está definido todavía si esta jerarquía se validará automáticamente antes de cada iteración.

---

## 4. Secuencia mínima del loop

### Confirmado
La secuencia mínima útil del loop es:

1. Leer el catálogo de motores y el estado disponible del motor.
2. Identificar el motor sobre el que se va a trabajar.
3. Leer su `current_stage`, `completed_stages`, `artifacts`, `missing_artifacts`, `validations`, `corrections`, `status`, `blocked`, `paused`, `waiting_on` y `closure`.
4. Distinguir entre el `status` catalogal de `motor_registry.md` y el `status` operativo de `motor_schema.json`.
5. Verificar qué exige el workflow para la etapa actual y la siguiente transición posible.
6. Verificar qué artefactos mínimos existen y cuáles faltan.
7. Determinar si el motor puede avanzar, debe esperar, debe pausar o debe abrir un bucle de corrección.
8. Producir o actualizar los artefactos correspondientes a la iteración actual.
9. Registrar validaciones, correcciones, faltantes y estado actualizado en `motor_schema.json`.
10. Detenerse o continuar según el resultado de la iteración.

### Inferido con alta confianza
La secuencia correcta es de lectura, chequeo, producción controlada y actualización explícita de estado. No debe saltar directamente de contexto a código sin pasar por verificación de etapa y artefactos.

### Pendiente o ambiguo
No está definido todavía si cada iteración debe producir exactamente un artefacto, cerrar una etapa completa o permitir avances más finos dentro de una misma etapa.

---

## 5. Decisiones que el loop sí puede tomar

### Confirmado
El loop sí puede tomar, como mínimo, estas decisiones:
- identificar qué motor del catálogo está siendo evaluado;
- leer el estado actual del motor;
- identificar la etapa actual y la siguiente etapa del workflow;
- verificar si existen los artefactos mínimos requeridos para avanzar;
- registrar artefactos faltantes;
- registrar validaciones ejecutadas;
- registrar correcciones abiertas o resueltas;
- actualizar estado, bloqueo, pausa, espera y cierre según el resultado de la iteración.

### Inferido con alta confianza
Si no hay ambigüedad material y las precondiciones están satisfechas, el loop puede avanzar automáticamente a la siguiente etapa lógica del workflow.

También puede:
- abrir un bucle de corrección cuando se detecta una inconsistencia objetiva ya tipificada por el workflow;
- detener el avance automático cuando detecta conflicto documental, faltantes críticos o ambigüedad no resuelta.

### Confirmado
El significado mínimo de `closed` y sus combinaciones válidas quedan fijados por `motor_state_semantics.md`.

### Pendiente o ambiguo
No está completamente formalizado si, además de cumplir esa semántica mínima, algunos cierres requerirán confirmación humana adicional.

---

## 6. Decisiones que el loop no debe tomar

### Confirmado
El loop no debe:
- crear motores nuevos fuera del catálogo actual;
- redefinir fases, metodología o epistemología;
- inventar etapas, estados o artefactos no definidos;
- tratar prompts de implementación como sustituto de arquitectura cerrada;
- usar IA como sustituto de contratos, versionado, lineage, normalización determinista, identity resolution final, quality gating final o gobernanza;
- mezclar responsabilidades de varios motores en uno;
- corregir silenciosamente artefactos o estados;
- cerrar automáticamente ambigüedades todavía abiertas.

### Inferido con alta confianza
Tampoco debe:
- resolver por su cuenta conflictos de autoridad entre archivos base;
- convertir `Inferido con alta confianza` en regla obligatoria;
- ni tratar `Pendiente o ambiguo` como decisión cerrada.

### Pendiente o ambiguo
No está formalizado todavía si el loop podrá proponer motores recomendados como candidatos a promoción futura o si eso deberá quedar siempre fuera de su alcance.

---

## 7. Condiciones para avanzar de etapa

### Confirmado
Las condiciones mínimas ya respaldadas para avanzar son estas:

### 7.1 De `documentation_base` a `schema_technical`
Solo cuando ya están definidos:
- propósito;
- límites;
- contrato funcional;
- objetos mínimos;
- reglas de validación;
- acceptance tests;
- failure modes.

### 7.2 De `schema_technical` a `tests` y `failure_modes`
Solo cuando ya existe una representación técnica suficientemente clara de:
- entidades;
- campos;
- relaciones;
- metadatos obligatorios.

### 7.3 De `tests` y `failure_modes` a `implementation`
Solo cuando:
- el contrato ya no está ambiguo;
- el schema técnico está cerrado;
- los tests mínimos ya están definidos;
- y los failure modes principales están explícitos.

### 7.4 De `implementation` a `conformance_review`
Solo cuando ya existe:
- código del motor;
- tests mínimos;
- ejemplo de uso;
- y una estructura suficientemente clara para revisar cumplimiento.

### Inferido con alta confianza
Antes de cualquier avance de etapa, el loop debería verificar además que el motor no esté en estado de bloqueo, pausa o espera activa.

### Pendiente o ambiguo
No está definido todavía si el avance entre etapas requerirá gates automatizados obligatorios o si parte de la transición seguirá siendo manual.

---

## 8. Condiciones para pausar, bloquear o esperar

### Confirmado
El estado mínimo del motor ya contempla:
- `blocked`
- `paused`
- `waiting_on`

Por tanto, el loop debe ser capaz de registrar y respetar estas condiciones.

### Inferido con alta confianza
El loop debe frenar el avance automático cuando ocurra cualquiera de estas situaciones:
- el motor ya está marcado como `blocked`;
- el motor ya está marcado como `paused`;
- `waiting_on` contiene una dependencia o espera no resuelta;
- faltan artefactos mínimos para la etapa siguiente;
- existe una ambigüedad documental material no resuelta;
- existe un conflicto entre archivos base que el loop no puede cerrar responsablemente.

### Confirmado
La semántica mínima de `blocked`, `paused`, `waiting_on`, `status` y `closure` queda fijada por `motor_state_semantics.md`.

### Pendiente o ambiguo
No está completamente tipificada todavía la política de uso fino de esos estados en automatizaciones más complejas o paralelas.

---

## 9. Condiciones para abrir un bucle de corrección

### Confirmado
Los bucles de corrección permitidos actualmente son estos:

1. De `schema_technical` hacia `documentation_base`  
   Solo si el schema revela una ambigüedad real no resuelta en el contrato o en los objetos mínimos.

2. De `tests` hacia `schema_technical`  
   Solo si los tests descubren que falta estructura mínima para validar el motor correctamente.

3. De `implementation` hacia `schema_technical` o `tests`  
   Solo si el código revela una inconsistencia objetiva con el diseño ya aprobado.

4. De `conformance_review` hacia `implementation`  
   Para corregir desviaciones del contrato, mezcla de responsabilidades o pérdida de metadatos críticos.

### Inferido con alta confianza
El loop debe abrir corrección solo cuando hay inconsistencia objetiva, no por hallazgos menores ni como excusa para reabrir el motor completo.

Debe registrar esas correcciones en `corrections`, incluyendo al menos:
- etapa de origen;
- etapa de destino;
- razón;
- y estado de resolución.

### Pendiente o ambiguo
No está definido todavía el umbral formal entre `corrección menor` y `cambio estructural`.

---

## 10. Condiciones para considerar cerrado un motor

### Confirmado
Un motor se considera cerrado cuando:
- su documentación base está cerrada;
- su schema técnico está cerrado;
- sus tests mínimos existen;
- sus failure modes están documentados;
- su implementación existe;
- su revisión de conformidad no muestra violaciones materiales;
- y el motor ya puede existir como unidad separada sin depender de reinterpretaciones continuas.

### Inferido con alta confianza
El loop debería usar este criterio de cierre de forma conservadora, y no considerar cerrado un motor si todavía mantiene contradicciones materiales, faltantes críticos o correcciones estructurales abiertas.

### Confirmado
`closed` ya queda tipificado como cierre del motor en el workflow mínimo, según `motor_state_semantics.md`.

### Pendiente o ambiguo
Siguen abiertos, fuera del estado serializable mínimo, los usos descriptivos más finos como cierre para implementación o cierre para integración.

---

## 11. Actualización de estado y trazabilidad

### Confirmado
La actualización mínima de estado del motor debe pasar por `motor_schema.json` y contemplar, como mínimo:
- `current_stage`
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

También ya está definido que:
- `validations` registra validaciones o checks ya ejecutados;
- `corrections` registra bucles de corrección aplicados;
- `closure` registra si el motor está cerrado y bajo qué condición mínima.

### Inferido con alta confianza
En cada iteración, el loop debería dejar explícito:
- qué artefactos existen;
- cuáles faltan;
- qué validaciones se corrieron;
- si hubo corrección;
- y cuál es el nuevo estado operativo del motor.

La actualización debe ser explícita y trazable. No debe haber silent mutation del estado ni de los artefactos del motor.

### Pendiente o ambiguo
No está definida todavía una política formal de versionado documental para estos archivos base ni para el propio estado del motor.

---

## 12. Qué debe evitarse en la automatización

### Confirmado
Debe evitarse:
- empezar por código;
- mezclar fases con motores;
- usar IA como sustituto de arquitectura explícita;
- redefinir el motor durante la implementación;
- mezclar responsabilidades de varios motores en uno;
- corregir silenciosamente contratos o metadatos;
- introducir features por si acaso;
- hacer sobre-ingeniería ornamental;
- producir documentación vaga;
- saltarse tests o failure modes;
- confundir un output funcional con un motor correctamente diseñado;
- usar narrativa o conveniencia como sustituto de trazabilidad y límites.

### Inferido con alta confianza
También debe evitarse:
- usar múltiples archivos como autoridad concurrente sin criterio de prioridad;
- avanzar de etapa con conflicto no resuelto entre artefacto y etapa;
- dejar que el loop trate `Inferido con alta confianza` como binding;
- mezclar automatización de construcción con ejecución runtime del sistema final.

### Pendiente o ambiguo
No existe todavía una política cerrada para resolver automáticamente conflictos documentales ni estados incoherentes cuando aparezcan durante la automatización.

---

## 13. Qué partes siguen abiertas o ambiguas

### Confirmado
Siguen abiertas o ambiguas, y no deben cerrarse automáticamente, estas partes del loop:
- formalización exacta de `conformance_review` como proceso;
- criterio operativo exacto para distinguir motor, submódulo, componente interno o artefacto;
- dependencias formales entre motores;
- gates automáticos exactos entre etapas;
- validación automática formal del propio estado serializado.

### Inferido con alta confianza
El loop mínimo ya puede organizar construcción disciplinada de motores, pero todavía no puede convertirse en automatización totalmente autónoma y segura sin cerrar mejor autoridad documental, semántica de estados y relación etapa/artefacto.

### Pendiente o ambiguo
No está definido todavía si el siguiente ajuste deberá concentrarse en:
- la jerarquía documental;
- la semántica de estado en `motor_schema.json`;
- la semántica de cierre;
- o la relación entre artefactos documentales y etapas del workflow.
