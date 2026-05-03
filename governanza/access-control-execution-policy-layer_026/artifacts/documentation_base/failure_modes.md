# Failure Modes — Access Control / Execution Policy Layer

Motor ID: motor_026

## failure_modes_list
- Permiso implícito por falta de autoridad: el motor devuelve allow cuando falta rights_profile, access_class, phase_contract o execution_policy aplicable. Síntoma observable: decisiones allow con decision_basis incompleta o authority_refs vacías.
- Invasión de responsabilidades: el motor modifica contratos, derechos o estado operacional en lugar de emitir una decisión. Síntoma observable: outputs con campos de source_registration, phase_contract, retry_decision o payloads mutados.
- Precedencia incorrecta de reglas: una regla allow general supera una prohibición explícita. Síntoma observable: acciones sobre prohibited_uses aparecen como autorizadas.
- Auditoría incompleta: decisiones sin request_id, policy_version, correlation_id o referencias documentales. Síntoma observable: imposibilidad de reconstruir por qué una ejecución fue permitida o bloqueada.
- Evaluación no determinista: la misma solicitud con las mismas versiones de autoridad produce resultados distintos. Síntoma observable: divergencia de status o reason_code entre corridas equivalentes.

## anti_patterns
- Usar este motor como orquestador general de jobs, mezclando autorización con scheduling, retries y métricas.
- Reimplementar dentro de cada motor downstream reglas locales de acceso que contradicen o duplican PolicyDecision.
- Tratar derechos ambiguos como permisos concedidos para mantener continuidad operacional.
- Delegar autorización a prompts, texto libre o inferencias de LLM sin policy_id, versionado y provenance.
- Emitir warnings no bloqueantes para violaciones que deberían producir deny o conditional.

## degradation_signals
- Aumento de decisiones allow sin decision_basis completa.
- Porcentaje creciente de solicitudes conditional sin verificación posterior o con requisitos vencidos.
- Diferencias entre decisiones para solicitudes idénticas bajo la misma policy_version.
- Registros de auditoría sin authority_refs o con referencias que no resuelven a contratos, derechos o políticas vigentes.
- Solicitudes rechazadas por campos faltantes provenientes siempre del mismo motor upstream, señalando contrato de handoff mal aplicado.
- Aparición de outputs de ejecución, source registry o phase contract dentro de este motor.
