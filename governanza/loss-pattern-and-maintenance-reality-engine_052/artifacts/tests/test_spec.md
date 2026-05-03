# Test Spec — Loss Pattern and Maintenance Reality Engine

Motor ID: motor_052

## happy_path
- Manufacturing sin maintenance sources: `maintenance maturity not evidenced` y downtime risk explícita.
- Manufacturing con maintenance sources: `maintenance maturity partially evidenced`, proof gaps y downtime dependencies presentes.

## sparse_case
- Con evidence parcial, el motor debe emitir hipótesis bounded y estrategia mínima de medición, no silencio.

## malformed_input
- Si faltan subsystems o maintenance dependencies, el motor no debe inventar mantenimiento observado.

## edge_cases
- Evidence parcial no puede subir a observada plena.
- Hardware minimality debe seguir a measurement strategy, no adelantarse.

## pass_criteria
- Los claims de maintenance reality son coherentes con la evidencia disponible.
- Los counts planos coinciden con sus registers.
- Existen proof gaps y downtime dependencies cuando corresponde.

## fail_criteria
- Mantenimiento parcialmente evidenciado tratado como observado fuerte.
- Registers críticos vacíos en casos que requieren discriminación.
- Count desincronizado.
