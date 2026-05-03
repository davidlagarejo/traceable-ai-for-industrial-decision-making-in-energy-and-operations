# Conceptual Schema — Search / Discovery Intelligence Layer

Motor ID: motor_028

## entities
1. `DiscoveryRequest`: solicitud gobernada que define el alcance de una busqueda.
2. `DiscoveryPlan`: plan reproducible de busqueda derivado de una solicitud, taxonomia y senales de refresh.
3. `CoverageGapRecord`: registro de hueco de cobertura o necesidad de descubrimiento.
4. `SourceCandidateRecord`: fuente candidata propuesta para revision, no admitida aun como fuente registrada.
5. `DiscoveryRunManifest`: manifiesto de ejecucion que conserva lineage, consultas y resultados de una corrida.
6. `DiscoveryRejectionRecord`: razon estructurada por la cual un hallazgo no se emite como candidato valido.

## relationships
- Un `DiscoveryRequest` produce cero o mas `DiscoveryPlan`.
- Un `DiscoveryPlan` referencia exactamente un scope taxonomico principal y puede usar muchas senales de refresh.
- Un `DiscoveryPlan` produce un `DiscoveryRunManifest` por corrida ejecutada.
- Un `DiscoveryRunManifest` puede contener cero o mas `SourceCandidateRecord` y cero o mas `DiscoveryRejectionRecord`.
- Un `CoverageGapRecord` puede originar uno o mas `DiscoveryRequest`, y cada candidato puede apuntar a uno o mas gaps que justifican su busqueda.
- Un `SourceCandidateRecord` puede referenciar un `source_id` existente cuando el resultado parece ser rediscovery o posible duplicado.

## key_fields
- `DiscoveryRequest`: `request_id:string`, `scope_terms:list[string]`, `jurisdiction:string|null`, `time_window:string|null`, `priority:string`, `requested_by:string`, `reason:string`, `created_at:datetime`.
- `DiscoveryPlan`: `plan_id:string`, `request_id:string`, `queries:list[string]`, `filters:object`, `allowed_access_classes:list[string]`, `taxonomy_version:string`, `stop_conditions:list[string]`.
- `CoverageGapRecord`: `gap_id:string`, `scope_terms:list[string]`, `gap_type:string`, `supporting_signal_ids:list[string]`, `severity:string`, `observed_at:datetime`.
- `SourceCandidateRecord`: `candidate_id:string`, `locator:string`, `title:string`, `publisher:string|null`, `source_type:string`, `matched_terms:list[string]`, `discovery_reason:string`, `candidate_status:string`, `provenance:object`.
- `DiscoveryRunManifest`: `run_id:string`, `plan_id:string`, `input_versions:object`, `executed_queries:list[object]`, `candidate_ids:list[string]`, `rejection_ids:list[string]`, `run_started_at:datetime`, `run_completed_at:datetime`.
- `DiscoveryRejectionRecord`: `rejection_id:string`, `run_id:string`, `locator:string|null`, `reason_code:string`, `reason_detail:string`, `observed_at:datetime`.
