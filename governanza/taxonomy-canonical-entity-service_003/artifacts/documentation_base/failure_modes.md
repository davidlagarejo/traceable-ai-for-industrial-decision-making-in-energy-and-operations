# Failure Modes — Taxonomy + Canonical Entity Service

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

## failure_modes_list
- SEMANTIC_DRIFT: an active canonical term changes meaning over time without a new boundary definition or explicit governed update; downstream motors start interpreting the same id differently.
- ALIAS_COLLISION: the same alias maps to multiple active canonical terms in the same taxonomy scope; downstream joins become unstable or non-deterministic.
- TAXONOMY_CYCLE_OR_ORPHAN: taxonomy nodes reference missing parents or create cycles; tree traversal, inheritance and scope validation fail.
- VOCABULARY_SCOPE_CREEP: the motor starts accepting normalized records, identity decisions or quality scores as if they were vocabulary governance inputs.
- PROVENANCE_LOSS: canonical terms or aliases are published without source vocabulary references; later rebuild, audit and dispute resolution cannot reconstruct why the term was accepted.

## anti_patterns
- Using the service as an ad hoc lookup table that accepts labels without provenance, boundary definition or contract reference.
- Treating aliases as proof that two records describe the same real-world entity.
- Overwriting canonical labels in place to match a new source vocabulary instead of preserving the existing term and creating a governed update.
- Letting downstream normalization rules create new canonical terms automatically when they encounter unknown labels.

## degradation_signals
- Rising count of `ALIAS_COLLISION` rejections for the same taxonomy and scope.
- Any active `CanonicalEntity` without an attached `BoundaryDefinition`.
- Non-zero count of orphan taxonomy nodes or cycle detection failures.
- Frequent proposals for variant labels that should already resolve to existing canonical terms.
- Downstream join instability traced to changed alias mappings rather than changed source data.
- Increase in manually overridden taxonomy decisions without corresponding provenance or contract references.
