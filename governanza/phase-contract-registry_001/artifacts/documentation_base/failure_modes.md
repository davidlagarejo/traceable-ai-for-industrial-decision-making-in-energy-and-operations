# Failure Modes — Phase Contract Registry

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

## failure_modes_list
- CONTRACT_DRIFT: los contratos registrados dejan de coincidir con las declaraciones vigentes y aparecen handoffs que pasan validación documental pero fallan en etapas posteriores.
- BOUNDARY_LEAKAGE: los contratos empiezan a incluir reglas de negocio, decisiones analíticas o instrucciones de ejecución que pertenecen a otros motores.
- SILENT_COERCION: inputs incompletos o incompatibles se normalizan sin emitir `ContractViolation`, ocultando pérdida de trazabilidad.
- VERSION_COLLISION: dos contenidos contractuales distintos comparten `contract_id` y `version`, impidiendo reconstrucción confiable.
- HANDOFF_AMBIGUITY: un handoff usa nombres genéricos o no tipados que permiten múltiples interpretaciones de origen o destino.

## anti_patterns
- Usar el Phase Contract Registry como orquestador que decide ejecución, orden de corrida o cierre de etapas.
- Guardar contratos como texto narrativo sin campos estructurados de inputs, outputs, límites, versión y provenance.
- Sobrescribir una versión contractual existente para hacer pasar un gate sin registrar una nueva versión o una violación.
- Declarar outputs amplios como `data`, `result` o `payload` sin nombre contractual específico.

## degradation_signals
- Aumento sostenido de `ContractViolation` por campos obligatorios ausentes en declaraciones que antes eran válidas.
- Crecimiento de handoffs con nombres genéricos, no tipados o repetidos entre motores no relacionados.
- Aparición de contratos con `limits=[]` o límites redactados como texto no verificable.
- Correcciones frecuentes sobre el mismo `contract_id` sin incremento de versión.
- Necesidad recurrente de aprobación manual porque los inputs y outputs contractuales no son suficientemente explícitos.
