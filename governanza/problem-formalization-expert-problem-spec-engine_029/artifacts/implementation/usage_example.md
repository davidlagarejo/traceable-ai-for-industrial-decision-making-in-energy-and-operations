# Usage Example — Problem Formalization / Expert Problem Spec Engine

Motor ID: motor_029

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir inference cases activados en especificaciones formales del problema: conocimiento experto, restricciones reales y supuestos explícitos del dominio.
why_it_exists:  Un dataset sintético sin especificación formal es ruido estructurado. Este motor produce el contrato del que depende toda la cadena sintética.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003)
key_outputs:    expert_problem_spec, ambiguity_register, parameter_constraints
key_objects:    ExpertProblemSpec, AmbiguityRegister, ParameterConstraint
what_not_to_do: No genera datos sintéticos. No corre ML. No puede ejecutarse sobre inference_cases con ambiguity_register crítico no resuelto.
design_notes:   Prerequisito obligatorio de toda la cadena sintética. No genera datos. No diseña modelos. Su output es non_evidentiary_flag=true.
epistemic_flags: non_evidentiary_flag=true, intended_use=exploration

All implementation example fields are complete.
-->

## example
`motor_029` is called after `motor_013` activates inference case `IC-029-001` for synthetic-chain exploration. The case asks for a formal binary classification problem that distinguishes facility scenarios where `failure_event=true` using declared `capacity_kw` and `inspection_interval_days` constraints, with phase authority from `PC-SYNTH-FORMALIZATION-v1` and taxonomy snapshot `TAX-2026-04-01`. The expected result is a non-evidentiary `ExpertProblemSpec`, one owning `AmbiguityRegister`, and deterministic `ParameterConstraint` records that can be consumed by `motor_030` only if no critical ambiguity remains unresolved.

## inputs_used
```python
from codebase import ProblemFormalizationExpertProblemSpecEngine

engine = ProblemFormalizationExpertProblemSpecEngine()

result = engine.formalize(
    inference_cases=[
        {
            "inference_case_id": "IC-029-001",
            "status": "activated",
            "phase_ref": "PC-SYNTH-FORMALIZATION-v1",
            "problem_statement": "Classify whether a facility scenario has failure_event=true from capacity_kw and inspection_interval_days.",
            "problem_class_hint": "classification_binary",
            "target_variable_ref": "failure_event",
            "expert_assumptions": [
                "Inspection interval is measured in days.",
                "Capacity is measured in kW at the facility boundary."
            ],
            "domain_terms": ["facility", "capacity_kw", "inspection_interval_days", "failure_event"],
            "source_provenance_refs": ["SRC-FIELD-PROTOCOL-17", "SRC-EXPERT-REVIEW-029-A"],
            "parameter_constraints": [
                {
                    "parameter_name": "capacity_kw",
                    "value_type": "float",
                    "allowed_domain": {"min": 50.0, "max": 500.0, "inclusive_min": True, "inclusive_max": True},
                    "unit": "kW",
                    "constraint_kind": "range",
                    "constraint_rationale": "Expert review bounds facility capacity for the activated case.",
                    "uncertainty_treatment": "Preserve the full expert range for downstream synthetic generation."
                },
                {
                    "parameter_name": "inspection_interval_days",
                    "value_type": "integer",
                    "allowed_domain": {"min": 7, "max": 90, "inclusive_min": True, "inclusive_max": True},
                    "unit": "days",
                    "constraint_kind": "range",
                    "constraint_rationale": "Source case limits inspections to the operational maintenance interval.",
                    "uncertainty_treatment": "Treat the interval as bounded expert uncertainty, not measured frequency."
                },
                {
                    "parameter_name": "failure_event",
                    "value_type": "boolean",
                    "allowed_domain": {"values": [False, True]},
                    "unit": None,
                    "constraint_kind": "category_set",
                    "constraint_rationale": "The target class is explicitly binary in the activated inference case.",
                    "uncertainty_treatment": "No probability is inferred; only the allowed target states are declared."
                }
            ],
            "input_ambiguities": []
        }
    ],
    phase_contracts={
        "PC-SYNTH-FORMALIZATION-v1": {
            "permits_synthetic_formalization": True,
            "authorized_motors": ["motor_029"],
            "allowed_handoffs": ["motor_030.expert_problem_spec"]
        }
    },
    version_records=[
        {"object_ref": "IC-029-001", "version_id": "VR-IC-029-001-v1", "version_hash": "case-hash-001"},
        {"object_ref": "PC-SYNTH-FORMALIZATION-v1", "version_id": "VR-PC-SYNTH-v1", "version_hash": "phase-hash-001"},
        {"object_ref": "TAX-2026-04-01", "version_id": "VR-TAX-2026-04-01", "version_hash": "taxonomy-hash-001"}
    ],
    canonical_taxonomy={
        "taxonomy_snapshot_ref": "TAX-2026-04-01",
        "facility": {"canonical_id": "CT-FACILITY", "name": "facility", "aliases": ["site"]},
        "capacity_kw": {"canonical_id": "CT-CAPACITY-KW", "name": "capacity_kw", "aliases": ["facility_capacity_kw"], "value_type": "float", "unit": "kW"},
        "inspection_interval_days": {"canonical_id": "CT-INSPECTION-INTERVAL-DAYS", "name": "inspection_interval_days", "value_type": "integer", "unit": "days"},
        "failure_event": {"canonical_id": "CT-FAILURE-EVENT", "name": "failure_event", "value_type": "boolean"}
    },
    produced_at="2026-04-17T12:00:00+00:00",
)
```

