# Design Done Criteria — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## criteria
- Los casos de `CORPORATE_HEADQUARTERS`, `REGISTERED_AGENT_OR_MAILING_ADDRESS` y `AMBIGUOUS_TARGET` siempre degradan a `target_not_yet_structurally_modelable` con `dominant_variable_count=0`.
- Las rutas específicas probadas en runtime seleccionan correctamente `commercial_office_tower_nyc`, `manufacturing_laminate` y `utility_heavy_site_generic` sólo cuando existen señales bounded coherentes con la librería.
- Los fallbacks genéricos para `warehouse_distribution` y `cold_chain_facility` quedan disponibles con `match_confidence=medium` cuando no existe soporte suficiente para una selección más estrecha.
- `system_abstraction_seed`, `archetype_minimum_evidence_register` y `anti_hallucination_contract` quedan alineados con el `ArchetypeDefinition` elegido y no contradicen `archetype_resolution`.
- El output final conserva tanto el bundle estructurado completo como las señales planas `selected_archetype_id`, `selected_archetype_label`, `match_confidence`, `resolver_state` y `dominant_variable_count`.
