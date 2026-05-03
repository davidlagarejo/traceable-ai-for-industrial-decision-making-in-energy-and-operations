# Functional Contract — Search / Discovery Intelligence Layer

Motor ID: motor_028

## inputs
1. `source_registry_snapshot`: lista estructurada de fuentes registradas, con `source_id`, dominio, tipo, derechos, estado y cobertura declarada. Productor: motor_008.
2. `canonical_taxonomy_scope`: conjunto de terminos canonicos, aliases permitidos, dominios y boundaries semanticos relevantes para la busqueda. Productor: motor_003.
3. `refresh_intelligence_signals`: eventos de cambio, prioridad de recaptura, staleness y gaps derivados de fuentes conocidas. Productor: motor_009.
4. `discovery_request`: instruccion operativa con alcance tematico, jurisdiccion, periodo, idioma, prioridad, restricciones de acceso y motivo de busqueda. Fuente: orquestador o proceso humano autorizado.
5. `prior_discovery_log`: historial de candidatos ya propuestos, descartados o enviados a revision para evitar repeticion no justificada. Fuente: este motor o repositorio versionado.

## outputs
1. `discovery_plan`: objeto documental con alcance, consultas, filtros, fuentes semilla, taxonomia aplicada, restricciones y criterio de parada. Destino: ejecucion controlada de busqueda y auditoria.
2. `source_candidate_record`: registro por candidato con identificador estable, locator, titulo, publicador, tipo de fuente, dominio taxonomico, motivo de descubrimiento, metodo, timestamp y provenance. Consumidor: motor_008 para revision de registro y derechos.
3. `coverage_gap_record`: descripcion de hueco de cobertura observado, evidencia estructural que lo motiva y relacion con taxonomia o refresh signal. Consumidores: orquestador, motor_009 y planning operativo.
4. `discovery_run_manifest`: resumen versionado de una corrida, inputs usados, consultas ejecutadas, candidatos emitidos, candidatos rechazados y limitaciones observadas. Destino: lineage/versioning y auditoria.

## limits
El motor no acepta contenido raw de fuentes como input primario, credenciales sin politica de acceso, instrucciones sin alcance taxonomico, ni listas de urls sin provenance minimo. No produce registros finales de fuente, perfiles de derechos aprobados, datos ingeridos, datos normalizados, calidad de dataset, deduplicacion documental final ni claims analiticos. Todo candidato emitido queda marcado como `candidate_status=proposed` hasta que otro motor o revision autorizada lo promueva o rechace.

## validations
Antes de procesar, valida que cada input declare productor, version o timestamp, y que el alcance use terminos canonicos o aliases reconocidos por motor_003. Rechaza solicitudes sin motivo operativo, sin dominio taxonomico o con restricciones de acceso incompatibles con el perfil de derechos disponible. Antes de emitir output, valida que cada candidato tenga locator, titulo o identificador externo, publicador o fuente emisora cuando exista, razon de descubrimiento, consulta o metodo que lo encontro, timestamp, hash o identificador de corrida y referencia a los inputs usados. Si un candidato coincide con una fuente registrada o con un candidato previo, no lo reemite como nuevo; lo marca como posible duplicado o redescubrimiento con referencia al registro existente.
