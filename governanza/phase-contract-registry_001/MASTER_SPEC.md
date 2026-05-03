# PHASE CONTRACT REGISTRY — MASTER SPEC

## 1. Propósito exacto
Definir el motor que registra, versiona, valida y sirve contratos formales entre Fase 1, Fase 2, Fase 3 y Fase 4 de ZLab. Su trabajo es congelar qué objetos, transiciones, metadata, límites epistemológicos y compatibilidades son válidos en cada handoff, sin hacer inferencia, sin hacer reporting y sin reinterpretar la constitución del framework.

## 2. Qué problema resuelve y qué no resuelve
### Resuelve
- Formalizar contratos de fase, objeto y transición.
- Hacer validable el handoff entre fases sin depender de interpretación manual.
- Detectar drift contractual, incompatibilidades y cambios breaking.
- Preservar metadata obligatoria y límites epistemológicos permitidos.
- Servir snapshots coherentes de contratos publicados para consumo de código.
- Hacer trazable la evolución contractual y sus migraciones.

### No resuelve
- Epistemología del framework.
- Inferencia, matching, parsing o evaluación del caso.
- Reporting, verification o generación de artifacts finales.
- UI, API, dashboards o infraestructura productiva.
- Auto-extracción de contratos desde prose.
- “Corrección inteligente” por LLM.

## 3. Rol dentro del framework
- Es un motor de gobernanza contractual, no una fase del pipeline.
- Se ubica por debajo de las fases como infraestructura de control de interfaces.
- Define qué puede circular entre fases, no qué significa el caso.
- Congela límites de interoperabilidad, no lógica de negocio de cada fase.
- Hace explorable y auditable la evolución del framework sin reabrir fases cerradas.

## 4. Límites duros y responsabilidades permitidas/prohibidas
### Permitido
- Registrar contratos versionados.
- Validar consistencia contractual y compatibilidad.
- Emitir registros de validación, diff, incompatibilidad y migración.
- Servir snapshots inmutables de contratos publicados.
- Preservar y verificar metadata y techos epistemológicos declarados.

### Prohibido
- Inferir contratos a partir de texto libre en el write path.
- Cambiar semántica de fases cerradas.
- Elevar estatus epistemológico por conveniencia técnica.
- Mezclar contrato con ejecución, serving con validación o historial con estado activo.
- Usar un modelo único como autoridad soberana.
- Reemplazar reglas duras por heurística probabilística.

## 5. Modelo de dominio mínimo

### 5.1 Objetos internos mínimos
| Objeto | Propósito |
|---|---|
| `phase_contract` | Contrato canónico de una fase publicada o en preparación. |
| `object_contract` | Contrato formal de un objeto permitido dentro de una fase. |
| `transition_contract` | Contrato formal de handoff entre contratos de fase/objeto. |
| `epistemic_policy_fragment` | Fragmento declarativo de límites epistemológicos aplicables a una fase, objeto o transición. |
| `metadata_preservation_policy` | Reglas de preservación, mutabilidad y obligatoriedad de metadata. |
| `validation_run_record` | Registro inmutable de una corrida de validación contractual. |
| `violation_record` | Registro de una violación detectada durante validación. |
| `contract_diff_record` | Diferencia estructural entre dos versiones contractuales. |
| `compatibility_record` | Resultado formal de compatibilidad entre dos contratos o conjuntos contractuales. |
| `migration_spec` | Especificación explícita para migrar entre versiones incompatibles o condicionalmente compatibles. |
| `contract_serving_snapshot` | Snapshot inmutable y servible de contratos publicados y validados. |

### 5.2 Clasificación: entidad, value object y enum
| Tipo | Objetos |
|---|---|
| Entidad | `phase_contract`, `object_contract`, `transition_contract`, `validation_run_record`, `violation_record`, `contract_diff_record`, `compatibility_record`, `migration_spec`, `contract_serving_snapshot` |
| Value object | `epistemic_policy_fragment`, `metadata_preservation_policy` |
| Enum | `phase_id`, `contract_status`, `validation_status`, `violation_severity`, `compatibility_status`, `migration_kind`, `serving_status`, `scope_kind`, `change_kind` |

### 5.3 Enums mínimos
| Enum | Valores mínimos |
|---|---|
| `phase_id` | `phase_1`, `phase_2`, `phase_3`, `phase_4` |
| `contract_status` | `draft`, `staged`, `published`, `deprecated`, `retired` |
| `validation_status` | `passed`, `failed` |
| `violation_severity` | `error`, `warning` |
| `compatibility_status` | `compatible`, `conditionally_compatible`, `incompatible` |
| `migration_kind` | `patch`, `minor`, `major`, `breaking` |
| `serving_status` | `inactive`, `active`, `superseded` |
| `scope_kind` | `phase_contract`, `object_contract`, `transition_contract`, `contract_set`, `snapshot` |
| `change_kind` | `additive`, `restrictive`, `removal`, `rename`, `semantic_change`, `metadata_change` |

