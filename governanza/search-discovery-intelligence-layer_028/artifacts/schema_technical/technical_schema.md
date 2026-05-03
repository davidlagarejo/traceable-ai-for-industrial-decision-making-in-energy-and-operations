# Technical Schema — Search / Discovery Intelligence Layer

Motor ID: motor_028

## entities

| Entidad | Tipo Python | Descripción funcional |
|---|---|---|
| `DiscoveryPlan` | `@dataclass(frozen=True)` | Plan reproducible de búsqueda derivado de una solicitud, taxonomía y señales de refresh. Contiene las consultas, filtros, condiciones de parada y versiones de inputs usados. |
| `SourceCandidateRecord` | `@dataclass(frozen=True)` | Fuente candidata propuesta para revisión. Nunca es fuente aprobada. Siempre lleva `candidate_status=proposed` y provenance completo. |
| `CoverageGapRecord` | `@dataclass(frozen=True)` | Registro de hueco de cobertura observado con evidencia estructural, términos afectados y relación con señales de refresh. |
| `DiscoveryRejectionRecord` | `@dataclass(frozen=True)` | Registro estructurado de un hallazgo rechazado: sin locator, duplicado, fuera de scope, restricción de acceso incompatible. |
| `DiscoveryRunManifest` | `@dataclass(frozen=True)` | Manifiesto versionado de una corrida: inputs, consultas ejecutadas, candidatos emitidos, rechazos y limitaciones observadas. |
| `DiscoveryResult` | `@dataclass` | Contenedor de salida que agrupa plan, candidatos, gaps, rechazos, manifiesto y señales de degradación de una corrida completa. |

## fields

### DiscoveryPlan
| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `plan_id` | `str` | sí | Identificador estable derivado de hash de inputs versionados |
| `request_id` | `str` | sí | Referencia al `DiscoveryRequest` que originó el plan |
| `scope_terms` | `list[str]` | sí | Términos canónicos o aliases validados contra motor_003 |
| `original_scope_terms` | `list[str]` | sí | Términos tal como llegaron en la solicitud (antes de expansión) |
| `queries` | `list[dict]` | sí | Consultas reproducibles generadas del scope y señales |
| `filters` | `dict` | sí | Filtros de jurisdicción, periodo, idioma, tipo de fuente |
| `seed_source_ids` | `list[str]` | sí | IDs de fuentes semilla del registro de motor_008 |
| `taxonomy_version` | `str` | sí | Versión o timestamp del scope taxonómico usado |
| `input_versions` | `dict[str, str\|None]` | sí | Versiones o timestamps de cada input usado |
| `access_restrictions` | `list[str]` | sí | Restricciones de derechos conocidas que limitan la búsqueda |
| `stop_conditions` | `list[str]` | sí | Condiciones de parada declaradas |
| `created_at` | `str` | sí | ISO 8601 timestamp de creación del plan |
| `version_id` | `str` | sí | Identificador de versión del objeto |
| `version_hash` | `str` | sí | Hash SHA-256 del contenido canónico del plan |
| `source_ref` | `str` | sí | Referencia de lineage a los inputs que lo produjeron |
| `produced_by_motor` | `str` | sí | Siempre `motor_028` |
| `produced_at` | `str` | sí | ISO 8601 timestamp de producción |
| `parent_id` | `str\|None` | no | ID del plan padre si es refinamiento de uno previo |

