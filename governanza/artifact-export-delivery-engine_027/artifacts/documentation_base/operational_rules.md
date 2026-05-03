# Operational Rules — Artifact Export / Delivery Engine

Motor ID: motor_027

## rules
1. Procesar solo solicitudes con `ExportRequest`, `DestinationProfile` y `DeliveryPolicy` validos.
2. Tratar el contenido de artefactos upstream como inmutable durante la exportacion.
3. Incluir todo archivo entregado en el `DeliveryManifest`; ningun archivo fuera del manifest puede formar parte del bundle.
4. Calcular checksums despues de preparar el bundle y antes de emitir el receipt.
5. Registrar resultado estructurado para toda solicitud: `PASS`, `WARNING` o `FAIL`.
6. Mantener separadas las advertencias recuperables de los errores bloqueantes.

## invariants
El `artifact_id`, `producer_motor_id`, `version` y `lineage_ref` de cada artefacto no cambian por pasar por este motor. El numero de artefactos incluidos en el bundle debe coincidir con el numero de entradas aceptadas, salvo rechazos registrados explicitamente. Todo `DeliveryReceipt` debe poder enlazarse a un `ExportRequest` y a un `DeliveryManifest`. Una entrega repetida con la misma entrada, politica y destino debe producir la misma estructura logica de manifest.

## forbidden_operations
Esta prohibido editar contenido, regenerar documentos, cambiar versiones upstream, inferir metadatos ausentes, enviar a destinos no registrados, ignorar fallos de checksum, sobrescribir bundles sin politica explicita, mezclar artefactos de requests distintos sin nuevo manifest y convertir un fallo de validacion en entrega parcial silenciosa.
