# Operational Rules — Taxonomy + Canonical Entity Service

Motor ID: motor_003

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Gobernar taxonomías, términos canónicos, aliases y límites semánticos del sistema.
why_it_exists:  Evita drift semántico, dialectos paralelos y joins inestables entre fuentes.
key_inputs:     raw terms, aliases, source vocabularies
key_outputs:    canonical_term, alias_map, taxonomy_tree, boundary_definition
key_objects:    CanonicalEntity, TaxonomyNode, AliasMappings
what_not_to_do: No normaliza datos. No resuelve identidad de registros. Solo gobierna el vocabulario.
design_notes:   Depende de motor_001. Es la referencia semántica que todos los motores downstream consultan.

Sections below are complete for documentation_base gate validation.
-->

## rules
1. Every accepted `CanonicalEntity` must have a non-empty `canonical_id`, `canonical_label`, `taxonomy_id`, `scope`, `status` and `provenance_refs`.
2. A canonical label can be active only once for the same `taxonomy_id` and `scope`; duplicates are rejected with `CANONICAL_TERM_DUPLICATE`.
3. Each accepted alias maps to exactly one active `CanonicalEntity` inside the same `taxonomy_id` and `scope`.
4. Any alias collision inside the same `taxonomy_id` and `scope` is blocking and emits `ALIAS_COLLISION`.
5. A `TaxonomyNode` with `parent_node_id` must reference an existing node in the same `taxonomy_id`.
6. The taxonomy graph must remain acyclic after every accepted create or update operation.
7. Every active `CanonicalEntity` must have a `BoundaryDefinition` that states semantic inclusion, semantic exclusion or a clear scope note.
8. Accepted changes must preserve the submitted source label and alias text; the motor never overwrites source vocabulary text in place.
9. Every published output must include the governing `phase_contract_ref` from motor_001.

## invariants
- `canonical_id` is stable and is never reused for a different concept.
- Active aliases are unique by the tuple `taxonomy_id`, `scope`, `alias_text`.
- Active canonical terms are unique by the tuple `taxonomy_id`, `scope`, `canonical_label`.
- A taxonomy tree has zero or more roots, but no cycles and no parent references outside its own `taxonomy_id`.
- Source provenance is retained for every canonical term, alias and boundary definition.
- Boundary definitions are attached to canonical terms before those terms are exposed to downstream consumers.
- Rejections are explicit and structured; failed candidates are not silently corrected or partially published.

## forbidden_operations
- Normalizing record values, fields, dates, units, addresses, measurements or payloads.
- Resolving whether two operational records refer to the same real-world entity.
- Merging facilities, organizations, documents or observations based on alias similarity.
- Ingesting or parsing raw source documents.
- Scoring dataset quality, source reliability, fitness for phase use or downstream trust.
- Creating duplicate-control clusters or near-duplicate decisions.
- Generating analytical conclusions, reports, inference records or validation agendas.
- Promoting an AI-suggested term to canonical status without structured source provenance and deterministic validation.
