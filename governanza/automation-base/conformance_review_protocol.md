# conformance_review_protocol.md
# Proceso exacto de revisión de conformidad por motor

## Autoridad
Este documento formaliza la etapa `conformance_review` como proceso ejecutable.
Resuelve la ambigüedad señalada en `consistency_audit.md` sección 2.6.
Fuente de verdad para el `task_builder` al generar la tarea de conformance review.

---

## Ejecutor

Codex (automatizado) como ejecutor primario.
Si el reporte produce `FAIL` o `CONDITIONAL_PASS` con `open_items` no resueltos,
el motor se pausa y espera revisión humana.

No depende del motor `Evaluation / Conformance Engine` para operar.
Cuando ese motor exista, podrá reemplazar o asistir al proceso automatizado.

---

## Inputs obligatorios

El proceso de conformance review requiere estos artefactos del motor:

| Artefacto | Etapa origen | Rol en review |
|---|---|---|
| `functional_contract` | documentation_base | Contrato a verificar |
| `operational_rules` | documentation_base | Reglas operativas |
| `acceptance_tests` | documentation_base | Criterios de aceptación conceptuales |
| `failure_modes` | documentation_base | Modos de fallo declarados |
| `technical_schema` | schema_technical | Estructura esperada |
| `test_spec` | tests | Casos de prueba definidos |
| `failure_modes_spec` | failure_modes | Especificación técnica de fallos |
| `codebase` | implementation | Código a revisar |
| `usage_example` | implementation | Ejemplo de uso a revisar |

Si alguno falta, la etapa `conformance_review` no puede iniciarse.
El orquestador lo detecta en el gate 5 antes de llegar aquí.

---

## Proceso en 5 pasos

### Paso 1: Contract compliance
Verificar que la implementación cumple exactamente el `functional_contract`.
- ¿Las entradas del código coinciden con las declaradas?
- ¿Las salidas del código coinciden con las declaradas?
- ¿Hay operaciones en el código no contempladas en el contrato?

### Paso 2: Boundary check
Verificar que el código no excede el scope declarado del motor.
- ¿El motor invade responsabilidades de otro motor definido en `motor_registry.md`?
- ¿Hay lógica que pertenece a otro motor?
- ¿El `usage_example` demuestra uso dentro de los límites?

### Paso 3: Metadata integrity
Verificar trazabilidad y versionado.
- ¿El código preserva lineage en los objetos que procesa?
- ¿Los campos de versionado del `technical_schema` están implementados?
- ¿Las mutaciones de objetos son trazables?

### Paso 4: Responsibility separation
Verificar separación de responsabilidades.
- ¿Hay signos de acoplamiento fuerte con otros motores no declarados?
- ¿El motor puede operar de forma aislada?
- ¿Las dependencias externas están explícitas y justificadas?

### Paso 5: Test coverage
Verificar cobertura declarativa de tests.
- ¿El código implementado cubre los casos del `test_spec`?
- Si los tests son ejecutables: correr y registrar resultados.
- Si no son ejecutables: verificar que el código contempla los escenarios declarados.

---

## Output — conformance_review_report

Formato JSON estricto. El orquestador lo parsea para tomar decisiones.

```json
{
  "motor_id": "string",
  "motor_name": "string",
  "reviewed_at": "ISO8601",
  "reviewer": "automated",
  "inputs_used": ["functional_contract", "technical_schema", "..."],
  "summary": {
    "status": "PASS | CONDITIONAL_PASS | FAIL",
    "verdict": "string — resumen ejecutivo en 1-2 oraciones"
  },
  "contract_compliance": {
    "status": "OK | VIOLATION",
    "findings": ["string"]
  },
  "boundary_violations": ["string"],
  "metadata_integrity": {
    "status": "OK | VIOLATION",
    "findings": ["string"]
  },
  "separation_issues": ["string"],
  "test_results": {
    "executable": false,
    "passed": 0,
    "failed": 0,
    "coverage_assessment": "string",
    "notes": "string"
  },
  "open_items": [
    {
      "id": "string",
      "step": "contract_compliance | boundary | metadata | separation | tests",
      "severity": "critical | major | minor",
      "description": "string",
      "resolution": "unresolved | accepted_risk | deferred",
      "resolution_notes": "string"
    }
  ]
}
```

---

## Semántica del campo summary.status

| Status | Condición | Acción del orquestador |
|---|---|---|
| `PASS` | Sin findings. Sin open_items. | Motor avanza a `closed` |
| `CONDITIONAL_PASS` | Open items presentes pero todos resueltos como `accepted_risk` o `deferred` | Motor se pausa para revisión humana. Una vez aprobado, avanza a `closed` |
| `FAIL` | Violations materiales sin resolución | Bucle de corrección: implementation fix (máx 3 intentos). Si persiste, motor pausa |

---

## Criterio de severidad para open_items

- `critical` — viola el contrato funcional o destruye trazabilidad. Bloquea PASS.
- `major` — excede scope o mezcla responsabilidades. Bloquea PASS, puede ser `CONDITIONAL_PASS` si `accepted_risk`.
- `minor` — problema de calidad no bloqueante. Puede ser `CONDITIONAL_PASS`.

---

## Variante lightweight

Solo aplica a motores de tipo governance/policy (sin código ejecutable).
Se activa si `motor_plan.execution_strategy` contiene `"lightweight_review": true`.

En variante lightweight:
- Paso 5 (tests) se omite
- `test_results.executable` = false, `test_results.notes` = "lightweight_review"
- Los pasos 1-4 aplican igual
