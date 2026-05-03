# Design Done Criteria — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.

Contenido completado para gate de documentation_base.
-->

## criteria
- `master_concept_doc.md` define proposito, acciones, limites y razon de existencia de `motor_006` sin marcadores abiertos.
- `functional_contract.md` lista inputs, outputs, limites y validaciones con tipos y fuentes o consumidores explicitos.
- `conceptual_schema.md` define `IdentityRecord`, `EntityCluster`, `ResolutionConflict`, `AmbiguityFlag` y sus campos minimos.
- `operational_rules.md` prohibe deduplicacion documental y exige preservar `record_id`, `source_ref`, `provenance_ref` y `rule_version`.
- `acceptance_tests.md` cubre un happy path, casos de empate o falta de entidad canonica y criterios de rechazo con senales de error explicitas.
- `failure_modes.md` documenta false merge, false split, colapso de ambigüedad, perdida de provenance y deriva de politica.
- La documentacion permite pasar a schema tecnico sin inventar inputs, outputs, objetos o responsabilidades adicionales.
