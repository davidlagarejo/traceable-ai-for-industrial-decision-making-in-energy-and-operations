# Technical Schema — Taxonomy + Canonical Entity Service

Motor ID: motor_003

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Gobernar taxonomías, términos canónicos, aliases y límites semánticos del sistema.
why_it_exists:  Evita drift semántico, dialectos paralelos y joins inestables entre fuentes.
key_inputs:     raw terms, aliases, source vocabularies
key_outputs:    canonical_term, alias_map, taxonomy_tree, boundary_definition
key_objects:    CanonicalEntity, TaxonomyNode, AliasMappings
what_not_to_do: No normaliza datos. No resuelve identidad de registros. Solo gobierna el vocabulario.
design_notes:   Depende de motor_001. Es la referencia semántica que todos los motores downstream consultan.
-->

## entities
- SourceVocabularyManifest: input DTO that declares an external or internal vocabulary source, its version, authority note and term reference before candidates are evaluated. Lives in `schema_technical` as the source input shape and in `implementation` as a validation DTO; it is not a published canonical vocabulary object by itself.
- RawTermCandidate: input DTO for a proposed canonical vocabulary term. It carries source text, taxonomy scope and provenance before deterministic validation. Lives in `schema_technical` as the candidate input shape and in `implementation` as a request DTO that can produce either a CanonicalEntity or a TaxonomyValidationError.
- AliasCandidate: input DTO for a proposed alias pointing to an existing or same-request canonical target. Lives in `schema_technical` as the alias input shape and in `implementation` as a request DTO that can produce either an AliasMappings record or a TaxonomyValidationError.
- CanonicalEntity: persisted canonical term authorized inside one `taxonomy_id` and `scope`. It stores the stable concept identifier, canonical label, status, phase contract reference, boundary attachment and provenance metadata. Lives in `schema_technical` as the canonical persistent entity and in `implementation` as the registry row consumed by downstream motors.
- TaxonomyNode: persisted acyclic tree placement for a CanonicalEntity within one taxonomy. It stores parent linkage, path and ordering without changing the CanonicalEntity identity. Lives in `schema_technical` as the taxonomy graph node contract and in `implementation` as the node table or in-memory node model.
- AliasMappings: persisted alias-to-canonical mapping. Each record maps one accepted alias string to exactly one active CanonicalEntity within one `taxonomy_id` and `scope`; an `alias_map` output may contain many AliasMappings records. Lives in `schema_technical` as the alias mapping contract and in `implementation` as the mapping table or lookup model.
- BoundaryDefinition: persisted semantic boundary attached to one CanonicalEntity. It declares inclusion rules, exclusion rules and scope notes required before a canonical term is exposed downstream. Lives in `schema_technical` as the boundary contract and in `implementation` as the boundary registry row.
- TaxonomyValidationError: immutable rejection signal emitted when a term, alias, taxonomy node or boundary proposal violates contract, provenance, uniqueness or acyclicity rules. Lives in `schema_technical` as the structured error output and in `implementation` as the blocking validation result.

## fields
SourceVocabularyManifest:
- source_vocab_id: string (required) — stable source vocabulary identifier supplied by the submitter or governance registry.
- source_name: string (required) — human-readable source vocabulary name.
- vocabulary_version: string (required) — declared version of the source vocabulary.
- terms_ref: string (required) — reference to the source term list or governed vocabulary extract.
- authority_note: string (required) — source authority statement or governance note explaining why the vocabulary may be considered.
- source_ref: string (required) — document, registry entry or source package reference for lineage.
- submitted_at: datetime (required) — timestamp when the manifest entered motor_003 validation.

RawTermCandidate:
- candidate_id: string (required) — stable request-local identifier for the proposed term.
- term_text: string (required) — source term text as submitted; the motor preserves it and does not rewrite it in place.
- source_vocab_id: string (required) — SourceVocabularyManifest identifier that supplied or authorized the candidate.
- taxonomy_id: string (required) — taxonomy where the term is proposed.
- scope: string (required) — semantic scope in which uniqueness and alias collision rules apply.
- parent_node_id: string|null (required) — proposed parent TaxonomyNode; null only for explicitly declared root candidates.
- boundary_include_rules: list[string] (required) — proposed inclusion rules for the BoundaryDefinition; may be empty only when exclusion rules or scope note are explicit.
- boundary_exclude_rules: list[string] (required) — proposed exclusion rules for the BoundaryDefinition; may be empty only when inclusion rules or scope note are explicit.
- boundary_scope_note: string (required) — explicit semantic boundary note for the candidate.
- provenance_ref: string (required) — source-level provenance reference for the submitted term.
- phase_contract_ref: string (required) — motor_001 phase contract reference authorizing taxonomy governance.

