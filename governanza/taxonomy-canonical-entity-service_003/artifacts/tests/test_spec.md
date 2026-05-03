# Test Spec — Taxonomy + Canonical Entity Service

Motor ID: motor_003

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Gobernar taxonomías, términos canónicos, aliases y límites semánticos del sistema.
why_it_exists:  Evita drift semántico, dialectos paralelos y joins inestables entre fuentes.
key_inputs:     raw terms, aliases, source vocabularies
key_outputs:    canonical_term, alias_map, taxonomy_tree, boundary_definition
key_objects:    CanonicalEntity, TaxonomyNode, AliasMappings
what_not_to_do: No normaliza datos. No resuelve identidad de registros. Solo gobierna el vocabulario.
design_notes:   Depende de motor_001. Es la referencia semántica que todos los motores downstream consultan.

Sections below are complete for tests gate validation.
-->

## happy_path
Input:
- `phase_contract_ref="motor_001:taxonomy_governance:v1"` autoriza gobernanza taxonómica.
- `source_vocabularies` contiene un manifiesto con `source_vocab_id="epa_biogas_vocab_v1"`, `source_name="EPA Biogas Vocabulary"`, `vocabulary_version="2026.01"`, `terms_ref="registry://epa_biogas/terms/2026.01"`, `authority_note="governed source vocabulary"`, `source_ref="source_package:epa_biogas:2026.01"` y `submitted_at="2026-01-15T10:00:00Z"`.
- `raw_terms` contiene `candidate_id="term_anaerobic_digester"`, `term_text="anaerobic digester"`, `source_vocab_id="epa_biogas_vocab_v1"`, `taxonomy_id="waste_system_taxonomy"`, `scope="facility_infrastructure"`, `parent_node_id="node_waste_treatment_system"`, `boundary_include_rules=["sealed anaerobic biological treatment vessel"]`, `boundary_exclude_rules=["aerobic composting system"]`, `boundary_scope_note="Facility infrastructure term, not a biological process label."`, `provenance_ref="source_vocab:epa_biogas_vocab_v1:term:42"` y el mismo `phase_contract_ref`.
- `aliases` contiene dos candidatos: `alias_text="AD"` y `alias_text="biodigester"`, ambos con `target_term_text="anaerobic digester"`, `taxonomy_id="waste_system_taxonomy"`, `scope="facility_infrastructure"`, `source_vocab_id="epa_biogas_vocab_v1"`, `provenance_ref` propio y el mismo `phase_contract_ref`.

Expected output:
- `canonical_term` is a `CanonicalEntity` with non-empty `record_id`, stable `canonical_id`, `canonical_label="anaerobic digester"`, `taxonomy_id="waste_system_taxonomy"`, `scope="facility_infrastructure"`, `status="active"`, `produced_by_motor="motor_003"`, the supplied `phase_contract_ref` and provenance including `source_vocab:epa_biogas_vocab_v1:term:42`.
- `alias_map` contains two active `AliasMappings` records, one for `AD` and one for `biodigester`, both pointing to the same `canonical_id`, preserving their submitted alias text and source provenance.
- `taxonomy_tree` contains an active `TaxonomyNode` for the canonical entity with `parent_node_id="node_waste_treatment_system"` and a path that includes both the parent node and the new node without repeated node ids.
- `boundary_definition` is active, references the same `canonical_id`, includes the submitted inclusion and exclusion rules, and carries a non-empty `authority_ref`.
- No `normalized_record`, `identity_resolution_record`, `duplicate_cluster`, analytical report or join decision is emitted.

## sparse_case
Input:
- A valid source vocabulary manifest and a valid `phase_contract_ref`.
- One `RawTermCandidate` for `term_text="waste treatment system"` with `taxonomy_id="waste_system_taxonomy"`, `scope="facility_infrastructure"`, `parent_node_id=null`, empty `boundary_include_rules=[]`, empty `boundary_exclude_rules=[]`, and `boundary_scope_note="Top-level root term for facility infrastructure taxonomy."`
- `aliases=[]`.

