# Failure Modes — Governance Event & Exception Registry

Motor ID: motor_024


## failure_modes_list
- `GOV_MISSING_REQUIRED_FIELD`: el evento entrante llega sin `source_motor_id`, `captured_at` o `lineage_context_ref`. Síntoma: el motor emite un rechazo estructurado y no produce GovernanceEvent. Causa típica: motor fuente emitió la señal sin completar el envelope de metadatos mínimos.
- `GOV_PHASE_CONTRACT_DENIED`: el `phase_contract_ref` del evento no está autorizado por motor_001. Síntoma: el motor rechaza el evento aunque el payload sea válido. Causa típica: el motor fuente intentó registrar un evento fuera de la fase activa, o con un contrato caducado.
- `GOV_DUPLICATE_EVENT`: el motor recibe dos veces el mismo evento con idéntico `governance_event_id` calculado. Síntoma: el segundo intento es rechazado con código de duplicado; el primer registro se mantiene intacto. Causa típica: retry sin idempotency check en el motor fuente.
- `GOV_UNKNOWN_EVENT_TYPE`: el tipo del evento no es `exception`, `override` ni `tension`. Síntoma: el motor rechaza el evento con código de tipo desconocido. Causa típica: cambio de interfaz en el motor fuente sin actualización del contrato.
- `GOV_INVALID_TIMESTAMP`: `captured_at` tiene formato inválido o está en el futuro. Síntoma: el motor rechaza el evento. Causa típica: error de serialización o clock skew en el motor fuente.

## anti_patterns
- **Usar motor_024 como log genérico del sistema**: enviarle eventos informativos, métricas de rendimiento o trazas de debug que no representan anomalías, overrides ni tensiones. Esto satura el registro con ruido y oscurece las señales de gobernanza reales.
- **Omitir `lineage_context_ref` en el evento entrante**: algunos motores emiten la señal sin adjuntar la referencia de lineage de motor_002, asumiendo que motor_024 lo resolverá. El motor rechaza estos eventos, dejando la excepción sin registro y sin trazabilidad.
- **Invocar motor_024 para tomar decisiones**: usar los outputs de GovernanceEvent como señal para que el motor fuente cambie su comportamiento automáticamente, sin revisión humana. Esto viola el límite del motor y convierte un registro en un mecanismo de control no autorizado.

## degradation_signals
- Tasa de rechazos `GOV_MISSING_REQUIRED_FIELD` superior al 5% del total de eventos en una sesión: indica que uno o más motores fuente no están completando correctamente el envelope de metadatos.
- Aparición de `GOV_DUPLICATE_EVENT` de forma repetida para el mismo `source_motor_id` en un intervalo corto: indica que el motor fuente está reintentando sin idempotency check, lo que puede inflar artificialmente el contador de eventos.
- Ausencia total de GovernanceEvents durante una sesión larga con múltiples motores activos: puede indicar que las señales de excepción no están llegando a motor_024, posiblemente por un problema de routing o porque los motores fuente están suprimiendo errores en lugar de reportarlos.
- Presencia de GovernanceEvents con `lineage_id` nulo o genérico ("unknown"): indica que el contrato de lineage de motor_002 no está siendo respetado por algún motor fuente.
