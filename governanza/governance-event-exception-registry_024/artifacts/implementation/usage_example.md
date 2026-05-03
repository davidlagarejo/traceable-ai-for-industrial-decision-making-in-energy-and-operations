# Usage Example — Governance Event & Exception Registry

Motor ID: motor_024

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar anomalías, overrides, excepciones recurrentes y tensiones de gobernanza relevantes.
why_it_exists:  La gobernanza necesita señales explícitas y no solo intuición.
key_inputs:     exception events from all motors, override records
key_outputs:    governance_event, exception_record, tension_signal
key_objects:    GovernanceEvent, ExceptionRecord, TensionSignal
what_not_to_do: No resuelve excepciones. No cambia políticas. Solo registra para revisión humana.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Solo requiere motor_001 y motor_002.

-->

## example
Un motor downstream (motor_004) detecta que recibió un payload vacío y no puede continuar. Emite un evento de excepción hacia motor_024 para que quede registrado en el sistema de gobernanza. motor_024 valida los metadatos mínimos, genera un GovernanceEvent inmutable y un ExceptionRecord vinculado, ambos con trazabilidad completa hacia el lineage de motor_002.

```python
from governance_event_registry.engine import GovernanceEventRegistry

registry = GovernanceEventRegistry()

result = registry.register_exception(
    source_motor_id="motor_004",
    exception_code="INGESTION_EMPTY_PAYLOAD",
    exception_payload={"source_ref": "src_001", "payload_size_bytes": 0},
    captured_at="2026-04-16T10:00:00Z",
    phase_contract_ref="phase_01_capture",
    lineage_context_ref="lineage_abc123",
)

print(result.governance_event.governance_event_id)
print(result.exception_record.exception_code)
```

## inputs_used
```python
{
    "source_motor_id": "motor_004",
    "exception_code": "INGESTION_EMPTY_PAYLOAD",
    "exception_payload": {
        "source_ref": "src_001",
        "payload_size_bytes": 0
    },
    "captured_at": "2026-04-16T10:00:00Z",
    "phase_contract_ref": "phase_01_capture",
    "lineage_context_ref": "lineage_abc123"
}
```

## expected_output
```python
GovernanceEventResult(
    governance_event=GovernanceEvent(
        governance_event_id="governance_event_<sha256_24chars>",
        event_type="exception",
        source_motor_id="motor_004",
        captured_at="2026-04-16T10:00:00Z",
        phase_contract_ref="phase_01_capture",
        lineage_id="lineage_abc123",
        raw_event_payload={
            "source_motor_id": "motor_004",
            "exception_code": "INGESTION_EMPTY_PAYLOAD",
            "exception_payload": {"source_ref": "src_001", "payload_size_bytes": 0},
            "captured_at": "2026-04-16T10:00:00Z",
            "phase_contract_ref": "phase_01_capture",
            "lineage_context_ref": "lineage_abc123"
        },
        produced_by_motor="motor_024",
        produced_at="<timestamp_de_emision>",
        version_id="governance_event_<sha256_24chars>:v1",
        version_hash="<sha256_del_contenido>",
        created_at="<timestamp_de_emision>",
        updated_at="<timestamp_de_emision>",
        parent_id="lineage_abc123"
    ),
    exception_record=ExceptionRecord(
        exception_record_id="exception_record_<sha256_24chars>",
        governance_event_id="governance_event_<sha256_24chars>",
        source_motor_id="motor_004",
        exception_code="INGESTION_EMPTY_PAYLOAD",
        exception_payload={"source_ref": "src_001", "payload_size_bytes": 0},
        lineage_id="lineage_abc123",
        produced_by_motor="motor_024",
        ...
    ),
    tension_signal=None,
    rejection=None
)
```

## notes
- El motor requiere que `phase_contract_ref` esté vigente según motor_001; si contiene tokens de denegación (`:deny`, `:blocked`, `:forbid`), el evento es rechazado.
- El `governance_event_id` es determinístico: los mismos inputs producen el mismo ID. El segundo intento con inputs idénticos resulta en rechazo `GOV_DUPLICATE_EVENT`.
- El campo `raw_event_payload` preserva el payload exactamente como fue recibido, sin modificaciones ni normalización.
- Para registrar tensiones entre motores, usar `registry.register_tension(motor_a_id, motor_b_id, conflict_description, ...)`.
- Para registrar overrides, usar `registry.register_override(override_id, policy_ref, ...)`.
- El motor no resuelve las excepciones ni activa ningún workflow; el output es solo registro persistente para revisión humana.
