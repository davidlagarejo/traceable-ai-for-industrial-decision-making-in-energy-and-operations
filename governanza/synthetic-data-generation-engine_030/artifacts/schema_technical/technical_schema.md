# Technical Schema — Synthetic Data Generation Engine

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

All open placeholders in this file have been resolved with concrete technical schema content.
-->

## entities
- `SyntheticGenerationRun`: registro tecnico, versionado e inmutable de una ejecucion determinista de `motor_030` sobre un `expert_problem_spec` aprobado. Vive en la etapa `schema_technical` como entidad persistente canonica del run y en `implementation` como objeto de control que valida entrada, parametros, semilla, lineage y estado de emision.
- `SyntheticDataset`: dataset sintetico producido por un `SyntheticGenerationRun`, con schema de columnas, registros o particiones generadas, conteos, hashes y etiquetas epistemicas completas. Vive en la etapa `schema_technical` como entidad persistente de salida consumible por `motor_031`; sus registros son no evidentiary y no pueden ser citados como datos reales.
- `GenerationManifest`: manifiesto auditable que explica como se produjo un `SyntheticDataset`: versiones usadas, `parameter_set`, restricciones aplicadas, escenarios, quality checks, limites de validez y notas de limitacion. Vive en la etapa `schema_technical` como entidad persistente de provenance y reconstruccion para gobernanza y conformance review.

## fields
`SyntheticGenerationRun`
- `run_id: string` (required) — identificador canonico estable del run de generacion.
- `record_id: string` (required) — identificador inmutable de almacenamiento para esta version persistida del run.
- `expert_spec_ref: string` (required) — referencia a `motor_029.ExpertProblemSpec.spec_id`; debe apuntar a un spec aprobado y elegible para handoff.
- `source_problem_ref: string` (required) — `inference_case_id` de origen preservado desde el `expert_problem_spec`.
- `generator_version: string` (required) — version semver del generador resuelta desde `version_records`.
- `version_record_refs: list[string]` (required) — referencias a `motor_002.VersionRecord.version_id` usadas para reconstruir input, reglas y generador.
- `parameter_set: object` (required) — parametros exactos del run, incluyendo `sample_size`, escenarios, estrategia de muestreo, semilla y overrides permitidos por el spec.
- `generation_seed: integer` (required) — semilla usada para garantizar reproducibilidad determinista.
- `scenario_refs: list[string]` (required) — escenarios del spec incluidos en el run; vacio solo cuando el spec declara un unico escenario implicito.
- `status: enum[prepared, generated, rejected]` (required) — estado tecnico del run; `rejected` no puede emitir dataset utilizable.
- `rejection_code: string | null` (required) — codigo estructurado de rechazo, por ejemplo `SPEC_NOT_APPROVED`, `CRITICAL_AMBIGUITY_UNRESOLVED`, `GENERATOR_VERSION_UNRESOLVED` o `INVALID_PARAMETER_CONSTRAINT`; null cuando `status` no es `rejected`.
- `constraint_summary: object` (required) — resumen normalizado de tipos, rangos, categorias, cardinalidades y compatibilidades tomadas del spec.
- `synthetic_data_flag: boolean` (required) — constante `true`; identifica que el output pertenece a la cadena de datos sinteticos.
- `non_evidentiary_flag: boolean` (required) — constante `true`; impide tratar el run como evidencia de campo o validacion real.
- `intended_use: enum[exploration]` (required) — uso permitido para este motor; el valor normal y permitido es `exploration`.
- `domain_validity_limits: string` (required) — limites de dominio heredados del spec y aplicados al run.
- `limitations_note: string` (required) — nota explicita de que el output es sintetico, no evidentiary y no sustituye Validation Data Bridge ni Verification Bridge.
- `source_ref: string` (required) — ancla primaria de lineage, normalmente igual a `source_problem_ref`.
- `produced_by_motor: string` (required) — constante `motor_030`.
- `produced_at: datetime` (required) — timestamp en que `motor_030` emitio el run.
- `parent_id: string | null` (required) — `record_id` previo de `SyntheticGenerationRun` supersedido para el mismo spec y configuracion; null en primera emision.
- `version_id: string` (required) — identificador estable de esta version gobernada del run.
- `created_at: datetime` (required) — timestamp de creacion de esta version persistida.
- `updated_at: datetime` (required) — ultimo timestamp de actualizacion gobernada de metadatos; no habilita mutacion silenciosa del payload.
- `version_hash: string` (required) — hash determinista sobre identidad del spec, versiones, parametros, semilla, flags, lineage y estado material.

