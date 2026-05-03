# INGESTION + PARSING ENGINE — MASTER SPEC

## 1. Qué es exactamente el Ingestion + Parsing Engine
Motor fundacional que captura fuentes autorizadas, preserva raw immutable, registra contexto de origen y materializa una representación estructural parcial y trazable del contenido. Su función es hacer disciplinado el ingreso del mundo al framework sin convertir retrieval ni parsing en inferencia, normalización, matching o autoridad semántica.

## 2. Qué problema resuelve y qué problema no resuelve
### Resuelve
- registrar una fuente antes de procesarla;
- capturar y preservar `raw_asset` sin sobrescritura;
- fijar hash, retrieval metadata y source-visible version;
- separar claramente raw zone y parsed zone;
- extraer tablas, campos, bloques y metadatos estructurales por formato;
- soportar parsing parcial con warnings, failures recuperables y provenance completo;
- preparar insumo consistente para normalization posterior.

### No resuelve
- suficiencia epistemológica de la fuente;
- normalización de unidades, tipos o vocabulario;
- matching, identidad o joins semánticos;
- inferencia, reporting o verification;
- corrección silenciosa de contenido;
- storage productivo, UI, API o cloud.

## 3. Qué rol cumple dentro del framework completo
- Es un motor transversal de captura y extracción, no una fase.
- Opera antes de normalización, taxonomía, lineage analítico y quality de uso por fase.
- Hace posible que downstream reciba material estructurado con provenance verificable.
- No decide qué significa el contenido; decide solo cómo queda preservado y extraído.

## 4. Qué NO debe hacer
- No reabrir fases cerradas ni alterar su semántica.
- No sobrescribir raw con parsed.
- No inferir columnas, equivalencias o categorías no explícitas.
- No limpiar ruido material sin dejar registro.
- No fusionar retrieval, parsing y normalización en un solo write path.
- No usar parsers “latest” como dependencia persistida.
- No colapsar scraping técnico en interpretación semántica.

## 5. Qué SÍ debe hacer
- consumir `source_record` y `source_access_policy` ya gobernados upstream;
- ejecutar retrieval/capture por tipo de fuente;
- materializar `raw_asset_version` immutable con checksum y context metadata;
- ejecutar una o más `parser_strategy` versionadas sobre el mismo raw;
- producir `parsed_document_object`, `parsed_table_object` y `parsed_field_object`;
- preservar localización estructural exacta o mejor-esfuerzo explícito;
- registrar `extraction_metadata`, `parsing_warning` y `parsing_failure`;
- marcar `partial_parse` sin desechar utilidad restante;
- dejar replay/rebuild exacto del parse.

## 6. Diferencias entre objetos y estados
- `source_record`: identidad registrada de una fuente externa o interna autorizada. No contiene contenido capturado.
- `source_access_policy`: política de acceso, rights, restricciones de retención y uso. No contiene raw.
- `raw_asset`: unidad lógica capturable desde una fuente, por ejemplo un PDF URL, endpoint+query, archivo XLSX o CSV descargable.
- `raw_asset_version`: captura inmutable y fechada de un `raw_asset`, con bytes/payload preservado, checksum y retrieval metadata.
- `parsed_object`: envelope general de extracción de una `raw_asset_version`; nunca existe sin ref a raw y parser strategy.
- `parsed_table`: objeto tabular extraído desde una versión raw, con headers, rows, cells y structural locators.
- `parsed_field`: objeto escalar o fragmento estructural extraído, incluyendo metadata fields, key-value pairs, text blocks o celdas materializadas.
- `extraction_metadata`: metadata técnica de cómo se obtuvo el parse: parser family, strategy version, run id, timing, heuristics usadas, locator confidence.
- `parsing_warning`: problema recuperable que no invalida todo el parse, por ejemplo tabla truncada, selector parcialmente roto o celda fusionada ambigua.
- `parsing_failure`: falla no recuperable para una estrategia o unidad de extracción concreta.
- `partial_parse`: estado en el que parte del raw fue extraída correctamente y parte quedó ausente, ambigua o fallida; no equivale a fracaso total.

