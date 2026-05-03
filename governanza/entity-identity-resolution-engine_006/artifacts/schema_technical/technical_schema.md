# Technical Schema — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.
-->

## entities
- IdentityRecord: decision tecnica auditable emitida por `motor_006` para un conjunto de `record_id` evaluados. Vive en la etapa `schema_technical` como entidad de contrato, y en `implementation` como output persistible `identity_resolution_record`.
- EntityCluster: agrupacion trazable de registros normalizados que representan una misma entidad candidata, confirmada o ambigua. Vive en la etapa `schema_technical` como estructura de salida, y en `implementation` como output persistible `entity_cluster`.
- ResolutionConflict: diagnostico estructurado de evidencia, taxonomia o reglas incompatibles durante la resolucion de identidad. Vive en la etapa `schema_technical` como entidad de control de errores, y en `implementation` como output persistible cuando una decision no puede cerrarse limpiamente.
- AmbiguityFlag: bandera estructurada que preserva una identidad abierta sin forzar merge. Vive en la etapa `schema_technical` como salida obligatoria para decisiones ambiguas, y en `implementation` como output consumible por motores downstream.
- CandidateMatch: comparacion intermedia entre un `NormalizedRecord` y una entidad canonica o cluster candidato. Vive en la etapa `schema_technical` como entidad derivada interna, y en `implementation` como evidencia reconstruible para `IdentityRecord`.

## fields
IdentityRecord:
- identity_record_id: string (required) — identificador estable de la decision de identidad emitida por `motor_006`.
- evaluated_record_ids: array<string> (required) — lista explicita de `record_id` evaluados; no admite miembros implicitos por orden o posicion.
- decision: enum<same_entity, distinct_entity, ambiguous> (required) — resultado determinista de la evaluacion.
- confidence_band: enum<high, medium, low, unresolved> (required) — banda discreta de confianza, derivada de la `resolution_policy` aplicada.
- evidence_refs: array<string> (required) — referencias a `CandidateMatch`, reglas o evidencia normalizada que sustentan la decision.
- rule_version: string (required) — version de la politica o reglas de resolucion usadas.
- lineage_refs: array<string> (required) — referencias de lineage heredadas de registros, candidatos y entidades canonicas evaluadas.
- ambiguity_flag_id: string | null (optional) — referencia a `AmbiguityFlag` cuando `decision` es `ambiguous`.
- conflict_ids: array<string> (optional) — referencias a `ResolutionConflict` relacionados con la decision.
- version_id: string (required) — version del objeto de decision.
- created_at: datetime (required) — timestamp ISO-8601 de creacion del objeto.
- updated_at: datetime (required) — timestamp ISO-8601 de ultima actualizacion controlada.
- version_hash: string (required) — hash determinista del contenido versionado.
- source_ref: string (required) — referencia agregada a las fuentes de los registros evaluados.
- produced_by_motor: string (required) — valor fijo `motor_006`.
- produced_at: datetime (required) — timestamp ISO-8601 de emision por el motor.
- parent_id: string | null (optional) — referencia a una decision previa si este objeto corrige o reemplaza una resolucion anterior.

EntityCluster:
- entity_cluster_id: string (required) — identificador estable del cluster emitido por `motor_006`.
- canonical_entity_id: string | null (optional) — referencia a `CanonicalEntity` de `motor_003` cuando existe entidad canonica compatible.
- member_record_ids: array<string> (required) — lista explicita de `record_id` incluidos en el cluster.
- cluster_status: enum<confirmed, provisional, ambiguous> (required) — estado operativo del cluster.
- identity_record_ids: array<string> (required) — decisiones `IdentityRecord` que sustentan el cluster.
- lineage_refs: array<string> (required) — referencias de lineage de los miembros y decisiones asociadas.
- version_id: string (required) — version del objeto de cluster.
- created_at: datetime (required) — timestamp ISO-8601 de creacion del objeto.
- updated_at: datetime (required) — timestamp ISO-8601 de ultima actualizacion controlada.
- version_hash: string (required) — hash determinista del contenido versionado.
- source_ref: string (required) — referencia agregada a las fuentes de los registros miembros.
- produced_by_motor: string (required) — valor fijo `motor_006`.
- produced_at: datetime (required) — timestamp ISO-8601 de emision por el motor.
- parent_id: string | null (optional) — referencia a un cluster previo si este objeto deriva de una resolucion anterior.

