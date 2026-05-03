# Operational Rules — Synthetic Data Generation Engine

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

Las secciones siguientes contienen las reglas operativas cerradas para este motor.
-->

## rules
1. El motor solo puede ejecutarse cuando `expert_problem_spec.status=approved`.
2. El motor debe rechazar cualquier spec con `ambiguity_register` critico no resuelto.
3. Cada run debe declarar `run_id`, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `parameter_set` y `generation_seed` antes de generar registros.
4. La generacion debe ser reproducible: mismo `expert_spec_ref`, `generator_version`, `parameter_set` y `generation_seed` producen el mismo `synthetic_dataset`.
5. Todo output del motor debe incluir `synthetic_data_flag=true` y `non_evidentiary_flag=true`.
6. Todo output debe incluir `intended_use`, `domain_validity_limits` y `limitations_note` antes de registrarse.
7. El dataset emitido debe respetar tipos, rangos, cardinalidades y restricciones declaradas en el spec aprobado.
8. Cualquier valor fuera de contrato debe producir rechazo estructurado; el motor no corrige silenciosamente parametros ni registros.

## invariants
- `expert_spec_ref` siempre corresponde al `spec_id` de un `expert_problem_spec` aprobado.
- `source_problem_ref` nunca es nulo y se conserva igual en `synthetic_generation_run`, `synthetic_dataset` y `generation_manifest`.
- `generator_version` siempre proviene de `version_records` y queda registrado en todos los outputs.
- `parameter_set` es inmutable una vez iniciado el run y queda repetido o referenciado en todos los outputs.
- `synthetic_data_flag` permanece en `true` para todos los outputs del motor.
- `non_evidentiary_flag` permanece en `true` para todos los outputs del motor.
- Ningun output de este motor cambia de nivel epistemico ni puede registrarse como evidencia real.

## forbidden_operations
- Citar o registrar un `synthetic_generation_run` o `synthetic_dataset` como evidencia de campo.
- Sustituir Validation Data Bridge con datos sinteticos.
- Sustituir Verification Bridge con datos sinteticos.
- Ejecutarse sobre specs en `draft`, specs sin revision aprobada o specs con ambiguedad critica no resuelta.
- Promover `synthetic_dataset` a `validation_data`, `field_evidence` o cualquier nivel evidentiary superior.
- Entrenar modelos, evaluar metricas ML o seleccionar modelos.
- Integrar resultados en Decision Core o cerrar inference cases.
- Inferir parametros ausentes usando conveniencia narrativa o prompts no gobernados.
