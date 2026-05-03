# Runtime Subject Admissibility Backlog

## 1. Propósito

Este backlog define el endurecimiento operativo necesario para que el runtime:

- deje de tratar compañías como si fueran activos físicos,
- imponga un criterio estricto de admisibilidad del sujeto antes de entrar al pipeline asset-first,
- separe claramente `issuer context`, `address candidate`, `site candidate` y `bounded asset`,
- y fuerce que Fases 1–8 trabajen sobre un sujeto físicamente admisible, no sobre un emisor con dirección.

Este documento complementa [runtime_asset_first_hardening_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_asset_first_hardening_backlog.md>).  
Ese backlog resuelve el giro general a `asset-first`.  
Este backlog resuelve el punto más estricto y más peligroso: **qué está permitido evaluar como activo y qué no**.

---

## 2. Diagnóstico rector

El breach actual no es solo de copy ni de reporting.

Es este:

1. El sistema puede partir de una compañía (`ticker`, `CIK`, owner context).
2. Si además encuentra una dirección, infiere `target_scope = asset`.
3. Construye `asset_entity_id` aunque no haya prueba suficiente de identidad física del activo.
4. Mide `asset_context_readiness`, pero no `target admissibility`.
5. Entonces el caso avanza como si fuera `asset_case`, cuando en realidad puede ser:
   - `issuer-only`
   - `HQ address`
   - `mailing address`
   - `office suite`
   - `site candidate`
   - `asset candidate`
6. La degradación ocurre demasiado tarde, cuando el sujeto ya fue admitido incorrectamente.

Conclusión:

- hoy existe `asset_context_readiness`,
- pero falta un gate anterior y más soberano:
  **`subject / target admissibility`**.

---

## 3. Leyes de implementación obligatorias

### 3.1 Company-is-not-an-asset rule

Una compañía, ticker, CIK o issuer name **nunca** constituye por sí mismo un activo físico admisible.

### 3.2 Address-is-not-yet-an-asset rule

Una dirección sola no equivale a `asset`.

Como máximo equivale a:

- `address_candidate`
- o `site_candidate`, si existe evidencia adicional mínima.

### 3.3 Asset admission precedence

El sistema solo puede abrir un `asset_case` si el sujeto alcanza al menos `bounded_asset_candidate` con evidencia explícita.

### 3.4 No silent subject promotion

Ningún motor puede promover silenciosamente:

- `issuer` -> `asset`
- `address_candidate` -> `bounded_asset`
- `site_candidate` -> `bounded_asset`

sin dejar un registro formal de por qué ocurrió.

### 3.5 Asset gate before readiness gate

Primero debe decidirse:

- `¿esto es realmente un activo admisible?`

Y solo después:

- `¿qué tan poblado está el contexto técnico del activo?`

### 3.6 Publication freeze on subject ambiguity

Si el sujeto sigue ambiguo, el runtime no puede producir:

- `Pre-Verification Asset Brief`
- `TDIR Preliminary`
- `Decision-Grade TDIR`

Como máximo puede producir:

- `Issuer Context Memo`
- `Address Candidate Brief`
- `Site Candidate Brief`
- `Asset Context Insufficiency Brief`

---

## 4. Modelo objetivo del sujeto

### 4.1 `subject_kind`

Estados canónicos:

- `issuer`
- `portfolio`
- `campus`
- `address_candidate`
- `site_candidate`
- `asset_candidate`
- `bounded_asset`
- `subsystem`

### 4.2 `subject_admissibility_state`

Estados operativos:

- `invalid_for_asset_pipeline`
- `issuer_context_only`
- `address_candidate_only`
- `site_candidate_only`
- `asset_candidate_but_unbounded`
- `bounded_asset`
- `bounded_asset_with_operable_context`

### 4.3 `asset_anchor_type`

Tipos permitidos:

- `postal_address`
- `parcel_id`
- `assessor_record`
- `benchmark_record`
- `permit_record`
- `facility_registry_id`
- `building_name_plus_address`
- `site_name_plus_city`
- `lat_lon`

### 4.4 `asset_identity_evidence_class`

Clases mínimas:

- `declared_only`
- `issuer_address_only`
- `geocoded_only`
- `parcel_or_record_linked`
- `local_asset_record_linked`
- `benchmark_record_linked`
- `multi-source_asset_bounded`

---

## 5. Gate soberano: ownership of responsibility

