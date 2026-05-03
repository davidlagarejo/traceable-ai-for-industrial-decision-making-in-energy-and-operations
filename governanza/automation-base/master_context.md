# Master Context

## 1. Propósito general del proyecto

### Confirmado
Este proyecto busca convertir el framework ZLab en una arquitectura de software implementable, trazable y escalable, sin perder la disciplina epistemológica ya definida en las fases del framework.

El objetivo inmediato no es construir una aplicación final ni una interfaz. El objetivo es congelar el contexto útil del proyecto para poder automatizar después el diseño e implementación de motores con Claude, Codex u otra herramienta, reduciendo improvisación, retrabajo y ambigüedad.

### Inferido con alta confianza
La intención operativa es pasar de metodología cerrada a infraestructura real de software, de forma modular y con contratos explícitos.

### Pendiente o ambiguo
No está definido todavía el repositorio final, formato exacto de carpetas ni pipeline completo de automatización.

---

## 2. Qué se está construyendo realmente

### Confirmado
Se está construyendo una arquitectura de **motores de software** para soportar todo el framework ZLab.

Estos motores no son las fases. Son componentes de software que materializan capacidades necesarias para que el framework opere con:
- contratos claros,
- trazabilidad,
- versionado,
- taxonomía controlada,
- ingesta disciplinada,
- normalización,
- resolución de identidad,
- evaluación de calidad,
- curación,
- inferencia,
- reporting,
- verificación,
- y gobernanza.

También se está construyendo una base documental para que cada motor pueda luego implementarse en código sin rediseñar la arquitectura en cada paso.

### Inferido con alta confianza
La construcción real se está enfocando primero en la columna vertebral de datos y gobernanza, antes de entrar en motores más downstream como reporting final o verification bridge operativo.

### Pendiente o ambiguo
No está cerrada todavía la lista final completa de todos los motores ni su nivel exacto de madurez para MVP versus fases posteriores.

---

## 3. Qué significa “motor” dentro del proyecto

### Confirmado
Un motor es una **capacidad de software separada**, con responsabilidad concreta, límites claros, inputs definidos, outputs definidos, contratos explícitos y posibilidad de crecimiento sin contaminar al resto del sistema.

Un motor:
- no equivale a una fase;
- no debe redefinir la fase que sirve;
- puede servir a una o varias fases;
- debe poder documentarse, testearse, versionarse y evaluarse por separado.

### Inferido con alta confianza
El motor debe existir como unidad de arquitectura real, no como etiqueta conceptual vaga ni como módulo que “hace de todo”.

### Pendiente o ambiguo
No está totalmente fijado si algunos motores se fusionarán temporalmente en el MVP por motivos prácticos, aunque la preferencia explícita ha sido evitar fusiones peligrosas.

---

## 4. Objetivo de los motores dentro del framework

### Confirmado
Los motores existen para materializar el framework sin romper su constitución epistemológica.

Su objetivo es:
- implementar funciones transversales y operativas;
- preservar trazabilidad y lineage;
- evitar mezcla de responsabilidades;
- soportar handoffs entre fases;
- preparar outputs utilizables por fases posteriores;
- y permitir que el sistema escale sin convertirse en un conjunto caótico de scripts.

### Inferido con alta confianza
Los motores son la capa que vuelve implementable el framework de manera disciplinada, de modo que los outputs visibles o analíticos no dependan de improvisación.

### Pendiente o ambiguo
No está definida todavía una taxonomía final de prioridad entre todos los motores más allá de los primeros motores fundacionales ya discutidos.

---

## 5. Principios técnicos ya definidos

### Confirmado
Los principios técnicos ya definidos son los siguientes:

1. **Las fases y los motores no son lo mismo.**  
   Las fases definen autoridad, límites epistemológicos, outputs permitidos y handoffs. Los motores implementan capacidades.

