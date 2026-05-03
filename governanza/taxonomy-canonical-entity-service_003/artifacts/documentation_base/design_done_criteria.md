# Design Done Criteria — Taxonomy + Canonical Entity Service

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

## criteria
- `master_concept_doc.md` defines purpose, concrete responsibilities, explicit non-responsibilities and the reason this motor is separate from ingestion, normalization and identity resolution.
- `functional_contract.md` lists typed inputs and outputs with source or consumer, including `raw_terms`, `aliases`, `source_vocabularies`, `canonical_term`, `alias_map`, `taxonomy_tree` and `boundary_definition`.
- `functional_contract.md`, `conceptual_schema.md` and `operational_rules.md` contain no open markers and include the required sections for Gate 1.
- `conceptual_schema.md` defines `CanonicalEntity`, `TaxonomyNode`, `AliasMappings` and `BoundaryDefinition` with required fields and relationships.
- `operational_rules.md` includes enforceable rules for stable canonical ids, alias uniqueness, acyclic taxonomy trees, provenance retention and explicit rejection.
- `acceptance_tests.md` covers a concrete happy path, duplicate or scope edge cases, and explicit rejection criteria with named error signals.
- `failure_modes.md` lists semantic drift, alias collision, taxonomy graph corruption, scope creep and provenance loss as observable risks.
- The documentation explicitly excludes data normalization, record identity resolution, source ingestion, dataset quality scoring and analytical reporting from this motor.
