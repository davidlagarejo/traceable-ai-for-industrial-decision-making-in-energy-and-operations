# Failure Modes — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## failure_modes_list
1. `public_context_promotion_error`
   Síntoma: un caso con packs sólo `public_context_only` o `requested_but_absent` sube a `hybrid_diligence` u `operator_integrated_congruence`.
   Riesgo: downstream trata screening público como si ya hubiera verdad local absorbida.
2. `pack_state_desynchronization`
   Síntoma: el `diligence_pack_register` dice un estado, pero el pack individual correspondiente dice otro.
   Riesgo: scorecards, dashboards y intake dinámico operan sobre realidades distintas.
3. `source_conflict_suppression`
   Síntoma: conflictos de autoridad o foreign-asset aparecen en registros intermedios, pero no generan blockers de promoción.
   Riesgo: se cierran claims críticos sobre fuentes incompatibles o contradictorias.
4. `binding_overclaim`
   Síntoma: claims pasan a `partially_bound` o `sufficiently_bound` sin bases locales reales en boundary, maintenance, utility o permits.
   Riesgo: la congruencia posterior hereda una falsa sensación de verdad local.
5. `family_misrouting`
   Síntoma: el motor asigna una familia de activo errónea y con ello activa preguntas, packs y comparaciones equivocadas.
   Riesgo: la investigación subsecuente persigue evidencia irrelevante y omite la que sí importa.
6. `dynamic_intake_under-specification`
   Síntoma: las preguntas de intake no discriminan hipótesis rivales ni cierran blockers concretos.
   Riesgo: el operador aporta datos sin impacto real en promoción o en validación de claims.

## anti_patterns
1. Tomar cualquier documento subido por el usuario como evidencia local fuerte sin pasar por source family, precedencia y binding basis.
2. Saltar directo de family inference a recommendation logic, sin respetar `operational_intake_pack`, blockers y scorecard.
3. Diseñar intake manual genérico en lugar de usar las preguntas discriminantes emitidas por el motor.

## degradation_signals
- `diligence_pack_count` distinto de diez o drift entre `diligence_pack_register` y estados individuales;
- casos `target_not_yet_operationally_bounded` que aun así aparecen con `hybrid_score` suficiente o con `evidence_mode_state` promovido;
- `binding_gap_count` igual a cero en casos claramente públicos o débiles, señal de sobrepromoción silenciosa;
- presencia de `unresolved_high_authority_conflict` sin blocker asociado;
- crecimiento de `partially_evidenced_pack_count` sin `extended_sources.records` que lo justifiquen;
- `dynamic_intake_question_count` alto pero sin correlato en `required_from_register`, `intake_priority_register` o cierres de gap taxonomy.
