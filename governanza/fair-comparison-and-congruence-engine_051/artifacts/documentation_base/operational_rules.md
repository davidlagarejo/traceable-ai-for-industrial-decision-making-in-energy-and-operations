# Operational Rules — Fair Comparison and Congruence Engine

Motor ID: motor_051

## rules
1. Ninguna comparación es válida si el peer frame ignora la variable dominante que realmente controla el outcome.
2. Buildings deben exigir boundary owner-vs-tenant antes de permitir whole-building owner-capturable comparisons.
3. Manufacturing no puede pasar a comparabilidad area-based si falta throughput normalization.
4. Logistics no puede pasar a comparabilidad area-only si falta service-level normalization.
5. Correlaciones estructurales pueden priorizar investigación, pero no se convierten automáticamente en causalidad final.
6. Toda contradicción cross-layer relevante debe quedar explícita en `cross_layer_congruence_register` o `invalid_problem_frame_register`.

## invariants
- cada register principal debe tener su count plano sincronizado;
- `gap_taxonomy_register` extendido no puede perder items originales de `motor_049`;
- `rival_hypothesis_register`, `hypothesis_discrimination_register` y `claim_impact_register` deben preservarse;
- `comparison_blocker_register` y `comparison_not_yet_valid_register` deben existir cuando la comparabilidad falla.

## forbidden_operations
- permitir peers por simple similitud de asset class sin normalización;
- borrar riesgos o blockers para forzar benchmark;
- tratar correlación como prueba causal cerrada;
- usar este motor para emitir tesis ejecutiva, acción estratégica final o claim governor final;
- sobrescribir la taxonomía de gaps original en lugar de extenderla.
