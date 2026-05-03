# TAXONOMY + CANONICAL ENTITY SERVICE — MASTER SPEC

## 1. Qué es exactamente el Taxonomy + Canonical Entity Service
Motor fundacional que mantiene taxonomías canónicas versionadas, términos controlados, aliases gobernados, límites semánticos explícitos y entidades canónicas estables para que todo el framework use lenguaje estructurado consistente. Su función es disciplinar significado, joins y resolución semántica sin hacer inferencia, sin reabrir epistemología y sin sustituir lineage, contracts, quality o verification.

## 2. Qué problema resuelve y qué problema no resuelve
### Resuelve
- vocabulario canónico común entre motores y fases;
- taxonomías versionadas por dominio y familia;
- aliases, sinónimos, legacy labels y deprecaciones controladas;
- identidad estable de entidades canónicas cuando corresponde;
- separación entre categoría, entidad y match;
- joins semánticos estables y auditables;
- manejo explícito de ambigüedad y candidate matches;
- comparabilidad histórica cuando cambia una taxonomía.

### No resuelve
- parsing o ingestión;
- inferencia sobre el caso;
- matching libre por similitud textual sin reglas;
- normalización de unidades o calidad global;
- reporting, verification o generación de documentos finales;
- decisiones de governance final sobre ampliación ontológica de alto impacto;
- storage productivo, UI, API o cloud.

## 3. Qué rol cumple dentro del framework completo
- Es un motor transversal semántico, no una fase.
- Opera por debajo de Fase 1–4 y por debajo de motores funcionales.
- Define lenguaje controlado, identidad semántica estable y reglas de relación; no define verdad del caso.
- Sirve a contracts, lineage, normalization, matching y quality como fuente común de semántica controlada.
- Hace posible que el framework no derive en dialectos incompatibles entre fases.

## 4. Qué NO debe hacer
- No reabrir fases cerradas ni cambiar su semántica.
- No fusionar entidades de alto impacto sin trazabilidad.
- No sobrescribir labels históricos.
- No convertir similitud textual en identidad real por defecto.
- No inferir nueva ontología en el write path.
- No borrar ambigüedad material.
- No mezclar taxonomía con quality, governance o lineage.
- No aceptar joins semánticos implícitos no gobernados.

## 5. Qué SÍ debe hacer
- Mantener taxonomías canónicas por dominio y familia.
- Mantener nodos, aliases, sinónimos, legacy terms y deprecated terms.
- Mantener entidades canónicas separadas de categorías.
- Mantener candidate matches, confirmed matches y relaciones no equivalentes.
- Mantener boundaries y criterios de uso de categorías.
- Mantener join keys semánticos y políticas de resolución.
- Versionar cambios taxonómicos y preservar comparabilidad histórica.
- Exponer conflictos semánticos, ambigüedades y joins inseguros.

## 6. Qué tipos de taxonomías necesita ZLab
### Contexto y fuente
- `source_family`
- `publisher_type`
- `jurisdiction`
- `geography`
- `sector`
- `subsector`
- `benchmark_family`
- `regulatory_family`

### Fase 1
- `facility_type`
- `system_family`
- `asset_family`
- `archetype_family`
- `climate_energy_context_family`
- `regulatory_trigger_family`
- `prior_assumption_family`
- `uncertainty_family`

### Fase 2
- `inference_case_family`
- `tension_family`
- `conflict_family`
- `opportunity_family`
- `evidence_gap_family`
- `validation_action_family`

### Fase 3
- `output_block_type`
- `artifact_type`
- `audience_view_type`
- `report_package_component_type`

### Fase 4
- `claim_upgrade_candidate_family`
- `required_site_evidence_family`
- `baseline_hardening_family`
- `instrumentation_gap_family`
- `upgrade_decision_family`

## 7. Qué tipos de entidades canónicas necesita ZLab
- instalaciones;
- sistemas;
- subsistemas;
- equipos;
- combustibles;
- vectores energéticos;
- métricas;
- normas y marcos normativos;
- instrumentos de medición;
- tipos de evidencia;
- familias de claim solo cuando operen como entidades referenciables y no solo como categorías.