### SourceCandidateRecord
| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `candidate_id` | `str` | sí | Identificador estable derivado de `run_id` + `locator` |
| `run_id` | `str` | sí | Corrida que produjo este candidato |
| `locator` | `str` | sí | URL u otro identificador externo estable de la fuente |
| `title` | `str` | sí | Título o nombre de la fuente candidata |
| `publisher` | `str\|None` | no | Publicador o entidad emisora cuando existe |
| `source_type` | `str` | sí | Tipo de fuente: `regulatory`, `academic`, `institutional`, etc. |
| `domain_taxonomic` | `list[str]` | sí | Términos canónicos del dominio matched |
| `matched_terms` | `list[str]` | sí | Términos que motivaron el hallazgo |
| `discovery_reason` | `str` | sí | Razón narrativa del descubrimiento (de qué gap o señal proviene) |
| `discovery_method` | `str` | sí | Método usado: `taxonomy_expansion`, `gap_fill`, `seed_crawl`, etc. |
| `discovered_at` | `str` | sí | ISO 8601 timestamp del hallazgo |
| `candidate_status` | `str` | sí | Siempre `proposed` al emitir; nunca `approved` |
| `discovery_classification` | `str` | sí | `new_candidate`, `rediscovery`, `potential_duplicate` |
| `linked_source_id` | `str\|None` | no | `source_id` de motor_008 si coincide con fuente ya registrada |
| `duplicate_of_candidate_id` | `str\|None` | no | ID de candidato previo si es posible duplicado |
| `rights_review_required` | `bool` | sí | Indica si motor_008 debe revisar derechos antes de uso |
| `access_class` | `str\|None` | no | Clase de acceso conocida si está disponible |
| `provenance` | `dict` | sí | Referencia a plan, consulta, corrida e inputs versionados |
| `version_id` | `str` | sí | Identificador de versión del objeto |
| `version_hash` | `str` | sí | Hash SHA-256 del contenido canónico |
| `source_ref` | `str` | sí | Referencia de lineage a la corrida que lo produjo |
| `produced_by_motor` | `str` | sí | Siempre `motor_028` |
| `produced_at` | `str` | sí | ISO 8601 timestamp de producción |
| `parent_id` | `str\|None` | no | ID del candidato previo si es refinamiento |

### CoverageGapRecord
| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `gap_id` | `str` | sí | Identificador estable del gap |
| `run_id` | `str` | sí | Corrida que detectó el gap |
| `scope_terms` | `list[str]` | sí | Términos afectados por el gap |
| `gap_type` | `str` | sí | `missing_jurisdiction`, `low_coverage`, `stale_sources`, etc. |
| `severity` | `str` | sí | `high`, `medium`, `low` |
| `supporting_signal_ids` | `list[str]` | sí | IDs de señales de motor_009 que evidencian el gap |
| `evidence` | `dict` | sí | Datos estructurales que motivan el gap (fuentes existentes, conteos) |
| `taxonomy_relation` | `dict` | sí | Relación con la taxonomía canónica (nodo afectado, aliases) |
| `observed_at` | `str` | sí | ISO 8601 timestamp de observación |
| `version_id` | `str` | sí | Identificador de versión |
| `version_hash` | `str` | sí | Hash SHA-256 del contenido canónico |
| `source_ref` | `str` | sí | Referencia de lineage |
| `produced_by_motor` | `str` | sí | Siempre `motor_028` |
| `produced_at` | `str` | sí | ISO 8601 timestamp |
| `parent_id` | `str\|None` | no | Gap previo si es refinamiento |

### DiscoveryRejectionRecord
| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `rejection_id` | `str` | sí | Identificador estable del rechazo |
| `run_id` | `str` | sí | Corrida que produjo el rechazo |
| `locator` | `str\|None` | no | Locator del hallazgo rechazado si estaba disponible |
| `reason_code` | `str` | sí | Código estructurado: `duplicate`, `no_locator`, `out_of_scope`, `access_restriction`, `raw_content`, `prior_rejection` |
| `reason_detail` | `str` | sí | Descripción del motivo de rechazo |
| `observed_at` | `str` | sí | ISO 8601 timestamp |
| `source_ref` | `str\|None` | no | Referencia al `source_id` existente si es duplicado |
| `provenance` | `dict` | sí | Consulta, plan y corrida que encontraron el hallazgo rechazado |
| `produced_by_motor` | `str` | sí | Siempre `motor_028` |
| `produced_at` | `str` | sí | ISO 8601 timestamp |

