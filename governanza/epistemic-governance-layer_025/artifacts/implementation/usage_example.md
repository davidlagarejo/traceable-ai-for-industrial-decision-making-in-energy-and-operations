# Usage Example — Epistemic Governance Layer

Motor ID: motor_025

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar tensiones estructurales, inflación de excepciones, insuficiencia taxonómica y distinguir cambio local, estructural o constitucional.
why_it_exists:  Evita que el framework crezca rompiendo su constitución en silencio.
key_inputs:     conformance_records (motor_022), governance_events (motor_024), phase_contracts (motor_001)
key_outputs:    epistemic_tension_record, constitutional_change_signal, governance_health_report
key_objects:    EpistemicTension, ConstitutionalSignal, GovernanceHealthReport
what_not_to_do: No modifica contratos ni políticas directamente. Solo detecta y señaliza tensiones estructurales.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Capa de gobernanza de más alto nivel.

Implementation example completed for Gate 5 validation.
-->

## example
El operador de gobernanza ejecuta `motor_025` después de que `motor_022` registra fallas de conformidad y `motor_024` registra tres overrides repetidos contra el mismo contrato de fase. El motor recibe solo registros estructurados con IDs, timestamps, referencias de contrato, provenance y lineage; como resultado detecta inflación de excepciones, emite una señal de revisión estructural y resume el estado de salud de la ventana evaluada.

## inputs_used
```json
{
  "phase_contracts": [
    {
      "contract_id": "PCR-014-v2",
      "phase_id": "phase_2",
      "allowed_inputs": ["normalized_evidence"],
      "allowed_outputs": ["phase_2_report"],
      "handoff_limits": ["no_unregistered_output_override"],
      "responsibility_limits": ["phase_2_must_not_emit_phase_3_outputs"],
      "version": "2.0.0",
      "status": "active"
    }
  ],
  "conformance_records": [
    {
      "record_id": "CR-401",
      "target_motor_id": "motor_014",
      "contract_ref": "PCR-014-v2",
      "status": "FAIL",
      "severity": "high",
      "findings": [{"type": "boundary_drift", "detail": "phase_2 output override repeated"}],
      "checked_at": "2026-04-18T10:00:00Z",
      "provenance_ref": "prov:cr:401"
    },
    {
      "record_id": "CR-402",
      "target_motor_id": "motor_014",
      "contract_ref": "PCR-014-v2",
      "status": "FAIL",
      "severity": "high",
      "findings": [{"type": "conformance_gap", "detail": "handoff limit bypassed"}],
      "checked_at": "2026-04-18T10:05:00Z",
      "provenance_ref": "prov:cr:402"
    }
  ],
  "governance_events": [
    {
      "event_id": "GE-771",
      "event_type": "exception_override",
      "affected_motor_id": "motor_014",
      "severity": "high",
      "recurrence_key": "phase_2_output_override",
      "contract_ref": "PCR-014-v2",
      "occurred_at": "2026-04-18T10:10:00Z",
      "lineage_ref": "lin:ge:771"
    },
    {
      "event_id": "GE-772",
      "event_type": "exception_override",
      "affected_motor_id": "motor_014",
      "severity": "high",
      "recurrence_key": "phase_2_output_override",
      "contract_ref": "PCR-014-v2",
      "occurred_at": "2026-04-18T10:12:00Z",
      "lineage_ref": "lin:ge:772"
    },
    {
      "event_id": "GE-773",
      "event_type": "exception_override",
      "affected_motor_id": "motor_014",
      "severity": "high",
      "recurrence_key": "phase_2_output_override",
      "contract_ref": "PCR-014-v2",
      "occurred_at": "2026-04-18T10:14:00Z",
      "lineage_ref": "lin:ge:773"
    }
  ],
  "evaluated_at": "2026-04-18T10:15:00Z"
}
```

## expected_output
```json
{
  "epistemic_tension_record": [
    {
      "tension_type": "exception_inflation",
      "severity": "high",
      "change_pressure": "structural",
      "evidence_refs": ["CR-401", "CR-402", "GE-771", "GE-772", "GE-773"],
      "governing_contract_refs": ["PCR-014-v2"],
      "recurrence_key": "phase_2_output_override",
      "affected_scope": {
        "motor_ids": ["motor_014"],
        "phase_ids": ["phase_2"],
        "contract_ids": ["PCR-014-v2"]
      },
      "produced_by_motor": "motor_025"
    }
  ],
  "constitutional_change_signal": [
    {
      "change_class": "structural",
      "recommended_review_path": "structural_design_review",
      "signal_severity": "high",
      "affected_contract_refs": ["PCR-014-v2"],
      "originating_tension_ids": ["motor_025:tension:<stable-hash>"],
      "produced_by_motor": "motor_025"
    }
  ],
  "governance_health_report": {
    "window_start": "2026-04-18T10:00:00Z",
    "window_end": "2026-04-18T10:14:00Z",
    "evaluated_contract_refs": ["PCR-014-v2"],
    "tension_counts_by_type": {
      "exception_inflation": 1,
      "taxonomic_insufficiency": 0,
      "boundary_drift": 0,
      "conformance_gap": 0,
      "structural_conflict": 0
    },
    "severity_counts": {"low": 0, "medium": 0, "high": 1, "critical": 0},
    "exception_inflation_score": 3.0,
    "governance_status": "escalate",
    "evidence_coverage": {
      "conformance_records_count": 2,
      "governance_events_count": 3,
      "phase_contracts_count": 1,
      "rejected_records_count": 0
    },
    "produced_by_motor": "motor_025"
  }
}
```

## notes
El ejemplo presupone que todas las referencias de contrato resuelven contra `phase_contracts` y que los IDs de evidencia no están duplicados con payloads conflictivos. El motor no aprueba la excepción, no modifica el contrato `PCR-014-v2`, no crea términos taxonómicos y no cambia estados de motores; solo produce registros trazables para revisión de gobernanza.
