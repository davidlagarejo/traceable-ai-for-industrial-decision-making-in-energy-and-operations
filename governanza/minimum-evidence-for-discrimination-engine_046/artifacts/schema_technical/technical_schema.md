# Technical Schema — Minimum Evidence For Discrimination Engine

Motor ID: motor_046

## entities
- `MinimumEvidenceForDiscriminationRecord`
- `MinimumEvidenceForDiscriminationRegister`
- `RivalHypothesisSet`

## fields
- `minimum_evidence_for_discrimination_register: list[MinimumEvidenceForDiscriminationRecord]`
- `minimum_evidence_for_discrimination_count: int`
- `MinimumEvidenceForDiscriminationRecord.rival_hypotheses: str`
- `MinimumEvidenceForDiscriminationRecord.minimum_evidence: str`
- `MinimumEvidenceForDiscriminationRecord.source: str`
- `MinimumEvidenceForDiscriminationRecord.what_it_confirms: str`
- `MinimumEvidenceForDiscriminationRecord.what_it_falsifies: str`
- `MinimumEvidenceForDiscriminationRecord.unlocks: str`

## relationships
- `motor_038` + `motor_040` + `motor_041` + `motor_044` -> `minimum_evidence_for_discrimination_register`
- `unlocks` depende de la hipótesis de rediseño y del framing que se intenta discriminar
- `minimum_evidence_for_discrimination_count` referencia el cardinal del register

## identifiers
- `motor_id = motor_046`
- el identificador lógico de fila es `minimum_evidence` + `rival_hypotheses`

## versioning
- este schema documenta la superficie actual del runtime wrapper y del `Motor046Adapter`
- ampliar la fila requiere preservar compatibilidad con el count
- cambios en `minimum_evidence` o `unlocks` requieren revisar tests y consumidores downstream

## lineage
- upstream principal: `motor_038`, `motor_040`, `motor_041`, `motor_044`
- downstream principal: `motor_033`, intake guidance, síntesis
- la lineage debe permitir rastrear qué conflicto y qué rediseño condicional justificaron la evidencia pedida

## input_dependencies
- `motor_038.dominant_variable_register`
- `motor_040.cross_layer_conflict_register`
- `motor_041.problem_framing_register`
- `motor_044.conditional_redesign_register`
- contextual target definition from `motor_012` or `motor_007`

## behavioral_constraints
- `minimum_evidence_for_discrimination_count == len(minimum_evidence_for_discrimination_register)`
- `minimum_evidence` no puede ser vacío ni genérico;
- `what_it_confirms` y `what_it_falsifies` deben ser distintos;
- `unlocks` debe describir un cambio real de admisibilidad o siguiente paso.