ResolutionConflict:
- conflict_id: string (required) — identificador estable del conflicto de resolucion.
- involved_record_ids: array<string> (required) — `record_id` afectados por el conflicto.
- involved_candidate_match_ids: array<string> (required) — comparaciones intermedias que originan o prueban el conflicto.
- conflict_type: enum<identifier_collision, taxonomy_mismatch, evidence_tie, provenance_conflict, rule_conflict> (required) — categoria tecnica del conflicto.
- blocking_reason: string (required) — explicacion operativa de por que la resolucion queda bloqueada o degradada.
- recommended_next_step: enum<manual_review, await_more_evidence, split_cluster, keep_ambiguous> (required) — siguiente accion permitida sin invadir otros motores.
- related_identity_record_ids: array<string> (optional) — decisiones asociadas al conflicto.
- version_id: string (required) — version del objeto de conflicto.
- created_at: datetime (required) — timestamp ISO-8601 de creacion del objeto.
- updated_at: datetime (required) — timestamp ISO-8601 de ultima actualizacion controlada.
- version_hash: string (required) — hash determinista del contenido versionado.
- source_ref: string (required) — referencia agregada a las fuentes involucradas.
- produced_by_motor: string (required) — valor fijo `motor_006`.
- produced_at: datetime (required) — timestamp ISO-8601 de emision por el motor.
- parent_id: string | null (optional) — referencia a un conflicto anterior si este objeto lo reemplaza o amplia.

AmbiguityFlag:
- ambiguity_flag_id: string (required) — identificador estable de la bandera de ambigüedad.
- identity_record_id: string (required) — referencia a la decision `IdentityRecord` que permanece abierta.
- ambiguity_reason: enum<insufficient_evidence, contradictory_evidence, candidate_tie, missing_canonical_reference, taxonomy_uncertainty> (required) — razon tecnica de la ambigüedad.
- severity: enum<warning, blocking> (required) — severidad para consumidores downstream.
- affected_record_ids: array<string> (required) — registros afectados por la ambigüedad.
- evidence_refs: array<string> (required) — evidencia usada para decidir que el caso debe quedar abierto.
- version_id: string (required) — version del objeto de bandera.
- created_at: datetime (required) — timestamp ISO-8601 de creacion del objeto.
- updated_at: datetime (required) — timestamp ISO-8601 de ultima actualizacion controlada.
- version_hash: string (required) — hash determinista del contenido versionado.
- source_ref: string (required) — referencia agregada a las fuentes afectadas.
- produced_by_motor: string (required) — valor fijo `motor_006`.
- produced_at: datetime (required) — timestamp ISO-8601 de emision por el motor.
- parent_id: string | null (optional) — referencia a una bandera previa si esta sustituye o refina una ambigüedad anterior.

CandidateMatch:
- candidate_match_id: string (required) — identificador estable de la comparacion intermedia.
- record_id: string (required) — referencia al `NormalizedRecord` evaluado.
- candidate_ref: string (required) — referencia a `canonical_entity_id` o `entity_cluster_id` candidato.
- candidate_type: enum<canonical_entity, entity_cluster> (required) — tipo tecnico del candidato comparado.
- match_features: object (required) — features normalizadas usadas por las reglas deterministas; no incluye texto crudo no normalizado.
- match_result: enum<pass, fail, tie, insufficient> (required) — resultado de la comparacion contra la politica vigente.
- rule_version: string (required) — version de reglas aplicada a la comparacion.
- evidence_refs: array<string> (required) — referencias a campos, identificadores o lineage que sustentan la comparacion.
- version_id: string (required) — version del objeto de comparacion.
- created_at: datetime (required) — timestamp ISO-8601 de creacion del objeto.
- updated_at: datetime (required) — timestamp ISO-8601 de ultima actualizacion controlada.
- version_hash: string (required) — hash determinista del contenido versionado.
- source_ref: string (required) — referencia a la fuente del registro evaluado.
- produced_by_motor: string (required) — valor fijo `motor_006`.
- produced_at: datetime (required) — timestamp ISO-8601 de emision por el motor.
- parent_id: string | null (optional) — referencia a una comparacion previa si esta reemplaza una evaluacion anterior.