## 7. Qué granularidad conviene para parsed objects
### Regla general
El parse debe materializar objetos al nivel mínimo reutilizable downstream sin perder provenance ni inflar el sistema con fragments inútiles.

### Granularidad mínima
| Contenido | Unidad recomendada |
|---|---|
| Documento completo | `parsed_document_object` por `raw_asset_version` y `parser_strategy` |
| Tabla | `parsed_table_object` por tabla/hoja/array tabular identificable |
| Campo escalar | `parsed_field_object` por field, cell, key-value o block relevante |
| Fragmento textual no tabular | `parsed_field_object` con locator de bloque/offset |

### Reglas
- Un mismo `raw_asset_version` puede producir múltiples `parsed_document_object` si corren estrategias distintas; no se mezclan.
- Un `parsed_table_object` siempre cuelga de un `parsed_document_object`.
- Un `parsed_field_object` puede colgar de documento o tabla.
- No se materializa “dato corregido”; solo contenido extraído y trazado.

## 8. Qué objetos internos necesita
### Entidades mínimas
| Objeto | Propósito |
|---|---|
| `retrieval_record` | Registro de una ejecución de captura contra un `source_record`. |
| `raw_asset` | Unidad lógica capturable bajo una fuente y access policy. |
| `raw_asset_version` | Captura inmutable de bytes/payload o archivo exacto. |
| `parsing_run_record` | Ejecución versionada de una estrategia de parser sobre una raw version. |
| `parsed_document_object` | Envelope estructural principal del parse. |
| `parsed_table_object` | Tabla extraída con provenance tabular. |
| `parsed_field_object` | Campo escalar, cell o block estructurado. |
| `parsing_warning_record` | Warning recuperable asociado a run, document, table o field. |
| `parsing_failure_record` | Failure explícito y tipado por scope de extracción. |

### Value objects mínimos
| Objeto | Propósito |
|---|---|
| `source_adapter_ref` | Identifica el adapter de captura usado. |
| `parser_strategy_ref` | Identifica familia, versión y fingerprint del parser. |
| `structural_location` | Localización estructural homogénea por formato. |
| `extraction_metadata` | Metadata técnica de extracción y parámetros efectivos. |
| `parsing_confidence` | Confidence explícita cuando la estrategia lo produce. |
| `request_fingerprint` | Firma estable del request/query de retrieval. |
| `content_checksum` | Hash del raw exacto capturado. |

### Enums mínimos
- `source_format`
- `raw_asset_kind`
- `retrieval_status`
- `parsing_status`
- `warning_severity`
- `failure_severity`
- `location_kind`
- `parser_family`
- `confidence_kind`

## 9. Qué metadatos debe preservar obligatoriamente
- `source_id`
- `source_access_policy_ref`
- `retrieval_record_id`
- `raw_asset_id`
- `raw_asset_version_id`
- `source_adapter_ref`
- `retrieval_timestamp`
- `request_fingerprint`
- `original_uri` o `endpoint_ref`
- `response_status` cuando aplique
- `content_type`
- `charset` cuando aplique
- `content_length`
- `content_checksum`
- `source_visible_version` nullable
- `retrieval_headers_snapshot` o equivalente permitido
- `parser_strategy_ref`
- `parser_run_timestamp`
- `parsing_status`
- `structural_location_refs`
- `warnings`
- `failures`
- `confidence` cuando exista
- `raw_preservation_path_or_pointer`

Ningún parsed object servible puede existir sin `raw_asset_version_id`, `parser_strategy_ref` y al menos un locator o declaración explícita de por qué ese locator no aplica.

## 10. Cómo representar localización estructural
`structural_location` debe ser un value object tipado con `location_kind` y campos opcionales estrictamente gobernados.

### Campos mínimos posibles
- `page_number`
- `table_index`
- `row_index`
- `column_index`
- `cell_address`
- `sheet_name`
- `sheet_index`
- `block_index`
- `char_start`
- `char_end`
- `byte_start`
- `byte_end`
- `css_selector`
- `xpath`
- `json_path`
- `endpoint_ref`
- `payload_pointer`
- `uri_fragment`