Expected behavior:
- The motor accepts the candidate as an explicit taxonomy root because `parent_node_id` is null and the boundary scope note is non-empty.
- The motor emits one active `CanonicalEntity`, one active root `TaxonomyNode` whose `path` contains only its own `node_id`, one active `BoundaryDefinition`, and an empty `alias_map`.
- The motor does not treat the absence of aliases as fatal and does not create aliases implicitly.

## malformed_input
Input:
- `phase_contract_ref="motor_001:taxonomy_governance:v1"`.
- `source_vocabularies` contains the referenced manifest.
- `raw_terms` contains `candidate_id="term_orphan_label"` with `term_text="unprovenanced label"`, `source_vocab_id=""`, `taxonomy_id="waste_system_taxonomy"`, `scope="facility_infrastructure"`, `parent_node_id="node_waste_treatment_system"`, boundary content present, and `provenance_ref=""`.
- `aliases` is submitted as an object instead of a list, with `alias_text="UL"` and no `provenance_ref`.

Expected behavior:
- The motor rejects the request before publishing any canonical term, alias mapping, taxonomy node or boundary.
- The rejection includes a blocking `TaxonomyValidationError` with `error_code="MISSING_PROVENANCE"`, `rejected_input_ref="term_orphan_label"`, `field_path` pointing to the missing `source_vocab_id` or `provenance_ref`, `taxonomy_id="waste_system_taxonomy"`, `scope="facility_infrastructure"`, `produced_by_motor="motor_003"` and the supplied `phase_contract_ref`.
- The malformed `aliases` shape is not coerced into a list and cannot create an alias mapping.

## edge_cases
- Duplicate canonical label in same scope: if `canonical_label="anaerobic digester"` is already active for `taxonomy_id="waste_system_taxonomy"` and `scope="facility_infrastructure"`, a new candidate with `term_text="Anaerobic Digester"` in the same tuple is rejected with blocking `TaxonomyValidationError.error_code="CANONICAL_TERM_DUPLICATE"` unless the request is an explicit governed update to the existing `canonical_id`.
- Alias collision in same scope: if active alias `AD` already maps to `canonical_id="canon_anaerobic_digester"` in `taxonomy_id="waste_system_taxonomy"` and `scope="facility_infrastructure"`, a new alias candidate `alias_text="AD"` targeting `canonical_id="canon_anaerobic_digestion_process"` in the same taxonomy and scope is rejected with `ALIAS_COLLISION`.
- Alias reused in a separate scope: the same alias text `AD` may be accepted for a different canonical target only when `taxonomy_id` and `scope` make the semantic boundary explicit and non-overlapping, for example `scope="biological_process"` rather than `scope="facility_infrastructure"`.
- Missing parent node: a candidate with `parent_node_id="node_thermal_treatment_system"` is rejected with `TAXONOMY_PARENT_NOT_FOUND` when that node does not exist in `taxonomy_id="waste_system_taxonomy"`.
- Taxonomy cycle: an update that would make `node_waste_treatment_system` a descendant of its own child `node_anaerobic_digester` is rejected with `TAXONOMY_CYCLE`; no partial tree update is published.
- Missing boundary: a candidate with valid text, scope and provenance but no inclusion rules, no exclusion rules and empty `boundary_scope_note` is rejected with `BOUNDARY_DEFINITION_MISSING`.

## pass_criteria
The test passes when every accepted case emits only the four authorized output families (`canonical_term`, `alias_map`, `taxonomy_tree`, `boundary_definition`), all persisted records include stable identifiers, `version_id`, `version_hash`, lineage fields, `produced_by_motor="motor_003"`, source provenance and the governing `phase_contract_ref`, and every rejected case emits a blocking `TaxonomyValidationError` with the expected `error_code`, `rejected_input_ref`, `field_path`, `taxonomy_id`, `scope` and no partial published vocabulary output.

## fail_criteria
The test fails if the motor accepts a term or alias without source provenance, creates a second active canonical term for the same `taxonomy_id`, `scope` and canonical label, maps one active alias to multiple canonical ids in the same scope, publishes a taxonomy node with a missing parent or cycle, exposes a canonical term without a boundary definition, silently rewrites submitted source labels, emits normalized records or identity decisions, or returns an unstructured exception instead of a deterministic `TaxonomyValidationError` for domain validation failures.
