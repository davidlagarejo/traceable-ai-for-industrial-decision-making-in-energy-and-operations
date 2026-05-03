# Functional Contract — Taxonomy + Canonical Entity Service

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

## inputs
- raw_terms: list[RawTermCandidate] — candidatos declarados por vocabularios fuente, revisión humana o extracción estructurada externa; cada item incluye `term_text`, `source_vocab_id`, `scope`, `provenance_ref`.
- aliases: list[AliasCandidate] — aliases propuestos desde vocabularios fuente o entradas de gobernanza; cada item incluye `alias_text`, `target_term_text` o `target_canonical_id`, `source_vocab_id`, `provenance_ref`.
- source_vocabularies: list[SourceVocabularyManifest] — manifiestos de vocabulario externo o interno; cada item incluye `source_vocab_id`, `source_name`, `vocabulary_version`, `terms_ref`, `authority_note`.
- phase_contract_ref: string — referencia al contrato aplicable producido por motor_001 para confirmar que la operación pertenece al alcance de gobernanza taxonómica.

## outputs
- canonical_term: CanonicalEntity — registro canónico consumido por motores downstream que necesitan vocabulario estable, especialmente normalización, identidad, calidad y harness de integración.
- alias_map: AliasMappings — mapa de alias aceptados hacia términos canónicos, consumido por motores que necesitan interpretar etiquetas fuente sin crear dialectos paralelos.
- taxonomy_tree: list[TaxonomyNode] — jerarquía acíclica de términos canónicos, consumida por motores que requieren agrupación, herencia semántica o validación de scope.
- boundary_definition: BoundaryDefinition — definición explícita de inclusión y exclusión semántica, consumida por motores downstream y revisiones de conformidad.
- taxonomy_rejection: TaxonomyValidationError — error estructurado emitido cuando un candidato no puede convertirse en vocabulario autorizado.

## limits
- Nunca acepta registros operativos completos, datasets raw, documentos fuente sin parsear, `parsed_record`, `normalized_record` ni `identity_record` como objetos a modificar.
- Nunca produce `normalized_record`, `identity_resolution_record`, `quality_record`, `duplicate_cluster`, reporte analítico ni decisión de join.
- Nunca convierte valores de datos a forma canónica; solo gobierna términos de vocabulario y aliases.
- Nunca acepta un alias sin `source_vocab_id` y `provenance_ref`.
- Nunca acepta un nodo taxonómico cuyo padre no exista en la misma taxonomía, salvo que el nodo se declare explícitamente como raíz.
- Nunca publica un término canónico sin `boundary_definition` mínima.

## validations
- Antes de procesar, valida que `phase_contract_ref` exista y autorice una operación de gobernanza taxonómica.
- Antes de procesar, valida que todo `raw_terms` incluya `term_text`, `source_vocab_id`, `scope` y `provenance_ref` no vacíos.
- Antes de procesar, valida que todo alias apunte a un `target_canonical_id` existente o a un candidato de término presente en la misma solicitud.
- Antes de procesar, rechaza aliases que apunten a más de un término canónico activo dentro del mismo `taxonomy_id` y `scope`.
- Antes de emitir `taxonomy_tree`, valida que no existan ciclos y que cada `parent_node_id` no nulo exista dentro del mismo `taxonomy_id`.
- Antes de emitir `canonical_term`, valida que no exista otro término activo con la misma etiqueta canónica, taxonomía y scope.
- Antes de emitir `boundary_definition`, valida que incluya al menos una regla de inclusión, una regla de exclusión o una nota de límite suficientemente explícita.
- Todo output aceptado incluye identificador estable, estado, source provenance y referencia de contrato.
