# Conceptual Schema — Conditional Redesign Engine

Motor ID: motor_044

## entities
- `ConditionalRedesignRecord`
- `ConditionalRedesignRegister`
- `HypothesisKillSwitch`
- `EvidenceProgressionStep`

## relationships
- variables dominantes + conflictos + problem framing + comparación bounded -> `ConditionalRedesignRegister`
- cada `ConditionalRedesignRecord` debe enlazar un `HypothesisKillSwitch`
- `EvidenceProgressionStep` indica cuál es la siguiente evidencia antes de actuar

## key_fields
- `ConditionalRedesignRecord`: `hypothesis`, `evidence_state`, `if_confirmed`, `redesign_direction`, `if_falsified`, `trigger_hypothesis`, `conflict_resolved`, `economic_logic`, `evidence_needed`, `kill_condition`, `next_evidence`
- `ConditionalRedesignRegister`: lista de `ConditionalRedesignRecord` y count plano
- `HypothesisKillSwitch`: condición explícita que invalida la vía de rediseño

## invariants
- ninguna hipótesis de rediseño puede existir sin condición de muerte;
- `if_confirmed` y `if_falsified` deben ser distintos;
- el rediseño debe seguir siendo bounded al conflicto que busca resolver;
- la dirección de rediseño no puede leerse como decisión definitiva.
