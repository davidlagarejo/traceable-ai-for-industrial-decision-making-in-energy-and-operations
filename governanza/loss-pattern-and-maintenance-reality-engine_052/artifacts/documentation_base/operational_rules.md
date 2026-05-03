# Operational Rules — Loss Pattern and Maintenance Reality Engine

Motor ID: motor_052

## rules
1. La realidad de mantenimiento debe expresarse como estado bounded, no como juicio moral o causalidad final.
2. Ausencia de maintenance sources debe dejar la madurez como no evidenciada.
3. Presencia de maintenance sources puede subir a parcialmente evidenciada, no automáticamente a observada.
4. Downtime dependency y maintenance proof gaps deben aparecer cuando la evidencia sigue incompleta.
5. Hardware sólo puede activarse si la estrategia mínima de medición lo dispara.
6. Loss patterns activados siguen siendo hipótesis o patrones bounded hasta nueva evidencia.

## invariants
- todos los counts planos deben coincidir con sus registers;
- `maintenance_reality_register` debe incluir allowed/prohibited use;
- `measurement_strategy_register` debe explicar confirmación y falsación;
- `hardware_minimality_register` no puede contradecir `measurement_strategy_register`.

## forbidden_operations
- afirmar “poor maintenance” como hecho observado con evidencia parcial;
- pedir hardware por reflejo sin hipótesis;
- convertir power-quality o leakage hints en diagnóstico final;
- suprimir gaps o dependencias de downtime para limpiar el caso.
