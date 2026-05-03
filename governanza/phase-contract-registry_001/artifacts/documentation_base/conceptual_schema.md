# Conceptual Schema — Phase Contract Registry

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

## entities
- PhaseContract: registro versionado que declara los inputs, outputs, límites y responsabilidades permitidas de un motor dentro de una fase.
- Handoff: vínculo contractual que declara que un output permitido por un contrato puede ser consumido como input por otro contrato.
- ContractViolation: señal estructurada que describe una infracción, incompatibilidad o ausencia de información detectada durante la validación contractual.

## relationships
- PhaseContract → Handoff (un contrato puede declarar cero o más entregas permitidas hacia otros contratos).
- Handoff → PhaseContract (cada handoff referencia exactamente un contrato origen y un contrato destino).
- PhaseContract → ContractViolation (un contrato puede generar una o más violaciones cuando incumple schema, límites o compatibilidad).
- Handoff → ContractViolation (un handoff genera violación cuando conecta outputs e inputs no compatibles o no declarados).
- ContractViolation → PhaseContract (cada violación conserva referencia al contrato afectado para auditoría y corrección).

## key_fields
PhaseContract:
- contract_id: string
- motor_id: string
- phase_id: string
- version: string
- source_ref: string
- allowed_inputs: list[string]
- allowed_outputs: list[string]
- limits: list[string]

Handoff:
- handoff_id: string
- source_contract_id: string
- destination_contract_id: string
- output_name: string
- expected_input_name: string
- source_ref: string

ContractViolation:
- violation_id: string
- contract_id: string
- violation_code: string
- severity: enum[ERROR, WARNING]
- field_path: string
- source_ref: string
