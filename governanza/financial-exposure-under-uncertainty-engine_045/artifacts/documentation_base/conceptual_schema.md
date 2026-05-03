# Conceptual Schema — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## entities
- `StructuralFinancialExposureRecord`
- `EvidenceStateByLayerRecord`
- `StructuralFinancialExposureRegister`
- `EvidenceStateByLayerRegister`

## relationships
- conflicto + framing + rediseño condicional -> `StructuralFinancialExposureRegister`
- sistema + variables + comparación + exposición financiera -> `EvidenceStateByLayerRegister`
- cada `EvidenceStateByLayerRecord` referencia conflictos y problem frames que abren o cierran esa capa

## key_fields
- `StructuralFinancialExposureRecord`: `structural_assumption`, `evidence_state`, `financial_exposure_if_wrong`, `evidence_needed`, `allowed_financial_output`, `prohibited_financial_output`
- `EvidenceStateByLayerRecord`: `layer`, `evidence_state`, `dominant_open_questions`, `observed_support`, `structural_risk_if_wrong`, `linked_conflicts`, `linked_problem_frames`

## invariants
- ninguna fila financiera puede permitir ROI o payback si el supuesto sigue condicional;
- cada capa debe mostrar qué pregunta dominante sigue abierta;
- el registro por capas no es decorativo: debe explicar por qué una afirmación financiera sigue o no sigue bloqueada.
