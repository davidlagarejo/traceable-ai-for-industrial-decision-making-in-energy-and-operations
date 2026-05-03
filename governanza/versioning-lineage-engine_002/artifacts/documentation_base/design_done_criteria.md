# Design Done Criteria — Versioning + Lineage Engine

Motor ID: motor_002

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
why_it_exists:  Sin versionado no hay rebuild, stale detection ni auditoría seria.
key_inputs:     object mutations, source references, transformation records
key_outputs:    version_record, lineage_graph, impact_set, rebuild_manifest
key_objects:    VersionRecord, LineageNode, ImpactEdge
what_not_to_do: No decide si un objeto es válido. Solo registra versiones y dependencias.
design_notes:   Depende de motor_001 (phase contracts anclan el contexto de versión).

Sections below are complete for Gate 1 review.
-->

## criteria
- All seven documentation_base artifacts exist, are over the minimum gate size, and contain no open placeholder markers checked by Gate 1.
- `functional_contract.md` declares concrete inputs, outputs, strict limits and validations for version_record, lineage_graph, impact_set and rebuild_manifest.
- `conceptual_schema.md` defines VersionRecord, LineageNode and ImpactEdge with required fields and relationships sufficient to derive a technical schema.
- `operational_rules.md` states append-only versioning, lineage acyclicity, phase contract anchoring and forbidden responsibility crossings.
- `acceptance_tests.md` includes a happy path, edge cases and explicit rejection criteria with structured error signals.
- `failure_modes.md` identifies lineage gaps, history rewrite risk, impact calculation errors and rebuild manifest degradation signals.
- The design explicitly states that this motor does not decide object validity, quality, identity resolution, refresh, re-evaluation or rebuild execution.
