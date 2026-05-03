# Operational Rules — Source Registry + Rights Engine

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

## rules
1. Every registered source must have one stable `source_id` before any output is emitted.
2. Every `source_id` must map to one current `SourceRecord`, one current `RightsProfile` and one current `AccessClass`.
3. A source with ambiguous or missing usage rights must be classified as `restricted` or `blocked`, never as `public` or `premium`.
4. Every rights decision must cite at least one `license_files` or `access_agreements` reference with an observation timestamp.
5. Access class assignment must be deterministic from documented license terms, access agreement terms and declared source metadata.
6. Refresh scheduling must be explicit: each source receives a periodicity, a next review date or a manual review condition.
7. Updates must create a new registral version or revision note; existing rights metadata must not be silently overwritten.
8. Outputs must preserve the same `source_id` across `source_registration`, `rights_profile`, `access_class` and `refresh_schedule`.

## invariants
- `source_id` is never null in any emitted object.
- Provenance for license and access evidence is preserved before and after create or update operations.
- The motor emits no payload content from the source itself.
- The motor emits no quality, fitness, identity resolution or inference judgment.
- A rights profile without explicit permission cannot produce an unrestricted access class.
- The current registration state is reconstructible from source declaration, license references, access agreement references and version notes.

## forbidden_operations
- Ingesting data from registered sources.
- Downloading, scraping, parsing or storing raw source content as part of registration.
- Evaluating data quality, fitness, completeness, reliability or analytic truth.
- Normalizing source payload records or canonicalizing entities found inside source content.
- Resolving whether two real-world entities in source data are the same entity.
- Promoting ambiguous or undocumented rights into allowed usage.
- Mutating license, agreement or access metadata without traceable revision history.
- Producing downstream reports, inference records, validation records or quality scores.
