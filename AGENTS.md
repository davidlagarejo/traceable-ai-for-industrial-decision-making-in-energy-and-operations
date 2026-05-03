# AGENTS.md — ZLab Operational Truth Framework

> Lee este archivo completo antes de ejecutar cualquier comando.
> Es la guia operativa actual para reanudar el framework sin perder la logica vigente.

---

## 1. Que es este proyecto hoy

ZLab Operational Truth Framework ya no es solo el sistema historico de 33 motores.

El estado real del proyecto al `3 de mayo de 2026` es este:

- existe un catalogo de `54` motores en `governanza/automation-base/motor_dependencies.json`;
- `runtime-orchestrator/` implementa y cubre esos `54` motores;
- `governanza/` ya quedo reconciliada contra ese catalogo;
- `motor-creator` ya refleja `54 closed`;
- la cola documental post-cierre ya no esta abierta.

Arquitectura cardinal:

- determinismo primero;
- la IA es subordinada, nunca motor soberano;
- `governanza/automation-base/` contiene los documentos de autoridad;
- `runtime-orchestrator/` es la verdad operativa del sistema ejecutable;
- `motor-creator/` vuelve a ser consistente con el framework expandido.

---

## 2. Fuente de verdad actual

Para retomar el trabajo, usa este orden de verdad:

1. `runtime-orchestrator/` + su suite de tests
2. certificaciones y matrices en `governanza/automation-base/`
3. `runtime_motor_reconciliation_snapshot_latest.md`
4. `motor_dependencies.json`, `motor_registry.md` y `motor-creator/`

No uses el backlog dinamico ni un estado viejo de `motor-creator` para inferir que la expansion sigue abierta.

Al `3 de mayo de 2026`, el estado consolidado es:

- `runtime-orchestrator`: expandido y operativo;
- ultima verdad de suite completa: `455 passed, 15 warnings` con `pytest -q` el `2026-05-03`;
- `motor-creator`: `54 closed`;
- `runtime_motor_reconciliation_snapshot_latest.md`: `54` motores en catalogo, `54` adapters runtime, `54` dirs esperados presentes, `54` cierres formales alineados y `0` motores runtime-ahead;
- los directorios legacy `validation-data-bridge_018` y `verification-bridge-engine_019` siguen preservados como historia, pero no representan mismatch actual.

Importante:

- ese rerun completo ya ocurrio despues de cerrar la ultima ola documental;
- por eso la verdad runtime y la reconciliacion de gobernanza ya quedaron alineadas en el mismo punto de reentrada.

---

## 3. Documentos que mandan para la reentrada

Lee estos documentos antes de decidir que sigue:

- `governanza/automation-base/runtime_reentry_status_latest.md`
- `governanza/automation-base/runtime_may_2_closure_boundary_latest.md`
- `governanza/automation-base/runtime_motor_reconciliation_snapshot_latest.md`
- `governanza/automation-base/post_closure_governance_documentation_order_latest.md`
- `governanza/automation-base/versioning_reentry_boundary_latest.md`
- `governanza/automation-base/legacy_governance_dir_disposition_latest.md`
- `governanza/automation-base/industrial_asset_congruence_prompt_closure_matrix.md`
- `governanza/automation-base/dynamic_congruence_intelligence_multicase_certification_latest.md`
- `governanza/automation-base/congruence_intelligence_multicase_certification_latest.md`
- `governanza/automation-base/congruence_intelligence_100_percent_closure_certification.md`

Lectura correcta:

- `DCI-01`–`DCI-20` estan declarados e implementados;
- la clausura del `2 de mayo de 2026` corresponde a runtime + tests + artefactos de autoridad;
- la reconciliacion documental posterior ya tambien quedo cerrada;
- el siguiente trabajo legitimo ya no es "seguir cerrando motores".

---

## 4. Mision actual

La mision actual no es inventar mas motores ni seguir una cola de reconciliacion por motor.

La mision es:

1. preservar la clausura funcional ya certificada;
2. mantener el runtime en verde;
3. conservar sincronizados runtime, gobernanza y `motor-creator`;
4. dejar una ruta de reentrada estable para futuras sesiones;
5. decidir con criterio si el siguiente paso es limpieza, versionado, archivado de legacy dirs o hardening opcional.

No reabras por defecto:

- backlog dinamico ya cerrado;
- expansiones del prompt ya certificadas;
- reconciliacion por motor como si siguiera pendiente.

---

## 5. Entry points correctos

### Runtime real

```bash
cd /Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator
pytest -q
```

Ese comando es el chequeo primario de salud del sistema ejecutable.

