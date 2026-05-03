# Failure Modes Spec — Governance Event & Exception Registry

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

## failure_modes_list
- `GOV_MISSING_REQUIRED_FIELD`: el evento entrante llega sin `source_motor_id`, `captured_at` o `lineage_context_ref`. Condición de activación: cualquier motor fuente emite la señal sin completar el envelope mínimo de metadatos. El motor rechaza con este código y no produce ningún objeto de salida.
- `GOV_PHASE_CONTRACT_DENIED`: el `phase_contract_ref` contiene tokens de denegación (`:deny`, `:blocked`, `:forbid`) o no está registrado en motor_001. Condición: el motor fuente emite la señal fuera de la fase activa o con contrato caducado.
- `GOV_DUPLICATE_EVENT`: el `governance_event_id` calculado ya existe en el almacenamiento del motor. Condición: el motor fuente reintenta sin control de idempotencia. El segundo intento se rechaza; el primer registro se mantiene intacto.
- `GOV_UNKNOWN_EVENT_TYPE`: el tipo del evento no es `exception`, `override` ni `tension`. Condición: cambio de interfaz en el motor fuente sin actualización del contrato de motor_024.
- `GOV_INVALID_TIMESTAMP`: `captured_at` tiene formato inválido o es un timestamp futuro. Condición: error de serialización o clock skew en el motor fuente.
- `GOV_INVALID_TENSION_ACTORS`: en un evento de tipo `tension`, `motor_a_id == motor_b_id`. Condición: el motor fuente construye mal el envelope de tensión.
- `GOV_PARTIAL_OUTPUT_ON_REJECTION`: el motor emite un objeto de salida parcial (GovernanceEvent sin ExceptionRecord, o ExceptionRecord sin GovernanceEvent raíz) cuando la validación falla. Condición de activación: error en la lógica de validación que permite continuar el flujo de emisión tras detectar un fallo.

## anti_patterns
- **Validar campos de forma parcial antes de emitir objetos**: verificar `source_motor_id` pero no `lineage_context_ref`, resultando en objetos de salida sin trazabilidad completa. La validación debe ser atómica: todos los campos mínimos o ningún objeto se emite.
- **Reutilizar `governance_event_id` sin verificar existencia previa**: generar el ID determinístico y sobrescribir el objeto existente en lugar de rechazar el duplicado. Esto destruye la inmutabilidad del registro histórico.
- **Mutar el `raw_event_payload` antes de persistir**: limpiar, normalizar o enriquecer el payload entrante antes de almacenarlo en GovernanceEvent. Viola el principio de preservación sin modificación.
- **Propagar excepciones del motor fuente como errores de motor_024**: exponer trazas internas del motor fuente en el rechazo de motor_024. El rechazo debe usar únicamente los códigos estructurados propios (GOV_*).
- **Emitir TensionSignal sin GovernanceEvent raíz**: crear el objeto derivado antes de confirmar que el GovernanceEvent fue persistido correctamente. Si la persistencia del raíz falla, el derivado queda huérfano.

## degradation_signals
- Tasa de rechazos `GOV_MISSING_REQUIRED_FIELD` superior al 5% del total de eventos en una sesión: indica que uno o más motores fuente no cumplen el contrato de envelope mínimo.
- Aparición de `GOV_DUPLICATE_EVENT` de forma repetida (>3 veces) para el mismo `source_motor_id` en un intervalo de 60 segundos: indica que el motor fuente está en bucle de reintentos sin control de idempotencia.
- Ausencia total de GovernanceEvents durante una sesión larga (>10 minutos) con múltiples motores activos: puede indicar routing roto o supresión silenciosa de errores en los motores fuente.
- Presencia de GovernanceEvents con `version_hash` inconsistente respecto al contenido del objeto: indica posible mutación post-emisión o error en el cálculo del hash.
- Ratio entre GovernanceEvents y sus objetos derivados esperados (ExceptionRecord para eventos de tipo exception) inferior a 1.0: indica que algunos eventos de excepción no están generando su ExceptionRecord correspondiente.

## expensive_errors
- **Sobrescritura silenciosa de GovernanceEvents duplicados**: si el motor no detecta duplicados y sobrescribe el registro original, la trazabilidad histórica se destruye retroactivamente. Reparar requiere reconstruir manualmente los objetos afectados desde los logs de los motores fuente, lo cual puede ser imposible si no hay otro mecanismo de preservación.
- **Emisión de objetos con `lineage_id` nulo o genérico ("unknown")**: una vez que un GovernanceEvent sin lineage válido es persistido, queda desconectado de la cadena de trazabilidad de motor_002. Corregirlo requiere reemitir el evento con el lineage correcto, pero el original incorrecto también persiste, creando ambigüedad histórica.
- **Aceptar eventos con `phase_contract_ref` inválido sin rechazo explícito**: GovernanceEvents fuera de fase quedan en el registro mezclados con eventos válidos, requiriendo auditoría manual posterior para distinguir señales legítimas de ruido.
