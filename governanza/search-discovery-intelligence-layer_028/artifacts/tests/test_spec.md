# Test Spec — Search / Discovery Intelligence Layer

Motor ID: motor_028

## happy_path

**Escenario:** Búsqueda de fuentes regulatorias nuevas sobre energía renovable en jurisdicciones con cobertura insuficiente.

**Input:**
```python
discovery_request = {
    "request_id": "req_001",
    "scope_terms": ["energia_renovable", "regulacion_energetica"],
    "jurisdiction": "latam",
    "time_window": "2020-2024",
    "priority": "high",
    "requested_by": "orchestrator",
    "reason": "gap de cobertura detectado por motor_009 en jurisdicciones LATAM",
    "version": "1.0",
    "created_at": "2026-01-01T00:00:00Z",
}
canonical_taxonomy_scope = {
    "version": "taxonomy_v3",
    "terms": [
        {"term": "energia_renovable", "aliases": ["renewable_energy", "energias_limpias"]},
        {"term": "regulacion_energetica", "aliases": ["energy_regulation"]},
    ],
    "produced_by": "motor_003",
}
source_registry_snapshot = {
    "version": "registry_v5",
    "sources": [{"source_id": "src_001", "domain": "energia_renovable", "jurisdiction": "eu"}],
    "produced_by": "motor_008",
}
refresh_intelligence_signals = {
    "version": "signals_v2",
    "signals": [
        {"signal_id": "sig_001", "type": "low_coverage", "domain": "energia_renovable", "jurisdiction": "latam", "severity": "high"},
    ],
    "produced_by": "motor_009",
}
prior_discovery_log = {"version": "log_v1", "entries": []}
```

**Output correcto:**
- `DiscoveryPlan` con `plan_id` determinista, `scope_terms=["energia_renovable", "regulacion_energetica"]`, `queries` no vacío, `input_versions` con versiones de los 5 inputs
- Al menos un `SourceCandidateRecord` con `locator` no vacío, `candidate_status="proposed"`, `discovery_classification` en `{"new_candidate", "rediscovery", "potential_duplicate"}`, `rights_review_required=True`, `provenance` referenciando el plan y la corrida
- `DiscoveryRunManifest` con `run_status` en `{"completed", "completed_with_warnings"}`, `candidate_ids` y `rejection_ids` presentes, `executed_queries` no vacío
- Cero `SourceCandidateRecord` con `candidate_status` distinto de `"proposed"`

## sparse_case

**Escenario:** `prior_discovery_log` vacío y `refresh_intelligence_signals` sin señales activas. Inputs mínimos válidos pero sin señales de gap.

**Input:** `discovery_request` válido con scope canónico; `refresh_intelligence_signals.signals=[]`; `prior_discovery_log.entries=[]`.

**Comportamiento esperado:**
- El motor procesa sin error fatal
- Emite un `DiscoveryPlan` con `queries` derivadas del scope taxonómico aunque no haya señales de refresh
- El `DiscoveryRunManifest` puede tener `candidate_ids=[]` si no se detectan candidatos nuevos
- Si el plan genera queries pero no hay candidatos, `run_status="empty_result"` y `limitations_observed` documenta la ausencia de resultados
- No se fabrican candidatos para llenar la corrida

## malformed_input

**Escenario A — `discovery_request` sin scope taxonómico:**
```python
discovery_request = {"request_id": "req_bad", "reason": "sin scope"}
```
**Resultado:** `SearchDiscoveryIntelligenceError` con código de error que indica `missing_scope_terms`. No se produce ningún output parcial.

**Escenario B — `canonical_taxonomy_scope` sin campo `terms`:**
```python
canonical_taxonomy_scope = {"version": "v1", "produced_by": "motor_003"}
```
**Resultado:** `SearchDiscoveryIntelligenceError` indicando taxonomía inválida. El motor no asume términos por defecto.

