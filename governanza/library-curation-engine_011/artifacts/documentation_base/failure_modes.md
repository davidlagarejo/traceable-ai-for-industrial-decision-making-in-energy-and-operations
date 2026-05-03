# Failure Modes — Library Curation Engine

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

## failure_modes_list
- `QUALITY_GATE_BYPASS`: objects with `evaluation_status = disqualified`, `rejected` or blocking quality flags appear inside a `CuratedBundle`.
- `IDENTITY_AMBIGUITY_PROMOTION`: a candidate with unresolved or blocking identity ambiguity is emitted as a normal `LibraryObject` without preserving the ambiguity reference.
- `DUPLICATE_COLLAPSE_WITHOUT_TRACE`: duplicate candidates disappear from bundle membership without `excluded_candidate_refs`, cluster evidence or rationale references.
- `LINEAGE_LOSS`: emitted library objects or versions lack provenance, lineage or upstream evidence references needed to rebuild the library.
- `NON_DETERMINISTIC_MEMBERSHIP`: repeated runs over the same valid inputs and policy produce different bundle membership or content fingerprints.
- `LOCAL_PSEUDO_LIBRARY_DRIFT`: downstream phases begin assembling their own curation lists because the engine output is incomplete, unstable or too vague to reuse.

## anti_patterns
- Treating library curation as a second quality evaluator by recalculating scores or overriding quality flags locally.
- Treating deduplication recommendations as permission to delete or rewrite upstream objects instead of preserving non-destructive exclusion metadata.
- Building separate per-phase library spreadsheets outside this engine and then importing them as if they were governed library versions.
- Allowing manual bundle edits without a new `LibraryVersion`, content fingerprint and curation rule reference.
- Using language-model preference or analyst convenience as the deciding authority for library eligibility.

## degradation_signals
- Increase in `LibraryObject` records with empty `quality_record_ref`, `identity_record_ref`, `provenance_refs` or `lineage_refs`.
- Rising share of bundle members with `curation_status = included_with_warning` without matching policy changes or governance review.
- Repeated changes in bundle membership fingerprint when upstream inputs and `curation_rule_version` have not changed.
- High count of excluded candidates without structured rejection codes.
- Downstream motors requesting raw quality, identity or duplicate inputs because `library_object` metadata is insufficient.
- Multiple library versions created with identical content fingerprint but different unstated selection rationale.
- Duplicate clusters represented by multiple included members when policy requires one representative.
