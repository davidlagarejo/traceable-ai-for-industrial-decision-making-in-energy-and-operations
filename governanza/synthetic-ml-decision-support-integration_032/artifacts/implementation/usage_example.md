# Usage Example — Synthetic ML Decision Support Integration

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

This example shows a complete accepted handoff with subordinate synthetic support only.
-->

## example
Decision Core calls motor_032 after motor_031 emits `capability_demonstration_report` `cdr-031-0007` for inference case `case-014-221`. The target inference record already exists in motor_014 as `hypothesis_only`, and the phase contract allows `synthetic_support` only as a subordinate signal. The expected result is an atomic bundle with a support register, a hypothesis signal and a labeled support record; the inference record keeps its current epistemic state and decision grade.

## inputs_used
```json
{
  "capability_demonstration_report": {
    "report_id": "cdr-031-0007",
    "source_ref": "src-031-cdr-0007__ir-014-221__pc-001-dc-alpha",
    "source_problem_ref": "case-014-221",
    "expert_spec_ref": "eps-029-041",
    "generator_version": "1.4.2",
    "gap_to_real_validation": "requires 90 days of measured site outcomes",
    "gap_to_deployment": "requires field calibration and monitoring plan",
    "known_failure_modes": ["generator range too narrow"],
    "domain_validity_limits": "valid only for synthetic scenarios defined by eps-029-041",
    "limitations_note": "synthetic capability report; not evidence of real-world predictability",
    "synthetic_data_flag": true,
    "non_evidentiary_flag": true
  },
  "inference_records": [
    {
      "inference_record_id": "ir-014-221",
      "inference_case_id": "case-014-221",
      "epistemic_state": "hypothesis_only",
      "decision_grade": null,
      "accepted_signal_classes": ["synthetic_support", "library_knowledge"]
    }
  ],
  "phase_contracts": [
    {
      "phase_contract_ref": "pc-001-dc-alpha",
      "allowed_subordinate_signal_classes": ["synthetic_support"]
    }
  ],
  "version_records": {
    "capability_report": "ver-031-cdr-0007",
    "inference_record": "ver-014-ir-221",
    "phase_contract": "ver-001-pc-alpha",
    "lineage_id": "lin-032-0007"
  }
}
```

## expected_output
```json
{
  "status": "accepted",
  "synthetic_ml_support_register": {
    "support_register_id": "smr-032-cdr-031-0007-ir-014-221",
    "source_report_id": "cdr-031-0007",
    "target_inference_record_id": "ir-014-221",
    "source_problem_ref": "case-014-221",
    "expert_spec_ref": "eps-029-041",
    "phase_contract_ref": "pc-001-dc-alpha",
    "support_level": "capability_demo",
    "intended_use": "preliminary_support",
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true,
    "cannot_substitute": [
      "Validation Data Bridge",
      "Verification Bridge",
      "field_evidence",
      "validation_data",
      "claim_closure",
      "final_TAD_output"
    ],
    "lineage_id": "lin-032-0007",
    "version_id": "smr_v-<deterministic-hash>",
    "version_hash": "<deterministic-content-hash>"
  },
  "hypothesis_signal": {
    "hypothesis_signal_id": "hs-032-cdr-031-0007-ir-014-221",
    "support_register_id": "smr-032-cdr-031-0007-ir-014-221",
    "signal_role": "subordinate",
    "evidence_level": "synthetic_support",
    "intended_use": "preliminary_support",
    "permitted_effect": "preliminary_prioritization",
    "decision_grade_change_allowed": false,
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true
  },
  "labeled_support_record": {
    "labeled_support_record_id": "lsr-032-cdr-031-0007-ir-014-221",
    "labels": [
      "synthetic_support",
      "non_evidentiary",
      "subordinate_signal",
      "preliminary_support"
    ],
    "destination_consumers": [
      "Decision Core handoff",
      "audit trail",
      "motor_033 preliminary prioritization"
    ],
    "rejection_boundaries": [
      "decision_grade_promotion",
      "claim_closure",
      "field_validation",
      "Validation Data Bridge replacement",
      "Verification Bridge replacement",
      "field_evidence replacement",
      "validation_data replacement",
      "final_TAD_output"
    ],
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true
  }
}
```

## notes
The example assumes the source report already passed motor_031 validation, the target inference record is owned by motor_014 and the phase contract is owned by motor_001. Motor_032 does not mutate those upstream objects, does not convert `hypothesis_only` to `decision_grade`, and does not replace Validation Data Bridge, Verification Bridge, field evidence or validation data. All emitted objects carry `synthetic_support_flag=true`, `non_evidentiary_flag=true`, `intended_use="preliminary_support"`, upstream version references and the original limitation text.
