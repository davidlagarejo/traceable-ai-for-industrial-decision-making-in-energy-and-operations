# Technical Schema — Fair Comparison and Congruence Engine

Motor ID: motor_051

## entities
- `FairComparisonProfile`
- `ComparisonValidityRecord`
- `PeerRequirementRecord`
- `PeerCandidateFamilyRecord`
- `ComparisonBlockerRecord`
- `InvalidComparisonRiskRecord`
- `StructuralCorrelationRecord`
- `CrossLayerCongruenceRecord`
- `ProblemFrameInvalidationRecord`

## fields
- `FairComparisonProfile`
  `asset_family: str (required)`
  `comparison_state: str (required)`
  `process_type: str (required)`
  `process_map_state: str (required)`
  `climate_context_state: str (required)`
  `operating_schedule_state: str (required)`
  `throughput_proxy_required: bool (required)`
  `throughput_proxy: str (required)`
  `throughput_proxy_state: str (required)`
  `control_boundary_state: str (required)`
  `control_boundary_count: int (required)`
  `maintenance_maturity_state: str (required)`
  `regulatory_context: str (required)`
  `technology_stack_hint: str (required)`
  `valid_peer_basis: list[str] (required)`
  `prohibited_peer_shortcuts: list[str] (required)`
- `ComparisonValidityRecord`
  `subject: str (required)`
  `peer_frame: str (required)`
  `comparable: bool (required)`
  `why: str (required)`
  `normalization_required: list[str] (required)`
  `invalid_comparison_risk: str (required)`
  `evidence_state: str (required)`
- `CrossLayerCongruenceRecord`
  `contradiction: str (required)`
  `layers: list[str] (required)`
  `strategic_risk: str (required)`
  `evidence_needed: list[str] (required)`
  `possible_redesign: list[str] (required)`
  `evidence_state: str (required)`
  `supporting_correlation_count: int (required)`
- aggregate surfaces
  `comparison_validity_register: list[ComparisonValidityRecord] (required)`
  `normalization_requirements_register: list[dict] (required)`
  `peer_requirement_register: list[PeerRequirementRecord] (required)`
  `peer_candidate_family_register: list[PeerCandidateFamilyRecord] (required)`
  `comparison_blocker_register: list[ComparisonBlockerRecord] (required)`
  `comparison_not_yet_valid_register: list[dict] (required)`
  `invalid_comparison_risk_register: list[InvalidComparisonRiskRecord] (required)`
  `structural_correlation_register: list[StructuralCorrelationRecord] (required)`
  `structural_correlation_graph: list[dict] (required)`
  `correlation_priority_register: list[dict] (required)`
  `gold_nugget_candidate_register: list[dict] (required)`
  `cross_layer_congruence_register: list[CrossLayerCongruenceRecord] (required)`
  `invalid_problem_frame_register: list[ProblemFrameInvalidationRecord] (required)`
  `gap_taxonomy_register: list[dict] (required)`
  `evidence_need_class_register: list[dict] (required)`

## relationships
- `FairComparisonProfile` gobierna `ComparisonValidityRecord`, peer requirements y normalization requirements.
- `subsystem_register`, `control_boundary_map` y `operational_intake_pack` alimentan correlaciones estructurales.
- correlaciones y fairness profile alimentan `CrossLayerCongruenceRecord` e invalid problem frames.
- risks de comparación extienden la taxonomía de gaps heredada de `motor_049`.

## identifiers
- Identificador natural de `ComparisonValidityRecord`: `peer_frame`.
- Identificador natural de `CrossLayerCongruenceRecord`: `contradiction`.
- Identificador natural de `FairComparisonProfile`: target bounded heredado del bundle `motor_049`.

## versioning
- Cambios en process map, boundaries o binding state implican nueva versión del fairness profile.
- Cualquier cambio en comparación válida/inválida requiere regenerar blockers, risks y taxonomía extendida.
- Los counts planos deben reflejar cada nueva versión de los registers.

## lineage
- fairness profile y peer requirements nacen de `motor_049` + `motor_050`;
- correlaciones nacen de subsystems, boundaries y maintenance dependencies;
- contradicciones e invalid problem frames nacen de correlaciones más fairness profile;
- gap taxonomy extendida conserva lineage de `motor_049` y agrega comparación inválida.
