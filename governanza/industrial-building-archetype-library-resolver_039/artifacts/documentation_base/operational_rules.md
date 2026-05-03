# Operational Rules — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## rules
1. Clasificar antes de modelar. Si el target llega como `CORPORATE_HEADQUARTERS`, `REGISTERED_AGENT_OR_MAILING_ADDRESS` o `AMBIGUOUS_TARGET`, el motor debe degradar a `target_not_yet_structurally_modelable` antes de evaluar cualquier clue adicional.
2. La especificidad del arquetipo debe estar bounded por señales observadas. Un arquetipo específico sólo puede activarse cuando la combinación de `target_type`, jurisdicción y hints públicos coincide con una regla explícita de la librería.
3. La prioridad de resolución debe respetar el orden codificado: no-operating/unresolved -> NYC tower bounded -> manufacturing laminate -> utility-heavy bounded -> NYC generic building -> fallback por `target_type` -> unresolved final.
4. Toda selección debe dejar rastro en `archetype_selection_basis_register`; no se permiten selecciones silenciosas sin base auditable.
5. `system_abstraction_seed` debe reflejar exactamente el `ArchetypeDefinition` elegido y presentarlo como estructura falsable, no como verdad cerrada.
6. El contrato anti-hallucination debe acompañar siempre la salida para restringir el uso del prior a estructuración de hipótesis, diseño de evidencia y motores estructurales posteriores.

## invariants
- `selected_archetype_id`, `selected_archetype_label`, `match_confidence` y `resolver_state` planos deben coincidir con `archetype_resolution`;
- `dominant_variable_count` debe ser exactamente el largo de `dominant_variable_hypotheses`;
- si el target no es modelable todavía, `dominant_variable_hypotheses` debe estar vacío y `selected_archetype_evidence_state` debe ser `INADMISSIBLE_CLAIM`;
- si el target sí recibe arquetipo, `selected_archetype_evidence_state` debe ser `ARCHETYPAL_PRIOR`, nunca `OBSERVED_FACT`;
- `archetype_minimum_evidence_register` debe provenir del arquetipo seleccionado y no de inputs inventados downstream;
- `selection_basis_register` debe estar compuesta por bases observadas como tipo, clasificación, jurisdicción o clues bounded, no por conclusión narrativa.

## forbidden_operations
- inventar un arquetipo nuevo fuera de `ARCHETYPE_LIBRARY`;
- promover una sede, mailing address u objetivo ambiguo a activo modelable sólo por nombre, prestigio o intuición;
- convertir `dominant_variable_hypotheses` en diagnóstico local confirmado del activo;
- emitir comparables, benchmark performance, ROI, CAPEX, savings claim o recomendación de rediseño final;
- usar fuentes aceptadas o datasets presentes como prueba automática de funcionamiento local sin pasar por la lógica bounded de selección;
- omitir el contrato anti-hallucination o degradar su severidad para facilitar cierre de reporte.
