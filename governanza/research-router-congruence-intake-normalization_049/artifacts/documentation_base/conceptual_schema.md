# Conceptual Schema — Research Router & Congruence Intake Normalization

Motor ID: motor_049

## entities
- `CaseFingerprint`
  Identificador estable del caso target que permite aislar investigación, intake y packaging downstream.
- `AssetFamilyResearchProfile`
  Perfil operativo del caso con `asset_family`, `route_state`, `research_mode`, fuentes autoritativas esperadas y rutas típicas de proceso/medición.
- `AssetFamilyResearchDossier`
  Snapshot versionado de la librería de research para la familia elegida.
- `NormalizedSourceRegister`
  Unión gobernada de fuentes públicas, structured local y raw local.
- `SourceAuthorityConflict`
  Conflicto de autoridad o de claim domain detectado dentro del source register normalizado.
- `EntityResolutionRecord`
  Resolución o conflicto de asset name, owner, operator y boundaries.
- `OperationalIntakePack`
  Bundle canónico de packs operativos, seed research y estados de evidencia.
- `DiligencePack`
  Unidad atómica de diligencia local como utility bills, tariffs, throughput schedule, equipment inventory, metering boundary, lease, maintenance, BMS, CMMS y permit detail.
- `LocalEvidenceBindingRecord`
  Registro que dice qué claims siguen unbound, cuáles quedaron partially bound y cuáles ya están sufficiently bound.
- `OperationalBoundingScorecard`
  Scorecard de promoción que define el `evidence_mode_state` final del caso.
- `DynamicIntakeQuestion`
  Pregunta operatoria discriminante que busca cerrar un gap concreto de evidencia o de hipótesis rival.
- `GapTaxonomyEntry`
  Taxonomía del gap detectado, su impacto en claims y la clase de evidencia requerida.
- `PromotionBlocker`
  Bloqueador explícito que impide subir el modo de evidencia del caso.

## relationships
- `TargetDefinition` + `TargetClassificationObject` + `asset_field_register` -> `AssetFamilyResearchProfile`
- `AssetFamilyResearchProfile` -> selecciona exactamente un `AssetFamilyResearchDossier`
- `source_register` público + `structured_local_source_register` + `raw_local_source_register` -> `NormalizedSourceRegister`
- `NormalizedSourceRegister` -> produce `SourceAuthorityConflict`, `EntityResolutionRecord` y evidencia local especializada
- `AssetFamilyResearchProfile` + `LocalEvidenceBindingRecord` + `NormalizedSourceRegister` -> `OperationalIntakePack`
- `OperationalIntakePack.diligence_pack_register` contiene muchas `DiligencePack`
- `OperationalIntakePack` + `discovery_need_register` + `stop_condition_register` -> muchas `DynamicIntakeQuestion`
- `DynamicIntakeQuestion` + `stop_condition_register` -> `required_from_register`, `intake_priority_register`, `rival_hypothesis_register`, `hypothesis_discrimination_register`, `claim_impact_register`
- `claim_impact_register` + blockers -> `GapTaxonomyEntry` -> `evidence_need_class_register`
- `OperationalIntakePack` + `AssetFamilyResearchProfile` -> `OperationalBoundingScorecard`
- `SourceAuthorityConflict` o asset-boundary failures críticos -> `PromotionBlocker`

## key_fields
- `CaseFingerprint`
  - `case_fingerprint: str`
- `AssetFamilyResearchProfile`
  - `asset_family: str`
  - `route_state: str`
  - `research_mode: str`
  - `authoritative_source_families: list[str]`
  - `typical_processes: list[str]`
  - `typical_subsystems: list[str]`
  - `typical_measurement_paths: list[str]`
- `AssetFamilyResearchDossier`
  - `asset_family: str`
  - `productization_state: str`
  - `research_library_version: str`
- `NormalizedSourceRegister`
  - `source_id: str`
  - `source_family: str`
  - `authority_score: str`
  - `round_id: str`
  - `used_for: list[str]`
- `SourceAuthorityConflict`
  - `conflict_domain: str`
  - `resolution_state: str`
  - `severity: str`
  - `lead_value: str`
- `EntityResolutionRecord`
  - `entity_type: str`
  - `resolution_state: str`
  - `source_id: str`
- `OperationalIntakePack`
  - `asset_family: str`
  - `research_mode: str`
  - `asset_identity_pack: dict`
  - `diligence_pack_register: list[dict]`
  - `diligence_pack_state_summary: dict`
- `DiligencePack`
  - `pack_name: str`
  - `current_state: str`
  - `decision_relevance: str`
  - `expected_local_sources: list[str]`
  - `present_source_families: list[str]`
  - `binding_needed: list[str]`
- `LocalEvidenceBindingRecord`
  - `claim_key: str`
  - `current_local_binding_state: str`
  - `local_binding_needed: list[str]`
  - `binding_basis: list[str]`
- `OperationalBoundingScorecard`
  - `bounded_asset_gate_passed: bool`
  - `evidence_mode_state: str`
  - `next_promotable_mode: str`
  - `hybrid_score: int`
  - `operator_score: int`
  - `required_hybrid_count: int`
  - `required_operator_count: int`
- `DynamicIntakeQuestion`
  - `question_id: str`
  - `intake_question: str`
  - `priority: str`
  - `required_from: str`
- `GapTaxonomyEntry`
  - `gap_code: str`
  - `gap_class: str`
  - `claim_impact: str`
  - `needed_evidence_class: str`
- `PromotionBlocker`
  - `blocker_code: str`
  - `severity: str`
  - `blocks_mode: str`
  - `why: str`
