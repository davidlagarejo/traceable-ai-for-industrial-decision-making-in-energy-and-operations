# Conceptual Schema — Minimum Evidence For Discrimination Engine

Motor ID: motor_046

## entities
- `MinimumEvidenceForDiscriminationRecord`
- `MinimumEvidenceForDiscriminationRegister`
- `RivalHypothesisSet`
- `UnlockCondition`

## relationships
- variables dominantes + conflicto + framing + rediseño -> `MinimumEvidenceForDiscriminationRegister`
- cada fila referencia un `RivalHypothesisSet`
- `UnlockCondition` expresa qué decisión o siguiente paso se habilita si la evidencia llega

## key_fields
- `MinimumEvidenceForDiscriminationRecord`: `rival_hypotheses`, `minimum_evidence`, `source`, `what_it_confirms`, `what_it_falsifies`, `unlocks`

## invariants
- `minimum_evidence` debe ser más pequeño que una due diligence completa;
- `what_it_confirms` y `what_it_falsifies` no pueden decir lo mismo;
- la evidencia mínima debe estar ligada a hipótesis rivales reales y no a curiosidad documental.
