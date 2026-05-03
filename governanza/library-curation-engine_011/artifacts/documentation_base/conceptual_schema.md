# Conceptual Schema — Library Curation Engine

Motor ID: motor_011

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
why_it_exists:  Evita que cada fase arme su propia pseudo-biblioteca local.
key_inputs:     quality_records (motor_007), identity_records (motor_006), dedup_records (motor_010)
key_outputs:    library_object, curated_bundle, library_version
key_objects:    LibraryObject, CuratedBundle, LibraryVersion
what_not_to_do: No ingesta datos nuevos. No evalúa calidad. Solo selecciona y organiza objetos aptos como biblioteca.
design_notes:   Requiere el pipeline completo de Fase 1.

All open placeholders in this file have been resolved with concrete documentation.
-->

## entities
- `LibraryObject`: reusable framework object promoted from an upstream structured object after quality, identity and duplicate-control evidence has been validated.
- `CuratedBundle`: scoped collection of `LibraryObject` references assembled for reuse by a phase, domain, facility class or downstream motor.
- `LibraryVersion`: immutable version descriptor for a `LibraryObject` or `CuratedBundle`, including fingerprint, prior version and rebuild references.

## relationships
- `QualityRecord` -> `LibraryObject` (a candidate can become a library object only when quality evidence satisfies the active curation policy).
- `IdentityRecord` -> `LibraryObject` (each library object keeps identity evidence and cannot invent or close identity decisions).
- `DuplicateCluster` -> `LibraryObject` (duplicate evidence determines whether a candidate is retained, represented by another object or excluded from bundle membership).
- `LibraryObject` -> `CuratedBundle` (a bundle contains zero or more library object references selected for the same declared scope).
- `CuratedBundle` -> `LibraryVersion` (each published bundle version records its membership fingerprint and prior bundle version when one exists).
- `LibraryObject` -> `LibraryVersion` (each published library object version records the exact upstream references, rule version and content fingerprint used to create it).
- `LibraryVersion` -> `LibraryVersion` (a version may reference one prior version to represent supersession, rebuild or rule-version change).

## key_fields
`LibraryObject`
- `library_object_id`: string
- `source_object_ref`: string
- `quality_record_ref`: string
- `identity_record_ref`: string
- `dedup_evidence_refs`: list[string]
- `curation_status`: enum[`included`, `included_with_warning`, `excluded_duplicate`, `rejected`]
- `curation_rule_version`: string
- `provenance_refs`: list[string]
- `lineage_refs`: list[string]

`CuratedBundle`
- `curated_bundle_id`: string
- `bundle_scope`: string
- `member_library_object_refs`: list[string]
- `excluded_candidate_refs`: list[string]
- `selection_rule_version`: string
- `created_at`: datetime
- `lineage_refs`: list[string]

`LibraryVersion`
- `library_version_id`: string
- `versioned_object_ref`: string
- `versioned_object_type`: enum[`library_object`, `curated_bundle`]
- `content_fingerprint`: string
- `prior_version_ref`: string | null
- `curation_rule_version`: string
- `created_at`: datetime
- `rebuild_manifest_ref`: string | null
