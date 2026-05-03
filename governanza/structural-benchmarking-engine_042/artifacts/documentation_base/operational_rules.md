# Operational Rules — Structural Benchmarking Engine

Motor ID: motor_042

## rules
1. Todo benchmark debe ser bounded por arquetipo, variable dominante y coverage real.
2. Buildings con coverage LL84/LL97 pueden emitir benchmark de screening público observado.
3. Manufacturing debe mantener el benchmark como contexto de proceso, no como cierre directo de waste.
4. Cada fila debe explicar cómo interpretar el benchmark y qué no concluir todavía.

## invariants
- `structural_benchmark_count` igual al largo del register;
- ninguna fila sin `interpretation`;
- `evidence_state` restringido a observada, condicional o arquetipal.

## forbidden_operations
- declarar retrofit economics o desperdicio final a partir del benchmark;
- usar benchmark sin arquetipo o coverage suficiente;
- convertir peer/best practice en claim cerrado.
