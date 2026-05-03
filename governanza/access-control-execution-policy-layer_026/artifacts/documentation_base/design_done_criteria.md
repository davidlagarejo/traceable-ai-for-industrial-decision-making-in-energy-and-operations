# Design Done Criteria — Access Control / Execution Policy Layer

Motor ID: motor_026

## criteria
- El propósito, límites, inputs, outputs y validaciones distinguen claramente autorización de ejecución frente a orquestación, registro de derechos y contratos de fase.
- El modelo conceptual define ExecutionRequest, ExecutionPolicy, PolicyDecision, PolicyViolationEvent, AccessAuditRecord y ConditionalExecutionRequirement con campos mínimos obligatorios.
- Las reglas operativas fijan precedencia determinista: deny explícito, ausencia de autoridad y violación de contrato bloquean antes que cualquier permiso general.
- Los acceptance tests cubren allow, deny, conditional, etapa inválida, derechos restrictivos, solicitud repetida y rechazo por campos obligatorios ausentes.
- Los failure modes documentan permisos implícitos, invasión de responsabilidades, precedencia incorrecta, auditoría incompleta y evaluación no determinista.
- Todo output del diseño preserva request_id, run_id, correlation_id, policy_version y referencias a las autoridades consultadas.
