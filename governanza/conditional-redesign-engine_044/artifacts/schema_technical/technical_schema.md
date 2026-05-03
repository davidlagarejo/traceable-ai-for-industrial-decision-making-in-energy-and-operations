# Technical Schema — Conditional Redesign Engine

Motor ID: motor_044

## entities
- `ConditionalRedesignRecord`
- `ConditionalRedesignRegister`
- `HypothesisKillSwitch`

## fields
- `conditional_redesign_register: list[ConditionalRedesignRecord]`
- `conditional_redesign_count: int`
- `ConditionalRedesignRecord.hypothesis: str`
- `ConditionalRedesignRecord.evidence_state: str`
- `ConditionalRedesignRecord.if_confirmed: str`
- `ConditionalRedesignRecord.redesign_direction: str`
- `ConditionalRedesignRecord.if_falsified: str`
- `ConditionalRedesignRecord.trigger_hypothesis: str`
- `ConditionalRedesignRecord.conflict_resolved: str`
- `ConditionalRedesignRecord.economic_logic: str`
- `ConditionalRedesignRecord.evidence_needed: str`
- `ConditionalRedesignRecord.kill_condition: str`
- `ConditionalRedesignRecord.next_evidence: str`

## relationships
- `motor_038` + `motor_040` + `motor_041` + `motor_043` -> `conditional_redesign_register`
- `kill_condition` y `if_falsified` gobiernan la reversibilidad de la hipótesis
- `conditional_redesign_count` referencia el cardinal del register

## identifiers
- `motor_id = motor_044`
- el identificador lógico de fila es `hypothesis` + `redesign_direction`
- `conflict_resolved` debe rastrear la contradicción upstream que la fila intenta descomprimir

## versioning
- este schema documenta la superficie actual del runtime wrapper y del `Motor044Adapter`
- cualquier cambio de campos debe preservar compatibilidad con `conditional_redesign_count`
- cambios en `kill_condition` o `next_evidence` requieren revisar `test_spec.md` y consumers downstream

## lineage
- upstream principal: `motor_038`, `motor_040`, `motor_041`, `motor_043`
- downstream principal: `motor_045`, `motor_046`, síntesis ejecutiva
- la lineage debe conservar qué conflicto y framing sostienen cada hipótesis

## input_dependencies
- `motor_038.dominant_variable_register`
- `motor_040.cross_layer_conflict_register`
- `motor_041.problem_framing_register`
- `motor_043.competitive_comparison_register`
- contextual target definition from `motor_012` or `motor_007`

## output_schema
- `conditional_redesign_register: list[ConditionalRedesignRecord]`
- `conditional_redesign_count: int`

## behavioral_constraints
- `conditional_redesign_count == len(conditional_redesign_register)`
- cada fila debe tener `kill_condition`
- el rediseño no puede presentarse como recomendación final
- `if_confirmed` y `if_falsified` deben permanecer distinguibles
