# Operational Rules — Search / Discovery Intelligence Layer

Motor ID: motor_028

## rules
1. Toda busqueda debe partir de un `DiscoveryRequest` con alcance, motivo, prioridad y referencia taxonomica.
2. Todo plan debe registrar las versiones de source registry, taxonomia y refresh signals usadas.
3. Toda consulta o filtro generado debe quedar en el `DiscoveryRunManifest` con timestamp y relacion al plan.
4. Todo candidato debe emitirse como propuesta, nunca como fuente aprobada.
5. Todo candidato debe incluir provenance suficiente para reproducir como fue encontrado.
6. Todo hallazgo rechazado por duplicado, falta de locator, falta de relevancia o restriccion de acceso debe quedar registrado como rechazo estructurado.
7. Si el motor detecta una coincidencia con una fuente existente, debe enlazarla y emitir redescubrimiento o duplicado potencial, no crear identidad nueva.
8. Las restricciones de derechos conocidas limitan donde buscar y que candidatos proponer; no se infieren permisos ausentes.

## invariants
- Ningun output del motor cambia el estado de una fuente registrada.
- Ningun candidato pierde la relacion con solicitud, plan, corrida e inputs versionados.
- Los terminos usados en busqueda permanecen mapeados a taxonomia canonica o alias autorizado.
- Un `candidate_id` identifica un candidato concreto en una corrida y no se reutiliza para otro locator.
- Las corridas son auditables: mismo plan, mismas versiones de input y mismo adaptador deben reconstruir el conjunto de consultas ejecutadas.
- La ausencia de resultados es un output valido si queda registrada en el manifiesto.

## forbidden_operations
- Descargar datasets completos o persistir contenido raw como si fuera ingesta.
- Crear, aprobar o modificar `source_registration`, `rights_profile` o `access_class`.
- Normalizar records, resolver entidades, evaluar calidad o curar bibliotecas.
- Usar un LLM como autoridad para decidir relevancia final sin reglas, provenance y validaciones deterministas.
- Sobrescribir candidatos previos sin versionado o borrar rechazos porque ya no son convenientes.
- Emitir claims analiticos, rankings de valor cientifico o recomendaciones de uso final de una fuente.
