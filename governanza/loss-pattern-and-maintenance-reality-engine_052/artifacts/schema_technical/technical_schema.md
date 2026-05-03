# Technical Schema — Loss Pattern and Maintenance Reality Engine

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
- `PowerQualityHypothesisRecord`
- `LeakageHypothesisRecord`

## fields
- `MaintenanceRealityRecord`
  `reality_claim: str (required)`
  `maintenance_state: str (required)`
  `evidence_state: str (required)`
  `why_it_matters: str (required)`
  `allowed_use: str (required)`
  `prohibited_use: str (required)`
- `MeasurementStrategyRecord`
  `hypothesis: str (required)`
  `minimum_measurement: str (required)`
  `why: str (required)`
  `if_confirmed: str (required)`
  `if_falsified: str (required)`
  `hardware_trigger: str (required)`
- aggregate surfaces
  `loss_pattern_hypothesis_register: list[dict] (required)`
  `activated_pattern_register: list[dict] (required)`
  `pattern_discrimination_register: list[dict] (required)`
  `industrial_common_sense_register: list[dict] (required)`
  `maintenance_reality_register: list[MaintenanceRealityRecord] (required)`
  `maintenance_proof_gap_register: list[dict] (required)`
  `downtime_dependency_register: list[dict] (required)`
  `measurement_strategy_register: list[MeasurementStrategyRecord] (required)`
  `hardware_minimality_register: list[dict] (required)`
  `power_quality_hypothesis_register: list[dict] (required)`
  `leakage_hypothesis_register: list[dict] (required)`

## relationships
- loss-pattern hypotheses drive activation and discrimination registers;
- maintenance dependencies drive maintenance reality, proof gaps and downtime;
- maintenance reality, loss, power quality and leakage feed measurement strategy;
- measurement strategy feeds hardware minimality.

## identifiers
- Identificador natural de `MaintenanceRealityRecord`: `reality_claim`.
- Identificador natural de `MeasurementStrategyRecord`: `hypothesis`.
- Identificador natural de cada aggregate register: target bounded del caso.

## versioning
- cambios en maintenance sources, subsystems o peer requirements alteran la versión lógica de los registers;
- counts planos deben regenerarse con cada versión.

## lineage
- lineage principal desde `motor_049`, `motor_050` y `motor_051`;
- `maintenance_reality_register` traza a intake pack y maintenance dependency map;
- `measurement_strategy_register` traza a loss, maintenance, power quality y leakage hypotheses.
