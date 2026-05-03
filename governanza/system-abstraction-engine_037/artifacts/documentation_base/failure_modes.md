# Failure Modes — System Abstraction Engine

Motor ID: motor_037

## failure_modes_list
- `ARCHETYPE_TRUTH_COLLAPSE`: tratar un prior de arquetipo como hecho observado en varias dimensiones.
- `REGULATORY_FALSE_POSITIVE`: declarar exposición regulatoria observada sin dataset o source markers suficientes.
- `CONTROL_BOUNDARY_INVENTION`: cerrar owner vs tenant o control topology sin evidencia de campo.
- `UNBOUNDED_ASSET_MASKING`: producir abstracción útil para un target que aún no es un activo físico bounded.

## anti_patterns
- reutilizar texto del arquetipo como output final sin recalificar `evidence_state`;
- mezclar coverage pública y clues de campo sin distinguir base observada vs hipótesis.

## degradation_signals
- demasiadas dimensiones marcadas `OBSERVED_FACT` en casos con evidencia pobre;
- `evidence_maturity` observado cuando `screening_supported=false`;
- bundle estructural emitido para clasificaciones inadmisibles.
