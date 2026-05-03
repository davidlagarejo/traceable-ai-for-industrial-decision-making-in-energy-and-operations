# Conceptual Schema — Taxonomy + Canonical Entity Service

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

## entities
- CanonicalEntity: término canónico autorizado que representa un concepto nombrable dentro de una taxonomía y un scope.
- TaxonomyNode: posición jerárquica de una entidad canónica dentro de un árbol taxonómico acíclico.
- AliasMappings: conjunto de aliases aceptados que conectan etiquetas fuente o variantes lingüísticas con una entidad canónica.
- BoundaryDefinition: declaración explícita de inclusión, exclusión y límites de uso semántico para un término canónico.
- TaxonomyValidationError: error estructurado que explica por qué un candidato fue rechazado antes de publicarse.

## relationships
- AliasMappings -> CanonicalEntity (cada alias aceptado apunta a exactamente una entidad canónica dentro de un `taxonomy_id` y `scope`).
- CanonicalEntity -> TaxonomyNode (una entidad canónica activa puede estar representada por uno o más nodos cuando participa en taxonomías distintas).
- TaxonomyNode -> TaxonomyNode (un nodo puede tener un padre dentro de la misma taxonomía; esta relación debe ser acíclica).
- CanonicalEntity -> BoundaryDefinition (cada entidad canónica activa tiene al menos una definición de frontera vigente).
- SourceVocabularyManifest -> AliasMappings (un vocabulario fuente puede aportar varios aliases, siempre con provenance explícita).
- TaxonomyValidationError -> raw_terms or aliases (cada rechazo referencia el input que no pasó validación).

## key_fields
CanonicalEntity:
- canonical_id: string
- canonical_label: string
- taxonomy_id: string
- scope: string
- status: enum[proposed, active, deprecated, rejected]
- provenance_refs: list[string]

TaxonomyNode:
- node_id: string
- taxonomy_id: string
- canonical_id: string
- parent_node_id: string|null
- path: list[string]
- sort_order: integer

AliasMappings:
- alias_id: string
- alias_text: string
- canonical_id: string
- taxonomy_id: string
- source_vocab_id: string
- provenance_ref: string

BoundaryDefinition:
- boundary_id: string
- canonical_id: string
- include_rules: list[string]
- exclude_rules: list[string]
- scope_note: string
- authority_ref: string

TaxonomyValidationError:
- error_code: enum[MISSING_PROVENANCE, ALIAS_COLLISION, TAXONOMY_PARENT_NOT_FOUND, TAXONOMY_CYCLE, CANONICAL_TERM_DUPLICATE, CONTRACT_SCOPE_VIOLATION]
- rejected_input_ref: string
- message: string
- blocking: boolean
- emitted_at: string
