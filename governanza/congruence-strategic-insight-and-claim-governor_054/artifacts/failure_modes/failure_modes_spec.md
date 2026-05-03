# Failure Modes Spec — Congruence Strategic Insight and Claim Governor

Motor ID: motor_054

## failure_modes_list
- `CONTRACT_HOLLOWING`: contrato de claim sin campos de gobernanza completos.
- `PROHIBITED_ACTION_REVERSAL`: acción prohibida tratada como permitida.
- `NUGGET_PROMOTION`: nugget estratégico promovido a hecho sin contrato.
- `SOURCE_DROP`: desaparecen fuentes de soporte o evidencia mínima.

## anti_patterns
- mezclar nuggets y claim contracts como si fueran lo mismo;
- usar claim permission sin falsificación;
- perder la relación con finance-to-physics.

## degradation_signals
- claim contracts muy cortos o vagos;
- same text repetido para allowed_use y prohibited_use;
- no aparecen supporting sources.

## expensive_errors
- afirmaciones ejecutivas indefendibles;
- priorización de acción fuera de gobierno;
- claims que rompen consistencia sistémica downstream.
