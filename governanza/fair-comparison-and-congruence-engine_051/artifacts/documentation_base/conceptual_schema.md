# Conceptual Schema — Fair Comparison and Congruence Engine

Motor ID: motor_051

## entities
- `FairComparisonProfile`: perfil global de comparabilidad y normalización.
- `ComparisonValidityRecord`: evaluación de una forma de comparación potencial.
- `PeerRequirementRecord`: requisito para peers admisibles.
- `InvalidComparisonRiskRecord`: riesgo de comparación inválida.
- `StructuralCorrelationRecord`: correlación estructural significativa.
- `CrossLayerCongruenceRecord`: contradicción entre capas físicas, regulatorias, operativas o de framing.
- `ProblemFrameInvalidationRecord`: framing aparente que debe rechazarse.

## relationships
- `asset_family_research_profile` + `process_map` + `control_boundary_map` + local binding → `FairComparisonProfile`
- `FairComparisonProfile` → `NormalizationRequirements`, `PeerRequirementRecord`, `ComparisonValidityRecord`
- `subsystem_register` + `control_boundary_map` + `operational_intake_pack` → `StructuralCorrelationRecord`
- `FairComparisonProfile` + correlaciones + dependencies → `CrossLayerCongruenceRecord`
- riesgos de comparación → extensión de `gap_taxonomy_register`

## key_fields
- `FairComparisonProfile`: `asset_family`, `comparison_state`, `process_type`, `throughput_proxy_required`, `control_boundary_state`, `valid_peer_basis`, `prohibited_peer_shortcuts`
- `ComparisonValidityRecord`: `subject`, `peer_frame`, `comparable`, `why`, `normalization_required`, `invalid_comparison_risk`, `evidence_state`
- `PeerRequirementRecord`: requisito de normalización o boundary para peer válido
- `InvalidComparisonRiskRecord`: `risk_name`, `why_invalid`, `blocked_claim_type`
- `StructuralCorrelationRecord`: `correlation`, `why_it_matters`, `evidence_state`
- `CrossLayerCongruenceRecord`: `contradiction`, `layers`, `strategic_risk`, `evidence_needed`, `possible_redesign`
- `ProblemFrameInvalidationRecord`: `apparent_problem`, `why_invalid`, `required_reframe`
