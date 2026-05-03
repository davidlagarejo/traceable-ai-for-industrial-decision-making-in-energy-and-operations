# Failure Modes Spec — Phase Contract Registry

Motor ID: motor_001

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Definir y hacer cumplir contratos de fase: inputs, outputs, límites y handoffs entre motores.
why_it_exists:  Evita que los motores invadan fases o produzcan outputs indebidos sin contrato explícito.
key_inputs:     phase definitions, motor declarations, contract schemas
key_outputs:    phase_contract records, handoff definitions, limit enforcement signals
key_objects:    PhaseContract, Handoff, ContractViolation
what_not_to_do: No implementa lógica de negocio. No ejecuta motores. Solo registra y valida contratos.
design_notes:   Motor fundacional. No depende de ningún otro. Es el ancla de todo el sistema.

Failure-mode specification completed for this artifact.
-->

## failure_modes_list
- CONTRACT_DRIFT: una `MotorDeclaration`, `PhaseDefinition` o `ContractSchema` cambia sin emitir nueva version contractual -> el registro acepta handoffs o contratos que ya no corresponden a las fuentes autorizadas -> bloquear el contrato afectado, emitir `ContractViolation.violation_code=CONTRACT_VERSION_CONFLICT` o `CONTRACT_SCHEMA_INVALID`, exigir nueva version semver y reconstruir `PhaseContract.version_hash` desde la fuente vigente.
- BOUNDARY_LEAKAGE: un contrato declara outputs, limites o reglas que autorizan ejecucion de motores, decisiones analiticas, cierre de gates o mutacion directa de estado -> el `PhaseContract` mezcla responsabilidades del orquestador u otros motores -> rechazar la declaracion, emitir `ContractViolation.violation_code=BOUNDARY_LEAKAGE`, mantener sin cambios el registro anterior y devolver la correccion al propietario documental.
- SILENT_COERCION: campos obligatorios llegan vacios, con tipo incorrecto o con listas implicitas, y el motor intenta normalizarlos sin senal de violacion -> los consumidores reciben contratos aparentemente validos sin provenance, limites o nombres contractuales reconstruibles -> detener la emision del registro, emitir `CONTRACT_FIELD_MISSING` o `CONTRACT_SCHEMA_INVALID` por `field_path`, y requerir una declaracion explicita en la fuente.
- VERSION_COLLISION: dos declaraciones comparten `contract_id` y `version_id` pero producen `version_hash` distinto -> la reconstruccion historica no puede determinar que contenido era vigente para ese contrato -> tratar la segunda declaracion como conflicto bloqueante, preservar el registro inmutable existente y exigir version nueva o correccion documentada de la fuente.
- HANDOFF_AMBIGUITY: un `Handoff` omite version del contrato, usa nombres genericos de output/input, o referencia un output no listado en `allowed_outputs` -> el handoff puede conectarse al contrato equivocado o a un objeto que el origen no puede emitir -> rechazar el handoff, emitir `HANDOFF_OUTPUT_NOT_ALLOWED`, `HANDOFF_INPUT_NOT_ALLOWED` o `HANDOFF_VERSION_AMBIGUOUS`, y exigir referencias completas a `source_version_id` y `destination_version_id`.
- LINEAGE_LOSS: un contrato, handoff o violacion carece de `source_ref`, `produced_by_motor`, `produced_at` o `parent_id` aplicable -> no se puede auditar por que el objeto fue aceptado, rechazado o supersedido -> no persistir el objeto como activo, emitir violacion con severidad `ERROR`, y requerir provenance completo antes de cualquier revalidacion.
- AUTHORITY_BYPASS: una declaracion introduce un `motor_id`, `phase_id` o dependencia no presente en los registros autorizados -> el registro deja de ser ancla contractual y empieza a crear alcance nuevo -> rechazar la declaracion con `MOTOR_NOT_AUTHORIZED` o `PHASE_NOT_RECOGNIZED`, sin crear motores, fases ni handoffs inferidos.

