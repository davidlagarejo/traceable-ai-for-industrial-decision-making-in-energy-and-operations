# Test Spec — Synthetic Data Generation Engine

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

All placeholder sections in this test spec have been filled with concrete test content.
-->

## happy_path
Input minimo valido: `expert_problem_spec` con `spec_id="eps-030-demo-001"`, `status="approved"`, `handoff_allowed=true`, `source_problem_ref="inf-case-118"`, `problem_class="classification_binary"`, `domain_validity_limits="Solo valido para exploracion sintetica del caso inf-case-118"`, `review_status="approved"`, `ambiguity_register=[]`, variables `temperature_c` tipo `number` rango `[15.0, 45.0]`, `pressure_bar` tipo `number` rango `[1.0, 3.5]`, y `alarm_state` tipo `category` con valores `["normal", "warning", "critical"]`. `version_records` incluye `{"version_id":"vr-gen-030-001","component":"synthetic_generator","status":"current","generator_version":"0.1.0"}`. `parameter_set={"sample_size":1000,"scenario":"baseline","sampling_strategy":"deterministic_seeded","seed":4142}`.

Resultado esperado: el motor emite `synthetic_generation_run`, `synthetic_dataset` y `generation_manifest`. Los tres outputs comparten `run_id`, `expert_spec_ref="eps-030-demo-001"`, `source_problem_ref="inf-case-118"`, `generator_version="0.1.0"` y el mismo `parameter_set`. `synthetic_generation_run.status="generated"`, `rejection_code=null`, `generation_seed=4142`, `synthetic_dataset.record_count=1000`, `synthetic_dataset.records` contiene solo valores dentro de los rangos y categorias declarados, y `generation_manifest.constraints_applied` documenta las tres restricciones del spec. En los tres outputs `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `intended_use="exploration"`, `domain_validity_limits` no esta vacio y `limitations_note` declara que el dataset es sintetico, no evidentiary y no sustituye Validation Data Bridge ni Verification Bridge.

## sparse_case
Input sparse valido: `expert_problem_spec` con `spec_id="eps-030-sparse-001"`, `status="approved"`, `handoff_allowed=true`, `source_problem_ref="inf-case-119"`, `problem_class="regression_continuous"`, una sola variable `risk_score` tipo `number` rango `[0.0, 1.0]`, `ambiguity_register=[]`, revision aprobada y `domain_validity_limits="Escenario sintetico unico para exploracion"`. El spec no declara escenarios multiples, no declara particiones, no incluye overrides opcionales y no incluye columnas auxiliares. `version_records` resuelve `generator_version="0.1.0"`. `parameter_set={"sample_size":1,"sampling_strategy":"deterministic_seeded","seed":7}`.

Comportamiento esperado: el motor acepta el input porque los campos obligatorios estan completos. `SyntheticGenerationRun.scenario_refs=[]` para reflejar el escenario implicito unico, `SyntheticDataset.partition_refs=[]`, `SyntheticDataset.scenario_column=null`, `SyntheticDataset.record_count=1` y `GenerationManifest.scenario_summary` registra un unico escenario implicito sin crear errores fatales. El registro generado contiene `risk_score` dentro de `[0.0, 1.0]`; los tres outputs mantienen `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `source_problem_ref="inf-case-119"`, `expert_spec_ref="eps-030-sparse-001"`, `generator_version="0.1.0"`, `parameter_set`, `intended_use="exploration"`, `domain_validity_limits` y `limitations_note`.

## malformed_input
Caso 1, spec no aprobado: si `expert_problem_spec.status="draft"` o `handoff_allowed=false`, el motor debe rechazar antes de generar registros. Resultado esperado: `synthetic_generation_run.status="rejected"`, `rejection_code="SPEC_NOT_APPROVED"` y no se emite `synthetic_dataset` utilizable ni `generation_manifest` de exito.

Caso 2, ambiguedad critica: si `ambiguity_register=[{"ambiguity_id":"amb-17","resolved":false,"impact_if_unresolved":"critical"}]`, el motor debe rechazar con `rejection_code="CRITICAL_AMBIGUITY_UNRESOLVED"` y preservar `expert_spec_ref` y `source_problem_ref` en el registro de rechazo.

