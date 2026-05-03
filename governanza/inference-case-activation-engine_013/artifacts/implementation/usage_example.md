# Usage Example — Inference Case Activation Engine

Motor ID: motor_013

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Activar casos inferenciales gobernados a partir de facility_prior, bundles y triggers.
why_it_exists:  Separa selección de casos del análisis del Decision Core.
key_inputs:     facility_prior (motor_012), library_objects (motor_011), quality_records (motor_007)
key_outputs:    inference_case, activation_record, trigger_log
key_objects:    InferenceCase, ActivationRecord, TriggerCondition
what_not_to_do: No analiza los casos. No produce conclusiones. Solo activa y registra.
design_notes:   Crea los casos que alimentan al Decision Core. Sin este motor, motor_014 no tiene input.

All implementation-stage placeholders in this usage example have been resolved.
-->

## example
A Fase 2 preparation job calls `InferenceCaseActivationEngine` after `motor_012` has emitted a facility prior for `FAC-221`, `motor_011` has supplied a governed energy trigger, and `motor_007` has marked the prior, bundle and library object as fit. The motor evaluates the trigger against explicit bundle signal data, opens one governed inference case for `motor_014`, and records the activation and trigger evaluation without producing any analytical conclusion.

## inputs_used
```json
{
  "facility_prior": {
    "prior_id": "prior-FAC-221-v3",
    "facility_id": "FAC-221",
    "prior_version": "3.0.0",
    "scope": "facility_energy",
    "lineage_id": "lin-prior-221-3",
    "lineage_refs": ["lin-prior-221-3"],
    "provenance_refs": ["prov-prior-221", "prov-bundle-energy-221"],
    "contextual_bundles": [
      {
        "bundle_id": "bundle-energy-221",
        "context_scope": "facility_energy",
        "signals": {
          "energy_variance_band": "high"
        }
      }
    ]
  },
  "library_objects": [
    {
      "library_object_id": "lib-energy-gap-001",
      "version": "1.4.0",
      "scope": "facility_energy",
      "activation_tags": ["energy_variance"],
      "provenance_refs": ["prov-library-energy-gap"],
      "lineage_refs": ["lin-library-energy-gap-001"],
      "triggers": [
        {
          "trigger_condition_id": "trg-energy-gap-high",
          "version": "1.4.0",
          "condition_type": "tag_match",
          "scope": "facility_energy",
          "required_fields": ["contextual_bundles.signals.energy_variance_band"],
          "activation_case_type": "energy_variance_gap",
          "condition_expression_ref": "expr-energy-band-high",
          "expected_value": "high",
          "trigger_priority": 10
        }
      ]
    }
  ],
  "quality_records": [
    {
      "quality_record_id": "qr-prior-221",
      "object_ref": "prior-FAC-221-v3",
      "fitness_status": "PASS",
      "provenance_refs": ["prov-quality-prior-221"],
      "lineage_refs": ["lin-quality-prior-221"]
    },
    {
      "quality_record_id": "qr-bundle-energy-221",
      "object_ref": "bundle-energy-221",
      "fitness_status": "PASS",
      "provenance_refs": ["prov-quality-bundle-energy-221"],
      "lineage_refs": ["lin-quality-bundle-energy-221"]
    },
    {
      "quality_record_id": "qr-lib-energy-gap-001",
      "object_ref": "lib-energy-gap-001",
      "fitness_status": "PASS",
      "provenance_refs": ["prov-quality-library-energy-gap"],
      "lineage_refs": ["lin-quality-library-energy-gap"]
    }
  ]
}
```

## expected_output
```json
{
  "status": "activated",
  "inference_case": [
    {
      "case_id": "case_<stable_hash>",
      "record_id": "case_<stable_hash>",
      "facility_id": "FAC-221",
      "source_prior_ref": "prior-FAC-221-v3",
      "source_prior_version": "3.0.0",
      "contextual_bundle_refs": ["bundle-energy-221"],
      "library_object_refs": ["lib-energy-gap-001"],
      "trigger_condition_ref": "trg-energy-gap-high",
      "supporting_trigger_refs": ["trg-energy-gap-high"],
      "activation_record_ref": "activation_<stable_hash>",
      "activation_case_type": "energy_variance_gap",
      "case_status": "activated",
      "activation_rule_version": "icae_rules_v1",
      "quality_record_refs": [
        "qr-prior-221",
        "qr-bundle-energy-221",
        "qr-lib-energy-gap-001"
      ],
      "conditional_quality_notes": [],
      "activation_rationale_code": "TRIGGER_MATCHED",
      "provenance_refs": [
        "prov-prior-221",
        "prov-bundle-energy-221",
        "prov-library-energy-gap",
        "prov-quality-prior-221",
        "prov-quality-bundle-energy-221",
        "prov-quality-library-energy-gap"
      ],
      "lineage_id": "case_lineage_<stable_hash>",
      "lineage_refs": [
        "lin-prior-221-3",
        "lin-library-energy-gap-001",
        "trg-energy-gap-high",
        "1.4.0",
        "lin-quality-prior-221",
        "lin-quality-bundle-energy-221",
        "lin-quality-library-energy-gap",
        "icae_rules_v1"
      ],
      "source_ref": "prior-FAC-221-v3",
      "produced_by_motor": "motor_013",
      "produced_at": "1970-01-01T00:00:00Z",
      "parent_id": null,
      "version_id": "case_version_<stable_hash>",
      "created_at": "1970-01-01T00:00:00Z",
      "updated_at": "1970-01-01T00:00:00Z",
      "version_hash": "<stable_sha256>"
    }
  ],
  "activation_record": [
    {
      "activation_id": "activation_<stable_hash>",
      "case_id": "case_<stable_hash>",
      "facility_id": "FAC-221",
      "source_prior_ref": "prior-FAC-221-v3",
      "trigger_condition_ref": "trg-energy-gap-high",
      "trigger_version": "1.4.0",
      "activation_case_type": "energy_variance_gap",
      "result": "activated",
      "reason_code": "TRIGGER_MATCHED",
      "activation_rule_version": "icae_rules_v1",
      "produced_by_motor": "motor_013",
      "version_hash": "<stable_sha256>"
    }
  ],
  "trigger_log": [
    {
      "trigger_condition_ref": "trg-energy-gap-high",
      "facility_prior_ref": "prior-FAC-221-v3",
      "facility_id": "FAC-221",
      "library_object_ref": "lib-energy-gap-001",
      "evaluated_field_refs": [
        "contextual_bundles.[bundle-energy-221].signals.energy_variance_band"
      ],
      "evaluation_result": "matched",
      "reason_code": "TRIGGER_MATCHED",
      "activation_record_ref": "activation_<stable_hash>",
      "case_ref": "case_<stable_hash>",
      "produced_by_motor": "motor_013",
      "version_hash": "<stable_sha256>"
    }
  ]
}
```

## notes
The example assumes quality records exist for the prior, the contextual bundle and the selected library object, and that none carries a blocking flag. If the required bundle field is missing, the motor emits a rejected trigger log with `REQUIRED_FIELD_MISSING`; if quality blocks the object, the trigger log and activation record use `QUALITY_GATE_BLOCKED`. The output remains activation-only: it carries deterministic reason codes, references, lineage and version hashes, but no conclusion, confidence claim, recommendation or Decision Core result.
