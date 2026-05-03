# stage_gates.md
# Gates automáticos entre etapas — condiciones verificables por máquina

## Autoridad
Este documento es fuente de verdad para las condiciones de transición entre etapas.
Complementa `workflow_rules.md` (que define intención narrativa) con condiciones
checkeables programáticamente. En caso de conflicto, este archivo prevalece sobre
`workflow_rules.md` en materia de gates automáticos.

## Semántica de condiciones

- `file_exists(path)` — el archivo existe y tiene tamaño > 500 bytes
- `no_markers(path)` — el archivo no contiene: TODO, TBD, [PENDIENTE], [DEFINIR], [FALTA], ???
- `has_sections(path, sections)` — el archivo contiene todos los títulos/keys listados
- `min_items(path, section, n)` — la sección tiene al menos n ítems enumerados
- `json_valid(path)` — el archivo es JSON válido parseables
- `field_not_empty(path, field)` — el campo JSON no es null ni string vacío

Una condición no verificable automáticamente se marca como `manual_check: true`
y bloquea el gate hasta aprobación explícita del operador.

---

## Gate 1: documentation_base → schema_technical

### Condiciones automáticas (todas deben cumplirse)

```
file_exists(artifacts/documentation_base/master_concept_doc)
file_exists(artifacts/documentation_base/functional_contract)
file_exists(artifacts/documentation_base/conceptual_schema)
file_exists(artifacts/documentation_base/operational_rules)
file_exists(artifacts/documentation_base/acceptance_tests)
file_exists(artifacts/documentation_base/failure_modes)
file_exists(artifacts/documentation_base/design_done_criteria)

no_markers(artifacts/documentation_base/functional_contract)
no_markers(artifacts/documentation_base/conceptual_schema)
no_markers(artifacts/documentation_base/operational_rules)

has_sections(artifacts/documentation_base/functional_contract, ["inputs", "outputs", "limits"])
min_items(artifacts/documentation_base/design_done_criteria, "criteria", 3)
```

### Condición manual
```
manual_check: "functional_contract no contiene ambigüedades materiales en inputs/outputs"
```

---

## Gate 2: schema_technical → tests

### Condiciones automáticas

```
file_exists(artifacts/schema_technical/technical_schema)
no_markers(artifacts/schema_technical/technical_schema)
has_sections(artifacts/schema_technical/technical_schema, [
  "entities", "fields", "relationships", "identifiers", "versioning", "lineage"
])
```

---

## Gate 3: tests → failure_modes

### Condiciones automáticas

```
file_exists(artifacts/tests/test_spec)
no_markers(artifacts/tests/test_spec)
has_sections(artifacts/tests/test_spec, [
  "happy_path", "sparse_case", "malformed_input", "edge_cases"
])
has_sections(artifacts/tests/test_spec, ["pass_criteria", "fail_criteria"])
```

---

## Gate 4: failure_modes → implementation

### Condiciones automáticas

```
file_exists(artifacts/failure_modes/failure_modes_spec)
no_markers(artifacts/failure_modes/failure_modes_spec)
has_sections(artifacts/failure_modes/failure_modes_spec, [
  "failure_modes_list", "anti_patterns", "degradation_signals", "expensive_errors"
])
no_markers(artifacts/schema_technical/technical_schema)
```

---

## Gate 5: implementation → conformance_review

### Condiciones automáticas

```
file_exists(artifacts/implementation/codebase)
file_exists(artifacts/implementation/usage_example)
no_markers(artifacts/implementation/usage_example)
```

### Nota
`codebase` puede ser un directorio o un archivo. Se verifica que exista y no esté vacío.
Si es directorio, debe contener al menos un archivo .py, .ts, .js o equivalente.

---

## Gate 6: conformance_review → closed

### Condiciones automáticas

```
file_exists(artifacts/conformance_review/conformance_review_report)
json_valid(artifacts/conformance_review/conformance_review_report)
field_not_empty(conformance_review_report, "summary.status")
field_value_in(conformance_review_report, "summary.status", ["PASS", "CONDITIONAL_PASS"])
```

### Condición adicional para CONDITIONAL_PASS
Si `summary.status == "CONDITIONAL_PASS"`:
```
all_items_resolved(conformance_review_report, "open_items",
  resolved_values=["accepted_risk", "deferred"])
```

Si algún `open_item` tiene `resolution: "unresolved"` → gate bloqueado,
motor entra en `paused`, `waiting_on: "human_review_conformance"`.

---

## Reglas generales de gates

1. Un gate solo se evalúa cuando el orquestador intenta avanzar de etapa.
2. Si un gate falla, la etapa actual permanece `in_progress` y se registra el
   motivo exacto del fallo en `validations`.
3. Los gates no se reevalúan solos: solo se evalúan al ejecutar explícitamente
   la transición.
4. Las condiciones `manual_check` bloquean el gate hasta que el operador ejecute:
   `python cli.py approve --motor {id} --gate {gate_name}`
5. Ningún gate puede saltarse excepto por comando explícito con flag `--force`
   que queda registrado en el audit trail.
