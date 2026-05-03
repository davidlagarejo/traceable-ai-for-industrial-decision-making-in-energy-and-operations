# Master Concept Document — Public Data Engine

Motor ID: motor_012

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Materializar Fase 1 y producir facility_prior y bundles contextuales listos para Fase 2.
why_it_exists:  Convierte infraestructura base en output útil de Fase 1.
key_inputs:     library_objects (motor_011), source_registry (motor_008), quality_records (motor_007)
key_outputs:    facility_prior, contextual_bundle, phase1_package
key_objects:    FacilityPrior, ContextualBundle, Phase1Package
what_not_to_do: No hace inferencias. No produce TADs. Solo empaqueta el prior de Fase 1.
design_notes:   Materialización final de Fase 1. Depende de toda la infraestructura base.

All placeholder markers have been replaced with concrete content.
-->

## purpose
Public Data Engine materializa el cierre operativo de Fase 1 convirtiendo objetos curados, registros de fuente y evaluaciones de calidad en un paquete determinista consumible por Fase 2. Su salida principal es el `facility_prior`, acompañado por `contextual_bundle` y `phase1_package` con referencias trazables a los insumos que los originan. El motor no interpreta evidencia ni deriva conclusiones; solo empaqueta y valida el prior de Fase 1 bajo contratos explícitos.

## what_it_does
- Recibe `library_objects` producidos por `motor_011` y verifica que estén curados, versionados y con provenance disponible.
- Recibe `source_registry` producido por `motor_008` y enlaza cada referencia de fuente usada por los objetos de biblioteca.
- Recibe `quality_records` producidos por `motor_007` y conserva sus evaluaciones como metadatos de aptitud, sin recalcularlas.
- Construye un `FacilityPrior` con el conjunto mínimo de conocimiento reutilizable autorizado para una facility o contexto operativo.
- Agrupa objetos, fuentes y evaluaciones en uno o más `ContextualBundle` listos para activación analítica posterior.
- Emite un `Phase1Package` que reúne el prior, los bundles, el snapshot de insumos y los metadatos de lineage necesarios para reconstruir el paquete.

## what_it_does_not_do
- No hace inferencias, no decide tensiones, no clasifica hallazgos y no produce conclusiones analíticas.
- No produce TADs, reportes finales, inference records ni salidas propias de Fase 2.
- No ingiere datos nuevos ni consulta fuentes externas; solo consume objetos ya generados por motores upstream.
- No evalúa ni recalcula calidad, fitness, duplicidad, derechos de uso o frescura de fuentes.
- No modifica silenciosamente objetos de biblioteca, registros de fuente ni quality records; cualquier rechazo debe ser explícito.

## why_it_exists
Existe como motor separado porque la materialización final de Fase 1 es una responsabilidad distinta de curar bibliotecas, registrar fuentes o evaluar calidad. Centraliza el handoff hacia Fase 2 en un paquete trazable y estable, evitando que motores downstream tengan que recomponer infraestructura base o asumir reglas implícitas de empaquetado.