### Reglas
- Solo se llenan los campos compatibles con `location_kind`.
- Debe poder representar:
  - página PDF;
  - tabla PDF/HTML;
  - celda CSV/XLSX;
  - bloque textual por offsets;
  - selector DOM;
  - path JSON;
  - endpoint y subpayload API.
- Si el parser no puede ubicar con precisión, debe declarar locator parcial y warning; no inventar precisión.

## 11. Cómo representar estrategias de parser por formato
Separación dura:
- `source_adapter`: obtiene raw.
- `parser_strategy`: transforma raw en estructura parcial.

### `parser_strategy_ref` mínimo
- `parser_family`
- `strategy_name`
- `strategy_version`
- `implementation_fingerprint`
- `parameter_fingerprint`

### Familias mínimas
- `pdf_text`
- `pdf_table`
- `csv_tabular`
- `xlsx_sheet`
- `html_dom`
- `html_table`
- `json_tree`
- `api_json`
- `api_tabular`

Una `parsing_run_record` debe fijar exactamente qué estrategia corrió. El sistema no persiste outputs producidos por una estrategia no versionada.

## 12. Cómo manejar formatos heterogéneos sin volver el sistema inconsistente
Regla: formatos distintos pueden usar estrategias distintas, pero todos deben aterrizar en el mismo contrato base:
- mismo envelope de raw provenance;
- mismo `parsing_run_record`;
- mismo `structural_location`;
- mismo modelo de warnings/failures/confidence;
- mismos invariantes de inmutabilidad y replay.

No se permite que cada parser invente su propio shape soberano. Las diferencias por formato viven en:
- `parser_strategy_ref`;
- `location_kind`;
- campos específicos de locator;
- metadata técnica adicional dentro de `extraction_metadata`.

## 13. Cómo manejar parsing parcial o defectuoso sin perder utilidad
- `parsing_status` debe distinguir al menos `complete`, `partial`, `failed`.
- Un `partial` puede producir parsed tables y fields válidos más warnings/failures parciales.
- Un `failed` para una tabla no obliga a invalidar todo el documento si otras unidades se extrajeron correctamente.
- Ningún parse parcial puede presentarse como completo.
- Los campos ausentes por fallo no se imputan ni se corrigen.

## 14. Cómo manejar fuentes premium/pagadas distinto de públicas
- Toda captura premium debe referir `source_access_policy_ref` explícito y restrictions snapshot.
- Raw premium sigue siendo immutable, pero su acceso y serving downstream quedan restringidos por policy.
- El parsed zone no puede desclasificar raw premium mediante fields o metadata que violen rights.
- Debe preservarse:
  - tipo de licencia o right class;
  - retención permitida;
  - restricciones de redistribución;
  - restricciones de serving downstream.
- Si policy permite captura pero no redistribución, el motor preserva raw en zona restringida y parsed con access flags explícitos.

## 15. Cómo interactúa con otros motores
### Source Registry + Rights Engine
- consume `source_id` y `source_access_policy_ref`;
- no decide rights, solo los aplica y preserva.

### Versioning + Lineage Engine
- cada `raw_asset_version`, `parsing_run_record`, `parsed_document_object`, `parsed_table_object` y `parsed_field_object` debe ser versionable/traceable;
- lineage debe poder reconstruir qué raw y qué parser generaron cada parsed output.

### Taxonomy Service
- no lo usa para resolver significado durante parsing;
- puede referenciar taxonomy solo como parser configuration externa cuando eso no altere extracción.

### Normalization Engine
- entrega parsed outputs estructurados con provenance suficiente;
- no normaliza unidades, nombres ni tipos.

### Quality/Fitness Engine
- expone warnings, failures, coverage y confidence;
- no decide por sí solo si un parse es apto para una fase.

### Evaluation/Conformance Engine
- debe poder auditar raw sin parsed, parsed sin raw, provenance roto, parse parcial y replay fidelity.

## 16. Qué partes pueden automatizarse y cuáles no
### Automatizable
- retrieval/capture;
- hashing;
- metadata técnica de retrieval;
- parse estructural por estrategia conocida;
- locators técnicos;
- warnings mecánicos;
- confidence derivado por estrategia cuando aplique.

