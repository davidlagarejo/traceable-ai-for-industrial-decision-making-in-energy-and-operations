# Acceptance Tests — Search / Discovery Intelligence Layer

Motor ID: motor_028

## happy_path
Entrada: un `DiscoveryRequest` para encontrar fuentes regulatorias nuevas sobre un dominio canonico, un snapshot de motor_008 con fuentes ya registradas, una taxonomia de motor_003 con aliases permitidos y senales de motor_009 indicando stale coverage en dos jurisdicciones. Accion esperada: el motor construye un `DiscoveryPlan`, ejecuta o registra consultas reproducibles, descarta resultados ya registrados y emite `SourceCandidateRecord` para hallazgos nuevos. Output correcto: cada candidato tiene locator, titulo, dominio taxonomico, razon de descubrimiento, timestamp, referencia a la consulta y estado `proposed`; el `DiscoveryRunManifest` lista inputs versionados, consultas, candidatos y rechazos.

## edge_cases
1. No hay resultados nuevos: el motor emite un manifiesto con cero candidatos, registra las consultas ejecutadas y conserva el `CoverageGapRecord` sin fabricar candidatos.
2. Resultado coincide con fuente existente: el motor no crea una fuente nueva; emite rechazo o redescubrimiento con referencia al `source_id` existente.
3. Taxonomia contiene aliases multiples para el mismo termino: el plan registra el termino canonico y los aliases usados, evitando consultas que creen dominios paralelos.
4. Fuente candidata tiene titulo y locator pero derechos desconocidos: el candidato puede emitirse como `proposed` solo si queda marcado para revision por motor_008 y no se declara apto para uso.

## rejection_criteria
1. Rechazar `DiscoveryRequest` sin scope taxonomico canonico, motivo operativo o prioridad declarada.
2. Rechazar inputs sin version, timestamp o productor identificable cuando sean necesarios para lineage.
3. Rechazar hallazgos sin locator estable o sin metodo de descubrimiento registrable.
4. Rechazar solicitudes que pidan descargar, parsear o evaluar datasets como parte de este motor.
5. Rechazar instrucciones que ordenen ignorar restricciones de derechos o promover candidatos como fuentes aprobadas.
