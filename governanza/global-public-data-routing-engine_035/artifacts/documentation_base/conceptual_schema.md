# Conceptual Schema — Global Public Data Routing Engine

Motor ID: motor_035

## entities
- `TargetClassificationResult`
  Resultado efectivo de clasificación operacional usado para decidir si el target admite ruta técnica o debe degradarse.
- `JurisdictionResolution`
  Resolución de jurisdicción y clase regulatoria usada para seleccionar familias de fuentes públicas.
- `SourceRoutingPlan`
  Objeto central del motor. Agrupa fuentes en `mandatory`, `high_priority`, `optional` y lista de sustituciones prohibidas.
- `ReportTypeSwitchRecommendation`
  Recomendación de superficie de reporte cuando la ruta técnica no es compatible con el caso actual.
- `CriticalFieldSummary`
  Resumen de campos críticos presentes o faltantes para soportar search, benchmarking y scraping posterior.
- `RoutingEligibility`
  Señal operativa que explica si el caso puede entrar a una ruta técnica pública o debe quedarse en una superficie degradada.

## relationships
- `subject_definition_contract` + `target_definition_contract` + `target_classification_object` -> `TargetClassificationResult`
- `TargetClassificationResult` + `jurisdiction_scope` -> `JurisdictionResolution`
- `TargetClassificationResult` + `JurisdictionResolution` + `observable_clusters` -> `SourceRoutingPlan`
- `TargetClassificationResult` + `subject_gate_passed` + `technical_substrate_readiness` -> `RoutingEligibility`
- `RoutingEligibility` + restricciones upstream de reporte -> `ReportTypeSwitchRecommendation`
- `target_type` + clusters observables -> `CriticalFieldSummary`
- el adapter final aplana partes de `SourceRoutingPlan`, `JurisdictionResolution` y `ReportTypeSwitchRecommendation` a campos de conveniencia para downstream.

## key_fields
- `TargetClassificationResult`
  - `target_type: str`
  - `technical_scraping_allowed: bool`
  - `classification_reason: str`
- `JurisdictionResolution`
  - `jurisdiction_class: str`
  - `state: str`
  - `city: str`
  - `regulatory_stack: list[str]`
- `SourceRoutingPlan`
  - `asset_type: str`
  - `mandatory_sources: list[dict]`
  - `high_priority_sources: list[dict]`
  - `optional_sources: list[dict]`
  - `disallowed_substitutions: list[str]`
  - `routing_notes: list[str]`
- `ReportTypeSwitchRecommendation`
  - `recommended_report_type: str`
  - `prohibited_report_types: list[str]`
  - `reason: str`
- `CriticalFieldSummary`
  - `missing_critical_fields: int`
  - `critical_fields: list[dict]`
- `RoutingEligibility`
  - `decision_type: str`
  - `routing_ready: bool`
  - `blocking_reason: str`