`SyntheticDataset`
- `dataset_id: string` (required) — identificador canonico estable del dataset sintetico producido.
- `record_id: string` (required) — identificador inmutable de almacenamiento para esta version persistida del dataset.
- `run_id: string` (required) — referencia al `SyntheticGenerationRun.run_id` que produjo el dataset.
- `manifest_id: string` (required) — referencia al `GenerationManifest.manifest_id` que documenta este dataset.
- `expert_spec_ref: string` (required) — referencia al `motor_029.ExpertProblemSpec.spec_id` usado por el run.
- `source_problem_ref: string` (required) — `inference_case_id` de origen preservado desde el spec.
- `generator_version: string` (required) — version semver del generador usada para producir los registros.
- `version_record_refs: list[string]` (required) — version records de motor_002 requeridos para reconstruccion del dataset.
- `parameter_set: object` (required) — parametros exactos compartidos con el run; debe ser materialmente identico al del `SyntheticGenerationRun`.
- `schema: object` (required) — definicion de columnas, tipos, dominios, nullable permitido y reglas de validacion por campo.
- `records: list[object]` (required) — registros sinteticos generados; puede materializarse como filas embebidas o como particiones gobernadas por el mismo schema.
- `record_count: integer` (required) — numero total de registros sinteticos emitidos; debe coincidir con `records` o con la suma de particiones.
- `partition_refs: list[string]` (required) — referencias a particiones internas o externas del dataset; vacio cuando el dataset se almacena como una sola coleccion.
- `scenario_column: string | null` (required) — nombre de columna que identifica escenarios cuando aplica; null si no hay multiples escenarios.
- `dataset_hash: string` (required) — hash determinista sobre schema, registros normalizados, particiones, parametros, flags y lineage.
- `quality_checks: object` (required) — resultados de validacion de tipos, rangos, categorias, conteos, reproducibilidad y drift de restricciones.
- `synthetic_data_flag: boolean` (required) — constante `true`.
- `non_evidentiary_flag: boolean` (required) — constante `true`.
- `intended_use: enum[exploration]` (required) — uso permitido para este output de `motor_030`.
- `domain_validity_limits: string` (required) — limites de dominio del dataset, heredados del spec y del manifest.
- `limitations_note: string` (required) — nota explicita de limitaciones epistemicas y prohibicion de uso como evidencia real.
- `source_ref: string` (required) — ancla primaria de lineage, normalmente igual a `source_problem_ref`.
- `produced_by_motor: string` (required) — constante `motor_030`.
- `produced_at: datetime` (required) — timestamp en que el dataset fue emitido.
- `parent_id: string | null` (required) — `record_id` previo de `SyntheticDataset` supersedido por rebuild gobernado; null en primera emision.
- `version_id: string` (required) — identificador estable de esta version gobernada del dataset.
- `created_at: datetime` (required) — timestamp de creacion de esta version persistida.
- `updated_at: datetime` (required) — ultimo timestamp de actualizacion gobernada de metadatos.
- `version_hash: string` (required) — hash determinista sobre payload material del dataset, referencias, flags, lineage y versionado.

