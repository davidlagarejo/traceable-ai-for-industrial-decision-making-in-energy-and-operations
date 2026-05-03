# CANONICAL NORMALIZATION ENGINE — MASTER SPEC

## 1. Qué es exactamente el Canonical Normalization Engine
Motor fundacional que transforma representación parseada heterogénea en representación canónica controlada, preservando el vínculo entre `raw_value`, `parsed_value` y `normalized_value`, así como reglas de mapping, typing y conversión aplicadas. Su función es volver comparable y reusable el material extraído sin convertir normalización en parsing, matching, identity resolution, inferencia o autoridad epistemológica.

## 2. Qué problema resuelve y qué problema no resuelve
### Resuelve
- traducir `parsed_field_object` y `parsed_table_object` a nombres de campo canónicos;
- unificar tipos de dato y formatos disciplinados;
- convertir unidades y monedas cuando exista regla explícita y contexto suficiente;
- preservar simultáneamente valor original, valor parseado y valor normalizado;
- registrar reglas, factores, coerciones y warnings de normalización;
- soportar `partial normalization` y `non-normalizable field` sin destruir utilidad restante;
- preparar insumo estable para bundles de Fase 1, objetos de Fase 2, bloques de Fase 3 y objetos de verificación de Fase 4.

### No resuelve
- ingestión o parsing;
- resolución de identidad o equivalencia semántica profunda;
- matching libre por similitud de nombres;
- calidad/fitness soberana por fase;
- inferencia, reporting, verification o packaging final;
- mutación de taxonomías o aliases globales;
- corrección silenciosa de valores defectuosos;
- serving, API, UI, storage productivo o cloud.

## 3. Qué rol cumple dentro del framework completo
- Es un motor transversal de transformación disciplinada, no una fase.
- Opera después de Ingestion + Parsing y antes de Identity/Resolution, Quality/Fitness, Library Curation y materialización final por fase.
- Entrega representación canónica reutilizable, no verdad del caso.
- Su responsabilidad es reducir heterogeneidad formal, no decidir significado profundo ni aptitud final.
- Existe como motor separado porque:
  - parsing y normalización son problemas distintos;
  - taxonomía y normalización son problemas distintos;
  - identidad y normalización son problemas distintos;
  - mezclar estas capas destruye trazabilidad, comparabilidad y auditabilidad.

## 4. Qué NO debe hacer
- No sobrescribir `raw_value` ni `parsed_value`.
- No borrar unidad original, label original ni precisión original.
- No inferir significado de campos por similitud superficial sin regla explícita.
- No resolver identidad de entidades ni equivalencias globales.
- No introducir taxonomía nueva ni aliases globales no gobernados.
- No arreglar valores imposibles o fuera de rango; solo señalarlos.
- No convertir ambigüedad en certeza.
- No emitir outputs que aparenten decision-grade o verification-grade.
- No mezclar mapping, conversion y quality final en el mismo juicio soberano.

## 5. Qué SÍ debe hacer
- Consumir parsed objects y extraction metadata con provenance suficiente.
- Mapear labels y paths a `canonical_field` mediante reglas explícitas y versionadas.
- Tipar valores de forma controlada.
- Normalizar formatos de fecha, número, booleano, enum y string disciplinado.
- Convertir unidades y monedas cuando la regla sea válida y trazable.
- Materializar `normalized_record` y `normalized_field_record` con triple valor y lineage.
- Registrar warnings, failures y estados de parcialidad.
- Conservar campos no normalizables como tales.
- Exponer manifests suficientes para replay y auditoría.