### Gobernanza por motor

```bash
cd /Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/motor-creator
.venv/bin/python cli.py status
```

Ahora ese estado ya es consistente con el runtime expandido, pero sigue siendo secundario frente a una suite runtime roja.

---

## 6. Procedimiento de reentrada

Cuando se retome el proyecto tras una interrupcion, sigue este orden:

1. leer `governanza/automation-base/runtime_reentry_status_latest.md`;
2. leer `governanza/automation-base/runtime_may_2_closure_boundary_latest.md`;
3. leer `governanza/automation-base/runtime_motor_reconciliation_snapshot_latest.md`;
4. leer `governanza/automation-base/post_closure_governance_documentation_order_latest.md`;
5. leer `governanza/automation-base/versioning_reentry_boundary_latest.md`;
6. leer `governanza/automation-base/legacy_governance_dir_disposition_latest.md`;
7. correr `pytest -q` en `runtime-orchestrator/`;
8. si la suite esta verde, tratar el framework como runtime-and-governance closed;
9. decidir despues si el trabajo pendiente es:
   - cleanup/versioning,
   - archivado de legacy dirs,
   - hardening opcional,
   - o nuevas capacidades explicitamente nuevas;
10. si la suite falla, tratar el runtime como prioridad absoluta;
11. no tocar certificaciones o docs de cierre como sustituto de arreglar el runtime.

---

## 7. Estado operativo consolidado

Resumen real:

- congruence intelligence: cerrada por certificacion;
- dynamic congruence intelligence: cerrada por certificacion;
- public data routing v1: `PASS`;
- system consistency certification: `accepted`;
- structural intelligence lane: implementada con cleanup residual;
- runtime suite completa: ultima verdad `455 passed, 15 warnings`;
- `motor-creator`: `54 closed`;
- snapshot de reconciliacion: `54 aligned_closed`, `0 runtime_ahead_of_governance`, `0 identity mismatches`;
- permanecen `2` directorios legacy historicos preservados:
  - `governanza/validation-data-bridge_018`
  - `governanza/verification-bridge-engine_019`

Esto implica:

- no hay que seguir expandiendo ciegamente `motor_034`–`motor_054` como si faltaran;
- no hay una cola documental por motor todavia abierta;
- si algo falla ahora, debe leerse como regresion o trabajo nuevo, no como "cierre pendiente del backlog del 2 de mayo".

---

## 8. Trabajo legitimo desde aqui

Los siguientes frentes si son validos:

1. limpieza del worktree y versionado serio del estado actual;
2. decidir si se preservan o archivan los dirs legacy de `018` y `019`;
3. reruns de certificacion si se quiere actualizar evidencia formal;
4. hardening opcional:
   - mas profundidad de extraccion documental;
   - superficies visuales o apendices tecnicos mas ricos;
   - ampliaciones nuevas explicitamente separadas del cierre ya logrado.

Helper local para versionado acotado:

- `./stage_framework_closure_sources.sh --dry-run`
- `./stage_framework_closure_sources.sh`

No hagas lo siguiente sin razon explicita:

- reescribir el backlog dinamico como si siguiera abierto;
- usar dirs legacy como prueba de mismatch actual;
- volver a tratar `motor-creator` como unica verdad del sistema;
- hacer `git add .` en el root sin separar fuente de stores regenerables;
- editar docs de cierre para ocultar una regresion runtime.

---

## 9. Regla de oro

Si hay conflicto entre:

- una certificacion que dice "closed",
- y una suite runtime que falla,

manda la suite runtime.

Si la suite runtime esta verde y `motor-creator` tambien esta cerrado,
el framework debe tratarse como reconciliado.

Los dirs legacy preservados no invalidan ese cierre.

---

## 10. Que hacer si algo falla

| Situacion | Accion |
|---|---|
| `pytest -q` falla en `runtime-orchestrator/` | arreglar runtime antes de tocar docs de cierre |
| certificacion dice "closed" pero el runtime rompe | tratarlo como regresion de reconciliacion |
| aparecen dudas por dirs legacy `018/019` | tratarlos como historia preservada, no como mismatch activo |
| dudas sobre que documento manda | usar `runtime_reentry_status_latest.md` y luego las certificaciones del `2 de mayo de 2026` |
| worktree sucio o no versionado | no borrar; inspeccionar y preservar |

---

## 11. Regla de edicion

No modifiques a mano estados de cierre para simular progreso.

Si vas a mover el estado formal del framework:

1. primero valida runtime;
2. luego actualiza documentos de autoridad;
3. luego reconcilia `motor-creator` si aplica.

Ese es el orden correcto.