2. **La prioridad del MVP no es capturar todo.**  
   La prioridad es separar responsabilidades, preservar metadatos correctos y evitar retrabajo futuro.

3. **Cada motor debe tener límites duros.**  
   Debe quedar claro qué hace, qué no hace, qué entra y qué sale.

4. **Cada motor debe documentarse antes de codificarse.**  
   Antes del código, cada motor debe tener documentación base mínima.

5. **La arquitectura debe ser deterministic-first.**  
   El LLM no puede sustituir contratos, trazabilidad, versionado, taxonomía ni lógica estructural.

6. **Todo debe ser trazable y reconstruible.**  
   Deben preservarse provenance, lineage, versionado y posibilidad de rebuild.

7. **No silent mutation.**  
   No se deben corregir datos, contratos, taxonomías o outputs silenciosamente.

8. **No monolitos.**  
   Los motores no deben crecer como módulos gigantes que mezclan responsabilidades.

9. **Escalabilidad desde el inicio, sin sobre-ingeniería ornamental.**  
   Cada motor debe nacer con estructura suficiente para crecer sin rehacerse, pero sin complejidad gratuita.

10. **Secuencia de trabajo por motor.**  
    Para cada motor, el flujo correcto es:
    - documentación base,
    - schema técnico,
    - tests,
    - failure modes,
    - implementación,
    - revisión de conformidad.

### Inferido con alta confianza
Existe una preferencia fuerte por modularidad, tipado claro, interfaces explícitas, errores estructurados y tests como parte central del diseño.

### Pendiente o ambiguo
No está fijado todavía un stack técnico definitivo único para toda la implementación.

---

## 6. Principios epistemológicos ya definidos

### Confirmado
Se han reafirmado como base del proyecto estos principios:

1. Ningún modelo único es soberano.  
2. La verdad emerge de acuerdo restringido entre capas.  
3. El sistema restringe hipótesis más de lo que sabe.  
4. El LLM no es soberano; solo participa downstream y subordinado.  
5. Benchmark no es evidencia local.  
6. El output no puede exceder el soporte real.  
7. La incertidumbre material debe preservarse.  
8. El conflicto material no debe borrarse narrativamente.  
9. Decision-grade y Verification-grade son distintos.  
10. Las fases cerradas no deben reabrirse silenciosamente.

También quedó claro que:
- los motores no pueden redefinir la epistemología;
- no pueden cambiar reglas base por intuición;
- no pueden convertir una excepción local en cambio global sin gobernanza;
- y no pueden usar narrativa como sustituto de soporte real.

### Inferido con alta confianza
Toda la arquitectura de motores debe estar subordinada a Fase 0 y al corpus metodológico ya cerrado.

### Pendiente o ambiguo
No está consolidado todavía en este archivo el detalle fino de cada ley por subfase o por objeto, solo la base general ya repetida de forma consistente.

---

## 7. Límites actuales del proyecto

### Confirmado
Los límites actuales del proyecto son los siguientes:

- no se está construyendo todavía UI;
- no se está construyendo todavía producto final;
- no se está construyendo todavía marketing;
- no se está construyendo todavía un chatbot;
- no se está construyendo todavía una solución genérica de “data lake + dashboard”;
- no se está permitiendo que los motores improvisen razonamiento libre;
- no se está autorizando a los motores a redefinir fases ni epistemología.

Además:
- el foco actual está en diseño documental y arquitectónico;
- el código debe venir después;
- y la automatización posterior con Claude, Codex u otra herramienta debe apoyarse en archivos base congelados.

### Inferido con alta confianza
El objetivo inmediato es consolidar contexto y luego usarlo como base para generar archivos, prompts y código con menos riesgo.

### Pendiente o ambiguo
No está definido todavía el momento exacto en el que se pasará de documentación a implementación efectiva de cada motor.

---

## 8. Qué decisiones ya están cerradas

### Confirmado
Estas decisiones ya están cerradas o se han repetido con suficiente consistencia como para tratarlas como base estable:

