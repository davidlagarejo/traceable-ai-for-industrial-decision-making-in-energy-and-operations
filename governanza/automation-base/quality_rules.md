# Quality Rules

## 1. Principios obligatorios

### Confirmado

1. La arquitectura debe ser deterministic-first.  
   El LLM no puede sustituir contratos, trazabilidad, versionado, taxonomía ni lógica estructural. Su rol, si existe, es auxiliar y subordinado.
2. Cada motor debe tener límites duros.  
   Debe quedar claro qué hace, qué no hace, qué entra y qué sale. Un motor no puede redefinir el rol de otro.
3. La documentación base precede al código.  
   Ningún motor debe pasar a implementación sin documentación base, schema técnico, tests y failure modes.
4. Todo debe ser trazable y reconstruible.  
   Deben preservarse provenance, lineage, versionado y posibilidad de rebuild. No se puede perder el rastro de cómo se produjo un objeto.
5. No silent mutation.  
   No se deben corregir silenciosamente datos, contratos, taxonomías, outputs o estados internos.
6. La prioridad del MVP no es capturar todo.  
   La prioridad es separar responsabilidades, preservar metadatos correctos y evitar retrabajo futuro.
7. No monolitos.  
   Los motores no deben crecer como módulos gigantes que mezclan responsabilidades o se convierten en contenedores de lógica difusa.
8. Escalabilidad sin sobre-ingeniería ornamental.  
   Cada motor debe nacer con estructura suficiente para crecer sin rehacerse, pero sin complejidad gratuita.
9. La separación entre fases y motores es obligatoria.  
   Las fases definen autoridad, límites epistemológicos, outputs permitidos y handoffs. Los motores implementan capacidades.
10. La implementación no es un espacio de rediseño.  
    El código debe obedecer lo ya cerrado en documentación, no reinterpretarlo ni ampliarlo.

### Inferido con alta confianza

- Hay preferencia fuerte por modularidad, tipado claro, interfaces explícitas, validación explícita, errores estructurados y tests como parte central del diseño.
- Se espera calidad de nivel senior: código limpio, mantenible, explícito y sobrio.

### Pendiente o ambiguo

- No está fijado un stack técnico único.
- No está fijada todavía una convención única de estilos de código por lenguaje.

---

## 2. Reglas estructurales

### Confirmado

1. Una pieza nueva solo debe existir si tiene una responsabilidad separable.  
   Si no puede definirse con límites claros, no debe nacer como pieza independiente.
2. Cada motor debe existir como unidad de arquitectura real.  
   No como etiqueta vaga ni como módulo que "hace de todo".
3. No mezclar responsabilidades entre captura, normalización, identidad, curación, reporting o gobernanza.  
   Cada una debe vivir en el motor correspondiente.
4. Cada motor debe tener contratos explícitos.  
   Inputs, outputs, objetos mínimos, validaciones, tests y failure modes deben estar definidos antes del código.
5. Toda pieza debe preservar metadatos críticos.  
   Si una pieza destruye provenance, lineage, versionado o contexto, degrada el sistema.
6. Toda pieza debe poder ser evaluada por separado.  
   Debe poder documentarse, testearse, versionarse y revisarse como unidad independiente.
7. Evitar dependencia opaca entre piezas.  
   Los handoffs deben ser explícitos. No deben existir acoplamientos invisibles ni supuestos tácitos entre motores.
8. No usar prompts de implementación como sustituto de arquitectura cerrada.  
   La arquitectura debe existir antes del prompt de código.

### Inferido con alta confianza

- El sistema debe crecer por suma de capacidades controladas, no por acumulación de scripts ad hoc.
- El bajo acoplamiento es un principio implícito fuerte: si una pieza obliga a rediseñar todas las demás, está mal recortada.

### Pendiente o ambiguo

- No está fijado todavía el patrón exacto de empaquetado o repositorios por motor.

---

## 3. Reglas para escribir nuevas piezas

### Confirmado

1. No crear una pieza nueva por comodidad local.  
   Debe justificarse por una responsabilidad clara y separable.
2. No escribir código antes de cerrar la documentación base.  
   La secuencia obligatoria es:
   - documentación base,
   - schema técnico,
   - tests,
   - failure modes,
   - implementación,
   - revisión de conformidad.
3. No introducir features "por si acaso".  
   La nueva pieza debe resolver un problema real ya identificado en el proyecto.
4. No introducir complejidad decorativa.  
   Se debe evitar sobre-ingeniería ornamental.
