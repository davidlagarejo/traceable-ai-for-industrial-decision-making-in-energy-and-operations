# Test Spec — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.

Contenido completado para gate de tests.
-->

## happy_path
Input minimo valido:
- `normalized_records` contiene dos registros:
  - `rec_101`: `entity_type = organization`, `normalized_fields.legal_name = "ACME HEALTH"`, `normalized_fields.org_tax_id = "98-7654321"`, `source_ref = "source_registry_a"`, `provenance_ref = "prov_rec_101"`, `lineage_refs = ["lin_rec_101"]`.
  - `rec_102`: `entity_type = organization`, `normalized_fields.legal_name = "ACME HEALTH"`, `normalized_fields.org_tax_id = "98-7654321"`, `source_ref = "source_registry_b"`, `provenance_ref = "prov_rec_102"`, `lineage_refs = ["lin_rec_102"]`.
- `canonical_entities` contiene `can_org_44` con `entity_type = organization`, `taxonomy_version_id = "taxonomy-2026-01"`, `aliases = ["ACME HEALTH"]` y `external_identifiers.org_tax_id = "98-7654321"`.
- `resolution_policy.rule_version = "identity-policy-1.0.0"` y la regla determinista considera match fuerte cuando `entity_type`, alias normalizado e identificador externo coinciden.

Expected output:
- Se emite un `identity_resolution_record` con `produced_by_motor = "motor_006"`, `decision = "same_entity"`, `confidence_band = "high"`, `evaluated_record_ids = ["rec_101", "rec_102"]`, `rule_version = "identity-policy-1.0.0"`, `evidence_refs` apuntando a las comparaciones de alias e identificador, y `lineage_refs` que conservan `lin_rec_101` y `lin_rec_102`.
- Se emite un `entity_cluster` con `canonical_entity_id = "can_org_44"`, `member_record_ids = ["rec_101", "rec_102"]`, `cluster_status = "confirmed"`, `identity_record_ids` apuntando al `identity_resolution_record` emitido y `produced_by_motor = "motor_006"`.
- `ambiguity_flag` es `null` o no se emite para esta decision.
- No se modifica ningun `normalized_record` ni `canonical_entity` de entrada.

## sparse_case
Input valido con campos opcionales ausentes:
- `normalized_records` contiene un unico registro `rec_150` con `entity_type = person`, `normalized_fields.full_name = "MARTA RIOS"`, `normalized_fields.national_researcher_id = "NR-8821"`, `source_ref = "source_research_roster"`, `provenance_ref = "prov_rec_150"` y `lineage_refs = ["lin_rec_150"]`.
- `rec_150` no incluye campos opcionales como direccion, afiliacion secundaria, aliases historicos ni `previous_identity_record_id`.
- `canonical_entities` contiene `can_person_07` con `entity_type = person`, `taxonomy_version_id = "taxonomy-2026-01"`, `aliases = ["MARTA RIOS"]` y `external_identifiers.national_researcher_id = "NR-8821"`.
- `previous_identity_records` esta ausente o es `[]`.
- `resolution_policy.rule_version = "identity-policy-1.0.0"`.

Expected output:
- El motor no falla por la ausencia de campos opcionales.
- Se emite un `identity_resolution_record` para `rec_150` con `decision = "same_entity"`, `confidence_band = "high"`, `evaluated_record_ids = ["rec_150"]`, `evidence_refs` no vacio, `rule_version = "identity-policy-1.0.0"` y `lineage_refs = ["lin_rec_150"]`.
- Se emite un `entity_cluster` con `canonical_entity_id = "can_person_07"`, `member_record_ids = ["rec_150"]` y `cluster_status = "confirmed"`.
- No se infieren ni se rellenan silenciosamente los campos opcionales ausentes.

## malformed_input
Casos de rechazo obligatorio:
- Si cualquier item de `normalized_records` omite `record_id`, el motor rechaza el lote con `ERR_NORMALIZED_RECORD_INVALID` y no emite `identity_resolution_record`.
- Si cualquier item de `normalized_records` omite `source_ref` o `provenance_ref`, el motor rechaza el lote con `ERR_MISSING_PROVENANCE` y no produce clusters parciales.
- Si un registro trae texto crudo en `raw_fields` pero no trae estructura `normalized_fields`, el motor rechaza con `ERR_UNNORMALIZED_INPUT`.
- Si `normalized_records` no es un array, por ejemplo un objeto unico `{ "record_id": "rec_bad" }`, el motor rechaza con `ERR_INPUT_TYPE_INVALID`.
- Si un item de `canonical_entities` omite `canonical_entity_id`, `entity_type` o `taxonomy_version_id`, el motor rechaza con `ERR_CANONICAL_ENTITY_INVALID`.
- Si `resolution_policy.rule_version` falta, esta vacio o no puede adjuntarse a cada decision emitida, el motor rechaza con `ERR_POLICY_VERSION_MISSING`.

