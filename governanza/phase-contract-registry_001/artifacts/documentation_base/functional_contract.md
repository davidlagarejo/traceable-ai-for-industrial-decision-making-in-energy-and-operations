# Functional Contract — Phase Contract Registry

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

## inputs
- phase_definitions: list[PhaseDefinition] — fuente: documentos de workflow y stage semantics de `governanza/automation-base/`.
- motor_declarations: list[MotorDeclaration] — fuente: `motor_registry.md`, `motor_dependencies.json` y registros operativos aprobados por el orquestador.
- contract_schemas: dict[str, ContractSchema] — fuente: schemas de contrato definidos para fases, motores y handoffs.

## outputs
- phase_contract_records: list[PhaseContract] — destino: orquestador, gate checker, conformance review y motores consumidores que necesitan conocer límites de fase.
- handoff_definitions: list[Handoff] — destino: orquestador y motores downstream que deben validar compatibilidad de inputs y outputs.
- limit_enforcement_signals: list[ContractViolation] — destino: gate checker, registros de validación y procesos de corrección que deben bloquear o explicar una incompatibilidad.

## limits
- No acepta declaraciones de motor sin `motor_id`, `phase_id`, `version`, lista explícita de inputs y lista explícita de outputs.
- No acepta texto narrativo libre como contrato operativo si no está mapeado a un schema de contrato con campos verificables.
- No acepta handoffs donde el output fuente no esté declarado como output permitido del contrato de origen.
- No produce decisiones de negocio, inferencias analíticas, reportes finales ni resultados de ejecución de motores.
- No ejecuta motores ni modifica directamente `motor_state.json`; solo produce registros contractuales y señales de cumplimiento o violación.
- No infiere motores, fases, dependencias ni elegibilidad operativa fuera de los registros autorizados.

## validations
- Rechaza cualquier input cuyo `motor_id`, `phase_id`, `contract_id` o `version` esté vacío.
- Verifica que cada `motor_id` exista en el catálogo autorizado antes de registrar un contrato.
- Verifica que cada `phase_id` pertenezca a la secuencia de etapas reconocida por el workflow.
- Verifica que `allowed_inputs`, `allowed_outputs` y `limits` sean listas explícitas, aunque estén vacías por diseño.
- Verifica que todo `Handoff` conecte un output permitido del contrato origen con un input permitido del contrato destino.
- Rechaza duplicados con el mismo `contract_id` y `version` si el contenido contractual difiere.
- Emite `ContractViolation` con `violation_code`, `severity`, `field_path` y `source_ref` para cada incumplimiento detectable.
- Antes de emitir output, garantiza que cada `PhaseContract` tenga `contract_id`, `motor_id`, `phase_id`, `version`, `source_ref` y límites declarados.
