# Technical Schema — Congruence Strategic Insight and Claim Governor

Motor ID: motor_054

## entities
- `StrategicGoldNuggetRecord`
- `ActionPriorityRecord`
- `ClaimContractRecord`
- `ProhibitedActionRecord`

## fields
- `gold_nugget_register: list[StrategicGoldNuggetRecord]`
- `gold_nugget_strength_register: list[dict]`
- `strategic_gold_nugget_register: list[StrategicGoldNuggetRecord]`
- `congruence_action_priority_register: list[ActionPriorityRecord]`
- `congruence_tad_enrichment_register: list[dict]`
- `expanded_tad_action_register: list[dict]`
- `prohibited_action_register: list[ProhibitedActionRecord]`
- `congruence_claim_contract_register: list[ClaimContractRecord]`
- count surfaces: `gold_nugget_count`, `gold_nugget_strength_count`, `strategic_gold_nugget_count`, `congruence_action_priority_count`, `expanded_tad_action_count`, `prohibited_action_count`, `congruence_claim_contract_count`

## relationships
- `motor_049` + `motor_051` + `motor_052` + `motor_053` -> action priorities, nuggets and claim contracts
- expanded TAD actions feed prohibited actions
- claim contracts combine nuggets, action priorities and regulatory/finance surfaces

## identifiers
- `motor_id = motor_054`
- `ClaimContractRecord.claim_id` es el identificador primario de claim
- nuggets y acciones deben conservar identificadores o statements distinguibles

## versioning
- este schema documenta la superficie actual del runtime wrapper y del `Motor054Adapter`
- cambios en claim contract fields requieren revisar tests y consumers downstream
- la compatibilidad exige preservar supporting sources, falsification y allowed/prohibited use

## lineage
- upstream principal: `motor_049`, `motor_051`, `motor_052`, `motor_053`
- downstream principal: síntesis ejecutiva, claim surfaces y reportes
- la lineage debe rastrear qué señales de congruencia o finance-to-physics sostuvieron cada claim

## input_dependencies
- `motor_049.asset_family_research_profile`
- `motor_051.invalid_comparison_risk_register`
- `motor_051.invalid_problem_frame_register`
- `motor_051.gap_taxonomy_register`
- `motor_051.evidence_need_class_register`
- `motor_051.comparison_not_yet_valid_register`
- `motor_051.gold_nugget_candidate_register`
- `motor_052.measurement_strategy_register`
- `motor_052.maintenance_reality_register`
- `motor_052.activated_pattern_register`
- `motor_052.loss_pattern_hypothesis_register`
- `motor_053.regulatory_physics_register`
- `motor_053.finance_physics_dependency_register`
- `motor_053.financial_exposure_type_register`
- `motor_053.culture_execution_proxy_register`

## claim_contract_record
- `claim_id: str`
- `claim_family: str`
- `statement: str`
- `permission: str`
- `evidence_state: str`
- `supporting_sources: list[str]`
- `assumptions: list[str]`
- `falsification_condition: str`
- `minimum_evidence_required: list[str] | str`
- `allowed_use: str`
- `prohibited_use: str`
- `current_evidence_summary: str`

## behavioral_constraints
- `congruence_claim_contract_count == len(congruence_claim_contract_register)`
- ningún claim contract puede omitir `supporting_sources`
- ningún claim contract puede omitir `prohibited_use`
- los nuggets estratégicos no liberan claims fuera del contrato
