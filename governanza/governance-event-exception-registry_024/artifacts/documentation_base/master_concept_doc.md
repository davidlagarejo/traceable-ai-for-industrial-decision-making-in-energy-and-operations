# Master Concept Document — Governance Event & Exception Registry

Motor ID: motor_024


## purpose
Motor motor_024 recibe señales de excepción, override y tensión provenientes de todos los motores del sistema y las registra como eventos de gobernanza trazables. Su función es convertir anomalías implícitas en registros explícitos, persistentes e inmutables, disponibles para revisión humana. No actúa sobre los datos ni modifica el comportamiento de ningún motor; solo captura y preserva la señal.

## what_it_does
- Recibe eventos de excepción emitidos por cualquier motor del sistema cuando una regla, contrato o invariante no se puede satisfacer.
- Recibe registros de override cuando un operador o proceso autorizado fuerza una decisión que viola una regla normal.
- Recibe señales de tensión cuando dos motores o políticas producen instrucciones contradictorias sin resolución automática.
- Valida que cada evento entrante incluya un identificador de fuente estable, un timestamp de captura y una referencia de lineage de motor_002.
- Emite un `GovernanceEvent` inmutable por cada señal aceptada, con metadatos de trazabilidad completos.
- Emite un `ExceptionRecord` cuando el evento corresponde a una excepción estructurada de un motor.
- Emite un `TensionSignal` cuando el evento refleja una contradicción entre políticas o motores.
- Persiste todos los objetos emitidos con version_id, produced_by_motor y lineage_id para reconstrucción completa.

## what_it_does_not_do
- No resuelve excepciones: registra la señal pero nunca aplica correcciones, fallbacks ni lógica compensatoria.
- No cambia políticas: la existencia de un evento de gobernanza no autoriza ni modifica ningún contrato, regla o configuración del sistema.
- No normaliza ni enriquece los datos del evento entrante: preserva el payload tal como llega, sin inferencias ni correcciones silenciosas.
- No evalúa si una excepción es grave o trivial: la clasificación de severidad corresponde a revisión humana o a un motor de evaluación downstream.
- No activa alertas ni notificaciones: su responsabilidad termina en el registro persistente; la observabilidad activa pertenece a otro motor.
- No agrega, consolida ni deduplica eventos: cada señal entrante produce su propio registro inmutable.

## why_it_exists
Sin un motor dedicado al registro de anomalías y tensiones, las excepciones del sistema quedan invisibles en logs difusos o en lógica distribuida sin trazabilidad. motor_024 existe como punto de captura explícito y separado para que la gobernanza opere sobre señales objetivas, registradas e inmutables, y no sobre intuiciones o efectos colaterales. Es un motor ligero que solo requiere los contratos de fase de motor_001 y el lineage de motor_002, sin dependencias adicionales.
