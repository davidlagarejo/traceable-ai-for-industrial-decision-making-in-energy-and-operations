# Operational Rules — Source Change Detection / Refresh Intelligence

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

## rules
1. Cada comparacion debe estar anclada a un `source_id` existente en `source_registry`.
2. Cada `change_detection_event` debe conservar referencias a los inputs que justifican el cambio, incluyendo al menos una referencia de ingesta o versionado.
3. Un cambio de estructura solo puede emitirse cuando `expected_schema_signature` y `observed_schema_signature` difieren o cuando version_history registra cambio estructural equivalente.
4. Un cambio de disponibilidad solo puede emitirse cuando `availability_status` o `access_error_code` cambia respecto del estado anterior registrado.
5. Una prioridad de recaptura solo puede calcularse desde reglas deterministas basadas en severidad, edad, refresh interval, disponibilidad y evidencia versionada.
6. Si la evidencia es insuficiente, el motor debe rechazar el caso con error estructurado y no emitir evento parcial.
7. Los outputs deben ser reproducibles a partir de los mismos inputs ordenados por `source_id`, timestamp y version lineage.

## invariants
- `source_id` nunca es nulo en inputs aceptados ni outputs emitidos.
- `event_id`, `priority_id` y `staleness_id` son estables para una misma combinacion de fuente, tipo de cambio, timestamp de deteccion y evidencia refs.
- `lineage_refs` se preserva en todos los outputs derivados de version_history.
- Ningun output reemplaza ni muta registros de motor_002, motor_004 o motor_008.
- Cada output conserva `detected_at` o `calculated_at` como timestamp explicito de produccion.
- La ausencia de evidencia se expresa como rechazo, no como inferencia silenciosa.

## forbidden_operations
- Descargar, scrapear, consultar APIs externas o recapturar fuentes.
- Decidir acciones operativas finales sobre cambios detectados.
- Modificar `source_registry`, rights profiles, access class, refresh schedule o permisos.
- Modificar, corregir o reescribir ingestion records y version history.
- Normalizar contenido, resolver identidad, deduplicar documentos o evaluar fitness analitico.
- Crear nuevas fuentes, nuevos motores, nuevas fases o nuevos contratos de fase.
- Ocultar cambios de evidencia mediante defaults silenciosos o mutacion implicita.