1. **Se está diseñando una arquitectura de motores, no de fases nuevas.**
2. **Las fases no equivalen 1:1 a motores.**
3. **La documentación base precede al código.**
4. **Cada motor debe tener contrato, objetos mínimos, tests y failure modes antes de implementarse.**
5. **El LLM es auxiliar y subordinado.**
6. **La trazabilidad, versionado y lineage son obligatorios desde el inicio.**
7. **La separación de responsabilidades es ley de diseño.**
8. **La prioridad del MVP es orden estructural, no captura total.**
9. **Los primeros motores fundacionales ya priorizados son:**
   - Phase Contract Registry
   - Versioning + Lineage Engine
   - Taxonomy + Canonical Entity Service
   - Ingestion + Parsing Engine
   - Canonical Normalization Engine
   - Entity Identity / Resolution Engine
   - Quality / Fitness Evaluation Engine
10. **Existen motores posteriores ya previstos, aunque no cerrados del todo, como:**
    - Library Curation Engine
    - Decision Core / Inference Engine
    - Output Block Composition Engine
    - Report Package Assembly Engine
    - LaTeX Report Compilation Engine
    - Verification Bridge Engine
    - Propagation / Re-evaluation Engine
    - Evaluation / Conformance Engine

### Inferido con alta confianza
También está bastante asentado que el orden de construcción empieza por gobernanza, contratos, trazabilidad, semántica y captura disciplinada antes de motores downstream.

### Pendiente o ambiguo
No está completamente cerrada la lista final y definitiva de todos los motores ni su agrupación final para MVP.

---

## 9. Qué sigue abierto o ambiguo

### Confirmado
Lo que sigue abierto o ambiguo debe tratarse como no cerrado:

- lista final definitiva de todos los motores;
- posibles fusiones temporales de algunos motores en el MVP;
- stack técnico exacto de implementación;
- repositorio y estructura final de archivos;
- automatización exacta con Codex, Claude u otra herramienta;
- orden final detallado después del motor 7;
- especificación final de todos los archivos base necesarios.

### Inferido con alta confianza
También siguen abiertos:
- el detalle completo de motores de reporting downstream;
- la forma exacta del motor de evaluación/conformance;
- y el nivel de granularidad de algunos objetos internos de motores todavía no documentados.

### Pendiente o ambiguo
No se puede afirmar todavía que el otro chat “Construcción de Motores” haya dejado cerrados todos los motores uno por uno. Esa integración no debe darse por concluida sin revisión específica.

---

## 10. Riesgos de interpretación que deben evitarse

### Confirmado
Estos riesgos deben evitarse explícitamente:

1. **Confundir fases con motores.**
2. **Asumir que ya existe una lista final cerrada de motores cuando todavía hay partes abiertas.**
3. **Asumir que un motor puede redefinir la metodología.**
4. **Saltar a código sin documentación base.**
5. **Usar IA como sustituto de arquitectura explícita.**
6. **Mezclar captura, normalización, identidad, curación, reporting o gobernanza en el mismo motor.**
7. **Pensar que más datos equivale a mejor sistema.**
8. **Confundir calidad estructural con verdad epistemológica final.**
9. **Suponer que benchmarks o contexto público equivalen a verificación de sitio.**
10. **Convertir prompts de implementación en espacios de rediseño.**
11. **Rellenar huecos con intuiciones no confirmadas.**
12. **Tomar deseos futuros como decisiones ya tomadas.**

### Inferido con alta confianza
También debe evitarse tratar la lista de prompts ya generados como si fuera equivalente a una arquitectura completamente congelada. Los prompts ayudan, pero el estado de cierre depende de la documentación real consolidada.

### Pendiente o ambiguo
No está claro todavía qué partes del contexto del otro chat requerirán revalidación manual antes de pasarse a archivos ejecutables o a automatización masiva.
