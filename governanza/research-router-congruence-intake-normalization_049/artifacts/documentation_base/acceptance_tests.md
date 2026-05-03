# Acceptance Tests — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## happy_path
1. One Vanderbilt en modo público.
   Input: `target_type=commercial_building`, NYC, `OPERATING_ASSET`, registros públicos de PLUTO / LL84.
   Expected output: `selected_asset_family=commercial_building`, `research_mode=public_only_screening`, `route_state=operational_asset_candidate`, `asset_identity_pack.classification_state=OPERATING_ASSET`, y claims de binding todavía en `public_context_only_unbound`.
2. Wilsonart laminate en modo híbrido.
   Input: facility manufacturing con utility bill, tariff, equipment, schedule, maintenance contract y permit record.
   Expected output: `selected_asset_family=industrial_manufacturing`, `research_mode=hybrid_diligence`, al menos cuatro packs `partially_evidenced`, `throughput by shift` en binding needed y scorecard promovido a `hybrid_diligence`.
3. Commercial building con evidencia local operatoria.
   Input: utility bills, lease matrix, BMS/controls, CMMS y operator input, con `extended_sources.records` para boundary y maintenance.
   Expected output: `research_mode=operator_integrated_congruence`, `evidence_mode_state=operator_integrated_congruence`, `control_boundary_pack` y `maintenance_maturity_pack` en `evidenced`, y `commercial_building_control_boundary` suficientemente bound.

## edge_cases
1. Warehouse candidate aún no bounded.
   Input: target warehouse con clasificación `REGISTERED_AGENT_OR_MAILING_ADDRESS` y sin evidencia operativa local.
   Correct output: `selected_asset_family=logistics_warehouse`, `route_state=target_not_yet_operationally_bounded`, `evidence_mode_state=public_only_screening`, blocker `asset_not_operationally_bounded` y binding inadmisible hasta acotar identidad.
2. Canonical diligence packs en public screening.
   Input: building public-only con pocas fuentes locales.
   Correct output: emisión completa de los diez `DILIGENCE_PACK_NAMES`, con packs como `utility_bill_pack`, `lease_responsibility_pack` y `permit_detail_pack` en `requested_but_absent`.
3. Conflicto de autoridad sin resolver.
   Input: utility bill y utility tariff de alta autoridad que abren conflicto crítico de `tariff_driver`.
   Correct output: `source_conflict_count>=1` y blocker `unresolved_source_authority_conflict` en `promotion_blocker_register`.

## rejection_criteria
1. Rechazar uso downstream que trate `research_mode` o `asset_family` como cierre suficiente de verdad local cuando el `operational_bounding_scorecard` no lo soporta.
2. Rechazar como contrato inválido cualquier consumo que ignore `promotion_blocker_register`, `source_conflict_register` o `entity_conflict_register` para promover claims críticos.
3. Rechazar confianza fuerte si `target_definition` no puede resolverse de forma mínimamente usable y el caller aun así espera más que un screening público o un caso no bounded.