**Escenario C — Input con campo `body` o `content` (contenido raw):**
```python
source_registry_snapshot = {"version": "v1", "body": "<html>...", "produced_by": "motor_008"}
```
**Resultado:** `SearchDiscoveryIntelligenceError` o rechazo de input. El motor detecta la presencia de campos de contenido raw (`body`, `content`, `html`, `full_text`, `records`, `dataset`, `documents`, `raw_content`) y rechaza el input.

**Escenario D — `discovery_request` con `scope_terms` fuera de taxonomía:**
```python
discovery_request = {"request_id": "req_x", "scope_terms": ["dominio_no_canonico_xyz"], "reason": "test"}
```
**Resultado:** El motor puede rechazar el request o emitir `CoverageGapRecord` documentando términos no reconocidos. No crea dominios paralelos.

## edge_cases

**Edge case 1 — Candidato coincide con fuente ya registrada:**

Input: `source_registry_snapshot` contiene `src_001` con `locator="https://fuente-regulatoria.example.com"`. La corrida detecta un hallazgo con el mismo locator.

Resultado: El candidato se emite como `SourceCandidateRecord` con `discovery_classification="rediscovery"` o `"potential_duplicate"` y `linked_source_id="src_001"`. No se emite como `"new_candidate"`. El `DiscoveryRejectionRecord` puede registrarlo si se considera duplicado exacto.

**Edge case 2 — Candidato coincide con entrada previa del `prior_discovery_log`:**

Input: `prior_discovery_log` contiene un candidato previo con el mismo locator.

Resultado: El motor no reemite el candidato como nuevo. Emite `DiscoveryRejectionRecord` con `reason_code="prior_rejection"` o `"duplicate"` referenciando el candidato anterior. El locator no produce un segundo `SourceCandidateRecord` distinto.

**Edge case 3 — `discovery_request` con `scope_terms` con aliases múltiples:**

Input: `canonical_taxonomy_scope` define `"energia_renovable"` con alias `["renewable_energy", "energias_limpias"]`.

Resultado: El plan registra el término canónico y los aliases usados en las queries. Los candidatos encontrados con cualquier alias quedan asociados al término canónico en `domain_taxonomic`. No se crean dominios paralelos.

**Edge case 4 — Corrida sin ningún resultado:**

Input: Scope válido, señales activas, pero el adaptador no genera candidatos.

Resultado: `DiscoveryRunManifest` con `candidate_ids=[]`, `rejection_ids=[]`, `run_status="empty_result"`, `limitations_observed` documenta que no se encontraron candidatos con los filtros aplicados. El output es válido: la ausencia de resultados está registrada.

## pass_criteria

Un test pasa cuando:
1. `DiscoveryPlan.plan_id` es determinista: mismos inputs producen el mismo `plan_id` en corridas independientes
2. Todos los `SourceCandidateRecord` tienen `candidate_status="proposed"` y `provenance` con `plan_id`, `run_id` e `input_versions`
3. `DiscoveryRunManifest.candidate_ids` coincide exactamente con el conjunto de `candidate_id` en los `SourceCandidateRecord` emitidos
4. Ningún output contiene campos `body`, `content`, `html`, `full_text`, `records`, `dataset`, `documents` o `raw_content` con contenido persistido
5. Ningún output modifica `source_registry_snapshot`, `rights_profile` ni crea un `source_id` nuevo
6. Inputs malformados lanzan excepción antes de producir output parcial

## fail_criteria

Un test falla cuando:
1. Un `SourceCandidateRecord` tiene `candidate_status` distinto de `"proposed"`
2. Un candidato no tiene `locator`, `discovery_reason`, `provenance.plan_id` o `provenance.run_id`
3. El motor emite un candidato con el mismo locator que una fuente ya en `source_registry_snapshot` sin marcarlo como `rediscovery` o `potential_duplicate`
4. El motor emite un candidato que ya estaba en `prior_discovery_log` como `"new_candidate"` sin referencia al registro previo
5. `DiscoveryPlan.plan_id` varía entre corridas con los mismos inputs
6. Un input malformado produce output parcial en lugar de excepción
7. `DiscoveryRunManifest` no existe o `candidate_ids` no coincide con los candidatos emitidos
