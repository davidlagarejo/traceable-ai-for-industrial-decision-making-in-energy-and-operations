# Operational Rules — Governance Event & Exception Registry

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

## rules
1. Todo evento entrante debe ser validado contra los campos mínimos requeridos antes de ser aceptado; si falla la validación, el motor emite un rechazo estructurado y no produce ningún objeto de salida.
2. Cada evento aceptado produce exactamente un `GovernanceEvent` inmutable; no se produce ningún objeto adicional sin un `GovernanceEvent` raíz.
3. El `governance_event_id` se genera de forma determinística a partir de los campos semánticos del evento (`source_motor_id`, `event_type`, `captured_at`, `lineage_context_ref`), garantizando reproducibilidad.
4. El campo `produced_by_motor` de todos los objetos emitidos debe ser siempre `motor_024`; no se puede delegar la atribución a otro motor.
5. El `lineage_id` de todos los objetos emitidos debe heredar de `lineage_context_ref` del evento entrante; no se permite un lineage_id autogenerado sin referencia a motor_002.
6. Ningún objeto emitido puede ser sobrescrito ni modificado una vez persistido; si el mismo evento llega dos veces, el segundo intento debe resultar en detección de duplicado sin sobrescritura.
7. El motor opera bajo el contrato de fase autorizado por motor_001; si el phase_contract_ref no está vigente, el motor rechaza el evento sin registro parcial.

## invariants
- Antes y después de cada operación: `governance_event_id` nunca es nulo en un objeto de salida aceptado.
- Antes y después de cada operación: `lineage_id` nunca es nulo en ningún objeto emitido.
- Antes y después de cada operación: el payload del evento entrante está preservado sin modificaciones en el objeto de salida correspondiente.
- Antes y después de cada operación: no existe ningún `ExceptionRecord` ni `TensionSignal` sin un `GovernanceEvent` raíz válido en la misma sesión.
- Antes y después de cada operación: el número de objetos emitidos no supera el número de eventos aceptados multiplicado por el número máximo de outputs por evento (1 GovernanceEvent + 0..1 objeto derivado).

## forbidden_operations
- Resolver excepciones: el motor no puede aplicar ninguna acción correctiva, fallback, compensación ni transformación de comportamiento basada en los eventos registrados.
- Modificar políticas o contratos: el motor no puede actualizar, anular ni extender ningún contrato de fase, regla operativa ni configuración de otro motor.
- Corregir o enriquecer el payload del evento: el motor no puede inferir, completar ni normalizar campos faltantes o incorrectos en el evento entrante.
- Emitir alertas o notificaciones activas: la generación de alertas, notificaciones push o activaciones de workflow es responsabilidad de otros motores.
- Agregar o consolidar eventos: el motor no puede fusionar dos eventos en un solo registro ni deduplicar señales entrantes.
