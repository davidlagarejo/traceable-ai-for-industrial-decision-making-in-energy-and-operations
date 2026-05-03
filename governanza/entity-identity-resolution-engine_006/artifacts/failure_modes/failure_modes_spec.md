# Failure Modes Spec — Entity Identity / Resolution Engine

Motor ID: motor_006

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Resolver cuándo distintos registros apuntan a la misma entidad y cuándo la ambigüedad debe quedar abierta.
why_it_exists:  Evita merges erróneos, duplicación de entidades y pérdida de comparabilidad.
key_inputs:     normalized_records, canonical_entities (motor_003)
key_outputs:    identity_resolution_record, entity_cluster, ambiguity_flag
key_objects:    IdentityRecord, EntityCluster, ResolutionConflict
what_not_to_do: No detecta duplicados documentales. Eso es motor_010. Solo resuelve identidad de entidades.
design_notes:   Puede dejar ambigüedad abierta — esto es correcto. No fuerza resolución cuando no hay certeza. Depende de motor_005 y motor_003.

Contenido completado para gate de failure_modes.
-->

## failure_modes_list
- FM-006-001_missing_provenance: `normalized_records` contiene un item sin `source_ref`, `provenance_ref` o `lineage_refs` reconstruibles → el motor no puede explicar de donde salio una decision de identidad, y los outputs quedan inutiles para auditoria downstream → rechazar el lote con error estructurado `ERR_MISSING_PROVENANCE`, no emitir clusters parciales y registrar el `record_id` afectado para correccion upstream.
- FM-006-002_taxonomy_mismatch_merge: un `NormalizedRecord.entity_type` se compara o agrupa con un `CanonicalEntity.entity_type` incompatible → se observa un `identity_resolution_record.decision = "same_entity"` o un `entity_cluster.cluster_status = "confirmed"` que une clases taxonomicas distintas → bloquear el merge, emitir `distinct_entity` o `ResolutionConflict.conflict_type = "taxonomy_mismatch"` con evidencia taxonomica, y conservar el caso fuera de clusters confirmados.
- FM-006-003_candidate_tie_forced_resolution: dos o mas candidatos tienen evidencia compatible bajo la misma `resolution_policy.rule_version` y ninguna regla determinista rompe el empate → se emite una decision cerrada sin `ambiguity_flag`, ocultando que la identidad sigue abierta → emitir `identity_resolution_record.decision = "ambiguous"`, `confidence_band = "unresolved"` y `ambiguity_flag.ambiguity_reason = "candidate_tie"`.
- FM-006-004_identifier_collision: registros o candidatos comparten alias normalizado pero tienen identificadores externos fuertes incompatibles, como `org_tax_id` divergente para organizaciones → el cluster confirmado mezcla entidades distintas o el record de identidad no cita la evidencia contradictoria → emitir `distinct_entity` o `ResolutionConflict.conflict_type = "identifier_collision"`, adjuntar `evidence_refs` de cada identificador incompatible y excluir esos miembros de cualquier cluster confirmado.
- FM-006-005_policy_version_loss: `resolution_policy.rule_version` falta, esta vacio o no se copia a `IdentityRecord` y `CandidateMatch` → decisiones equivalentes no pueden compararse entre corridas y no es posible reconstruir que reglas cerraron la identidad → rechazar con `ERR_POLICY_VERSION_MISSING` antes de evaluar candidatos, o invalidar la decision emitida si falta en el output.
- FM-006-006_silent_input_mutation: el motor corrige nombres, reescribe `normalized_fields`, completa campos ausentes o modifica `canonical_entities` para facilitar el match → los outputs parecen consistentes pero pierden comparabilidad con los inputs autorizados de `motor_005` y `motor_003` → tratar cualquier mutacion de entrada como violacion material, fallar la corrida y conservar los objetos originales sin cambios.
- FM-006-007_partial_output_after_contract_error: un input malformado produce algunos `identity_resolution_record` o `entity_cluster` antes del rechazo del lote → consumidores downstream reciben una mezcla de objetos validos y decisiones no auditables → validar contrato completo antes de emitir salidas persistibles, devolver un unico error estructurado y dejar la coleccion de outputs vacia.

