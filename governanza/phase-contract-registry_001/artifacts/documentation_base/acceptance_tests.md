# Acceptance Tests — Phase Contract Registry

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

## happy_path
Input: `phase_definitions` declara la etapa `documentation_base`; `motor_declarations` incluye `motor_001` con inputs `phase_definitions`, `motor_declarations`, `contract_schemas` y outputs `phase_contract_records`, `handoff_definitions`, `limit_enforcement_signals`; `contract_schemas` exige identificadores, versión, límites y provenance.

Action: el motor valida que los campos obligatorios existen, que `motor_001` está en el catálogo, que la fase pertenece al workflow y que los outputs declarados están dentro de su propósito contractual.

Expected output: un `PhaseContract` con `contract_id=phase-contract-registry.documentation_base.v1`, `motor_id=motor_001`, `phase_id=documentation_base`, `version=1.0.0`, inputs y outputs permitidos explícitos; una lista `handoff_definitions` vacía si no se declaró consumidor downstream para este caso; una lista `limit_enforcement_signals` vacía porque no hay violaciones.

## edge_cases
- Empty downstream handoff list: si un contrato válido no declara consumidores downstream, el motor registra el `PhaseContract`, emite `handoff_definitions=[]` y no crea violación por ausencia de handoff.
- Identical duplicate declaration: si llega dos veces el mismo `contract_id` y `version` con contenido idéntico, el motor trata la segunda entrada como idempotente y no crea un segundo contrato.
- Explicit empty outputs: si una fase terminal declara `allowed_outputs=[]` con límite explícito de no emisión downstream, el contrato es válido y cualquier handoff asociado queda rechazado.

## rejection_criteria
- Missing required identity: si una declaración carece de `motor_id`, `phase_id` o `version`, el motor rechaza el contrato y emite `ContractViolation` con `violation_code=CONTRACT_FIELD_MISSING`.
- Undeclared output handoff: si un handoff intenta entregar `quality_score` desde un contrato que no tiene `quality_score` en `allowed_outputs`, el motor rechaza el handoff y emite `violation_code=HANDOFF_OUTPUT_NOT_ALLOWED`.
- Version conflict: si llega el mismo `contract_id` y `version` con límites distintos, el motor rechaza la nueva declaración y emite `violation_code=CONTRACT_VERSION_CONFLICT`.
