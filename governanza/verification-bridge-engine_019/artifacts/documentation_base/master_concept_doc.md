# Master Concept Document — Verification Bridge Engine

Motor ID: motor_019

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir claims y tensiones en rutas explícitas de endurecimiento de evidencia.
why_it_exists:  Sin este motor el sistema se queda en hipótesis y reporting, sin puente real a verificación.
key_inputs:     inference_records (motor_014), validation_data (motor_018), phase_contracts (motor_001)
key_outputs:    verification_path, hardening_agenda, evidence_gap_record
key_objects:    VerificationPath, HardeningAgenda, EvidenceGap
what_not_to_do: No cierra claims automáticamente. No puede ser reemplazado por synthetic_support.
design_notes:   Produce field_evidence level cuando completa verificación. Depende de motor_014, motor_018 y motor_001.

All placeholder markers in this file have been replaced with governed content.
-->

## purpose
Verification Bridge Engine convierte claims, tensiones y gaps inferenciales en rutas explícitas para endurecer evidencia. Recibe inference_records del Decision Core, validation_data real del Validation Data Bridge y phase_contracts vigentes para determinar qué pasos, evidencias y controles faltan antes de considerar una verificación como robusta. Su salida no es una decisión final sobre el claim, sino una estructura trazable que conecta hipótesis analíticas con evidencia de campo verificable.

## what_it_does
- Recibe inference_records emitidos por motor_014 y extrae claim_id, tension_id, confidence_state, evidentiary_basis y unresolved_gaps.
- Recibe validation_data de motor_018 y lo vincula solo si conserva provenance, lineage y referencia a datos reales estructurados.
- Consulta phase_contracts de motor_001 para confirmar que la ruta propuesta pertenece a una fase autorizada y usa outputs permitidos.
- Construye un verification_path por claim o tensión verificable, con pasos, dependencias, evidencia requerida, criterios de avance y criterios de bloqueo.
- Construye una hardening_agenda priorizada que ordena acciones de recolección, contraste, medición o revisión necesarias para fortalecer la evidencia.
- Registra evidence_gap_record cuando la evidencia disponible no alcanza el umbral requerido o cuando una tensión no tiene ruta verificable inmediata.
- Marca una ruta como elegible para nivel field_evidence solo cuando existe soporte real trazable y las validaciones contractuales están completas.

## what_it_does_not_do
- No cierra claims automáticamente ni convierte una ruta verificada en decisión terminal.
- No puede ser reemplazado por synthetic_support ni aceptar datos sintéticos como evidencia de verificación.
- No produce inference_records; esa responsabilidad pertenece al Decision Core / Inference Engine.
- No captura, parsea ni normaliza fuentes primarias; consume datos ya estructurados por motores upstream.
- No redefine phase_contracts, niveles de evidencia, taxonomías ni reglas de gobernanza.
- No ensambla reportes ni redacta output blocks visibles para stakeholders.

## why_it_exists
Existe como motor separado porque el salto entre inferencia analítica y verificación de campo requiere reglas propias, trazabilidad propia y objetos propios. Motor_014 produce claims y tensiones, motor_018 estructura validation_data real y motor_001 gobierna contratos de fase; motor_019 conecta esas piezas en rutas de endurecimiento de evidencia sin invadir la decisión final ni la adquisición de datos.
