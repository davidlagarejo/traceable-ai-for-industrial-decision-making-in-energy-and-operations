# Functional Contract — Congruence Strategic Insight and Claim Governor

Motor ID: motor_054

## inputs
- `asset_family_research_profile`
  Tipo: `dict`
  Productor: `motor_049`
  Uso: familia del activo para orientar TAD y claims.
- señales de comparación, gap y priorización
  Tipo: `list[dict]`
  Productor: `motor_051`
  Uso: invalid comparison, invalid problem frame, gap taxonomy, evidence classes.
- maintenance, measurement y patrones activados
  Tipo: `list[dict]`
  Productor: `motor_052`
  Uso: restricciones prácticas sobre claims y acciones.
- traducciones regulatorias y finance-to-physics
  Tipo: `list[dict]`
  Productor: `motor_053`
  Uso: cerrar uso permitido, prohibido y claims admisibles.

## outputs
- `gold_nugget_register`
- `gold_nugget_strength_register`
- `strategic_gold_nugget_register`
- `congruence_action_priority_register`
- `congruence_tad_enrichment_register`
- `expanded_tad_action_register`
- `prohibited_action_register`
- `congruence_claim_contract_register`
- y counts asociados.

## limits
- ningún claim puede carecer de falsification condition;
- ninguna acción puede perder su estado de prohibición si aplica;
- no puede convertir un nugget en hecho soberano fuera del contrato;
- no puede borrar evidencia mínima requerida o supporting sources.

## validations
- cada claim contract debe tener `claim_id`, `permission`, `supporting_sources`, `falsification_condition`, `minimum_evidence_required`, `allowed_use` y `prohibited_use`;
- los counts deben permanecer sincronizados;
- manufacturing debe emitir claims gobernados sobre comparación inválida, measurement minimality, regulatory physics y finance physics.
