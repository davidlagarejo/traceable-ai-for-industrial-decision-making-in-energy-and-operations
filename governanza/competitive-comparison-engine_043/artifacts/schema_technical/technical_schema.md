# Technical Schema — Competitive Comparison Engine

Motor ID: motor_043

## entities
- `CompetitiveComparisonRecord`
- `CompetitiveComparisonRegister`
- `PeerTransferabilityEnvelope`

## fields
- `competitive_comparison_register: list[CompetitiveComparisonRecord]`
- `competitive_comparison_count: int`
- `CompetitiveComparisonRecord.better_performer: str`
- `CompetitiveComparisonRecord.what_they_do_better: str`
- `CompetitiveComparisonRecord.structural_advantage: str`
- `CompetitiveComparisonRecord.why_it_matters: str`
- `CompetitiveComparisonRecord.transferability: str`
- `CompetitiveComparisonRecord.peer_type: str`
- `CompetitiveComparisonRecord.what_it_proves: str`
- `CompetitiveComparisonRecord.what_it_does_not_prove: str`
- `CompetitiveComparisonRecord.source_reference: str`
- `CompetitiveComparisonRecord.evidence_needed: str`
- `CompetitiveComparisonRecord.evidence_state: str`
- `CompetitiveComparisonRecord.comparison_mode: str`

## relationships
- `motor_039.archetype_resolution` + `motor_042.structural_benchmark_register` -> `competitive_comparison_register`
- `what_it_does_not_prove` y `transferability` limitan cómo downstream puede usar la comparación
- `competitive_comparison_count` referencia el cardinal del `competitive_comparison_register`

## identifiers
- `motor_id = motor_043`
- el identificador lógico de cada fila es el par `better_performer` + `peer_type`
- `source_reference` debe permitir rastrear si la comparación viene de peer observado o práctica arquetipal

## versioning
- este schema refleja la superficie actual del runtime wrapper y del `Motor043Adapter`
- ampliar `comparison_mode` requiere revisar `test_spec.md`, `failure_modes_spec.md` y consumers downstream
- cambios en `what_it_does_not_prove` o `transferability` no pueden romper la disciplina bounded del motor

## lineage
- upstream principal: `motor_039`, `motor_042`
- downstream principal: `motor_044`, `motor_047`, síntesis ejecutiva
- la lineage debe conservar qué benchmark estructural justificó cada comparación emitida

## input_dependencies
- `motor_039.archetype_resolution`
- `motor_042.structural_benchmark_register`
- contextual target definition from `motor_012` or `motor_007`

## output_schema
- `competitive_comparison_register: list[CompetitiveComparisonRecord]`
- `competitive_comparison_count: int`

## allowed_modes
- `conditional_comparison`
- `archetypal_best_practice`
- `observed_peer_pattern`

## behavioral_constraints
- `competitive_comparison_count == len(competitive_comparison_register)`;
- `what_it_does_not_prove` no puede quedar vacío;
- `comparison_mode` debe ser coherente con `evidence_state`;
- la comparación debe permanecer en el mismo arquetipo o peer type admisible;
- `evidence_needed` debe explicar qué faltaría para endurecer la comparación.
