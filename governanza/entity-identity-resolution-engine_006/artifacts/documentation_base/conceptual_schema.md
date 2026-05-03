# Conceptual Schema — Entity Identity / Resolution Engine

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

## entities
- IdentityRecord: decision auditable que indica si registros evaluados representan la misma entidad, entidades distintas o una identidad ambigua.
- EntityCluster: conjunto trazable de registros normalizados asociados a una entidad candidata o confirmada.
- ResolutionConflict: diagnostico de incompatibilidad cuando la evidencia o las reglas producen decisiones contradictorias.
- AmbiguityFlag: senal estructurada que preserva un caso abierto sin forzar resolucion.
- CandidateMatch: comparacion intermedia entre un registro normalizado y una entidad canonica o cluster existente.

## relationships
- NormalizedRecord -> CandidateMatch (1:n; un registro puede compararse contra varias entidades canonicas o clusters candidatos).
- CanonicalEntity -> CandidateMatch (1:n; una entidad canonica puede ser candidata para muchos registros normalizados).
- CandidateMatch -> IdentityRecord (n:1; una o mas comparaciones sustentan una decision de resolucion).
- IdentityRecord -> EntityCluster (n:1; varias decisiones compatibles pueden consolidarse en un cluster de entidad).
- IdentityRecord -> AmbiguityFlag (1:0..1; toda decision no cerrada debe emitir una bandera de ambigüedad).
- ResolutionConflict -> IdentityRecord (1:n; un conflicto referencia las decisiones o candidatos incompatibles que lo originan).

## key_fields
IdentityRecord:
- identity_record_id: string
- evaluated_record_ids: array<string>
- decision: enum<same_entity, distinct_entity, ambiguous>
- confidence_band: enum<high, medium, low, unresolved>
- evidence_refs: array<string>
- rule_version: string

EntityCluster:
- entity_cluster_id: string
- canonical_entity_id: string | null
- member_record_ids: array<string>
- cluster_status: enum<confirmed, provisional, ambiguous>
- lineage_refs: array<string>

ResolutionConflict:
- conflict_id: string
- involved_record_ids: array<string>
- conflict_type: enum<identifier_collision, taxonomy_mismatch, evidence_tie, provenance_conflict>
- blocking_reason: string
- recommended_next_step: enum<manual_review, await_more_evidence, split_cluster>

AmbiguityFlag:
- ambiguity_flag_id: string
- identity_record_id: string
- ambiguity_reason: enum<insufficient_evidence, contradictory_evidence, candidate_tie, missing_canonical_reference>
- severity: enum<warning, blocking>
- created_at: string

CandidateMatch:
- candidate_match_id: string
- record_id: string
- candidate_ref: string
- match_features: object
- match_result: enum<pass, fail, tie, insufficient>
