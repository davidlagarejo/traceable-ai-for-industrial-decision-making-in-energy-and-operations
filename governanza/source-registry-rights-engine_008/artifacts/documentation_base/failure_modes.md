# Failure Modes — Source Registry + Rights Engine

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

## failure_modes_list
- RIGHTS_AMBIGUITY_COLLAPSE: ambiguous license or agreement language is emitted as allowed usage, making restricted sources look open.
- SOURCE_ID_COLLISION: two distinct sources are registered under the same `source_id`, causing downstream ingestion or refresh logic to mix rights contexts.
- ACCESS_CLASS_DRIFT: manual updates change access class without matching change in rights evidence, producing a class that cannot be justified from documents.
- MISSING_REFRESH_DISCIPLINE: registered sources lack periodicity or manual review condition, leaving rights and access metadata stale.
- DOCUMENT_PROVENANCE_LOSS: a `RightsProfile` remains present but no longer links to the license file or access agreement that justified it.

## anti_patterns
- Treating a successful source registration as permission to ingest or redistribute the source content.
- Using this motor to score source reliability, quality, truthfulness or analytic fitness.
- Registering licenses from summarized notes without preserving the original document reference.
- Collapsing all non-public sources into a generic restricted class without recording the specific contractual condition.
- Updating access class by hand without recording version, reason and evidence reference.

## degradation_signals
- Rising count of `RightsProfile` objects with empty `prohibited_uses`, empty `restriction_notes` or generic license labels.
- Any output object whose `source_id` has no corresponding current SourceRecord.
- Access classes changed without a matching new `document_ref`, `observed_at` or revision note.
- More than one current `RightsProfile` for a single `source_id`.
- Increasing share of sources with `refresh_schedule` set to manual review but no manual review condition.
- Logs showing repeated `RIGHTS_CONFLICT` or `MISSING_RIGHTS_EVIDENCE` for the same source without resolution.
