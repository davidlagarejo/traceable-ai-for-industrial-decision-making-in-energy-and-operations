# ENTITY IDENTITY / RESOLUTION ENGINE — MASTER SPEC

## 1. Qué es exactamente el Entity Identity / Resolution Engine
Motor fundacional que resuelve identidad estable sobre registros ya normalizados y referenciados taxonómicamente, determinando cuándo distintos registros apuntan a la misma entidad, cuándo solo existe `candidate match`, cuándo hay `no-match`, cuándo la resolución debe permanecer `ambiguous/unresolved` y cuándo existe relación material sin equivalencia. Su función es producir `entity_id` estable, historial de resolución y rationale auditable sin borrar nombres observados ni colapsar ambigüedad legítima.

## 2. Qué problema resuelve y qué problema no resuelve
### Resuelve
- asignar `entity_id` estable a entidades relevantes del framework;
- construir candidate match sets explícitos;
- confirmar matches solo bajo reglas y evidencia suficientes;
- registrar aliases, nombres observados y contextos de uso;
- distinguir `confirmed match`, `no-match`, `ambiguous/unresolved` y `related-but-not-equivalent`;
- soportar `merge` y `split` con trazabilidad histórica;
- preservar base de evidencia, confidence, actor y rationale de cada decisión.

### No resuelve
- ingesta o parsing;
- normalización de valores;
- taxonomía soberana o membresía taxonómica;
- inferencia libre, verificación, reporting o packaging final;
- quality/fitness global;
- curation bibliográfica;
- matching textual libre por similitud;
- ontología nueva o rediseño de categorías del framework.

## 3. Qué rol cumple dentro del framework completo
- Opera después de Canonical Normalization Engine.
- Consume registros normalizados, references taxonómicas controladas y lineage suficiente.
- Entrega entidades canónicas, candidate sets, decisiones de resolución y eventos históricos reutilizables aguas abajo.
- Sirve a Quality/Fitness, Library Curation, joins semánticos, packaging por fase y análisis posterior.
- Existe como motor separado porque identidad no es taxonomía, normalización ni quality.

## 4. Qué NO debe hacer
- No confirmar identidad solo por similitud textual.
- No sobrescribir nombres observados ni aliases originales.
- No convertir `candidate match` en `confirmed match` sin soporte suficiente.
- No borrar ambigüedad material.
- No mutar historial de merge/split sin rastro.
- No cambiar taxonomías ni categorías de referencia.
- No inferir relaciones semánticas profundas fuera de reglas explícitas.
- No emitir joins como definitivos cuando la resolución sigue abierta.

## 5. Qué SÍ debe hacer
- Consumir `normalized_record` y referencias controladas del Taxonomy Service.
- Construir `observed_entity_record` por mención normalizada con provenance.
- Agrupar candidatos plausibles bajo reglas explícitas y versionadas.
- Asignar `entity_id` estable cuando la resolución sea suficiente.
- Mantener `candidate matches` no resueltos cuando falte evidencia.
- Registrar aliases, evidence basis, confidence y rationale.
- Soportar `confirmed`, `rejected`, `unresolved`, `related-but-not-equivalent`, `merged`, `split`.
- Exponer manifests suficientes para replay y auditoría.

## 6. Qué tipos de entidades debe resolver ZLab
### Institucionales
- `publisher`
- `issuing_body`
- `utility`
- `jurisdictional_body`
- `standard_or_framework_issuer`

### Físicas y operativas
- `facility`
- `plant`
- `campus`
- `building`
- `system`
- `subsystem`
- `asset`
- `equipment_family` cuando sea entidad operativa explícita
- `instrumentation_item` cuando sea entidad rastreable

### Documentales y referenciales
- `benchmark_source_family`
- `regulatory_reference`
- `methodology_document`
- `case_study_reference`
- `evidence_source_family`

### Regla
- La identidad siempre debe declarar `entity_kind`: `physical`, `institutional`, `documental`, `reference`.
- No se asume que toda entidad es física ni que todo label operativo merece `entity_id`.

## 7. Qué granularidad de resolución conviene
| Granularidad | Regla |
|---|---|
| Por documento | Solo para entidades documentales o referencias explícitas; no para instalaciones salvo evidencia suficiente. |
| Por fuente | Útil para publishers, issuers, benchmark families y evidence source families. |
| Por institución | Primaria para utilities, issuers, jurisdictional bodies y framework owners. |
| Por instalación | Primaria para facility, plant, campus y building. |
| Por sistema | Separada de instalación cuando el sistema es objeto operativo distinto y trazable. |
| Por activo | Solo si el activo es materialmente distinguible y estable. |
| Por referencia normativa/metodológica | Separada de institución emisora; el documento o referencia puede tener identidad propia. |

