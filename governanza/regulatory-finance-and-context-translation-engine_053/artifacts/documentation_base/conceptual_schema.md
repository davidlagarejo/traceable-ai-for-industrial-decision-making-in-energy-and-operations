# Conceptual Schema — Regulatory, Finance and Context Translation Engine

Motor ID: motor_053

## entities
- `RegulatoryPhysicsRecord`
- `FinancePhysicsDependencyRecord`
- `FinancialExposureTypeRecord`
- `ContextRegisterRecord`
- `CapitalLogicRecord`

## relationships
- target definition + sources + family profile -> `RegulatoryPhysicsRecord`, `PermitSignalRecord`, `ClimateLocationContextRecord`
- fair comparison + maintenance reality + measurement strategy -> `FinancePhysicsDependencyRecord`
- finance-physics dependencies + constraints -> `CapitalLogicRecord`, `FinancialExposureTypeRecord`
- exposure types -> `UnderwritingMisreadRecord`, `ValueLeakageRecord`
- intake + local source context -> tariff and culture proxy registers

## key_fields
- `RegulatoryPhysicsRecord`: `regulatory_signal`, `physical_implication`, `evidence_state`, `what_it_supports`, `what_it_does_not_support`
- `FinancePhysicsDependencyRecord`: `financial_assumption`, `physical_dependency`, `evidence_state`, `risk_if_wrong`, `evidence_needed`
- `CapitalLogicRecord`: `capital_logic`, `current_admissibility`, `why`, `minimum_evidence_before_capex`
- `FinancialExposureTypeRecord`: `financial_exposure_type`, `trigger`, `why_it_matters`, `evidence_needed`, `tad_consequence`
- `ContextRegisterRecord`: climate, tariff y culture proxies con `allowed_use` y `prohibited_use`

## invariants
- ninguna asunción financiera puede existir sin dependencia física asociada;
- los context registers deben decir explícitamente para qué sirven y para qué no;
- la traducción regulatoria puede soportar screening o constraint, pero no sustituir medición física;
- `underwriting_misread_register` y `value_leakage_register` nacen de exposure types, no de intuición editorial;
- counts y registers deben permanecer alineados aunque algunos registers queden vacíos en ciertos casos.
