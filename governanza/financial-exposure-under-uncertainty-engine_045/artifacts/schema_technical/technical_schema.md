# Technical Schema — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## entities
- `StructuralFinancialExposureRecord`
- `EvidenceStateByLayerRecord`
- `StructuralFinancialExposureRegister`
- `EvidenceStateByLayerRegister`

## fields
- `structural_financial_exposure_register: list[StructuralFinancialExposureRecord]`
- `structural_financial_exposure_count: int`
- `evidence_state_by_layer_register: list[EvidenceStateByLayerRecord]`
- `evidence_state_by_layer_count: int`
- `StructuralFinancialExposureRecord.structural_assumption: str`
- `StructuralFinancialExposureRecord.evidence_state: str`
- `StructuralFinancialExposureRecord.financial_exposure_if_wrong: str`
- `StructuralFinancialExposureRecord.evidence_needed: str`
- `StructuralFinancialExposureRecord.allowed_financial_output: str`
- `StructuralFinancialExposureRecord.prohibited_financial_output: str`
- `EvidenceStateByLayerRecord.layer: str`
- `EvidenceStateByLayerRecord.evidence_state: str`
- `EvidenceStateByLayerRecord.dominant_open_questions: str`
- `EvidenceStateByLayerRecord.observed_support: str`
- `EvidenceStateByLayerRecord.structural_risk_if_wrong: str`
- `EvidenceStateByLayerRecord.linked_conflicts: list[str]`
- `EvidenceStateByLayerRecord.linked_problem_frames: list[str]`

## relationships
- `motor_038` + `motor_040` + `motor_041` + `motor_044` -> `structural_financial_exposure_register`
- `motor_037` + `motor_038` + `motor_040` + `motor_041` + `motor_043` + financial exposure register -> `evidence_state_by_layer_register`
- counts referencian el cardinal de cada register

## identifiers
- `motor_id = motor_045`
- la fila financiera se identifica lógicamente por `structural_assumption`
- la fila de capa se identifica por `layer`

## versioning
- este schema documenta la superficie actual del runtime wrapper y del `Motor045Adapter`
- cualquier ampliación debe preservar compatibilidad con los counts
- cambios en las 12 capas requieren revisar tests y consumidores downstream

## lineage
- upstream principal: `motor_037`, `motor_038`, `motor_040`, `motor_041`, `motor_043`, `motor_044`
- downstream principal: `motor_034`, síntesis y reportes financieros bounded
- la lineage debe permitir rastrear qué conflicto y qué framing sostienen cada exposición

## input_dependencies
- `motor_037.system_abstraction`
- `motor_038.dominant_variable_register`
- `motor_040.cross_layer_conflict_register`
- `motor_041.problem_framing_register`
- `motor_043.competitive_comparison_register`
- `motor_044.conditional_redesign_register`
- contextual target definition from `motor_012` or `motor_007`

## behavioral_constraints
- `structural_financial_exposure_count == len(structural_financial_exposure_register)`
- `evidence_state_by_layer_count == len(evidence_state_by_layer_register)`
- las capas del register por layer deben permanecer en 12
- `prohibited_financial_output` no puede quedar vacío en una fila emitida
