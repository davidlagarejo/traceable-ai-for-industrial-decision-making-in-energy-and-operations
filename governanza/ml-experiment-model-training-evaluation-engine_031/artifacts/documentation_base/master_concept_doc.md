# Master Concept Document — ML Experiment / Model Training & Evaluation Engine

Motor ID: motor_031

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Entrenar, comparar y documentar modelos de ML sobre datasets sintéticos, produciendo capability_demonstration_report.
why_it_exists:  Demuestra capacidades analíticas antes de que exista evidencia real.
key_inputs:     synthetic_dataset (motor_030), expert_problem_spec (motor_029), version_records (motor_002)
key_outputs:    training_run_record, model_eval_summary, capability_demonstration_report
key_objects:    TrainingRunRecord, ModelEvalSummary, CapabilityDemonstrationReport
what_not_to_do: No produce modelos listos para producción. No puede ser usado como evidencia de validación de campo.
design_notes:   No produce modelos de producción. La política de selección de modelos en synthetic_epistemology_rules.md es vinculante.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true

Complete all sections with real motor-specific content before gate validation.
-->

## purpose
El motor_031 entrena, compara y documenta modelos de ML usando exclusivamente datasets sintéticos producidos por motor_030 y especificaciones expertas producidas por motor_029. Su salida principal es un `capability_demonstration_report` que describe qué capacidad analítica puede demostrarse bajo las reglas del generador sintético. Todas sus métricas, conclusiones y comparaciones quedan marcadas como soporte sintético no evidenciario y no pueden elevar claims sobre el mundo real.

## what_it_does
- Recibe `synthetic_dataset` desde motor_030, `expert_problem_spec` desde motor_029 y `version_records` desde motor_002.
- Verifica que el dataset sintético, la especificación experta y los registros de versionado correspondan al mismo `source_problem_ref`.
- Construye un `experiment_config` reproducible a partir del `problem_class`, la métrica primaria, los límites de dominio y los parámetros declarados por el spec.
- Selecciona familias candidatas de modelos según la política vinculante de `synthetic_epistemology_rules.md`, incluyendo el baseline obligatorio para el `problem_class`.
- Ejecuta entrenamientos reproducibles sobre datos sintéticos con semillas, splits, versiones y parámetros registrados.
- Compara modelos usando métricas declaradas, estabilidad entre escenarios del bundle y `generator_sensitivity_test`.
- Produce `training_run_record`, `model_eval_summary` y `capability_demonstration_report` con lineage, versionado y flags epistémicos completos.
- Documenta brechas explícitas hacia validación real, despliegue productivo y evidencia requerida para confirmar o invalidar la capacidad observada.

## what_it_does_not_do
- No produce modelos listos para producción, binarios serializados, endpoints, pipelines de inferencia operativa ni decisiones automáticas.
- No puede ser usado como evidencia de validación de campo, verificación de sitio o cierre de un inference case.
- No genera datasets sintéticos; consume únicamente los datasets emitidos por motor_030.
- No formaliza el problema experto; consume únicamente `expert_problem_spec` aprobado por motor_029.
- No registra ni modifica versionado global; consume `version_records` de motor_002 y preserva las referencias.
- No sustituye Validation Data Bridge, Verification Bridge, Decision Core ni Synthetic ML Decision Support Integration.
- No responde preguntas causales ni convierte rankings de variables sobre datos sintéticos en evidencia causal real.

## why_it_exists
Existe como motor separado porque el entrenamiento y la evaluación reproducible de ML sobre datos sintéticos requieren reglas, objetos, métricas y controles distintos a la generación de datos y a la integración en decisión. Su función es demostrar capacidad analítica bajo supuestos controlados sin producir modelos de producción ni evidencia real; por eso la política de selección de modelos y los límites epistémicos definidos en `synthetic_epistemology_rules.md` son vinculantes.