## 8. Qué granularidad debe tener la taxonomía
### Regla general
La granularidad mínima debe ser suficiente para:
- clasificar objetos reales sin colapsar entidades distintas;
- soportar joins estables;
- preservar comparabilidad histórica;
- y expresar insuficiencia cuando el vocabulario actual no alcanza.

### Granularidad mínima
| Eje | Unidad mínima |
|---|---|
| Por fase | familias controladas de objetos y salidas admitidas por la fase |
| Por dominio | taxonomía versionada por familia semántica autónoma |
| Por objeto | clasificación explícita por `taxonomy_node` y no por label libre |
| Por familia de sistema | nodo para familia; entidad aparte para el sistema real |
| Por familia regulatoria | nodo para trigger/family; entidad aparte para norma o framework real |
| Por output/documento | tipos de bloque, artifact, audience view y componentes de report package |

## 9. Qué objetos internos necesita
### Entidades mínimas
| Objeto | Propósito |
|---|---|
| `taxonomy_family` | Agrupa un dominio taxonómico coherente y versionable. |
| `taxonomy_version` | Snapshot inmutable de una taxonomía o familia. |
| `taxonomy_node` | Término canónico controlado dentro de una taxonomía. |
| `alias_record` | Label alternativo gobernado apuntando a un `taxonomy_node` o `entity_id`. |
| `canonical_entity` | Identidad estable de una entidad real o semánticamente estable. |
| `candidate_match_record` | Propuesta explícita de match aún no confirmada. |
| `semantic_relation_record` | Relación tipada entre nodos o entidades. |
| `boundary_definition_record` | Límite semántico y criterio de inclusión/exclusión. |
| `deprecation_record` | Regla explícita de deprecación y reemplazo. |
| `join_key_policy` | Política controlada para joins semánticos estables. |

### Value objects mínimos
| Objeto | Propósito |
|---|---|
| `taxonomy_locator` | Referencia homogénea a `taxonomy_version`, `taxonomy_node`, `entity_id` o alias. |
| `canonical_label` | Label canónico estable para escritura controlada. |
| `semantic_scope` | Contexto mínimo donde una relación o alias es válida. |
| `match_rationale` | Justificación estructurada de un candidate o confirmed match. |
| `equivalence_assertion` | Afirmación explícita de equivalencia con estatus y alcance. |

### Enums mínimos
- `taxonomy_family_kind`
- `node_status`
- `alias_kind`
- `entity_status`
- `match_status`
- `relation_type`
- `boundary_status`
- `join_safety_status`
- `conflict_severity`

## 10. Qué metadatos debe preservar obligatoriamente
- `taxonomy_family_id`
- `taxonomy_version_id`
- `taxonomy_version_label`
- `node_id`
- `canonical_label`
- `entity_id` cuando aplique
- `scope`
- `source_of_authority`
- `created_at`
- `created_by_engine`
- `effective_from`
- `deprecated_at` nullable
- `replacement_ref` nullable
- `rationale`
- `confidence` cuando exista candidate match
- `join_policy_ref`
- `lineage_ref` o `version_ref` a la taxonomía usada downstream

Ningún alias, match o deprecación debe existir sin `scope`, `rationale` y referencia a la versión taxonómica en la que fue materializado.

## 11. Diferencia entre términos, aliases y resolución
- `canonical_term`: label oficial de un `taxonomy_node`; único dentro de su `taxonomy_version`.
- `alias`: label alternativo gobernado que apunta a un nodo o entidad dentro de un scope.
- `synonym`: alias cuyo uso es semánticamente equivalente al canónico dentro de scope explícito.
- `legacy_term`: label histórico aún observable en fuentes o histórico interno, no recomendado para nueva escritura.
- `candidate_match`: propuesta no final de que dos labels o registros refieren al mismo nodo o entidad.
- `confirmed_match`: equivalencia aprobada y materializable en joins controlados.
- `related-but-not-equivalent`: cercanía semántica sin identidad ni sustitución.
- `deprecated_term`: término que no debe usarse en nuevas escrituras, con reemplazo o retiro explícito.
- `entity_id`: identidad estable de una entidad; no es categoría.
- `taxonomy_node`: categoría o término controlado; no implica entidad del mundo real.

