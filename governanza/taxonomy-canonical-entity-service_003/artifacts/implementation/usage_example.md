# Usage Example — Taxonomy + Canonical Entity Service

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

## example
El registro de gobernanza de vocabulario recibe desde una fuente EPA un candidato de término para `anaerobic digester` dentro de la taxonomía `waste_system_taxonomy` y el scope `facility_infrastructure`. Motor_003 valida que el contrato de fase autoriza gobernanza taxonómica, que la fuente y el término tienen provenance explícita, que el padre taxonómico existe y que los aliases `AD` y `biodigester` no colisionan dentro del mismo scope. El resultado esperado es un término canónico activo con boundary semántica, aliases trazables y un nodo taxonómico acíclico, sin producir registros normalizados ni decisiones de identidad.

## inputs_used
```json
{
  "phase_contract_ref": "motor_001:taxonomy_governance:v1",
  "source_vocabularies": [
    {
      "source_vocab_id": "epa_biogas_vocab_v1",
      "source_name": "EPA Biogas Vocabulary",
      "vocabulary_version": "2026.01",
      "terms_ref": "registry://epa_biogas/terms/2026.01",
      "authority_note": "governed source vocabulary for biogas infrastructure terminology",
      "source_ref": "source_package:epa_biogas:2026.01",
      "submitted_at": "2026-01-15T10:00:00Z"
    }
  ],
  "raw_terms": [
    {
      "candidate_id": "term_anaerobic_digester",
      "term_text": "anaerobic digester",
      "source_vocab_id": "epa_biogas_vocab_v1",
      "taxonomy_id": "waste_system_taxonomy",
      "scope": "facility_infrastructure",
      "parent_node_id": "node_waste_treatment_system",
      "boundary_include_rules": ["sealed anaerobic biological treatment vessel"],
      "boundary_exclude_rules": ["aerobic composting system"],
      "boundary_scope_note": "Facility infrastructure term, not a biological process label.",
      "provenance_ref": "source_vocab:epa_biogas_vocab_v1:term:42",
      "phase_contract_ref": "motor_001:taxonomy_governance:v1"
    }
  ],
  "aliases": [
    {
      "candidate_id": "alias_ad",
      "alias_text": "AD",
      "target_canonical_id": null,
      "target_term_text": "anaerobic digester",
      "source_vocab_id": "epa_biogas_vocab_v1",
      "taxonomy_id": "waste_system_taxonomy",
      "scope": "facility_infrastructure",
      "provenance_ref": "source_vocab:epa_biogas_vocab_v1:alias:42a",
      "phase_contract_ref": "motor_001:taxonomy_governance:v1"
    },
    {
      "candidate_id": "alias_biodigester",
      "alias_text": "biodigester",
      "target_canonical_id": null,
      "target_term_text": "anaerobic digester",
      "source_vocab_id": "epa_biogas_vocab_v1",
      "taxonomy_id": "waste_system_taxonomy",
      "scope": "facility_infrastructure",
      "provenance_ref": "source_vocab:epa_biogas_vocab_v1:alias:42b",
      "phase_contract_ref": "motor_001:taxonomy_governance:v1"
    }
  ]
}
```

## expected_output
```json
{
  "canonical_term": {
    "record_id": "rec_canonical_<stable_hash>",
    "canonical_id": "canon_<stable_hash>",
    "canonical_label": "anaerobic digester",
    "taxonomy_id": "waste_system_taxonomy",
    "scope": "facility_infrastructure",
    "status": "active",
    "phase_contract_ref": "motor_001:taxonomy_governance:v1",
    "boundary_id": "boundary_<stable_hash>",
    "provenance_refs": ["source_vocab:epa_biogas_vocab_v1:term:42"],
    "version_id": "ver_canonical_<stable_hash>",
    "version_hash": "<deterministic_content_hash>",
    "source_ref": "source_package:epa_biogas:2026.01",
    "produced_by_motor": "motor_003",
    "parent_id": null
  },
  "alias_map": [
    {
      "alias_text": "AD",
      "canonical_id": "canon_<same_as_canonical_term>",
      "taxonomy_id": "waste_system_taxonomy",
      "scope": "facility_infrastructure",
      "source_vocab_id": "epa_biogas_vocab_v1",
      "provenance_ref": "source_vocab:epa_biogas_vocab_v1:alias:42a",
      "status": "active",
      "phase_contract_ref": "motor_001:taxonomy_governance:v1",
      "produced_by_motor": "motor_003"
    },
    {
      "alias_text": "biodigester",
      "canonical_id": "canon_<same_as_canonical_term>",
      "taxonomy_id": "waste_system_taxonomy",
      "scope": "facility_infrastructure",
      "source_vocab_id": "epa_biogas_vocab_v1",
      "provenance_ref": "source_vocab:epa_biogas_vocab_v1:alias:42b",
      "status": "active",
      "phase_contract_ref": "motor_001:taxonomy_governance:v1",
      "produced_by_motor": "motor_003"
    }
  ],
  "taxonomy_tree": [
    {
      "node_id": "node_<stable_hash>",
      "canonical_id": "canon_<same_as_canonical_term>",
      "taxonomy_id": "waste_system_taxonomy",
      "parent_node_id": "node_waste_treatment_system",
      "path": ["node_waste_treatment_system", "node_<stable_hash>"],
      "status": "active",
      "phase_contract_ref": "motor_001:taxonomy_governance:v1",
      "produced_by_motor": "motor_003"
    }
  ],
  "boundary_definition": {
    "boundary_id": "boundary_<stable_hash>",
    "canonical_id": "canon_<same_as_canonical_term>",
    "taxonomy_id": "waste_system_taxonomy",
    "scope": "facility_infrastructure",
    "include_rules": ["sealed anaerobic biological treatment vessel"],
    "exclude_rules": ["aerobic composting system"],
    "scope_note": "Facility infrastructure term, not a biological process label.",
    "authority_ref": "governed source vocabulary for biogas infrastructure terminology",
    "phase_contract_ref": "motor_001:taxonomy_governance:v1",
    "status": "active",
    "produced_by_motor": "motor_003"
  },
  "taxonomy_rejection": []
}
```

## notes
Precondiciones: `motor_001:taxonomy_governance:v1` debe existir como contrato autorizado y `node_waste_treatment_system` debe estar registrado previamente como nodo activo en `waste_system_taxonomy`. Si falta provenance, el alias apunta a otro canonical activo dentro del mismo scope, el padre no existe o la boundary queda vacía, el motor publica solo `taxonomy_rejection` con un `TaxonomyValidationError` bloqueante. Este ejemplo no convierte valores fuente a forma canónica, no resuelve identidad de instalaciones y no emite `normalized_record`, `identity_resolution_record`, `quality_record`, `duplicate_cluster` ni reporte analítico.
