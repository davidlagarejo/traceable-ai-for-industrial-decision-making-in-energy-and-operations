# Conceptual Schema — Structural Benchmarking Engine

Motor ID: motor_042

## entities
- `StructuralBenchmarkRecord`
- `StructuralBenchmarkRegister`
- `BenchmarkSelectionContext`
- `BoundedInterpretationEnvelope`

## relationships
- arquetipo + abstracción + variables dominantes + coverage → `StructuralBenchmarkRegister`
- `BenchmarkSelectionContext` determina qué peer set es admisible para el asset sin saltar a comparables financieros o estratégicos.
- `BoundedInterpretationEnvelope` encapsula la lectura permitida de cada diferencia para que downstream pueda usarla sin convertirla en decisión final.

## key_fields
- `StructuralBenchmarkRecord`: `dimension`, `subject_asset`, `peer_or_benchmark`, `difference`, `evidence_state`, `interpretation`
- `StructuralBenchmarkRegister`: lista de `StructuralBenchmarkRecord` y count plano
- `BenchmarkSelectionContext`: `asset_kind`, `operating_envelope`, `control_boundary`, `evidence_basis`, `benchmark_scope`
- `BoundedInterpretationEnvelope`: `usable_for`, `not_usable_for`, `confidence_posture`, `handoff_target`

## invariants
- Cada fila de benchmark debe comparar dimensiones estructurales, no concluir ranking competitivo final.
- El `peer_or_benchmark` tiene que ser explicable desde arquetipo, cobertura regulatoria, escala operativa o madurez del sistema.
- `difference` puede expresar gap, asymmetry o missing parity, pero no inferir causa raíz por sí sola.
- `interpretation` debe permanecer bounded y dejar explícito si la lectura alimenta `motor_043`, `motor_051` u otros motores posteriores.
