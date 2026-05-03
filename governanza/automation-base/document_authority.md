# document_authority.md

## 1. Objetivo

### Confirmado
Este archivo fija la jerarquía mínima de autoridad documental para que una herramienta no trate todos los archivos base como si tuvieran el mismo peso normativo.

Su función es resolver, de forma explícita y mínima:
- qué archivo manda sobre cuál;
- qué etiquetas son vinculantes para automatización;
- y qué hacer cuando dos archivos no dicen exactamente lo mismo.

### Inferido con alta confianza
Sin esta jerarquía, la automatización tendería a mezclar contexto, resumen, diagnóstico y reglas como si fueran equivalentes.

### Pendiente o ambiguo
No está definido todavía si esta jerarquía se convertirá después en política formal versionada del proyecto completo.

---

## 2. Semántica vinculante de etiquetas

### Confirmado
Para automatización, las etiquetas deben interpretarse así:
- `Confirmado`: vinculante.
- `Inferido con alta confianza`: usable con cautela, pero no suficiente por sí solo para cerrar ambigüedades, crear motores nuevos, cambiar etapas o declarar cierre final.
- `Pendiente o ambiguo`: no cerrable automáticamente.

### Inferido con alta confianza
Una herramienta puede usar contenido `Inferido con alta confianza` para preparar trabajo, priorizar revisión o señalar una opción razonable, pero no para imponer una decisión terminal.

### Pendiente o ambiguo
No está definido todavía si existirán más niveles intermedios de autoridad documental.

---

## 3. Jerarquía mínima de autoridad documental

### Confirmado
La jerarquía mínima para este paquete base es:

1. `document_authority.md`  
   Define cómo interpretar autoridad y conflicto entre documentos.

2. `workflow_rules.md`  
   Manda sobre secuencia de etapas, transiciones, criterios de cierre por etapa y bucles de corrección del workflow.

3. `quality_rules.md`  
   Manda sobre principios de calidad, criterios mínimos de aceptación, antipatrones y límites de diseño.

4. `motor_registry.md`  
   Manda sobre el catálogo operativo actual de motores y sobre su clasificación como `documented`, `planned`, `recommended`, `ambiguous` u otros estados del catálogo.

5. `motor_state_semantics.md`  
   Manda sobre la semántica de `current_stage`, `status`, `blocked`, `paused`, `waiting_on`, `closure` y el significado operativo de `closed`.

6. `stage_artifact_semantics.md`  
   Manda sobre la relación entre etapas del workflow y artefactos como `acceptance_tests`, `test_spec`, `failure_modes`, `failure_modes_spec` y `conformance_review_report`.

7. `artifact_layout.md`  
   Manda sobre agrupación mínima de artefactos, separación entre fuente de verdad, derivados y tracking, y relación general entre artefactos y workflow.

8. `motor_schema.json`  
   Es el esquema serializable mínimo de estado por motor. No sustituye las reglas textuales anteriores; las representa operativamente.

9. `synthetic_epistemology_rules.md`  
   Manda sobre la semántica epistémica de todos los outputs de la cadena sintética y ML (motores 029–033): flags obligatorios, jerarquía evidentiary, usos prohibidos y política de selección de modelos. En caso de conflicto sobre el significado o el uso permitido de un output sintético, este archivo prevalece sobre cualquier otro documento del framework en esa materia específica.

10. `automation_loop.md`  
    Define el loop mínimo de automatización y debe obedecer a las reglas anteriores. No puede contradecirlas.

11. `framework_manifest.md`  
    Consolida y resume. Sirve como visión integrada, pero no sustituye a los documentos más específicos cuando hay conflicto.

12. `master_context.md`  
    Preserva contexto base y decisiones amplias del proyecto. Sirve como referencia general, pero no manda por encima de los documentos operativos más específicos.

13. `consistency_audit.md`  
    Es diagnóstico. Señala tensiones, huecos y riesgos, pero no define por sí solo la política normativa final.

### Inferido con alta confianza
La regla práctica es: si hay conflicto, manda el documento más específico y más normativo dentro de esta jerarquía.

### Pendiente o ambiguo
No está definido todavía si en el futuro aparecerán otros documentos con autoridad superior sobre partes específicas del sistema.

---

## 4. Regla mínima de resolución de conflicto

### Confirmado
Si dos documentos difieren:
- primero se aplica la jerarquía documental definida arriba;
- luego se prioriza el contenido marcado como `Confirmado`;
- si el conflicto persiste entre dos afirmaciones igualmente `Confirmado`, la automatización debe detenerse y escalar a revisión humana.

### Inferido con alta confianza
La automatización no debe intentar “promediar” documentos en conflicto ni resolverlos por conveniencia local.

### Pendiente o ambiguo
No existe todavía un protocolo más fino de arbitraje documental que distinga conflictos menores de conflictos estructurales.

---

## 5. Qué no debe hacer una herramienta

### Confirmado
Una herramienta no debe:
- tratar todos los archivos como autoridad concurrente equivalente;
- convertir un resumen en fuente primaria si existe un documento más específico;
- usar `Inferido con alta confianza` como regla obligatoria;
- cerrar automáticamente un punto marcado como `Pendiente o ambiguo`;
- ignorar un conflicto documental explícito.

### Inferido con alta confianza
Tampoco debe usar `framework_manifest.md` como si reemplazara todo el resto del paquete.

### Pendiente o ambiguo
No está definido todavía si habrá una validación automática que detecte contradicciones documentales antes de ejecutar el loop de automatización.
