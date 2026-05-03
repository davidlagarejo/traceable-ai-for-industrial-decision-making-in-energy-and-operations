# Master Concept Document — Source Change Detection / Refresh Intelligence

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

## purpose
Este motor detecta cambios relevantes en fuentes registradas comparando metadatos de fuente, registros de ingesta y version history. Identifica cambios de disponibilidad, metodología declarada, estructura observada, cadencia de actualización y señales de obsolescencia. Su salida es una señal trazable de cambio y prioridad de recaptura, no una acción de descarga ni una decisión operativa final.

## what_it_does
- Recibe `source_registry` desde motor_008 con `source_id`, derechos, clase de acceso, refresh schedule y metadatos declarados de fuente.
- Recibe `ingestion_records` desde motor_004 con resultados de captura previa, timestamps, disponibilidad observada, checksums, schema fingerprints y errores de acceso.
- Recibe `version_history` desde motor_002 con versiones anteriores, lineage y cambios registrados sobre objetos de fuente o datasets derivados.
- Compara el estado declarado de cada fuente con el último estado observado por ingesta y versionado.
- Clasifica eventos de cambio como disponibilidad, estructura, metodología, frecuencia, acceso o contenido fingerprint.
- Produce `change_detection_event` con evidencia mínima, timestamp, tipo de cambio, severidad y referencias de lineage.
- Produce `refresh_priority` como recomendación estructurada de prioridad para recaptura.
- Produce `staleness_signal` cuando una fuente o dataset supera umbrales de antiguedad, cambio o inconsistencia.

## what_it_does_not_do
- No descarga datos ni ejecuta recapturas.
- No decide que hacer con los cambios detectados; solo emite señales estructuradas para consumidores posteriores.
- No modifica el `source_registry`, los `ingestion_records` ni el `version_history`.
- No normaliza contenido, no resuelve identidad, no elimina duplicados y no evalua calidad analitica del dato.
- No cambia derechos, licencias, permisos de uso ni clase de acceso de una fuente.
- No declara verdad epistemica sobre el contenido de la fuente; solo detecta diferencias operativas y trazables.

## why_it_exists
Este motor existe separado porque la deteccion de stale state requiere cruzar registro de fuente, ingesta y versionado sin invadir a ninguno de esos motores. Motor_008 sabe que fuente existe y bajo que reglas, motor_004 sabe que se observo durante ingesta, motor_002 preserva versiones y lineage; motor_009 convierte esa comparacion en senales de cambio y recaptura.
