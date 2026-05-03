# Operational Rules — Problem Framing Engine

Motor ID: motor_041

## sequencing
1. leer target definition para ubicar la familia del caso;
2. consumir abstracción, variables dominantes y conflictos;
3. intentar framing estructural directo;
4. si el framing directo queda vacío, inadmisible o demasiado genérico, traducir el invalid frame desde `motor_051`;
5. emitir sólo problemas reformulados que downstream pueda usar como disciplina, no como decisión.

## evidence_rules
- si el conflicto fuente es condicional, el problema reformulado también debe quedar bounded;
- si el fallback de congruencia es la única base disponible, debe preservarse `linked_layers`;
- `evidence_needed` no se colapsa a una frase genérica tipo “more data needed”.

## domain_rules
- building: priorizar control boundary, tenant-load separation y presión regulatoria;
- manufacturing: priorizar process-duty, throughput, downtime y maintenance dependence;
- logistics: priorizar comparabilidad justa y variable operacional correcta.

## boundary_rules
- no recomendar rediseño ni CAPEX;
- no producir peer comparison;
- no convertir “wrong framing” en “root cause proven”;
- no borrar el problema original para que la auditoría posterior no pierda el hilo.
