# Operational Rules — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## rules
1. Bounded asset identity antes de promoción. Si `route_state` no es `operational_asset_candidate`, el scorecard no puede promover el caso fuera de `public_only_screening`.
2. `research_mode` y `evidence_mode_state` no son lo mismo. El primero describe qué familias de fuente se observaron; el segundo se decide por scorecard usando core packs y bounded asset gate.
3. Todo run debe emitir los diez diligence packs canónicos, aunque varios queden en `not_primary`, `public_context_only` o `requested_but_absent`.
4. La presencia de una familia de fuente local no basta para marcar un pack como `evidenced`; para algunos packs se requieren `extended_sources.records` realmente absorbidos.
5. Los conflictos de autoridad de alta precedencia y los conflictos críticos de entidad/boundary deben aparecer como blockers explícitos cuando impiden promoción.
6. Las preguntas dinámicas de intake deben ser discriminantes y mapearse a `required_from_register` e `intake_priority_register`; no pueden ser preguntas genéricas sin efecto operativo.
7. Toda mejora de `local_evidence_binding_state` debe apoyarse en bases concretas como control-boundary evidence, maintenance proof, utility breakdown, tariffs o responsibility matrices.

## invariants
- `diligence_pack_count` debe ser igual al largo de `DILIGENCE_PACK_NAMES`;
- los estados de los packs individuales y los del `diligence_pack_register` deben permanecer sincronizados;
- `dynamic_intake_question_count`, `required_from_count` e `intake_priority_count` deben corresponder al volumen real de registros emitidos;
- si `bounded_asset_gate_passed=false`, `evidence_mode_state` debe quedar en `public_only_screening`;
- `operator_integrated_congruence` sólo puede aparecer cuando el scorecard alcanza umbral híbrido y umbral operador;
- un claim no puede pasar a `sufficiently_bound` sin alguna base local concreta en `binding_basis`;
- si existe `unresolved_source_authority_conflict`, debe existir el blocker correspondiente en `promotion_blocker_register`.

## forbidden_operations
- promover un caso a `hybrid_diligence` u `operator_integrated_congruence` sólo porque el activo “parece” operacional;
- tratar vendor material, brochures o seed público como diagnóstico local dominante cuando la policy de fuentes lo prohíbe;
- omitir `declared_input_downgrade_register`, `source_conflict_register` o `entity_conflict_register` para limpiar artificialmente el caso;
- saltarse la emisión de canonical diligence packs o reetiquetarlos fuera del vocabulario gobernado;
- convertir `public_context_only` o `requested_but_absent` en cierre práctico de control boundary, maintenance maturity o permit detail;
- usar este motor para emitir comparables finales, claims financieros cerrados o acciones estratégicas definitivas.
