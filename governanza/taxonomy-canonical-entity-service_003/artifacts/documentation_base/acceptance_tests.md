# Acceptance Tests — Taxonomy + Canonical Entity Service

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

## happy_path
Input: a `source_vocabularies` manifest with `source_vocab_id="epa_biogas_vocab_v1"`, one raw term `term_text="anaerobic digester"`, aliases `["AD", "biodigester"]`, `scope="facility_infrastructure"`, `provenance_ref="source_vocab:epa_biogas_vocab_v1:term:42"`, and `phase_contract_ref="motor_001:taxonomy_governance"`.

Action: the motor validates the contract, confirms that the parent node `waste_treatment_system` exists, checks that aliases do not collide inside the same taxonomy and registers the term.

Expected output: a `canonical_term` with stable `canonical_id`, `canonical_label="anaerobic digester"`, active status and provenance; an `alias_map` mapping `AD` and `biodigester` to that canonical id; a `taxonomy_tree` node under `waste_treatment_system`; and a `boundary_definition` that includes sealed anaerobic biological treatment vessels and excludes aerobic composting systems. The output contains no normalized record and no identity resolution decision.

## edge_cases
- Case variant duplicate: input proposes `term_text="Anaerobic Digester"` in the same `taxonomy_id` and `scope` where `canonical_label="anaerobic digester"` is already active. Correct behavior: reject creation of a second canonical entity with `CANONICAL_TERM_DUPLICATE` or attach the submission as provenance to the existing entity through an explicit governed update.
- Alias reused across scopes: input proposes alias `AD` for `anaerobic digestion` in `scope="biological_process"` while `AD` already maps to `anaerobic digester` in `scope="facility_infrastructure"`. Correct behavior: accept only if the scopes and taxonomy paths are explicit and non-overlapping; otherwise reject with `ALIAS_COLLISION`.
- Root node insertion: input proposes a new top-level taxonomy node with `parent_node_id=null`. Correct behavior: accept only when the source manifest declares it as a root and boundary definition is present.
- Missing parent node: input proposes parent `thermal_treatment_system` that is absent from the same taxonomy. Correct behavior: reject with `TAXONOMY_PARENT_NOT_FOUND` and publish no partial taxonomy tree.

## rejection_criteria
- Missing provenance: any raw term or alias without `source_vocab_id` or `provenance_ref` is rejected with `MISSING_PROVENANCE`.
- Alias collision: an alias that maps to two active canonical terms in the same `taxonomy_id` and `scope` is rejected with `ALIAS_COLLISION`.
- Taxonomy cycle: any parent-child change that would make a node its own ancestor is rejected with `TAXONOMY_CYCLE`.
- Contract violation: any operation not authorized by the supplied motor_001 phase contract is rejected with `CONTRACT_SCOPE_VIOLATION`.