### 5.1 `motor_001` — dueño del contrato del sujeto

Responsabilidad:

- validar que el caso declara correctamente qué sujeto intenta analizar.

No decide todavía si el activo está resuelto.  
Decide si el contrato es admisible como intento.

### 5.2 `motor_006` — dueño de la resolución de identidad

Responsabilidad:

- probar si el sujeto declarado puede o no sostener una identidad asset/site.

### 5.3 `motor_007` — dueño del gate soberano

Responsabilidad:

- decidir si el pipeline puede seguir como `asset_case`.

Respuesta operativa:

- sí, como `bounded_asset`
- sí, pero solo como `site_candidate`
- no, solo como `issuer_context_only`
- no, sujeto inválido para asset pipeline

### 5.4 `motor_024` / `motor_025` — dueños del enforcement posterior

Responsabilidad:

- detectar y bloquear cualquier fuga donde el pipeline se comporte como asset case sin haber pasado el gate soberano.

---

## 6. Backlog por etapas

## Etapa A — Contrato estricto del sujeto

### Objetivo

Sacar del sistema la inferencia peligrosa:

- `hay dirección -> entonces es asset`

### Archivos

- [asset_contracts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/asset_contracts.py>)
- [motor_001.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py>)
- [models.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/models.py>)
- [pipeline_orchestrator.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py>)

### Tareas

- A1. Crear `subject_definition_contract`.
- A2. Separar `subject_definition_contract` de `target_definition_contract`.
- A3. Añadir campos obligatorios:
  - `subject_kind`
  - `subject_scope`
  - `subject_origin`
  - `asset_anchor_type`
  - `asset_anchor_value`
  - `asset_anchor_confidence`
  - `owner_context_optional`
  - `operator_context_optional`
  - `declared_asset_name`
  - `declared_asset_identifier`
- A4. Eliminar la inferencia por defecto:
  - `address -> asset`
- A5. Introducir estados:
  - `issuer_seeded`
  - `address_seeded`
  - `site_seeded`
  - `asset_seeded`
- A6. Persistir este contrato en runtime manifest.

### Criterio de aceptación

- un ticker o CIK sin ancla física explícita ya no puede aparecer como `asset`.
- una dirección sola ya no puede aparecer como `bounded_asset`.

---

## Etapa B — Admisibilidad contractual en `motor_001`

### Objetivo

`motor_001` deja de ser un validador pasivo y pasa a ser el primer filtro de sujeto.

### Archivos

- [motor_001.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py>)
- [motor_state_semantics.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/motor_state_semantics.md>)

### Tareas

- B1. Añadir `subject_contract_status`.
- B2. Añadir `subject_contract_admissibility`.
- B3. Clasificar:
  - `valid_asset_candidate`
  - `issuer_only`
  - `ambiguous_subject`
  - `invalid_for_asset_pipeline`
- B4. Convertir warnings actuales en outcomes explícitos.
- B5. Añadir razones estructuradas:
  - `missing_asset_anchor`
  - `issuer_context_only`
  - `address_without_asset_evidence`
  - `target_scope_claim_exceeds_declared_anchor`
- B6. Publicar `subject_contract_warning_register`.

### Criterio de aceptación

- `motor_001` puede decir formalmente:
  - “esto no es todavía un asset case”
  sin esperar a `motor_024`.

---

## Etapa C — Resolución de identidad real en `motor_006`

### Objetivo

Dejar de sintetizar `asset_entity_id` como si una dirección + owner equivalieran a un activo resuelto.

### Archivos

- [motor_006.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py>)
- [asset_contracts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/asset_contracts.py>)

### Tareas

- C1. Añadir `subject_resolution_state`.
- C2. Añadir `asset_authenticity_state`.
- C3. Añadir `address_semantics`:
  - `issuer_hq`
  - `mailing_address`
  - `office_suite`
  - `candidate_site`
  - `candidate_building`
- C4. Añadir `asset_identity_evidence_register`.
- C5. Separar IDs:
  - `issuer_entity_id`
  - `site_candidate_id`
  - `asset_candidate_id`
  - `bounded_asset_id`
- C6. Prohibir que exista `bounded_asset_id` sin evidencia de identity class suficiente.
- C7. Añadir `site_vs_issuer_disambiguation`.

### Criterio de aceptación

- un HQ de empresa deja de generar un `asset_entity_id` fuerte.
- el runtime distingue entre dirección de issuer y activo físico probable.

