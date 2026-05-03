# Master Concept Document — TAD Preliminary Prioritization Engine

Motor ID: motor_033

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ordenar preliminarmente inference cases activos usando señales sintéticas del motor_032.
why_it_exists:  Cuando hay múltiples inference cases activos compitiendo por recursos, se necesita una señal preliminar de orden de atención trazable y no arbitraria.
key_inputs:     synthetic_ml_support_register (motor_032), inference_cases (motor_013), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    preliminary_priority_register, ranking_basis, rank_uncertainty_record
key_objects:    PreliminaryPriorityRegister, RankingBasis, RankUncertaintyRecord
what_not_to_do: No puede ser TAD final. No puede usarse como evidencia para cerrar inference cases. Siempre requiere revisión con evidencia real.
design_notes:   Output es preliminary_priority_register, nunca TAD final. El ranking es exploratorio.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true, rank_is_preliminary=true

All sections below are completed with concrete content for this motor.
-->

## purpose
Este motor ordena preliminarmente inference cases activos usando señales sintéticas ya etiquetadas por el motor_032. Produce un registro de prioridad exploratoria que ayuda a decidir dónde mirar primero cuando varios casos compiten por atención analítica. El resultado es una señal subordinada, trazable y no evidentiary; no cambia el estado epistémico de ningún claim ni sustituye evidencia real.

## what_it_does
- Recibe `synthetic_ml_support_register` desde motor_032 con `synthetic_support_flag=true` y `non_evidentiary_flag=true`.
- Recibe `inference_cases` activos desde motor_013 y limita el ranking a casos abiertos y procesables.
- Recibe `phase_contracts` desde motor_001 para respetar límites de fase, autoridad y handoffs permitidos.
- Recibe `version_records` desde motor_002 para registrar lineage, versión de insumos y reconstruibilidad del ranking.
- Valida que cada señal sintética esté explícitamente marcada como soporte preliminar y no evidentiary.
- Construye `ranking_basis` con las señales usadas, pesos declarados, referencias a insumos y razones de ordenamiento.
- Calcula un orden preliminar de atención y lo registra en `preliminary_priority_register`.
- Registra `rank_uncertainty_record` cuando hay señales incompletas, empates, sensibilidad alta o diferencias débiles entre casos.
- Emite todos sus outputs con `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `rank_is_preliminary=true`, `source_problem_ref`, `expert_spec_ref`, `intended_use=preliminary_support`, `domain_validity_limits` y `limitations_note`.

## what_it_does_not_do
- No produce TAD final ni declara una prioridad definitiva de decisión.
- No usa señales sintéticas como evidencia para cerrar inference cases.
- No valida claims contra datos de sitio, Validation Data Bridge ni Verification Bridge.
- No modifica `inference_cases`, `phase_contracts`, `version_records` ni outputs del motor_032.
- No promueve `synthetic_support` a `validation_data`, `field_evidence` ni `decision_grade`.
- No asigna recursos de ejecución por sí mismo; solo entrega un pre-filtro revisable.
- No oculta incertidumbre, empates ni falta de evidencia real para forzar un ranking limpio.

## why_it_exists
Existe como motor separado porque la priorización preliminar es una operación distinta de generar soporte sintético, gestionar inference cases o cerrar decisiones. Su salida es `preliminary_priority_register`, nunca TAD final, y permite orientar el esfuerzo analítico sin contaminar la cadena evidentiary ni convertir el ranking exploratorio en prueba.
