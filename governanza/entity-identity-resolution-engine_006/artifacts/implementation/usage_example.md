# Usage Example — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.

Implementation example completed for gate 5.
-->

## example
Un pipeline de curacion recibe dos registros normalizados desde `motor_005` para la organizacion ACME HEALTH y los compara contra una entidad canonica autorizada por `motor_003`. El motor aplica `identity-policy-1.0.0`, confirma que ambos registros tienen el mismo tipo de entidad, alias normalizado e identificador fiscal, y emite una decision trazable de identidad compartida.

## inputs_used
```json
{
  "normalized_records": [
    {
      "record_id": "rec_101",
      "entity_type": "organization",
      "normalized_fields": {
        "legal_name": "ACME HEALTH",
        "org_tax_id": "98-7654321"
      },
      "source_ref": "source_registry_a",
      "provenance_ref": "prov_rec_101",
      "lineage_refs": ["lin_rec_101"]
    },
    {
      "record_id": "rec_102",
      "entity_type": "organization",
      "normalized_fields": {
        "legal_name": "ACME HEALTH",
        "org_tax_id": "98-7654321"
      },
      "source_ref": "source_registry_b",
      "provenance_ref": "prov_rec_102",
      "lineage_refs": ["lin_rec_102"]
    }
  ],
  "canonical_entities": [
    {
      "canonical_entity_id": "can_org_44",
      "entity_type": "organization",
      "taxonomy_version_id": "taxonomy-2026-01",
      "aliases": ["ACME HEALTH"],
      "external_identifiers": {
        "org_tax_id": "98-7654321"
      },
      "lineage_refs": ["lin_can_org_44"]
    }
  ],
  "resolution_policy": {
    "rule_version": "identity-policy-1.0.0",
    "match_threshold": 2,
    "high_confidence_score": 3,
    "strong_identifier_fields": ["org_tax_id"]
  },
  "previous_identity_records": []
}
```

## expected_output
```json
{
  "identity_resolution_record": [
    {
      "evaluated_record_ids": ["rec_101", "rec_102"],
      "decision": "same_entity",
      "confidence_band": "high",
      "rule_version": "identity-policy-1.0.0",
      "evidence_refs": [
        "candidate_match_<deterministic-id-for-rec_101>",
        "candidate_match_<deterministic-id-for-rec_102>"
      ],
      "lineage_refs": [
        "canonical_entity:can_org_44",
        "lin_can_org_44",
        "lin_rec_101",
        "lin_rec_102",
        "prov_rec_101",
        "prov_rec_102",
        "taxonomy:taxonomy-2026-01"
      ],
      "produced_by_motor": "motor_006"
    }
  ],
  "entity_cluster": [
    {
      "canonical_entity_id": "can_org_44",
      "member_record_ids": ["rec_101", "rec_102"],
      "cluster_status": "confirmed",
      "identity_record_ids": ["identity_record_<deterministic-id>"],
      "produced_by_motor": "motor_006"
    }
  ],
  "ambiguity_flag": [],
  "resolution_conflict": []
}
```

## notes
Los registros ya deben estar normalizados antes de llegar a este motor; el motor no corrige nombres, no deduplica documentos y no crea una nueva entidad canonica global. Si el identificador fiscal difiere, si aparece un empate entre candidatos canonicos o si falta una referencia canonica compatible, la salida correcta es `distinct_entity` o `ambiguous` con evidencia trazable, no un merge forzado.
