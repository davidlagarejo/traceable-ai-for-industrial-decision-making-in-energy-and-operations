# Operational Rules — Access Control / Execution Policy Layer

Motor ID: motor_026

## rules
1. Toda solicitud debe evaluarse contra contratos de fase vigentes antes de considerar derechos de fuente o reglas de permiso específicas.
2. Las reglas de denegación explícita tienen precedencia sobre permisos generales y sobre condiciones parciales.
3. La ausencia de rights_profile, access_class, phase_contract o policy_version requerida bloquea la autorización.
4. Cada decisión debe incluir reason_code estable, policy_version, referencias a autoridades consultadas y correlation_id del run.
5. Una decisión conditional solo es válida si la condición requerida, la evidencia esperada y el responsable de verificación están definidos.
6. La evaluación debe ser determinista: la misma solicitud con las mismas versiones de contrato, derechos y políticas produce el mismo resultado.

## invariants
- No se emite policy_decision sin preservar request_id, actor_id, motor_id, action, target_ref, run_id y correlation_id de la solicitud original.
- Ningún output pierde la referencia a las autoridades usadas para decidir: phase_contract, rights_profile, access_class y execution_policy cuando aplican.
- El motor nunca modifica el contenido del recurso solicitado ni el estado interno del motor solicitante.
- Un resultado allow no puede coexistir con una violación crítica sin condición explícita de mitigación.
- Todo rechazo debe ser observable como PolicyViolationEvent o quedar representado dentro de AccessAuditRecord con razón estructurada.

## forbidden_operations
- Ejecutar, detener o reintentar motores por cuenta propia.
- Crear, actualizar o corregir licencias, source_registration, rights_profile o access_class.
- Crear, actualizar o corregir phase_contracts, dependencias de motores o definición de etapas.
- Autorizar por defecto cuando falten políticas, contratos o derechos documentados.
- Ocultar una denegación convirtiéndola en warning no bloqueante.
- Usar criterios probabilísticos, LLM o heurísticas no versionadas como base soberana de autorización.
