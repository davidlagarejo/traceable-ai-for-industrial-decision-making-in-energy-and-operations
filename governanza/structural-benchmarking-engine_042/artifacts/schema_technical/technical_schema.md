# Technical Schema — Structural Benchmarking Engine

Motor ID: motor_042

## entities
- `StructuralBenchmarkRecord`
- `StructuralBenchmarkRegister`

## fields
- `StructuralBenchmarkRecord`
  `dimension: str (required)`
  `subject_asset: str (required)`
  `peer_or_benchmark: str (required)`
  `difference: str (required)`
  `evidence_state: str (required)`
  `interpretation: str (required)`
- `StructuralBenchmarkRegister`
  `structural_benchmark_register: list[StructuralBenchmarkRecord] (required)`
  `structural_benchmark_count: int (required)`

## relationships
- arquetipo, abstracción, variables dominantes y coverage alimentan cada record benchmark.

## identifiers
- Identificador natural de `StructuralBenchmarkRecord`: combinación `dimension + peer_or_benchmark`.
- Identificador natural de `StructuralBenchmarkRegister`: target bounded del caso.

## versioning
- cambios de arquetipo, dominant variables o coverage exigen regenerar el register;
- el count plano se regenera con cada versión.

## lineage
- `subject_asset` y `peer_or_benchmark` nacen de `target_definition` y `archetype_resolution`;
- `difference`, `evidence_state` e `interpretation` nacen de `system_abstraction`, dominant variables y coverage.
