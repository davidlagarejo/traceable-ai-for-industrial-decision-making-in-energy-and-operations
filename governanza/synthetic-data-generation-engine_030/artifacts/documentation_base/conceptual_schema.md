# Conceptual Schema — Synthetic Data Generation Engine

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

Las secciones siguientes contienen el schema conceptual cerrado para este motor.
-->

## entities
- `SyntheticGenerationRun`: registro auditable de una ejecucion determinista del generador condicionada por un `expert_problem_spec` aprobado.
- `SyntheticDataset`: coleccion de registros sinteticos producidos por un run, con schema de columnas, filas generadas, particiones opcionales y etiquetas epistemicas completas.
- `GenerationManifest`: manifiesto de provenance que explica que parametros, versiones, restricciones, escenarios y limites produjeron el dataset.

## relationships
- `expert_problem_spec` -> `SyntheticGenerationRun` (un spec aprobado puede originar multiples runs versionados con parametros distintos).
- `version_records` -> `SyntheticGenerationRun` (cada run referencia las versiones exactas usadas para reconstruccion).
- `SyntheticGenerationRun` -> `SyntheticDataset` (un run produce uno o mas datasets sinteticos bajo el mismo `run_id` y `parameter_set`).
- `SyntheticGenerationRun` -> `GenerationManifest` (cada run tiene un manifiesto obligatorio que documenta provenance y limites).
- `GenerationManifest` -> `SyntheticDataset` (el manifiesto describe el dataset que puede ser consumido por motor_031 y sus restricciones de uso).

## key_fields
`SyntheticGenerationRun`
- `run_id`: string
- `expert_spec_ref`: string
- `source_problem_ref`: string
- `generator_version`: string
- `parameter_set`: object
- `generation_seed`: integer
- `synthetic_data_flag`: boolean, fixed `true`
- `non_evidentiary_flag`: boolean, fixed `true`

`SyntheticDataset`
- `dataset_id`: string
- `run_id`: string
- `schema`: object
- `records`: array
- `record_count`: integer
- `intended_use`: enum string, normally `exploration`
- `domain_validity_limits`: string
- `limitations_note`: string
- `synthetic_data_flag`: boolean, fixed `true`
- `non_evidentiary_flag`: boolean, fixed `true`

`GenerationManifest`
- `manifest_id`: string
- `run_id`: string
- `expert_spec_ref`: string
- `source_problem_ref`: string
- `generator_version`: string
- `version_record_refs`: array
- `parameter_set`: object
- `constraints_applied`: array
- `quality_checks`: object
- `limitations_note`: string
- `synthetic_data_flag`: boolean, fixed `true`
- `non_evidentiary_flag`: boolean, fixed `true`
