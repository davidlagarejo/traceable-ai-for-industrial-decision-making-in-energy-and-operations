# Operational Rules — Library Curation Engine

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

## rules
1. Every curation run must declare a non-empty `curation_run_id`, `bundle_scope`, `curation_rule_version` and deterministic duplicate handling policy before candidates are evaluated.
2. A candidate can become a `LibraryObject` only when it has matching quality, identity and duplicate-control evidence from the required upstream motors.
3. A candidate with `evaluation_status = disqualified` or `evaluation_status = rejected` must never be included in a `CuratedBundle`.
4. A candidate with `conditional_pass` quality can be included only when the active policy explicitly allows each warning flag carried by that candidate.
5. A candidate with unresolved or blocking identity ambiguity must be rejected for default library use; the motor must preserve the ambiguity reference instead of closing it.
6. Duplicate recommendations must be applied non-destructively: the selected representative may be included, suppressed candidates must remain referenced as excluded candidates, and no upstream record may be deleted or merged.
7. Bundle membership must be deterministic and stable under input reordering by using stable identifiers, rule version and content fingerprints.
8. Any change in eligible membership, duplicate handling, curation policy or upstream evidence must produce a new `LibraryVersion` rather than mutating an existing version.
9. Every emitted object must preserve provenance, lineage, upstream evidence references and rule version sufficient for rebuild and audit.

## invariants
- Inputs from `motor_006`, `motor_007` and `motor_010` are read-only for the full operation.
- No `LibraryObject` exists without `quality_record_ref`, `identity_record_ref`, `curation_rule_version`, `provenance_refs` and `lineage_refs`.
- No `CuratedBundle` member exists without a corresponding emitted `LibraryObject`.
- `excluded_candidate_refs` never means deleted input; it means candidate not promoted to bundle membership under an explicit reason.
- `LibraryVersion` records are immutable after emission; later changes create a new version with a prior version reference.
- The same valid inputs and same curation policy produce the same library objects, bundle membership and fingerprints.
- Duplicate, identity and quality evidence are preserved as references, not recomputed inside this motor.

## forbidden_operations
- Ingesting new data, scraping sources, parsing files or refreshing source availability.
- Normalizing fields, creating canonical entities, changing taxonomies or repairing upstream records.
- Evaluating quality, recalculating fitness scores, suppressing quality flags or overriding disqualification reasons.
- Resolving entity identity, closing ambiguity or changing entity cluster membership.
- Detecting duplicates, calculating similarity scores or rewriting deduplication recommendations.
- Deleting, merging, overwriting, enriching or silently mutating upstream records.
- Producing analytic claims, inference records, validation evidence, report packages or phase approvals.
- Using opaque language-model judgment as the authority for library eligibility.
