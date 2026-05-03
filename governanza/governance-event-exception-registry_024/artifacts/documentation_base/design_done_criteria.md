# Design Done Criteria — Governance Event & Exception Registry

Motor ID: motor_024


## criteria
- `functional_contract.md` no contiene marcadores [PENDIENTE] y define inputs, outputs, limits y validations con al menos 5 inputs, 3 outputs y 7 límites explícitos.
- `conceptual_schema.md` no contiene marcadores [PENDIENTE] y define las 3 entidades principales (GovernanceEvent, ExceptionRecord, TensionSignal) con sus campos mínimos obligatorios y relaciones entre ellas.
- `operational_rules.md` no contiene marcadores [PENDIENTE] y enumera al menos 7 reglas operativas, invariantes explícitos y operaciones prohibidas.
- `acceptance_tests.md` no contiene marcadores [PENDIENTE] y cubre al menos un happy path completo, 3 edge cases y 4 criterios de rechazo con códigos de error específicos.
- `failure_modes.md` no contiene marcadores [PENDIENTE] y documenta al menos 5 modos de fallo con síntomas observables, 3 antipatrones y señales de degradación silenciosa.
- El motor nunca emite un GovernanceEvent sin `governance_event_id`, `lineage_id` y `produced_by_motor` presentes — verificable en tests de implementación.
- El motor rechaza correctamente eventos con `source_motor_id` vacío, `captured_at` inválido o `phase_contract_ref` denegado — verificable con tests de rechazo unitarios.
