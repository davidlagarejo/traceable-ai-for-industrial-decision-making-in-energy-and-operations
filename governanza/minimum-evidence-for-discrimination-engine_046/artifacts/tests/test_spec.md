# Test Spec — Minimum Evidence For Discrimination Engine

Motor ID: motor_046

## happy_path
- Building: pedir tenant metering map, topology y LL97 basis.
- Manufacturing: pedir throughput, bills, inventory y downtime logs.

## sparse_case
- con conflicto parcial, el motor puede seguir emitiendo evidencia mínima si todavía discrimina hipótesis reales.

## malformed_input
- sin framing o sin rediseño condicional, el motor no debe inventar una lista fuerte.

## edge_cases
- el paquete mínimo puede ser una sola fila si ya concentra el mayor valor de información;
- `source` debe seguir siendo accionable y no vago.

## pass_criteria
- filas con confirmación, falsificación y unlock
- evidencia mínima específica
- count sincronizado

## fail_criteria
- checklist genérica;
- rival hypotheses difusas;
- unlock vacío o decorativo.
