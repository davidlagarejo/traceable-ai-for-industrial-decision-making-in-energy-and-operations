# Acceptance Tests — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## happy_path
1. NYC office tower con señales públicas bounded.
   Input: `target_type=commercial_building`, jurisdicción `US-NY-NYC`, nombre tipo One Vanderbilt, `GFA` alta, `floor_count` alto y fuentes NYC aceptadas.
   Expected output: `selected_archetype_id=commercial_office_tower_nyc`, `match_confidence=high`, hipótesis que incluyan `central_plant`, `tenant_metering`, `after_hours_occupancy` y `LL97_pathway`, todas como `ARCHETYPAL_PRIOR`.
2. Manufacturing facility con clues de laminate process.
   Input: `target_type=manufacturing_facility`, hints como `laminate`, `resin`, `curing`, `pressing` en `asset_field_register`.
   Expected output: `selected_archetype_id=manufacturing_laminate`, `match_confidence=high`, presencia de `resin_curing_profile` y otras hipótesis de proceso térmico.
3. Industrial plant con support-utility clues explícitas.
   Input: `target_type=industrial_plant` o `utility_heavy_site`, campos como `central utility island`, `power factor`, `reactive`, `large motors and drives`.
   Expected output: `selected_archetype_id=utility_heavy_site_generic`, `match_confidence=high`, hipótesis con `demand_structure` y contrato anti-hallucination intacto.

## edge_cases
1. Headquarters o mailing address no operativo.
   Input: `target_classification_object.target_type=CORPORATE_HEADQUARTERS`.
   Correct output: `selected_archetype_id=target_not_yet_structurally_modelable`, `dominant_variable_count=0`, `selected_archetype_evidence_state=INADMISSIBLE_CLAIM`.
2. Warehouse distribution operating asset sin clues específicos.
   Input: `target_type=warehouse_distribution` y ausencia de señales que activen un arquetipo más específico.
   Correct output: `selected_archetype_id=logistics_warehouse_generic`, `match_confidence=medium`, hipótesis con `service_level_complexity`.
3. Cold chain operating asset sin override específico.
   Input: `target_type=cold_chain_facility` con contexto operacional básico pero sin señales más estrechas.
   Correct output: `selected_archetype_id=cold_chain_generic`, `match_confidence=medium`, hipótesis con `refrigeration_duty`.

## rejection_criteria
1. Rechazar confianza fuerte si el caller no aporta `target_type` resoluble en `facility_prior`, `motor_007` ni `__pipeline__`; en ese caso sólo es válido un fallback no modelable.
2. Rechazar como contrato roto cualquier invocación que pretenda tratar `dominant_variable_hypotheses` o `system_abstraction_seed` como hechos observados del activo.
3. Rechazar inputs estructuralmente mal formados para `asset_field_register`, `dataset_coverage_register` o `source_register` cuando impidan distinguir entre selección específica y fallback genérico auditable.