## expected_output
```json
{
  "expert_problem_spec": {
    "spec_id": "EPS-IC-029-001-v1",
    "source_problem_ref": "IC-029-001",
    "phase_contract_ref": "PC-SYNTH-FORMALIZATION-v1",
    "taxonomy_snapshot_ref": "TAX-2026-04-01",
    "version_record_refs": ["VR-IC-029-001-v1", "VR-PC-SYNTH-v1", "VR-TAX-2026-04-01"],
    "problem_class": "classification_binary",
    "target_variable_ref": "CT-FAILURE-EVENT",
    "parameter_constraints_ref": [
      "PC-EPS-IC-029-001-v1-capacity-kw-c2f4e576a8",
      "PC-EPS-IC-029-001-v1-inspection-interval-days-45284a2d0f",
      "PC-EPS-IC-029-001-v1-failure-event-369864edaa"
    ],
    "ambiguity_register_ref": "AR-EPS-IC-029-001-v1",
    "handoff_allowed": true,
    "handoff_block_reason": null,
    "non_evidentiary_flag": true,
    "intended_use": "exploration",
    "domain_validity_limits": "Valid only for the declared source case scope and canonicalized terms: facility, capacity_kw, inspection_interval_days, failure_event.",
    "limitations_note": "This expert problem specification is a non-evidentiary generator contract for exploration. It is not field evidence, validation data, decision-grade proof, or a substitute for real-world verification."
  },
  "ambiguity_register": {
    "register_id": "AR-EPS-IC-029-001-v1",
    "spec_id": "EPS-IC-029-001-v1",
    "source_problem_ref": "IC-029-001",
    "items": [],
    "has_unresolved_critical": false,
    "highest_unresolved_impact": "none",
    "handoff_allowed": true,
    "blocking_item_refs": [],
    "non_evidentiary_flag": true,
    "intended_use": "exploration"
  },
  "parameter_constraints": [
    {
      "parameter_name": "capacity_kw",
      "canonical_term_ref": "CT-CAPACITY-KW",
      "value_type": "float",
      "allowed_domain": {"min": 50.0, "max": 500.0, "inclusive_min": true, "inclusive_max": true},
      "unit": "kW",
      "constraint_kind": "range",
      "non_evidentiary_flag": true,
      "intended_use": "exploration"
    },
    {
      "parameter_name": "inspection_interval_days",
      "canonical_term_ref": "CT-INSPECTION-INTERVAL-DAYS",
      "value_type": "integer",
      "allowed_domain": {"min": 7, "max": 90, "inclusive_min": true, "inclusive_max": true},
      "unit": "days",
      "constraint_kind": "range",
      "non_evidentiary_flag": true,
      "intended_use": "exploration"
    },
    {
      "parameter_name": "failure_event",
      "canonical_term_ref": "CT-FAILURE-EVENT",
      "value_type": "boolean",
      "allowed_domain": {"values": [false, true]},
      "unit": null,
      "constraint_kind": "category_set",
      "non_evidentiary_flag": true,
      "intended_use": "exploration"
    }
  ]
}
```

## notes
This example is valid only because the inference case is active, the phase contract explicitly authorizes `motor_029`, required version records are present, all required terms resolve through `canonical_taxonomy`, and no critical ambiguity is unresolved. The output remains `expert_spec` level and `non_evidentiary_flag=true`; it cannot validate a real-world claim, replace field evidence, generate synthetic rows, select a model, or close an inference case.