Caso 3, version de generador irresoluble: si `version_records=[]` o no existe un record vigente para `synthetic_generator`, el motor debe rechazar con `rejection_code="GENERATOR_VERSION_UNRESOLVED"` y no debe inventar `generator_version`.

Caso 4, tipo o restriccion invalida: si `parameter_set.sample_size="1000"` como string, `generation_seed="abc"`, una variable numerica carece de rango verificable, o una categoria no declara valores permitidos, el motor debe rechazar con `rejection_code="INVALID_PARAMETER_CONSTRAINT"`. El motor no debe convertir silenciosamente tipos, inferir rangos ni completar dominios faltantes.

## edge_cases
- Reproducibilidad determinista: ejecutar dos veces con el mismo `expert_spec_ref`, `source_problem_ref`, `version_record_refs`, `generator_version="0.1.0"`, `parameter_set` y `generation_seed=4142` debe producir los mismos `run_id`, `dataset_id`, `manifest_id`, `dataset_hash`, `reproducibility_fingerprint` y registros normalizados. Cambios solo en timestamps fuera del hash no deben alterar hashes materiales.
- Limite numerico cerrado: si una variable `calibration_factor` tipo `number` declara `min=1.25` y `max=1.25`, el motor debe generar siempre `1.25`, registrar la restriccion como aplicada y no rechazar el spec si el rango cerrado fue declarado explicitamente.
- Escenarios multiples: si el spec aprobado declara escenarios `baseline` y `stress`, el motor debe registrar ambos en `SyntheticGenerationRun.scenario_refs`, reflejarlos en `parameter_set`, separar registros por `scenario_column` o `partition_refs`, y documentar en `GenerationManifest.scenario_summary` las restricciones aplicadas por escenario. Ningun dataset del manifest puede pertenecer a otro `run_id`.
- Proteccion epistemica: si cualquier output candidato omite `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `intended_use="exploration"`, `domain_validity_limits` o `limitations_note`, el motor debe tratar el output como invalido y bloquear el registro. Un output incompleto no puede degradarse a warning ni enviarse a `motor_031`.
- Drift de restricciones: si un registro generado contiene `temperature_c=60.0` cuando el spec fija `[15.0,45.0]`, o `alarm_state="unknown"` fuera de las categorias permitidas, el motor debe rechazar el dataset, reportar el fallo en `quality_checks` y no emitirlo como dataset utilizable.

## pass_criteria
El test pasa cuando, para inputs validos, existen exactamente los tres outputs esperados (`synthetic_generation_run`, `synthetic_dataset`, `generation_manifest`) con IDs no vacios, referencias cruzadas consistentes, `produced_by_motor="motor_030"`, `source_ref` igual al `source_problem_ref`, `generator_version` resuelto desde `version_records`, `parameter_set` materialmente identico en los tres objetos, `record_count` igual al tamano solicitado, `quality_checks` sin violaciones de tipo/rango/categoria, hashes deterministas reproducibles y flags epistemicos completos (`synthetic_data_flag=true`, `non_evidentiary_flag=true`, `intended_use="exploration"`, `domain_validity_limits` y `limitations_note` no vacios).

El test tambien pasa para inputs invalidos cuando el motor rechaza de forma estructurada con el `rejection_code` esperado, preserva las referencias disponibles para auditoria, no corrige silenciosamente el input y no emite `synthetic_dataset` utilizable.

## fail_criteria
El test falla si un input valido no produce alguno de los tres outputs requeridos, si los outputs no comparten `run_id`, `expert_spec_ref`, `source_problem_ref`, `generator_version` y `parameter_set`, si falta cualquier flag epistemico obligatorio, si `intended_use` no es `exploration`, si `limitations_note` permite uso evidentiary, si `record_count` no coincide con los registros o particiones, si un registro viola tipos, rangos o categorias del spec, o si dos ejecuciones equivalentes producen hashes materiales distintos.

El test tambien falla si un input invalido genera registros parciales utilizables, si un spec en `draft` no produce `SPEC_NOT_APPROVED`, si una ambiguedad critica no resuelta no produce `CRITICAL_AMBIGUITY_UNRESOLVED`, si falta `generator_version` y el motor inventa una version, o si el motor convierte tipos, infiere dominios o completa restricciones ausentes sin rechazo estructurado.