## 6. Campos mínimos obligatorios por objeto

### 6.1 `phase_contract`
- `phase_contract_id`
- `phase_id`
- `contract_version`
- `contract_status`
- `canonical_name`
- `source_of_authority_ref`
- `allowed_output_names`
- `forbidden_output_names`
- `required_metadata_keys`
- `epistemic_policy_fragments`
- `object_contract_ids`
- `transition_contract_ids`
- `supersedes_contract_id` nullable
- `created_at`
- `published_at` nullable
- `checksum`

### 6.2 `object_contract`
- `object_contract_id`
- `phase_contract_id`
- `object_name`
- `object_role`
- `canonical_purpose`
- `required_fields`
- `optional_fields`
- `forbidden_fields`
- `required_metadata_keys`
- `metadata_preservation_policy`
- `allowed_epistemic_state_tokens`
- `forbidden_epistemic_state_tokens`
- `created_at`
- `checksum`

### 6.3 `transition_contract`
- `transition_contract_id`
- `source_phase_contract_id`
- `target_phase_contract_id`
- `transition_name`
- `source_object_refs`
- `target_object_refs`
- `required_preconditions`
- `required_metadata_keys`
- `prohibited_transforms`
- `allowed_status_transforms`
- `blocked_status_transforms`
- `epistemic_policy_fragments`
- `created_at`
- `checksum`

### 6.4 `epistemic_policy_fragment`
- `policy_key`
- `scope_kind`
- `scope_ref`
- `allowed_state_tokens`
- `forbidden_state_tokens`
- `must_preserve_uncertainty`
- `must_preserve_conflict`
- `output_ceiling_rule`

### 6.5 `metadata_preservation_policy`
- `required_keys`
- `immutable_keys`
- `passthrough_keys`
- `derivable_keys`
- `missing_key_behavior`
- `unknown_key_behavior`

### 6.6 `validation_run_record`
- `validation_run_id`
- `scope_kind`
- `target_refs`
- `validator_version`
- `executed_at`
- `validation_status`
- `violation_ids`
- `input_checksum_set`

### 6.7 `violation_record`
- `violation_record_id`
- `validation_run_id`
- `scope_kind`
- `scope_ref`
- `rule_code`
- `violation_severity`
- `message`
- `blocking`
- `evidence_ref`

### 6.8 `contract_diff_record`
- `contract_diff_record_id`
- `scope_kind`
- `source_ref`
- `target_ref`
- `change_set`
- `breaking_change_detected`
- `generated_at`

### 6.9 `compatibility_record`
- `compatibility_record_id`
- `scope_kind`
- `source_ref`
- `target_ref`
- `compatibility_status`
- `breaking_reasons`
- `migration_required`
- `generated_at`

### 6.10 `migration_spec`
- `migration_spec_id`
- `source_ref`
- `target_ref`
- `migration_kind`
- `required_steps`
- `manual_steps`
- `data_loss_risk`
- `approval_required`
- `created_at`

### 6.11 `contract_serving_snapshot`
- `contract_serving_snapshot_id`
- `snapshot_version`
- `included_phase_contract_refs`
- `included_object_contract_refs`
- `included_transition_contract_refs`
- `source_validation_run_id`
- `serving_status`
- `created_at`
- `checksum`

## 7. Invariantes duros del dominio
- Un `published phase_contract` es inmutable; cualquier cambio crea nueva versión.
- Ningún `object_contract` existe fuera de exactamente un `phase_contract`.
- Ningún `transition_contract` puede referir fases u objetos inexistentes.
- Ningún `transition_contract` puede permitir outputs, estados o metadata que contradigan contratos fuente/destino.
- Ningún `object_contract` puede declarar campos prohibidos por su `phase_contract`.
- Todo contrato publicado debe tener `checksum`.
- Todo `validation_run_record` es append-only y nunca muta contratos.
- Toda `violation_record` pertenece a exactamente un `validation_run_record`.
- `compatibility_record` y `contract_diff_record` son derivados; nunca son fuente de verdad.
- `migration_spec` no altera contratos; describe cómo pasar entre versiones.
- Un `contract_serving_snapshot` solo puede incluir contratos `published`.
- Un `contract_serving_snapshot` activo debe venir de una validación `passed`.
- No puede existir más de un `contract_serving_snapshot` `active` para la misma combinación de alcance/versiones.
- Ningún cambio compatible puede eliminar metadata obligatoria, outputs permitidos usados downstream ni restricciones epistemológicas requeridas.
- Ningún contrato puede elevar silenciosamente techos epistemológicos respecto de su versión previa sin marcar cambio `breaking`.