### Regla de diseño
- Resolver al nivel más bajo que el soporte real permita sin colapsar entidades distintas.
- No promover una mención local a entidad global solo porque el label parece específico.

## 8. Qué objetos internos necesita
### Entidades mínimas
- `canonical_entity_record`
- `observed_entity_record`
- `entity_alias_record`
- `candidate_match_record`
- `resolution_decision_record`
- `merge_event_record`
- `split_event_record`
- `identity_evidence_record`
- `resolution_run_record`
- `resolution_replay_manifest`

### Records de estado mínimo
- `confirmed_match_record`
- `no_match_record`
- `ambiguous_resolution_record`
- `related_entity_link_record`
- `resolution_confidence_record`

### Value objects mínimos
- `entity_id`
- `observed_record_id`
- `candidate_match_id`
- `resolution_decision_id`
- `merge_event_id`
- `split_event_id`
- `alias_id`
- `confidence_value`
- `rationale_text`
- `evidence_ref`
- `resolution_scope`
- `entity_kind`
- `match_basis`
- `observed_name`
- `canonical_name`

## 9. Qué metadatos debe preservar obligatoriamente
- `entity_id`
- `entity_kind`
- `canonical_entity_status`
- `observed_record_id`
- `normalized_record_ref`
- `normalized_field_refs` relevantes
- `taxonomy_refs` consumidas
- `observed_name`
- `observed_aliases`
- `source_provenance`
- `resolution_run_id`
- `candidate_match_set_id`
- `resolution_decision_id`
- `decision_mode` (`auto_resolved`, `human_confirmed`, `human_rejected`, `carried_forward`)
- `confidence`
- `evidence_basis`
- `rationale`
- `rule_refs`
- `merge_predecessors` / `split_successors` cuando aplique
- `created_at`
- `effective_from`
- `effective_to` nullable

Ninguna resolución confirmada válida puede existir sin evidence basis, rationale mínima y provenance suficiente hacia registros normalizados.

## 10. Qué diferencia debe existir entre conceptos clave
- `observed record`: representación local de una mención o registro normalizado que parece referir a una entidad. Todavía no es la entidad canónica.
- `canonical entity`: entidad estable del motor, con `entity_id`, lifecycle y historial.
- `entity_id`: identificador estable de la entidad canónica; no cambia por alias ni por fuente nueva.
- `alias`: nombre observado o variante asociada a una entidad; nunca reemplaza el nombre observado original.
- `candidate match`: par o conjunto de observaciones/entidades con plausibilidad de identidad compartida, aún no confirmada.
- `confirmed match`: decisión explícita de que dos o más observaciones/entidades refieren a la misma entidad.
- `no-match`: decisión explícita de que no deben colapsarse bajo el mismo `entity_id`.
- `ambiguous / unresolved`: existe plausibilidad material, pero falta evidencia suficiente para confirmar o rechazar.
- `related-but-not-equivalent`: relación real sin identidad compartida, por ejemplo issuer-documento, campus-building, cooling plant-chiller plant según contexto.
- `merge event`: evento histórico que consolida dos o más `entity_id` preexistentes en una entidad vigente.
- `split event`: evento histórico que revierte o descompone una resolución previa en dos o más entidades distintas.

## 11. Cómo representar confidence y rationale
### `resolution_confidence_record`
Debe declarar:
- `confidence_band`: `high`, `moderate`, `low`, `insufficient`
- `decision_mode`
- `evidence_count`
- `conflict_present`
- `computed_under_rule_set`

### `rationale`
Debe ser estructurado, no solo texto libre:
- `rule_refs`
- `evidence_refs`
- `supporting_signals`
- `contradicting_signals`
- `decision_summary`

### Regla
- `confidence` nunca reemplaza evidence.
- Confidence bajo no autoriza merge.

## 12. Cómo representar bases de evidencia para resolución
### `identity_evidence_record`
Debe preservar:
- `evidence_ref`
- `evidence_type`
- `source_provenance`
- `normalized_values_used`
- `field_refs_used`
- `taxonomy_refs_used`
- `weight_class` solo como clase controlada, no score mágico
- `supports` / `contradicts`

### Evidence types mínimos
- external identifier exacto
- nombre institucional exacto gobernado
- alias gobernado observado
- parent entity context
- jurisdiction or geography context
- document issuer context
- facility/system parent-child context
- source family continuity

