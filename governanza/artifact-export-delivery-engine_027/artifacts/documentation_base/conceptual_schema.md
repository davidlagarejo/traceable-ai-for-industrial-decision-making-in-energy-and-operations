# Conceptual Schema — Artifact Export / Delivery Engine

Motor ID: motor_027

## entities
1. `ExportRequest`: solicitud determinista de entrega para uno o mas artefactos exportables.
2. `ExportableArtifact`: referencia a un artefacto upstream con metadatos suficientes para ser empaquetado.
3. `DestinationProfile`: declaracion del destino permitido y sus restricciones de formato, tamano y nombrado.
4. `DeliveryPolicy`: reglas aplicables al empaquetado, integridad, retencion, compresion y sobrescritura.
5. `DeliveryBundle`: resultado material de empaquetado preparado para entrega.
6. `DeliveryManifest`: inventario auditable que permite reconstruir el bundle.
7. `DeliveryReceipt`: registro final de estado de la operacion.

## relationships
Un `ExportRequest` referencia uno o muchos `ExportableArtifact`. Cada `ExportableArtifact` debe tener exactamente un productor upstream declarado y al menos un `lineage_ref`. Un `ExportRequest` usa exactamente un `DestinationProfile` y una `DeliveryPolicy` compatible. Un `DeliveryBundle` se crea desde un solo `ExportRequest` aprobado. Cada `DeliveryBundle` tiene exactamente un `DeliveryManifest` y uno o mas `DeliveryReceipt` si existen reintentos documentados.

## key_fields
`ExportRequest`: `request_id:string`, `destination_id:string`, `requested_formats:list[string]`, `delivery_mode:string`, `requested_at:datetime`.
`ExportableArtifact`: `artifact_id:string`, `artifact_type:string`, `format:string`, `path_or_uri:string`, `producer_motor_id:string`, `version:string`, `lineage_ref:string`, `exportable_status:string`.
`DestinationProfile`: `destination_id:string`, `destination_type:string`, `allowed_formats:list[string]`, `max_bundle_size_bytes:int`, `overwrite_policy:string`.
`DeliveryPolicy`: `policy_id:string`, `checksum_algorithm:string`, `compression:string`, `retention_rule:string`, `on_error:string`.
`DeliveryManifest`: `manifest_id:string`, `bundle_id:string`, `files:list[object]`, `created_at:datetime`, `manifest_hash:string`.
`DeliveryReceipt`: `delivery_id:string`, `request_id:string`, `status:string`, `warnings:list[string]`, `errors:list[string]`.
