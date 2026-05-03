# Operational Rules — Global Public Data Routing Engine

Motor ID: motor_035

## rules
1. Clasificar antes de rutear. El motor no puede proponer fuentes si todavía no resolvió si el caso es un activo operativo enrutable o una superficie degradada.
2. La jurisdicción manda sobre el portal. Toda fuente propuesta debe ser compatible con la jurisdicción resuelta, no con preferencias genéricas del caso.
3. La lista `mandatory_sources` debe contener sólo fuentes cuyo valor sea estructural para bounded discovery del target actual.
4. Las sustituciones prohibidas deben declararse explícitamente cuando el sistema detecta riesgo de usar benchmarks o issuer context como reemplazo de evidencia local requerida.
5. Si `subject_gate_passed=false` o el target no es técnicamente enrutable, el motor debe degradar la ruta pública y recomendar una superficie de reporte más estrecha.
6. El motor debe preservar tanto el bundle estructurado completo como señales planas listas para consumo downstream.

## invariants
- no se inventan fuentes fuera del registry de routing público;
- una ruta no puede marcarse `routing_ready=true` si la clasificación efectiva bloquea scraping técnico;
- `mandatory_sources`, `high_priority_sources` y `optional_sources` deben ser mutuamente coherentes con `asset_type` y `jurisdiction_class`;
- el `report_type_switch_recommendation` no puede contradecir una prohibición upstream explícita;
- el motor no altera el caso; sólo publica un contrato de búsqueda pública y una consecuencia de reporte.

## forbidden_operations
- ejecutar requests, scrapers o llamadas a portales;
- usar heurísticas de HQ / mailing address para promover un caso a activo operativo sin soporte contractual;
- tratar benchmarking genérico como si sustituyera property record, permits o energía local cuando la ruta los exige;
- emitir facts del activo, claims económicos o diagnósticos técnicos;
- introducir overrides manuales silenciosos sobre la clasificación o la resolución jurisdiccional.
