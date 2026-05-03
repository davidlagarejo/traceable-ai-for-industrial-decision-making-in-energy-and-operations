# Failure Modes Spec — Taxonomy + Canonical Entity Service

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

## failure_modes_list
- FM-003-001_MISSING_PROVENANCE: a `RawTermCandidate`, `AliasCandidate` or `SourceVocabularyManifest` enters validation with empty `source_vocab_id`, `provenance_ref`, `source_ref` or unauthorized `phase_contract_ref` -> accepted records would be impossible to audit or rebuild, or validation emits repeated `MISSING_PROVENANCE` / `CONTRACT_SCOPE_VIOLATION` errors -> reject the candidate before publication, emit blocking `TaxonomyValidationError`, and require the submitter to resubmit with explicit source vocabulary, source reference and motor_001 contract reference.
- FM-003-002_CANONICAL_DUPLICATE: a proposed canonical label normalizes to an already active `(taxonomy_id, scope, canonical_label)` tuple but carries a different `canonical_id` -> downstream consumers see two active canonical identifiers for the same governed term and joins become unstable -> reject with `CANONICAL_TERM_DUPLICATE`; if the change is legitimate, process it as a governed version update that links the new immutable record through `parent_id`.
- FM-003-003_ALIAS_COLLISION: an `AliasCandidate` reuses active `alias_text` inside the same `taxonomy_id` and `scope` while targeting a different canonical term -> alias lookup becomes non-deterministic and downstream motors can map the same source label to conflicting concepts -> reject with `ALIAS_COLLISION`, preserve the prior active mapping, and require an explicit deprecation or scope split before any remap is accepted.
- FM-003-004_TAXONOMY_GRAPH_CORRUPTION: a `TaxonomyNode` references a missing parent, a parent outside its taxonomy, or a parent update that introduces a repeated node in `path` -> taxonomy traversal fails, inherited scope checks become unreliable, or tree consumers loop -> reject with `TAXONOMY_PARENT_NOT_FOUND` or `TAXONOMY_CYCLE`, publish no partial tree update, and rebuild the proposed path from the last valid active tree version.
- FM-003-005_BOUNDARYLESS_CANONICAL_TERM: a candidate has valid label and provenance but no inclusion rule, exclusion rule or explicit scope note -> an active `CanonicalEntity` would be exposed without a semantic boundary and could drift into normalization, identity or quality responsibilities -> reject with `BOUNDARY_DEFINITION_MISSING`; require at least one explicit boundary element before canonical publication.
- FM-003-006_SILENT_MUTATION_OF_GOVERNED_TEXT: an update overwrites `canonical_label`, `alias_text`, `BoundaryDefinition` text, `phase_contract_ref` or provenance fields in place instead of producing a new version -> historical records no longer explain earlier downstream behavior and rebuilds produce different results from the same lineage -> block in-place mutation, require new `record_id`, `version_id`, `version_hash` and `parent_id` linkage, and keep the previous active or deprecated record immutable.
- FM-003-007_SCOPE_CREEP_INTO_DOWNSTREAM_LOGIC: the service accepts `normalized_record`, `identity_resolution_record`, duplicate clusters, quality scores or analytical decisions as inputs or emits those outputs -> motor_003 becomes a semantic monolith and starts deciding responsibilities assigned to other motors -> reject unsupported object families with `CONTRACT_SCOPE_VIOLATION`, emit only vocabulary governance records or structured taxonomy rejections, and route the foreign object to its owning motor.

## anti_patterns
- Treating motor_003 as a general data normalizer that rewrites source values, units, addresses, measurements or operational payloads.
- Treating alias equality as identity resolution between facilities, organizations, documents or observations.
- Letting downstream motors create canonical terms automatically when an unknown label is encountered.
- Storing the current taxonomy tree as mutable rows without immutable version records and explicit `parent_id` lineage.
- Using one global alias table without the `(taxonomy_id, scope)` boundary, which makes legitimate same-text aliases collide across separate semantic scopes.
- Publishing `CanonicalEntity` records before their matching `BoundaryDefinition` is validated and linked.
- Correcting missing provenance by copying provenance from a nearby term, a similar alias or a downstream object.
- Collapsing `TaxonomyNode.parent_node_id` and historical `parent_id` into one field; taxonomy structure and version lineage are different relationships.
- Allowing LLM-suggested terms, labels or boundaries to bypass deterministic validation and source vocabulary provenance.
- Returning unstructured exceptions or warnings for blocking taxonomy violations instead of immutable `TaxonomyValidationError` records.

## degradation_signals
- `taxonomy_validation_errors_total{error_code="ALIAS_COLLISION", taxonomy_id, scope}` rises for the same alias text across multiple submissions.
- Any active `CanonicalEntity` has an empty `boundary_id`, empty `provenance_refs`, empty `phase_contract_ref` or `produced_by_motor` other than `motor_003`.
- Any active `AliasMappings` tuple `(taxonomy_id, scope, alias_text)` resolves to more than one active `canonical_id`.
- Any active `TaxonomyNode.path` contains a repeated `node_id`, a parent outside the same `taxonomy_id`, or a `parent_node_id` that is absent from the active tree.
- Rebuild checks produce a different `version_hash` for unchanged material content, provenance and phase contract reference.
- The count of accepted taxonomy updates without non-null `parent_id` increases after the first version of a term, alias, node or boundary already exists.
- Logs contain unsupported output families such as `normalized_record`, `identity_resolution_record`, `quality_record`, `duplicate_cluster` or analytical report objects emitted by motor_003.
- A high ratio of manual override events lacks matching source vocabulary references or contract references.
- Downstream test harness failures trace to changed alias targets or boundary text while source vocabulary versions are unchanged.
- Idempotent duplicate submissions create new `record_id` values instead of returning or referencing the existing version with the same `version_hash`.

## expensive_errors
- Publishing an alias collision: expensive because every downstream lookup that used the alias may have attached records to the wrong canonical concept; prevention is enforcing active uniqueness on `(taxonomy_id, scope, alias_text)` before publication and blocking remaps without explicit deprecation lineage.
- Reusing a `canonical_id` for a different concept: expensive because historical normalized records, identity decisions, quality records and reports can appear to reference the same concept while meaning changed; prevention is never reusing `canonical_id` and requiring superseding records to use new immutable versions with `parent_id`.
- Accepting a canonical term without boundary definition: expensive because downstream motors may build normalization and validation rules around an undefined semantic scope; prevention is making `BoundaryDefinition` mandatory before any `CanonicalEntity.status="active"` exposure.
- Mutating taxonomy tree placement in place: expensive because previous tree traversals and inherited scope checks cannot be reconstructed; prevention is creating a new `TaxonomyNode` version for every material parent or path change and preserving prior node versions.
- Inferring missing provenance after acceptance: expensive because later audits cannot distinguish true source support from reconstructed assumptions; prevention is rejecting missing `source_vocab_id`, `source_ref`, `provenance_ref` or `phase_contract_ref` at ingest time.
- Allowing unsupported downstream objects into the service: expensive because motor boundaries blur and later correction requires separating vocabulary governance from normalization, identity, duplicate control or quality decisions across persisted artifacts; prevention is schema-level rejection of foreign object families and contract validation against motor_001.
- Producing non-deterministic identifiers or hashes: expensive because identical submissions can fork canonical records and make rebuild manifests disagree; prevention is deterministic identifier and `version_hash` generation from normalized material content, taxonomy, scope, source reference, phase contract and lineage.
