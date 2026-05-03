# Acceptance Tests — Loss Pattern and Maintenance Reality Engine

Motor ID: motor_052

## happy_path
- Manufacturing sin fuentes locales de mantenimiento: aparecen `maintenance maturity not evidenced`, `reactive-maintenance risk plausible` y `downtime economics may dominate visible energy symptoms`.
- Manufacturing con maintenance sources: aparece `maintenance maturity partially evidenced`, existen `maintenance_proof_gap_register` y `downtime_dependency_register`.

## edge_cases
- La presencia parcial de fuentes de mantenimiento no debe transformarse en evidencia observada completa.
- La estrategia de medición debe seguir hipótesis reales de pérdida, leakage o power quality.

## rejection_criteria
- Falla si maintenance evidence parcial se traduce en juicio observacional fuerte.
- Falla si faltan proof gaps o downtime dependencies cuando la evidencia sigue incompleta.
- Falla si los counts planos no coinciden con los registers.
