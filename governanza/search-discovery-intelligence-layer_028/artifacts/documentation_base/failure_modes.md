# Failure Modes — Search / Discovery Intelligence Layer

Motor ID: motor_028

## failure_modes_list
1. Drift de busqueda: las consultas se separan de la taxonomia canonica. Sintoma observable: candidatos con terminos no mapeados o dominios paralelos no aprobados.
2. Duplicacion de fuentes: el motor repropone fuentes ya registradas como si fueran nuevas. Sintoma observable: candidatos con locator o publisher coincidente sin referencia a `source_id` existente.
3. Perdida de provenance: candidatos sin consulta, timestamp, input versions o razon de descubrimiento. Sintoma observable: no se puede reconstruir por que aparecio el candidato.
4. Expansion de alcance: el motor empieza a ingerir, evaluar calidad o aprobar derechos. Sintoma observable: outputs con registros finales o contenido raw persistido.
5. Busqueda sesgada por historial: solo explora dominios ya conocidos aunque existan gaps. Sintoma observable: baja diversidad de publishers, jurisdicciones o tipos de fuente frente al scope pedido.

## anti_patterns
1. Usar listas manuales de links sin `DiscoveryRequest`, plan, taxonomia ni manifest de corrida.
2. Tratar un candidato como fuente admitida antes de que motor_008 revise derechos y registro.
3. Mezclar descubrimiento con ingestion para ahorrar pasos operativos.
4. Usar resultados de motores de busqueda externos sin conservar consulta, filtros, fecha y criterio de seleccion.
5. Rellenar huecos con inferencias narrativas sobre lo que deberia existir, en vez de registrar busquedas reproducibles y resultados observados.

## degradation_signals
- Porcentaje creciente de candidatos sin publisher, sin locator estable o sin motivo de descubrimiento.
- Repeticion alta de candidatos ya rechazados o ya registrados.
- Corridas con muchas consultas no versionadas o no asociadas a plan.
- Disminucion sostenida de cobertura nueva pese a gaps abiertos de alta prioridad.
- Uso frecuente de terminos fuera de taxonomia canonica.
- Candidatos emitidos sin restricciones de acceso conocidas o sin marca para revision de derechos.
