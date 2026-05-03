# Acceptance Tests — Governance Event & Exception Registry

Motor ID: motor_024


## happy_path
**Escenario: motor_004 emite excepción por payload vacío**
- Input: `exception_event` con `source_motor_id="motor_004"`, `exception_code="INGESTION_EMPTY_PAYLOAD"`, `captured_at="2026-04-16T10:00:00Z"`, `lineage_context_ref="lineage_abc123"`, `phase_contract_ref="phase_01_capture"`.
- Acción: el motor valida los campos mínimos, genera un `governance_event_id` determinístico, preserva el payload completo.
- Output esperado: `GovernanceEvent` con `event_type="exception"`, `source_motor_id="motor_004"`, `lineage_id="lineage_abc123"`, `produced_by_motor="motor_024"`. Además, un `ExceptionRecord` con `exception_code="INGESTION_EMPTY_PAYLOAD"` vinculado al mismo `governance_event_id`.

**Escenario: override autorizado registrado**
- Input: `override_record` con `override_id="ovr_001"`, `source_motor_id="motor_001"`, `policy_ref="phase_01_capture:deny"`, `captured_at="2026-04-16T10:05:00Z"`, `lineage_context_ref="lineage_abc123"`.
- Output esperado: `GovernanceEvent` con `event_type="override"` y los campos de trazabilidad completos. No se produce ExceptionRecord ni TensionSignal.

## edge_cases
**Caso: mismo evento enviado dos veces (duplicado)**
- Input: dos invocaciones idénticas con los mismos valores de `source_motor_id`, `exception_code`, `captured_at` y `lineage_context_ref`.
- Comportamiento correcto: el segundo intento debe ser detectado como duplicado (mismo `governance_event_id` generado determinísticamente). El motor no sobrescribe el primer registro; emite un rechazo indicando que el evento ya existe.

**Caso: señal de tensión entre motor_013 y motor_014**
- Input: `tension_signal_input` con `motor_a_id="motor_013"`, `motor_b_id="motor_014"`, `conflict_description="motor_013 requiere datos de motor_012 aún no disponibles, motor_014 ya inició inferencia"`, `captured_at="2026-04-16T10:10:00Z"`, `lineage_context_ref="lineage_abc123"`.
- Comportamiento correcto: se emite un `GovernanceEvent` de tipo `tension` y un `TensionSignal` con ambos motor_id y la descripción completa. El motor no intenta resolver ni priorizar ninguno de los dos motores.

**Caso: evento con timestamp futuro**
- Input: `exception_event` con `captured_at` en el futuro respecto al momento de procesamiento.
- Comportamiento correcto: el motor rechaza el evento con código `GOV_INVALID_TIMESTAMP` y no produce ningún objeto de salida.

## rejection_criteria
1. **Campo mínimo ausente**: si `source_motor_id`, `captured_at` o `lineage_context_ref` están vacíos, nulos o son valores inestables ("unknown", "undefined"), el motor emite un rechazo estructurado con código `GOV_MISSING_REQUIRED_FIELD` y no produce ningún objeto de salida.
2. **Phase contract denegado**: si `phase_contract_ref` no está autorizado por motor_001 para la fase actual (contiene tokens `:deny`, `:blocked`, `:forbid`), el motor emite un rechazo con código `GOV_PHASE_CONTRACT_DENIED`.
3. **Tipo de evento desconocido**: si el tipo del evento entrante no es `exception`, `override` ni `tension`, el motor emite un rechazo con código `GOV_UNKNOWN_EVENT_TYPE`.
4. **Duplicado detectado**: si el `governance_event_id` calculado ya existe en el registro persistente, el motor emite un rechazo con código `GOV_DUPLICATE_EVENT` sin sobrescribir el original.