## anti_patterns
- Acoplar el registro a la ejecucion real de motores, por ejemplo invocar pipelines, aprobar gates o escribir `motor_state.json` desde la validacion contractual.
- Tratar texto narrativo libre como contrato operativo sin mapearlo a `PhaseContract.allowed_inputs`, `allowed_outputs`, `limits`, `version`, `source_ref` y `contract_schema_ref`.
- Sobrescribir un `PhaseContract` o `Handoff` existente para resolver una incompatibilidad local en lugar de crear nueva version o emitir `ContractViolation`.
- Crear handoffs por convencion de nombres, similitud semantica o inferencia de IA sin que ambos lados declaren explicitamente el output y el input.
- Usar nombres amplios como `data`, `payload`, `result` o `metadata` como outputs permitidos sin contrato especifico y verificable.
- Convertir `ContractViolation` en advertencia no bloqueante cuando falta identidad, version, provenance, schema o limite obligatorio.
- Mezclar validacion contractual con normalizacion de contenido, scoring de calidad, identity resolution, decision core, rendering o cualquier logica de negocio de otros motores.
- Permitir excepciones ad hoc no versionadas para hacer pasar una etapa; toda excepcion material debe quedar como violacion, correccion trazable o aprobacion externa del orquestador.

## degradation_signals
- `contract_violation_rate` aumenta por encima de la linea base del motor, especialmente para `CONTRACT_FIELD_MISSING`, `CONTRACT_SCHEMA_INVALID` o `HANDOFF_VERSION_AMBIGUOUS`.
- Mas de una declaracion por corrida produce `CONTRACT_VERSION_CONFLICT` para el mismo `contract_id`, indicando colision de versiones o cambios no gobernados.
- Proporcion creciente de `PhaseContract.limits` con valores vacios, genericos o no verificables frente al total de contratos registrados.
- Aparicion repetida de `allowed_outputs` con nombres genericos como `data`, `result` o `payload` en contratos de motores distintos.
- Handoffs rechazados por `HANDOFF_OUTPUT_NOT_ALLOWED` o `HANDOFF_INPUT_NOT_ALLOWED` despues de que el contrato fuente ya fue aceptado.
- Registros emitidos con `parent_id=null` para versiones que declaran superseder una version previa, o con `parent_id` poblado sin registro predecessor existente.
- Diferencia entre el numero de declaraciones procesadas y el numero de registros activos mas violaciones emitidas, lo que indica perdida silenciosa de entradas.
- Logs de validacion que mencionan correccion automatica, coercion de tipos o inferencia de campos obligatorios en vez de emision de violacion estructurada.
- Reintentos frecuentes del mismo `source_ref` sin cambio de version ni cambio de `version_hash`, senal de correccion manual insuficientemente trazada.

## expensive_errors
- Aceptar un contrato sin `source_ref`: es caro porque todo objeto downstream construido desde ese contrato pierde provenance y requiere auditoria manual para reconstruir autoridad documental. Se previene rechazando el registro con `CONTRACT_FIELD_MISSING` antes de emitir `PhaseContract` activo.
- Permitir una colision de version con overwrite: es caro porque rompe comparabilidad historica, rebuild y deteccion de stale objects. Se previene calculando `version_hash` deterministico, tratando contenidos distintos bajo la misma version como `CONTRACT_VERSION_CONFLICT`, y preservando records previos inmutables.
- Registrar un handoff con output no declarado: es caro porque motores downstream pueden construir tests, schemas o implementaciones sobre un objeto que el origen no esta autorizado a producir. Se previene verificando `output_name in source.allowed_outputs` y `expected_input_name in destination.allowed_inputs` antes de persistir el handoff.
- Dejar pasar boundary leakage: es caro porque desplaza responsabilidades del orquestador, gate checker o motores analiticos al registro contractual y obliga a redisenar contratos, tests e implementacion. Se previene con reglas bloqueantes para outputs o limites que impliquen ejecucion, cierre de gates, decisiones de negocio o mutacion directa de estado.
- Normalizar silenciosamente listas ausentes: es caro porque una lista faltante y una lista deliberadamente vacia significan cosas distintas, especialmente en contratos terminales. Se previene exigiendo presencia explicita de `allowed_inputs`, `allowed_outputs` y `limits`, aceptando listas vacias solo cuando el contrato declara el limite que las justifica.
- Crear motores, fases o dependencias desde una declaracion no autorizada: es caro porque contamina el DAG operativo y puede abrir trabajo fuera del catalogo confirmado. Se previene validando `motor_id` y `phase_id` contra fuentes autorizadas y emitiendo `MOTOR_NOT_AUTHORIZED` o `PHASE_NOT_RECOGNIZED` sin modificar registros base.
