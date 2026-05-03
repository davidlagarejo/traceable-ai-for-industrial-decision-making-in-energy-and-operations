# Usage Example — Verification Bridge Engine

Motor ID: motor_019

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir claims y tensiones en rutas explícitas de endurecimiento de evidencia.
why_it_exists:  Sin este motor el sistema se queda en hipótesis y reporting, sin puente real a verificación.
key_inputs:     inference_records (motor_014), validation_data (motor_018), phase_contracts (motor_001)
key_outputs:    verification_path, hardening_agenda, evidence_gap_record
key_objects:    VerificationPath, HardeningAgenda, EvidenceGap
what_not_to_do: No cierra claims automáticamente. No puede ser reemplazado por synthetic_support.
design_notes:   Produce field_evidence level cuando completa verificación. Depende de motor_014, motor_018 y motor_001.

All placeholder markers in this file have been replaced with governed content.
-->

## example
Un coordinador de validacion llama a `VerificationBridgeEngine` despues de que motor_014 emite una inferencia sobre una brecha de energia en una instalacion y motor_018 entrega una medicion real aceptada. El motor debe convertir esa inferencia en una ruta de verificacion trazable, conservar el enlace al contrato de fase y abrir gaps para la confirmacion de mantenimiento y la evidencia de campo que aun faltan. El resultado no cierra el claim ni produce un reporte; solo entrega la ruta, la agenda y los gaps necesarios para endurecer evidencia.

## inputs_used
```json
{
  "inference_records": [
    {
      "inference_record_id": "inf_014_power_001",
      "claim_id": "claim_facility_power_gap",
      "tension_id": null,
      "confidence_state": "hypothesis_with_real_indicators",
      "evidentiary_basis": ["val_018_meter_031"],
      "unresolved_gaps": ["maintenance_log_confirmation"],
      "lineage_refs": ["lin_014_power_001"],
      "version_id": "motor_014:v:inf_014_power_001"
    }
  ],
  "validation_data": [
    {
      "validation_data_id": "val_018_meter_031",
      "claim_id": "claim_facility_power_gap",
      "evidence_level": "validation_data",
      "measured_value": {
        "metric": "power_draw_kw",
        "value": 187.4,
        "unit": "kW"
      },
      "source_provenance": "site_meter_export",
      "quality_status": "accepted",
      "lineage_refs": ["lin_018_meter_031"],
      "version_id": "motor_018:v:val_018_meter_031"
    }
  ],
  "phase_contracts": [
    {
      "contract_id": "phase4_verification_v2",
      "contract_version": "2.0.0",
      "allowed_inputs": ["inference_records", "validation_data"],
      "allowed_outputs": [
        "verification_path",
        "hardening_agenda",
        "evidence_gap_record"
      ],
      "evidence_thresholds": {
        "claim_facility_power_gap": "field_evidence"
      },
      "handoff_rules": {
        "requires_lineage": true,
        "allow_synthetic_support": false
      },
      "owner_role": "field_validation_lead"
    }
  ]
}
```

## expected_output
```json
{
  "verification_path": [
    {
      "motor_id": "motor_019",
      "target_ref": {
        "target_type": "claim",
        "claim_id": "claim_facility_power_gap",
        "tension_id": null,
        "target_label": null
      },
      "source_inference_ref": "inf_014_power_001",
      "source_tension_ref": null,
      "phase_contract_id": "phase4_verification_v2",
      "contract_version": "2.0.0",
      "current_evidence_level": "validation_data",
      "target_evidence_level": "field_evidence",
      "linked_evidence_refs": [
        {
          "upstream_motor_id": "motor_018",
          "upstream_artifact_ref": "val_018_meter_031",
          "evidence_level": "validation_data",
          "quality_status": "accepted",
          "lineage_ref": "lin_018_meter_031"
        }
      ],
      "required_evidence": [
        {
          "evidence_type": "measurement",
          "required_level": "validation_data",
          "satisfied_by_refs": ["val_018_meter_031"],
          "is_satisfied": true,
          "gap_ref": null
        },
        {
          "evidence_type": "source_confirmation",
          "required_level": "field_evidence",
          "satisfied_by_refs": [],
          "is_satisfied": false,
          "gap_ref": "motor_019:evidence_gap:{stable_suffix}"
        },
        {
          "evidence_type": "site_validation",
          "required_level": "field_evidence",
          "satisfied_by_refs": [],
          "is_satisfied": false,
          "gap_ref": "motor_019:evidence_gap:{stable_suffix}"
        }
      ],
      "status": "actionable",
      "review_trigger": "blocking_evidence_gap",
      "lineage_refs": [
        "lin_014_power_001",
        "lin_018_meter_031",
        "motor_014:v:inf_014_power_001",
        "motor_018:v:val_018_meter_031",
        "phase4_verification_v2@2.0.0"
      ],
      "produced_by_motor": "motor_019",
      "parent_id": null
    }
  ],
  "hardening_agenda": {
    "motor_id": "motor_019",
    "path_refs": ["motor_019:verification_path:{stable_suffix}"],
    "blocking_gaps": [
      "motor_019:evidence_gap:{source_confirmation_suffix}",
      "motor_019:evidence_gap:{site_validation_suffix}"
    ],
    "owner_role": "field_validation_lead",
    "review_trigger": "blocking_evidence_gap",
    "status": "partially_blocked",
    "prioritized_actions": [
      {
        "action_type": "confirm_source",
        "priority": "blocking",
        "expected_evidence_level": "validation_data",
        "action_status": "ready"
      },
      {
        "action_type": "obtain_observation",
        "priority": "blocking",
        "expected_evidence_level": "field_evidence",
        "action_status": "ready"
      }
    ]
  },
  "evidence_gap_record": [
    {
      "motor_id": "motor_019",
      "target_ref": {
        "target_type": "claim",
        "claim_id": "claim_facility_power_gap",
        "tension_id": null
      },
      "missing_evidence_type": "source_confirmation",
      "gap_severity": "blocking",
      "blocking_reason": "upstream unresolved gap remains open: maintenance_log_confirmation",
      "recommended_next_action": "confirm the source record and attach traceable validation data",
      "related_validation_data_refs": [],
      "resolved_by_ref": null,
      "status": "open"
    },
    {
      "motor_id": "motor_019",
      "target_ref": {
        "target_type": "claim",
        "claim_id": "claim_facility_power_gap",
        "tension_id": null
      },
      "missing_evidence_type": "site_validation",
      "gap_severity": "blocking",
      "blocking_reason": "linked validation data is below the field_evidence threshold",
      "recommended_next_action": "collect authorized field evidence or site validation data",
      "related_validation_data_refs": ["val_018_meter_031"],
      "resolved_by_ref": null,
      "status": "open"
    }
  ],
  "errors": []
}
```

## notes
El ejemplo presupone que `phase4_verification_v2` autoriza los outputs `verification_path`, `hardening_agenda` y `evidence_gap_record`, y que la medicion de motor_018 tiene provenance real, lineage y calidad aceptada. Si la evidencia viene marcada como `synthetic_support`, `non_evidentiary` o sin `source_provenance`, el motor rechaza el bundle con `INVALID_EVIDENCE_LEVEL` y no emite objetos parciales. La salida mantiene referencias inmutables a motor_014, motor_018 y motor_001; cualquier correccion upstream debe producir una nueva version en el motor de origen.
