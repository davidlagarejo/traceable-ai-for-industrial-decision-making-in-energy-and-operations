# Test Spec — Fair Comparison and Congruence Engine

Motor ID: motor_051

## happy_path
- Building: aparece `whole_building_owner_capturable_comparison` y la normalización `owner_tenant_control_boundary`.
- Manufacturing: `area_based_energy_intensity_comparison` queda inválida sin `throughput by shift`.
- Logistics: `warehouse_area_only_comparison` queda inválida sin `service level`.
- Manufacturing: aparecen correlaciones `Inductive support systems + tariff context` y `Support-system complexity + maintenance dependency`.

## sparse_case
- Con bundle operativo parcial, el motor debe seguir emitiendo blockers, risks y comparaciones no válidas en vez de declarar comparabilidad limpia.

## malformed_input
- Si faltan process map o control boundaries, el motor no puede declarar peer validity fuerte.
- Si la taxonomía de gaps heredada está vacía, el motor puede extenderla, pero no debe fingir ausencia de riesgos.

## edge_cases
- Buildings deben producir invalid problem frames ligados a owner action cuando la frontera de control no está cerrada.
- Correlaciones pueden existir sin que la comparación sea todavía válida; no se deben colapsar ambos conceptos.

## pass_criteria
- Los registros principales preservan counts planos sincronizados.
- Buildings, manufacturing y logistics producen reglas distintas de comparabilidad.
- Risks, blockers y contradictions aparecen explícitamente cuando el caso lo requiere.

## fail_criteria
- Comparaciones inválidas marcadas como comparables.
- Ausencia de blockers o risks en casos con normalización faltante.
- Loss de lineage respecto a rival hypotheses, hypothesis discrimination o claim impacts.
