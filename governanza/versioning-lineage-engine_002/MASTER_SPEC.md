# VERSIONING + LINEAGE ENGINE — MASTER SPEC

## 1. Qué es exactamente el Versioning + Lineage Engine
Motor fundacional que asigna identidad estable, registra versiones inmutables, materializa dependencias y preserva genealogía completa de objetos versionables del framework. Su función es hacer reconstruible, comparable y auditable cualquier objeto relevante de ZLab sin reabrir la epistemología ni sustituir motores de governance, quality, reporting o verification.

## 2. Qué problema resuelve y qué problema no resuelve
### Resuelve
- versionado explícito de objetos y bundles relevantes;
- lineage completo upstream/downstream;
- diff entre versiones del mismo objeto;
- stale detection cuando cambia algo upstream;
- impact analysis sobre dependencias;
- rebuildabilidad ex post;
- comparabilidad histórica sin sobrescritura del pasado.

### No resuelve
- inferencia, reporting o verification;
- parsing, ingestión o normalización primaria;
- calidad/fitness por sí sola;
- aptitud contractual por fase;
- identidad semántica automática en casos ambiguos;
- UI, API, storage productivo o cloud.

## 3. Qué rol cumple dentro del framework completo
- Es un motor transversal de trazabilidad, no una fase.
- Opera por debajo de Fase 1–4 y por debajo de motores funcionales.
- Registra qué produjo cada objeto, con qué dependencias y en qué versión.
- No decide si un objeto es epistemológicamente válido; deja esa decisión a governance, phase contracts y quality engines.
- Hace posible reconstrucción, auditoría y re-evaluación sin mutar historial.

## 4. Qué NO debe hacer
- No reabrir fases cerradas.
- No alterar outputs ni contratos.
- No corregir silenciosamente objetos.
- No sobrescribir versiones previas.
- No inferir identidad estable a partir de narrativa libre sin control.
- No mezclar lineage con quality, observabilidad general o governance.
- No usar referencias flotantes tipo `latest` como dependencia persistida.

## 5. Qué SÍ debe hacer
- Asignar `object_identity` estable a todo objeto versionable.
- Registrar `object_version` inmutable.
- Registrar `dependency_edge` versionado y tipado.
- Registrar versiones de contratos, taxonomías, reglas, librerías y modelos usados.
- Soportar diff, stale state, impact analysis y rebuild manifest.
- Preservar historial completo y traversal reproducible.

## 6. Qué debe ser versionable y a qué granularidad
### Regla general
Se versiona todo objeto materializado que:
- cruza boundaries de fase o motor;
- se reutiliza downstream;
- participa en decisiones, reporting o verification;
- o necesita reconstrucción/auditoría posterior.

### No se versiona
- caches efímeros;
- retries;
- logs de ejecución;
- UI state;
- prompts temporales;
- traces de depuración;
- intermedios anónimos no referenciados downstream.

### Granularidad mínima
| Nivel | Unidad versionable | Regla mínima de nueva versión |
|---|---|---|
| Fuente | `source_record`, `source_version`, `raw_asset`, `parsed_object`, `normalized_object` | cambia asset, metodología, parsing material o checksum |
| Fase 1 | bundles, priors, flags, markers, benchmark bundles | cambia contenido, composición o dependencia upstream |
| Fase 2 | registers, maps, matrices, queues | cambia lógica material, evidencia usada o dependencia estructural |
| Fase 3 | output blocks, artifacts, audience views, export bundles, report packages | cambia contenido visible, composición o versión de inputs |
| Fase 4 | registers y decision maps del bridge | cambia claim set, pathway set, metadata crítica o dependencia upstream |
| Dependencias externas | contract version, taxonomy version, rule pack version, library version, model/engine version | cambia versión fijada o fingerprint material |

### Regla de bundle
Un bundle u output compuesto obtiene nueva versión si cambia cualquiera de:
- su member set;
- el orden material si afecta reconstrucción;
- cualquier dependencia marcada `required`;
- su contract/taxonomy/rule pack pinning;
- o su content checksum final.

## 7. Qué objetos internos mínimos necesita

### 7.1 Entidades mínimas
| Objeto | Propósito |
|---|---|
| `lineage_object_identity` | Identidad estable de un objeto lógico a través de versiones. |
| `lineage_object_version` | Versión inmutable y reconstruible de una identidad. |
| `dependency_edge` | Relación tipada y version-pinned entre una versión y una dependencia. |
| `version_diff_record` | Diff estructural entre dos versiones del mismo `object_identity`. |
| `stale_state_record` | Estado de freshness/staleness de una `object_version`. |
| `impact_record` | Registro de impacto downstream disparado por un cambio upstream. |