## 6. Qué diferencia debe existir entre conceptos clave
- `original_label`: label visible en la fuente o estructura parseada original, por ejemplo header, key o caption. Puede ser ruidoso, ambiguo o legacy.
- `parsed_field`: objeto del motor de parsing que contiene el fragmento extraído y su provenance estructural. No implica aún mapeo canónico.
- `canonical_field`: definición controlada del campo esperado downstream. Tiene nombre estable, tipo canónico, unidad esperada y reglas de uso.
- `raw_value`: representación textual o material más cercana al contenido original de la fuente.
- `parsed_value`: valor estructurado mínimo obtenido por parsing. Puede seguir siendo string, fragmento o escalar sin tipado canónico final.
- `normalized_value`: valor ya mapeado, tipado y, si aplica, convertido a unidad/forma canónica bajo reglas explícitas.
- `conversion_rule`: regla versionada que transforma un valor o unidad a otra de forma determinista y auditada.
- `normalization_warning`: señal explícita de degradación, ambigüedad, rango sospechoso o normalización parcial sin bloquear necesariamente todo el resultado.
- `non-normalizable field`: campo cuyo significado, tipo, unidad o contexto no permite producir `normalized_value` confiable con las reglas disponibles.
- `partial normalization`: estado en el que una parte de los campos de un input fue normalizada y otra parte quedó pendiente, ambigua o no normalizable.

## 7. Qué granularidad conviene para normalized records
### Regla general
La granularidad mínima debe ser suficiente para reutilización downstream, replay exacto y preservación de evidencia, sin inflar el sistema con artefactos redundantes.

### Granularidad mínima
| Unidad | Uso |
|---|---|
| `normalized_document_record` | envelope de una corrida de normalización sobre un documento parseado |
| `normalized_table_record` | envelope canónico por tabla parseada cuando el origen es tabular |
| `normalized_record` | grupo lógico de campos canónicos coherentes, por fila, entidad candidata o bloque estructural |
| `normalized_field_record` | unidad mínima reutilizable y auditable del motor |

### Reglas
- Todo `normalized_field_record` debe poder vincularse a un `parsed_field_object` o a una celda/posición tabular derivable.
- Un `normalized_record` agrupa campos que comparten el mismo scope estructural y contractual.
- No se permite saltar directo de documento parseado a bundle final por fase sin pasar por fields/records canónicos auditables.

## 8. Qué objetos internos necesita
### Entidades mínimas
| Objeto | Propósito |
|---|---|
| `canonical_schema_profile` | Agrupa campos canónicos válidos para una familia de salida o uso downstream. |
| `canonical_field_definition` | Define nombre estable, tipo canónico, unidad esperada, cardinalidad y constraints mínimos. |
| `field_alias_record` | Alias controlado de labels/path names para mapping local al motor; no es taxonomía global soberana. |
| `field_mapping_rule` | Regla versionada que decide cuándo un `original_label` o `parsed_field` mapea a un `canonical_field`. |
| `typing_rule` | Regla versionada de coerción/parseo determinista a tipo canónico. |
| `unit_conversion_rule` | Regla versionada de conversión de unidades o magnitudes. |
| `currency_conversion_rule` | Regla versionada de conversión monetaria cuando existe base temporal y fuente explícita. |
| `normalization_run_record` | Ejecución versionada de normalización sobre inputs parseados concretos. |
| `normalized_document_record` | Resultado documental de una corrida de normalización. |
| `normalized_table_record` | Resultado tabular canónico derivado de una tabla parseada. |
| `normalized_record` | Grupo lógico de fields canónicos coherentes. |
| `normalized_field_record` | Resultado canónico mínimo con triple valor y provenance. |
| `normalization_warning_record` | Warning recuperable y tipado por scope. |
| `normalization_failure_record` | Failure explícito y tipado por scope. |
| `normalization_replay_manifest` | Manifiesto suficiente para reproducir la normalización exacta. |

### Value objects mínimos
| Objeto | Propósito |
|---|---|
| `field_name_ref` | Nombre estable del campo canónico. |
| `original_label_ref` | Label original observado. |
| `value_triplet` | Agrupa `raw_value`, `parsed_value`, `normalized_value` sin perder diferencias. |
| `unit_ref` | Unidad original o canónica. |
| `currency_ref` | Moneda declarada. |
| `precision_descriptor` | Precisión temporal o numérica del valor. |
| `normalization_scope` | Scope de aplicación de una regla o record. |
| `rule_fingerprint` | Fingerprint estable de una regla efectiva. |
| `mapping_context` | Contexto mínimo que habilita un mapping sin inferencia libre. |

