# Operational Rules — Entity Identity / Resolution Engine

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

## rules
1. Todo registro evaluado debe provenir de `normalized_records` y conservar `record_id`, `source_ref` y `provenance_ref` en la salida.
2. Toda comparacion contra identidad debe usar entidades canonicas o clusters existentes con identificador estable; no se permite comparar contra texto libre no normalizado.
3. Una decision `same_entity` solo puede emitirse cuando los identificadores o features compatibles superan el umbral determinista de la `resolution_policy` vigente.
4. Una decision `distinct_entity` debe emitirse cuando hay conflicto de clase taxonomica, identificador incompatible o regla determinista de separacion.
5. Una decision `ambiguous` debe emitirse cuando existe evidencia insuficiente, empate entre candidatos o conflicto no resoluble sin revision.
6. Cada output debe incluir la version de reglas aplicada y referencias a evidencia o lineage suficientes para reconstruir la decision.
7. Las resoluciones previas pueden informar la comparacion, pero no pueden cerrar automaticamente una decision nueva si el input actual contradice la evidencia historica.

## invariants
- Ningun `record_id` de entrada se elimina, se reemplaza o se sobrescribe durante la resolucion.
- Todo `identity_resolution_record` referencia al menos un `record_id` evaluado y una version de reglas.
- Todo `entity_cluster` contiene una lista explicita de miembros; no existen miembros implicitos por posicion o orden de archivo.
- Todo caso ambiguo permanece representado como output valido y trazable, no como ausencia silenciosa de decision.
- `provenance_ref` y `lineage_refs` se preservan en cada decision, conflicto o cluster emitido.
- Una entidad canonica usada como referencia nunca es modificada por este motor.

## forbidden_operations
- Detectar duplicados documentales, fusionar documentos o reducir inflacion de dataset; eso pertenece a `motor_010`.
- Normalizar valores crudos, corregir nombres, inferir campos faltantes o reescribir atributos de origen.
- Crear, renombrar o retirar entidades canonicas como autoridad global.
- Forzar merges cuando la decision correcta es `ambiguous`.
- Ocultar conflictos de identidad para producir un cluster aparentemente limpio.
- Eliminar registros de entrada por baja confianza o por pertenecer a un cluster ambiguo.
- Usar un resultado de IA no trazable como decision final de identidad.
