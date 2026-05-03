# Acceptance Tests — Access Control / Execution Policy Layer

Motor ID: motor_026

## happy_path
Una execution_request completa solicita que un motor permitido por motor_001 ejecute una acción de lectura sobre un target_ref asociado a rights_profile y access_class de motor_008. La policy_version activa contiene una regla allow para ese actor, motor, acción, target_type, access_class y declared_purpose. El motor emite PolicyDecision con status allow, reason_code estable, referencias al phase_contract, rights_profile, access_class y execution_policy evaluada, además de AccessAuditRecord con run_id y correlation_id originales.

## edge_cases
- Fuente premium con uso permitido solo para lectura interna: una solicitud de lectura interna produce allow si el contrato de fase lo permite; una solicitud de exportación produce deny con policy_violation_event y referencia a prohibited_uses.
- Motor válido pero etapa incorrecta: si motor_id existe pero stage_name no está autorizado por el phase_contract vigente, el resultado es deny aunque la fuente tenga rights_profile permisivo.
- Permiso condicionado por evidencia externa: si la política exige aprobación humana o credencial activa, el resultado es conditional e incluye ConditionalExecutionRequirement con evidencia requerida, responsable y vencimiento.
- Repetición de la misma solicitud: con los mismos inputs y policy_version, el motor produce la misma decisión lógica y conserva un nuevo audit_id sin cambiar la razón de autorización.

## rejection_criteria
- Rechaza execution_request sin request_id, actor_id, motor_id, action, target_ref, requested_at, run_id o correlation_id.
- Rechaza solicitudes cuyo target_ref no pueda enlazarse a rights_profile o access_class cuando el target sea fuente, dataset derivado de fuente o output con restricciones heredadas.
- Rechaza policy_set con reglas sin policy_id, policy_version, effect, scope o provenance_ref.
- Rechaza cualquier solicitud cuyo timestamp sea inválido o cuya policy_version activa no sea determinable.
- Rechaza inputs que pidan modificar contratos, derechos, artefactos o estado de otros motores como parte de la decisión de acceso.
