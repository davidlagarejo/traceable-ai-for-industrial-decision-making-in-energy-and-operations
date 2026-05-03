# Functional Contract — Synthetic Data Generation Engine

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

Las secciones siguientes contienen el contrato funcional cerrado para este motor.
-->

## inputs
- `expert_problem_spec`: object — producido por motor_029; debe incluir `spec_id`, `status`, `source_problem_ref`, `problem_class`, variables declaradas, restricciones de parametros, escenarios permitidos, `ambiguity_register`, `domain_validity_limits` y revision experta aprobada.
- `version_records`: object array — producido por motor_002; debe identificar `generator_version`, reglas de versionado aplicables, referencias de lineage y estado vigente de los artefactos usados para ejecutar el run.

## outputs
- `synthetic_generation_run`: object — registro del run para lineage interno y consumo por motor_031; contiene `run_id`, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `parameter_set`, timestamps, semilla y estado del run.
- `synthetic_dataset`: object — dataset sintetico estructurado para motor_031; contiene `dataset_id`, `run_id`, filas o particiones generadas, schema de columnas, etiquetas epistemicas y limites de uso.
- `generation_manifest`: object — manifiesto auditable para gobernanza y revision de conformidad; contiene parametros exactos, version records usados, restricciones aplicadas, resumen de calidad, `domain_validity_limits` y `limitations_note`.

## limits
- No acepta `expert_problem_spec` con `status=draft`, sin `spec_id`, sin `source_problem_ref` o sin revision aprobada.
- No acepta un `ambiguity_register` con items no resueltos cuyo impacto sea `critical`.
- No acepta restricciones de parametros sin dominio, tipo o rango verificable.
- No produce evidencia de campo, `validation_data`, `field_evidence`, objetos de Verification Bridge ni conclusiones decisionales.
- No produce modelos de ML, metricas de performance, rankings de variables ni `capability_demonstration_report`.
- No emite ningun output sin `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `source_problem_ref`, `expert_spec_ref`, `generator_version`, `parameter_set`, `intended_use`, `domain_validity_limits` y `limitations_note`.

## validations
- Rechaza el input si `expert_problem_spec.status` no es `approved`.
- Rechaza el input si `expert_problem_spec.ambiguity_register` contiene cualquier item no resuelto con `impact_if_unresolved=critical`.
- Rechaza el input si `version_records` no contiene una version vigente del generador o si `generator_version` no puede resolverse.
- Rechaza el input si variables, restricciones o escenarios del spec son insuficientes para construir un `parameter_set` determinista.
- Antes de emitir output, verifica que cada registro sintetico respeta tipos, rangos y restricciones declaradas por el spec aprobado.
- Antes de emitir output, verifica que los tres outputs comparten el mismo `run_id`, `expert_spec_ref`, `source_problem_ref`, `generator_version` y `parameter_set`.
- Antes de registrar output, verifica que `synthetic_data_flag=true` y `non_evidentiary_flag=true` aparecen en `synthetic_generation_run`, `synthetic_dataset` y `generation_manifest`.
- Antes de registrar output, verifica que `intended_use` pertenece a `exploration`, `capability_demo` o `preliminary_support`; para este motor el valor normal es `exploration`.
