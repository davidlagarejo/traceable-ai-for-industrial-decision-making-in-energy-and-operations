# Failure Modes — Source Change Detection / Refresh Intelligence

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

## failure_modes_list
- `UNDETECTED_SOURCE_DRIFT`: la fuente cambia schema, metodologia o disponibilidad pero no se emite `change_detection_event`; sintoma observable: datasets downstream siguen marcados fresh aunque fingerprints o schema signatures divergen.
- `FALSE_REFRESH_ESCALATION`: el motor eleva `refresh_priority` sin evidencia suficiente; sintoma observable: prioridades altas aparecen sin `derived_from_event_ids` ni regla temporal clara.
- `LINEAGE_LOSS`: el output no conserva referencias a version_history o ingestion records; sintoma observable: eventos no pueden reconstruirse desde `evidence_refs` y `lineage_refs`.
- `SILENT_AVAILABILITY_FAILURE`: errores de acceso repetidos no generan cambio de disponibilidad; sintoma observable: `availability_status` degradado en ingesta pero ausencia de evento `access` o `availability`.
- `SCOPE_CREEP_RECAPTURE`: el motor intenta ejecutar descarga o remediacion; sintoma observable: artefactos raw nuevos o llamadas externas producidas por este motor.

## anti_patterns
- Usar este motor como scheduler de recaptura o downloader, mezclando deteccion con accion operativa.
- Calcular prioridad por intuicion o texto narrativo sin regla determinista basada en evidencia.
- Sobrescribir registros de ingesta o versionado para "arreglar" comparaciones.
- Tratar un cambio de fingerprint como interpretacion semantica del contenido sin pasar por motores de parsing, normalizacion o evaluacion.

## degradation_signals
- Aumento sostenido de eventos con `evidence_refs` vacio o con una sola referencia insuficiente.
- Proporcion de `refresh_priority.high` o `urgent` crece sin crecimiento equivalente en cambios observados de schema, acceso, disponibilidad o staleness.
- Fuentes con `age_days` mayor que el refresh interval siguen recibiendo `staleness_status = "fresh"`.
- Eventos repetidos para el mismo `source_id` y `change_type` con ids no estables ante los mismos inputs.
- Caida del conteo de eventos `access` mientras ingestion_records muestran errores de acceso crecientes.
- Aparicion de outputs sin `lineage_refs` o con referencias a motores no incluidos en el contrato de entrada.