## 12. Cómo representar boundaries y límites semánticos
Cada `taxonomy_node` o familia que lo requiera debe poder declarar:
- definición breve;
- criterios de inclusión;
- criterios de exclusión;
- ejemplos positivos;
- ejemplos negativos;
- scope de validez;
- nodo más cercano cuando el caso queda fuera.

Boundary no es prose decorativa; es criterio operativo para evitar merges, memberships o joins ilegítimos.

## 13. Cómo representar relaciones
### Relaciones mínimas
- `broader`
- `narrower`
- `equivalent`
- `related`
- `incompatible`
- `ambiguous`

### Reglas
- `broader/narrower` solo entre nodos taxonómicos, no como sustituto de identidad de entidad.
- `equivalent` exige scope y estatus explícito; no nace de similitud textual.
- `related` preserva cercanía sin colapso.
- `incompatible` bloquea joins o merges automáticos.
- `ambiguous` obliga a mantener múltiples candidatos o a no resolver.

## 14. Cómo distinguir categoría, entidad, similitud y sustitución
- `category_membership`: un objeto pertenece a una categoría taxonómica.
- `entity_identity`: dos referencias apuntan a la misma entidad canónica.
- `semantic_similarity`: labels o nodos se parecen; no implica equivalencia.
- `operational_substitutability`: dos objetos pueden cumplir función parecida en cierto contexto; no implica misma entidad ni misma categoría.

Regla: categoría y entidad nunca se colapsan. Un mismo `entity_id` puede pertenecer a varias categorías contextuales; una categoría puede contener muchas entidades.

## 15. Cómo soportar joins estables sin sobresimplificar el mundo real
Los joins semánticos deben descansar en:
- `entity_id` cuando haya identidad confirmada;
- `taxonomy_node_id` cuando el join sea por categoría;
- `alias_record` solo si está confirmado y dentro del scope;
- `join_key_policy` que declare seguridad, restricciones y fallback.

### Estados mínimos de join
- `safe`
- `conditional`
- `unsafe`

Un join por alias no confirmado o por similitud superficial debe salir `unsafe`.

## 16. Cómo manejar ambigüedad legítima
- La ambigüedad se preserva como estado explícito, no como vacío silencioso.
- Un label puede mapear a múltiples `candidate_match_record`.
- Un alias puede ser válido solo en un `semantic_scope` concreto.
- Si no hay criterio suficiente, el motor debe devolver “no resuelto” o “ambiguous”, no un merge optimista.

## 17. Cómo manejar cambios taxonómicos sin romper comparabilidad histórica
- Toda taxonomía es versionada.
- Los nodos no se sobrescriben históricamente; se deprecán o reemplazan.
- Un cambio de taxonomy no reescribe memberships antiguas.
- La comparabilidad histórica puede quedar:
  - `comparable`
  - `conditionally_comparable`
  - `not_comparable`
- Toda migración taxonómica debe declarar si:
  - es simple rename;
  - es split;
  - es merge;
  - o redefine boundary.

## 18. Cómo interactúa con otros motores
### Phase Contract Registry
- Consume restricciones de nombres, objetos y metadata permitidos.
- No redefine contratos; solo ofrece vocabulario controlado usable por ellos.

### Versioning + Lineage Engine
- Entrega `taxonomy_version` y `entity_id` como referencias versionadas.
- No sustituye lineage; lineage preserva qué versión taxonómica fue usada.

### Normalization Engine
- Entrega vocabulario y entity anchors.
- No ejecuta normalización por sí mismo.

### Matching / Identity workflows
- Entrega taxonomía, aliases, candidate matches y estados.
- No ejecuta resolución heurística soberana.

### Quality / Fitness Engine
- Entrega hechos semánticos: alias ambiguo, join unsafe, taxonomy inconsistente.
- No puntúa calidad global por sí mismo.