## anti_patterns
- Acoplar la decision de identidad a un ranking probabilistico opaco sin `rule_version`, `evidence_refs` y umbrales deterministas reproducibles.
- Usar un resultado de IA, similitud semantica libre o explicacion textual como autoridad final de merge sin convertirlo en evidencia subordinada y trazable.
- Mezclar normalizacion de texto crudo dentro de `motor_006`; los inputs deben llegar ya normalizados desde `motor_005`.
- Crear, renombrar o retirar `CanonicalEntity` como salida de este motor; la autoridad canonica pertenece a `motor_003`.
- Implementar deduplicacion documental, conteo de documentos unicos o correccion de inflacion de dataset; ese limite pertenece a `motor_010`.
- Forzar una decision binaria cuando la salida correcta es `ambiguous` con `AmbiguityFlag`.
- Construir clusters por posicion de archivo, orden de llegada o estado global mutable en lugar de listas explicitas de `record_id`, `identity_record_id` y evidencia.
- Ocultar conflictos dentro de un cluster aparentemente limpio en vez de emitir `ResolutionConflict` o degradar el cluster a estado ambiguo.
- Mutar decisiones previas sin `parent_id`, `version_id` y `version_hash`; una correccion debe crear nueva version trazable.
- Aceptar registros sin `record_id`, `source_ref`, `provenance_ref` o `normalized_fields` y rellenarlos silenciosamente.

## degradation_signals
- Aumento sostenido de `ambiguity_flag.severity = "blocking"` para una misma fuente o tipo de entidad por encima del rango historico de la politica vigente.
- Incremento de `ResolutionConflict.conflict_type = "taxonomy_mismatch"` despues de cambios en taxonomia, aliases canonicos o normalizacion upstream.
- Proporcion creciente de `identity_resolution_record` sin `evidence_refs` multiples cuando la politica exige evidencia compuesta para `same_entity`.
- Aparicion en logs de rechazos `ERR_POLICY_VERSION_MISSING`, `ERR_MISSING_PROVENANCE` o `ERR_UNNORMALIZED_INPUT` para fuentes que antes pasaban validacion.
- Clusters con `member_record_ids` vacio, miembros duplicados o miembros no presentes en `evaluated_record_ids` de sus `IdentityRecord`.
- Diferencias no explicadas en `version_hash` para la misma combinacion de `record_id`, `candidate_ref` y `rule_version`.
- Crecimiento anomalo de clusters `confirmed` con muchos miembros y poca diversidad de `source_ref`, senal de merge agresivo por alias superficial.
- Decisiones `same_entity` emitidas sin `CandidateMatch.match_result = "pass"` asociado.
- Caida abrupta de `confidence_band = "high"` junto con aumento de `candidate_tie`, senal de que las reglas ya no discriminan candidatos.
- Logs o metricas que muestran escrituras sobre objetos de entrada `NormalizedRecord` o `CanonicalEntity` durante la resolucion.

## expensive_errors
- Merge falso entre entidades distintas: es caro porque contamina clusters, metricas longitudinales y cualquier analisis downstream que asume identidad estable. Se previene bloqueando `same_entity` ante identificadores incompatibles, taxonomia divergente o evidencia insuficiente, y prefiriendo `AmbiguityFlag` cuando no hay certeza determinista.
- Perdida de provenance o lineage en una decision: es caro porque no se puede reconstruir por que un registro entro en un cluster ni revertir con precision una decision mala. Se previene haciendo obligatorios `source_ref`, `provenance_ref`, `lineage_refs`, `evidence_refs`, `rule_version`, `version_id` y `version_hash` antes de emitir outputs.
- Decision cerrada sin `rule_version`: es caro porque una misma identidad puede cambiar bajo reglas nuevas y no hay forma de comparar corridas o explicar regresiones. Se previene validando `resolution_policy.rule_version` al inicio y copiandolo en cada `IdentityRecord` y `CandidateMatch`.
- Mutacion silenciosa de `normalized_records` o `canonical_entities`: es caro porque desplaza responsabilidades hacia este motor y rompe la autoridad de `motor_005` y `motor_003`. Se previene tratando inputs como inmutables, comparando snapshots antes y despues de la corrida y fallando cualquier intento de escritura.
- Creacion de entidad canonica global desde un cluster local: es caro porque convierte una salida provisional en autoridad upstream y obliga a reconciliar catalogos canonicos a posteriori. Se previene limitando este motor a `identity_resolution_record`, `entity_cluster`, `ambiguity_flag` y `resolution_conflict`, con `canonical_entity_id` solo como referencia externa.
- Output parcial despues de error de contrato: es caro porque consumidores downstream pueden persistir decisiones incompletas antes de ver el fallo. Se previene con validacion de lote previa a emision y con una politica de no producir clusters parciales cuando existe error estructural de input.
- Conflicto oculto por limpieza cosmetica del cluster: es caro porque el sistema aparenta certeza y las revisiones posteriores no encuentran el punto donde se perdio la ambigüedad. Se previene emitiendo `ResolutionConflict` con `blocking_reason`, `recommended_next_step` y referencias a los `CandidateMatch` incompatibles.