`GenerationManifest`
- `manifest_id: string` (required) — identificador canonico estable del manifiesto de generacion.
- `record_id: string` (required) — identificador inmutable de almacenamiento para esta version persistida del manifest.
- `run_id: string` (required) — referencia al `SyntheticGenerationRun.run_id` documentado.
- `dataset_refs: list[string]` (required) — `SyntheticDataset.dataset_id` producidos por el run y cubiertos por este manifest.
- `expert_spec_ref: string` (required) — referencia al `motor_029.ExpertProblemSpec.spec_id` usado por el run.
- `source_problem_ref: string` (required) — `inference_case_id` de origen preservado desde el spec.
- `generator_version: string` (required) — version semver del generador resuelta para el run.
- `version_record_refs: list[string]` (required) — referencias a version records de motor_002 para spec, generador, reglas y artefactos de entrada.
- `parameter_set: object` (required) — copia canonica del conjunto exacto de parametros del run.
- `constraints_applied: list[object]` (required) — restricciones de tipos, rangos, categorias, compatibilidades y escenarios aplicadas desde el spec.
- `scenario_summary: object` (required) — resumen de escenarios incluidos, particiones generadas y diferencias de parametros por escenario.
- `quality_checks: object` (required) — resultados agregados de validacion del run y datasets emitidos.
- `reproducibility_fingerprint: string` (required) — huella determinista que permite verificar que spec, versiones, parametros y semilla reproducen el mismo output.
- `forbidden_uses: list[string]` (required) — lista explicita de usos prohibidos, incluyendo evidencia de campo, Validation Data Bridge, Verification Bridge y cierre decisional.
- `synthetic_data_flag: boolean` (required) — constante `true`.
- `non_evidentiary_flag: boolean` (required) — constante `true`.
- `intended_use: enum[exploration]` (required) — uso permitido para el manifest y los outputs cubiertos.
- `domain_validity_limits: string` (required) — descripcion del scope valido heredado del spec.
- `limitations_note: string` (required) — texto explicito de limitaciones, incluyendo que los datos sinteticos no elevan ningun claim.
- `source_ref: string` (required) — ancla primaria de lineage, normalmente igual a `source_problem_ref`.
- `produced_by_motor: string` (required) — constante `motor_030`.
- `produced_at: datetime` (required) — timestamp en que el manifest fue emitido.
- `parent_id: string | null` (required) — `record_id` previo de `GenerationManifest` supersedido para el mismo run o rebuild; null en primera emision.
- `version_id: string` (required) — identificador estable de esta version gobernada del manifest.
- `created_at: datetime` (required) — timestamp de creacion de esta version persistida.
- `updated_at: datetime` (required) — ultimo timestamp de actualizacion gobernada de metadatos.
- `version_hash: string` (required) — hash determinista sobre parametros, restricciones, referencias de dataset, quality checks, flags, lineage y versionado.

## relationships
- `SyntheticGenerationRun.expert_spec_ref` referencia exactamente un `motor_029.ExpertProblemSpec.spec_id`; el spec debe tener `status=approved`, `handoff_allowed=true` y no debe tener ambiguedad critica no resuelta.
- `SyntheticGenerationRun.source_problem_ref` debe coincidir con `ExpertProblemSpec.source_problem_ref` y se propaga sin mutacion a `SyntheticDataset` y `GenerationManifest`.
- `SyntheticGenerationRun.version_record_refs[]` referencia `motor_002.VersionRecord.version_id` para el spec, el generador y reglas relevantes; si no se puede resolver `generator_version`, el run se rechaza.
- `SyntheticDataset.run_id` referencia un unico `SyntheticGenerationRun.run_id`; un run puede producir uno o mas datasets bajo el mismo `parameter_set`.
- `SyntheticDataset.manifest_id` referencia el `GenerationManifest.manifest_id` que documenta restricciones, quality checks y limites del dataset.
- `GenerationManifest.run_id` referencia un unico `SyntheticGenerationRun.run_id`; todo run generado debe tener un manifest obligatorio.
- `GenerationManifest.dataset_refs[]` referencia los `SyntheticDataset.dataset_id` emitidos por el mismo `run_id`; un manifest no puede cubrir datasets de otro run.
- `SyntheticGenerationRun.parameter_set`, `SyntheticDataset.parameter_set` y `GenerationManifest.parameter_set` deben ser materialmente identicos para el mismo `run_id`.
- `SyntheticGenerationRun.generator_version`, `SyntheticDataset.generator_version` y `GenerationManifest.generator_version` deben coincidir para el mismo `run_id`.
- `parent_id` en cada entidad referencia solo un `record_id` anterior de la misma entidad; no puede apuntar a specs, datasets de otro tipo, version records ni objetos downstream.
- `source_ref`, `produced_by_motor`, `produced_at`, `version_id` y `version_hash` son obligatorios en las tres entidades y deben preservarse en cualquier handoff downstream.

