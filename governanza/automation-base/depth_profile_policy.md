# depth_profile_policy.md
# Política de profundidad de construcción por motor

## Autoridad
Resuelve la ambigüedad sobre si todos los motores exigen la misma profundidad.
Fuente de verdad para el orquestador al determinar qué artefactos son obligatorios por motor.

---

## Decisión

Todos los motores confirmados (Grupos A y B) usan el mismo perfil de profundidad.
Los motores del Grupo C no son procesados por el orquestador.

Hay una excepción para motores de tipo governance/policy sin código ejecutable.

---

## Perfil estándar (Grupos A y B)

13 artefactos obligatorios distribuidos en 6 etapas:

| Etapa | Artefactos obligatorios |
|---|---|
| documentation_base | master_concept_doc, functional_contract, conceptual_schema, operational_rules, acceptance_tests, failure_modes, design_done_criteria |
| schema_technical | technical_schema |
| tests | test_spec |
| failure_modes | failure_modes_spec |
| implementation | codebase, usage_example |
| conformance_review | conformance_review_report |

Todos son obligatorios. Ninguno es opcional. El gate de cada etapa verifica su presencia.

---

## Excepción: perfil lightweight

Aplica solo a motores cuyo `motor_plan` declara explícitamente:
```json
"execution_strategy": {
  "lightweight_review": true,
  "reason": "motor de tipo governance/policy sin código ejecutable"
}
```

En perfil lightweight, las diferencias son:
- `codebase` puede ser un documento de especificación formal en lugar de código ejecutable
- `test_spec` define escenarios de validación conceptual, no tests ejecutables
- `conformance_review_report` omite `test_results.executable`, usa solo revisión documental

Los artefactos siguen siendo 13. Cambia el tipo de contenido, no la cantidad.

**Criterio para activar lightweight:** el orquestador solo acepta `lightweight_review: true`
si el motor está en la lista de motores governance explícitamente aprobada:

```
motor_024: Governance Event & Exception Registry
motor_025: Epistemic Governance Layer
```

Para cualquier otro motor, el flag `lightweight_review` es ignorado.

---

## Grupo C — No elegibles

Motors 026, 027, 028 tienen `orchestrator_eligible: false` en `motor_dependencies.json`.
El orquestador los ignora al seleccionar el siguiente motor.

Para promover un motor del Grupo C:
1. Editar `motor_dependencies.json` y cambiar `catalog_status` de `"recommended"` o `"ambiguous"` a `"planned"`
2. Cambiar `orchestrator_eligible` a `true`
3. Esto requiere edición manual y no puede hacerse automáticamente

---

## Uniformidad como principio operativo

La decisión de usar el mismo perfil para todos los motores confirmados es intencional:
- Simplifica el orquestador (no necesita lógica condicional por profundidad)
- Garantiza que todos los motores tienen el mismo nivel de trazabilidad
- Evita que motores "menores" se construyan con menos rigor y generen deuda técnica

Si en el futuro se requiere un tercer perfil, debe definirse aquí con criterios explícitos
y lista cerrada de motores que lo usan. No puede inferirse del nombre o grupo del motor.
