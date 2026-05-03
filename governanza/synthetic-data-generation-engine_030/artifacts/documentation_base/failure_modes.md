# Failure Modes — Synthetic Data Generation Engine

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

Las secciones siguientes contienen los failure modes conceptuales para este motor.
-->

## failure_modes_list
- `SPEC_STATUS_BYPASS`: el motor genera datos desde un spec en `draft` o sin aprobacion; sintoma observable: outputs con `expert_spec_ref` valido pero sin evidencia de revision aprobada.
- `CRITICAL_AMBIGUITY_LEAK`: una ambiguedad critica no resuelta entra al `parameter_set`; sintoma observable: campos generados con reglas contradictorias o restricciones omitidas en el manifest.
- `EPISTEMIC_FLAG_MISSING`: algun output no incluye `synthetic_data_flag=true` o `non_evidentiary_flag=true`; sintoma observable: el objeto no puede distinguirse mecanicamente de datos evidentiary.
- `NON_REPRODUCIBLE_RUN`: mismo spec, version, seed y parametros producen datasets distintos; sintoma observable: hashes o conteos de registros cambian entre ejecuciones equivalentes.
- `CONSTRAINT_DRIFT`: los registros generados violan rangos, categorias o cardinalidades del spec; sintoma observable: quality checks del manifest reportan valores fuera de contrato.

## anti_patterns
- Usar el dataset sintetico como prueba de que el fenomeno real existe o es predecible.
- Rellenar parametros ausentes con intuicion del operador para poder generar datos sin reabrir motor_029.
- Mezclar generacion de datos con entrenamiento o seleccion de modelos dentro del mismo motor.
- Eliminar o simplificar `limitations_note` para que el output parezca mas fuerte epistemicamente.

## degradation_signals
- Aumento de runs rechazados por `INVALID_PARAMETER_CONSTRAINT`, lo que indica specs de entrada insuficientemente formales.
- Datasets emitidos con `record_count` distinto al declarado en `parameter_set` sin explicacion en `quality_checks`.
- Repeticion de `parameter_set` identico con hashes de dataset distintos para el mismo `generation_seed`.
- Manifest con `constraints_applied` vacio cuando el spec declara variables o rangos obligatorios.
- Outputs downstream que omiten `limitations_note` o tratan `synthetic_dataset` como `validation_data`.
