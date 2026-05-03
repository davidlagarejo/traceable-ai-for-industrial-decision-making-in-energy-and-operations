# Usage Example — Artifact Export / Delivery Engine

Motor ID: motor_027

## example
Un proceso de release solicita entregar dos artefactos ya generados por motores upstream hacia un destino local registrado para auditoria. El motor valida que ambos archivos existan, que sus formatos esten permitidos, que conserven productor, version y lineage, y prepara un bundle con manifest, checksums y receipt sin modificar el contenido original.

## inputs_used
`export_request`: `request_id="export_req_2026_04_18_001"`, `destination_id="audit_drop_local"`, `delivery_mode="local_bundle"`, `requested_formats=["pdf", "json"]`, `requested_at="2026-04-18T12:00:00Z"`, `actor="release_pipeline"`.

`artifact_set`: dos objetos exportables: `artifact_report_pdf` con `format="pdf"`, `path_or_uri="/tmp/zlab/report.pdf"`, `producer_motor_id="motor_017"`, `version="v1"`, `lineage_ref="lineage_report_001"`, `exportable_status="exportable"`; y `artifact_manifest_json` con `format="json"`, `path_or_uri="/tmp/zlab/report_manifest.json"`, `producer_motor_id="motor_016"`, `version="v1"`, `lineage_ref="lineage_manifest_001"`, `exportable_status="exportable"`.

`destination_profile`: `destination_id="audit_drop_local"`, `destination_type="local_bundle"`, `allowed_formats=["pdf", "json"]`, `naming_convention="{request_id}-{bundle_id}"`, `max_bundle_size_bytes=50000000`, `overwrite_policy="replace"`.

`delivery_policy`: `policy_id="delivery_policy_sha256_no_compression"`, `checksum_algorithm="sha256"`, `compression="none"`, `retention_rule="retain_90_days"`, `on_error="fail"`.

## expected_output
El resultado incluye `delivery_bundle` con `bundle_id`, `bundle_path`, `manifest_path`, `file_count=2`, `checksum_algorithm="sha256"` y `compression="none"`; `delivery_manifest` con dos entradas, una por artefacto, cada una con `artifact_id`, `relative_path`, `size_bytes`, `checksum`, `producer_motor_id`, `version` y `lineage_ref`; y `delivery_receipt` con `status="PASS"`, `request_id="export_req_2026_04_18_001"`, `destination_id="audit_drop_local"`, dos archivos incluidos, sin errores bloqueantes.

## notes
Los archivos referenciados deben existir antes de invocar el motor y deben representar artefactos ya cerrados por motores upstream. Si falta `lineage_ref`, el destino no coincide con el perfil, un formato no esta permitido, el bundle excede el limite de tamano o un checksum no coincide, el motor emite `DeliveryReceipt.status="FAIL"` y `rejection_report` en lugar de producir una entrega parcial silenciosa.
