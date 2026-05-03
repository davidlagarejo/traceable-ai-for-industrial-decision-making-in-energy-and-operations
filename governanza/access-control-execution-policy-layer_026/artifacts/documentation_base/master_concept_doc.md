# Master Concept Document — Access Control / Execution Policy Layer

Motor ID: motor_026

## purpose
El Access Control / Execution Policy Layer decide, de forma determinista y auditable, si un motor, proceso o actor operacional puede ejecutar una acción sobre una fuente, dataset, artefacto u output concreto. Evalúa solicitudes de ejecución contra contratos de fase, derechos de fuente, clases de acceso y políticas explícitas de operación. Su salida principal no es ejecutar la acción, sino emitir una decisión permitida, denegada o condicionada con razones trazables.

## what_it_does
- Recibe solicitudes de ejecución con actor, motor, etapa, acción solicitada, objetivo, run_id, timestamp y contexto de provenance.
- Consulta contratos de fase producidos por motor_001 para verificar que el motor y la etapa están autorizados a operar en ese punto del workflow.
- Consulta rights_profile y access_class producidos por motor_008 para validar restricciones de fuentes, licencias, uso permitido y límites de acceso.
- Usa eventos y contexto operativo de motor_023 para asociar cada decisión a un run, correlation_id y estado observable.
- Produce decisiones de política con status, reason_code, policy_basis, objeto afectado y evidencia documental usada.
- Emite eventos de rechazo o condición para observabilidad, auditoría y revisión de conformidad.

## what_it_does_not_do
- No ejecuta motores, jobs, ingestas, transformaciones ni entregas de artefactos.
- No crea ni modifica contratos de fase; solo los consulta como autoridad operacional.
- No registra fuentes, licencias ni derechos nuevos; esa responsabilidad pertenece a motor_008.
- No orquesta retries, scheduling, métricas generales ni alertas operativas fuera de la decisión de acceso; eso pertenece a motor_023.
- No decide verdad, calidad, prioridad analítica, identidad, normalización ni clasificación epistemológica.
- No convierte permisos ausentes o ambiguos en permisos concedidos.

## why_it_exists
Existe para impedir que la automatización multi-motor opere sobre recursos no autorizados, fuentes restringidas o outputs fuera de contrato. Motor_001 define límites de fase, motor_008 define derechos y clases de acceso, y motor_023 observa la operación; este motor combina esas autoridades en una decisión concreta de ejecución sin absorber sus responsabilidades. La separación evita que cada motor implemente reglas propias de acceso, reduce decisiones silenciosas y deja un rastro reconstruible de por qué una acción fue permitida o bloqueada.
