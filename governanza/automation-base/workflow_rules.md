# Workflow Rules

## 1. Definición operativa del flujo por motor

### Confirmado

El trabajo por motor sigue un flujo secuencial y disciplinado. Cada motor se trata como una unidad separada de arquitectura, con límites claros, documentación previa y posterior implementación controlada.

Un motor no nace en código. Nace como una definición arquitectónica y documental. Solo después de cerrar esa base pasa a schema técnico, tests, implementación y revisión.

El flujo por motor existe para evitar:
- mezclar responsabilidades;
- improvisar arquitectura durante el código;
- usar IA como sustituto de contratos explícitos;
- y generar retrabajo estructural.

### Inferido con alta confianza

El flujo por motor está pensado para que Claude, Codex u otra herramienta puedan intervenir después sin rediseñar el motor en cada etapa.

### Pendiente o ambiguo

No está definido todavía si todos los motores usarán exactamente el mismo nivel de profundidad documental o si algunos motores menores tendrán un flujo abreviado.

---

## 2. Secuencia estándar de etapas

### Confirmado

La secuencia estándar de trabajo por motor es:
1. Documentación base
2. Schema técnico
3. Tests
4. Failure modes
5. Implementación
6. Revisión de conformidad

Esta secuencia ya fue explicitada varias veces como el orden correcto de trabajo.

### Inferido con alta confianza

La documentación base funciona como autoridad de implementación. El schema técnico deriva de ella. Los tests y failure modes refinan límites antes del código. La implementación no debe reinterpretar lo ya cerrado. La revisión de conformidad verifica que el motor implementado respeta su contrato.

### Pendiente o ambiguo

No está completamente fijado si en algunos casos los tests y failure modes se documentarán en archivos separados o juntos dentro de la misma etapa documental.

---

## 3. Objetivo de cada etapa

### Confirmado

### 3.1 Documentación base

Definir qué es el motor, qué hace, qué no hace, qué entra, qué sale, qué objetos mínimos necesita, cómo se valida y qué errores deben bloquearse.

### 3.2 Schema técnico

Traducir la documentación base a una estructura técnica concreta: entidades, objetos, campos, relaciones, versionado, lineage y persistencia conceptual.

### 3.3 Tests

Definir cómo se valida que el motor cumple su función mínima y cómo se detectan errores, casos sparse, malformed input y edge cases.

### 3.4 Failure modes

Definir cómo puede degradarse el motor, qué anti-patterns lo dañan, qué errores serían costosos de corregir después y qué señales indican monolitización o exceso de responsabilidad.

### 3.5 Implementación

Construir el núcleo de código del motor respetando exactamente la documentación base, el schema técnico y los límites ya definidos.

### 3.6 Revisión de conformidad

Verificar que la implementación:
- respeta el contrato;
- no mezcla responsabilidades;
- preserva metadatos críticos;
- y no excede el rol del motor.

### Inferido con alta confianza

La intención no es solo producir código funcional, sino producir motores correctos, mantenibles, trazables y listos para escalar.

### Pendiente o ambiguo

No está definido todavía un protocolo universal de benchmarking de performance o rendimiento para todos los motores.

---

## 4. Artefactos esperados por etapa

### Confirmado

### 4.1 Documentación base

Debe producir, como mínimo:
- documento maestro conceptual;
- contrato funcional;
- modelo de objetos / schema conceptual;
- reglas operativas y de validación;
- acceptance tests;
- failure modes y anti-patterns;
- criterio de terminado del diseño conceptual.

### 4.2 Schema técnico

Debe producir, como mínimo:
- estructura de entidades u objetos;
- campos mínimos;
- tipos;
- relaciones;
- claves o identificadores estables;
- campos de versionado;
- campos de lineage/provenance;
- separación entre objeto vigente, historial y derivados.

### 4.3 Tests

Debe producir, como mínimo:
- happy path;
- sparse case;
- malformed input;
- missing provenance;
- duplicate/conflicting input si aplica;
- backward compatibility si aplica;
- edge cases críticos;
- criterio observable de PASS / WARNING / FAIL.

### 4.4 Failure modes

Debe producir, como mínimo:
- lista de failure modes principales;
- anti-patterns arquitectónicos;
- errores caros de corregir después;
- señales de degradación o monolitización.

### 4.5 Implementación

Debe producir, como mínimo:
- estructura de archivos;
- entidades/modelos;
- validadores;
- lógica principal del motor;
- errores estructurados;
- tests mínimos ejecutables;
- ejemplo mínimo de uso;
- checklist de conformidad.

### 4.6 Revisión de conformidad

Debe producir, como mínimo:
- validación contra contrato;
- verificación de límites;
- revisión de metadatos críticos;
- confirmación de separación de responsabilidades;
- identificación de desviaciones si existen.

