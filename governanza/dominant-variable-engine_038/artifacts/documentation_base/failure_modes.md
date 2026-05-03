# Failure Modes — Dominant Variable Engine

Motor ID: motor_038

## failure_modes_list
- `PRIOR_AS_OBSERVED`: prior arquetipal promovido a hecho observado sin soporte admisible.
- `REGULATORY_OVERPROMOTION`: `LL97_pathway` observado sin coverage real.
- `BOUNDARY_VARIABLE_OMISSION`: ausencia de `owner_control_boundary` en el register final.
- `FIELD_SIGNAL_COLLAPSE`: cualquier field de proceso promociona indebidamente múltiples variables sin distinción.

## anti_patterns
- usar el register como ranking final y no como capa gobernada de variables candidatas;
- colapsar building y manufacturing en la misma lógica de promoción.

## degradation_signals
- demasiadas variables observadas en casos con evidencia pobre;
- registers building sin variables de control o regulación;
- registers manufacturing sin throughput ni process-duty candidates.
