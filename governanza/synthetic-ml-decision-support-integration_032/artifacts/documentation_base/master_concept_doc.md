# Master Concept Document — Synthetic ML Decision Support Integration

Motor ID: motor_032

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Integrar capability_demonstration_report al Decision Core como señal subordinada etiquetada.
why_it_exists:  El Decision Core necesita recibir soporte sintético de forma trazable, etiquetada y epistemológicamente limitada.
key_inputs:     capability_demonstration_report (motor_031), inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    synthetic_ml_support_register, hypothesis_signal, labeled_support_record
key_objects:    SyntheticMLSupportRegister, HypothesisSignal, LabeledSupportRecord
what_not_to_do: No puede convertir hypothesis_only inference_records a decision_grade. No sustituye Validation Data Bridge ni Verification Bridge.
design_notes:   No puede elevar claims. No puede sustituir evidencia real. synthetic_support_flag=true en todo output.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true

Sections below are fully specified for the documentation_base gate.
-->

## purpose
Este motor integra un `capability_demonstration_report` producido por motor_031 en el Decision Core como señal subordinada, etiquetada y no evidentiary. Convierte la demostración sintética de capacidad en registros explícitos de soporte sintético vinculados a `inference_records`, sin cambiar el grado epistémico del claim. Su salida conserva lineage, versión, límites de dominio y flags obligatorios para impedir que el soporte sintético se confunda con evidencia real.

## what_it_does
- Recibe `capability_demonstration_report` desde motor_031 y verifica que conserve sus referencias a `source_problem_ref`, `expert_spec_ref`, `generator_version` y límites declarados.
- Lee `inference_records` desde motor_014 para identificar el caso de inferencia que recibirá una señal sintética subordinada.
- Consulta `phase_contracts` desde motor_001 para confirmar que la fase receptora permite señales de tipo `synthetic_support`.
- Consulta `version_records` desde motor_002 para registrar lineage entre el reporte de capacidad, el inference record y los outputs emitidos.
- Produce `synthetic_ml_support_register` con `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `support_level` y `cannot_substitute`.
- Produce `hypothesis_signal` con rol subordinado, nivel evidentiary `synthetic_support` y efecto permitido limitado a exploración o priorización preliminar.
- Produce `labeled_support_record` que encapsula la señal para consumo por Decision Core sin permitir promoción automática del inference record.

## what_it_does_not_do
- No convierte `hypothesis_only` `inference_records` a `decision_grade`.
- No sustituye Validation Data Bridge ni Verification Bridge.
- No genera datos sintéticos, entrena modelos, selecciona modelos ni recalcula métricas del `capability_demonstration_report`.
- No valida claims contra evidencia de campo ni declara un claim como verificado.
- No modifica retroactivamente outputs de motor_029, motor_030 o motor_031.
- No decide cierre de inference cases, TAD final ni rutas de verificación de campo.

## why_it_exists
Existe como motor separado porque el paso entre una demostración sintética de capacidad y una señal consumible por Decision Core necesita controles epistémicos propios. No puede elevar claims ni sustituir evidencia real; por diseño, todo output debe llevar `synthetic_support_flag=true` y `non_evidentiary_flag=true` para que el soporte sintético permanezca subordinado y trazable.