5. Toda nueva pieza debe nacer con criterio de escalabilidad real.  
   Eso implica:
   - límites claros,
   - separación de responsabilidades,
   - contratos duros,
   - objetos mínimos,
   - versionado,
   - lineage/provenance,
   - observabilidad mínima,
   - acceptance tests,
   - failure modes,
   - handoffs controlados.
6. Toda nueva pieza debe poder explicar qué problema resuelve y cuál no.  
   Si no puede decirlo con precisión, no está lista para existir.
7. Toda nueva pieza debe definir qué no hace.  
   Esto es obligatorio para evitar invasión de rol de otros motores.

### Inferido con alta confianza

- Una pieza nueva debería nacer pequeña pero estructuralmente correcta, no grande y difusa.
- La calidad de una pieza se evalúa por utilidad real, no por volumen de código o sofisticación aparente.

### Pendiente o ambiguo

- No existe todavía una plantilla única obligatoria de naming de módulos o carpetas.

---

## 4. Reglas para modificar piezas existentes

### Confirmado

1. No reabrir una pieza cerrada por hallazgos menores.  
   Los bucles de corrección deben ser localizados y controlados.
2. No usar implementación como excusa para rediseñar el motor completo.  
   Si el problema es local, la corrección debe ser local.
3. Solo volver de una etapa posterior a una anterior cuando exista inconsistencia objetiva.  
   Ejemplos ya permitidos:
   - del schema técnico a documentación base si el contrato era ambiguo;
   - de tests a schema si falta estructura mínima;
   - de implementación a schema o tests si el código revela inconsistencia objetiva;
   - de revisión de conformidad a implementación para corregir desviaciones.
4. No corregir piezas existentes con silent mutation.  
   Todo cambio material debe ser visible, justificable y trazable.
5. No mezclar corrección con expansión de alcance.  
   Corregir una pieza no autoriza añadir funciones nuevas no cerradas.
6. No romper la separación entre objeto vigente, historial y derivados.  
   Esto es especialmente importante en piezas con lineage o versionado.

### Inferido con alta confianza

- Modificar una pieza existente debe preservar comparabilidad histórica y trazabilidad.
- Un cambio estructural en una pieza debe justificarse más que un ajuste local.

### Pendiente o ambiguo

- No está definido todavía el umbral formal entre "corrección menor" y "cambio estructural".

---

## 5. Antipatrones prohibidos

### Confirmado

1. Empezar por código.
2. Confundir fases con motores.
3. Usar IA como sustituto de arquitectura explícita.
4. Redefinir el motor durante la implementación.
5. Mezclar responsabilidades de varios motores en uno.
6. Corregir silenciosamente contratos o metadatos.
7. Introducir features "por si acaso".
8. Hacer sobre-ingeniería ornamental.
9. Producir documentación vaga.
10. Asumir que prompts de implementación equivalen a arquitectura cerrada.
11. Saltarse tests o failure modes.
12. Confundir un output funcional con un motor correctamente diseñado.
13. Usar narrativa o conveniencia como sustituto de trazabilidad y límites.
14. Construir scripts monolíticos que acumulen lógica de varias capas.
15. Permitir que el LLM se vuelva núcleo soberano del sistema.
16. Construir piezas que obliguen a rehacer el resto al crecer.
17. Pensar que más datos equivale a mejor sistema.
18. Confundir calidad estructural con verdad epistemológica final.
19. Suponer que benchmarks o contexto público equivalen a verificación de sitio.
20. Rellenar huecos con intuiciones no confirmadas.
21. Tomar deseos futuros como decisiones ya tomadas.

### Inferido con alta confianza

- También es antipatrón construir una pieza "bonita" pero imposible de auditar.
- También es antipatrón esconder lógica importante en helpers genéricos o abstracciones bonitas sin necesidad real.

### Pendiente o ambiguo

- No hay todavía una lista cerrada de antipatrones específicos por lenguaje o framework.

---

## 6. Criterios mínimos de aceptación

### Confirmado

Una pieza o motor no debe considerarse aceptable si no cumple, como mínimo, con lo siguiente:
1. Respeta su contrato.
2. Respeta sus límites.
3. No mezcla responsabilidades.
4. Preserva metadatos críticos.
5. Tiene tests mínimos.
6. Tiene failure modes explícitos.
7. Puede revisarse por conformidad.
8. Puede existir como unidad separada sin reinterpretaciones continuas.
9. Está listo para escalar sin tener que rehacerse estructuralmente.

También se confirmó que un motor se considera cerrado cuando:
- su documentación base está cerrada;
- su schema técnico está cerrado;
- sus tests mínimos existen;
- sus failure modes están documentados;
- su implementación existe;
- su revisión de conformidad no muestra violaciones materiales.