### DiscoveryRunManifest
| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `run_id` | `str` | sí | Identificador de la corrida, derivado de hash del plan + inputs + adapter |
| `plan_id` | `str` | sí | Plan que guió la corrida |
| `input_versions` | `dict[str, str\|None]` | sí | Versiones o timestamps de los 5 inputs usados |
| `executed_queries` | `list[dict]` | sí | Consultas ejecutadas con término, filtros y timestamp |
| `candidate_ids` | `list[str]` | sí | IDs de candidatos emitidos |
| `rejection_ids` | `list[str]` | sí | IDs de rechazos estructurados |
| `limitations_observed` | `list[str]` | sí | Limitaciones encontradas durante la corrida |
| `run_started_at` | `str` | sí | ISO 8601 inicio de corrida |
| `run_completed_at` | `str` | sí | ISO 8601 fin de corrida |
| `run_status` | `str` | sí | `completed`, `completed_with_warnings`, `empty_result` |
| `version_id` | `str` | sí | Identificador de versión |
| `version_hash` | `str` | sí | Hash SHA-256 del contenido canónico |
| `source_ref` | `str` | sí | Referencia de lineage a inputs |
| `produced_by_motor` | `str` | sí | Siempre `motor_028` |
| `produced_at` | `str` | sí | ISO 8601 timestamp |
| `parent_id` | `str\|None` | no | Manifiesto padre si es re-corrida |

## relationships

- `DiscoveryPlan.request_id` → `DiscoveryRequest.request_id` (referencia externa, no persistida en este motor)
- `SourceCandidateRecord.run_id` → `DiscoveryRunManifest.run_id`
- `SourceCandidateRecord.linked_source_id` → `source_id` de motor_008 (referencia cross-motor)
- `SourceCandidateRecord.duplicate_of_candidate_id` → `SourceCandidateRecord.candidate_id` (auto-referencia)
- `CoverageGapRecord.run_id` → `DiscoveryRunManifest.run_id`
- `CoverageGapRecord.supporting_signal_ids` → IDs de señales de motor_009 (referencia cross-motor)
- `DiscoveryRejectionRecord.run_id` → `DiscoveryRunManifest.run_id`
- `DiscoveryRejectionRecord.source_ref` → `source_id` de motor_008 si es duplicado
- `DiscoveryRunManifest.plan_id` → `DiscoveryPlan.plan_id`
- `DiscoveryRunManifest.candidate_ids` → `SourceCandidateRecord.candidate_id` (lista)
- `DiscoveryRunManifest.rejection_ids` → `DiscoveryRejectionRecord.rejection_id` (lista)

## identifiers

| Entidad | ID canónico | Derivación |
|---|---|---|
| `DiscoveryPlan` | `plan_id` | Hash SHA-256 prefijado de input_versions serializados |
| `SourceCandidateRecord` | `candidate_id` | Hash SHA-256 prefijado de `run_id` + `locator` + `source_type` |
| `CoverageGapRecord` | `gap_id` | Hash SHA-256 prefijado de `run_id` + `scope_terms` + `gap_type` |
| `DiscoveryRejectionRecord` | `rejection_id` | Hash SHA-256 prefijado de `run_id` + `locator` (o hash de `reason_detail` si no hay locator) |
| `DiscoveryRunManifest` | `run_id` | Hash SHA-256 prefijado de `plan_id` + `input_versions` + `adapter_id` |

Todos los IDs son estables y deterministas: mismos inputs producen mismo ID. No se usan UUIDs aleatorios.

## versioning

Todos los objetos de output llevan:
- `version_id`: identificador de versión del objeto, derivado del mismo hash que el ID canónico
- `version_hash`: hash SHA-256 del contenido canónico serializado en JSON ordenado
- `produced_at`: ISO 8601 timestamp de cuándo fue producido el objeto

El campo `parent_id` permite trazar refinamientos o re-corridas sobre el mismo plan o candidato.

Los inputs son versionados externamente (motor_008, motor_003, motor_009) y sus versiones quedan registradas en `input_versions` del plan y del manifiesto.

## lineage

Todos los objetos de output llevan:
- `source_ref`: hash prefijado que referencia el conjunto de inputs versionados que lo produjeron
- `produced_by_motor`: siempre `motor_028`
- `produced_at`: ISO 8601 timestamp

`DiscoveryRunManifest.input_versions` registra las versiones exactas de los 5 inputs para permitir reconstrucción auditora de cualquier corrida.

`SourceCandidateRecord.provenance` registra plan, consulta, corrida, adapter e input versions para permitir reconstruir exactamente cómo fue encontrado el candidato.