### Governance Layer
- Entrega cambios, deprecaciones, unresolved matches y boundaries conflictivos.
- No aprueba cambios de alto impacto por sí solo.

## 19. Qué partes pueden automatizarse y cuáles no
### Automatizable
- lookup exacto de canonical terms y aliases confirmados;
- validación estructural de taxonomías;
- detección de alias duplicados o conflictivos;
- joins seguros ya aprobados;
- deprecation lookup;
- candidate generation controlada cuando exista política explícita.

### No automatizable por defecto
- crear nueva categoría estructural;
- confirmar equivalencia de alto impacto;
- fusionar entidades físicas o regulatorias;
- resolver ambigüedad sectorial sin evidencia contextual;
- decidir que un split/merge preserva comparabilidad histórica.

## 20. Qué rol permitido y prohibido puede tener un LLM dentro de este motor
### Permitido
- sugerir candidate matches;
- proponer aliases candidatos;
- resumir boundaries ya definidos;
- asistir revisión humana de cambios taxonómicos.

### Prohibido
- asignar `entity_id` definitivo en el write path;
- confirmar equivalencias de alto impacto;
- crear categorías oficiales sin gobernanza;
- borrar ambigüedad material;
- sobrescribir historial taxonómico.

## 21. Qué acceptance tests mínimos debe tener
1. registrar una `taxonomy_version` con nodos canónicos, aliases y boundaries válidos;
2. rechazar alias ambiguo no scoped;
3. distinguir `canonical_term` de `entity_id`;
4. preservar candidate match sin convertirlo en confirmed match;
5. bloquear join `unsafe` por alias no confirmado;
6. preservar comparabilidad histórica tras deprecación o split;
7. mantener una entidad en múltiples categorías operativas sin duplicar `entity_id`;
8. detectar conflicto entre dos fuentes que usan el mismo término con meaning distinto;
9. rechazar merge silencioso entre entidades distintas;
10. exponer taxonomía rota o relación incompatible circular donde no aplique.

## 22. Qué observabilidad debe exponer
- conteo de nodos por `taxonomy_family`;
- conteo de aliases por estado;
- conteo de deprecated terms y reemplazos abiertos;
- cantidad de candidate matches pendientes;
- cantidad de joins `safe` / `conditional` / `unsafe`;
- conflictos semánticos por severidad;
- cobertura de boundaries definidos por familia;
- comparabilidad histórica afectada por versión taxonómica.

Estas señales deben salir como registros estructurados, no como UI obligatoria.

## 23. Qué failure modes deben bloquearse desde el día 1
- alias apuntando a múltiples targets sin scope;
- confirmed match sin rationale;
- uso de labels libres como canónicos persistidos;
- merge silencioso entre entidades distintas;
- node sin `taxonomy_version`;
- deprecación sin replacement ni rationale cuando el caso lo requiera;
- joins materiales por similitud textual no confirmada;
- categoría usada como si fuera identidad de entidad;
- cambio taxonómico que sobrescribe el pasado;
- boundary inexistente en familias con alta colisión semántica.

## 24. Qué errores de arquitectura serían muy caros de corregir después
- confundir taxonomía con identidad de entidad;
- almacenar aliases como texto libre sin scope ni estatus;
- tratar candidate match y confirmed match como lo mismo;
- no versionar taxonomías;
- permitir merges silenciosos;
- modelar todo como un árbol cuando parte del dominio necesita relaciones laterales;
- hacer joins por label y no por IDs controlados;
- incrustar heurística de matching en el dominio canónico.

## 25. Cómo diseñarlo para MVP sin volverlo mediocre
El MVP debe incluir desde el inicio:
- taxonomías versionadas;
- nodos canónicos;
- aliases con scope y estatus;
- entidades canónicas separadas;
- candidate matches y confirmed matches;
- boundaries mínimos;
- deprecación explícita;
- join safety explícito;
- aceptación de ambigüedad legítima.