### 7.2 Value objects mínimos
| Objeto | Propósito |
|---|---|
| `external_dependency_ref` | Referencia versionada a contrato, taxonomía, regla, librería o modelo. |
| `rebuild_manifest` | Conjunto mínimo de pins y fingerprints para reconstruir una versión exacta. |
| `lineage_locator` | Referencia homogénea a `object_identity`, `object_version` o dependencia externa. |
| `change_descriptor` | Cambio unitario dentro de un diff. |

### 7.3 Enums mínimos
- `object_kind`
- `dependency_type`
- `dependency_target_kind`
- `identity_status`
- `version_status`
- `stale_state`
- `impact_severity`
- `change_severity`
- `change_kind`

### 7.4 Campos mínimos obligatorios
#### `lineage_object_identity`
- `object_identity_id`
- `object_kind`
- `phase_scope` nullable
- `stable_key`
- `canonical_name`
- `identity_status`
- `replaced_by_identity_id` nullable
- `created_at`

#### `lineage_object_version`
- `object_version_id`
- `object_identity_id`
- `version_index`
- `content_checksum`
- `schema_fingerprint`
- `version_status`
- `created_at`
- `producer_engine_name`
- `producer_engine_version`
- `rebuild_manifest`

#### `dependency_edge`
- `dependency_edge_id`
- `from_object_version_id`
- `target_kind`
- `target_ref`
- `dependency_type`
- `required`
- `contributes_to_rebuild`
- `input_role`
- `created_at`

#### `version_diff_record`
- `version_diff_record_id`
- `object_identity_id`
- `source_object_version_id`
- `target_object_version_id`
- `change_set`
- `change_severity`
- `breaking_detected`
- `generated_at`

#### `stale_state_record`
- `stale_state_record_id`
- `object_version_id`
- `stale_state`
- `reasons`
- `upstream_trigger_refs`
- `detected_at`
- `cleared_at` nullable

#### `impact_record`
- `impact_record_id`
- `trigger_ref`
- `affected_object_version_id`
- `impact_severity`
- `requires_rebuild`
- `migration_required`
- `detected_at`

## 8. Qué metadatos debe preservar obligatoriamente
- `created_at`
- `created_by_engine`
- `producer_engine_version`
- `content_checksum`
- `schema_fingerprint`
- `contract_version_refs`
- `taxonomy_version_refs`
- `rule_pack_version_refs`
- `library_version_refs`
- `model_version_refs` cuando aplique
- `source dependency refs`
- `phase_scope`
- `object_kind`
- `stable_key`
- `rebuild manifest fingerprint`

Ninguna versión servible puede existir sin `content_checksum`, dependencias requeridas pinneadas y referencias a contratos/taxonomías/reglas usadas si participaron materialmente.

## 9. Diferencia entre identity, version y estados relacionados
- `object_identity`: el mismo objeto lógico a lo largo del tiempo. No contiene contenido mutable.
- `object_version`: una materialización inmutable y fechada de esa identidad.
- `derived_object`: identidad cuya existencia depende de otras versiones u objetos fuente.
- `replacement_object`: nueva identidad que sustituye a otra cuando cambia el boundary semántico y la comparabilidad directa ya no debe asumirse.
- `deprecated_object`: identidad todavía histórica pero no destinada a nuevas versiones.
- `stale_object`: versión históricamente válida pero desactualizada respecto de dependencias relevantes actuales.

### Regla de nueva versión
Es nueva versión si se mantiene el mismo `stable_key` y cambia cualquiera de:
- contenido material;
- dependency set;
- versión de dependencias requeridas;
- contract/taxonomy/rule/model pins;
- schema fingerprint;
- build/rebuild manifest.

### Regla de nuevo objeto
Es nueva identidad si cambia cualquiera de:
- boundary semántico;
- objeto/subject principal;
- granularidad comparativa;
- `object_kind`;
- o el cambio hace engañosa la comparación directa versión-a-versión.

## 10. Cómo representar dependencies y lineage
Lineage se representa como grafo dirigido y version-pinned:
- nodo: `lineage_object_version`
- edge: `dependency_edge`
- target del edge: otra `object_version` o `external_dependency_ref`