AliasCandidate:
- candidate_id: string (required) — stable request-local identifier for the proposed alias.
- alias_text: string (required) — source alias text as submitted; the motor preserves it and does not rewrite it in place.
- target_canonical_id: string|null (required) — existing CanonicalEntity target when the target already exists.
- target_term_text: string|null (required) — same-request target term text when `target_canonical_id` is not yet available.
- source_vocab_id: string (required) — SourceVocabularyManifest identifier that supplied or authorized the alias.
- taxonomy_id: string (required) — taxonomy where the alias is proposed.
- scope: string (required) — semantic scope in which alias uniqueness is enforced.
- provenance_ref: string (required) — source-level provenance reference for the submitted alias.
- phase_contract_ref: string (required) — motor_001 phase contract reference authorizing taxonomy governance.

CanonicalEntity:
- record_id: string (required) — immutable storage identifier for this persisted canonical entity version.
- canonical_id: string (required) — stable logical identifier for the canonical concept; never reused for a different concept.
- canonical_label: string (required) — authorized canonical label exposed to downstream motors.
- taxonomy_id: string (required) — taxonomy namespace that owns this canonical term.
- scope: string (required) — semantic scope for uniqueness, alias mapping and boundary enforcement.
- status: enum[proposed, active, deprecated, rejected] (required) — governed publication state of the canonical term.
- phase_contract_ref: string (required) — motor_001 phase contract reference authorizing this taxonomy governance output.
- boundary_id: string (required) — current BoundaryDefinition identifier required before active publication.
- provenance_refs: list[string] (required) — complete source provenance references supporting the term.
- version_id: string (required) — stable technical key for this immutable version.
- created_at: datetime (required) — timestamp when this version was first registered by motor_003.
- updated_at: datetime (required) — timestamp when registry metadata for this version was last updated.
- version_hash: string (required) — deterministic hash of normalized canonical entity content and immutable metadata.
- source_ref: string (required) — primary source vocabulary or governance record used to produce this version.
- produced_by_motor: string (required) — fixed value `motor_003`.
- produced_at: datetime (required) — timestamp when motor_003 emitted this version.
- parent_id: string|null (required) — previous CanonicalEntity `record_id` when this version supersedes another version; null for the first accepted version.

TaxonomyNode:
- record_id: string (required) — immutable storage identifier for this persisted taxonomy node version.
- node_id: string (required) — stable logical identifier for the node placement inside a taxonomy.
- taxonomy_id: string (required) — taxonomy namespace that owns the node.
- canonical_id: string (required) — CanonicalEntity represented by this node.
- parent_node_id: string|null (required) — parent TaxonomyNode in the same taxonomy; null only for explicit roots.
- path: list[string] (required) — ordered ancestor node identifiers from root to this node, including this `node_id`.
- sort_order: integer (required) — deterministic sibling order for stable tree traversal.
- status: enum[active, deprecated, rejected] (required) — governed publication state of this node placement.
- phase_contract_ref: string (required) — motor_001 phase contract reference authorizing this taxonomy governance output.
- version_id: string (required) — stable technical key for this immutable node version.
- created_at: datetime (required) — timestamp when this node version was first registered by motor_003.
- updated_at: datetime (required) — timestamp when registry metadata for this node version was last updated.
- version_hash: string (required) — deterministic hash of normalized node content and immutable metadata.
- source_ref: string (required) — source vocabulary, governance record or accepted term candidate that produced this node.
- produced_by_motor: string (required) — fixed value `motor_003`.
- produced_at: datetime (required) — timestamp when motor_003 emitted this node version.
- parent_id: string|null (required) — previous TaxonomyNode `record_id` when this version supersedes another version; null for the first accepted node version.