## 8. Relaciones entre objetos
- `phase_contract` 1..* `object_contract`
- `phase_contract` 0..* `transition_contract` como origen
- `phase_contract` 0..* `transition_contract` como destino
- `phase_contract` 1..* `epistemic_policy_fragment`
- `object_contract` 1 `metadata_preservation_policy`
- `object_contract` 0..* `epistemic_policy_fragment`
- `transition_contract` 0..* `epistemic_policy_fragment`
- `validation_run_record` 0..* `violation_record`
- `contract_diff_record` compara exactamente dos refs homogéneos
- `compatibility_record` compara exactamente dos refs homogéneos
- `migration_spec` conecta exactamente un origen y un destino
- `contract_serving_snapshot` referencia un conjunto coherente de contratos publicados y una validación exitosa

## 9. Separación obligatoria de capas internas
| Capa | Contiene | No puede contener |
|---|---|---|
| Contrato | `phase_contract`, `object_contract`, `transition_contract`, policy value objects | resultados de validación, serving state, historial derivado |
| Validación | `validation_run_record`, `violation_record` | mutación contractual, serving activo |
| Historial | `contract_diff_record`, `compatibility_record`, `migration_spec` | verdad canónica activa |
| Serving | `contract_serving_snapshot` | lógica de authoring, validación inline, edición manual del contrato |

Regla: contrato define; validación evalúa; historial compara; serving congela y sirve.

## 10. Reglas mínimas de versionado, compatibilidad y migración

### 10.1 Versionado
- Usar `major.minor.patch`.
- `patch`: corrección no semántica ni estructural.
- `minor`: cambio aditivo compatible.
- `major`: cambio breaking o cambio semántico relevante.

### 10.2 Compatibilidad
`compatible` si no rompe lectura ni consumo downstream bajo contrato previo.

`conditionally_compatible` si requiere `migration_spec` no destructiva o ajuste explícito.

`incompatible` si elimina, endurece o redefine elementos consumidos sin migración suficiente.

### 10.3 Reglas breaking mínimas
Son `major` por defecto:
- eliminar output permitido;
- eliminar campo obligatorio;
- volver obligatorio un campo antes opcional;
- cambiar meaning de un objeto o transición;
- estrechar metadata obligatoria de forma incompatible;
- endurecer o ampliar techos epistemológicos de forma no compatible;
- fusionar o dividir contratos sin migración explícita.

### 10.4 Migración
- Toda migración entre versiones `major` requiere `migration_spec`.
- Toda migración debe declarar si hay riesgo de pérdida de información.
- Toda migración debe distinguir pasos automáticos y manuales.
- El motor registra migración; no ejecuta transformaciones productivas complejas en el primer ciclo.

## 11. Qué debe quedar explícitamente fuera del primer ciclo de implementación
- Parser automático de contratos desde documentos Markdown.
- Generación automática de contratos por LLM.
- DSL compleja de políticas.
- Codegen automático para todos los consumidores.
- Multi-tenant, auth, permisos finos o colaboración en tiempo real.
- Event bus distribuido.
- Migraciones autoejecutables sobre datos productivos.
- Resolución probabilística de compatibilidad.
- UI de authoring o dashboards de gobierno.
- Runtime enforcement embebido dentro de cada fase.

## 12. Estructura mínima sugerida para pasar luego a código
```text
governanza/
  phase-contract-registry/
    MASTER_SPEC.md
    domain/
      entities/
      value_objects/
      enums/
      invariants/
      services/
    application/
      commands/
      queries/
      validators/
      diff/
      compatibility/
      migrations/
      serving/
    adapters/
      persistence/
      serialization/
      loading/
    tests/
      fixtures/
      contract_sets/
      invariants/
```

### Reglas de estructura
- `domain/` no conoce persistencia ni transporte.
- `application/` orquesta casos de uso determinísticos.
- `adapters/` implementa IO.
- `tests/fixtures/contract_sets` debe contener juegos mínimos por fase y por transición.

## 13. Riesgos de arquitectura caros si se diseña mal desde el inicio
- Convertir `phase_contract` en god object.
- Mezclar contrato canónico con resultado de validación.
- Usar blobs JSON libres para políticas críticas.
- Tratar `compatibility_record` como verdad y no como derivado.
- Permitir snapshots mutables.
- Versionar solo snapshots y no contratos individuales.
- Acoplar fuerte el dominio a base de datos o framework web.
- Delegar interpretación contractual al LLM.
- Permitir migraciones implícitas o silenciosas.
- No modelar metadata preservation como regla de primer orden.
- No distinguir cambio aditivo de cambio breaking.
- Mezclar historial con serving activo.

## 14. Cierre operativo
El primer ciclo queda suficientemente congelado cuando:
- el modelo anterior puede representarse sin ambigüedad en código;
- los invariantes pueden implementarse como validaciones determinísticas;
- el ciclo `registrar -> validar -> comparar -> migrar -> servir snapshot` queda claro;
- y ninguna parte crítica depende de UI, LLM o infraestructura productiva para existir.

En ese punto, el código puede empezar de inmediato.