### Inferido con alta confianza

Estos artefactos se están usando como base para luego automatizar con prompts, Codex o Claude sin rediseño adicional.

### Pendiente o ambiguo

No está fijado todavía el formato final exacto de carpetas o nombres de archivos para todos los artefactos.

---

## 5. Reglas de transición entre etapas

### Confirmado

### 5.1 De documentación base a schema técnico

Solo se pasa cuando el motor ya tiene definidos:
- propósito;
- límites;
- contrato funcional;
- objetos mínimos;
- reglas de validación;
- acceptance tests;
- failure modes.

### 5.2 De schema técnico a tests / failure modes finales

Solo se pasa cuando ya existe una representación técnica suficientemente clara de entidades, campos, relaciones y metadatos obligatorios.

### 5.3 De tests y failure modes a implementación

Solo se pasa cuando:
- el contrato ya no está ambiguo;
- el schema técnico está cerrado;
- los tests mínimos ya están definidos;
- y los failure modes principales están explícitos.

### 5.4 De implementación a revisión de conformidad

Solo se pasa cuando ya existe:
- código del motor;
- tests mínimos;
- ejemplo de uso;
- y una estructura suficientemente clara para revisar cumplimiento.

### Inferido con alta confianza

El objetivo de estas transiciones es impedir que el código se convierta en un espacio de rediseño.

### Pendiente o ambiguo

No está definido todavía si habrá gates automatizados obligatorios entre etapas o si parte de la transición seguirá siendo manual.

---

## 6. Criterios de cierre de etapa

### Confirmado

### 6.1 Cierre de documentación base

La documentación base se considera cerrada cuando:
- el motor está definido con claridad;
- sus límites están explícitos;
- no quedan ambiguos inputs/outputs principales;
- se conocen sus objetos mínimos;
- y está listo para pasar a schema técnico.

### 6.2 Cierre de schema técnico

El schema técnico se considera cerrado cuando:
- entidades u objetos están definidos;
- campos mínimos están cerrados;
- relaciones y versionado están definidos;
- y el motor ya puede ser testeado sin inventar estructura.

### 6.3 Cierre de tests

La etapa de tests se considera cerrada cuando:
- están cubiertos los casos mínimos exigidos;
- los criterios observables de éxito y fallo son claros;
- y los edge cases críticos del motor están explícitos.

### 6.4 Cierre de failure modes

La etapa se considera cerrada cuando:
- ya se conocen los modos principales de degradación;
- ya están listados los anti-patterns;
- y ya están marcados los errores de arquitectura más caros de corregir.

### 6.5 Cierre de implementación

La implementación se considera cerrada cuando:
- respeta el contrato;
- respeta límites;
- preserva metadatos críticos;
- y existe una base mínima usable del motor.

### 6.6 Cierre de revisión de conformidad

La revisión se considera cerrada cuando:
- no hay violaciones materiales del contrato;
- no hay mezcla grave de responsabilidades;
- no hay pérdida de trazabilidad o lineage esenciales;
- y el motor puede considerarse listo para integrarse o pasar al siguiente.

### Inferido con alta confianza

El cierre no depende de volumen de código, sino de conformidad arquitectónica y utilidad real.

### Pendiente o ambiguo

No está fijado todavía un formato único de acta de cierre por etapa.

---

## 7. Criterios de cierre de motor

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

El cierre de un motor no implica que quede congelado para siempre, pero sí que queda suficientemente definido e implementado como para no tener que rehacerse estructuralmente al siguiente paso.

### Pendiente o ambiguo

No está definido todavía si el cierre final de un motor requerirá integración obligatoria con otros motores antes de declararlo listo.

---

## 8. Posibles bucles de corrección

### Confirmado

El flujo admite correcciones, pero no debe convertirse en un ciclo caótico de rediseño permanente.

Los bucles de corrección esperados son:
1. De schema técnico hacia documentación base  
   Solo si el schema revela una ambigüedad real no resuelta en el contrato o en los objetos mínimos.
2. De tests hacia schema técnico  
   Solo si los tests descubren que falta estructura mínima para validar el motor correctamente.
3. De implementación hacia schema técnico o tests  
   Solo si el código revela una inconsistencia objetiva con el diseño ya aprobado.
4. De revisión de conformidad hacia implementación  
   Para corregir desviaciones del contrato, mezcla de responsabilidades o pérdida de metadatos críticos.

### Inferido con alta confianza

La corrección debe ser localizada y controlada. No debe usarse cada hallazgo menor como excusa para reabrir el motor completo.

### Pendiente o ambiguo

No está definido todavía cuándo una corrección amerita reabrir documentación base completa versus solo una sección.

---

## 9. Qué debe evitarse en el flujo

### Confirmado