AliasMappings:
- record_id: string (required) — immutable storage identifier for this persisted alias mapping version.
- alias_id: string (required) — stable logical identifier for the alias within taxonomy and scope.
- alias_text: string (required) — accepted alias label exactly as governed for lookup.
- canonical_id: string (required) — target CanonicalEntity identifier.
- taxonomy_id: string (required) — taxonomy namespace in which the alias is valid.
- scope: string (required) — semantic scope in which the alias must be unique.
- source_vocab_id: string (required) — SourceVocabularyManifest identifier that supplied or authorized the alias.
- provenance_ref: string (required) — source-level provenance reference for the alias.
- status: enum[active, deprecated, rejected] (required) — governed publication state of this alias mapping.
- phase_contract_ref: string (required) — motor_001 phase contract reference authorizing this taxonomy governance output.
- version_id: string (required) — stable technical key for this immutable alias mapping version.
- created_at: datetime (required) — timestamp when this alias mapping version was first registered by motor_003.
- updated_at: datetime (required) — timestamp when registry metadata for this alias mapping version was last updated.
- version_hash: string (required) — deterministic hash of normalized alias mapping content and immutable metadata.
- source_ref: string (required) — primary source vocabulary or governance record used to produce this mapping.
- produced_by_motor: string (required) — fixed value `motor_003`.
- produced_at: datetime (required) — timestamp when motor_003 emitted this mapping version.
- parent_id: string|null (required) — previous AliasMappings `record_id` when this version supersedes another version; null for the first accepted mapping version.

BoundaryDefinition:
- record_id: string (required) — immutable storage identifier for this persisted boundary version.
- boundary_id: string (required) — stable logical identifier for the boundary definition.
- canonical_id: string (required) — CanonicalEntity governed by this boundary.
- taxonomy_id: string (required) — taxonomy namespace where the boundary applies.
- scope: string (required) — semantic scope where the boundary applies.
- include_rules: list[string] (required) — explicit inclusion rules for the canonical term.
- exclude_rules: list[string] (required) — explicit exclusion rules for the canonical term.
- scope_note: string (required) — narrative boundary note when inclusion and exclusion lists are insufficient by themselves.
- authority_ref: string (required) — source, governance or phase authority reference for the boundary.
- phase_contract_ref: string (required) — motor_001 phase contract reference authorizing this boundary.
- status: enum[active, deprecated, rejected] (required) — governed publication state of this boundary definition.
- version_id: string (required) — stable technical key for this immutable boundary version.
- created_at: datetime (required) — timestamp when this boundary version was first registered by motor_003.
- updated_at: datetime (required) — timestamp when registry metadata for this boundary version was last updated.
- version_hash: string (required) — deterministic hash of normalized boundary content and immutable metadata.
- source_ref: string (required) — primary source vocabulary or governance record used to produce this boundary.
- produced_by_motor: string (required) — fixed value `motor_003`.
- produced_at: datetime (required) — timestamp when motor_003 emitted this boundary version.
- parent_id: string|null (required) — previous BoundaryDefinition `record_id` when this version supersedes another version; null for the first accepted boundary version.

TaxonomyValidationError:
- record_id: string (required) — immutable storage identifier for this validation error.
- error_id: string (required) — stable identifier for the emitted error signal.
- error_code: enum[MISSING_PROVENANCE, ALIAS_COLLISION, TAXONOMY_PARENT_NOT_FOUND, TAXONOMY_CYCLE, CANONICAL_TERM_DUPLICATE, CONTRACT_SCOPE_VIOLATION, BOUNDARY_DEFINITION_MISSING] (required) — machine-readable rejection reason.
- rejected_input_ref: string (required) — candidate, alias, manifest, node or boundary reference that failed validation.
- taxonomy_id: string|null (required) — taxonomy involved in the rejection when known; null only when the taxonomy field itself is missing.
- scope: string|null (required) — scope involved in the rejection when known; null only when the scope field itself is missing.
- field_path: string (required) — dotted path to the invalid or missing field.
- message: string (required) — concise human-readable explanation of the rejection.
- blocking: boolean (required) — true when the error prevents publication of the candidate or dependent output.
- phase_contract_ref: string|null (required) — motor_001 phase contract reference when supplied; null only for missing-contract errors.
- emitted_at: datetime (required) — timestamp when the validation error was detected.
- version_id: string (required) — stable technical key for this immutable error record.
- created_at: datetime (required) — timestamp when this error record was first emitted by motor_003.
- updated_at: datetime (required) — immutable audit timestamp; for TaxonomyValidationError it must equal `created_at`.
- version_hash: string (required) — deterministic hash of normalized error content and immutable metadata.
- source_ref: string (required) — source candidate, vocabulary manifest or governance record that caused the rejection.
- produced_by_motor: string (required) — fixed value `motor_003`.
- produced_at: datetime (required) — timestamp when motor_003 emitted this error signal.
- parent_id: string|null (required) — prior TaxonomyValidationError `record_id` if a later validation supersedes an earlier signal; null for a new signal.

