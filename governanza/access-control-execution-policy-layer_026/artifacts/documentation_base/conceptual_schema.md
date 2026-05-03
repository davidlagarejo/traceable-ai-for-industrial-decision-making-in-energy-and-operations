# Conceptual Schema — Access Control / Execution Policy Layer

Motor ID: motor_026

## entities
- ExecutionRequest: solicitud normalizada de autorización para que un actor, motor o proceso realice una acción sobre un recurso gobernado.
- ExecutionPolicy: regla versionada y trazable que define condiciones de allow, deny o conditional para una clase de solicitud.
- PolicyDecision: resultado determinista de evaluar una ExecutionRequest contra contratos, derechos, clases de acceso y políticas vigentes.
- PolicyViolationEvent: evento generado cuando la solicitud incumple una regla, carece de autoridad suficiente o intenta operar fuera de contrato.
- AccessAuditRecord: registro reconstruible que conserva solicitud, autoridades consultadas, reglas evaluadas, resultado y rationale estructurado.
- ConditionalExecutionRequirement: condición explícita que debe cumplirse antes de autorizar una ejecución limitada.

## relationships
- Una ExecutionRequest produce exactamente una PolicyDecision por evaluación de política y versión de reglas.
- Una PolicyDecision puede referenciar cero o más PolicyViolationEvent cuando el resultado es deny o conditional.
- Una ExecutionRequest debe enlazarse a un PhaseContract de motor_001 cuando la acción pertenece a una etapa del workflow.
- Una ExecutionRequest que opera sobre fuente o derivado de fuente debe enlazarse a un RightsProfile y AccessClass de motor_008.
- Un AccessAuditRecord pertenece a una PolicyDecision y conserva referencias a todas las ExecutionPolicy evaluadas.
- Una PolicyDecision conditional puede producir una o más ConditionalExecutionRequirement, cada una con condición, responsable y criterio observable.

## key_fields
- ExecutionRequest: request_id string, actor_id string, actor_type enum, motor_id string, stage_name string, action string, target_ref string, target_type enum, requested_at datetime, run_id string, correlation_id string, declared_purpose string.
- ExecutionPolicy: policy_id string, policy_version string, scope string, effect enum, subject_selector object, action_selector object, target_selector object, condition_set object, provenance_ref string, active_from datetime.
- PolicyDecision: decision_id string, request_id string, status enum, reason_code string, decision_basis list[string], evaluated_at datetime, policy_version string, run_id string, correlation_id string.
- PolicyViolationEvent: violation_id string, decision_id string, request_id string, severity enum, violated_rule_ref string, actor_id string, motor_id string, target_ref string, observed_at datetime.
- AccessAuditRecord: audit_id string, decision_id string, request_snapshot_ref string, evaluated_policy_refs list[string], authority_refs list[string], result_status enum, created_at datetime.
- ConditionalExecutionRequirement: requirement_id string, decision_id string, condition_type enum, required_evidence string, responsible_role string, expires_at datetime, verification_status enum.
