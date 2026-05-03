# Test Spec — Library Curation Engine

Motor ID: motor_011

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
why_it_exists:  Evita que cada fase arme su propia pseudo-biblioteca local.
key_inputs:     quality_records (motor_007), identity_records (motor_006), dedup_records (motor_010)
key_outputs:    library_object, curated_bundle, library_version
key_objects:    LibraryObject, CuratedBundle, LibraryVersion
what_not_to_do: No ingesta datos nuevos. No evalúa calidad. Solo selecciona y organiza objetos aptos como biblioteca.
design_notes:   Requiere el pipeline completo de Fase 1.

All test sections below have concrete content aligned with the closed contract.
-->

## happy_path
Input mínimo válido:
- `quality_records` contiene un registro `qr-lib-001` con `subject_ref = obj-001`, `evaluation_status = pass`, `fitness_score.total_score = 0.92`, `quality_flags = []`, `phase_contract_ref = pc-phase1` y `evaluation_run_id = qrun-001`.
- `identity_records` contiene `ir-lib-001` con `evaluated_record_ids = [obj-001]`, `decision = same_entity`, `confidence_band = high`, `evidence_refs = [ev-id-001]`, `rule_version = idrule-1.0.0` y `lineage_refs = [lin-id-001]`.
- `dedup_records` contiene una decisión no bloqueante `dd-lib-001` para `candidate_ref = obj-001`, `recommendation = retain`, `cluster_ref = dc-lib-001`, `member_refs = [obj-001, obj-009]`, `method_version = dedup-1.0.0` y `rationale_refs = [rat-dedup-001]`.
- `curation_policy` contiene `curation_run_id = cur-run-001`, `curation_rule_version = libcur-1.0.0`, `bundle_scope = phase_1_context_library`, `accepted_quality_statuses = [pass, conditional_pass]`, `blocking_flag_codes = [missing_lineage, missing_provenance, not_fit_for_phase]`, `duplicate_policy = retain_representative` y `published_at = 2026-04-17T10:00:00Z`.

Comportamiento esperado:
- El motor emite un `LibraryObject` para `obj-001` con `source_object_ref = obj-001`, `quality_record_ref = qr-lib-001`, `identity_record_ref = ir-lib-001`, `dedup_evidence_refs = [dd-lib-001]`, `curation_status = included`, `curation_rule_version = libcur-1.0.0`, `bundle_scope = phase_1_context_library`, `produced_by_motor = motor_011`, `provenance_refs` y `lineage_refs` no vacios.
- El motor emite un `CuratedBundle` con `bundle_scope = phase_1_context_library`, `member_library_object_refs` con el `library_object_id` emitido, `excluded_candidate_refs = []`, `rejection_refs = []`, `selection_rule_version = libcur-1.0.0` y `membership_fingerprint` deterministico no vacio.
- El motor emite `LibraryVersion` para el objeto y para el bundle, con `versioned_object_ref` resolviendo al output correspondiente, `versioned_object_type` correcto, `curation_rule_version = libcur-1.0.0`, `content_fingerprint` no vacio, `prior_version_ref = null`, `produced_by_motor = motor_011` y `lineage_refs` no vacios.

## sparse_case
Input con campos opcionales ausentes:
- Mismos registros base del happy path, pero `quality_records[0].disqualification_reason` no existe, `identity_records[0].entity_cluster_ref` no existe, no hay `rebuild_manifest_ref`, no hay `parent_id` previo y `warning_refs` no se suministra porque no hay advertencias.
- `dedup_records = []`, lo que significa que no existe recomendacion de supresion ni cluster aplicable para `obj-001`.
- La politica declara los campos obligatorios `curation_run_id`, `curation_rule_version` y `bundle_scope`, pero omite valores opcionales de publicacion previa.

Comportamiento esperado:
- El motor no falla por ausencia de campos opcionales o por lista de deduplicacion vacia.
- El `LibraryObject` se emite con `dedup_evidence_refs = []`, `warning_refs = []`, `rejection_reason_ref = null`, `parent_id = null` y `curation_status = included`.
- El `CuratedBundle` se emite con un solo miembro, `excluded_candidate_refs = []`, `rejection_refs = []`, `parent_id = null` y huellas deterministicas calculadas desde los identificadores disponibles.
- Los `LibraryVersion` emitidos usan `prior_version_ref = null` y `rebuild_manifest_ref = null`, sin inventar versiones previas ni completar silenciosamente metadatos inexistentes.

## malformed_input
Input invalido:
- `quality_records` contiene `qr-bad-001` con `subject_ref = obj-bad-001`, pero `fitness_score = "0.91"` en vez de un objeto/numero estructurado aceptado por el contrato, o falta `evaluation_run_id`.
- `identity_records` contiene `ir-bad-001` con `evaluated_record_ids = [obj-bad-001]`, pero `evidence_refs = "ev-id-001"` en vez de `list[string]`.
- `curation_policy` omite `curation_rule_version` o lo entrega como cadena vacia.

