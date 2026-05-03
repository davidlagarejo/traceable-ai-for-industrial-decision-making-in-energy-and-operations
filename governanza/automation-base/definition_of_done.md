# definition_of_done.md
# Definición de terminado — condiciones de cierre por motor y por etapa

## Autoridad
Este documento consolida las condiciones de cierre extraídas de:
- `workflow_rules.md` (criterios narrativos por etapa y por motor)
- `quality_rules.md` (criterios mínimos de aceptación)
- `motor_state_semantics.md` (semántica exacta de `closed` y combinaciones válidas)
- `stage_gates.md` (condiciones verificables por máquina)
- `depth_profile_policy.md` (artefactos obligatorios por motor)
- `conformance_review_protocol.md` (semántica de PASS, CONDITIONAL_PASS, FAIL)
- `artifact_layout.md` (artefactos mínimos por etapa)

No reemplaza ninguno de esos documentos. Los consolida en una referencia operativa única.
En caso de conflicto con otro documento sobre lo que significa `closed`, este archivo
prevalece exclusivamente como definición de terminado. Las condiciones de transición
entre etapas siguen siendo autoridad de `stage_gates.md`.

---

## 1. Qué significa que un motor esté cerrado

### Confirmado
Un motor está cerrado cuando se cumplen simultáneamente estas condiciones:

**Condición de estado (verificable en `motor_schema.json`):**
- `status = closed`
- `current_stage = closed`
- `closure.is_closed = true`
- `blocked = false`
- `paused = false`
- `waiting_on = null`

**Condición de etapas:**
- Todas las etapas del workflow aparecen en `completed_stages`.

**Condición de artefactos:**
- Los 13 artefactos obligatorios del perfil estándar existen y no están vacíos.

**Condición de conformidad:**
- El `conformance_review_report` tiene `summary.status` en `["PASS", "CONDITIONAL_PASS"]`
  con todos los `open_items` resueltos como `accepted_risk` o `deferred`.

Las cuatro condiciones deben cumplirse. Ninguna es suficiente por sí sola.

### Inferido con alta confianza
Un motor que tiene código funcional pero no pasó conformance review no está cerrado.
Un motor que tiene conformance review aprobada pero `missing_artifacts` no vacío no está cerrado.

### Pendiente o ambiguo
No está definido si el cierre de un motor requerirá integración obligatoria con otros
motores como condición adicional. Hoy basta con que el motor exista como unidad autónoma
correctamente construida.

---

## 2. Artefactos obligatorios para cierre

### Confirmado
Todos los motores confirmados (Grupos A y B) exigen exactamente 13 artefactos.
Ninguno es opcional. El perfil es uniforme sin excepción salvo el lightweight explícito.

| Etapa | Artefactos obligatorios |
|---|---|
| `documentation_base` | `master_concept_doc`, `functional_contract`, `conceptual_schema`, `operational_rules`, `acceptance_tests`, `failure_modes`, `design_done_criteria` |
| `schema_technical` | `technical_schema` |
| `tests` | `test_spec` |
| `failure_modes` | `failure_modes_spec` |
| `implementation` | `codebase`, `usage_example` |
| `conformance_review` | `conformance_review_report` |

Un motor no puede cerrar si alguno de estos artefactos está ausente o vacío
(menos de 500 bytes), independientemente del estado de otras condiciones.

### Confirmado (excepción lightweight)
Solo `motor_024` y `motor_025` pueden activar `lightweight_review: true`.
En ese caso los 13 artefactos siguen siendo obligatorios, pero:
- `codebase` puede ser especificación formal en lugar de código ejecutable.
- `test_spec` define escenarios conceptuales, no tests ejecutables.
- `conformance_review_report` omite `test_results.executable`.

Para cualquier otro motor el flag `lightweight_review` es ignorado.

### Inferido con alta confianza
La uniformidad del perfil no es accidental: garantiza trazabilidad homogénea y
evita que motores "menores" se construyan con menos rigor.

---

## 3. Criterios de cierre por etapa

### Confirmado

### 3.1 Cierre de `documentation_base`
Cerrada cuando:
- El motor está definido con claridad: propósito, límites, inputs, outputs.
- `functional_contract`, `conceptual_schema` y `operational_rules` no contienen marcadores
  abiertos (TODO, TBD, [PENDIENTE], [DEFINIR], [FALTA], ???).
- `acceptance_tests` y `failure_modes` existen como artefactos independientes.
- `design_done_criteria` lista al menos 3 criterios.
- Gate 1 automático supera todas las condiciones de `stage_gates.md`.

### 3.2 Cierre de `schema_technical`
Cerrado cuando:
- `technical_schema` existe, es válido y no tiene marcadores abiertos.
- Contiene secciones: `entities`, `fields`, `relationships`, `identifiers`, `versioning`, `lineage`.
- El motor puede ser testeado sin inventar estructura.