## relationships
- RawTermCandidate.source_vocab_id references SourceVocabularyManifest.source_vocab_id.
- AliasCandidate.source_vocab_id references SourceVocabularyManifest.source_vocab_id.
- RawTermCandidate.phase_contract_ref and AliasCandidate.phase_contract_ref reference the motor_001 phase contract that authorizes taxonomy governance.
- CanonicalEntity.phase_contract_ref, TaxonomyNode.phase_contract_ref, AliasMappings.phase_contract_ref and BoundaryDefinition.phase_contract_ref reference the motor_001 phase contract used to authorize the output.
- CanonicalEntity.boundary_id references BoundaryDefinition.boundary_id for the current active boundary; a CanonicalEntity cannot become active without a valid boundary.
- BoundaryDefinition.canonical_id references CanonicalEntity.canonical_id and must share the same `taxonomy_id` and `scope`.
- TaxonomyNode.canonical_id references CanonicalEntity.canonical_id. The referenced CanonicalEntity must belong to the same `taxonomy_id`.
- TaxonomyNode.parent_node_id references TaxonomyNode.node_id in the same `taxonomy_id`; null is valid only for explicit root nodes.
- TaxonomyNode path entries reference TaxonomyNode.node_id values in ancestor order and must not contain repeated node identifiers.
- AliasMappings.canonical_id references an active CanonicalEntity.canonical_id in the same `taxonomy_id` and `scope`.
- AliasMappings.source_vocab_id references SourceVocabularyManifest.source_vocab_id through the submitted alias provenance.
- TaxonomyValidationError.rejected_input_ref references the failed RawTermCandidate.candidate_id, AliasCandidate.candidate_id, SourceVocabularyManifest.source_vocab_id, or a proposed persisted record identifier when validation occurs during update.
- CanonicalEntity.parent_id references a prior CanonicalEntity.record_id only when a governed version supersedes an earlier version.
- TaxonomyNode.parent_id references a prior TaxonomyNode.record_id only when a governed version supersedes an earlier node version; it is separate from `parent_node_id`, which represents tree structure.
- AliasMappings.parent_id references a prior AliasMappings.record_id only when a governed version supersedes an earlier alias mapping.
- BoundaryDefinition.parent_id references a prior BoundaryDefinition.record_id only when a governed version supersedes an earlier boundary.
- TaxonomyValidationError.parent_id references a prior TaxonomyValidationError.record_id only when a later validation result supersedes an earlier signal.
- Active CanonicalEntity records are unique by `(taxonomy_id, scope, canonical_label)`.
- Active AliasMappings records are unique by `(taxonomy_id, scope, alias_text)` and each active alias maps to exactly one CanonicalEntity.
- The TaxonomyNode parent-child graph must remain acyclic inside each `taxonomy_id`.

