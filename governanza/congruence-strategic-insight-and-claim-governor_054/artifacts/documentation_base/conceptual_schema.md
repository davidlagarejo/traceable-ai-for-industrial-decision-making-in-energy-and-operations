# Conceptual Schema — Congruence Strategic Insight and Claim Governor

Motor ID: motor_054

## entities
- `StrategicGoldNuggetRecord`
- `ActionPriorityRecord`
- `ClaimContractRecord`
- `ProhibitedActionRecord`

## relationships
- congruence + maintenance + finance translation -> `ActionPriorityRecord`
- action priorities -> TAD enrichment and expanded actions
- strategic nuggets + action priorities + regulatory/finance context -> `ClaimContractRecord`
- expanded actions -> `ProhibitedActionRecord`

## key_fields
- `ClaimContractRecord`: `claim_id`, `claim_family`, `statement`, `permission`, `evidence_state`, `supporting_sources`, `assumptions`, `falsification_condition`, `minimum_evidence_required`, `allowed_use`, `prohibited_use`, `current_evidence_summary`
- `ActionPriorityRecord`: prioridad de acción gobernada con razón y estado
- `StrategicGoldNuggetRecord`: insight bounded con fuerza y límites

## invariants
- ningún claim contract puede existir sin uso permitido y uso prohibido;
- los nuggets estratégicos no reemplazan contratos de claim;
- la priorización de acción debe seguir bounded a evidencia y comparación válida;
- el motor puede prohibir acciones aunque existan nuggets prometedores.
