# Functional Contract — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.

Contenido completado para gate de documentation_base.
-->

## inputs
- normalized_records: array<NormalizedRecord> — producido por `motor_005`; cada item debe incluir `record_id`, `normalized_fields`, `source_ref`, `provenance_ref` y tipo de entidad declarado.
- canonical_entities: array<CanonicalEntity> — producido por `motor_003`; contiene entidades autorizadas, aliases canonicos, clase taxonomica y identificadores estables disponibles.
- resolution_policy: object — configuracion local versionada del motor; define umbrales deterministas, pesos permitidos y reglas de empate para identity matching.
- previous_identity_records: array<IdentityRecord> — historial opcional de resoluciones previas; se usa solo como referencia trazable y no como autorizacion para mutar decisiones nuevas sin evaluacion.

## outputs
- identity_resolution_record: IdentityRecord — registro auditable consumido por motores downstream que requieren identidad resuelta, especialmente evaluacion de calidad y lineage.
- entity_cluster: EntityCluster — grupo de `record_id` que representan la misma entidad bajo una decision determinista o un cluster con ambigüedad explicitada.
- ambiguity_flag: AmbiguityFlag — senal estructurada para consumidores downstream cuando la identidad no puede cerrarse sin riesgo de merge erroneo.
- resolution_conflict: ResolutionConflict — salida de diagnostico cuando dos o mas candidatos tienen evidencia contradictoria o reglas de resolucion incompatibles.

## limits
- No acepta registros sin `record_id`, sin `source_ref` o sin `provenance_ref`.
- No acepta entidades canonicas sin identificador estable o sin clase taxonomica minima.
- No acepta texto crudo como sustituto de `normalized_records`; la normalizacion debe estar completada antes.
- No produce documentos deduplicados, listas de documentos unicos ni decisiones de dataset inflation; eso pertenece a `motor_010`.
- No produce una entidad canonica nueva como autoridad global; solo propone clusters y registros de identidad dentro de su contrato.
- No produce merges irreversibles ni modifica el contenido de los registros fuente.

## validations
- Rechaza cualquier `normalized_record` con `record_id`, `source_ref`, `provenance_ref` o `normalized_fields` ausente.
- Rechaza cualquier `canonical_entity` sin `canonical_entity_id`, `entity_type` o identificador de version de taxonomia.
- Verifica que todos los candidatos comparados pertenezcan a una clase de entidad compatible antes de calcular identidad.
- Verifica que cada decision emitida tenga `decision`, `confidence_band`, `evidence_refs`, `rule_version` y `lineage_refs`.
- Emite `ambiguity_flag` en lugar de `resolved_same_entity` cuando la evidencia esta bajo umbral, hay empate entre candidatos o existe conflicto de clase taxonomica.
- Registra `resolution_conflict` cuando dos reglas deterministas producen resultados incompatibles para el mismo par o cluster.
- Mantiene referencias a todos los `record_id` evaluados para que la resolucion pueda reconstruirse sin depender de estado implicito.