### 3.3 Cierre de `tests`
Cerrado cuando:
- `test_spec` existe y cubre: `happy_path`, `sparse_case`, `malformed_input`, `edge_cases`.
- Contiene criterios observables: `pass_criteria`, `fail_criteria`.
- Los edge cases críticos del motor están explícitos.

### 3.4 Cierre de `failure_modes`
Cerrado cuando:
- `failure_modes_spec` existe y cubre: `failure_modes_list`, `anti_patterns`,
  `degradation_signals`, `expensive_errors`.
- No contiene marcadores abiertos.

### 3.5 Cierre de `implementation`
Cerrado cuando:
- `codebase` existe y no está vacío (si directorio: contiene al menos un archivo ejecutable).
- `usage_example` existe y no contiene marcadores abiertos.
- La implementación respeta el contrato y preserva metadatos críticos.

### 3.6 Cierre de `conformance_review`
Cerrado cuando:
- `conformance_review_report` existe y es JSON válido.
- `summary.status` es `PASS` o `CONDITIONAL_PASS`.
- Si `CONDITIONAL_PASS`: todos los `open_items` tienen `resolution` en
  `["accepted_risk", "deferred"]`. Ninguno tiene `resolution: "unresolved"`.
- Si `FAIL`: el motor entra en bucle de corrección, no en cierre.

### Inferido con alta confianza
El cierre de una etapa no depende de volumen de contenido, sino de conformidad
con los criterios de calidad y ausencia de ambigüedades materiales.

---

## 4. Gates automáticos necesarios para cierre

### Confirmado
El cierre de un motor es el resultado secuencial de 6 gates superados.
Ningún gate puede omitirse excepto por `--force` con registro en audit trail.

| Gate | Transición | Condición crítica |
|---|---|---|
| Gate 1 | `documentation_base` → `schema_technical` | 7 artefactos presentes + `functional_contract` sin marcadores + `design_done_criteria` ≥ 3 ítems |
| Gate 2 | `schema_technical` → `tests` | `technical_schema` válido con 6 secciones requeridas |
| Gate 3 | `tests` → `failure_modes` | `test_spec` con 4 secciones de casos + criterios PASS/FAIL |
| Gate 4 | `failure_modes` → `implementation` | `failure_modes_spec` con 4 secciones requeridas |
| Gate 5 | `implementation` → `conformance_review` | `codebase` no vacío + `usage_example` sin marcadores |
| Gate 6 | `conformance_review` → `closed` | `conformance_review_report` JSON válido con `summary.status` en `[PASS, CONDITIONAL_PASS]` y `open_items` resueltos |

Gate 1 tiene además una condición manual (no automatizable):
`"functional_contract no contiene ambigüedades materiales en inputs/outputs"`.
Esta condición bloquea el gate hasta aprobación explícita del operador via:
`python cli.py approve --motor {id} --gate gate_1`.

Si un gate falla, la etapa permanece `in_progress` y se registra el motivo exacto
en `validations`. Los gates no se reevalúan solos.

### Inferido con alta confianza
Un motor que tiene `completed_stages` completo pero no superó Gate 6 no puede
considerarse cerrado. Los `completed_stages` son necesarios pero no suficientes.

---

## 5. Criterios mínimos de aceptación del motor

### Confirmado
Un motor no puede cerrar si no cumple, como mínimo, con los nueve criterios siguientes:

1. Respeta su contrato funcional (inputs, outputs, límites declarados en `functional_contract`).
2. Respeta sus límites (no invade responsabilidades de otro motor).
3. No mezcla responsabilidades.
4. Preserva metadatos críticos (lineage, versionado, provenance).
5. Tiene tests mínimos definidos en `test_spec`.
6. Tiene failure modes documentados en `failure_modes_spec`.
7. Puede revisarse por conformidad (tiene `conformance_review_report` válido).
8. Puede existir como unidad separada sin reinterpretaciones continuas.
9. Está listo para escalar sin tener que rehacerse estructuralmente.

Estos criterios son condiciones necesarias. No son lista de verificación subjetiva.
Si alguno falla, el motor no puede transicionar a `status = closed`.

### Inferido con alta confianza
El criterio 9 (escalabilidad sin rehacerse) no es verificable automáticamente pero
es evaluado durante conformance_review en los pasos boundary_check y responsibility_separation.

---

## 6. Estado del motor al cerrar

### Confirmado
Al cerrarse, el motor debe tener exactamente esta combinación de campos en `motor_schema.json`:

```json
{
  "status": "closed",
  "current_stage": "closed",
  "closure": {
    "is_closed": true,
    "closed_at": "<ISO8601 timestamp>"
  },
  "blocked": false,
  "paused": false,
  "waiting_on": null
}
```