### No automatizable sin gobernanza adicional
- interpretación semántica del contenido;
- corrección de encabezados ambiguos;
- matching de entidades;
- taxonomización canónica;
- decisión de suficiencia para uso epistemológico;
- “arreglo” de tablas defectuosas como si fuera verdad.

## 17. Qué rol permitido y prohibido puede tener un LLM dentro de este motor
### Prohibido
- parser soberano en write path;
- corrección silenciosa de contenido;
- extracción semántica que reescriba raw;
- inventar columnas, headers o valores.

### Permitido
- fuera del MVP, solo como asistente no soberano en flujos de rescate manual/quarantined parse candidates;
- cualquier salida LLM debe quedar marcada como no canónica y no sustituir el parse determinístico base.

Para el MVP, el LLM queda fuera del runtime normal del motor.

## 18. Qué acceptance tests mínimos debe tener
- PDF público capturado, hasheado y parseado en tablas/campos con locators válidos.
- CSV parseado completo con row/column locators reproducibles.
- XLSX multi-sheet con celdas fusionadas y parse parcial explícito.
- HTML con selector roto que produce warnings y no contamina parsed previos.
- JSON/API con endpoint ref, request fingerprint y payload pointers estables.
- fuente premium con restrictions metadata y raw serving restringido.
- replay del mismo raw con misma strategy produce mismos parsed ids/checksums esperados.
- raw sin parsed y parsed sin raw quedan detectables.

## 19. Qué observabilidad debe exponer
- counts por formato y por strategy;
- retrieval success/partial/failure rate;
- parsing complete/partial/failure rate;
- warning rate por formato y parser;
- failure clusters por strategy version;
- coverage mínima por unidad de extracción;
- raw-preserved-without-parse count;
- parse-with-broken-provenance count;
- replay mismatch count.

Observabilidad aquí es técnica y de integridad, no dashboard narrativo.

## 20. Qué failure modes deben bloquearse desde el día 1
- `parsed_object` sin `raw_asset_version_id`;
- raw mutable o sobrescrito;
- parse persistido sin `parser_strategy_ref`;
- pérdida de checksum o retrieval metadata;
- parser que “corrige” silenciosamente headers/values;
- mezcla de raw y parsed en la misma zona lógica;
- serving de contenido premium sin access restriction propagada;
- locators imposibles o inventados;
- uso de strategies no versionadas.

## 21. Qué errores de arquitectura serían muy caros de corregir después
- mezclar retrieval, raw preservation y parsing en un único objeto;
- no separar raw zone de parsed zone;
- dejar que cada formato emita shapes incompatibles;
- no versionar parser strategy ni parsing runs;
- parsed outputs sin locators ni warnings;
- permitir corrección silenciosa durante parse;
- no guardar enough metadata para replay exacto;
- convertir parsing en una pseudo-normalización temprana.

## 22. Cómo diseñarlo para MVP sin volverlo mediocre
- soportar un conjunto acotado pero real de formatos: PDF, CSV, XLSX, HTML, JSON/API;
- usar un contrato base común para todos los outputs;
- tratar `partial_parse` como first-class;
- fijar raw immutable, strategy version y locators desde el inicio;
- no intentar resolver semántica ni calidad profunda todavía.

## 23. Cómo escalarlo sin volverlo un monolito
- separar `source_adapter` de `parser_strategy`;
- crecer por familias de parser, no por un mega-parser único;
- mantener `structural_location` y `extraction_metadata` como contrato común;
- aislar parsers específicos por formato en módulos propios;
- dejar replay, validation y serving como capas separadas del dominio de captura y parse.

## 24. Una estructura mínima sugerida para pasar luego a código
```text
governanza/
  ingestion-parsing-engine/
    MASTER_SPEC.md
    ingestion_parsing_engine/
      domain/
        entities/
        value_objects/
        enums/
        records/
      retrieval/
        adapters/
        capture/
      parsing/
        strategies/
        locators/
        warnings/
      validation/
      tests/
        fixtures/
        acceptance/
```

## Ejemplos obligatorios

