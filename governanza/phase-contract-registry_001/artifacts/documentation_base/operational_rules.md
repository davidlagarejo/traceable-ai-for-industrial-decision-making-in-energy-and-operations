# Operational Rules — Phase Contract Registry

Motor ID: motor_001

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Definir y hacer cumplir contratos de fase: inputs, outputs, límites y handoffs entre motores.
why_it_exists:  Evita que los motores invadan fases o produzcan outputs indebidos sin contrato explícito.
key_inputs:     phase definitions, motor declarations, contract schemas
key_outputs:    phase_contract records, handoff definitions, limit enforcement signals
key_objects:    PhaseContract, Handoff, ContractViolation
what_not_to_do: No implementa lógica de negocio. No ejecuta motores. Solo registra y valida contratos.
design_notes:   Motor fundacional. No depende de ningún otro. Es el ancla de todo el sistema.

Documentation content completed for this artifact.
-->

## rules
1. Un `PhaseContract` solo puede registrarse si declara `contract_id`, `motor_id`, `phase_id`, `version`, `source_ref`, inputs permitidos, outputs permitidos y límites explícitos.
2. Un `Handoff` solo es válido si el output nombrado existe en `allowed_outputs` del contrato origen y el input nombrado existe en `allowed_inputs` del contrato destino.
3. Todo conflicto, omisión o incompatibilidad detectable debe producir un `ContractViolation`; el motor no puede corregir ni completar el contrato por inferencia silenciosa.
4. Una versión contractual registrada es inmutable; cualquier cambio material debe generar una nueva versión de contrato.
5. Ningún output puede considerarse permitido si no aparece de forma explícita en el contrato vigente del motor y fase correspondiente.
6. Las señales de violación deben conservar la referencia documental que permite reconstruir qué declaración causó el bloqueo.

## invariants
- Todo `PhaseContract` registrado conserva un `contract_id` estable y una `version` no vacía.
- Todo registro emitido conserva `source_ref` para provenance y auditoría.
- La lista de inputs permitidos y la lista de outputs permitidos existen siempre, incluso cuando una de ellas sea deliberadamente vacía.
- Ningún `Handoff` existe sin contrato origen y contrato destino.
- Ningún `ContractViolation` existe sin `violation_code`, `severity`, `field_path` y referencia al contrato afectado.
- El motor nunca transforma una violación en aprobación automática.

## forbidden_operations
- Implementar lógica de negocio, analítica o epistemológica de otros motores.
- Ejecutar motores, iniciar pipelines, correr parsers, compilar reportes o activar procesos downstream.
- Modificar directamente `motor_state.json`, `motor_dependencies.json` o el catálogo de motores durante una validación contractual.
- Crear motores, fases, dependencias o handoffs no declarados por las fuentes autorizadas.
- Promover una etapa, cerrar un gate o aprobar una excepción; esas acciones pertenecen al orquestador o a revisión explícita.
- Reescribir contratos previos sin cambio de versión y sin señal de corrección trazable.