### Enums mínimos
- `canonical_data_type`
- `normalization_status`
- `warning_severity`
- `failure_severity`
- `range_status`
- `missingness_kind`
- `precision_kind`
- `conversion_kind`
- `schema_profile_kind`

## 9. Qué metadatos debe preservar obligatoriamente
- `normalization_run_id`
- `canonical_schema_profile_id`
- `canonical_schema_profile_version`
- `canonical_field_definition_id`
- `field_mapping_rule_id`
- `typing_rule_id` nullable
- `unit_conversion_rule_id` nullable
- `currency_conversion_rule_id` nullable
- `parsed_document_object_id`
- `parsed_table_object_id` nullable
- `parsed_field_object_id` nullable
- `raw_asset_version_id`
- `extraction_metadata_record_id`
- `parser_strategy_ref`
- `original_label`
- `raw_value`
- `parsed_value`
- `normalized_value` nullable
- `original_unit` nullable
- `normalized_unit` nullable
- `original_currency` nullable
- `normalized_currency` nullable
- `precision_descriptor`
- `measurement_period` nullable
- `source_date` nullable
- `currency_year` nullable
- `status`
- `warnings`
- `failures`
- `created_at`

Ningún `normalized_field_record` válido puede existir sin ref a parsed object o a su provenance derivable, sin regla de mapping efectiva o sin conservar `raw_value` y `parsed_value`.

## 10. Cómo representar nombres canónicos de campo y alias de campo
### `canonical_field_definition`
Debe declarar al menos:
- `canonical_field_name`
- `description`
- `canonical_data_type`
- `expected_unit_family` nullable
- `allowed_units` nullable
- `allowed_enum_set` nullable
- `cardinality`
- `nullability`
- `schema_profile_refs`
- `version`
- `lifecycle_status`

### `field_alias_record`
Debe declarar:
- `alias_label`
- `normalized_alias_key`
- `scope`
- `canonical_field_definition_id`
- `conditions_of_use`
- `source_family_constraints` nullable
- `format_constraints` nullable
- `status`

### Reglas
- El alias de campo no es identidad semántica global.
- Un alias puede ser válido solo en un scope concreto.
- Un mismo label no puede mapear automáticamente a varios `canonical_field` dentro del mismo scope sin quedar `ambiguous`.
- Todo mapping debe apoyarse en `field_alias_record`, `field_mapping_rule` o ambos; nunca en parecido textual libre.

## 11. Cómo representar typing y coerción controlada
### Tipos canónicos mínimos
- `string_disciplined`
- `integer`
- `decimal`
- `boolean`
- `date`
- `timestamp`
- `year`
- `enum_controlled`
- `ratio`
- `percentage`
- `currency_amount`
- `measure_with_unit`

### `typing_rule`
Debe fijar:
- tipo de entrada esperado;
- tipo canónico de salida;
- coerciones permitidas;
- formato esperado;
- locale assumptions explícitas si existen;
- tratamiento de nulls y missingness;
- versión y fingerprint.

### Reglas
- Coerción solo si es determinista.
- Si una string como `"1,234"` depende de locale no declarado, no se tipa automáticamente.
- Si una fecha no tiene día/mes, no se inventa.
- Si un booleano depende de vocabulario no gobernado, debe quedar warning o no-normalizable.

## 12. Cómo representar conversiones de unidades y monedas
### `unit_conversion_rule`
Debe declarar:
- `source_unit`
- `target_unit`
- `conversion_kind`
- `formula` o `factor/offset`
- `valid_domain`
- `precision_policy`
- `version`
- `fingerprint`