Estas son las únicas combinaciones válidas en estado `closed`.
Las siguientes son combinaciones inválidas que el orquestador debe rechazar:

| Combinación inválida | Razón |
|---|---|
| `status = closed` + `current_stage ≠ closed` | Inconsistencia entre status y stage |
| `closure.is_closed = true` + `blocked = true` | Un motor cerrado no puede estar bloqueado |
| `closure.is_closed = true` + `paused = true` | Un motor cerrado no puede estar en pausa |
| `closure.is_closed = true` + `waiting_on ≠ null` | Un motor cerrado no espera nada |
| `blocked = true` + `paused = true` | Estados mutuamente excluyentes |
| `status = waiting` + `waiting_on = null` | `waiting` requiere referencia explícita |

### Inferido con alta confianza
Un motor que tiene `closure.is_closed = true` con alguna etapa no completada
también debe tratarse como estado inválido, aunque no esté listado explícitamente.

---

## 7. Condiciones de dependencia para iniciar un motor

### Confirmado
Un motor no puede transicionar de `not_started` a `in_progress` si alguno de los
motores listados en su campo `requires` de `motor_dependencies.json` no tiene
`status = closed` en su `motor_schema`.

Esta condición es estricta y sin excepciones automáticas.
Solo puede omitirse mediante comando explícito `--force` registrado en audit trail.

Los motores del Grupo C (`motor_026`, `motor_027`, `motor_028`) no pueden iniciarse
bajo ninguna circunstancia mientras su `orchestrator_eligible` sea `false`.
La promoción requiere edición manual de `motor_dependencies.json`.

Un motor con `requires: []` puede iniciarse en cualquier momento si el orquestador
está activo.

### Inferido con alta confianza
Esta condición de dependencia no es criterio de cierre del motor en cuestión,
sino criterio de apertura. Queda aquí documentada porque el DoD completo incluye
tanto las condiciones de cierre como las de elegibilidad.

---

## 8. Qué no cuenta como terminado

### Confirmado
Ninguna de las siguientes condiciones, por sí sola, equivale a motor terminado:

- El motor tiene código funcional pero no tiene `conformance_review_report`.
- El motor pasó conformance review pero le faltan artefactos de etapas anteriores.
- El motor tiene `completed_stages` completo pero `closure.is_closed = false`.
- El motor tiene documentación completa pero no tiene implementación.
- El motor tiene `status = closed` pero `current_stage ≠ closed`.
- El motor fue declarado cerrado verbalmente o en notas sin actualizar `motor_schema`.
- El motor tiene conformance review con `status = FAIL` o con `open_items` sin resolver.
- El motor tiene `status = closed` pero `blocked = true` o `paused = true`.
- El motor tiene artefactos con marcadores abiertos (TODO, TBD, [PENDIENTE], etc.).

Estas situaciones representan estados incompletos, no cierres parciales.
El sistema no admite cierre parcial: un motor está cerrado o no lo está.

### Confirmado
También son antipatrones que impiden el cierre legítimo:
- Corregir silenciosamente artefactos sin dejar rastro en `validations` o `corrections`.
- Saltarse la etapa de tests o failure modes justificando que "son evidentes".
- Usar el prompt de implementación como sustituto del contrato funcional.
- Redefinir el motor durante la implementación.
- Mezclar responsabilidades de varios motores en el mismo codebase.

---

## 9. Qué sigue abierto o ambiguo

### Confirmado
Siguen abiertos o ambiguos, y no deben cerrarse automáticamente:

- Si el cierre final de un motor requerirá integración obligatoria con otros motores
  antes de declararlo listo.
- El umbral formal entre "corrección menor" y "cambio estructural" que amerita
  reabrir documentación base.
- Si `completed_stages` debe exigirse estrictamente en orden o solo como subconjunto
  válido de `stage_sequence`.
- Si en el futuro se definirá una tipificación formal para `closed_for_implementation`,
  `closed_for_integration`, `closed_as_stable_reference` como estados serializables
  distintos en `motor_schema.json`.
- El protocolo exacto de cierre cuando varios motores dependientes ya estén integrados.
- Si se agregará validación automática formal de combinaciones de estado en `motor_schema.json`.

### Inferido con alta confianza
Estos huecos no bloquean la operación del orquestador en su diseño actual.
Solo se volverán bloqueantes si se intenta automatizar cierre por integración
o tipificación fina de cierre parcial, que no están en el alcance del sistema actual.

### Pendiente o ambiguo
No existe todavía una política cerrada para resolver qué pasa cuando un motor ya
cerrado requiere cambios por dependencia de un motor posterior que descubre
inconsistencia en el contrato de un motor upstream.
