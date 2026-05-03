# Failure Modes Spec — Search / Discovery Intelligence Layer

Motor ID: motor_028

## failure_modes_list

### FM-01: Drift taxonómico de queries
**Descripción técnica:** Las consultas generadas usan términos no mapeados a la taxonomía canónica de motor_003, creando dominios paralelos no autorizados.
**Condición de activación:** `DiscoveryPlan.scope_terms` contiene términos que no están en `canonical_taxonomy_scope.terms` ni en sus aliases. El motor usa inferencia narrativa para expandir el scope en lugar de rechazar el request.
**Síntoma observable:** `SourceCandidateRecord.domain_taxonomic` contiene valores que no aparecen en la taxonomía de motor_003. `DiscoveryPlan.scope_terms` difiere de los términos validados en `input_versions.taxonomy_version`.
**Prevención:** El motor valida cada término del request contra `canonical_taxonomy_scope` antes de construir el plan. Términos no reconocidos causan rechazo del request o gap record, nunca expansión silenciosa.

### FM-02: Pérdida de provenance en candidatos
**Descripción técnica:** `SourceCandidateRecord` emitidos sin `provenance.plan_id`, `provenance.run_id` o `provenance.input_versions`, haciendo imposible reconstruir cómo fue encontrado el candidato.
**Condición de activación:** El adaptador o la lógica de construcción de candidatos omite campos de provenance por optimización o error de integración.
**Síntoma observable:** `SourceCandidateRecord.provenance` vacío o sin `plan_id`. Imposibilidad de relacionar el candidato con una corrida auditada. `DiscoveryRunManifest.candidate_ids` no coincide con candidatos que se pueden rastrear.
**Prevención:** La construcción de `SourceCandidateRecord` siempre recibe `run_id`, `plan_id` e `input_versions` como parámetros obligatorios. No hay ruta de construcción que los omita.

### FM-03: Candidato emitido como fuente aprobada
**Descripción técnica:** Un `SourceCandidateRecord` sale con `candidate_status` distinto de `"proposed"`, o el motor produce un objeto que motor_008 podría interpretar como fuente ya admitida.
**Condición de activación:** Modificación incorrecta del flujo de construcción de candidatos, o integración que intenta pre-aprobar candidatos para acelerar el pipeline.
**Síntoma observable:** `SourceCandidateRecord.candidate_status` toma valores como `"approved"`, `"registered"`, `"active"` o similares.
**Prevención:** La constante `candidate_status="proposed"` está fija en la construcción del dataclass. El motor nunca recibe ni produce perfiles de derechos ni registros de fuente finales. Motor_008 es el único que puede promover un candidato.

### FM-04: Re-emisión de candidatos ya rechazados o ya registrados
**Descripción técnica:** El motor propone como `"new_candidate"` una fuente que ya existe en `source_registry_snapshot` o ya fue rechazada en `prior_discovery_log`.
**Condición de activación:** El chequeo de duplicados contra el registro y el log previo no se ejecuta, o se omite por performance.
**Síntoma observable:** `SourceCandidateRecord.discovery_classification="new_candidate"` para una fuente cuyo locator aparece en el registro de motor_008. Ausencia de `linked_source_id` o `duplicate_of_candidate_id` cuando debería estar presente.
**Prevención:** Antes de emitir cualquier candidato, el motor verifica el locator contra `source_registry_snapshot` y `prior_discovery_log`. Coincidencias producen `"rediscovery"`, `"potential_duplicate"` o `DiscoveryRejectionRecord`, nunca `"new_candidate"` limpio.

### FM-05: Expansión de responsabilidad hacia ingesta o aprobación
**Descripción técnica:** El motor comienza a descargar contenido de fuentes, persistir datos raw, normalizar registros o crear perfiles de derechos como efecto secundario del descubrimiento.
**Condición de activación:** Integración que añade pasos de descarga o procesamiento de contenido al flujo de descubrimiento para "ahorrar pasos". Presencia de campos de contenido raw (`body`, `content`, `html`, etc.) en los outputs.
**Síntoma observable:** Outputs contienen campos de contenido raw. Tamaño de outputs crece desproporcionalmente respecto al número de candidatos. Aparecen objetos con estructura de motor_004 o motor_008 mezclados con los outputs de motor_028.
**Prevención:** El motor verifica la ausencia de campos raw en todos los inputs y rechaza cualquier input que los contenga. Los outputs son únicamente metadata: locators, identificadores, razones y provenance. No hay capacidad de descarga ni persistencia de contenido.

### FM-06: IDs no deterministas entre corridas
**Descripción técnica:** `plan_id` o `run_id` varían entre corridas con los mismos inputs, rompiendo la auditabilidad y la capacidad de detectar duplicados entre corridas.
**Condición de activación:** Uso de UUIDs aleatorios o timestamps variables como base de identificadores en lugar de hashes de contenido.
**Síntoma observable:** Dos corridas con inputs idénticos producen `plan_id` diferentes. Imposibilidad de correlacionar corridas para detectar re-ejecuciones innecesarias.
**Prevención:** Todos los IDs se derivan de hash SHA-256 sobre contenido canónico serializado con claves ordenadas. No se usan fuentes de aleatoriedad.