### `currency_conversion_rule`
Debe declarar:
- `source_currency`
- `target_currency`
- `basis_kind` (`declared_rate`, `official_table`, `fixed_policy_table`)
- `basis_date_or_year`
- `factor`
- `rounding_policy`
- `version`
- `fingerprint`

### Reglas
- Nunca se pierde la unidad o moneda original.
- Toda conversión debe dejar rastro de la regla exacta usada.
- Si falta contexto crítico para la conversión, el valor no se normaliza.
- No se permite “usar el último tipo de cambio disponible” sin base explícita y versionada.

## 13. Cómo manejar ranges, nulls, missingness y mixed values
### Nulls y missingness
Debe distinguirse al menos:
- `explicit_null`
- `missing_not_present`
- `not_parseable`
- `not_normalizable`
- `withheld_or_redacted`

### Ranges
- Un rango como `10-12` no debe colapsarse a un único número.
- Puede representarse como `normalized_range` solo si existe tipo/rule explícita para ello.
- Si downstream no acepta rangos, debe quedar `non-normalizable` o warning con valor original preservado.

### Mixed values
- Ejemplos: `"gas/electric"`, `"2023/2024"`, `"~42"`, `"N/A; 17"`.
- No se separan ni eligen componentes sin regla explícita.
- Pueden quedar como string disciplinado, range, multi-value explícito o `non-normalizable`, según contrato del schema profile.

### Fuera de rango
- El motor puede marcar `range_status = suspicious` o warning.
- No cambia el valor para que “parezca correcto”.

## 14. Cómo manejar campos ambiguos sin inventar significado
- Ambigüedad de label, unidad o contexto debe conservarse.
- Si un label puede mapear a varios campos canónicos y el contexto no lo resuelve, el campo queda `ambiguous` o `non-normalizable`.
- El motor puede usar contexto estructural explícito: tabla origen, header hermano, schema profile esperado, scope documental, unidad declarada.
- El motor no puede usar inferencia semántica libre ni resolución profunda de identidad.

## 15. Cómo interactúa con otros motores
### Ingestion + Parsing Engine
- consume `parsed_document_object`, `parsed_table_object`, `parsed_field_object` y `extraction_metadata`;
- no reemplaza parsing ni redefine locators.

### Versioning + Lineage Engine
- toda corrida y todo output canónico relevante debe ser versionable y trazable;
- lineage debe permitir reconstruir qué parsed objects, qué rules y qué conversiones produjeron cada normalized output.

### Taxonomy Service
- puede consumir nombres canónicos de campo y enums controlados previamente gobernados;
- no modifica taxonomías ni decide equivalencias taxonómicas nuevas.

### Entity Identity / Resolution Engine
- entrega campos canónicos útiles para matching posterior;
- no asigna `entity_id` ni fusiona entidades.

### Quality/Fitness Engine
- entrega warnings, failures, gaps y flags de parcialidad;
- no decide por sí solo si el record es apto para una fase concreta.

### Library Curation Engine
- puede consumir normalized records para curación y comparación;
- no debe recibir records sin provenance ni without rule trace.

### Evaluation/Conformance Engine
- debe poder auditar completeness, conversion trace, unit preservation, replay y compliance del contrato.

## 16. Qué partes pueden automatizarse y cuáles no
### Automatizable
- mapping por reglas explícitas;
- typing determinista;
- conversiones con reglas registradas;
- disciplina de strings, booleans y fechas cuando el formato es inequívoco;
- warning generation por patrones duros;
- replay de normalización.

### No automatizable soberanamente
- decidir significado de un field ambiguo solo por nombre superficial;
- elegir entre múltiples mappings plausibles sin regla;
- decidir equivalencia semántica profunda;
- corregir valores sospechosos;
- declarar que un normalized record ya es apto para decisión o verificación.

## 17. Qué rol permitido y prohibido puede tener un LLM dentro de este motor
### Permitido
- asistencia offline para proponer reglas o documentación humana de nuevas mappings;
- ayuda en authoring de catálogos, nunca en write path soberano.

