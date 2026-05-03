# Usage Example — Decision Core / Inference Engine

Motor ID: motor_014

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Producir registros de inferencia, tensiones, conflictos, oportunidades, gaps y agenda de validación.
why_it_exists:  Es el corazón analítico de Fase 2.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001)
key_outputs:    inference_record, tension_record, gap_agenda, validation_agenda
key_objects:    InferenceRecord, Tension, ValidationAgenda
what_not_to_do: No produce reportes finales. No verifica claims. Solo infiere y registra con contratos explícitos.
design_notes:   Determinismo primero. La IA puede asistir pero no decide. Depende de motor_013 y motor_001.

All placeholder markers in this file have been replaced with concrete content.
-->

## example
`motor_014` is called after `motor_013` has activated a Fase 2 inference case about backup power resilience for facility `FAC-123`. The caller provides the activated inference case plus the matching `PhaseContract` from `motor_001`; the expected result is a bounded inference record with an explicit missing-validation tension, a gap agenda item, and a validation agenda routed to `motor_018`.

## inputs_used
```json
{
  "inference_cases": [
    {
      "case_id": "IC-014-HP-001",
      "activation_record_ref": "AR-013-HP-001",
      "trigger_log_ref": "TL-013-HP-001",
      "phase_id": "phase_2",
      "case_status": "activated",
      "analysis_question": "Does facility FAC-123 require validation of backup power resilience?",
      "evidence_refs": [
        {
          "evidence_id": "EV-FAC-123-PRIOR",
          "source_class": "facility_prior",
          "evidence_level": "contextual",
          "provenance_ref": "PROV-FAC-123",
          "lineage_ref": "LIN-FAC-123"
        },
        {
          "evidence_id": "EV-LIB-456",
          "source_class": "library_object",
          "evidence_level": "contextual",
          "provenance_ref": "PROV-LIB-456",
          "lineage_ref": "LIN-LIB-456"
        }
      ],
      "lineage_refs": [
        "LIN-IC-014-HP-001",
        "LIN-FAC-123",
        "LIN-LIB-456"
      ]
    }
  ],
  "phase_contracts": [
    {
      "contract_id": "PC-PHASE-2-v1",
      "phase_id": "phase_2",
      "allowed_inputs": ["inference_cases"],
      "allowed_outputs": [
        "inference_record",
        "tension_record",
        "gap_agenda",
        "validation_agenda"
      ],
      "handoff_rules": {
        "validation": "motor_018"
      },
      "output_limits": {
        "may_verify_claims": false,
        "may_render_reports": false
      },
      "contract_version": "1.0.0"
    }
  ]
}
```