## anti_patterns

### AP-01: Búsqueda sin `DiscoveryRequest` formal
Ejecutar corridas pasando solo listas de URLs o términos ad-hoc sin un `DiscoveryRequest` con `request_id`, `reason` y `scope_terms` canónicos. Resultado: candidatos sin trazabilidad a una solicitud, sin `plan_id` y sin capacidad de auditoría posterior.

### AP-02: Tratar `SourceCandidateRecord` como fuente admitida
Usar el output de motor_028 directamente en pipelines de ingestión sin pasar por la revisión de motor_008. El candidato siempre es una propuesta; solo motor_008 puede crear una fuente registrada con derechos validados.

### AP-03: Mezclar descubrimiento con ingesta en el mismo step
Añadir lógica de descarga, parsing o normalización al flujo de motor_028 para reducir el número de pasos en el pipeline. Esto viola los límites del motor y produce outputs de responsabilidad mixta que no pueden auditarse por separado.

### AP-04: Usar el motor como autoridad de relevancia final
Confiar en las queries generadas por motor_028 como criterio definitivo de qué fuentes son científicamente válidas o aptas para uso analítico. El motor propone candidatos basados en scope y señales; la evaluación de relevancia y calidad corresponde a motores posteriores.

### AP-05: Omitir `prior_discovery_log` entre corridas
Pasar un log previo vacío en corridas consecutivas sobre el mismo scope. Resultado: re-emisión repetida de los mismos candidatos como `"new_candidate"`, inflando el pipeline de revisión de motor_008 con trabajo ya realizado.

## degradation_signals

### DS-01: Crecimiento de `candidate_status != "proposed"`
Cualquier aparición de `candidate_status` con valor distinto de `"proposed"` en el output. Indica que el motor está asumiendo roles de aprobación que no le corresponden.

### DS-02: Porcentaje creciente de candidatos sin publisher o sin locator estable
Si más del 20% de los candidatos emitidos en una corrida no tienen `publisher` Y tienen `locator` con formato inestable (sin esquema URL reconocible), indica degradación en la calidad de las fuentes semilla o en los adaptadores de búsqueda.

### DS-03: Tasa alta de re-emisión de candidatos previos
Si más del 30% de los candidatos de una corrida ya aparecen en `prior_discovery_log` como `"new_candidate"` sin referencia al registro previo, indica que el chequeo de duplicados está fallando.

### DS-04: `DiscoveryRunManifest.executed_queries` vacío con candidatos no vacíos
Un manifiesto con `candidate_ids` no vacío pero `executed_queries` vacío indica pérdida de trazabilidad entre las consultas y los candidatos producidos.

### DS-05: `input_versions` con valores `null` para inputs obligatorios
Si `DiscoveryPlan.input_versions` o `DiscoveryRunManifest.input_versions` tienen `null` para `source_registry_snapshot`, `canonical_taxonomy_scope` o `refresh_intelligence_signals`, indica que esos inputs no fueron versionados correctamente y la corrida no es reproducible.

### DS-06: Ausencia sistemática de `CoverageGapRecord` en corridas con señales de gap activas
Si `refresh_intelligence_signals` contiene señales de `low_coverage` o `stale_sources` con `severity="high"` y la corrida no emite ningún `CoverageGapRecord`, indica que la lógica de detección de gaps no está procesando las señales correctamente.

## expensive_errors

### EE-01: IDs no deterministas en producción
Si `plan_id` o `run_id` se implementan con aleatoriedad en lugar de hashes deterministas y ya hay corridas en producción, corregir requiere re-indexar todo el historial de candidatos y manifiestos, ya que las referencias cruzadas quedan rotas.

### EE-02: Candidatos aprobados prematuramente
Si candidatos de motor_028 son usados directamente por otros motores sin pasar por motor_008, y luego se descubre que no tenían derechos validados, el retrabajo implica invalidar datos de ingesta, normalización y posiblemente reportes ya generados con esas fuentes.

### EE-03: Pérdida masiva de `prior_discovery_log`
Si el log de corridas previas se pierde o no se persiste entre sesiones, el motor no puede detectar duplicados y re-emite el universo completo de candidatos en la siguiente corrida. El costo es proporcional al volumen acumulado de descubrimientos.

### EE-04: Drift silencioso de taxonomía
Si el motor acepta términos no canónicos sin rechazo explícito y construye planes con ellos, los candidatos emitidos quedan asociados a términos que no existen en la taxonomía de motor_003. Corregir requiere rehacer la clasificación taxonómica de todos los candidatos afectados y posiblemente re-ejecutar corridas completas.