Durante el flujo de un motor debe evitarse:
- empezar por código;
- mezclar fases con motores;
- usar IA como sustituto de arquitectura explícita;
- redefinir el motor durante la implementación;
- mezclar responsabilidades de varios motores en uno;
- corregir silenciosamente contratos o metadatos;
- introducir features "por si acaso";
- hacer sobre-ingeniería ornamental;
- producir documentación vaga;
- asumir que prompts de implementación equivalen a arquitectura cerrada;
- saltarse tests o failure modes;
- confundir un output funcional con un motor correctamente diseñado;
- usar narrativa o conveniencia como sustituto de trazabilidad y límites.

### Inferido con alta confianza

También debe evitarse tratar el MVP como permiso para construir motores mediocres o irreparables.

### Pendiente o ambiguo

No está fijado todavía qué grado de refactor se tolerará por motor una vez declarado cerrado.

---

## 10. Qué partes están confirmadas y cuáles siguen ambiguas

### Confirmado

Está confirmado que:
- cada motor sigue un flujo por etapas;
- la documentación base ocurre antes del código;
- el schema técnico ocurre antes de implementación;
- los tests y failure modes forman parte del flujo;
- existe revisión de conformidad después del código;
- el objetivo es evitar caos, mezcla de responsabilidades e improvisación.

También está confirmado que la secuencia estándar por motor es:
1. Documentación base
2. Schema técnico
3. Tests
4. Failure modes
5. Implementación
6. Revisión de conformidad

### Inferido con alta confianza

Está altamente respaldado que este flujo se está usando como base para automatización posterior con herramientas externas.

### Pendiente o ambiguo

Siguen ambiguos:
- el formato exacto final de todos los archivos por etapa;
- si todos los motores tendrán exactamente el mismo número de artefactos;
- qué gates automáticos existirán entre etapas;
- y el protocolo exacto de cierre final cuando varios motores ya estén integrados.

---

## 11. Regla de consulta de madurez de variable

### Confirmado

Todo output que pretenda producir:

- claims numéricos,
- claims financieros,
- claims regulatorios,
- claims de ahorro,
- superficies de ROI,
- posture de cumplimiento,
- o decisiones TAD de alto peso,

debe consultar primero un `variable_maturity_register` o su equivalente contractual.

Esto implica:

1. Ningún motor downstream puede emitir un claim fuerte si la variable requerida no tiene madurez suficiente.
2. La madurez de variable debe consultarse antes de componer prose, charts, tables o decision fronts.
3. Variables derivadas deben consultar el cuello de botella de sus dependencias antes de subir de fuerza semántica.
4. Si un output no puede reconstruir qué variable lo habilita, ese output no está listo para publicación fuerte.

### Inferido con alta confianza

- La secuencia correcta pasa a ser:
  - scraping / source routing,
  - source classification,
  - entity resolution,
  - variable extraction,
  - evidence maturity assignment,
  - claim permission,
  - decisión / reporte.
- Esto vuelve explícito que reporting y TAD no son espacios para reinterpretar soporte, solo para materializarlo.

### Pendiente o ambiguo

- No está fijado todavía el nombre final del motor transversal que ejecutará esta regla, aunque el backlog operativo ya propone `motor_034`.

---

## 12. Regla de routing público antes del scraping

### Confirmado

Todo flujo de discovery público debe pasar por una capa explícita de routing antes de ejecutar scraping técnico.

La secuencia mínima obligatoria pasa a ser:

1. target classification
2. jurisdiction resolution
3. asset-type routing
4. source routing plan
5. discovery execution
6. field extraction
7. evidence gating
8. report-type switching

Esto implica que, antes de buscar contenido técnico, el sistema ya debe saber:

- qué tipo de objeto está evaluando;
- en qué estado, ciudad y stack regulatorio cae;
- qué utility territory y climate-zone son plausibles;
- qué familia de activo gobierna la estrategia de ingestión;
- qué fuentes son obligatorias;
- qué fuentes son opcionales;
- y qué sustituciones están prohibidas.

### Reglas duras

1. No technical scraping before routing.
2. Structured canonical public sources come before weak web search.
3. If a route-specific public dataset exists, it must be attempted before fallback benchmark substitution.
4. `mandatory_sources`, `high_priority_sources`, `optional_sources`, and `disallowed_substitutions` must be explicit.
5. A technical route may not proceed if the target is classified as HQ, mailing, ambiguous, or invalid.

### Inferido con alta confianza

- `motor_028` should become a discovery executor, not the sovereign source-chooser.
- a dedicated routing layer should decide where to look before `motor_028` attempts anything.
- routing output should become visible in API, governance, and report packaging.

### Pendiente o ambiguo

- the final motor id of the sovereign routing layer is not yet active in the DAG, though the operative proposal is `motor_035`.