### Tipos mínimos de dependencia
- `source_input`
- `derives_from`
- `aggregates`
- `uses_contract`
- `uses_taxonomy`
- `uses_rule_pack`
- `uses_library`
- `uses_model`
- `replaces`

### Reglas
- Toda dependencia persistida debe apuntar a versión explícita, nunca a `latest`.
- Debe distinguirse `required` de `optional`.
- Debe distinguirse dependencia de contenido de dependencia de policy/contract/taxonomy.
- Todo objeto derivado debe exponer lineage upstream completo hasta fuentes y pins externos materiales.

## 11. Cómo representar diff
El diff compara dos `object_version` del mismo `object_identity`. No compara tipos heterogéneos por defecto.

### `change_descriptor` mínimo
- `path`
- `change_kind`
- `old_ref` nullable
- `new_ref` nullable
- `severity`
- `description`

### Cambios mínimos a detectar
- agregado o remoción de members;
- cambio de dependency pins;
- cambio de metadata requerida preservada;
- cambio de contract/taxonomy/rule pack version;
- cambio de status material;
- cambio de content checksum o schema fingerprint;
- cambio de composición de bundle u output.

## 12. Cómo detectar stale state
Una `object_version` queda stale si cualquiera de sus dependencias requeridas:
- tiene nueva versión aplicable;
- fue reemplazada;
- cambió de forma breaking/restrictive;
- desapareció o quedó ilegible;
- o su contract/taxonomy/rule pin ya no coincide con la versión vigente esperada por policy.

### Estados mínimos
- `fresh`
- `stale_rebuild_recommended`
- `stale_migration_required`
- `stale_blocked`

### Regla mínima de severidad
- upstream additive -> `stale_rebuild_recommended`
- upstream restrictive -> `stale_migration_required`
- upstream breaking/unknown o dependencia faltante -> `stale_blocked`

## 13. Cómo soportar impact analysis
Impact analysis es traversal downstream desde:
- una `source_version`
- una `object_version`
- una `contract_version`
- una `taxonomy_version`
- una `rule_pack_version`

Debe producir, como mínimo:
- versiones directamente afectadas;
- versiones transitivamente afectadas;
- severidad del impacto;
- si requiere rebuild;
- si requiere migración;
- si rompe comparabilidad histórica.

No ejecuta rebuild; solo materializa el impacto y sus razones.

## 14. Cómo soportar rebuild
El motor soporta rebuild registrando un `rebuild_manifest` suficiente para repetir la construcción de una versión exacta.

### Mínimos del `rebuild_manifest`
- pins completos de dependencias requeridas;
- contract/taxonomy/rule/library/model refs;
- `producer_engine_name`
- `producer_engine_version`
- `schema_fingerprint`
- `execution_fingerprint`
- `content_checksum` esperado

El motor no recomputa lógica de negocio; solo hace posible que otro motor la re-ejecute con los mismos pins.

## 15. Cómo manejar historial sin romper comparabilidad
- Toda `object_version` es inmutable.
- Nunca se sobrescribe una versión previa.
- `stale` no significa inválido históricamente.
- Comparabilidad por defecto existe solo dentro del mismo `object_identity`.
- Si hay `replacement_object`, la relación debe quedar explícita y la comparabilidad histórica debe marcarse como condicionada o interrumpida.
- Los cambios de taxonomía o contrato no reescriben versiones antiguas.

## 16. Cómo manejar breaking upstream changes
Cuando un upstream change es breaking:
1. se registra nueva versión upstream;
2. se materializa diff/severity;
3. se recorren dependencias downstream requeridas;
4. se crean `impact_record`;
5. se marcan downstream versions `stale_blocked` o `stale_migration_required`;
6. nunca se muta el pasado para “alinearlo”.

## 17. Cómo interactúa con otros motores
### Phase Contract Registry
- Este motor consume `contract_version` como dependencia externa pinneada.
- No evalúa validez contractual; solo registra qué contrato se usó y expone stale si cambió.

### Taxonomy Service
- Consume `taxonomy_version` y alias map version.
- No resuelve taxonomía por sí mismo; solo fija pins y preserva comparabilidad histórica.

### Quality / Fitness Engine
- Entrega hechos de lineage: dependencia faltante, lineage roto, rebuild impossible, stale state.
- No asigna quality score.

### Propagation / Re-evaluation Engine
- Entrega triggers e `impact_record`.
- No orquesta rebuilds complejos por sí solo.