## identifiers
- SourceVocabularyManifest stable identifier: `source_vocab_id`.
- RawTermCandidate stable request identifier: `candidate_id`.
- AliasCandidate stable request identifier: `candidate_id`.
- CanonicalEntity storage identifier: `record_id`; canonical logical identifier: `canonical_id`.
- TaxonomyNode storage identifier: `record_id`; canonical logical identifier: `node_id`.
- AliasMappings storage identifier: `record_id`; canonical logical identifier: `alias_id`.
- BoundaryDefinition storage identifier: `record_id`; canonical logical identifier: `boundary_id`.
- TaxonomyValidationError storage identifier: `record_id`; canonical logical identifier: `error_id`.
- `record_id` identifies one immutable persisted version. It must not be reused across different entity types or material versions.
- `canonical_id` is assigned when a concept is first accepted and is never reused for a different concept, even if the canonical label is later deprecated or superseded.
- `node_id` identifies a governed taxonomy placement for one CanonicalEntity in one taxonomy. Tree parent changes require a new version record and explicit lineage through `parent_id`.
- `alias_id` identifies one governed alias within a taxonomy and scope. Remapping or deprecation requires a new version record rather than silent mutation.
- `boundary_id` identifies the governed semantic boundary for a CanonicalEntity. Boundary changes require a new version record rather than rewriting previous boundary text.
- `error_id` identifies one emitted validation signal and remains immutable for audit.
- Deterministic identifier generation should use normalized entity type, taxonomy_id, scope, logical label or alias, target reference where applicable, source reference and content hash so duplicate identical submissions are idempotent.
- Empty identifiers, reused identifiers across incompatible content, or conflicting identifiers with different `version_hash` values are invalid and emit TaxonomyValidationError.

## versioning
- Every persisted motor_003 output includes `version_id`, `created_at`, `updated_at` and `version_hash`.
- `version_id` identifies one immutable version of a CanonicalEntity, TaxonomyNode, AliasMappings, BoundaryDefinition or TaxonomyValidationError.
- `created_at` is set once when motor_003 registers or emits the version.
- `updated_at` records registry metadata updates for the same immutable version. For immutable rejection signals it must equal `created_at`.
- `version_hash` is computed deterministically from normalized material content, logical identifiers, phase contract reference, provenance and lineage fields, excluding non-material registry timestamps.
- A material change to canonical label, status, taxonomy placement, alias target, boundary text, phase contract reference, provenance or parent linkage creates a new `record_id`, new `version_id` and new `version_hash`.
- A duplicate submission with the same logical identifier and same `version_hash` is idempotent.
- A duplicate active CanonicalEntity with the same `(taxonomy_id, scope, canonical_label)` and a different `canonical_id` is rejected with `CANONICAL_TERM_DUPLICATE`.
- A duplicate active AliasMappings record with the same `(taxonomy_id, scope, alias_text)` and a different `canonical_id` is rejected with `ALIAS_COLLISION`.
- Current records, historical records and rejection signals remain separate. Superseding versions link to earlier immutable records through `parent_id` rather than rewriting prior content.
- SourceVocabularyManifest, RawTermCandidate and AliasCandidate are request DTOs; they are preserved through accepted output provenance or TaxonomyValidationError lineage rather than treated as published canonical vocabulary records.

## lineage
- Every persisted motor_003 output includes `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref` records the primary source vocabulary, governance record, candidate reference or source package used to construct the persisted record.
- `produced_by_motor` is always `motor_003` for records emitted by the Taxonomy + Canonical Entity Service.
- `produced_at` records when motor_003 emitted the accepted record or validation signal, independent of the source vocabulary timestamp.
- `parent_id` links a superseding persisted record to the previous immutable `record_id`; it is null when no predecessor exists.
- Accepted CanonicalEntity, TaxonomyNode, AliasMappings and BoundaryDefinition records retain source provenance through `source_ref`, candidate-level `provenance_ref` or `provenance_refs`, and the governing `phase_contract_ref`.
- TaxonomyValidationError records retain enough lineage to reconstruct the failed input, the validation rule, the source vocabulary, the phase contract reference when present and the blocking decision.
- The motor does not infer missing provenance from label similarity, taxonomy proximity or downstream usage. Missing lineage fields produce TaxonomyValidationError instead of partial publication.
- Lineage for taxonomy tree changes is explicit: tree structure uses `parent_node_id`, while historical supersession uses `parent_id`; these two references must not be collapsed.
- Downstream motors consume canonical terms, aliases, taxonomy nodes and boundaries by reference. They do not gain authority to rewrite motor_003 lineage, identifiers or version history.
