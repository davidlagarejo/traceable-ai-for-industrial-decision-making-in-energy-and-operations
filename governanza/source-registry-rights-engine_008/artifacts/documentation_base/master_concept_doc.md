# Master Concept Document — Source Registry + Rights Engine

Motor ID: motor_008

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
why_it_exists:  Sin este motor no hay control serio de fuentes públicas, premium o restringidas.
key_inputs:     source declarations, license files, access agreements
key_outputs:    source_registration, rights_profile, access_class, refresh_schedule
key_objects:    SourceRecord, RightsProfile, AccessClass
what_not_to_do: No ingesta datos. No evalúa calidad. Solo registra metadatos de fuentes y derechos.
design_notes:   Depende de motor_001. Puede construirse temprano en paralelo con el pipeline de normalización.
-->

## purpose
El Source Registry + Rights Engine registra, normaliza a nivel documental y conserva los metadatos mínimos de fuentes externas e internas: identidad de fuente, licencia, restricciones de uso, clase de acceso, periodicidad esperada de refresh y usos permitidos. Su salida es un registro gobernado que permite saber si una fuente puede usarse, bajo qué condiciones y con qué cadencia debe revisarse. El motor no captura contenido de la fuente ni juzga su calidad; solo establece el estado administrativo y de derechos que condiciona su uso por otros motores.

## what_it_does
- Recibe declaraciones de fuente con identificador, nombre, propietario, localizador, tipo de fuente y finalidad de uso declarada.
- Recibe archivos o referencias de licencia y extrae sus metadatos estructurales mínimos: tipo de licencia, vigencia, permisos, restricciones y obligaciones de atribución.
- Recibe acuerdos de acceso y registra condiciones de autenticación, pago, contrato, cuota, embargo, uso interno o restricción territorial.
- Crea o actualiza un `SourceRecord` con identificador estable, provenance documental y estado registral.
- Crea un `RightsProfile` asociado a cada fuente con permisos, usos prohibidos, limitaciones temporales y referencias a documentos legales.
- Asigna una `AccessClass` determinista como `public`, `premium`, `restricted`, `contractual`, `internal` o `blocked`.
- Produce un `refresh_schedule` con periodicidad declarada, fecha de revisión siguiente y razón de la cadencia asignada.
- Emite errores estructurados cuando la declaración de fuente, la licencia o el acuerdo de acceso no permiten construir un perfil de derechos auditable.

## what_it_does_not_do
- No ingesta datos, no descarga contenido, no parsea datasets y no preserva raw source payloads; esa responsabilidad pertenece al motor de ingesta.
- No evalúa calidad, completitud, confiabilidad, fitness ni aptitud analítica de los datos; esa responsabilidad pertenece al motor de calidad.
- No normaliza entidades, valores de dominio ni registros extraídos de las fuentes; solo registra metadatos de fuente y derechos.
- No resuelve identidad de entidades descritas dentro de una fuente.
- No decide prioridades analíticas ni reemplaza los contratos de fase definidos por `motor_001`.
- No concede permisos reales fuera del sistema; solo registra el estado documental de permisos, restricciones y uso permitido.

## why_it_exists
Este motor existe como pieza separada porque el control de derechos y acceso es una obligación previa a la ingesta, la normalización y el uso analítico, pero no pertenece a ninguna de esas responsabilidades. Depende de `motor_001` para respetar límites de fase y puede construirse temprano en paralelo con el pipeline de normalización porque sus entradas son declaraciones y documentos administrativos, no datos procesados.