### Governance Layer
- Entrega trazabilidad auditable.
- No decide qué lineage incompleto es aceptable; governance lo decide.

## 18. Qué partes pueden automatizarse y cuáles no
### Automatizable
- asignación de `object_version_id`
- checksum y fingerprint
- creación de `dependency_edge`
- diff estructural
- stale propagation
- impact traversal
- detección de rebuild manifest incompleto

### No automatizable por defecto
- resolución de ambigüedad de identidad estable;
- decisión entre nueva versión y nueva identidad en cambios semánticos fuertes;
- excepciones de retención;
- reinterpretación histórica cuando cambia una taxonomía o boundary.

## 19. Qué rol permitido y prohibido puede tener un LLM dentro de este motor
### Permitido
- resumir lineage ya estructurado;
- ayudar a explicar diffs ya materializados;
- asistir a operadores en lectura de impacto.

### Prohibido
- asignar identidad estable en el write path;
- decidir stale/blocking state como autoridad;
- completar dependencias faltantes por heurística;
- reescribir historial;
- mutar lineage canónico.

## 20. Qué acceptance tests mínimos debe tener
1. crear dos versiones del mismo `object_identity` con distinto checksum y preservar ambas.
2. registrar dependencia requerida a una `source_version` y marcar stale cuando aparece nueva versión upstream.
3. marcar downstream impact sobre bundles y outputs transitivos.
4. reconstruir exacto un `report_package` histórico desde `rebuild_manifest`.
5. bloquear `object_version` sin dependency pins requeridos.
6. detectar lineage roto cuando falta una dependencia requerida.
7. distinguir nueva versión vs nuevo objeto cuando cambia el boundary semántico.
8. preservar comparabilidad histórica frente a cambio de taxonomía.
9. marcar `stale_migration_required` cuando cambia un `contract_version` o `rule_pack_version` de forma restrictiva.
10. recorrer lineage upstream y downstream sin pérdida de referencias.

## 21. Qué observabilidad debe exponer
No observabilidad general del sistema, sino señales propias del motor:
- conteo de `object_version` por `object_kind`;
- conteo de versiones stale por estado;
- conteo de dependency edges rotos;
- coverage de lineage completo vs incompleto;
- rebuildability rate;
- depth máxima y media de lineage;
- cantidad de impactos abiertos por trigger upstream.

Estas señales deben salir como registros estructurados o snapshots, no como UI requerida.

## 22. Qué failure modes deben bloquearse desde el día 1
- `object_version` sin `object_identity`;
- dependencias requeridas sin versión explícita;
- lineage con edges a `latest`;
- sobrescritura de historial;
- diff entre objetos heterogéneos sin control;
- `rebuild_manifest` incompleto para objetos marcados reconstruibles;
- objeto derivado sin contract/taxonomy/rule pins cuando corresponden;
- stale calculado pero no persistido;
- replacement object sin vínculo explícito con identidad previa.

## 23. Qué errores de arquitectura serían muy caros de corregir después
- confundir `object_identity` con `object_version`;
- versionar solo datasets y no objetos derivados;
- almacenar dependencias como blobs libres sin tipos;
- usar lineage como narrativa y no como grafo pinneado;
- no preservar pins de contratos, taxonomías y reglas;
- tratar `stale` como sinónimo de `deprecated`;
- permitir delete/overwrite de versiones históricas;
- acoplar lineage a storage o UI antes de cerrar el dominio.

## 24. Cómo diseñarlo para MVP sin volverlo mediocre
El MVP debe incluir desde el inicio:
- identidad estable;
- versiones inmutables;
- dependency graph tipado;
- pins externos;
- stale state explícito;
- diff mínimo;
- impact analysis mínimo;
- rebuild manifest;
- historial completo.

Puede dejar fuera en MVP:
- serving sofisticado;
- optimizaciones de traversal;
- políticas complejas de retención;
- migración automática;
- observabilidad avanzada.

## 25. Cómo escalarlo sin volverlo un monolito
- mantener separado dominio de lineage, diff, stale e impacto;
- agregar reglas por `object_kind`, no un mega-engine único;
- mantener `dependency_edge` como objeto de primer orden;
- delegar rebuild/orchestration a otros motores;
- exponer snapshots y records, no servicios omnipotentes;
- preservar que governance, quality y lineage sigan desacoplados.