Expected behavior:
- El rechazo es estructurado, determinista y trazable.
- No se emiten `entity_cluster`, `ambiguity_flag` ni `resolution_conflict` como sustituto de una validacion de contrato fallida.
- No se corrige silenciosamente ningun campo malformado.

## edge_cases
- Same normalized name with incompatible identifiers: `rec_201` y `rec_202` tienen `entity_type = organization` y `normalized_fields.legal_name = "NOVA LABS"`, pero `org_tax_id` difiere entre `"11-1111111"` y `"22-2222222"`. Correct behavior: emitir `identity_resolution_record.decision = "distinct_entity"`, `confidence_band` al menos `medium`, `evidence_refs` hacia los identificadores incompatibles y ningun `entity_cluster` confirmado que los una.
- Candidate tie: `rec_401` tiene `entity_type = person`, alias normalizado compatible con `can_person_10` y `can_person_18`, y no contiene identificador fuerte que rompa el empate bajo `resolution_policy.rule_version = "identity-policy-1.0.0"`. Correct behavior: emitir `identity_resolution_record.decision = "ambiguous"`, `confidence_band = "unresolved"`, `ambiguity_flag.ambiguity_reason = "candidate_tie"`, `ambiguity_flag.severity = "blocking"` y conservar `rec_401` en `affected_record_ids`.
- Missing canonical reference: `rec_301` tiene `record_id`, `source_ref`, `provenance_ref`, `lineage_refs` y `normalized_fields` completos, pero no existe `canonical_entity` compatible. Correct behavior: emitir `decision = "ambiguous"`, `ambiguity_reason = "missing_canonical_reference"` y no crear una nueva entidad canonica global.
- Taxonomy mismatch: `rec_501` declara `entity_type = organization` y el unico candidato `can_person_501` declara `entity_type = person` aunque comparta alias textual. Correct behavior: bloquear el merge, emitir `ResolutionConflict.conflict_type = "taxonomy_mismatch"` o una decision `distinct_entity` sustentada por evidencia taxonomica, y nunca emitir `same_entity`.

## pass_criteria
Un test pasa cuando todas estas condiciones observables se cumplen:
- Los inputs validos producen objetos del contrato esperado: `identity_resolution_record` y, cuando aplica, `entity_cluster`, `ambiguity_flag` o `resolution_conflict`.
- Cada `identity_resolution_record` incluye `identity_record_id`, `evaluated_record_ids`, `decision`, `confidence_band`, `evidence_refs`, `rule_version`, `lineage_refs`, `version_id`, `version_hash`, `source_ref`, `produced_by_motor = "motor_006"` y `produced_at`.
- Cada `entity_cluster` emitido incluye `entity_cluster_id`, `member_record_ids`, `cluster_status`, `identity_record_ids`, `lineage_refs`, versionado, `source_ref`, `produced_by_motor = "motor_006"` y `produced_at`.
- Cada caso ambiguo produce `identity_resolution_record.decision = "ambiguous"` y un `ambiguity_flag` con `ambiguity_reason`, `severity`, `affected_record_ids` y `evidence_refs`.
- Los casos invalidos se rechazan con el codigo de error especificado y sin outputs parciales de identidad.
- Los `record_id`, `source_ref`, `provenance_ref`, `lineage_refs` y `rule_version` necesarios para reconstruir la decision permanecen presentes en las salidas o referencias de evidencia.
- Ningun test exige deduplicacion documental, normalizacion de texto crudo ni creacion de entidades canonicas nuevas.

## fail_criteria
Un test falla si se observa cualquiera de estas condiciones:
- Un input valido produce excepcion fatal, output vacio o un objeto sin los campos requeridos por el schema tecnico.
- Un caso `same_entity` confirmado no conserva todos los `evaluated_record_ids`, no adjunta `rule_version` o carece de `evidence_refs` reconstruibles.
- Un caso ambiguo se fuerza a `same_entity` o `distinct_entity` sin emitir `ambiguity_flag`.
- Un caso con identificadores incompatibles produce un `entity_cluster.cluster_status = "confirmed"` que une registros que deben permanecer separados.
- Un input malformado es aceptado, corregido en silencio o produce outputs parciales en lugar del codigo de error esperado.
- Se pierde `source_ref`, `provenance_ref`, `lineage_refs` o `produced_by_motor = "motor_006"` en cualquier output emitido.
- El motor modifica registros normalizados de entrada, modifica entidades canonicas de `motor_003`, crea una entidad canonica global nueva o ejecuta deduplicacion documental propia de `motor_010`.
