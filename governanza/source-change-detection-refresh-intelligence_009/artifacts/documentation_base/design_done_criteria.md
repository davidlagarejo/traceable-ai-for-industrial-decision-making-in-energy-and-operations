# Design Done Criteria — Source Change Detection / Refresh Intelligence

Motor ID: motor_009

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar cambios de fuente, metodología, estructura, disponibilidad y prioridad de recaptura.
why_it_exists:  Sin este motor los datasets quedan stale sin que el sistema lo sepa.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), version_history (motor_002)
key_outputs:    change_detection_event, refresh_priority, staleness_signal
key_objects:    ChangeEvent, RefreshPriority, StalenessRecord
what_not_to_do: No descarga datos. No decide qué hacer con cambios. Solo detecta y señaliza.
design_notes:   Depende de motor_008, motor_004, motor_002.

All documentation-base sections are filled for gate verification.
-->

## criteria
- `master_concept_doc.md` define proposito, acciones, limites y razon de existencia sin marcadores abiertos.
- `functional_contract.md` lista los tres inputs autorizados (`source_registry`, `ingestion_records`, `version_history`) y los tres outputs autorizados (`change_detection_event`, `refresh_priority`, `staleness_signal`).
- `conceptual_schema.md` define `ChangeEvent`, `RefreshPriority` y `StalenessRecord` con relaciones y campos minimos.
- `operational_rules.md` prohibe explicitamente descarga, recaptura, decision final, normalizacion, deduplicacion y mutacion de registros upstream.
- `acceptance_tests.md` cubre happy path, casos limite de fresh state, acceso bloqueado y fingerprint distinto, mas criterios de rechazo estructurados.
- `failure_modes.md` identifica degradacion por drift no detectado, escalamiento falso, perdida de lineage, fallo silencioso de disponibilidad y scope creep.
- Todos los artefactos de `documentation_base` tienen mas de 500 bytes y no contienen marcadores abiertos.
- La documentacion deja claro que motor_009 solo detecta y senaliza cambios con evidencia trazable, sin invadir motor_008, motor_004 ni motor_002.