Puede dejar fuera en MVP:
- resolución probabilística avanzada;
- tooling editorial complejo;
- support multi-tenant;
- taxonomías exhaustivas de todos los dominios desde el día 1.

## 26. Cómo escalarlo sin volverlo un monolito
- separar `taxonomy`, `entities`, `aliases`, `matches`, `boundaries` y `joins` como módulos de dominio;
- hacer versionado por familia, no una ontología gigante única;
- añadir nuevos dominios como familias versionadas, no como ramas arbitrarias de un árbol global;
- mantener resolución, governance y serving separados;
- usar lineage para auditar uso de taxonomía, no para cargar lógica semántica dentro del motor.

## 27. Una estructura mínima sugerida para pasar luego a código
```text
governanza/
  taxonomy-canonical-entity-service/
    MASTER_SPEC.md
    domain/
      taxonomy/
      entities/
      aliases/
      matches/
      boundaries/
      joins/
      enums/
      value_objects/
    application/
      registration/
      resolution/
      validation/
      migrations/
    tests/
      unit/
      acceptance/
      fixtures/
```

## Ejemplos obligatorios
### Ejemplo 1: “chiller plant”, “central chilled water”, “cooling plant”, “CHW system”
`taxonomy_node` canónico: `system_family:central_chilled_water_plant`.

`alias_record`:
- `chiller plant` -> candidate o confirmed según scope;
- `central chilled water` -> alias confirmado si el boundary del nodo incluye producción/distribución central;
- `cooling plant` -> `candidate_match_record`, no confirmed por defecto, porque puede colisionar con otras configuraciones;
- `CHW system` -> alias scoped, porque puede referir loop, plant o distribución según contexto.

`entity_id` solo existe si se trata de una planta o sistema real específico del sitio. El motor no colapsa label similar en identidad automáticamente. Resultado correcto:
- mismo nodo canónico posible para algunos labels;
- misma entidad física solo si el contexto y el matching lo confirman;
- ambigüedad preservada cuando `cooling plant` o `CHW system` no fijan boundary suficiente.

### Ejemplo 2: nueva familia de refrigeración industrial que no encaja
No se fuerza un nodo definitivo. Se crea:
- `candidate_match_record` hacia nodos cercanos;
- `boundary_definition_record` marcando insuficiencia;
- estado de familia o node como `provisional` o `needs_governance` si el modelo lo incluye.

El motor debe permitir “insuficiente para clasificar con seguridad” sin inventar una categoría nueva en silencio.

### Ejemplo 3: misma palabra, significado distinto por sector
La palabra `steam loop` en district energy y en proceso industrial puede pertenecer a familias distintas. El alias se registra con `semantic_scope` sectorial. Resultado:
- no hay confirmed match global;
- el mismo alias puede resolver distinto por scope;
- un join cross-sector sin scope sale `unsafe`.

### Ejemplo 4: deprecación de un término antiguo
Se depreca `boiler room efficiency class` y se reemplaza por `steam_generation_efficiency_family`.

El motor registra:
- `deprecation_record` con `replacement_ref`;
- mantiene el nodo viejo para histórico;
- marca comparabilidad como `conditionally_comparable` si el boundary cambió;
- no reescribe objetos históricos que usaban el término viejo.

### Ejemplo 5: motor downstream usa alias libre inexistente
Si un motor intenta persistir `super cooling hub` y ese label no existe como canónico ni alias confirmado:
- el servicio no lo promueve automáticamente;
- devuelve `unknown_term` o `unregistered_alias`;
- puede abrir `candidate_match_record` si la policy lo permite;
- el join o clasificación queda bloqueado o `unsafe`.

### Ejemplo 6: una misma entidad pertenece a varias categorías operativas
Una planta central real puede tener un único `entity_id`, pero ser miembro de:
- `system_family:central_chilled_water_plant`
- `asset_family:thermal_generation_asset`
- `facility_type:campus_utility_core` según contexto de modelado.

La identidad no se duplica. Lo que cambia es `category_membership` por contexto operativo. Ese es el punto donde el motor debe distinguir entidad de clasificación.
