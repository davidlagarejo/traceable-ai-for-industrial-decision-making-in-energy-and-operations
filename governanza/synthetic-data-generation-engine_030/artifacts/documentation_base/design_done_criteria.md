# Design Done Criteria — Synthetic Data Generation Engine

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

Las secciones siguientes contienen criterios verificables de cierre del diseno.
-->

## criteria
- Los siete artefactos de `documentation_base` existen, tienen contenido sustantivo y no contienen marcadores abiertos.
- `functional_contract.md` declara `expert_problem_spec` y `version_records` como inputs, y `synthetic_generation_run`, `synthetic_dataset` y `generation_manifest` como outputs.
- `functional_contract.md` y `operational_rules.md` exigen `synthetic_data_flag=true` y `non_evidentiary_flag=true` para todos los outputs.
- `conceptual_schema.md` define `SyntheticGenerationRun`, `SyntheticDataset` y `GenerationManifest` con campos minimos para lineage, versionado, parametros y limites epistemicos.
- `operational_rules.md` prohibe el uso de outputs como evidencia de campo y prohibe sustituir Validation Data Bridge o Verification Bridge.
- `acceptance_tests.md` contiene happy path, edge cases y criterios de rechazo con senales de error explicitas.
- `failure_modes.md` enumera fallos de status bypass, fuga de ambiguedad critica, perdida de flags, no reproducibilidad y drift de restricciones.
