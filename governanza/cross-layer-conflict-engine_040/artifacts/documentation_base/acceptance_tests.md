# Acceptance Tests — Cross-Layer Conflict Engine

Motor ID: motor_040

## happy_path
- Caso building: aparecen `Regulation vs control boundary` y `Finance assumes owner-capturable savings before control is proven`.
- Caso manufacturing: aparecen `Energy-savings framing vs unresolved process load` y `Maintenance and uptime economics may dominate visible energy symptoms`.

## edge_cases
- Caso logistics sin conflictos estructurales directos: el motor debe traducir el conflicto desde `motor_051`.

## rejection_criteria
- Falla si un conflicto estructural esperable no aparece.
- Falla si el fallback desde `motor_051` pierde `evidence_state`.
- Falla si `cross_layer_conflict_count` no coincide con el register.