## 26. Estructura mínima sugerida para pasar luego a código
```text
governanza/
  versioning-lineage-engine/
    MASTER_SPEC.md
    versioning_lineage_engine/
      domain/
        identities.py
        versions.py
        dependencies.py
        diff.py
        stale.py
        impacts.py
        enums.py
      application/
        versioning/
        lineage/
        stale/
        impact/
        rebuild/
      tests/
        fixtures/
        acceptance/
```

Reglas:
- `domain/` no conoce storage ni transporte;
- `application/` orquesta casos de uso determinísticos;
- `tests/acceptance` prueba reconstrucción, stale, impacto y comparabilidad.

## 27. Ejemplos normativos

### Ejemplo 1 — Fuente pública cambia de metodología o versión
Una fuente pública `source_record:utility_tariff_feed` publica `source_version:v5` con nueva metodología de cálculo.

El motor debe:
- registrar nueva `source_version` con nuevo checksum y metodología;
- marcar stale las `parsed_object` y `normalized_object` que dependen de `v4`;
- propagar impacto a bundles de Fase 1 que usan esas normalizaciones;
- crear `impact_record` directos para `benchmark_bundle` y transitivos para `facility_prior`, `hypothesis_register` y outputs visibles si dependen de ellos.

Si el cambio fue solo aditivo, el stale puede ser `stale_rebuild_recommended`. Si fue breaking, downstream required edges pasan a `stale_blocked`.

### Ejemplo 2 — Se corrige un `benchmark_bundle` de Fase 1
`benchmark_bundle:office_energy_intensity` genera nueva versión porque cambió una corrección de unidades.

El motor debe permitir ver:
- que `facility_prior:facility_123` fue derivado de la versión anterior;
- que `inference_case_register` y `tension_map` consumieron ese `facility_prior`;
- que esos objetos quedan afectados vía lineage downstream.

No debe recomputarlos automáticamente, pero sí producir `impact_record` y stale flags suficientes para que otro motor dispare rebuild o review.

### Ejemplo 3 — Output Block de Fase 3 construido con `tension_map` viejo
`output_block:ops_summary` depende de `tension_map:v7`. Luego aparece `tension_map:v8`.

El motor debe mostrar:
- `output_block:ops_summary@v3` -> dependency edge -> `tension_map:v7`
- nueva versión disponible upstream: `tension_map:v8`
- stale state: `stale_rebuild_recommended` o `stale_migration_required` según el diff entre `v7` y `v8`

El objeto sigue siendo históricamente válido; lo que cambia es su frescura respecto de la última base disponible.

### Ejemplo 4 — Fase 4 usa `claim_upgrade_candidate` derivado de `facility_prior` reemplazado
Un `claim_upgrade_candidate_register` en Fase 4 se construyó a partir de un `facility_prior` que luego fue reemplazado por nueva identidad porque cambió su boundary semántico.

El motor debe permitir ver simultáneamente:
- el `facility_prior` original y su cadena histórica;
- la nueva identidad que lo reemplaza;
- el edge `replaces`;
- y que el claim de Fase 4 depende de la identidad antigua.

Esto bloquea la confusión histórica: no se debe fingir que el claim “siempre” dependió del nuevo prior.

### Ejemplo 5 — Cambia la taxonomía y algunos aliases se reagrupan
`taxonomy_version:site_system_taxonomy:v12` reagrupa aliases que antes estaban separados en `v11`.

El motor debe:
- registrar `v12` como nueva dependencia externa;
- no sobrescribir las versiones históricas construidas con `v11`;
- marcar comparabilidad condicionada entre outputs que mezclan ambas taxonomías;
- generar stale sobre objetos que dependen de la taxonomía antigua si policy exige rebuild.

Comparabilidad histórica se preserva manteniendo pins explícitos por versión, no reinterpretando retroactivamente el pasado.

### Ejemplo 6 — Reconstruir un `report_package` exacto de una fecha anterior
Se necesita reconstruir `report_package:case_456_exec:v4` exactamente como existía el 2026-02-14.

El motor debe haber preservado:
- `object_identity` y `object_version_id`;
- member set exacto del package;
- pins de `output_block`, `artifact`, `audience_view` y `machine_export_bundle`;
- contract/taxonomy/rule/model/library refs;
- `rebuild_manifest` con producer version y fingerprints;
- `content_checksum` esperado.

Con eso, otro motor puede re-ejecutar o verificar reconstrucción exacta sin adivinar dependencias ni usar narrativa.
