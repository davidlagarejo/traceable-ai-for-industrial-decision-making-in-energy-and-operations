# Acceptance Tests — Artifact Export / Delivery Engine

Motor ID: motor_027

## happy_path
Input: un `ExportRequest` con dos artefactos exportables, ambos con ruta existente, formato permitido, productor upstream, version y lineage; un `DestinationProfile` que acepta esos formatos; y una `DeliveryPolicy` que exige SHA-256. Accion: el motor valida la solicitud, prepara el bundle, genera manifest, calcula checksums y emite receipt. Output esperado: `DeliveryBundle` creado, `DeliveryManifest` con dos entradas y hashes validos, `DeliveryReceipt.status = PASS` sin errores bloqueantes.

## edge_cases
1. Request con lista minima de un solo artefacto exportable: debe producir bundle, manifest y receipt sin asumir que siempre hay multiples archivos.
2. Request con artefactos grandes pero dentro del limite del destino: debe validar tamano agregado, conservar checksums y no cambiar politica de compresion.
3. Request repetido con el mismo contenido, destino y politica: debe producir manifest logicamente equivalente o receipt de idempotencia, segun la politica de sobrescritura.
4. Artefacto valido con advertencia no bloqueante de formato legado permitido: debe emitir `WARNING` si la politica lo permite y conservar trazabilidad.

## rejection_criteria
1. Rechazar con `missing_lineage` si cualquier artefacto no declara `lineage_ref` o `producer_motor_id`.
2. Rechazar con `destination_not_allowed` si el destino no existe en perfiles permitidos.
3. Rechazar con `format_not_allowed` si un artefacto no coincide con `allowed_formats`.
4. Rechazar con `checksum_mismatch` si el contenido empaquetado no coincide con el hash calculado o registrado.
