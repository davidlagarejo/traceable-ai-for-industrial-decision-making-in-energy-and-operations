# Master Concept Document — Synthetic Data Generation Engine

Motor ID: motor_030

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Generar datasets sintéticos condicionados por expert_problem_spec aprobado.
why_it_exists:  El framework necesita datos para ML exploratoria sin comprometer la separación entre evidencia real y soporte sintético.
key_inputs:     expert_problem_spec (motor_029), version_records (motor_002)
key_outputs:    synthetic_generation_run, synthetic_dataset, generation_manifest
key_objects:    SyntheticGenerationRun, SyntheticDataset, GenerationManifest
what_not_to_do: No puede citarse como evidencia de campo. No sustituye Validation Data Bridge.
design_notes:   Todo output lleva synthetic_data_flag=true y non_evidentiary_flag=true. No puede ejecutarse sobre specs en draft o con ambiguity_register crítico.
epistemic_flags: synthetic_data_flag=true, non_evidentiary_flag=true

Las secciones siguientes contienen la definicion conceptual cerrada para este motor.
-->

## purpose
El Synthetic Data Generation Engine genera datasets sinteticos condicionados por un `expert_problem_spec` aprobado por motor_029. Su funcion es convertir restricciones, variables, rangos, supuestos y escenarios del spec en registros sinteticos reproducibles para exploracion analitica posterior. Todo output producido por este motor declara `synthetic_data_flag=true` y `non_evidentiary_flag=true`, por lo que queda separado de evidencia de campo y de datos reales de validacion.

## what_it_does
- Recibe un `expert_problem_spec` aprobado desde motor_029 y los `version_records` aplicables desde motor_002.
- Verifica que el spec no este en estado `draft` y que su `ambiguity_register` no contenga items criticos sin resolver.
- Extrae variables, dominios validos, restricciones de parametros, escenarios y limites declarados en el spec.
- Construye un `parameter_set` explicito para el run, incluyendo semilla, version del generador, tamano objetivo y escenarios incluidos.
- Genera un `synthetic_dataset` reproducible que respeta las restricciones declaradas por el spec aprobado.
- Registra un `synthetic_generation_run` con lineage hacia `expert_problem_spec.spec_id`, `source_problem_ref`, version del generador y version records usados.
- Produce un `generation_manifest` que documenta parametros, limites de validez, notas de limitacion y banderas epistemicas obligatorias.

## what_it_does_not_do
- No puede citarse como evidencia de campo ni producir objetos con nivel `field_evidence` o `validation_data`.
- No sustituye Validation Data Bridge ni Verification Bridge.
- No formaliza problemas expertos; consume `expert_problem_spec` de motor_029 como contrato de entrada.
- No entrena, compara ni evalua modelos de ML; esa responsabilidad pertenece al motor_031.
- No integra soporte sintetico en Decision Core ni eleva claims; esa responsabilidad pertenece a motores posteriores.
- No corrige silenciosamente ambiguedades del spec ni inventa parametros ausentes para cerrar huecos del contrato.

## why_it_exists
Existe como motor separado porque la generacion de datos sinteticos necesita un limite epistemico propio entre la especificacion experta y la experimentacion ML. El framework requiere datos para exploracion sin contaminar la cadena evidentiary: por eso este motor solo opera sobre specs aprobados, rechaza ambiguedades criticas y etiqueta todo output con `synthetic_data_flag=true` y `non_evidentiary_flag=true`.
