# Conceptual Schema — Loss Pattern and Maintenance Reality Engine

Motor ID: motor_052

## entities
- `LossPatternHypothesisRecord`
- `ActivatedPatternRecord`
- `PatternDiscriminationRecord`
- `MaintenanceRealityRecord`
- `MaintenanceProofGapRecord`
- `DowntimeDependencyRecord`
- `MeasurementStrategyRecord`
- `HardwareMinimalityRecord`

## relationships
- family research + intake pack + subsystems + dynamic intake + peer requirements → loss patterns
- family research + intake pack + maintenance dependencies → maintenance reality
- loss, maintenance, power quality y leakage → measurement strategy
- measurement strategy → hardware minimality

## key_fields
- `MaintenanceRealityRecord`: `reality_claim`, `maintenance_state`, `evidence_state`, `why_it_matters`, `allowed_use`, `prohibited_use`
- `MeasurementStrategyRecord`: `hypothesis`, `minimum_measurement`, `why`, `if_confirmed`, `if_falsified`, `hardware_trigger`
- los demás registers conservan forma estructurada de hipótesis, activación, discriminación o gap.
