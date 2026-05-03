# Acceptance Tests — Problem Framing Engine

Motor ID: motor_041

## acceptance_cases
- Building:
  El motor recibe conflictos entre regulación, control boundary y economía owner-capturable.
  Debe reencuadrar el problema hacia qué loads y qué frontera de control dominan realmente la lógica LL97 y la economía del owner.
- Manufacturing:
  El motor recibe conflicto entre framing energético, carga estructural de proceso y mantenimiento.
  Debe reformular hacia proceso, uptime y prueba mínima antes de tratar el gasto energético como desperdicio.
- Logistics fallback:
  Si el framing estructural es inadmisible, debe traducir el invalid frame desde `motor_051` sin perder `linked_layers`.

## acceptance_threshold
- al menos una fila útil y auditables por caso;
- `problem_framing_count` sincronizado;
- `evidence_needed` presente;
- ningún caso convierte el framing en solución final.
