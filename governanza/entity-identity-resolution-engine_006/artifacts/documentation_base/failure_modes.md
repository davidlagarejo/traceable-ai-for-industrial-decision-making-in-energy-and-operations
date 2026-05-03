# Failure Modes — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.

Contenido completado para gate de documentation_base.
-->

## failure_modes_list
- FALSE_MERGE: registros de entidades distintas quedan en el mismo `entity_cluster`; se observa por conflictos posteriores de identificadores, taxonomia o provenance.
- FALSE_SPLIT: registros de la misma entidad quedan separados en clusters diferentes; se observa por repeticion estable de identificadores fuertes en clusters no conectados.
- AMBIGUITY_COLLAPSE: casos con evidencia insuficiente se emiten como `same_entity` o `distinct_entity`; se observa por baja tasa de `ambiguity_flag` frente a inputs con evidencia incompleta.
- PROVENANCE_LOSS: outputs carecen de `source_ref`, `provenance_ref` o `lineage_refs`; se observa por imposibilidad de reconstruir la decision.
- POLICY_DRIFT: decisiones equivalentes cambian sin cambio versionado de `resolution_policy`; se observa por resultados no reproducibles entre corridas.

## anti_patterns
- Tratar similitud de nombres como prueba suficiente de identidad sin identificadores, contexto taxonomico o evidencia adicional.
- Usar este motor para deduplicar documentos completos o reducir filas de dataset, invadiendo la responsabilidad de `motor_010`.
- Corregir silenciosamente aliases o identificadores durante la resolucion para que un merge parezca valido.
- Convertir todos los casos ambiguos en errores, perdiendo la salida valida que preserva incertidumbre.
- Permitir que una sugerencia generada por IA cierre identidad sin regla determinista y evidencia trazable.

## degradation_signals
- Aumento abrupto de `same_entity` sin aumento correspondiente de identificadores fuertes en evidencia.
- Descenso sostenido de `ambiguity_flag` en fuentes donde historicamente existen aliases incompletos o identificadores ausentes.
- Clusters con crecimiento anomalo de miembros sin `canonical_entity_id` estable o sin cambio versionado de politica.
- Reaparicion de los mismos `record_id` en multiples clusters confirmados.
- Alto volumen de `ResolutionConflict` con `conflict_type = taxonomy_mismatch`, lo que indica desalineacion entre normalizacion, taxonomia e identidad.
- Outputs sin `rule_version` o con referencias de evidencia vacias.
