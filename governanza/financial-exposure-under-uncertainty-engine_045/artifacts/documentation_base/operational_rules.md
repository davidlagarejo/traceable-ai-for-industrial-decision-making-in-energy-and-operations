# Operational Rules — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## sequencing
1. derivar el target definition operativo;
2. construir exposición financiera estructural desde variables, conflicto, framing y rediseño;
3. construir evidencia por capa usando abstracción, comparación y exposición resultante;
4. devolver sólo outputs financieros bounded.

## evidence_rules
- `allowed_financial_output` y `prohibited_financial_output` deben coexistir;
- `evidence_state_by_layer_register` debe conservar capas aunque algunas estén pobres;
- un caso financieramente prometedor no justifica endurecer `evidence_state`.

## domain_rules
- building: priorizar owner control, tenant-load split, compliance economics;
- manufacturing: priorizar throughput, process-duty, maintenance y downtime economics.

## boundary_rules
- no emitir ROI final;
- no emitir payback final;
- no abrir savings claim libre;
- no colapsar las 12 capas a un solo juicio financiero.
