# Acceptance Tests — Synthetic Data Generation Engine

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

Las secciones siguientes contienen pruebas de aceptacion conceptuales para este motor.
-->

## happy_path
Input: `expert_problem_spec.spec_id="eps-030-demo-001"`, `status="approved"`, `source_problem_ref="inf-case-118"`, `problem_class="classification_binary"`, dos variables numericas con rangos cerrados, una variable categorica con tres valores permitidos, `ambiguity_register=[]`, y `version_records` con `generator_version="0.1.0"`. Accion: el motor construye `parameter_set={"sample_size": 1000, "scenario": "baseline", "seed": 4142}` y ejecuta la generacion determinista. Output esperado: se emiten `synthetic_generation_run`, `synthetic_dataset` y `generation_manifest` con el mismo `run_id`, `expert_spec_ref="eps-030-demo-001"`, `source_problem_ref="inf-case-118"`, `generator_version="0.1.0"`, `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `intended_use="exploration"` y registros que respetan los rangos y categorias del spec.

## edge_cases
- Minimum viable run: un spec aprobado solicita `sample_size=1` con una variable booleana y una restriccion simple. Comportamiento correcto: el motor produce un dataset de una fila, conserva todos los metadatos obligatorios y no degrada el manifiesto por bajo volumen.
- Multiple scenarios: un spec aprobado declara escenarios `baseline` y `stress` con rangos distintos para el mismo parametro. Comportamiento correcto: el motor registra los escenarios dentro del `parameter_set`, separa los registros o particiones por escenario y documenta en el manifest las restricciones aplicadas a cada uno.
- Tight parameter bounds: un spec aprobado contiene una variable numerica con rango cerrado donde `min=max`. Comportamiento correcto: el motor genera el valor constante, lo documenta como restriccion aplicada y no lo interpreta como error si el spec lo declara explicitamente.

## rejection_criteria
- Si `expert_problem_spec.status="draft"`, el motor rechaza el input con error `SPEC_NOT_APPROVED` y no emite outputs parciales.
- Si `ambiguity_register` contiene un item no resuelto con `impact_if_unresolved="critical"`, el motor rechaza el input con error `CRITICAL_AMBIGUITY_UNRESOLVED`.
- Si `version_records` no permite resolver `generator_version`, el motor rechaza el input con error `GENERATOR_VERSION_UNRESOLVED`.
- Si una variable declarada carece de tipo, dominio o rango verificable, el motor rechaza el input con error `INVALID_PARAMETER_CONSTRAINT`.
