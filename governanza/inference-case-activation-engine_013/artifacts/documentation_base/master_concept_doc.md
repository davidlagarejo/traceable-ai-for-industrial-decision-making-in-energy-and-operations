# Master Concept Document — Inference Case Activation Engine

Motor ID: motor_013

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
why_it_exists:  Separa selección de casos del análisis del Decision Core.
key_inputs:     facility_prior (motor_012), library_objects (motor_011), quality_records (motor_007)
key_outputs:    inference_case, activation_record, trigger_log
key_objects:    InferenceCase, ActivationRecord, TriggerCondition
what_not_to_do: No analiza los casos. No produce conclusiones. Solo activa y registra.
design_notes:   Crea los casos que alimentan al Decision Core. Sin este motor, motor_014 no tiene input.

Sections below completed for Gate 1 validation.
-->

## purpose
El Inference Case Activation Engine activa casos inferenciales gobernados a partir de un `facility_prior`, objetos curados de biblioteca y condiciones de disparo verificables. Su funcion es decidir, de forma determinista y trazable, que casos deben abrirse para analisis posterior. El motor produce el paquete minimo de activacion que el Decision Core necesita para trabajar, sin ejecutar el analisis inferencial ni emitir conclusiones.

## what_it_does
- Recibe `facility_prior` desde `motor_012` con identificadores, contexto de facility, version y lineage.
- Recibe `library_objects` desde `motor_011` y selecciona solo los objetos elegibles para activacion segun tipo, version, tags y scope declarado.
- Recibe `quality_records` desde `motor_007` y bloquea cualquier prior, bundle u objeto de biblioteca que no sea apto para uso inferencial.
- Evalua `TriggerCondition` contra campos presentes en el prior, bundles referenciados y metadatos de calidad.
- Crea un `InferenceCase` por cada condicion gobernada que cumple los criterios de activacion.
- Registra un `ActivationRecord` por cada decision de activacion, incluyendo entradas usadas, reglas aplicadas, resultado y razon.
- Emite un `trigger_log` con todas las condiciones evaluadas, tanto activadas como no activadas, para auditoria y reconstruccion.

## what_it_does_not_do
- No analiza los casos activados.
- No produce conclusiones, inferencias finales, decisiones, tensiones, oportunidades ni gaps.
- No reescribe `facility_prior`, `library_objects` ni `quality_records`.
- No crea reglas de trigger nuevas fuera de la biblioteca o contrato vigente.
- No resuelve conflictos analiticos entre casos; solo registra que mas de un caso fue activado cuando corresponde.
- No reemplaza al Decision Core de `motor_014`; solo prepara su input gobernado.

## why_it_exists
Este motor existe para separar la seleccion gobernada de casos del analisis que realiza el Decision Core. Sin esta separacion, `motor_014` tendria que decidir que analizar y analizarlo en el mismo paso, mezclando responsabilidades y perdiendo trazabilidad sobre por que un caso fue abierto.
