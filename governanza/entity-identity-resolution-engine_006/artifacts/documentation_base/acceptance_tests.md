# Acceptance Tests — Entity Identity / Resolution Engine

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

## happy_path
Input: `normalized_records` contiene `rec_101` y `rec_102`, ambos con `entity_type = organization`, nombre normalizado `ACME HEALTH`, mismo identificador externo `org_tax_id = 98-7654321`, `source_ref` distinto y `provenance_ref` valido. `canonical_entities` contiene `can_org_44` con alias `ACME HEALTH` y el mismo identificador externo.

Action: el motor evalua ambos registros contra `can_org_44`, aplica la `resolution_policy` version `identity-policy-1.0.0` y registra las features coincidentes.

Expected output: se emite un `identity_resolution_record` con `decision = same_entity`, `confidence_band = high`, `evaluated_record_ids = ["rec_101", "rec_102"]`, `evidence_refs` hacia los campos de identificador y alias, y `rule_version = identity-policy-1.0.0`. Tambien se emite un `entity_cluster` con `canonical_entity_id = can_org_44`, `member_record_ids = ["rec_101", "rec_102"]` y `cluster_status = confirmed`. No se emite `ambiguity_flag`.

## edge_cases
- Same name, different identifiers: `rec_201` y `rec_202` tienen nombre normalizado `NOVA LABS` pero identificadores externos incompatibles. Correct behavior: emitir `identity_resolution_record` con `decision = distinct_entity`, conservar ambos `record_id` y registrar evidencia de separacion.
- Missing canonical candidate: `rec_301` tiene provenance valido y campos normalizados completos, pero no existe `canonical_entity` compatible. Correct behavior: emitir `decision = ambiguous`, `ambiguity_reason = missing_canonical_reference` y no crear una entidad canonica nueva.
- Candidate tie: `rec_401` coincide por alias con `can_person_10` y `can_person_18`, sin identificador fuerte que rompa empate. Correct behavior: emitir `ambiguity_flag` con `ambiguity_reason = candidate_tie` y `severity = blocking`.
- Sparse but valid input: un unico registro con `record_id`, `source_ref`, `provenance_ref`, tipo de entidad y un identificador fuerte coincide con una entidad canonica. Correct behavior: permitir resolucion contra esa entidad si la regla determinista alcanza umbral.

## rejection_criteria
- Reject with `ERR_MISSING_PROVENANCE` when any `normalized_record` lacks `source_ref` or `provenance_ref`.
- Reject with `ERR_UNNORMALIZED_INPUT` when the input contains raw extraction fields but no `normalized_fields` structure.
- Reject with `ERR_CANONICAL_ENTITY_INVALID` when a canonical entity lacks `canonical_entity_id` or `entity_type`.
- Reject with `ERR_POLICY_VERSION_MISSING` when `resolution_policy.rule_version` is absent, empty or not attached to the emitted decision.
