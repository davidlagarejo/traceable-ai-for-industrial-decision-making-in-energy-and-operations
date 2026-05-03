# Functional Contract — Access Control / Execution Policy Layer

Motor ID: motor_026

## inputs
- execution_request: object — producido por motor_023, orquestador operacional o proceso de ejecución; incluye request_id, actor_id, actor_type, motor_id, stage_name, action, target_ref, target_type, requested_at, run_id, correlation_id y declared_purpose.
- phase_contracts: list[PhaseContract] — producido por motor_001; define motores permitidos, etapas válidas, handoffs, límites de fase y acciones compatibles con cada contrato.
- rights_profile: RightsProfile — producido por motor_008; contiene source_id, license_basis, permitted_uses, prohibited_uses, restriction_notes, rights_status y referencias documentales.
- access_class: AccessClass — producido por motor_008; clasifica el nivel de acceso del recurso solicitado y la base documental que justifica esa clasificación.
- execution_policy_set: list[ExecutionPolicy] — configuración gobernada del framework; enumera reglas explícitas de allow, deny o conditional para combinaciones de actor, motor, acción, target_type, access_class y propósito declarado.

## outputs
- policy_decision: PolicyDecision — consumido por motor_023 u orquestador; decisión determinista con decision_id, request_id, status, reason_code, decision_basis, evaluated_at y correlation_id.
- policy_violation_event: PolicyViolationEvent — consumido por observabilidad, conformance review o revisión humana; describe rechazo, actor, motor, acción, target_ref, reglas incumplidas y evidencia usada.
- access_audit_record: AccessAuditRecord — persistencia de auditoría; registra solicitud, políticas evaluadas, contratos consultados, rights_profile consultado, resultado y hash o referencia de cada fuente normativa.
- conditional_execution_requirement: ConditionalExecutionRequirement — consumido por motor_023 u operador humano cuando una acción solo puede continuar si se cumple una condición explícita de acceso.

## limits
- No acepta execution_request sin request_id, actor_id, motor_id, action, target_ref, target_type, requested_at, run_id y correlation_id.
- No acepta target_ref cuyo source_id o artifact_id no pueda enlazarse a rights_profile, access_class o contrato de fase vigente.
- No acepta políticas sin identificador estable, versión, scope, condición evaluable, efecto y provenance de aprobación.
- No produce ejecución real, retry_decision, metric_record general, source_registration, rights_profile, access_class ni phase_contract.
- No produce permisos implícitos; si falta una autoridad requerida, el resultado debe ser deny o conditional con razón explícita.
- No reescribe payloads de otros motores para ajustarlos a una política.

## validations
- Rechaza cualquier input con campos obligatorios ausentes, nulos, tipo incompatible o timestamp no parseable.
- Verifica que motor_id y stage_name existan en phase_contracts y que la action solicitada no viole límites de fase.
- Verifica que rights_profile y access_class correspondan al mismo source_id o target_ref de la solicitud.
- Evalúa reglas de deny antes que reglas de allow; una prohibición explícita prevalece sobre permiso general.
- Exige que toda decisión incluya al menos una base normativa: phase_contract, rights_profile, access_class o execution_policy.
- Antes de emitir policy_decision exige decision_id, request_id, status, reason_code, decision_basis, evaluated_at, policy_version y correlation_id.
- Antes de emitir access_audit_record exige referencia a la solicitud original, reglas evaluadas, resultado, actor, motor, target_ref, run_id y provenance de las autoridades consultadas.
