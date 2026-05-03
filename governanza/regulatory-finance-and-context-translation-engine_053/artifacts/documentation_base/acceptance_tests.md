# Acceptance Tests — Regulatory, Finance and Context Translation Engine

Motor ID: motor_053

## acceptance_cases
- Building:
  Debe ligar owner economics a whole-building performance pressure y control boundary.
- Manufacturing:
  Debe ligar lógica de costo a proceso, uptime y downtime.
- Sparse sources:
  Puede emitir context registers bounded sin usarlos como sustituto de prueba física.

## acceptance_threshold
- existen filas en regulación y finanzas para building y manufacturing;
- `financial_assumption` siempre aparece junto a una dependencia física;
- los counts principales permanecen sincronizados;
- context registers expresan usos permitidos y prohibidos.