---

## Etapa D — Gate soberano en `motor_007`

### Objetivo

Crear el verdadero gate metodológico que hoy falta.

### Archivos

- [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
- [asset_contracts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/asset_contracts.py>)
- [definition_of_done.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/definition_of_done.md>)

### Tareas

- D1. Crear `target_admissibility_state`.
- D2. Crear `subject_gate_passed`.
- D3. Separar dos gates:
  - `subject_admissibility_gate`
  - `asset_context_readiness_gate`
- D4. Definir outcomes:
  - `issuer_context_only`
  - `address_candidate_only`
  - `site_candidate_only`
  - `asset_candidate_but_unbounded`
  - `bounded_asset`
  - `bounded_asset_with_operable_context`
- D5. Añadir `subject_gate_reason_register`.
- D6. Añadir `allowed_report_classes`.
- D7. Hacer que `target_scope_fitness` deje de ser el gate soberano principal.

### Criterio de aceptación

- el pipeline ya puede saber:
  - `sí, esto es activo admisible`
  - `no, esto sigue siendo issuer/address only`

---

## Etapa E — Superficie de intake: matar `company-first`

### Objetivo

Quitar a la compañía como unidad primaria de operación.

### Archivos

- [companies.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/companies.py>)
- [companies_db.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/companies_db.json>)
- [dashboard.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/dashboard.py>)
- [cli.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/cli.py>)

### Tareas

- E1. Crear `targets_db` o `assets_db` como fuente primaria de selección.
- E2. Relegar `companies_db` a owner/issuer context opcional.
- E3. Sustituir la sidebar de “empresas” por:
  - dirección
  - site
  - asset candidate
  - asset
- E4. Cambiar `pipeline_id` para que deje de nacer del ticker.
- E5. Cambiar `cli.py` para resolver inputs por target, no por ticker.
- E6. Permitir casos manuales:
  - address-first
  - facility-name-first
  - parcel-id-first

### Criterio de aceptación

- el usuario ya no selecciona “Boston Properties”.
- selecciona “800 Boylston Street” o un `target_id` físico.

---

## Etapa F — Rehacer `companies.py`

### Objetivo

Evitar que el generador siga mintiendo con `target_scope = asset`.

### Archivos

- [companies.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/companies.py>)

### Tareas

- F1. Renombrar su propósito:
  - de generator de asset cases
  - a generator de `issuer context seeds`
- F2. Prohibir que genere por defecto:
  - `target_scope = asset`
  - `target_type = commercial_building`
- F3. Si se usa SEC business address:
  - marcar `subject_kind = issuer`
  - marcar `asset_anchor_type = declared_business_address`
  - marcar `subject_contract_admissibility = ambiguous_subject`
- F4. Cambiar `decision_type` default:
  - quitar `investment_evaluation`
  - usar algo como `target_identification_required`

### Criterio de aceptación

- `companies.py generate BXP` deja de crear un pseudo-asset case.

---

## Etapa G — Discovery condicionado por admisibilidad

### Objetivo

Hacer que `motor_028` obedezca el gate del sujeto.

### Archivos

- [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- [motor_dependencies.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/motor_dependencies.json>)

### Tareas

- G1. Añadir input formal desde `motor_007`.
- G2. Cambiar rutas:
  - `issuer_context_only` -> issuer search only
  - `address_candidate_only` -> geocoder/parcel/building registry
  - `site_candidate_only` -> site/jurisdiction/benchmark discovery
  - `bounded_asset` -> full asset-first discovery
- G3. No activar priors físicos completos si el sujeto no pasó.
- G4. Mantener SEC solo como `issuer_context`.

### Criterio de aceptación

- un caso `issuer_only` ya no genera discovery que parezca activo físico.

---

## Etapa H — Fase 1 y Decision Core obedecen admisibilidad

### Objetivo

Que ni el prior físico ni el Decision Core se monten sobre un sujeto incorrecto.

### Archivos

- [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- [motor_013.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_013.py>)
- [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)

### Tareas

- H1. `motor_012` debe producir modos distintos:
  - `issuer_context_prior`
  - `address_candidate_prior`
  - `site_candidate_prior`
  - `bounded_asset_prior`
- H2. `motor_013` debe activar casos de sujeto:
  - `invalid_subject_for_asset_case`
  - `issuer_asset_scope_confusion`
  - `address_not_yet_asset`
- H3. `motor_014` debe priorizar esos blockers por encima de deuda y finanzas.

### Criterio de aceptación

- el primer blocker del caso pasa a ser el sujeto incorrecto cuando aplica.

---

## Etapa I — Packaging y TAD obedecen el gate

### Objetivo

Que la salida visible y la priorización no vuelvan a comportarse como si el activo ya existiera.

### Archivos

- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_018.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py>)
- [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)

### Tareas

- I1. Nuevas clases documentales visibles:
  - `Issuer Context Memo`
  - `Address Candidate Brief`
  - `Site Candidate Brief`
- I2. `motor_018` solo puede mostrar charts técnicos de activo si el sujeto es admisible.
- I3. `motor_019` debe explicar primero:
  - por qué el target no es todavía asset
  - qué falta para bounded asset
- I4. `motor_033` debe priorizar:
  - `classify target`
  - `confirm asset identity`
  - `resolve site vs issuer`

### Criterio de aceptación

- el sistema nunca vuelve a sonar asset-technical cuando el sujeto aún no lo soporta.

---

## Etapa J — Gobernanza y auto-bloqueo

### Objetivo

Que el sistema se detenga solo ante un breach de sujeto.

### Archivos

- [motor_020.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_020.py>)
- [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)

### Tareas

- J1. Nuevos eventos:
  - `subject_mismatch_detected`
  - `issuer_seeded_asset_case_detected`
  - `asset_identity_not_bounded`
- J2. Nuevos outcomes:
  - `freeze_publication`
  - `degrade_to_issuer_context_memo`
  - `degrade_to_address_candidate_brief`
  - `degrade_to_site_candidate_brief`
- J3. Hacer que `delivery_manifest` publique:
  - `subject_kind`
  - `subject_admissibility_state`
  - `asset_identity_evidence_class`

### Criterio de aceptación

- si el sujeto es inválido, el sistema no publica un asset brief por accidente.

---

## 7. Orden de implementación recomendado

1. Etapa A
2. Etapa B
3. Etapa C
4. Etapa D
5. Etapa E
6. Etapa F
7. Etapa G
8. Etapa H
9. Etapa I
10. Etapa J

Racional:

- primero contrato,
- luego identidad,
- luego gate soberano,
- y solo después discovery, inference y reporting.

---

## 8. Casos de prueba obligatorios

### Caso 1 — Ticker only

Input:

- `BXP`

Expected:

- `issuer_context_only`
- no asset pipeline
- `Issuer Context Memo`

### Caso 2 — SEC business address only

Input:

- issuer + business address de filing

Expected:

- `address_candidate_only`
- no `bounded_asset`
- máximo `Address Candidate Brief`

### Caso 3 — Address only

Input:

- `800 Boylston Street, Boston, MA`

Expected:

- `address_candidate_only` o `site_candidate_only`
- no issuer dominance by design

### Caso 4 — Address + parcel/building corroboration

Expected:

- `site_candidate_only` o `asset_candidate_but_unbounded`

### Caso 5 — Address + benchmark/permit/assessor linkage

Expected:

- `bounded_asset`

### Caso 6 — False asset alias

Input:

- company name with HQ address

Expected:

- blocked from asset pipeline

---

## 9. Definition of Done

Esto está terminado cuando:

- una compañía ya no puede entrar al pipeline como activo por accidente,
- una dirección sola ya no se promociona a `asset`,
- `motor_007` decide explícitamente la admisibilidad del sujeto,
- el dashboard deja de estar organizado alrededor de compañías como objetos analizables,
- `companies.py` deja de fabricar pseudo-assets,
- y todos los entregables visibles obedecen el gate soberano del sujeto.

---

## 10. Riesgos que este backlog debe evitar

- Resolver esto solo en UI.
- Resolverlo solo en `motor_024/025`, demasiado tarde.
- Seguir usando SEC business address como pseudo-asset.
- Confundir `site_candidate` con `bounded_asset`.
- Mantener `pipeline_id` por ticker como camino principal.
- Introducir nuevas categorías sin enforcement real.

---

## 11. Recomendación final

El primer sprint correcto no es tocar charts ni copy.  
Es cerrar el triángulo soberano:

- [motor_001.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py>)
- [motor_006.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py>)
- [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)

Mientras eso no esté cerrado, todo lo demás seguirá siendo vulnerable a confundir emisor con activo.