### Ejemplo 1: PDF público de benchmarking energético industrial
1. `source_record` ya identifica un benchmark público del DOE o banco multilateral.
2. El motor ejecuta `retrieval_record` con `source_adapter_ref=http_download:v1`.
3. Se materializa `raw_asset` para la URL del PDF y `raw_asset_version` con:
   - bytes exactos del PDF;
   - `content_checksum`;
   - `retrieval_timestamp`;
   - `content_type=application/pdf`;
   - `source_visible_version` si el PDF la declara.
4. Corre `parser_strategy_ref=pdf_table:camelot_vX` y `parser_strategy_ref=pdf_text:pdfminer_vY`.
5. Se genera un `parsed_document_object` por strategy.
6. Cada tabla sale como `parsed_table_object` con `location_kind=pdf_table_region`, `page_number`, `table_index`.
7. Cada celda o field clave sale como `parsed_field_object` con `page_number`, `row_index`, `column_index`, `char offsets` si existen.
8. El motor no decide si “kWh/ton” es una métrica normalizada ni si la tabla aplica a un sector específico; solo preserva extracción.

### Ejemplo 2: Base premium pagada con datos utility o de mercado
1. `source_record` refiere una base premium y `source_access_policy_ref` declara rights, retención y serving restrictions.
2. El adapter captura un CSV/API payload autenticado y crea `raw_asset_version` en zona restringida.
3. `retrieval_record` preserva request fingerprint, timestamp, endpoint y restricciones.
4. El parse produce tablas/campos normales del motor, pero todos los outputs cargan access flags derivados de policy.
5. Downstream puede usar parsed objects solo si su policy lo permite; el motor no desclasifica ni duplica raw fuera de la zona restringida.

### Ejemplo 3: Un HTML regulatorio cambia de estructura
1. `raw_asset_version` nuevo preserva HTML exacto con checksum y headers.
2. `parser_strategy_ref=html_table:bs4_xpath_v3` intenta extraer una tabla regulatoria usando selectors previos.
3. La tabla principal no aparece y el parser encuentra solo parte del contenido.
4. El run queda `partial`.
5. Se registran:
   - `parsing_warning_record` por selector roto;
   - `parsing_warning_record` por tabla ausente;
   - `parsed_field_object` de metadata que sí pudo extraerse.
6. El motor no “rellena” la tabla ni reusa outputs viejos como si fueran nuevos.

### Ejemplo 4: Un XLSX con varias hojas, encabezados ambiguos y celdas fusionadas
1. El `raw_asset_version` preserva el archivo XLSX exacto.
2. `parser_strategy_ref=xlsx_sheet:openpyxl_v2` materializa un `parsed_document_object`.
3. Cada hoja relevante genera uno o más `parsed_table_object` con:
   - `sheet_name`;
   - `sheet_index`;
   - rangos de celdas;
   - headers observados tal cual.
4. Las celdas fusionadas no se “desfusionan” semánticamente; se registran como layout ambiguity con warning.
5. Los headers ambiguos quedan como strings extraídos o fields parciales; normalization posterior decidirá si son equivalentes o no.

### Ejemplo 5: Un parser produce una tabla incompleta pero útil
1. Un PDF tiene tres tablas; la segunda sale truncada.
2. El run queda `partial`, no `failed`.
3. `parsed_table_object` 1 y 3 quedan completos.
4. `parsed_table_object` 2 queda materializado con rows parciales, `coverage_ratio` en `extraction_metadata` y warning de truncation.
5. Downstream puede usar las partes útiles con conocimiento explícito del límite.

### Ejemplo 6: Reconstruir exactamente qué contenido se extrajo en una fecha pasada
Para reconstrucción exacta, el motor debe conservar:
- `raw_asset_version_id`;
- bytes/payload raw exacto o pointer immutable controlado;
- `content_checksum`;
- `retrieval_record` completo;
- `parser_strategy_ref` con versión y fingerprint;
- `parameter_fingerprint`;
- `parsing_run_record`;
- todos los `structural_location`;
- warnings/failures del run;
- ids y checksums de `parsed_document_object`, `parsed_table_object` y `parsed_field_object`.

Con eso, un replay puede reejecutar el parser exacto o, al menos, auditar si el parsed persistido corresponde fielmente al raw capturado y a la strategy declarada.