## identifiers
- `SyntheticGenerationRun`: identificador canonico `run_id`; identidad persistida `record_id` mas `version_id`. El `run_id` debe derivarse deterministicamente de `motor_030`, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `parameter_set`, `generation_seed` y referencias de version relevantes.
- `SyntheticDataset`: identificador canonico `dataset_id`; identidad persistida `record_id` mas `version_id`. El `dataset_id` debe derivarse de `motor_030`, `run_id`, rol o particion del dataset, schema normalizado y `dataset_hash`.
- `GenerationManifest`: identificador canonico `manifest_id`; identidad persistida `record_id` mas `version_id`. El `manifest_id` debe derivarse de `motor_030`, `run_id`, `dataset_refs`, `generator_version`, `parameter_set` y `reproducibility_fingerprint`.
- `record_id` identifica una version persistida inmutable y no debe reutilizarse para contenido materialmente incompatible.
- IDs upstream como `expert_spec_ref`, `source_problem_ref` y `version_record_refs` se preservan como referencias externas; `motor_030` no los reescribe ni los reemplaza por identificadores locales.
- Timestamps, nombres de escenarios, posiciones de lista, etiquetas narrativas o nombres de archivo no son identificadores estables suficientes.

## versioning
- Las tres entidades persistidas incluyen `version_id`, `created_at`, `updated_at` y `version_hash`.
- `version_id` cambia cuando cambia contenido material: spec de entrada, referencias de version, `generator_version`, `parameter_set`, `generation_seed`, restricciones aplicadas, schema, registros, quality checks, flags epistemicos, lineage o parent linkage.
- `created_at` se fija al emitir por primera vez la version persistida de la entidad.
- `updated_at` solo registra actualizaciones gobernadas de metadatos o supersesion; no permite modificar silenciosamente payloads, registros sinteticos, parametros ni flags de una version ya emitida.
- `version_hash` se calcula de forma determinista sobre payload material normalizado, identificadores estables, referencias upstream, flags epistemicos, lineage y parent linkage, excluyendo metadatos de transporte no materiales.
- `SyntheticGenerationRun.version_hash` incluye `expert_spec_ref`, `source_problem_ref`, `generator_version`, `version_record_refs`, `parameter_set`, `generation_seed`, `scenario_refs`, `status`, `rejection_code`, `constraint_summary`, flags, lineage y `parent_id`.
- `SyntheticDataset.version_hash` incluye `run_id`, `manifest_id`, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `version_record_refs`, `parameter_set`, `schema`, registros o particiones normalizadas, `record_count`, `dataset_hash`, `quality_checks`, flags, lineage y `parent_id`.
- `GenerationManifest.version_hash` incluye `run_id`, `dataset_refs`, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `version_record_refs`, `parameter_set`, `constraints_applied`, `scenario_summary`, `quality_checks`, `reproducibility_fingerprint`, `forbidden_uses`, flags, lineage y `parent_id`.
- Un rebuild material para el mismo spec crea nuevas versiones con `parent_id` hacia el `record_id` supersedido; no se sobrescribe la version anterior.
- Reejecutar con el mismo spec aprobado, mismas version records, mismo `generator_version`, mismo `parameter_set` y misma `generation_seed` debe reproducir los mismos IDs canonicos y hashes materiales, salvo timestamps definidos fuera del hash.

## lineage
- Cada `SyntheticGenerationRun`, `SyntheticDataset` y `GenerationManifest` incluye `source_ref`, `produced_by_motor`, `produced_at` y `parent_id`.
- `source_ref` es la ancla primaria de provenance; para este motor normalmente es igual a `source_problem_ref` heredado del `expert_problem_spec`.
- `produced_by_motor` es siempre `motor_030` en las tres entidades; ningun output de este motor puede declarar otro productor.
- `produced_at` registra el instante en que `motor_030` emitio la version y debe permanecer estable despues de persistencia.
- `parent_id` es null en primera emision y referencia el `record_id` anterior de la misma entidad cuando una correccion o rebuild gobernado supersede el output.
- `expert_spec_ref`, `source_problem_ref`, `version_record_refs`, `generator_version`, `parameter_set` y `generation_seed` forman el lineage minimo necesario para reconstruir un run y su dataset.
- El lineage debe preservar la separacion epistemica: `synthetic_data_flag=true`, `non_evidentiary_flag=true`, `intended_use=exploration`, `domain_validity_limits` y `limitations_note` se mantienen en todos los outputs y handoffs.
- Missing `source_ref`, `produced_by_motor`, `produced_at`, `parent_id` requerido por supersesion, `expert_spec_ref`, `source_problem_ref`, `generator_version`, `parameter_set` o flags epistemicos hace invalida la entidad; el motor no debe reparar esos huecos con inferencias silenciosas.
- El lineage de `motor_030` no autoriza a citar datasets como evidencia de campo, sustituir Validation Data Bridge o Verification Bridge, entrenar modelos, elevar claims ni cerrar inference cases.