## 13. Cómo distinguir identidad real de similitud textual
- La similitud textual solo puede producir `candidate match`, nunca `confirmed match` por sí sola.
- `confirmed match` requiere al menos una combinación explícita de:
  - identificador externo estable;
  - alias gobernado y contexto consistente;
  - parent context consistente;
  - jurisdiction/owner/operator consistente;
  - lineage documental coherente;
  - ausencia de conflicto material.
- Un label corto o repetido como `Plant 2` nunca es suficiente.

## 14. Cómo manejar ambigüedad legítima
- Mantener `candidate_match_record` abierto.
- Emitir `ambiguous_resolution_record`.
- Registrar qué señales faltan para confirmar.
- Permitir múltiples candidatos plausibles bajo el mismo observed record.
- Bloquear joins definitivos mientras la resolución siga abierta.

## 15. Cómo manejar merges y splits sin romper comparabilidad histórica
### Merge
- No borrar entidades preexistentes.
- Crear `merge_event_record` con:
  - `predecessor_entity_ids`
  - `surviving_entity_id`
  - `effective_from`
  - `rationale`
  - `evidence_refs`
- Mantener lineage de aliases y observed records.

### Split
- No reescribir el pasado silenciosamente.
- Crear `split_event_record` con:
  - `pre_split_entity_id`
  - `successor_entity_ids`
  - `effective_from`
  - `rationale`
  - `evidence_refs`
- Reasignar observed records solo con registro explícito de la nueva base.

## 16. Cómo interactúa con otros motores
### Taxonomy + Canonical Entity Service
- Consume tipos y refs controladas.
- No redefine taxonomía.
- Puede usar taxonomy membership como evidencia contextual, nunca como prueba suficiente de identidad.

### Canonical Normalization Engine
- Consume `normalized_record` y `normalized_field_record`.
- No corrige ni re-normaliza valores.

### Versioning + Lineage Engine
- Registra lineage de decisiones, merges, splits y manifests de replay.
- No sustituye el engine de versionado.

### Quality/Fitness Engine
- Entrega estados de resolución, warnings y conflictos de identidad.
- No decide fitness final.

### Library Curation Engine
- Entrega entidades y aliases resueltos o conflictivos.
- No cura bibliotecas por sí mismo.

### Governance Layer
- Human confirmation/rejection y reglas nuevas deben entrar por gobernanza explícita.
- No cambia ontología ni reglas maestras sin control.

### Evaluation/Conformance Engine
- Debe poder auditar candidate matches abiertos, merges inseguros, aliases conflictivos y replay de decisiones.

## 17. Qué partes pueden automatizarse y cuáles no
### Automatizable
- candidate generation bajo reglas explícitas;
- detección de conflictos de contexto;
- confirmación automática solo en casos fuertes y acotados;
- no-match automático cuando existe contradicción explícita;
- construcción de replay manifest y lineage.

### No automatizable de forma soberana
- merges sobre evidencia parcial;
- splits con implicaciones históricas fuertes;
- resolución de aliases ambiguos de alta colisión;
- cambios de criterio que afecten entidades ya usadas downstream.

## 18. Qué rol permitido y prohibido puede tener un LLM dentro de este motor
### Permitido
- sugerir candidate aliases o rationale draft fuera del runtime soberano;
- asistir en revisión humana de casos ambiguos;
- ayudar a redactar explicaciones downstream.

### Prohibido
- confirmar identidad por sí mismo;
- alterar reglas efectivas de resolución;
- hacer matching soberano en runtime;
- borrar ambigüedad o conflicto material.

## 19. Qué acceptance tests mínimos debe tener
- alias institucionales equivalentes con confirmación correcta;
- labels similares pero no equivalentes que permanecen separados;
- mismo label superficial en compañías distintas sin merge;
- candidate match abierto por evidencia incompleta;
- no-match explícito por conflicto fuerte;
- split posterior a merge previo conservando historial;
- related-but-not-equivalent sin colapso de `entity_id`;
- replay exacto de una decisión antigua;
- entity_id estable frente a alias nuevos no conflictivos;
- bloqueo de merge cuando falte provenance o rationale.

## 20. Qué observabilidad debe exponer
- conteo de candidate matches abiertos;
- conteo de auto-resolved vs human-confirmed;
- merges y splits por período;
- entidades con aliases conflictivos;
- resoluciones con confidence baja;
- decisiones bloqueadas por falta de contexto;
- ratio de `no-match` por tipo de entidad;
- replayability status por run.

## 21. Qué failure modes deben bloquearse desde el día 1
- merge confirmado sin evidence basis suficiente;
- split o merge sin evento histórico trazable;
- candidate match colapsado silenciosamente a confirmed;
- entity_id sin lineage hacia observed records;
- alias conflictivo usado como prueba soberana única;
- no-match o confirmed match sin rationale;
- relación taxonómica tratada como identidad;
- entity reuse entre entidades de kind distinto sin regla explícita.

