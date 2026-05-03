# Design Done Criteria — TAD Preliminary Prioritization Engine

Motor ID: motor_033

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ordenar preliminarmente inference cases activos usando señales sintéticas del motor_032.
why_it_exists:  Cuando hay múltiples inference cases activos compitiendo por recursos, se necesita una señal preliminar de orden de atención trazable y no arbitraria.
key_inputs:     synthetic_ml_support_register (motor_032), inference_cases (motor_013), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    preliminary_priority_register, ranking_basis, rank_uncertainty_record
key_objects:    PreliminaryPriorityRegister, RankingBasis, RankUncertaintyRecord
what_not_to_do: No puede ser TAD final. No puede usarse como evidencia para cerrar inference cases. Siempre requiere revisión con evidencia real.
design_notes:   Output es preliminary_priority_register, nunca TAD final. El ranking es exploratorio.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true, rank_is_preliminary=true

All sections below are completed with concrete content for this motor.
-->

## criteria
- `master_concept_doc.md` defines purpose, concrete actions, explicit boundaries, and rationale for keeping this motor separate from TAD final and Decision Core.
- `functional_contract.md` lists all required inputs and outputs, including `synthetic_ml_support_register`, `inference_cases`, `phase_contracts`, `version_records`, `preliminary_priority_register`, `ranking_basis`, and `rank_uncertainty_record`.
- `functional_contract.md` and `operational_rules.md` require `synthetic_support_flag=true`, `non_evidentiary_flag=true`, and `rank_is_preliminary=true` on all motor_033 outputs.
- `conceptual_schema.md` defines `PreliminaryPriorityRegister`, `RankingBasis`, and `RankUncertaintyRecord` with required fields and relationships.
- `operational_rules.md` prohibits TAD final, inference case closure, evidentiary promotion, source mutation, and suppression of ranking uncertainty.
- `acceptance_tests.md` includes a concrete happy path, sparse support, ties, conflicting support, out-of-scope support, and explicit rejection criteria.
- `failure_modes.md` documents epistemic promotion, missing flags, overstated certainty, lineage break, and scope drift as observable risks.
- All documentation_base files contain no open markers and are large enough to satisfy Gate 1 file existence checks.
- The design preserves lineage through version references and keeps preliminary prioritization subordinate to review with real evidence.
