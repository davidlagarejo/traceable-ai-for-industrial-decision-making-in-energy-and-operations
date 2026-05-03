# Functional Contract — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## inputs
- `__pipeline__`
  Tipo: `dict`
  Productor: runtime orchestration
  Uso: fallback para `derive_target_definition` y fuente de structured/raw local intake mediante `build_structured_local_source_register` y `build_raw_local_evidence_source_register`.
- `motor_007.target_definition_contract`
  Tipo: `dict`
  Productor: `motor_007`
  Contenido mínimo esperado: `target_type`, `target_name` o `target_identifier`, `jurisdiction_scope`, `address_raw`.
- `motor_007.target_classification_object`
  Tipo: `dict`
  Productor: `motor_007`
  Uso: decidir `route_state` y si el asset está bounded como `OPERATING_ASSET` o sigue sin cierre operativo.
- `motor_012.facility_prior`
  Tipo: `dict`
  Productor: `motor_012`
  Uso: fuente preferida de `target_definition`, dataset coverage y algunos campos de facility context.
- `motor_012.asset_field_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: hints operativos, de proceso y de family inference.
- `motor_012.declared_input_downgrade_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: propagar degradaciones declaradas que ya afectan la confianza del caso.
- `motor_028.source_register`
  Tipo: `list[dict]`
  Productor: `motor_028`
  Uso: base pública de fuentes observadas que luego se fusiona con fuentes locales estructuradas y crudas.
- `motor_028.enriched_data.extended_sources`
  Tipo: `dict`
  Productor: `motor_028` o intake local
  Uso: detectar si packs como bills, tariffs, lease, submetering, maintenance o CMMS tienen registros realmente absorbidos y no sólo presencia de source family.
- registers de discovery upstream
  Tipo: múltiples `list[dict]`
  Productor: `motor_028`
  Contenido: `search_budget_register`, `search_attempt_ledger`, `search_attempt_outcome_register`, `search_exhaustion_register`, `discovery_need_register`, `search_family_execution_plan`, `accepted_evidence_type_register`, `discovery_stop_condition_register`, `next_best_search_register`, `search_target_priority_register`, `search_success_effect_register`, `search_failure_effect_register`, y si existen los stop/downgrade/escalation/minimum-sufficient registers previos.

## outputs
- perfilado y librería de research
  Tipo: `dict` y `list[dict]`
  Consumidores: `motor_050` a `motor_053`, auditoría
  Contenido: `case_fingerprint`, `asset_family_research_profile`, `asset_family_research_dossier`, `family_research_coverage_register`, `family_research_gap_register`, `authoritative_source_trace_register`, `authoritative_source_acquisition_trace`, `family_source_gap_register`, `family_source_refresh_state`, `research_library_version`.
- normalización y gobierno de fuentes
  Tipo: `list[dict]`
  Consumidores: validadores de congruencia, intake downstream
  Contenido: `structured_local_source_register`, `raw_local_source_register`, `authority_precedence_register`, `source_conflict_register`, `conflict_resolution_outcome_register`.
- resolución de entidad y boundary
  Tipo: `list[dict]` y `str`
  Consumidores: validadores, comparison safety, packaging
  Contenido: `entity_resolution_register`, `entity_conflict_register`, `asset_boundary_resolution_register`, `owner_operator_tenant_resolution_register`, `entity_resolution_state`.
- pack operativo de intake
  Tipo: `dict`
  Consumidores: dynamic intake, operational bounding, dashboards
  Contenido: `operational_intake_pack` con `asset_identity_pack`, packs seed, `diligence_pack_register`, state summary y snapshots de campos observados.
- evidencia local extraída
  Tipo: `list[dict]`
  Consumidores: local binding, congruence motors posteriores
  Contenido: `utility_charge_breakdown_register`, `tariff_exposure_register`, `permit_to_system_register`, `regulated_process_scope_register`, `control_boundary_evidence_register`, `owner_operator_tenant_responsibility_register`, `maintenance_proof_evidence_register`.
- intake dinámico y stop logic
  Tipo: `list[dict]`
  Consumidores: recolección operatoria y reruns
  Contenido: `stop_condition_register`, `downgrade_condition_register`, `escalation_condition_register`, `minimum_sufficient_evidence_register`, `dynamic_intake_question_register`, `required_from_register`, `intake_priority_register`, `rival_hypothesis_register`, `hypothesis_discrimination_register`, `claim_impact_register`, `gap_taxonomy_register`, `evidence_need_class_register`.
- binding y promoción
  Tipo: `list[dict]` y `dict`
  Consumidores: `motor_050+`, validadores, reporting
  Contenido: `local_evidence_binding_register`, `binding_upgrade_register`, `local_truth_confidence_register`, `binding_sufficiency_reason_register`, `operational_bounding_scorecard`, `promotion_blocker_register`, `evidence_mode_state`.
- señales derivadas y conteos
  Tipo: escalares
  Consumidores: runtime general y dashboards
  Contenido: familia seleccionada, modo de research, counts de packs, conflicts, questions, blockers, sources y binding gaps.

## limits
- no acepta promoción a `hybrid_diligence` u `operator_integrated_congruence` si el target no pasó el bounded asset gate;
- no acepta source presence como equivalente a evidencia local absorbida; un pack puede quedar `partially_evidenced` aunque exista la familia de fuente;
- nunca produce claim closure, recommendation closure ni comparables finales;
- nunca trata vendor material o seed público como sustituto automático de utility bills, lease matrices, meter maps, permit detail o maintenance proof cuando el caso los necesita;
- nunca descarta conflictos críticos de autoridad o de foreign asset sólo para permitir promoción;
- nunca omite los diez diligence packs canónicos definidos en `DILIGENCE_PACK_NAMES`.

## validations
- la resolución de `target_definition` debe seguir el orden `facility_prior.target_definition` -> `motor_007.target_definition_contract` -> `derive_target_definition(__pipeline__)`;
- `asset_family_research_profile` debe producir una `asset_family` del catálogo gobernado y un `route_state` coherente con la clasificación operacional;
- `source_register` final debe integrar fuentes públicas, structured local y raw local antes de calcular precedencia, conflictos y resolución de entidad;
- `operational_intake_pack.diligence_pack_register` debe contener exactamente los packs canónicos y mantenerse sincronizado con los estados de cada pack individual;
- `evidence_mode_state` debe venir del `operational_bounding_scorecard`, no de intuición narrativa sobre `research_mode`;
- si aparecen `unresolved_high_authority_conflict`, el motor debe reflejarlos en `promotion_blocker_register`;
- si no existe evidencia local suficiente, `local_evidence_binding_register` debe permanecer en estados como `public_context_only_unbound` o equivalentes, no promoverse artificialmente.