## 22. Qué errores de arquitectura serían muy caros de corregir después
- no separar observed record de canonical entity;
- no separar candidate match de resolution final;
- no modelar merges y splits como eventos;
- no preservar aliases observados por fuente;
- mezclar identidad con taxonomía;
- usar scores opacos como sustituto de rationale;
- permitir reescritura silenciosa del historial.

## 23. Cómo diseñarlo para MVP sin volverlo mediocre
- Soportar primero entidades institucionales, documentales y de instalación con reglas explícitas.
- Confirmar automáticamente solo casos fuertes.
- Mantener unresolved y no-match como outputs de primera clase.
- Exigir provenance, rationale y rule refs desde el día 1.
- Incluir merge/split history aunque el volumen inicial sea bajo.

## 24. Cómo escalarlo sin volverlo un monolito
- Separar:
  - catálogo de entidades;
  - candidate generation;
  - rule evaluation;
  - decision records;
  - merge/split history;
  - validation;
  - replay.
- Versionar reglas y manifests.
- No meter heurísticas nuevas dentro del mismo módulo de decisión.
- Tratar nuevos tipos de entidad como rule packs y value objects, no como excepciones ad hoc.

## 25. Una estructura mínima sugerida para pasar luego a código
```text
entity_identity_resolution_engine/
  domain/
    enums.py
    value_objects.py
    entities.py
    records.py
    errors.py
  resolution/
    candidate_builder.py
    rule_evaluator.py
    decision_engine.py
    merge_split.py
    replay.py
  validation/
    context.py
    candidate_validator.py
    decision_validator.py
    history_validator.py
    orchestrator.py
  tests/
    test_candidate_matching.py
    test_confirmed_vs_no_match.py
    test_ambiguous_resolution.py
    test_merge_split_history.py
    test_replay_integrity.py
```

## 26. Ejemplos técnicos obligatorios
### Ejemplo 1: “Con Edison”, “ConEd”, “Consolidated Edison”
- Se crean tres `observed_entity_record` distintos, cada uno con `observed_name`, source provenance y normalized refs.
- Las reglas generan un `candidate_match_set` porque:
  - los aliases están gobernados;
  - el contexto institucional y jurisdiccional coincide;
  - no hay conflicto material.
- La resolución produce un `confirmed_match_record` hacia un `canonical_entity_record` con `entity_id` estable.
- Los tres nombres siguen preservados como `entity_alias_record`; ninguno sobrescribe el observado original.

### Ejemplo 2: “Cooling plant” vs “chiller plant”
- El texto similar solo habilita `candidate match`.
- Si el contexto no demuestra equivalencia exacta, la salida correcta es:
  - `ambiguous_resolution_record`, o
  - `related_entity_link_record` si se sabe que están relacionados pero no son la misma entidad.
- No se confirma merge solo porque ambos labels viven en la misma instalación.

### Ejemplo 3: “Plant 2” en empresas distintas
- Dos `observed_entity_record` comparten label superficial.
- Las reglas observan parent issuer distinto, ownership distinta o jurisdiction distinta.
- El resultado correcto es `no-match` explícito o ausencia de candidate viable.
- Nunca se asigna el mismo `entity_id` solo por coincidencia del label.

### Ejemplo 4: split posterior por nueva evidencia
- Históricamente se había confirmado que dos observaciones eran el mismo subsystem bajo un único `entity_id`.
- Nueva evidencia muestra que eran dos subsistemas distintos.
- Se crea `split_event_record` con:
  - `pre_split_entity_id`
  - `successor_entity_ids`
  - `effective_from`
  - `rationale`
  - `evidence_refs`
- El historial previo se conserva; no se reescribe silenciosamente la decisión antigua.

### Ejemplo 5: misma entidad, varias categorías operativas
- Una `facility` puede pertenecer a varias categorías operativas o taxonómicas según contexto.
- El `entity_id` sigue siendo uno.
- La clasificación vive en taxonomy membership o refs externas; no se crean entidades nuevas por cada categoría.
- Identidad y clasificación permanecen separadas.

### Ejemplo 6: reconstrucción meses después
- Para reconstruir por qué se asignó cierto `entity_id`, el motor debe guardar:
  - `resolution_run_record`
  - `resolution_replay_manifest`
  - `candidate_match_records`
  - `resolution_decision_record`
  - `identity_evidence_records`
  - `rule_refs`
  - `confidence_record`
  - `source_provenance`
- Con eso se puede reejecutar o auditar exactamente la base de la decisión sin depender de memoria externa o texto narrativo.
