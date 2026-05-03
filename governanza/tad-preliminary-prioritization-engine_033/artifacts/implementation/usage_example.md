# Usage Example — TAD Preliminary Prioritization Engine

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

This example demonstrates an accepted preliminary ranking with mandatory synthetic-support flags.
-->

## example
The orchestration layer calls motor_033 after motor_032 has emitted synthetic support for three active inference cases competing for analyst attention. The phase contract permits preliminary prioritization only as a non-final analytic signal, and all support, case, contract, and schema references resolve through motor_002 version records. The expected result is a traceable `preliminary_priority_register` that orders the cases for review without closing any inference case or producing TAD final.

## inputs_used
```json
{
  "synthetic_ml_support_register": {
    "register_id": "SMSR-033-HP-001",
    "source_ref": "motor_032:SMSR-033-HP-001",
    "support_items": [
      {
        "support_item_id": "SUP-IC-200",
        "source_problem_ref": "IC-200",
        "expert_spec_ref": "EPS-200",
        "synthetic_support_flag": true,
        "non_evidentiary_flag": true,
        "intended_use": "preliminary_support",
        "domain_validity_limits": "case_scope=renewable-grid-dispatch synthetic bundle SB-200 only",
        "limitations_note": "Synthetic support only; not field evidence or validation data.",
        "priority_signal": 0.86,
        "support_quality": "strong",
        "version_record_ref": "VR-SUP-200"
      },
      {
        "support_item_id": "SUP-IC-100",
        "source_problem_ref": "IC-100",
        "expert_spec_ref": "EPS-100",
        "synthetic_support_flag": true,
        "non_evidentiary_flag": true,
        "intended_use": "preliminary_support",
        "domain_validity_limits": "case_scope=renewable-grid-dispatch synthetic bundle SB-100 only",
        "limitations_note": "Synthetic support only; not field evidence or validation data.",
        "priority_signal": 0.63,
        "support_quality": "moderate",
        "version_record_ref": "VR-SUP-100"
      },
      {
        "support_item_id": "SUP-IC-300",
        "source_problem_ref": "IC-300",
        "expert_spec_ref": "EPS-300",
        "synthetic_support_flag": true,
        "non_evidentiary_flag": true,
        "intended_use": "preliminary_support",
        "domain_validity_limits": "case_scope=renewable-grid-dispatch synthetic bundle SB-300 only",
        "limitations_note": "Synthetic support only; not field evidence or validation data.",
        "priority_signal": 0.41,
        "support_quality": "limited",
        "version_record_ref": "VR-SUP-300"
      }
    ]
  },
  "inference_cases": [
    {
      "inference_case_id": "IC-100",
      "status": "active",
      "case_scope": "renewable-grid-dispatch",
      "version_record_ref": "VR-CASE-100"
    },
    {
      "inference_case_id": "IC-200",
      "status": "active",
      "case_scope": "renewable-grid-dispatch",
      "version_record_ref": "VR-CASE-200"
    },
    {
      "inference_case_id": "IC-300",
      "status": "active",
      "case_scope": "renewable-grid-dispatch",
      "version_record_ref": "VR-CASE-300"
    }
  ],
  "phase_contracts": [
    {
      "phase_contract_ref": "PC-PRELIM-001",
      "allows_preliminary_prioritization": true,
      "forbids_final_decision": true,
      "version_record_ref": "VR-PC-PRELIM-001"
    }
  ],
  "version_records": {
    "SUP-IC-100": "VR-SUP-100",
    "SUP-IC-200": "VR-SUP-200",
    "SUP-IC-300": "VR-SUP-300",
    "IC-100": "VR-CASE-100",
    "IC-200": "VR-CASE-200",
    "IC-300": "VR-CASE-300",
    "PC-PRELIM-001": "VR-PC-PRELIM-001",
    "motor_033_schema": "VR-SCHEMA-033-001",
    "lineage_id": "LIN-033-HP-001"
  }
}
```

## expected_output
```json
{
  "status": "accepted",
  "preliminary_priority_register": {
    "record_id": "ppr-033-smsr-033-hp-001-<hash>",
    "produced_by_motor": "motor_033",
    "source_ref": "motor_032:SMSR-033-HP-001",
    "source_problem_ref": "IC-100,IC-200,IC-300",
    "expert_spec_ref": "EPS-100,EPS-200,EPS-300",
    "intended_use": "preliminary_support",
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true,
    "rank_is_preliminary": true,
    "ranking_basis_ref": "rb-033-smsr-033-hp-001-<hash>",
    "rank_uncertainty_ref": "rur-033-smsr-033-hp-001-<hash>",
    "ranked_cases": [
      {
        "inference_case_id": "IC-200",
        "rank_position": 1,
        "priority_band": "high_preliminary",
        "preliminary_score": 0.86,
        "source_support_refs": ["SUP-IC-200"],
        "phase_contract_refs": ["PC-PRELIM-001"],
        "version_record_refs": ["VR-CASE-200", "VR-PC-PRELIM-001", "VR-SCHEMA-033-001", "VR-SUP-200"],
        "requires_real_evidence": [
          "field_evidence for IC-200 that confirms or revises the synthetic priority signal",
          "validation_data for IC-200 collected outside the synthetic generator assumptions",
          "Verification Bridge review for IC-200 before any closure or TAD-final use"
        ]
      },
      {
        "inference_case_id": "IC-100",
        "rank_position": 2,
        "priority_band": "medium_preliminary",
        "preliminary_score": 0.63
      },
      {
        "inference_case_id": "IC-300",
        "rank_position": 3,
        "priority_band": "low_preliminary",
        "preliminary_score": 0.41
      }
    ],
    "cannot_substitute": [
      "TAD_final",
      "inference_case_closure",
      "field_evidence",
      "validation_data",
      "Validation Data Bridge",
      "Verification Bridge"
    ],
    "status": "emitted"
  },
  "ranking_basis": {
    "record_id": "rb-033-smsr-033-hp-001-<hash>",
    "signal_fields_used": ["priority_signal", "support_quality", "domain_validity_limits", "limitations_note"],
    "weighting_rule": "For each active case, use valid motor_032 support only. The preliminary score is the maximum numeric priority_signal for that case after epistemic flag, phase, provenance, and domain-validity checks. Cases are ordered by descending preliminary score.",
    "tie_break_rule": "Exact score ties are retained in rank_uncertainty_record.tie_groups and ordered deterministically by inference_case_id for a stable register.",
    "excluded_signal_reasons": []
  },
  "rank_uncertainty_record": {
    "record_id": "rur-033-smsr-033-hp-001-<hash>",
    "tie_groups": [],
    "rank_separation_notes": [],
    "conflicting_signal_notes": [],
    "insufficient_support_case_refs": [],
    "uncertainty_level": "low",
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true,
    "rank_is_preliminary": true
  }
}
```

## notes
The example assumes motor_032 support items already carry the required synthetic epistemic labels and that motor_002 lineage resolves every referenced source object. Motor_033 does not mutate the support register, inference cases, phase contract, or version records. The rank order is a subordinate exploration signal only: it cannot be used as TAD final, inference case closure, field evidence, validation data, Validation Data Bridge, or Verification Bridge.