## relationships
- IdentityRecord.evaluated_record_ids -> NormalizedRecord.record_id: referencia externa obligatoria hacia `normalized_records` producidos por `motor_005`.
- CandidateMatch.record_id -> NormalizedRecord.record_id: referencia externa obligatoria hacia el registro normalizado comparado.
- CandidateMatch.candidate_ref -> CanonicalEntity.canonical_entity_id | EntityCluster.entity_cluster_id: referencia polimorfica controlada por `candidate_type`.
- IdentityRecord.evidence_refs -> CandidateMatch.candidate_match_id: referencia n:m desde decisiones hacia comparaciones que las sustentan.
- IdentityRecord.ambiguity_flag_id -> AmbiguityFlag.ambiguity_flag_id: referencia 1:0..1; requerida cuando `IdentityRecord.decision` es `ambiguous`.
- IdentityRecord.conflict_ids -> ResolutionConflict.conflict_id: referencia 1:n opcional para decisiones afectadas por conflictos.
- EntityCluster.identity_record_ids -> IdentityRecord.identity_record_id: referencia n:m desde clusters hacia decisiones compatibles.
- EntityCluster.member_record_ids -> NormalizedRecord.record_id: referencia externa obligatoria a todos los miembros del cluster.
- EntityCluster.canonical_entity_id -> CanonicalEntity.canonical_entity_id: referencia externa opcional hacia `motor_003`; null cuando el cluster es provisional o ambiguo.
- ResolutionConflict.involved_candidate_match_ids -> CandidateMatch.candidate_match_id: referencia n:m hacia comparaciones incompatibles.
- ResolutionConflict.related_identity_record_ids -> IdentityRecord.identity_record_id: referencia opcional hacia decisiones que el conflicto bloquea o degrada.
- AmbiguityFlag.identity_record_id -> IdentityRecord.identity_record_id: referencia 1:1 hacia la decision abierta.
- AmbiguityFlag.affected_record_ids -> NormalizedRecord.record_id: referencia externa a los registros afectados por ambigüedad.
- parent_id -> same entity identifier: referencia interna opcional para reconstruir reemplazos, correcciones o derivaciones versionadas sin mutacion silenciosa.

## identifiers
- IdentityRecord: `identity_record_id` es la clave estable canonica del registro de decision; se calcula o asigna de forma determinista desde `motor_006`, los `evaluated_record_ids`, `rule_version` y `version_hash`.
- EntityCluster: `entity_cluster_id` es la clave estable canonica del cluster; no sustituye a `canonical_entity_id` de `motor_003` y solo identifica el cluster producido por este motor.
- ResolutionConflict: `conflict_id` es la clave estable canonica del conflicto; debe permanecer estable para la misma combinacion de registros, tipo de conflicto y version de reglas.
- AmbiguityFlag: `ambiguity_flag_id` es la clave estable canonica de la bandera; se vincula de forma obligatoria con `identity_record_id`.
- CandidateMatch: `candidate_match_id` es la clave estable canonica de la comparacion; debe diferenciar `record_id`, `candidate_ref`, `candidate_type` y `rule_version`.
- Referencias externas: `record_id` identifica registros normalizados provenientes de `motor_005`; `canonical_entity_id` identifica entidades canonicas provenientes de `motor_003`.

## versioning
- version_id: string (required) — identificador de version del objeto emitido. Debe cambiar cuando cambian campos materiales del objeto.
- created_at: datetime (required) — timestamp ISO-8601 de creacion de la version inicial del objeto.
- updated_at: datetime (required) — timestamp ISO-8601 de la ultima actualizacion controlada de la version del objeto.
- version_hash: string (required) — hash determinista del contenido versionado, excluyendo solo metadatos no materiales si la implementacion lo documenta explicitamente.
- rule_version: string (required on IdentityRecord and CandidateMatch) — version de la politica determinista aplicada; forma parte del contenido versionado.
- Versioning scope: cada `IdentityRecord`, `EntityCluster`, `ResolutionConflict`, `AmbiguityFlag` y `CandidateMatch` porta sus propios campos de versionado. No se permite actualizar un objeto previo en silencio; una correccion debe crear nueva version y conservar `parent_id`.

## lineage
- source_ref: string (required) — referencia a la fuente o conjunto de fuentes de los `NormalizedRecord` evaluados. Para objetos agregados debe preservar todas las fuentes relevantes mediante referencia agregada o lista serializada controlada.
- produced_by_motor: string (required) — identificador del motor productor; para este schema el valor permitido es `motor_006`.
- produced_at: datetime (required) — timestamp ISO-8601 de emision del objeto por el motor.
- parent_id: string | null (optional) — identificador del objeto previo del mismo tipo cuando existe correccion, reemplazo o refinamiento versionado.
- lineage_refs: array<string> (required where decisions or clusters are emitted) — referencias a lineage heredado de registros normalizados, entidades canonicas, comparaciones candidatas y decisiones usadas como soporte.
- evidence_refs: array<string> (required where decisions, ambiguity, conflicts or matches are emitted) — referencias reconstruibles a evidencia normalizada y comparaciones intermedias; no puede depender de estado implicito.
- Provenance rule: ningun output de `motor_006` puede eliminar `record_id`, `source_ref`, `provenance_ref` heredado o lineage necesario para reconstruir la decision.
