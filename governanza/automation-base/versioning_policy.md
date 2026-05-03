# versioning_policy.md
# Política de versionado documental — artefactos por motor y documentos del framework

## Autoridad
Resuelve el hueco 4.6 de `consistency_audit.md`.
Aplica a artefactos generados por motor y a los documentos del framework en `automation-base`.

---

## Nivel 1 — Artefactos por motor

### Header obligatorio en artefactos de texto

Todo artefacto generado por motor debe incluir este bloque al inicio del archivo:

```
---
motor_id: motor_001
artifact_type: functional_contract
version: 1.0
created_at: ISO8601
updated_at: ISO8601
stage: documentation_base
status: draft | approved | superseded
---
```

### Esquema de versión

Formato: `{major}.{minor}`

| Tipo de cambio | Acción |
|---|---|
| Cambio en contrato, schema, inputs/outputs declarados | `major` bump (1.0 → 2.0) |
| Adición de contenido sin cambiar estructura | `minor` bump (1.0 → 1.1) |
| Corrección de errores sin cambio de contenido | `minor` bump (1.0 → 1.1) |

### Cuándo versiona el orquestador

- Al crear un artefacto: `version: 1.0`, `status: draft`
- Al aprobar (gate pasado): `status: approved`, `updated_at` actualizado
- Al corregir (bucle de fix): `minor` bump, `status: draft` de nuevo
- El orquestador nunca hace `major` bump automáticamente — requiere intervención humana

### Tracking en motor_schema.json

El campo `artifacts` del estado por motor registra:
```json
{
  "functional_contract": {
    "exists": true,
    "path": "artifacts/documentation_base/functional_contract.md",
    "version": "1.1",
    "validated": true,
    "validation_notes": null
  }
}
```

---

## Nivel 2 — Documentos del framework (automation-base)

### Control de versiones

Los documentos del framework se versionan mediante git.
El orquestador opera con snapshot de los documentos en el momento de iniciar un run.

### SHA lock por run

Al iniciar cada run, el orquestador registra en el log:
```json
{
  "event": "run_started",
  "context_sha": "abc123def456",
  "context_path": "/path/to/automation-base",
  "timestamp": "ISO8601"
}
```

### Política de cambios en documentos del framework durante un run

| Escenario | Acción del orquestador |
|---|---|
| SHA no cambió entre sesiones | Continúa normalmente |
| SHA cambió, secciones `Inferido` o `Pendiente` | Registra advertencia en log, continúa |
| SHA cambió, secciones `Confirmado` editadas | Registra alerta en log, recomienda revisar motores `in_progress` manualmente |

El orquestador **no pausa ni bloquea automáticamente** por cambios en el framework.
La responsabilidad de decidir si reabrir motores en progreso es humana.

### No-retroactividad

Un motor que ya completó `analyze_motor` (tiene `motor_plan` no nulo) **no se re-analiza**
automáticamente por cambios en los documentos del framework.

Para forzar re-análisis:
```
python cli.py reanalyze --motor motor_001
```
Esto borra el `motor_plan` existente y vuelve a ejecutar `analyze_motor`.

---

## Nivel 3 — Política de cierre de versión por motor

Un motor cerrado (`status: closed`) no tiene artefactos en estado `draft`.
Todos deben estar en `approved` al momento del cierre.

Si un artefacto aprobado necesita cambio después del cierre:
1. El motor sale de `closed` a `in_progress` (requiere comando manual)
2. El artefacto vuelve a `draft` con `minor` bump
3. El motor debe re-pasar el gate correspondiente
4. Si el cambio es `major`, el motor puede requerir re-pasar múltiples gates

Este proceso queda registrado en `corrections` del motor_schema.json.
