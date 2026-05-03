# Conceptual Schema — Competitive Comparison Engine

Motor ID: motor_043

## entities
- `CompetitiveComparisonRecord`
- `CompetitiveComparisonRegister`
- `TransferabilityEnvelope`
- `EvidenceBoundedPeer`

## relationships
- arquetipo + benchmark estructural -> `CompetitiveComparisonRegister`
- cada `CompetitiveComparisonRecord` referencia un `EvidenceBoundedPeer`
- `TransferabilityEnvelope` expresa qué parte de la ventaja comparativa podría migrar al asset y qué parte no

## key_fields
- `CompetitiveComparisonRecord`: `better_performer`, `what_they_do_better`, `structural_advantage`, `why_it_matters`, `transferability`, `peer_type`, `what_it_proves`, `what_it_does_not_prove`, `source_reference`, `evidence_needed`, `evidence_state`, `comparison_mode`
- `CompetitiveComparisonRegister`: lista de `CompetitiveComparisonRecord` y count plano
- `TransferabilityEnvelope`: `transferability`, `evidence_needed`, `what_it_does_not_prove`
- `EvidenceBoundedPeer`: peer o práctica de referencia descrita con estado de evidencia y modo comparativo

## invariants
- toda comparación debe permanecer bounded al arquetipo y benchmark admisible;
- `what_it_does_not_prove` es obligatorio para impedir overclaim;
- `comparison_mode` distingue comparación condicional de best practice arquetipal;
- la comparación puede ser útil aunque exista una sola fila, siempre que conserve transferabilidad y límites;
- la ventaja estructural nunca debe leerse como resultado económico final.