### Inferido con alta confianza

- El criterio de aceptación no depende de volumen de código, sino de conformidad arquitectónica y utilidad real.
- La aceptación exige que la pieza sea mantenible y trazable, no solo funcional.

### Pendiente o ambiguo

- No existe todavía una matriz única y formal de scoring de calidad para todos los motores.

---

## 7. Qué puntos siguen abiertos o ambiguos

### Confirmado

Siguen abiertos o ambiguos:
- stack técnico exacto de implementación;
- formato exacto de carpetas y archivos;
- gates automáticos entre etapas;
- protocolo exacto de cierre final cuando varios motores ya estén integrados;
- lista final cerrada de todos los motores;
- nivel exacto de profundidad documental por motor;
- convención final de nombrado técnico por lenguaje o repositorio.

### Inferido con alta confianza

- También sigue abierto el detalle fino de performance y eficiencia por motor específico.
- La eficiencia de CPU, RAM, disco e I/O está implícitamente deseada por el rechazo a monolitos, scripts caóticos y sobre-ingeniería, pero no está desarrollada todavía como política detallada por motor.

### Pendiente o ambiguo

- No hay todavía reglas operativas suficientemente detalladas para decidir con exactitud cuándo una nueva pieza debe existir como motor separado versus quedarse como parte interna de otro motor, más allá del principio general de responsabilidad separable.

---

## 8. Reglas de calidad para madurez de evidencia y permisos de claim

### Confirmado

Queda prohibido:

1. usar variables `Level 0-1` para claims `Level 3-4`;
2. usar benchmarks como si fueran verdad local;
3. convertir proxy en ROI cerrado;
4. convertir trigger plausible en cierre regulatorio;
5. convertir intake, brochure o listing en verificación-grade por estilo;
6. permitir que una variable derivada outrun the weakest dependency that supports it;
7. emitir charts numéricos o tablas de decisión fuerte cuando la variable crítica sigue en `L0-L1`;
8. rellenar variables faltantes con `0`, `blank`, `null` o `unspecified` como si fueran dato.

### Inferido con alta confianza

- También es una violación de calidad dejar que web search o snippets sustituyan structured public records canónicos cuando esos records están disponibles para la ruta.

---

## 9. Reglas de calidad para routing público y selección de fuentes

### Confirmado

Queda prohibido:

1. hacer scraping técnico antes de clasificar el target;
2. hacer scraping técnico antes de resolver jurisdicción y tipo de activo;
3. usar búsqueda genérica como primer paso cuando existe un dataset canónico estructurado para esa ruta;
4. mezclar fuentes de distintas jurisdicciones como si fueran equivalentes;
5. permitir que una fuente opcional llene un campo que la ruta marca como `mandatory canonical source required`;
6. permitir sustituciones prohibidas entre:
   - `ENTITY_LEVEL -> ASSET_LEVEL`
   - `PORTFOLIO_LEVEL -> ASSET_LEVEL`
   - `BENCHMARK_LEVEL -> local truth`
7. usar una ciudad o utility territory equivocada para derivar stack regulatorio, tariff context o benchmark route;
8. seguir a análisis técnico si el target cae en `CORPORATE_HQ`, `MAILING_ADDRESS`, `PORTFOLIO_ENTITY`, `AMBIGUOUS_TARGET` o `INVALID_TARGET`;
9. esconder la razón de routing por la cual una fuente fue obligatoria, opcional, descartada o prohibida.

### Reglas positivas obligatorias

1. canonical structured public datasets first;
2. route-specific source priority before generic discovery;
3. explicit `mandatory_sources`, `high_priority_sources`, `optional_sources`, and `disallowed_substitutions`;
4. explicit `critical_field_contract` by asset family;
5. downgrade before substitution;
6. contamination detection before publication.

### Inferido con alta confianza

- a routing engine should be treated as production governance infrastructure, not as a helper around the scraper.
- the routing layer should be testable without requiring live discovery.

### Pendiente o ambiguo

- the exact source inventory for all US jurisdictions remains an implementation concern, but the quality rules already require deterministic routing and explicit substitution policy.

- La calidad estructural de un motor downstream pasa a depender también de que respete el ceiling de las variables que consume.
- Un reporte puede estar bien renderizado y aun así ser de baja calidad si viola la madurez de evidencia de sus variables críticas.

### Pendiente o ambiguo

- Todavía no existe una matriz única implementada para todas las familias de variables; esa pieza debe materializarse en un registro técnico transversal.
