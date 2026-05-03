# Master Concept Document — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## purpose
Research Router & Congruence Intake Normalization transforma un caso ya clasificado en un bundle canónico de investigación y bounded local diligence para la lane de congruencia. Une contexto público, intake estructurado, ingestión documental local y señales de discovery en un único contrato operativo que responde cuatro preguntas: qué familia de activo estamos modelando, qué evidencia local falta de verdad, qué conflictos o blockers impiden promoción y qué preguntas dinámicas debe hacer el sistema para cerrar el gap. Su trabajo no es decidir la tesis final, sino fijar la superficie de evidencia mínima desde la cual los motores `050` a `053` pueden razonar sin mezclar seed público con verdad local.

## what_it_does
- infiere `asset_family`, `route_state` y `research_mode` a partir de `target_definition`, clasificación operacional y familias de fuente observadas;
- construye `case_fingerprint`, `asset_family_research_profile`, `asset_family_research_dossier`, cobertura/gaps de librería y trazas de adquisición de fuentes autoritativas versionadas;
- fusiona `source_register` público con `structured_local_source_register` y `raw_local_source_register` derivados del pipeline, y sobre ese conjunto calcula precedencia, conflictos y outcomes de resolución;
- resuelve entidad, owner/operator/tenant y boundary con `entity_resolution_register`, `entity_conflict_register`, `asset_boundary_resolution_register` y `owner_operator_tenant_resolution_register`;
- arma `operational_intake_pack` con los diez diligence packs canónicos, sus estados sincronizados, focos por familia y señales de packs de proceso, control, mantenimiento, medición, clima y finanzas;
- extrae evidencia local utilizable de utility bills, tariffs, permits, lease matrices, submetering, BMS, CMMS, maintenance y operator inputs para poblar registers especializados;
- deriva `stop_condition_register`, `downgrade_condition_register`, `escalation_condition_register`, `minimum_sufficient_evidence_register`, preguntas dinámicas de intake, prioridades, rival hypotheses, claim impacts, gap taxonomy y classes de necesidad de evidencia;
- calcula `local_evidence_binding_register`, upgrades de binding, confianza de verdad local, `operational_bounding_scorecard`, blockers de promoción y el `evidence_mode_state` final.

## what_it_does_not_do
- no emite cierre de claim final ni decide si una hipótesis ya es admisible para recomendación ejecutiva;
- no selecciona peer sets, correlaciones, loss patterns, fairness final, regulatory physics ni claim governance final; eso pertenece a `motor_050` en adelante;
- no convierte seed público o hints de brochure en verdad local suficientemente bounded;
- no elimina ni oculta conflictos de autoridad entre fuentes para facilitar promoción artificial;
- no reemplaza la necesidad de utility bills, meter maps, lease matrices, permits o maintenance proof cuando esos packs siguen en `requested_but_absent` o `public_context_only`;
- no diseña CAPEX, ROI ni plan de intervención; sólo organiza la base de evidencia y los blockers para que downstream lo haga con disciplina.

## why_it_exists
Existe como motor separado porque el framework necesitaba una frontera única entre discovery/instrumentación y razonamiento de congruencia. Antes de esta capa, el runtime podía tener piezas sueltas de routing, packs, documentos locales y blockers, pero no una normalización auditable que dijera qué modo de evidencia es legítimo en ese momento y por qué. `motor_049` resuelve ese problema: convierte inputs heterogéneos en un contrato único de familia de activo, local binding, intake dinámico y promoción gobernada, evitando que los motores posteriores arranquen sobre una mezcla ambigua de contexto público y supuesta verdad local.
