# Functional Contract — Artifact Export / Delivery Engine

Motor ID: motor_027

## inputs
1. `export_request`: objeto estructurado con `request_id`, `destination_id`, `delivery_mode`, `requested_formats`, `requested_at` y actor o proceso solicitante.
2. `artifact_set`: lista de artefactos producidos por motores upstream, cada uno con `artifact_id`, `artifact_type`, `format`, `path_or_uri`, `producer_motor_id`, `version`, `lineage_ref` y `exportable_status`.
3. `destination_profile`: configuracion declarativa del destino permitido, incluyendo tipo de destino, formatos aceptados, convencion de nombrado, limite de tamano y politica de sobrescritura.
4. `delivery_policy`: reglas deterministas de empaquetado, retencion, checksum requerido, compresion permitida y tratamiento de errores.

## outputs
1. `delivery_bundle`: paquete local o remoto con los artefactos exportados, manifest, checksums y estructura de directorios definida por la politica.
2. `delivery_manifest`: JSON o YAML serializable con inventario de archivos, hashes, tamanos, formatos, lineage, productor upstream y destino previsto.
3. `delivery_receipt`: registro estructurado con `delivery_id`, `request_id`, `status`, `created_at`, `destination_id`, archivos incluidos, errores bloqueantes y advertencias no bloqueantes.
4. `rejection_report`: error estructurado cuando la solicitud no puede procesarse por falta de metadatos, destino invalido, formato no permitido o inconsistencia de integridad.

## limits
El motor solo acepta artefactos ya generados y declarados como exportables. No acepta contenido bruto de investigacion, prompts, datasets sin provenance, rutas opacas sin identificador, formatos no declarados ni destinos no registrados. Nunca produce analisis nuevo, documentos renderizados desde cero, autorizaciones de acceso, cambios de version upstream ni correcciones silenciosas de archivos.

## validations
Antes de procesar valida identificadores unicos, existencia del artefacto, formato permitido, destino permitido, lineage presente, productor upstream declarado y politica compatible con el request. Antes de emitir valida que el manifest enumere todos los archivos, que cada checksum corresponda al contenido exportado, que no haya archivos extra fuera del manifest y que el receipt registre PASS, WARNING o FAIL con causa explicita.
