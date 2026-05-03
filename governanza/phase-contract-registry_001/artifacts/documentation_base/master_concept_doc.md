# Master Concept Document — Phase Contract Registry

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

## purpose
El Phase Contract Registry define y valida los contratos que delimitan cada fase y cada handoff entre motores. Registra qué inputs puede recibir un motor, qué outputs puede emitir, qué límites no puede cruzar y bajo qué condiciones un output puede ser entregado a otro motor. Su resultado principal es una base explícita de contratos de fase que permite detectar invasión de responsabilidades antes de que contamine etapas posteriores.

## what_it_does
- Recibe definiciones de fase y extrae los límites operativos que deben respetarse.
- Recibe declaraciones de motores y las vincula con las fases, inputs, outputs y consumidores permitidos.
- Valida declaraciones contractuales contra los schemas de contrato vigentes.
- Produce registros `PhaseContract` con identificadores, versión, límites, inputs y outputs permitidos.
- Produce definiciones `Handoff` cuando un output declarado por un motor puede ser consumido por otro.
- Emite señales `ContractViolation` cuando falta un campo obligatorio, existe una incompatibilidad de handoff o un motor declara responsabilidades fuera de su fase.
- Conserva referencias de provenance, versión y fuente documental para que cada contrato pueda auditarse y reconstruirse.

## what_it_does_not_do
- No implementa lógica de negocio de ningún dominio analítico.
- No ejecuta motores, pipelines, parsers, evaluadores ni renderizadores.
- No decide el contenido sustantivo de un output; solo valida si el output está permitido por contrato.
- No crea motores nuevos ni redefine el catálogo de motores existente.
- No corrige silenciosamente contratos incompletos, ambiguos o incompatibles.
- No sustituye al orquestador, al motor de calidad, al motor de versioning ni a la revisión de conformidad.

## why_it_exists
Existe como motor separado porque los contratos de fase son el ancla estructural del framework: todos los motores posteriores dependen de límites explícitos para no invadir responsabilidades ajenas. Al no depender de ningún otro motor, puede operar como control fundacional y evitar que los handoffs se definan por supuestos implícitos o por conveniencia local.