### Prohibido
- decidir runtime qué canonical field usar;
- tipar o convertir valores como autoridad final;
- resolver ambigüedad de negocio sin regla explícita;
- reescribir valores sin traza;
- actuar como normalizador principal del motor.

## 18. Qué acceptance tests mínimos debe tener
1. `happy_path_scalar_mapping`
   - parsed field claro, mapping unívoco, tipado correcto, conversión válida.
2. `happy_path_tabular_units`
   - tabla con varias filas y misma unidad; outputs canónicos completos.
3. `partial_normalization_due_to_missing_unit`
   - algunos campos normalizables, otros no por falta de unidad.
4. `malformed_numeric_value`
   - valor imposible o mal formado que dispara warning/failure sin corrección silenciosa.
5. `ambiguous_label_not_mapped`
   - label superficial ambiguo queda abierto.
6. `unit_conversion_traceability`
   - reconstrucción de factor y regla exacta usada.
7. `date_precision_preserved`
   - fecha completa vs año solo no colapsan.
8. `currency_conversion_requires_basis`
   - sin basis date/year o tabla explícita, no hay conversión.
9. `missing_provenance_blocks_output`
   - normalized record sin refs críticos debe fallar.
10. `replay_manifest_rebuilds_same_output`
   - mismos inputs y mismas reglas producen mismo resultado.

## 19. Qué observabilidad debe exponer
- conteo de `normalized_field_record` por status;
- tasa de `non-normalizable field`;
- warnings por código y severidad;
- failures por código y regla;
- mappings ambiguos recurrentes;
- conversiones por tipo de unidad y por regla;
- pérdidas de unidad original detectadas;
- valores fuera de rango por canonical field;
- drift de mapping entre versiones de reglas;
- replay consistency rate.

No requiere observabilidad avanzada en MVP, pero sí métricas y registros estructurados suficientes para auditoría.

## 20. Qué failure modes deben bloquearse desde el día 1
- `normalized_value` sin `raw_value` o `parsed_value`;
- conversiones sin regla registrada;
- pérdida de unidad o moneda original;
- mapping automático bajo ambigüedad material;
- normalized record sin provenance a parsed/raw;
- coerción no determinista presentada como válida;
- cambio silencioso de schema profile o rule version;
- record marcado completo cuando solo es parcial;
- currencies convertidas sin basis explícita;
- sobrescritura del valor original por el normalizado.

## 21. Qué errores de arquitectura serían muy caros de corregir después
- no separar mapping, typing y conversion;
- no modelar el triple valor original/parsed/normalized;
- no versionar reglas de normalización;
- no registrar replay manifest;
- mezclar field alias locales con taxonomía/global identity;
- materializar solo outputs agregados y no field-level lineage;
- permitir reglas hardcodeadas por fuente sin contrato común.

## 22. Cómo diseñarlo para MVP sin volverlo mediocre
- empezar con pocos `schema_profile` bien definidos;
- limitarse a tipos y unidades con reglas claras y auditables;
- construir primero field-level normalization y envelopes simples;
- privilegiar warnings y estados explícitos sobre heurística agresiva;
- dejar fuera matching profundo, currency intelligence libre, imputación y quality soberana;
- exigir provenance y replay desde el inicio.

## 23. Cómo escalarlo sin volverlo un monolito
- separar catálogo de campos, reglas de mapping, typing y conversiones;
- mantener orchestrator pequeño y reglas modulares;
- añadir nuevas familias de reglas como componentes hermanos, no flags dentro de una clase gigante;
- usar `schema_profile` para agrupar campos por uso downstream sin duplicar lógica;
- aislar validación de integridad de la ejecución de normalización;
- impedir que parsers, taxonomía o identity se cuelen en el write path.

