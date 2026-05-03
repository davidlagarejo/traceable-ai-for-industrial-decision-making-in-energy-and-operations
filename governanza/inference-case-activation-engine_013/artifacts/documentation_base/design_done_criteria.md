# Design Done Criteria — Inference Case Activation Engine

Motor ID: motor_013

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
why_it_exists:  Separa selección de casos del análisis del Decision Core.
key_inputs:     facility_prior (motor_012), library_objects (motor_011), quality_records (motor_007)
key_outputs:    inference_case, activation_record, trigger_log
key_objects:    InferenceCase, ActivationRecord, TriggerCondition
what_not_to_do: No analiza los casos. No produce conclusiones. Solo activa y registra.
design_notes:   Crea los casos que alimentan al Decision Core. Sin este motor, motor_014 no tiene input.

Sections below completed for Gate 1 validation.
-->

## criteria
- `master_concept_doc.md` defines purpose, concrete actions, explicit non-responsibilities and separate existence rationale for `motor_013`.
- `functional_contract.md` lists `facility_prior`, `library_objects` and `quality_records` as inputs with their producer motors and lists `inference_case`, `activation_record` and `trigger_log` as outputs.
- `functional_contract.md`, `conceptual_schema.md` and `operational_rules.md` contain no open markers and define enough fields, limits and validations to derive the technical schema.
- `conceptual_schema.md` defines `InferenceCase`, `ActivationRecord`, `TriggerCondition` and trigger log fields with required identifiers, status and lineage fields.
- `operational_rules.md` explicitly forbids analysis, conclusions, mutation of upstream objects and ad hoc trigger creation.
- `acceptance_tests.md` covers a concrete happy path, no-match behavior, duplicate-prevention behavior and explicit rejection criteria.
- `failure_modes.md` documents quality bypass, trigger scope drift, duplicate activation, lineage loss and analysis leakage as observable risks.
- All seven documentation base artifacts exist, are larger than the minimum gate threshold and contain no open placeholder markers.
