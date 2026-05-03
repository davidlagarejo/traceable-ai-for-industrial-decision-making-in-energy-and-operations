# Master Concept Document — Decision Core / Inference Engine

Motor ID: motor_014

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
why_it_exists:  Es el corazón analítico de Fase 2.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001)
key_outputs:    inference_record, tension_record, gap_agenda, validation_agenda
key_objects:    InferenceRecord, Tension, ValidationAgenda
what_not_to_do: No produce reportes finales. No verifica claims. Solo infiere y registra con contratos explícitos.
design_notes:   Determinismo primero. La IA puede asistir pero no decide. Depende de motor_013 y motor_001.

Sections below define the completed documentation-base contract for this motor.
-->

## purpose
El Decision Core / Inference Engine recibe casos inferenciales activados y contratos de fase para producir registros analíticos estructurados de Fase 2. Su salida principal son inferencias registradas, tensiones, conflictos, oportunidades, gaps y una agenda explícita de validación. El motor no decide verdad final ni verifica claims; organiza el razonamiento permitido por contrato y deja trazabilidad completa de qué caso, evidencia y regla originaron cada salida.

## what_it_does
- Recibe `inference_cases` activados por `motor_013`.
- Recibe `phase_contracts` emitidos por `motor_001` y valida que autorizan los outputs de Fase 2.
- Rechaza casos que no tengan identificador estable, estado activado, referencias de evidencia o lineage mínimo.
- Evalúa reglas deterministas de inferencia sobre el contenido estructurado del caso.
- Registra un `inference_record` por cada caso procesado correctamente.
- Identifica tensiones, conflictos, oportunidades y gaps derivados del caso sin resolverlos por mutación silenciosa.
- Produce `tension_record` cuando existen señales incompatibles, insuficientes o analíticamente relevantes.
- Produce `gap_agenda` con vacíos de evidencia, datos o contrato que impiden endurecer la inferencia.
- Produce `validation_agenda` con rutas de validación requeridas para motores downstream.
- Conserva referencias a caso origen, contrato de fase, evidencia usada, reglas aplicadas y versión del motor.

## what_it_does_not_do
- No produce reportes finales, paquetes de reporte, vistas ejecutivas ni documentos renderizados.
- No verifica claims, no cierra hipótesis como verdaderas y no sustituye al Verification Bridge.
- No ingesta fuentes, no parsea documentos, no normaliza entidades y no evalúa calidad estructural de datos upstream.
- No activa casos inferenciales; esa responsabilidad pertenece a `motor_013`.
- No modifica `inference_cases`, `phase_contracts`, evidencia fuente ni contratos de fase.
- No usa IA como decisor soberano; cualquier asistencia semántica queda subordinada a reglas, contratos y trazabilidad explícita.
- No promueve soporte sintético, conocimiento de biblioteca o inferencias preliminares a evidencia de campo.

## why_it_exists
Existe como motor separado porque Fase 2 necesita un núcleo analítico que transforme casos activados en registros inferenciales auditables sin mezclarse con activación, reporting o verificación. Su diseño preserva determinismo primero: `motor_013` decide qué casos entran, `motor_001` fija los límites permitidos, y `motor_014` solo infiere y registra dentro de esos contratos.