## 24. Una estructura mínima sugerida para pasar luego a código
```text
canonical-normalization-engine/
  MASTER_SPEC.md
  canonical_normalization_engine/
    domain/
      enums.py
      value_objects.py
      entities.py
      records.py
      errors.py
    normalization/
      mapping.py
      typing.py
      conversions.py
      orchestrator.py
      results.py
    validation/
      rules.py
      collector.py
      context.py
      schema_validator.py
      rule_validator.py
      output_validator.py
      orchestrator.py
  tests/
    test_domain.py
    test_validation.py
    test_mapping.py
    test_typing.py
    test_conversions.py
    test_normalization_flow.py
```

## 25. Ejemplos obligatorios
### Ejemplo 1: “Energy Use”, “Power Cons.” y “Annual kWh”
- `original_label` puede ser:
  - `Energy Use`
  - `Power Cons.`
  - `Annual kWh`
- El motor no asume que todo eso significa lo mismo.
- Reglas explícitas posibles:
  - `Annual kWh` + unidad `kWh/year` -> `canonical_field = annual_energy_consumption`
  - `Power Cons.` + unidad `kW` -> `canonical_field = demand_power`
  - `Energy Use` sin unidad ni contexto suficiente -> `ambiguous` o `non-normalizable`
- Resultado:
  - dos fields normalizados con mapping explícito;
  - uno preservado como no normalizable o parcial;
  - sin resolver todavía identidad semántica profunda del sistema o entidad.

### Ejemplo 2: kWh, MWh y GJ
- Fuente A trae `42 kWh`.
- Fuente B trae `3.2 MWh`.
- Fuente C trae `11.5 GJ`.
- El motor debe preservar:
  - `raw_value`
  - `parsed_value`
  - `original_unit`
- Si el `canonical_field_definition` exige energía en `kWh`, entonces:
  - `42 kWh` -> `42 kWh`
  - `3.2 MWh` -> `3200 kWh` con `unit_conversion_rule_id`
  - `11.5 GJ` -> `3194.444... kWh` con factor y policy explícitos
- Nunca se pierde que el origen venía en `MWh` o `GJ`.

### Ejemplo 3: fechas heterogéneas
- Fuente A: `2024-03-17`
- Fuente B: `03/17/2024`
- Fuente C: `2024`
- Las dos primeras pueden normalizarse a tipo `date` si el formato está explícitamente soportado.
- La tercera no debe convertirse a `2024-01-01`.
- Debe materializarse como:
  - `normalized_value = 2024`
  - `canonical_data_type = year`
  - `precision_kind = year_only`
- La diferencia de precisión debe permanecer visible.

### Ejemplo 4: columna “fuel”
- Caso A: tabla de sistemas energéticos donde `fuel` significa vector energético.
- Caso B: tabla financiera donde `fuel` significa costo o gasto de combustible.
- El motor no puede mapear `fuel` solo por superficie.
- Debe usar `mapping_context` explícito:
  - tabla origen;
  - campos vecinos;
  - unidad;
  - schema profile esperado.
- Si el contexto no resuelve, el field queda `ambiguous` o `non-normalizable`.

### Ejemplo 5: valor fuera de rango
- Llega `temperature = 1200 C` en una tabla donde el contexto sugiere ambiente interior.
- El motor no lo corrige a `120 C` ni lo descarta sin registro.
- Debe:
  - preservar `raw_value = "1200"`
  - producir `normalized_value = 1200` si el typing es válido
  - emitir `normalization_warning_record` por rango sospechoso
  - dejar la decisión de aptitud a Quality/Fitness o verificación posterior

### Ejemplo 6: reconstruir una conversión meses después
- Debe poder responder:
  - qué `parsed_field_object_id` originó el valor;
  - qué `field_mapping_rule_id` lo asignó al campo canónico;
  - qué `typing_rule_id` lo tipó;
  - qué `unit_conversion_rule_id` o `currency_conversion_rule_id` lo transformó;
  - qué versiones y fingerprints tenían esas reglas;
  - qué `raw_asset_version_id` y `extraction_metadata_record_id` estaban upstream.
- Eso requiere un `normalization_replay_manifest` y lineage completo por field.