Comportamiento esperado:
- El motor rechaza el run antes de emitir `LibraryObject`, `CuratedBundle` o `LibraryVersion` parciales.
- El error estructurado identifica el contrato incumplido como `CURATION_POLICY_BLOCKED` cuando falta `curation_policy.curation_rule_version`.
- Si la politica es valida pero el candidato carece de campos obligatorios de calidad, el candidato se rechaza con `CURATION_QUALITY_REF_MISSING` cuando no puede resolverse un `quality_record_ref` valido o con `CURATION_QUALITY_NOT_ELIGIBLE` cuando el registro existe pero no cumple la elegibilidad declarada.
- Si la politica y calidad son validas pero la identidad tiene tipos invalidos o evidencia incompleta, el candidato se rechaza con `CURATION_IDENTITY_REF_MISSING` y no se promueve a biblioteca.

## edge_cases
- Conjunto elegible vacio: `quality_records`, `identity_records` y `dedup_records` son sintacticamente validos, pero todos los candidatos tienen `evaluation_status = rejected`, `evaluation_status = disqualified`, un flag incluido en `blocking_flag_codes` o identidad ambigua bloqueante. El motor emite cero `LibraryObject`, emite `CurationRejection` por cada candidato excluido, emite un `CuratedBundle` valido para `bundle_scope` con `member_library_object_refs = []`, preserva `excluded_candidate_refs` y emite una `LibraryVersion` del bundle vacio.
- Supresion por duplicado: dos candidatos validos `obj-010` y `obj-011` pertenecen a `dc-lib-010`, y `dedup_records` recomienda `retain_representative = obj-010` y `suppress_duplicate = obj-011`. El motor incluye solo el `LibraryObject` de `obj-010` en `member_library_object_refs`, registra `obj-011` en `excluded_candidate_refs`, crea una `CurationRejection` con `error_code = CURATION_DEDUP_REF_INVALID` solo si la evidencia de cluster es inconsistente, y si la evidencia es consistente usa un rechazo/exclusion trazable por duplicado sin mutar los registros upstream.
- Inclusion con advertencia permitida: un candidato tiene `evaluation_status = conditional_pass` y `quality_flags = [restricted_use]`, donde `restricted_use` no esta en `blocking_flag_codes`. El motor emite `LibraryObject.curation_status = included_with_warning`, copia la referencia de advertencia a `warning_refs`, conserva la membresia en el bundle y no recalcula el score de calidad.
- Orden de entrada no deterministico: los mismos candidatos validos llegan en orden distinto en `quality_records`, `identity_records` y `dedup_records`. El motor produce el mismo conjunto ordenado de `member_library_object_refs`, el mismo `membership_fingerprint` y los mismos `version_hash` para contenidos equivalentes.

## pass_criteria
Un test pasa cuando todas estas condiciones observables se cumplen:
- Cada candidato elegible genera exactamente un `LibraryObject` con `library_object_id`, `source_object_ref`, `quality_record_ref`, `identity_record_ref`, `curation_status`, `curation_rule_version`, `provenance_refs`, `lineage_refs`, `version_id`, `version_hash` y `produced_by_motor = motor_011` no vacios.
- Cada candidato rechazado o excluido aparece en `CurationRejection` o en `CuratedBundle.excluded_candidate_refs` con evidencia suficiente para auditar la decision y sin borrar ni modificar registros de calidad, identidad o deduplicacion.
- Cada `CuratedBundle.member_library_object_refs` resuelve a `LibraryObject.library_object_id` emitidos en el mismo `curation_run_id` y `bundle_scope`.
- Cada `LibraryVersion.versioned_object_ref` resuelve al objeto o bundle versionado, tiene `versioned_object_type` correcto, `content_fingerprint` y `version_hash` no vacios, y preserva `prior_version_ref` o `parent_id` cuando existe version previa.
- Ejecutar el mismo input dos veces produce identificadores, membresia, fingerprints y hashes equivalentes salvo campos de tiempo permitidos por el contrato de emision.

## fail_criteria
Un test falla cuando se observa cualquiera de estas condiciones:
- Se emite un `LibraryObject` para un candidato sin `quality_record_ref`, sin `identity_record_ref`, con evidencia de deduplicacion invalida, con `evaluation_status` no aceptado por la politica o con un flag bloqueante.
- Se emite un bundle cuyo `member_library_object_refs` contiene referencias inexistentes, duplicadas, pertenecientes a otro `bundle_scope` o no reproducibles bajo reordenamiento de input.
- Se pierde o inventa trazabilidad: `provenance_refs`, `lineage_refs`, `source_ref`, `produced_by_motor`, `produced_at`, `parent_id`, `version_id` o `version_hash` faltan en outputs que los requieren.
- El motor corrige silenciosamente tipos invalidos, rellena campos obligatorios con valores fabricados, recalcula calidad, resuelve identidad o modifica decisiones de deduplicacion en vez de rechazar o preservar referencias upstream.
- Un rechazo esperado no produce codigo/error estructurado auditable, o el run invalido deja outputs parciales persistidos.
