# Failure Modes — Artifact Export / Delivery Engine

Motor ID: motor_027

## failure_modes_list
1. `manifest_drift`: el bundle contiene archivos que no aparecen en el manifest o el manifest lista archivos ausentes; sintoma observable: diferencia entre inventario y filesystem o destino.
2. `lineage_loss`: el receipt o manifest omite productor, version o lineage; sintoma observable: el bundle no puede reconstruirse desde artefactos upstream.
3. `unauthorized_destination`: una solicitud apunta a un destino no registrado o incompatible; sintoma observable: rechazo por politica antes de transferencia.
4. `integrity_failure`: checksum no coincide despues de empaquetar o transferir; sintoma observable: `DeliveryReceipt.status = FAIL` con error de integridad.
5. `silent_partial_delivery`: solo una parte del bundle llega al destino sin error estructurado; sintoma observable: conteo de archivos entregados menor que manifest sin rechazo explicito.

## anti_patterns
1. Usar el motor para renderizar o recomponer contenido, mezclando delivery con reporting.
2. Permitir destinos ad hoc definidos por texto libre sin perfil ni politica.
3. Exportar archivos sin checksums porque el canal parece confiable.
4. Rellenar metadatos ausentes por inferencia local para hacer pasar la validacion.

## degradation_signals
Senales de degradacion incluyen aumento de receipts con `WARNING`, diferencia frecuente entre manifest y archivos reales, entregas repetidas con resultados no equivalentes, artefactos sin productor upstream, crecimiento de excepciones manuales por destino y aparicion de archivos no inventariados en bundles. Cualquier senal debe bloquear cierre automatico hasta que se conserve trazabilidad completa.
