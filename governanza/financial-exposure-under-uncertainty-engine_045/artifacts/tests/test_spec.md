# Test Spec — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## happy_path
- Building: bloquear ROI/payback y savings claims fuertes bajo control boundary abierto.
- Manufacturing: traducir risk de CAPEX a carga de proceso, throughput y downtime.
- Layer matrix: emitir las 12 capas con evidencia y preguntas dominantes.

## sparse_case
- con soporte parcial, el motor puede seguir emitiendo screening bounded pero no economics cerrados.

## malformed_input
- sin framing o sin rediseño condicional, el motor no debe fabricar outputs financieros fuertes.

## edge_cases
- `regulation` puede estar observada aunque `finance` siga condicional;
- `control/responsibility` y `market/competitiveness` deben exponer preguntas abiertas reales.

## pass_criteria
- filas financieras con outputs permitidos y prohibidos
- 12 capas exactas en el register por layer
- counts sincronizados

## fail_criteria
- ROI o payback final;
- register por capas incompleto;
- riesgo estructural mal explicado.