## expected_output
```json
[
  {
    "inference_record": {
      "inference_id": "motor_014:inference:IC-014-HP-001:<stable_version>",
      "motor_id": "motor_014",
      "case_id": "IC-014-HP-001",
      "activation_record_ref": "AR-013-HP-001",
      "trigger_log_ref": "TL-013-HP-001",
      "phase_id": "phase_2",
      "phase_contract_ref": "PC-PHASE-2-v1",
      "contract_version": "1.0.0",
      "analysis_question": "Does facility FAC-123 require validation of backup power resilience?",
      "inference_state": "bounded_inference",
      "inference_basis": [
        "AR-013-HP-001",
        "EV-FAC-123-PRIOR",
        "EV-LIB-456",
        "TL-013-HP-001"
      ],
      "evidence_refs": [
        {
          "evidence_id": "EV-FAC-123-PRIOR",
          "source_class": "facility_prior",
          "evidence_level": "contextual",
          "provenance_ref": "PROV-FAC-123",
          "lineage_ref": "LIN-FAC-123"
        },
        {
          "evidence_id": "EV-LIB-456",
          "source_class": "library_object",
          "evidence_level": "contextual",
          "provenance_ref": "PROV-LIB-456",
          "lineage_ref": "LIN-LIB-456"
        }
      ],
      "lineage_refs": [
        "AR-013-HP-001",
        "LIN-FAC-123",
        "LIN-IC-014-HP-001",
        "LIN-LIB-456",
        "PC-PHASE-2-v1",
        "TL-013-HP-001"
      ],
      "rule_version": "dicie_rules_v1",
      "decision_trace": [
        "case_status_activated",
        "phase_contract_authorized",
        "evidence_refs_validated",
        "state_bounded_inference_real_evidence",
        "gap_validation_data_required"
      ],
      "synthetic_support_present": false,
      "created_at": "1970-01-01T00:00:00Z",
      "updated_at": "1970-01-01T00:00:00Z",
      "version_id": "<stable_version>",
      "version_hash": "<stable_hash>",
      "source_ref": "IC-014-HP-001",
      "produced_by_motor": "motor_014",
      "produced_at": "1970-01-01T00:00:00Z",
      "parent_id": null
    },
    "tension_record": [
      {
        "tension_id": "motor_014:tension:<stable_hash>",
        "motor_id": "motor_014",
        "inference_id": "motor_014:inference:IC-014-HP-001:<stable_version>",
        "case_id": "IC-014-HP-001",
        "phase_contract_ref": "PC-PHASE-2-v1",
        "contract_version": "1.0.0",
        "tension_type": "missing_evidence",
        "severity": "medium",
        "source_refs": ["EV-FAC-123-PRIOR", "EV-LIB-456"],
        "description": "contextual evidence bounds the inference but lacks validation data",
        "requires_validation": true,
        "related_gap_item_ids": ["motor_014:gap_item:<stable_hash>"],
        "lineage_refs": [
          "AR-013-HP-001",
          "LIN-FAC-123",
          "LIN-IC-014-HP-001",
          "LIN-LIB-456",
          "PC-PHASE-2-v1",
          "TL-013-HP-001"
        ],
        "rule_version": "dicie_rules_v1",
        "created_at": "1970-01-01T00:00:00Z",
        "updated_at": "1970-01-01T00:00:00Z",
        "version_id": "<stable_version>",
        "version_hash": "<stable_hash>",
        "source_ref": "motor_014:inference:IC-014-HP-001:<stable_version>",
        "produced_by_motor": "motor_014",
        "produced_at": "1970-01-01T00:00:00Z",
        "parent_id": null
      }
    ],
    "gap_agenda": {
      "gap_agenda_id": "motor_014:gap_agenda:<stable_hash>",
      "motor_id": "motor_014",
      "inference_id": "motor_014:inference:IC-014-HP-001:<stable_version>",
      "case_id": "IC-014-HP-001",
      "phase_contract_ref": "PC-PHASE-2-v1",
      "contract_version": "1.0.0",
      "gap_items": [
        {
          "gap_item_id": "motor_014:gap_item:<stable_hash>",
          "gap_type": "missing_validation_data",
          "affected_ref": "motor_014:inference:IC-014-HP-001:<stable_version>",
          "missing_condition": "site-level backup power validation data",
          "required_downstream_action": "request validation data through motor_018",
          "priority": "medium",
          "source_refs": ["EV-FAC-123-PRIOR", "EV-LIB-456"]
        }
      ],
      "priority_order": ["motor_014:gap_item:<stable_hash>"],
      "validation_dependency_refs": ["motor_014:validation_item:<stable_hash>"],
      "lineage_refs": [
        "AR-013-HP-001",
        "LIN-FAC-123",
        "LIN-IC-014-HP-001",
        "LIN-LIB-456",
        "PC-PHASE-2-v1",
        "TL-013-HP-001"
      ],
      "rule_version": "dicie_rules_v1",
      "created_at": "1970-01-01T00:00:00Z",
      "updated_at": "1970-01-01T00:00:00Z",
      "version_id": "<stable_version>",
      "version_hash": "<stable_hash>",
      "source_ref": "motor_014:inference:IC-014-HP-001:<stable_version>",
      "produced_by_motor": "motor_014",
      "produced_at": "1970-01-01T00:00:00Z",
      "parent_id": null
    },
    "validation_agenda": {
      "validation_agenda_id": "motor_014:validation_agenda:<stable_hash>",
      "motor_id": "motor_014",
      "inference_id": "motor_014:inference:IC-014-HP-001:<stable_version>",
      "case_id": "IC-014-HP-001",
      "gap_agenda_id": "motor_014:gap_agenda:<stable_hash>",
      "phase_contract_ref": "PC-PHASE-2-v1",
      "contract_version": "1.0.0",
      "validation_items": [
        {
          "validation_item_id": "motor_014:validation_item:<stable_hash>",
          "gap_item_id": "motor_014:gap_item:<stable_hash>",
          "required_evidence_level": "validation_data",
          "reason": "bounded contextual inference still requires validation data",
          "handoff_target": "motor_018",
          "priority": "medium",
          "source_refs": [
            "EV-FAC-123-PRIOR",
            "EV-LIB-456",
            "motor_014:gap_item:<stable_hash>"
          ]
        }
      ],
      "required_evidence_level": "validation_data",
      "handoff_target": "motor_018",
      "lineage_refs": [
        "AR-013-HP-001",
        "LIN-FAC-123",
        "LIN-IC-014-HP-001",
        "LIN-LIB-456",
        "PC-PHASE-2-v1",
        "TL-013-HP-001"
      ],
      "rule_version": "dicie_rules_v1",
      "created_at": "1970-01-01T00:00:00Z",
      "updated_at": "1970-01-01T00:00:00Z",
      "version_id": "<stable_version>",
      "version_hash": "<stable_hash>",
      "source_ref": "motor_014:gap_agenda:<stable_hash>",
      "produced_by_motor": "motor_014",
      "produced_at": "1970-01-01T00:00:00Z",
      "parent_id": null
    }
  }
]
```

## notes
The case must already be activated by `motor_013`, and the `phase_contracts` input must authorize `inference_cases` plus all four outputs emitted by this motor. The example intentionally uses contextual evidence only, so the motor may create a bounded inference but must still register the missing validation data instead of treating the result as a verified claim.
