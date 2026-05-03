# Design Done Criteria — Source Registry + Rights Engine

Motor ID: motor_008

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
why_it_exists:  Sin este motor no hay control serio de fuentes públicas, premium o restringidas.
key_inputs:     source declarations, license files, access agreements
key_outputs:    source_registration, rights_profile, access_class, refresh_schedule
key_objects:    SourceRecord, RightsProfile, AccessClass
what_not_to_do: No ingesta datos. No evalúa calidad. Solo registra metadatos de fuentes y derechos.
design_notes:   Depende de motor_001. Puede construirse temprano en paralelo con el pipeline de normalización.
-->

## criteria
- `master_concept_doc.md` states purpose, concrete operations, explicit non-responsibilities and rationale for a separate Source Registry + Rights Engine.
- `functional_contract.md` defines source declarations, license files and access agreements as inputs, and defines source registration, rights profile, access class and refresh schedule as outputs.
- `conceptual_schema.md` defines SourceRecord, RightsProfile and AccessClass with required fields and relationships.
- `operational_rules.md` includes deterministic rules, invariants and prohibited operations that exclude ingestion, quality evaluation and source payload transformation.
- `acceptance_tests.md` includes a happy path, at least two edge cases and explicit rejection criteria with named error signals.
- `failure_modes.md` lists primary degradation modes, anti-patterns and observable degradation signals for rights and source registry behavior.
- No documentation_base artifact contains open placeholder markers, generic filler text or unresolved field definitions.
