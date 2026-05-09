# Fase 1 — Motor de Datos Publicos

> Nota canonica de gobernanza: este documento pertenece a una linea de trabajo anterior del framework. El documento constitucional autoritativo para la arquitectura integrada de 8 fases es `Phases/phase-0/docs/en/0_Phase_0_Master_Document.md`. Si este documento entra en conflicto con Fase 0 en numeracion, autoridad de fase, claims permitidos, techos semanticos o logica de boundaries, Fase 0 gobierna hasta que esta fase sea reconstituida formalmente.

## 1. Proposito de la Fase 1

La Fase 1 establece la capa de observacion publica del framework. Su funcion es construir la base externa estructurada minima necesaria para soportar inferencia restringida posterior sin conceder soberania epistemica a una sola fuente, benchmark, dataset, score o narrativa producida por un LLM.

La Fase 1 no es un motor de diagnostico. No es un motor de verificacion. No es un motor de recomendacion de alto peso operativo. Su proposito es mas estrecho y fundacional: organizar restricciones publicas, benchmarks, priors, arquetipos, senales de aplicabilidad regulatoria y relaciones contextuales dentro de un sustrato trazable capaz de soportar un primer `facility_prior` bajo limites de Decision-grade.

Su entregable esperado es una capa de datos publicos curada, versionada, joinable, semanticamente disciplinada y estructuralmente apta para uso posterior.

## 2. Rol de la Fase 1 Dentro del Framework Completo

La Fase 1 pertenece a la base inferencial previa a evidencia especifica de sitio. Se ubica despues de la capa constitucional establecida en Fase 0 y antes de cualquier regimen analitico, de modelado o de verificacion mas fuerte que dependa de evidencia mas profunda de la instalacion, modelado formal, analisis fisico o medicion.

Su rol es responder una clase restringida de preguntas:

- que estructura contextual publica es relevante para la instalacion candidata;
- que benchmarks publicos y priors sectoriales restringen plausiblemente la interpretacion;
- que condiciones jurisdiccionales y regulatorias son materialmente aplicables;
- que arquetipos son candidatos para comparacion disciplinada;
- que supuestos previos pueden introducirse provisionalmente con limites explicitos;
- y que incertidumbre sigue siendo irreductible en esta etapa.

La Fase 1 no responde:

- que esta ocurriendo realmente en el sitio;
- que mecanismo esta causando el desempeno observado;
- que ahorro verificado existe;
- que intervencion merece recomendacion de alto peso;
- o si algun claim ya alcanzo suficiencia de Verification-grade.

## 3. Dependencia Explicita de Fase 0

La Fase 1 esta estrictamente subordinada a Fase 0 — Operational Truth and Epistemic Governance. Hereda sin reinterpretacion:

- las leyes no negociables del framework;
- la distincion critica entre soporte analitico estructurado y formulacion gobernada;
- las reglas de proporcionalidad semantica;
- la separacion entre Decision-grade y Verification-grade;
- la primacia de la trazabilidad;
- la gobernanza de claims, outputs y artifacts mediante admisibilidad;
- y la tesis de que el LLM no es soberano.

En consecuencia, la Fase 1 debe leerse bajo las siguientes leyes heredadas:

1. No single model is trusted with truth.
2. Truth emerges from constrained agreement across independent layers.
3. Operational truth emerges from constrained multilayer inference, not from a single source, a single score, or a single narrative.
4. The system restricts hypotheses more than it knows.
5. The LLM is not sovereign.

El LLM solo puede participar en Fase 1 como capa semantica gobernada para formulacion, estructuracion, traduccion, resumen y verificacion semantica de material previamente acotado. No puede operar como motor analitico principal de la fase. La ingesta publica, el mapeo canonico, el computo de benchmarks, la aplicabilidad de reglas, la logica de joins y el output estructurado versionado deben permanecer anclados en mecanismos deterministas, inspeccionables y trazables.

## 4. Objetivo de Salida de la Fase 1

El objetivo de salida de la Fase 1 es un motor de datos publicos acotado capaz de producir un primer `facility_prior` con limites explicitos a partir de input escaso de la instalacion.

Los entregables esperados son:

- un data lake publico curado;
- un esquema maestro organizado por instalacion, jurisdiccion, sector, familia de benchmark y conjunto de reglas aplicables;
- join keys estables y versionado de datasets;
- un repositorio de benchmarks, priors y bundles contextuales publicos;
- y un objeto `facility_prior` restringido y apto para uso posterior.

La Decision de salida de la Fase 1 no es que el sistema ya "conozca" la instalacion. La Decision de salida es que, con aproximadamente diez inputs materialmente relevantes del usuario, el sistema pueda construir un prior publico trazable, acotado y de Decision-grade suficiente para restringir el trabajo posterior.

## 5. 1A — Delimitacion epistemologica y funcional del Public Data Engine

### 5.1 Funcion de la Subfase 1A

La Subfase 1A cierra el perimetro epistemologico y funcional del Public Data Engine. Define que tipos de observacion publica, benchmark, restriccion, regla, arquetipo y metadata contextual pueden entrar en la Fase 1 para generar un `facility_prior` Decision-grade, trazable y explicitamente no verificatorio.

La Subfase 1A no construye todavia el data lake completo, las tablas fisicas ni los pipelines productivos de ingesta. Su funcion es previa y restrictiva. Existe para impedir dataset sprawl, sobreafirmacion semantica, migracion silenciosa de lenguaje de Verification-grade hacia una capa de Decision-grade e impedir que el LLM se convierta en el centro analitico primario de la fase.

Su criterio rector no es riqueza documental. Su criterio rector es utilidad restrictiva bajo gobernanza epistemica.

### 5.2 Estatus de la Fase 1 Bajo la Jerarquia de Gobernanza

La Fase 1 pertenece, como maximo, a Decision-grade. Puede producir estructura contextual materialmente util, pero no puede presentar ningun output de Fase 1 como si ya hubiera cruzado el umbral de verificacion, confirmacion especifica de sitio o recomendacion de alto peso.

Todo output material de la Fase 1 debe ser:

- estructurado;
- trazable a fuente y version;
- semanticamente proporcional a la base de evidencia realmente disponible;
- acotado en dominio y uso pretendido;
- y marcado explicitamente como no verificatorio.

### 5.3 Regla de Alcance

Solo pueden entrar en la Fase 1 aquellas fuentes publicas, benchmarks, reglas, relaciones, arquetipos y objetos contextuales que restrinjan materialmente hipotesis y mejoren de forma disciplinada la construccion del `facility_prior`.

Nada entra en la Fase 1 por:

- disponibilidad;
- prestigio;
- volumen;
- apariencia tecnica;
- facilidad de scraping;
- facilidad de lectura por parte del LLM;
- o simple proximidad tematica con el dominio industrial.

La admision depende de funcion analitica, no de abundancia documental.

### 5.4 Producto Positivo de la Fase 1

La Fase 1 solo puede producir:

- contexto publico estructurado;
- arquetipos candidatos;
- benchmark bundles;
- jurisdiction bundles;
- regulatory flags;
- supuestos previos;
- uncertainty markers;
- objetos contextuales join-ready;
- y un `facility_prior` acotado.

Estos outputs pueden disciplinar trabajo posterior. No pueden cerrarlo.

### 5.5 Lo Que la Fase 1 No Puede Producir

La Fase 1 no puede producir:

- closed causal claims;
- verified performance claims;
- site-specific savings claims;
- high-weight recommendation claims;
- verification result claims;
- ni diagnosticos fuertes presentados como resueltos operativamente.

La Fase 1 puede indicar que una instalacion se parece a un arquetipo, cae bajo un regimen jurisdiccional o es compatible con una familia de benchmarks. No puede afirmar que la instalacion ya fue explicada analiticamente, verificada o ranqueada para intervencion con alta confianza.

### 5.6 Familias de Claim Permitidas en la Fase 1

Las siguientes familias de claim son admisibles en Fase 1, sujetas a trazabilidad y proporcionalidad:

- `contextual_public_claim`
- `benchmark_claim`
- `regulatory_applicability_claim`
- `archetype_candidate_claim`
- `prior_assumption_claim`
- `exploratory_structural_claim`

### 5.7 Familias de Claim Prohibidas en la Fase 1

Las siguientes familias de claim son inadmisibles en Fase 1:

- `verified_performance_claim`
- `closed_causal_claim`
- `site_specific_savings_claim`
- `high_weight_recommendation_claim`
- `verification_result_claim`

Estas quedan prohibidas porque su peso semantico excede la estructura de soporte que la Fase 1 esta autorizada a poseer.

### 5.8 Gates Binarios Minimos de Admisibilidad

Ninguna fuente, dataset, familia de benchmarks, bundle regulatorio u objeto contextual puede entrar en la Fase 1 si no pasa todos los gates binarios minimos:

- restrictive utility;
- canonical mapping;
- traceable origin;
- Decision-grade proportionality;
- non-LLM dependence;
- downstream role;
- y sprawl resistance.

### 5.9 Regla Anti-Sprawl

La Fase 1 no debe optimizar acumulacion de datos publicos. Debe optimizar densidad restrictiva por objeto admitido.

Cualquier dataset, familia de benchmarks, clase de fuente o repositorio contextual que incremente almacenamiento, ingesta, mantenimiento o superficie semantica sin mejorar materialmente la construccion acotada del prior debe quedar excluido.

La postura por defecto frente a nuevos datos publicos es rechazo hasta justificacion.

### 5.10 Interfaz de la Subfase 1A con el Resto de la Fase 1

La Subfase 1A define el perimetro de admisibilidad para toda ingesta, diseno de esquemas, curacion de benchmarks, logica de mapeo y construccion de priors dentro de la Fase 1. Ninguna subfase posterior puede ampliar ese perimetro de forma silenciosa.

## 6. 1B — Taxonomia y politica de admision de fuentes publicas

### 6.1 Funcion de la Subfase 1B

La Subfase 1B define que familias de fuentes publicas vale la pena integrar en el MVP de la Fase 1, que objetos canonicos puede alimentar cada familia, en que orden de prioridad debe entrar cada una, que riesgos epistemologicos introduce y donde conviene buscar primero para implementar el nucleo del Public Data Engine.

Su regla central es estricta:

En Fase 1 no se integran fuentes por ser "buenas", prestigiosas, numerosas o tecnicamente impresionantes. Se integran solo si pueden alimentar objetos canonicos del `facility_prior` con utilidad restrictiva real.

La Subfase 1B no reabre el perimetro epistemologico definido en 1A. Lo vuelve operativo mediante politica de admision, orden de implementacion y criterios de rechazo para el MVP.

### 6.2 Principio de admision

Toda familia de fuente debe justificar su entrada mediante:

- contribucion explicita a uno o mas objetos canonicos del `facility_prior`;
- utilidad restrictiva medible sobre el espacio de hipotesis;
- fuerza semantica acotada y compatible con Decision-grade;
- origen trazable y reproducible;
- y valor marginal claro frente a la complejidad que introduce.

Ninguna familia de fuente publica entra en el MVP solo porque pueda scrapearse, leerse con un LLM o agregarse a un corpus amplio.

### 6.3 Familias prioritarias para el MVP

El nucleo del MVP del Public Data Engine debe construirse sobre cinco familias prioritarias.

#### 6.3.1 Geografia y clima

Esta familia entra porque restringe el contexto operativo climatico, la comparabilidad y la estructura base del prior sin pretender verificacion de sitio.

Sus funciones restrictivas principales son:

- delimitar contexto de heating y cooling;
- acotar presion energetica estacional plausible;
- asignar climate zone y comparabilidad meteorologica;
- restringir interpretacion de arquetipos candidatos;
- e informar supuestos energeticos iniciales.

Variables tipicas incluyen:

- climate zone;
- HDD y CDD;
- normales de temperatura;
- contexto de humedad;
- rango estacional;
- y descriptores climaticos locales.

Ejemplos tipicos de instalacion incluyen:

- oficinas cuyo perfil HVAC depende fuertemente del balance HDD/CDD;
- retail alimentario o instalaciones refrigeradas donde el clima modifica la interpretacion de carga;
- escuelas u hospitales donde los supuestos de ocupacion deben leerse bajo contexto estacional local;
- e instalaciones industriales livianas donde el clima acota parcialmente cargas de servicios del edificio.

Objetos canonicos alimentados por esta familia:

- `climate_energy_context_bundle`
- `candidate_archetype_bundle`
- `facility_prior`

First-stop references:

- NOAA / NCEI Climate Normals
- publicaciones oficiales de degree days

Patrones de busqueda indicativos:

- `official climate normals HDD CDD site:ncei.noaa.gov`
- `NOAA daily climate normals degree days official`

Riesgos epistemologicos principales:

- falsa precision al tratar promedios climaticos como comportamiento real del sitio;
- mala asignacion geografica por join keys debiles;
- e inflacion semantica desde "clima normal" hacia "explicacion de carga real".

#### 6.3.2 Benchmarks sectoriales y tipologicos

Esta familia entra porque provee rangos plausibles, clases de comparacion tipologica y estructura de usos finales acotada para instalaciones candidatas sin colapsar en verificacion de desempeno.

Sus funciones restrictivas principales son:

- acotar rangos plausibles de consumo;
- seleccionar arquetipos candidatos;
- adjuntar estructuras tipicas de uso final;
- y definir prior assumptions para contraste posterior.

Variables tipicas incluyen:

- tipo de edificio;
- subsector manufacturero;
- intensidad energetica normalizada;
- shares de end use;
- contexto de fuel split;
- y perfiles por arquetipo.

Ejemplos tipicos de instalacion incluyen:

- office, school, hospital, warehouse, hotel y retail;
- arquetipos manufactureros como food processing, fabricated metals, chemicals, pulp and paper o plastics;
- e instalaciones mixtas donde la propia ambiguedad del benchmark debe entrar como uncertainty marker.

Objetos canonicos alimentados:

- `benchmark_bundle`
- `candidate_archetype_bundle`
- `prior_assumptions_pack`

First-stop references:

- EIA CBECS
- EIA MECS

Patrones de busqueda indicativos:

- `EIA CBECS building type end use official`
- `EIA MECS manufacturing end use official`

Riesgos epistemologicos principales:

- falsa comparabilidad entre instalaciones no equivalentes;
- uso de benchmark fuera de frontera metodologica;
- y sobreclaim desde promedios sectoriales hacia desempeno especifico de sitio.

#### 6.3.3 Jurisdiccion y regulacion de primer orden

Esta familia entra porque restringe que obligaciones, thresholds, regimens de reporte o condiciones de cumplimiento pueden aplicar plausiblemente antes de que exista verificacion de sitio.

Sus funciones restrictivas principales son:

- identificar aplicabilidad jurisdiccional de primer orden;
- adjuntar benchmarking, disclosure o performance flags;
- surfacing de thresholds materiales;
- y restringir que debe verificarse mas adelante.

Variables tipicas incluyen:

- ciudad, estado, provincia o pais;
- requerimientos de building benchmarking;
- energy performance standard applicability;
- disclosure thresholds;
- emisiones o reporting triggers;
- y flags de clasificacion regulada.

Ejemplos tipicos de instalacion incluyen:

- edificios comerciales en ciudades con benchmarking laws;
- instalaciones industriales bajo thresholds de emisiones o reporte;
- campus o portfolios bajo energy performance standards;
- y activos cuya localizacion modifica la plausibilidad de obligaciones regulatorias.

Objetos canonicos alimentados:

- `jurisdiction_bundle`
- `regulatory_flag_bundle`
- `facility_prior`

Patrones de busqueda indicativos:

- `official building energy benchmarking law [city/state]`
- `official energy performance standard [jurisdiction]`

Riesgos epistemologicos principales:

- mala clasificacion jurisdiccional;
- importacion de texto legal sin disciplina de aplicabilidad;
- y conversion de flag preliminar en conclusion legal implicita.

#### 6.3.4 Contexto energetico regional y factores de emision

Esta familia entra porque restringe el entorno energetico publico externo en el que opera la instalacion candidata, incluyendo grid mix, factores de emision publicos, contexto regional de precios y disponibilidad de combustibles.

Sus funciones restrictivas principales son:

- acotar contexto regional de emisiones;
- contextualizar supuestos de electricidad y combustibles;
- restringir interpretacion comparativa por region de red;
- e informar supuestos previos sobre carbono y entorno energetico.

Variables tipicas incluyen:

- subregion eGRID;
- factores publicos de emision electrica;
- contexto regional de precios energeticos;
- disponibilidad de combustibles;
- y descriptores de mezcla de red.

Ejemplos tipicos de instalacion incluyen:

- instalaciones intensivas en electricidad cuyo contexto de carbono depende de la region;
- arquetipos dependientes de gas donde el entorno regional cambia la plausibilidad del prior;
- y portfolios multiestado que requieren priors sensibles a region.

Objetos canonicos alimentados:

- `climate_energy_context_bundle`
- `benchmark_bundle`
- `facility_prior`

First-stop references:

- EPA eGRID
- EPA GHG Emission Factors Hub
- EIA energy prices

Patrones de busqueda indicativos:

- `EPA eGRID subregion emissions official`
- `EPA GHG emission factors hub official`

Riesgos epistemologicos principales:

- confundir factores regionales publicos con emisiones verificadas del sitio;
- sobreinterpretar senales de precio como certeza operativa;
- e importar factores sin control temporal o geografico.

#### 6.3.5 Bibliotecas tecnicas estructurales

Esta familia entra porque aporta taxonomias estructurales disciplinadas de sistemas, familias de end use, familias de oportunidad y logica de inputs faltantes que pueden restringir la construccion del `facility_prior` sin reclamar diagnostico verificado.

Sus funciones restrictivas principales son:

- organizar familias de sistema y categorias de uso final;
- restringir familias plausibles de oportunidad;
- definir que inputs faltantes importan;
- y mejorar prior assumptions para escalamiento posterior.

Variables tipicas incluyen:

- steam, motors, refrigeration, compressed air, lighting y automation;
- descomposicion tipica de end use;
- requisitos de perfil de proyecto;
- requisitos de baseline;
- y categorias de gestion operacional relevantes para etapas posteriores.

Ejemplos tipicos de instalacion incluyen:

- una planta de alimentos cuyo prior estructural debe distinguir steam, refrigeration, motors y process thermal loads;
- un edificio comercial cuya estructura probable depende de HVAC, lighting, controls y domestic hot water;
- y un campus donde la taxonomia de sistemas importa antes de admitir cualquier causalidad.

Objetos canonicos alimentados:

- `prior_assumptions_pack`
- `candidate_archetype_bundle`
- `benchmark_bundle`

First-stop references:

- AChEE
- DOE sector guides
- LBNL sector guides
- guias publicas de steam, motors, refrigeration, lighting y automation

La guia AChEE es una referencia valida dentro del corpus del usuario porque exige project profile, energy background, energy balance, baseline, end uses, areas of interest, OMEE y economic valuation. Su valor en Fase 1 no consiste en verificar nada, sino en explicitar que componentes estructurales deben existir antes de que otras fases puedan fortalecer claims.

Riesgos epistemologicos principales:

- tratar guias tecnicas como si fueran evidencia de sitio;
- importar familias de oportunidad como si fueran recomendaciones;
- y permitir que la riqueza narrativa exceda la utilidad restrictiva.

### 6.4 Fuentes utiles pero secundarias

Las siguientes familias pueden entrar despues de estabilizar el nucleo del MVP:

- datasets publicos de benchmarking municipal y disclosure;
- proxies operativos publicos;
- y casos publicos o case studies con frontera metodologica clara.

Son secundarias porque pueden enriquecer el prior, pero no son necesarias para estabilizar el primer `facility_prior`.

### 6.5 Fuentes interesantes pero no necesarias para el MVP

Las siguientes familias quedan fuera del MVP salvo necesidad especifica:

- tarifas utility exhaustivas;
- capas detalladas de mercados de carbono;
- contextos de resiliencia extrema, guerra o sabotaje;
- y series temporales publicas complejas cuyo costo de procesamiento excede su valor marginal en el prior inicial.

### 6.6 Fuentes peligrosas o ruidosas

Las siguientes familias se consideran presumiblemente inadmisibles:

- whitepapers comerciales;
- benchmarks sin frontera metodologica;
- scraping normativo indiscriminado;
- y fuentes cuya utilidad dependa de interpretacion libre del LLM.

Sus riesgos principales son sesgo promocional, falsa comparabilidad, erosion de fronteras y transferencia silenciosa de autoridad analitica al LLM.

### 6.7 Orden de admision para el MVP

El orden preferente de implementacion es:

1. geografia y clima;
2. benchmarks sectoriales y tipologicos;
3. jurisdiccion y regulacion de primer orden;
4. contexto energetico regional y factores de emision;
5. bibliotecas tecnicas estructurales.

### 6.8 Politica de first-stop references

La implementacion de Fase 1 debe buscar primero en familias de fuente que cumplan:

- provenance oficial o canonical;
- superficie metodologica acotada;
- identificadores o metadata suficientemente estables para mapeo canonico;
- utilidad directa para objetos canonicos;
- y fuerza semantica manejable dentro de Decision-grade.

Por ello, los first-stop references preferidos son:

- NOAA / NCEI para climate normals y degree-day context;
- EIA CBECS y EIA MECS para estructura benchmark;
- fuentes oficiales jurisdiccionales para benchmarking y performance laws;
- EPA eGRID y EPA GHG Emission Factors Hub, junto con EIA energy prices, para entorno energetico regional;
- y AChEE, DOE y LBNL para taxonomia tecnica estructural.

### 6.9 Regla de cierre de la Subfase 1B

El nucleo del Public Data Engine MVP se construira sobre cinco familias de fuente: (i) geografia y clima, (ii) benchmarks sectoriales y tipologicos, (iii) jurisdiccion y regulacion de primer orden, (iv) contexto energetico regional y factores de emision, y (v) bibliotecas tecnicas estructurales. Toda fuente adicional debera justificar explicitamente su utilidad restrictiva, su mapeo a objetos canonicos y su valor marginal frente al costo de complejidad que introduce.

## 7. 1C — Esquema maestro canonico del Public Data Engine

### 7.1 Proposito de la Subfase 1C

La Subfase 1C define el esquema maestro canonico del Public Data Engine. Su funcion es especificar la arquitectura minima de entidades requerida para convertir contexto publico admisible, input escaso del usuario, estructura de benchmarks, logica de arquetipos y supuestos acotados en un `facility_prior` trazable que permanezca estrictamente dentro de Decision-grade.

La Subfase 1C no organiza la Fase 1 alrededor de archivos, repositorios de fuentes o inventarios de datasets. Organiza la Fase 1 alrededor de entidades canonicas y bundles de salida. Su proposito es asegurar que todo dato admitido entre mediante clases de objeto gobernadas, relaciones explicitas y joins controlados en lugar de acumulacion documental ad hoc.

### 7.2 Decision arquitectonica central

La Fase 1 no se organiza por archivos ni por datasets. La Fase 1 se organiza por entidades canonicas, relaciones explicitas, join keys controladas y bundles de salida derivados de esas entidades.

Una fuente solo es admisible en la medida en que pueda poblar una o mas entidades canonicas bajo las restricciones ya establecidas en 1A y 1B.

### 7.3 Entidades maestras canonicas

El Public Data Engine queda gobernado por las siguientes doce entidades maestras:

1. `Facility`
2. `Jurisdiction`
3. `ClimateContext`
4. `SectorArchetype`
5. `BenchmarkContext`
6. `EnergyContext`
7. `RegulatoryContext`
8. `SourceVersion`
9. `SystemAsset`
10. `OperationalPractice`
11. `OrganizationCapability`
12. `ImprovementConstraint`

Estas entidades son suficientes para el MVP porque cubren en conjunto anclaje de instalacion, contexto territorial y climatico, comparabilidad arquetipica, estructura de benchmarks, entorno energetico, relevancia regulatoria, provenance y versionado, visibilidad de familias de sistemas, realismo operacional, realismo organizacional de ejecucion y restricciones de accionabilidad.

### 7.4 Rol y justificacion de cada entidad

#### 7.4.1 `Facility`

**Rol dentro de la Fase 1**  
`Facility` es el objeto ancla del `facility_prior`. Representa el perfil normalizado inicial de la instalacion a partir de input escaso, no una verdad completa del sitio.

**Por que existe**  
Sin un ancla canonica de instalacion, todo el contexto publico queda desconectado y no accionable.

**Que alimenta**  
`normalized_facility_profile`, `candidate_archetype_bundle`, `climate_energy_context_bundle`, `benchmark_bundle`, `jurisdiction_bundle`, `facility_prior`.

**Atributos minimos**
- `facility_id`
- `facility_name`
- `facility_type`
- `sector_code`
- `subsector_code`
- `primary_use`
- `size_value`
- `size_unit`
- `vintage_bucket`
- `operation_schedule_proxy`
- `primary_energy_type`
- `known_utility_context`
- `jurisdiction_id`
- `climate_zone_id`

**Ejemplos concretos**
- cold storage warehouse
- office building
- food processing plant
- metals manufacturing plant

**Que no debe pretender en esta fase**  
No debe pretender ser un modelo verificado del sitio, un inventario completo de activos, un objeto de desempeno medido ni una explicacion causal del sitio.

#### 7.4.2 `Jurisdiction`

**Rol dentro de la Fase 1**  
`Jurisdiction` es el ancla territorial y normativa primaria.

**Por que existe**  
La Fase 1 debe saber en que espacio administrativo y regulatorio se ubica la instalacion candidata antes de formular cualquier claim acotado de aplicabilidad.

**Que alimenta**  
`jurisdiction_bundle`, `regulatory_flag_bundle`, `facility_prior`.

**Atributos minimos**
- `jurisdiction_id`
- `country_code`
- `state_region_code`
- `city_code`
- `postal_zone`
- `regulatory_scope_tags`
- `benchmarking_applicability_flag`
- `reporting_applicability_flag`
- `performance_standard_flag`
- `effective_date`
- `source_version_id`

**Ejemplos concretos**
- NYC large building context
- state industrial compliance context
- municipal benchmarking applicability

**Que no debe pretender en esta fase**  
No debe pretender ser una opinion legal, una conclusion de compliance ni un motor regulatorio completo.

#### 7.4.3 `ClimateContext`

**Rol dentro de la Fase 1**  
`ClimateContext` representa la capa climatica agregada relevante para consumo energetico, comparabilidad y operacion.

**Por que existe**  
El clima restringe materialmente la plausibilidad de servicios de edificio, las expectativas estacionales de carga y la comparacion entre arquetipos.

**Que alimenta**  
`climate_energy_context_bundle`, `candidate_archetype_bundle`, `facility_prior`.

**Atributos minimos**
- `climate_zone_id`
- `climate_classification_system`
- `climate_zone_code`
- `hdd_annual`
- `cdd_annual`
- `avg_temp`
- `humidity_band`
- `solar_band`
- `weather_source_id`
- `weather_period`

**Ejemplos concretos**
- ASHRAE climate zone
- humid subtropical
- high cooling degree day profile

**Que no debe pretender en esta fase**  
No debe pretender describir operacion real del sitio, comportamiento termico medido ni carga de uso final verificada.

#### 7.4.4 `SectorArchetype`

**Rol dentro de la Fase 1**  
`SectorArchetype` representa arquetipos comparables candidatos por sector, uso, escala y patron operativo.

**Por que existe**  
La Fase 1 necesita estructuras de comparacion candidatas. No se fuerza un unico match cerrado de arquetipo en esta etapa; se requieren candidate sets.

**Que alimenta**  
`candidate_archetype_bundle`, `benchmark_bundle`, `prior_assumptions_pack`, `facility_prior`.

**Atributos minimos**
- `archetype_id`
- `sector_code`
- `subsector_code`
- `facility_type`
- `primary_use`
- `scale_bucket`
- `schedule_pattern`
- `climate_dependency_flag`
- `typical_end_use_profile`
- `typical_energy_vector_profile`
- `applicability_conditions`
- `benchmark_set_id`

**Ejemplos concretos**
- refrigerated warehouse archetype
- office archetype with high ventilation dependence
- process heat intensive manufacturing archetype

**Que no debe pretender en esta fase**  
No debe pretender ser la identidad verificada del sitio ni una asignacion conclusiva de arquetipo.

#### 7.4.5 `BenchmarkContext`

**Rol dentro de la Fase 1**  
`BenchmarkContext` representa benchmarks comparables normalizados.

**Por que existe**  
Los benchmarks son necesarios para definir rangos plausibles y clases de comparacion estructuradas. El benchmark no es evidencia local. Es restriccion contextual.

**Que alimenta**  
`benchmark_bundle`, `prior_assumptions_pack`, `facility_prior`.

**Atributos minimos**
- `benchmark_set_id`
- `benchmark_family`
- `benchmark_metric`
- `metric_unit`
- `sector_code`
- `facility_type`
- `climate_zone_dependency`
- `percentile_low`
- `percentile_mid`
- `percentile_high`
- `sample_scope`
- `methodological_boundary_note`
- `source_version_id`

**Ejemplos concretos**
- EUI ranges
- end-use shares
- electricity intensity by subsector

**Que no debe pretender en esta fase**  
No debe pretender ser desempeno local verificado, evidencia de anomalia ni prueba causal.

#### 7.4.6 `EnergyContext`

**Rol dentro de la Fase 1**  
`EnergyContext` representa el entorno energetico regional.

**Por que existe**  
El prior de la instalacion debe quedar restringido por region de red, factores publicos de emision, bandas regionales de precio y combustibles disponibles cuando aplique.

**Que alimenta**  
`climate_energy_context_bundle`, `benchmark_bundle`, `facility_prior`.

**Atributos minimos**
- `energy_context_id`
- `jurisdiction_id`
- `grid_region`
- `electricity_emission_factor`
- `fuel_emission_factor_set`
- `regional_energy_price_band`
- `fuel_availability_tags`
- `grid_mix_summary`
- `source_version_id`

**Ejemplos concretos**
- eGRID subregion
- high gas availability
- high carbon grid mix

**Que no debe pretender en esta fase**  
No debe pretender ser costo energetico verificado del sitio, emisiones medidas ni realidad contractual de procurement.

#### 7.4.7 `RegulatoryContext`

**Rol dentro de la Fase 1**  
`RegulatoryContext` representa reglas regulatorias ya mapeadas con logica acotada de aplicabilidad.

**Por que existe**  
La Fase 1 debe visibilizar que reglas publicas importan antes de cualquier escalamiento analitico posterior.

**Que alimenta**  
`jurisdiction_bundle`, `regulatory_flag_bundle`, `facility_prior`.

**Atributos minimos**
- `regulatory_context_id`
- `jurisdiction_id`
- `rule_family`
- `rule_name`
- `applicability_condition`
- `threshold_type`
- `threshold_value`
- `threshold_unit`
- `compliance_relevance_level`
- `effective_date`
- `expiration_date`
- `source_version_id`

**Ejemplos concretos**
- benchmarking threshold by floor area
- performance standard applicability
- lighting code relevance
- refrigerant regulation relevance

**Que no debe pretender en esta fase**  
No debe pretender ser determinacion final de compliance, cierre legal ni prediccion de enforcement.

#### 7.4.8 `SourceVersion`

**Rol dentro de la Fase 1**  
`SourceVersion` es la entidad de provenance y control de version.

**Por que existe**  
La Fase 1 no puede permitir silent overwrite, mutacion oculta de fuentes ni deriva no trazable de benchmarks.

**Que alimenta**  
Todas las entidades core, todos los bundles y toda la logica de reevaluacion.

**Atributos minimos**
- `source_version_id`
- `source_family`
- `source_name`
- `publisher`
- `coverage_scope`
- `release_date`
- `retrieval_date`
- `method_note`
- `trust_class`
- `stability_class`
- `version_label`

**Ejemplos concretos**
- NOAA climate normals release snapshot
- EIA CBECS edition reference
- EPA eGRID version label
- municipal benchmarking rule publication snapshot

**Que no debe pretender en esta fase**  
Registra provenance trazable y dependencia versionada, no infalibilidad epistemica.

#### 7.4.9 `SystemAsset`

**Rol dentro de la Fase 1**  
`SystemAsset` representa familias funcionalmente recurrentes de sistemas que pueden estar presentes, reportadas, ser plausibles, no aplicar o permanecer desconocidas.

**Por que existe**  
Un facility prior sin capa de sistemas colapsa en contextualismo grueso.

**Que alimenta**  
`candidate_archetype_bundle`, `prior_assumptions_pack`, `uncertainty_markers`, `facility_prior`.

**Atributos minimos**
- `system_asset_id`
- `facility_id`
- `system_family`
- `system_subfamily`
- `presence_status`
- `energy_role`
- `control_level_proxy`
- `criticality_level`
- `maintenance_dependency_flag`
- `benchmark_relevance_flag`
- `archetype_link_id`
- `source_version_id`

**Ejemplos concretos**
- HVAC rooftop units
- chilled water system
- steam boiler
- compressed air
- motors and drives
- refrigeration rack
- process furnace
- domestic hot water
- lighting system
- material handling or logistics

**Que no debe pretender en esta fase**  
No debe pretender ser un asset registry exhaustivo, un objeto CMMS ni un inventario verificado de sistemas.

#### 7.4.10 `OperationalPractice`

**Rol dentro de la Fase 1**  
`OperationalPractice` representa practicas operativas y de mantenimiento plausibles, reportadas o inferidas por proxy.

**Por que existe**  
El facility prior no debe detenerse en que sistemas podrian existir. Debe incluir tensiones operativas visibles sin convertirlas en claims causales.

**Que alimenta**  
`prior_assumptions_pack`, `uncertainty_markers`, `facility_prior`.

**Atributos minimos**
- `operational_practice_id`
- `facility_id`
- `practice_family`
- `practice_name`
- `practice_status`
- `affected_system_family`
- `risk_if_absent`
- `expected_energy_relevance`
- `expected_reliability_relevance`
- `source_basis`
- `source_version_id`

**Ejemplos concretos**
- preventive maintenance exists or absent
- utility bill reconciliation
- scheduling by occupancy or production
- setpoint management
- condensate recovery routine
- leak inspection routine
- BMS sequence review
- power factor monitoring

**Que no debe pretender en esta fase**  
No debe pretender probar que una falla de practica esta causando un problema del sitio.

#### 7.4.11 `OrganizationCapability`

**Rol dentro de la Fase 1**  
`OrganizationCapability` representa la capacidad organizacional minima requerida para detectar, gobernar, priorizar y ejecutar mejoras.

**Por que existe**  
Un facility prior que ignora las condiciones organizacionales de ejecucion se vuelve tecnicamente irreal.

**Que alimenta**  
`prior_assumptions_pack`, `uncertainty_markers`, `facility_prior`.

**Atributos minimos**
- `organization_capability_id`
- `facility_id`
- `role_coverage_tags`
- `energy_management_presence_flag`
- `bms_ems_usage_flag`
- `maintenance_governance_flag`
- `budget_process_maturity_level`
- `roi_decision_style`
- `vendor_dependency_level`
- `compliance_management_flag`
- `confidence_note`
- `source_version_id`

**Ejemplos concretos**
- no facility manager
- outsourced HVAC contractor only
- finance requires less than two-year payback
- BMS installed but underused
- no energy review process
- compliance handled externally

**Que no debe pretender en esta fase**  
No debe pretender inferir cultura, psicologia ni causalidad gerencial profunda.

#### 7.4.12 `ImprovementConstraint`

**Rol dentro de la Fase 1**  
`ImprovementConstraint` representa limites reales de accionabilidad.

**Por que existe**  
El `facility_prior` no puede ser solo un mapa de lo que podria estar mal o ser plausible. Tambien debe codificar que espacio de accion parece existir.

**Que alimenta**  
`prior_assumptions_pack`, `uncertainty_markers`, `facility_prior`.

**Atributos minimos**
- `improvement_constraint_id`
- `facility_id`
- `constraint_family`
- `constraint_name`
- `constraint_level`
- `affected_system_family`
- `impact_on_actionability`
- `reversibility_flag`
- `time_sensitivity_flag`
- `source_basis`
- `source_version_id`

**Ejemplos concretos**
- no shutdown window
- strict payback threshold
- production continuity constraint
- capex freeze
- compliance deadline
- reliability-critical line
- tenant comfort constraint
- refrigeration uptime constraint

**Que no debe pretender en esta fase**  
No debe pretender optimizar estrategia de intervencion ni producir una jerarquia final de recomendaciones.

### 7.5 Atributos minimos por entidad

Los atributos minimos del esquema son los listados arriba para cada entidad. Son suficientes porque permiten normalizacion de ancla mediante `Facility`, restriccion territorial y normativa mediante `Jurisdiction` y `RegulatoryContext`, comparabilidad climatica mediante `ClimateContext`, matching estructural candidato mediante `SectorArchetype`, comparacion acotada mediante `BenchmarkContext`, restriccion energetica regional mediante `EnergyContext`, provenance y reevaluacion mediante `SourceVersion`, representacion minima de sistemas mediante `SystemAsset`, realismo operacional mediante `OperationalPractice`, realismo de ejecucion mediante `OrganizationCapability` y realismo de accionabilidad mediante `ImprovementConstraint`.

### 7.6 Relaciones minimas entre entidades

El conjunto minimo de relaciones es:

- `Facility -> Jurisdiction`
- `Facility -> ClimateContext`
- `Facility -> SectorArchetype` mediante logica de candidate set, no match singular forzado
- `SectorArchetype -> BenchmarkContext`
- `Jurisdiction -> RegulatoryContext`
- `Jurisdiction -> EnergyContext`
- `Facility -> SystemAsset`
- `Facility -> OperationalPractice`
- `Facility -> OrganizationCapability`
- `Facility -> ImprovementConstraint`
- `All core entities -> SourceVersion`

Estas relaciones son suficientes para el MVP porque crean un camino restringido completo desde identidad escasa de instalacion hacia emplazamiento contextual, candidatura de arquetipo, vinculacion de benchmarks, plausibilidad de sistemas, visibilidad operacional, capacidad de ejecucion y limites de accionabilidad.

### 7.7 Join keys minimas

Las join keys minimas son:

- `facility_id`
- `jurisdiction_id`
- `climate_zone_id`
- `sector_code`
- `facility_type`
- `archetype_id`
- `benchmark_set_id`
- `source_version_id`
- `energy_context_id`
- `regulatory_context_id`
- `system_asset_id`
- `operational_practice_id`
- `organization_capability_id`
- `improvement_constraint_id`

Reglas de join:

- no debe usarse texto libre como join key primaria;
- si una relacion es incierta, debe representarse mediante candidate sets, applicability conditions o estructuras acotadas many-to-one o many-to-many en lugar de linkage deterministico forzado;
- toda taxonomia usada en joins debe llevar al menos code, label, definition y boundary;
- `source_version_id` debe adjuntarse donde exista dependencia material.

### 7.8 Bundles de salida que el esquema debe soportar

El esquema canonico debe soportar al menos los siguientes bundles de salida:

- `normalized_facility_profile`
- `candidate_archetype_bundle`
- `climate_energy_context_bundle`
- `benchmark_bundle`
- `jurisdiction_bundle`
- `regulatory_flag_bundle`
- `prior_assumptions_pack`
- `uncertainty_markers`
- `facility_prior`

La contribucion de grupos de entidades sigue esta logica:

- contexto base: `Facility`, `Jurisdiction`, `ClimateContext`, `EnergyContext`;
- capa de comparabilidad: `SectorArchetype`, `BenchmarkContext`;
- capa de sistemas: `SystemAsset`;
- tensiones operativas ocultas: `OperationalPractice`;
- realismo de implementacion: `OrganizationCapability`;
- realismo de accionabilidad: `ImprovementConstraint`;
- trazabilidad y reevaluacion: `SourceVersion`.

### 7.9 Reglas de versionado y provenance

El esquema canonico queda gobernado por las siguientes reglas de versionado y provenance:

- ningun objeto material puede circular sin atribucion de fuente;
- ningun objeto publico reutilizado materialmente puede existir sin linkage a `SourceVersion`;
- no se permite silent overwrite para dependencias de benchmark, regulacion, clima o contexto energetico;
- rebuild y reevaluacion deben seguir siendo posibles desde la provenance almacenada;
- cualquier cambio en edicion de fuente, release, retrieval basis o methodological note debe poder representarse en la capa `SourceVersion`.

`SourceVersion` no es por tanto un objeto auxiliar de conveniencia. Es un objeto rector de trazabilidad exigido por la herencia de Fase 0.

### 7.10 Campos epistemologicos minimos heredados de Fase 0

Los objetos derivados y bundles de salida producidos desde el esquema canonico deben heredar, como minimo, los siguientes campos de gobernanza epistemica:

- `claim_family`
- `knowledge_mode`
- `validation_status`
- `intended_use`
- `critical_limits`
- `dependency_note`
- `uncertainty_level`
- `review_needed_flag`

La normalizacion de entidades por si sola es insuficiente. La materializacion de bundles debe arrastrar las marcas de gobernanza de Fase 0.

### 7.11 Que seria sobre-ingenieria en 1C

Quedan fuera de alcance de la Subfase 1C y constituirian sobre-ingenieria:

- una ontologia industrial exhaustiva;
- un asset registry completo;
- un digital twin detallado;
- un maintenance history engine;
- un anomaly engine;
- un utility tariff engine exhaustivo;
- un process graph fino por linea;
- un knowledge graph complejo;
- o modelado blando de cultura organizacional.

### 7.12 Criterio de terminado de la Subfase 1C

La Subfase 1C queda terminada cuando el framework puede declarar sin ambiguedad:

- que entidades canonicas minimas existen;
- que atributos minimos porta cada entidad;
- como se relacionan esas entidades;
- que join keys gobiernan el esquema;
- que bundles de salida soporta;
- y por que este recorte es suficiente para producir un `facility_prior` util sin fingir mas de lo que el sistema realmente sabe.

La Subfase 1C no queda terminada cuando el esquema es grande. Queda terminada cuando el esquema es minimo, coherente, joinable, trazable y suficientemente fuerte para soportar la Fase 1 sin inflacion semantica.

## 8. 1D — Contrato formal del `facility_prior` e inputs minimos

### 8.1 Proposito de la Subfase 1D

La Subfase 1D cierra el contrato formal del `facility_prior` y define el intake minimo con el que puede generarse sin sobreafirmacion epistemologica.

Su funcion es resolver dos puntos de diseno que no pueden quedar implicitos:

1. que es exactamente el `facility_prior`;
2. con que inputs minimos puede generarse legitimamente dentro de la Fase 1.

La decision central de esta subfase es cerrada:

> El `facility_prior` no es un diagnostico, ni una linea base verificada, ni una recomendacion final.  
> Es una representacion estructurada y no verificatoria del contexto probable de una instalacion, suficientemente restringida para orientar inferencia posterior, priorizacion de medicion y lectura regulatoria inicial.

### 8.2 Definicion formal del `facility_prior`

El `facility_prior` es el objeto central de salida de la Fase 1.

Es una representacion estructurada, trazable, versionable y no verificatoria del contexto probable de una instalacion candidata, construida a partir de fuentes publicas admisibles, inputs minimos del usuario, arquetipos comparables, benchmarks normalizados, supuestos explicitos y marcadores visibles de incertidumbre.

Su funcion no es establecer verdad local del sitio. Su funcion es restringir el espacio de hipotesis antes de fases posteriores de analisis, modelado, medicion o verificacion.

### 8.3 Que contiene el `facility_prior`

El `facility_prior` contiene unicamente aquello que Fase 1 puede sostener legitimamente bajo Decision-grade.

#### 8.3.1 `normalized_facility_profile`

Es la traduccion estructurada del intake minimo. Describe la instalacion candidata de forma normalizada y joinable.

Debe incluir, como minimo:

- tipo de instalacion;
- sector;
- subsector cuando aplique;
- uso principal;
- tamano o proxy de escala;
- vintage aproximado;
- jurisdiccion;
- clima;
- energia principal conocida;
- y horario operativo aproximado.

#### 8.3.2 `candidate_archetypes`

Es la lista ordenada de arquetipos plausibles compatibles con el perfil inicial de la instalacion.

No debe forzar un unico arquetipo cerrado. Debe preservar pluralidad cuando el soporte inicial no alcance para cierre.

Debe incluir:

- lista ordenada de arquetipos plausibles;
- condiciones de aplicabilidad;
- nota de incertidumbre;
- y relacion con benchmarks relevantes.

#### 8.3.3 `climate_energy_context`

Es el bundle contextual que acota el entorno climatico y energetico dentro del cual debe leerse la instalacion.

Debe incluir:

- HDD / CDD;
- banda o clasificacion climatica;
- grid region y factores publicos de emisiones;
- banda regional de costo energetico;
- y combustibles plausibles o disponibles.

#### 8.3.4 `benchmark_context`

Es el conjunto acotado de benchmarks comparables que disciplina la lectura inicial de la instalacion.

Debe incluir:

- metricas comparables aplicables;
- rango bajo / medio / alto;
- notas metodologicas;
- y advertencia explicita de que benchmark no equivale a evidencia local.

#### 8.3.5 `regulatory_context`

Es la lectura regulatoria inicial de primer orden derivada de jurisdiccion, tipo de instalacion, escala y thresholds plausibles.

Debe incluir:

- flags aplicables;
- thresholds;
- reporting relevance;
- pressure indicators;
- y posibles obligaciones normativas de primer orden.

#### 8.3.6 `system_asset_hypothesis`

Es la hipotesis funcional sobre sistemas comunes presentes o plausibles.

No es un inventario verificado del sitio. Es una capa estructurada de sistemas esperables o compatibles.

Puede incluir familias como:

- HVAC;
- boilers;
- furnaces;
- refrigeration;
- domestic hot water;
- lighting;
- motors and drives;
- compressed air;
- ventilation;
- BMS / EMS;
- CHP;
- y logistics or material handling systems.

#### 8.3.7 `operational_tension_hypothesis`

Es la capa de tensiones operativas plausibles asociadas a sistemas, horarios, practicas y patrones repetibles.

No afirma error causal. No demuestra falla. No cierra diagnostico tecnico.

Puede incluir hipotesis como:

- scheduling mismatch;
- poor setpoint governance;
- weak maintenance routines;
- missing condensate recovery attention;
- weak bill reconciliation;
- low control integration;
- hidden losses in repeated processes;
- underuse of BMS / EMS;
- no power factor monitoring;
- reactive maintenance profile.

#### 8.3.8 `organization_actionability_profile`

Es el perfil minimo de capacidad de accion de la organizacion respecto de operacion, mantenimiento, revision energetica, cumplimiento y ejecucion de mejoras.

No es psicologia organizacional. Es una capa minima de capacidad operativa.

Puede incluir senales como:

- outsourced-only maintenance model;
- no facility manager;
- BMS installed but underused;
- finance requires sub-2-year payback;
- no formal energy review process;
- compliance handled externally;
- low in-house technical control.

#### 8.3.9 `improvement_constraint_profile`

Es la representacion temprana del espacio de maniobra.

No es priorizacion final. No es diseno de estrategia de intervencion. No es ranking definitivo de inversiones.

Puede incluir restricciones como:

- no shutdown window;
- production continuity constraint;
- capex freeze;
- strict payback threshold;
- compliance deadline;
- tenant comfort constraint;
- uptime-critical refrigeration;
- reliability-critical production line.

#### 8.3.10 `prior_assumptions_pack`

Es el paquete explicito de supuestos utilizado para cerrar vacios inevitables del intake y del contexto publico.

Es no negociable.

Debe incluir, como minimo:

- supuestos usados para completar arquetipos;
- supuestos sobre sistemas plausibles;
- supuestos sobre operacion;
- supuestos regulatorios;
- y supuestos sobre restricciones.

#### 8.3.11 `uncertainty_markers`

Es el conjunto explicito de marcadores de incertidumbre asociado al prior.

Puede incluir incertidumbres como:

- low certainty in facility type classification;
- unknown tariff;
- unknown real system mix;
- limited regulatory applicability confidence;
- unknown schedule precision;
- unknown energy vector mix;
- low confidence in organization capability inference.

### 8.4 Que NO contiene el `facility_prior`

El `facility_prior` no debe contener:

- ahorro verificado;
- consumo real medido;
- root cause analysis;
- recomendacion final de intervencion;
- ROI confiable por proyecto;
- compliance determination final;
- M&V;
- inferencia causal cerrada;
- priorizacion definitiva de inversiones.

Estas exclusiones son duras y no admiten reinterpretacion dentro de la Fase 1.

### 8.5 Estado epistemologico del `facility_prior`

El `facility_prior` pertenece a Decision-grade y no puede exceder ese estatus.

Debe declararse mediante campos de gobernanza epistemologica heredados de Fase 0, como minimo:

- `claim_family`
- `knowledge_mode`
- `validation_status`
- `intended_use`
- `critical_limits`
- `dependency_note`
- `uncertainty_level`
- `review_needed_flag`

Reglas minimas:

- su familia principal es `exploratory_structural_claim`, acompanada por claims contextuales derivados;
- su `validation_status` no puede exceder un uso valido en Decision-grade;
- nunca debe presentarse como `Verified`;
- su `intended_use` queda limitado a screening, scoping, early prioritization, next-measurement planning y lectura regulatoria inicial.

### 8.6 Inputs minimos del usuario

El contrato minimo de generacion del `facility_prior` se cierra con diez inputs razonables.

#### 8.6.1 Ubicacion

Debe admitir, segun disponibilidad:

- pais;
- estado o region;
- ciudad;
- zip o postal code si existe.

Este input activa jurisdiccion, clima, energia y regulacion.

#### 8.6.2 Tipo de instalacion

Ejemplos tipicos:

- office;
- hospital;
- warehouse;
- cold storage;
- food processing;
- manufacturing;
- data center;
- retail;
- school;
- multifamily.

Este input activa arquetipos, systems layer y benchmarks.

#### 8.6.3 Sector o subsector

Este input mejora comparabilidad, typical end-use structure y disciplina la seleccion de benchmarks y arquetipos.

#### 8.6.4 Uso principal

Ejemplos tipicos:

- produccion;
- almacenamiento;
- oficinas;
- salud;
- educacion;
- retail;
- mixed-use.

#### 8.6.5 Tamano aproximado

Puede expresarse como:

- area;
- capacidad;
- produccion;
- numero de pisos;
- o proxy equivalente.

#### 8.6.6 Antiguedad o vintage aproximado

Este input afecta sistemas plausibles, controles plausibles, regimen regulatorio y eficiencia esperable.

#### 8.6.7 Horario operativo aproximado

Ejemplos tipicos:

- 24/7;
- one shift;
- two shifts;
- commercial hours;
- seasonal;
- mixed.

#### 8.6.8 Energia o combustible principal conocido

Ejemplos tipicos:

- electricity;
- gas;
- steam;
- chilled water;
- district energy;
- multiple;
- unknown.

#### 8.6.9 Sistemas principales conocidos

Debe capturarse como checklist corto, por ejemplo:

- HVAC;
- boilers;
- furnaces;
- refrigeration;
- motors / VFD;
- DHW;
- ventilation;
- BMS / EMS;
- compressed air;
- CHP;
- unknown.

#### 8.6.10 Preocupacion principal o driver principal

Ejemplos tipicos:

- cost;
- compliance;
- comfort;
- process performance;
- reliability;
- carbon;
- unknown.

Este input no sirve para diagnosticar. Sirve para orientar lectura y priorizacion posterior.

### 8.7 Inputs opcionales pero valiosos

No forman parte del contrato minimo, pero son utiles cuando existen:

- utility name;
- tarifa conocida;
- presupuesto aproximado;
- threshold de payback;
- existencia de facility manager;
- existencia de BMS / EMS;
- problema recurrente declarado.

### 8.8 Mapeo de inputs a bundles y entidades

#### 8.8.1 Ubicacion

Alimenta:

- `Jurisdiction`
- `ClimateContext`
- `EnergyContext`
- `RegulatoryContext`
- `jurisdiction_bundle`
- `climate_energy_context_bundle`

#### 8.8.2 Tipo de instalacion + sector + uso principal

Alimenta:

- `Facility`
- `SectorArchetype`
- `BenchmarkContext`
- `SystemAsset`
- `candidate_archetype_bundle`
- `benchmark_bundle`

#### 8.8.3 Tamano + vintage

Alimenta:

- `Facility`
- `BenchmarkContext`
- `RegulatoryContext`

#### 8.8.4 Horario operativo

Alimenta:

- `Facility`
- `OperationalPractice`
- `candidate_archetype_bundle`
- `operational_tension_hypothesis`

#### 8.8.5 Energia principal + sistemas conocidos

Alimenta:

- `EnergyContext`
- `SystemAsset`
- `prior_assumptions_pack`

#### 8.8.6 Driver principal

Alimenta:

- `OrganizationCapability`
- `ImprovementConstraint`
- orientacion de lectura del prior

### 8.9 Forma estructurada de salida del `facility_prior`

La salida principal de la Subfase 1D no es texto libre. Es un objeto estructurado.

Un contrato logico minimo admisible es:

```yaml
facility_prior:
  prior_id:
  generated_at:
  claim_family: exploratory_structural_claim
  knowledge_mode:
  validation_status:
  intended_use:
  critical_limits: []
  dependency_note:
  uncertainty_level:
  review_needed_flag:
  normalized_facility_profile: {}
  candidate_archetypes: []
  climate_energy_context: {}
  benchmark_context: {}
  regulatory_context: {}
  system_asset_hypothesis: []
  operational_tension_hypothesis: []
  organization_actionability_profile: {}
  improvement_constraint_profile: {}
  prior_assumptions_pack: []
  uncertainty_markers: []
  source_dependencies: []
```

Reglas estructurales minimas:

- `normalized_facility_profile` debe existir siempre;
- `candidate_archetypes` debe ser una lista, no una unica etiqueta forzada;
- `system_asset_hypothesis` debe distinguir estado conocido, reportado, plausible o desconocido;
- `operational_tension_hypothesis` debe expresarse como plausibilidad acotada, no como falla confirmada;
- `prior_assumptions_pack` y `uncertainty_markers` no son opcionales;
- `source_dependencies` debe permitir trazabilidad a entidades y `SourceVersion`.

### 8.10 Errores tipicos de diseno de esta subfase

1. convertir el prior en pseudo-diagnostico;
2. pedir demasiados inputs y matar el MVP;
3. forzar exactitud donde solo hay plausibilidad;
4. no explicitar supuestos;
5. no distinguir sistemas comunes plausibles vs sistemas confirmados;
6. usar benchmarks como evidencia local;
7. convertir drivers del usuario en conclusiones tecnicas.

### 8.11 Criterio de terminado

La Subfase 1D queda terminada cuando se sabe sin ambiguedad:

- que es el `facility_prior`;
- que contiene;
- que no contiene;
- que nivel epistemologico tiene;
- con que diez inputs minimos puede generarse;
- como esos inputs alimentan entidades y bundles;
- y en que forma estructurada debe vivir.

El `facility_prior` es el objeto central de Fase 1. Resume, en forma estructurada, trazable y no verificatoria, el contexto probable de una instalacion a partir de fuentes publicas, inputs minimos del usuario, arquetipos, benchmarks y supuestos explicitos. Su funcion no es diagnosticar ni verificar, sino restringir el espacio de hipotesis y preparar la inferencia posterior.

## 9. 1E — Reglas anti-sprawl, recorte MVP, gobernanza de curacion y criterio de terminado

### 9.1 Proposito de la Subfase 1E

La Subfase 1E cierra el mecanismo final de defensa de la Fase 1. Define que entra ahora, que entra despues, que se difiere, que se bloquea, como se gobierna la curacion y que prueba objetiva debe pasarse para declarar terminada la Fase 1.

Existe para cerrar alcance, disciplina de curacion, politica anti-sprawl y logica de cierre bajo una sola politica operativa.

> La calidad de la Fase 1 no se mide por la cantidad de fuentes, variables o tablas, sino por su capacidad de producir un `facility_prior` util, trazable, no verificatorio y suficientemente restrictivo con el menor numero de componentes necesarios.

### 9.2 Riesgo central: dataset sprawl

Dataset sprawl es el riesgo central de la Fase 1: demasiados datos sin estructura util.

En la practica, este riesgo se manifiesta no solo como exceso de volumen, sino como exceso de superficie semantica, exceso de joins, exceso de heterogeneidad de fuentes y exceso de confianza inferida respecto de lo que la fase puede sostener legitimamente.

### 9.3 Formas concretas de sprawl que deben prevenirse

#### 9.3.1 Sprawl de fuentes

Ejemplos:

- agregar varios portales regulatorios porque quizas sirvan;
- incorporar repositorios completos de benchmarking municipal antes de estabilizar el nucleo de benchmarks;
- cargar repositorios climaticos redundantes sin mejorar el climate bundle.

#### 9.3.2 Sprawl de variables

Ejemplos:

- campos de humedad, viento, radiacion, presion, orientacion, ocupacion o materiales sin destino canonico;
- variables que parecen sofisticadas pero no mejoran comparabilidad, aplicabilidad regulatoria, plausibilidad de sistemas, realismo de accionabilidad o control de incertidumbre.

#### 9.3.3 Sprawl semantico

Ejemplos:

- taxonomias infinitas de `facility_type`;
- demasiadas subcategorias de sistemas;
- multiples nombres para la misma entidad o concepto.

#### 9.3.4 Sprawl funcional

Ejemplos:

- intentar hacer diagnostico, scoring financiero por proyecto, compliance final, contabilidad fuerte de carbono o recomendaciones de alto peso dentro de la Fase 1.

#### 9.3.5 Sprawl narrativo

Ejemplos:

- summaries ejecutivos que suenan a diagnostico;
- dashboards que implican mas certeza de la que el soporte real permite.

### 9.4 Reglas anti-sprawl duras

#### Regla 1 — Ningun dato entra sin destino canonico

Todo dato, fuente, benchmark, regla o campo debe tener:

- entidad destino;
- bundle destino;
- uso downstream;
- y limite epistemologico explicito.

Ejemplo:
- HDD entra porque alimenta `ClimateContext` y `climate_energy_context_bundle`.
- Un PDF comercial sin variable destino no entra.

#### Regla 2 — Ningun campo entra “por si acaso”

Los campos solo entran si mejoran materialmente:

- clasificacion o calidad de arquetipo;
- comparabilidad;
- aplicabilidad regulatoria;
- utilidad de la systems layer;
- realismo de accionabilidad;
- o marcacion de incertidumbre.

#### Regla 3 — Ninguna fuente entra por prestigio

Que una fuente venga de DOE, EPA o un publisher de alto estatus no es suficiente. Si no mejora materialmente el prior, no entra.

#### Regla 4 — Ninguna complejidad entra sin ganancia marginal clara

Ejemplos tipicamente bloqueados en el MVP:

- utility tariffs exhaustivas;
- armonizacion multinacional profunda;
- graph modeling fino;
- compliance engines complejos.

#### Regla 5 — Ningun output de Fase 1 puede depender de infraestructura no necesaria para el MVP

Complejidad bloqueada en esta etapa:

- scraping masivo;
- vector database como nucleo;
- orchestration compleja;
- engines normativos exhaustivos.

#### Regla 6 — Todo supuesto debe ser mas barato que el dato que reemplaza

Si el horario exacto es desconocido, puede admitirse un proxy grueso de horario comercial. Un perfil horario sintetico y fino no es admisible si introduce mas ruido que valor.

#### Regla 7 — No forzar resolucion donde la incertidumbre es la salida correcta

Ejemplos:

- candidate archetype set en vez de un arquetipo unico falso;
- `unknown` en presencia de sistemas en vez de inventario ficticio;
- bandera de incertidumbre regulatoria en vez de claim fuerte de aplicabilidad.

### 9.5 Gobernanza de curacion del MVP

> En el MVP, la curacion del nucleo de la Fase 1 es una funcion gobernada por criterio humano asistido por IA. La IA puede proponer, clasificar, resumir, normalizar, mapear, priorizar y documentar. La aprobacion final de admision del nucleo, la definicion del recorte y el bloqueo de complejidad prematura permanecen bajo control humano.

#### 9.5.1 Rol humano

El arquitecto humano:

- define criterios de admision;
- aprueba o rechaza nuevas fuentes nucleo;
- resuelve ambiguedad epistemologica;
- bloquea fuentes ruidosas o que inducen sobrelectura;
- decide el recorte MVP;
- y autoriza la entrada de nuevas familias de complejidad.

#### 9.5.2 Rol de la IA

La IA:

- propone familias de fuentes;
- clasifica fuentes por prioridad y riesgo;
- normaliza nombres, taxonomias y atributos;
- resume contenido relevante;
- mapea variables a entidades y bundles;
- documenta provenance y notas metodologicas;
- detecta duplicidad y sprawl;
- y prepara matrices de admision.

#### 9.5.3 Que NO se delega a la IA en esta etapa

La IA no:

- define sola el nucleo de fuentes;
- decide sola que complejidad entra al MVP;
- declara terminado el sistema;
- ni sustituye juicio arquitectonico sobre limites de fase.

### 9.6 Que se cura manualmente, que asiste la IA y que puede automatizarse despues

#### 9.6.1 Curacion manual obligatoria en el MVP

- seleccion de las cinco familias nucleo de fuente;
- definicion de taxonomias canonicas;
- aprobacion de benchmarks nucleo;
- aprobacion de reglas regulatorias de primer orden;
- decision de que campos son realmente indispensables.

#### 9.6.2 Curacion asistida por IA en el MVP

- extraccion y resumen de metadatos de fuentes;
- clasificacion de fuente en prioritaria / secundaria / peligrosa;
- sugerencias de mapping a entidades;
- deteccion de duplicados;
- generacion de notas de frontera metodologica;
- identificacion de gaps de cobertura.

#### 9.6.3 Automatizacion posterior

- refresh periodico de fuentes estables;
- verificacion automatica de versiones;
- deteccion de cambios en datasets publicos;
- validacion formal de esquemas;
- scoring de cobertura;
- propagacion de cambios a objetos dependientes.

### 9.7 Recorte MVP: indispensable ahora

#### 9.7.1 Nucleo de fuentes

El MVP incluye solo:

1. geografia y clima;
2. benchmarks sectoriales y tipologicos;
3. jurisdiccion y regulacion de primer orden;
4. contexto energetico regional y factores de emision;
5. bibliotecas tecnicas estructurales.

#### 9.7.2 Nucleo de entidades

El MVP incluye las doce entidades canonicas definidas en 1C.

#### 9.7.3 Nucleo de salida

Con diez inputs minimos del usuario, el sistema debe producir:

- `normalized_facility_profile`
- `candidate_archetype_bundle`
- `climate_energy_context_bundle`
- `benchmark_bundle`
- `jurisdiction_bundle`
- `regulatory_flag_bundle`
- `prior_assumptions_pack`
- `uncertainty_markers`
- `facility_prior`

#### 9.7.4 Nucleo de gobernanza

El MVP incluye:

- provenance minima;
- supuestos explicitos;
- limites visibles;
- control de incertidumbre;
- y no dependencia del LLM como analista soberano.

### 9.8 Util despues

Util despues, pero no necesario para cerrar el MVP:

- disclosure datasets mas finos;
- contexto utility mas especifico;
- proxies operativos mejor calibrados;
- subtipos mas granulares de systems layer;
- scoring interno mas refinado;
- perfiles de accionabilidad mas granulares.

### 9.9 Investigacion futura

Investigacion futura, no cierre del MVP:

- utility tariffs exhaustivas;
- armonizacion internacional profunda;
- integracion detallada de mercados de carbono;
- escenarios de resiliencia extrema;
- graph modeling fino;
- linking automatico con standards complejos.

### 9.10 Humo

Los siguientes elementos son ruido o teatro en esta etapa, salvo justificacion posterior bajo gobernanza:

- chatbot que “mira datasets y opina”;
- dashboards bonitos como sustituto del prior;
- vector database como nucleo;
- scraping masivo sin modelo canonico;
- taxonomias infinitas;
- compliance engine legalista desde el dia 1;
- asset registry exhaustivo;
- digital twin decorativo.

### 9.11 Criterios de admision de nueva complejidad

Ninguna nueva fuente, variable, entidad o regla entra despues si no puede responder afirmativamente a las preguntas relevantes siguientes:

1. ¿Mejora materialmente el `facility_prior`?
2. ¿Alimenta un bundle existente o justifica claramente uno nuevo?
3. ¿Tiene provenance estable?
4. ¿Evita duplicar una pieza ya existente?
5. ¿Su valor marginal supera su costo de complejidad?
6. ¿Evita invadir Fase 2 o Fase 4?
7. ¿Evita inducir sobrelectura?

Si falla una condicion material, la nueva complejidad no entra.

### 9.12 Que significa “Fase 1 terminada”

#### 9.12.1 Fase 1 no esta terminada si

- hay datasets cargados pero no bundles utiles;
- hay taxonomias pero no puede producirse un prior util;
- existe un prior pero requiere cuarenta preguntas;
- el prior depende de interpretacion libre del LLM;
- no hay supuestos explicitos;
- no existe provenance minima;
- la incertidumbre no es visible.

#### 9.12.2 Fase 1 si esta terminada si

Con diez inputs minimos, el sistema puede producir un `facility_prior` que:

1. sea estructurado;
2. sea trazable;
3. sea explicitamente no verificatorio;
4. tenga candidate archetypes plausibles;
5. tenga benchmark context util;
6. tenga climate-energy context util;
7. tenga regulatory relevance util;
8. tenga systems layer plausible;
9. tenga tensiones operativas plausibles;
10. tenga actionability y constraint realism basico;
11. muestre supuestos;
12. muestre incertidumbre;
13. sirva materialmente como insumo para Fase 2.

### 9.13 Pruebas minimas de aceptacion del MVP

#### Test A — Office / compliance-driven

Perfil de entrada:

- ubicacion: NYC
- tipo: office
- tamano: 120,000 sq ft
- vintage: 1985
- horario: commercial hours
- energia: electricity + gas
- sistemas conocidos: HVAC, lighting, BMS unknown
- preocupacion principal: compliance

Salida esperada:

- candidate archetypes plausibles;
- benchmark context util;
- regulatory flags plausibles;
- systems layer comun;
- tensiones operativas plausibles;
- restricciones plausibles;
- incertidumbre visible.

#### Test B — Industrial / reliability-driven

Perfil de entrada:

- ubicacion: zona industrial en Colombia
- tipo: food processing
- horario: 24/7
- energia: electricidad + refrigeration + motors
- vintage: 2000s
- sistemas conocidos: refrigeration, motors, boilers unknown
- preocupacion principal: cost + reliability

Salida esperada:

- arquetipos de proceso mas refrigeracion;
- benchmark context razonable;
- systems layer plausible;
- tensiones de mantenimiento, control y continuidad;
- restricciones de uptime y proceso;
- sin fingir diagnostico.

#### Test C — Sparse data case

Perfil de entrada:

- ciudad
- tipo de instalacion
- tamano
- uso principal
- preocupacion principal
- muchos campos unknown

Salida esperada:

- prior todavia util;
- mayor incertidumbre visible;
- menor resolucion;
- estructura preservada;
- sin cierre inventado.

### 9.14 Errores tipicos al cerrar Fase 1

Errores frecuentes:

1. declarar terminado porque existe el esquema aunque no exista prior util;
2. seguir agregando fuentes indefinidamente;
3. confundir granularidad con mejor inteligencia;
4. permitir que el LLM tape huecos estructurales;
5. no probar casos sparse e industriales;
6. automatizar la curacion demasiado pronto;
7. permitir que el prior suene mas fuerte que su soporte.

### 9.15 Criterio de terminado de la subfase

La Subfase 1E queda terminada cuando el documento de Fase 1 deja explicito:

- que entra ahora;
- que entra despues;
- que se investiga despues;
- que se bloquea;
- como se gobierna la curacion;
- que parte permanece bajo control humano;
- que parte es asistida por IA;
- que pruebas minimas debe pasar el prior;
- y que condiciones objetivas definen el cierre real de la Fase 1.

> La Fase 1 se considera terminada cuando el Public Data Engine, usando unicamente fuentes publicas admitidas y un intake minimo de 10 inputs, puede generar un `facility_prior` estructurado, trazable, no verificatorio y suficientemente util para restringir hipotesis, orientar lectura regulatoria inicial y preparar inferencia posterior, sin depender de sobreingenieria, sin invadir Fase 2 y sin inducir falsa precision.

> En el MVP, la curacion del nucleo de la Fase 1 permanece bajo gobernanza humana asistida por IA. La automatizacion se aplica primero a tareas repetibles de clasificacion, normalizacion, trazabilidad y actualizacion; no a la definicion soberana del nucleo epistemologico del sistema.

## 10. 1F — Integracion, coherencia final y gate computable de avance a Fase 2

### 10.1 Proposito de la Subfase 1F

La Subfase 1F define el gate computable de aceptacion para el cierre de la Fase 1 y la condicion formal bajo la cual el Public Data Engine puede avanzar a Fase 2.

Su proposito es eliminar una ambiguedad inaceptable: la Fase 1 no puede cerrarse porque el output suena convincente, porque el documento esta bien escrito o porque el arquitecto tiene una impresion general favorable. La Fase 1 se cierra solo cuando se cumplen condiciones estructurales, epistemologicas y operativas explicitas.

La Subfase 1F convierte por tanto “operacionalmente util” en una logica auditable compuesta por:

- gates binarios obligatorios;
- scores auxiliares computables;
- reglas de no compensacion;
- casos de prueba explicitos;
- y condiciones explicitas de pase, fallo y rebuild.

### 10.2 Por que el cierre no puede depender de juicio subjetivo libre

Si el cierre depende solo de juicio arquitectonico amplio, el framework se vuelve vulnerable a cuatro fallas recurrentes:

- narrativa persuasiva reemplazando estructura real;
- sofisticacion aparente reemplazando provenance y supuestos;
- outputs densos ocultando incertidumbre no resuelta;
- y avance prematuro de fase impulsado por inercia en lugar de admisibilidad.

Un prior de Fase 1 puede parecer coherente y aun asi fallar en su funcion real. Puede sonar disciplinado y aun carecer de:

- provenance explicita;
- supuestos visibles;
- incertidumbre visible;
- estatus no verificatorio acotado;
- o robustez bajo casos sparse e industriales.

### 10.3 Que significa volver computable el gate de aceptacion

Volver computable el gate de aceptacion no significa fingir que toda pregunta epistemologica puede reducirse a un solo numero. Significa que la condicion de cierre de la Fase 1 se evalua mediante chequeos explicitos y auditables sobre la estructura de salida, su provenance, sus limites declarados y su robustez operativa minima.

Las siguientes cosas son computables en Fase 1 y, por tanto, deben formalizarse:

- si existe un objeto estructurado `facility_prior`;
- si todos los bundles obligatorios estan presentes;
- si el prior puede generarse con no mas de diez inputs obligatorios;
- si cada componente principal tiene provenance minima;
- si existen supuestos explicitos;
- si existen uncertainty markers;
- si la salida esta marcada explicitamente como no verificatoria;
- si la estructura critica no esta siendo improvisada solo por el LLM;
- si existen candidate archetypes;
- si existe una systems layer plausible;
- si existen capas operativas o de accionabilidad;
- y si pasan los casos de prueba obligatorios.

Ejemplos simples aclaran el principio:

- si falta `uncertainty_markers`, eso no es una opinion; es una ausencia objetiva;
- si el sistema requiere dieciseis inputs obligatorios en lugar de diez, eso puede contarse;
- si el sparse case colapsa y devuelve cero candidate archetypes, eso puede medirse.

### 10.4 Limite epistemologico: que si se puede computar y que no

La Fase 1 debe distinguir entre lo que es legitimamente computable y aquello que se volveria falsa objetividad si se forzara a matematica prematuramente.

#### 10.4.1 Que si puede computarse

Lo siguiente puede computarse sin abuso epistemologico:

- completitud estructural;
- presencia de bundles;
- presencia de campos;
- completitud de provenance;
- visibilidad de supuestos;
- visibilidad de incertidumbre;
- estatus de validacion declarado;
- cantidad de inputs;
- pase o fallo de casos de prueba;
- e indicadores acotados de cobertura.

#### 10.4.2 Que no debe fingirse como 100 por ciento matematico

Lo siguiente no debe representarse como resuelto por computo pleno en Fase 1:

- si una tension operativa es real o solo plausible;
- si una organizacion es “buena” o “mala” en un sentido fuerte;
- si un arquetipo es el unico correcto bajo evidencia escasa;
- si ya puede emitirse una recomendacion final;
- si la causalidad esta cerrada.

En Fase 1, eso debe permanecer representado como:

- hipotesis;
- candidate set;
- supuesto;
- uncertainty marker;
- o profile acotado.

Ejemplo:
si un warehouse podria ser logistics-heavy o refrigerated-light, el sistema no debe forzar una clasificacion exacta para parecer mas objetivo. Debe preservar dos arquetipos plausibles, hacer explicitas las condiciones y exponer incertidumbre.

### 10.5 Gates binarios obligatorios

Los siguientes gates son binarios. Cada uno evalua `1` para pase o `0` para fallo.

#### G1. `facility_prior_exists`

**Que verifica**  
Si existe un objeto estructurado `facility_prior`.

**Por que importa**  
La Fase 1 no puede cerrar sobre narrativa sola.

**Ejemplo simple de pase**  
Existe un objeto estructurado con campos definidos y secciones de bundles.

**Ejemplo simple de fallo**  
Solo existe un parrafo o summary libre.

#### G2. `mandatory_bundles_complete`

**Que verifica**  
Si todos los bundles obligatorios estan presentes:

- `normalized_facility_profile`
- `candidate_archetype_bundle`
- `climate_energy_context_bundle`
- `benchmark_bundle`
- `jurisdiction_bundle`
- `regulatory_flag_bundle`
- `prior_assumptions_pack`
- `uncertainty_markers`

**Por que importa**  
El prior es invalido si falta una capa estructural obligatoria.

**Ejemplo simple de pase**  
Los ocho bundles estan presentes.

**Ejemplo simple de fallo**  
Falta `benchmark_bundle` aunque el resto exista.

#### G3. `inputs_max_10`

**Que verifica**  
Si el prior puede generarse con maximo diez inputs minimos obligatorios.

**Por que importa**  
La Fase 1 es un motor temprano de prior estructurado, no un intake pesado.

**Ejemplo simple de pase**  
Diez o menos inputs obligatorios son suficientes.

**Ejemplo simple de fallo**  
Se requieren diecisiete preguntas antes de generar.

#### G4. `traceability_minimum_met`

**Que verifica**  
Si cada componente principal tiene `source_dependencies` o provenance minima equivalente.

**Por que importa**  
La estructura no trazable no es admisible.

**Ejemplo simple de pase**  
Las capas de clima, benchmark y regulacion identifican sus dependencias de fuente.

**Ejemplo simple de fallo**  
Aparece una climate zone pero no puede rastrearse su fuente.

#### G5. `assumptions_explicit`

**Que verifica**  
Si los supuestos estan declarados explicitamente.

**Por que importa**  
El cierre no declarado es una alucinacion oculta por arquitectura.

**Ejemplo simple de pase**  
Se asume horario comercial y eso queda declarado.

**Ejemplo simple de fallo**  
Se inserta silenciosamente un horario comercial.

#### G6. `uncertainty_explicit`

**Que verifica**  
Si la incertidumbre esta representada explicitamente.

**Por que importa**  
La Fase 1 debe exponer subdeterminacion en lugar de suprimirla.

**Ejemplo simple de pase**  
La incertidumbre de arquetipo queda visible.

**Ejemplo simple de fallo**  
El output presenta un arquetipo incierto como si estuviera cerrado.

#### G7. `non_verificatory_state_explicit`

**Que verifica**  
Si la salida esta marcada explicitamente como no verificatoria y no diagnostica.

**Por que importa**  
La Fase 1 no debe derivar semanticamente hacia verificacion o diagnostico fuerte.

**Ejemplo simple de pase**  
Validation status y critical limits marcan explicitamente el prior como Decision-grade y no verificatorio.

**Ejemplo simple de fallo**  
El prior dice o implica “el sitio esta mal operado” como hecho resuelto.

#### G8. `llm_not_structural_dependency`

**Que verifica**  
Si el prior evita depender del LLM por si solo para llenar huecos estructurales criticos.

**Por que importa**  
El LLM no es soberano y no puede servir como motor estructural oculto de la Fase 1.

**Ejemplo simple de pase**  
Las hipotesis de sistemas derivan de facility type, sector, logica de arquetipo, supuestos trazables o input explicito del usuario.

**Ejemplo simple de fallo**  
Aparece una caldera solo porque “el modelo cree que probablemente hay una caldera”.

#### G9. `candidate_archetypes_nonempty`

**Que verifica**  
Si existe al menos un candidate archetype set plausible.

**Por que importa**  
Sin estructura de arquetipos, el prior no restringe comparabilidad de forma material.

**Ejemplo simple de pase**  
Se producen dos arquetipos plausibles para un warehouse sparse.

**Ejemplo simple de fallo**  
`candidate_archetypes` esta vacio.

#### G10. `regulatory_or_contextual_relevance_present`

**Que verifica**  
Si existe relevancia regulatoria aplicable o, cuando no aplica regulacion fuerte, contexto jurisdiccional explicito.

**Por que importa**  
La Fase 1 debe anclar la instalacion en contexto territorial incluso cuando no salta una regla fuerte.

**Ejemplo simple de pase**  
El caso no tiene performance standard directo, pero si tiene jurisdiction bundle y flags contextuales de primer orden.

**Ejemplo simple de fallo**  
No se adjunta contexto regulatorio ni jurisdiccional.

#### G11. `system_layer_present`

**Que verifica**  
Si existe una capa plausible de `SystemAsset` o `system_asset_hypothesis`.

**Por que importa**  
Un prior sin plausibilidad de sistemas es demasiado delgado para soportar inferencia posterior.

**Ejemplo simple de pase**  
Aparecen HVAC, lighting y ventilation como sistemas comunes plausibles para un office.

**Ejemplo simple de fallo**  
No existe systems layer.

#### G12. `operational_or_actionability_layer_present`

**Que verifica**  
Si existe al menos una de las capas siguientes:

- `operational_tension_hypothesis`
- `organization_actionability_profile`
- `improvement_constraint_profile`

**Por que importa**  
El prior debe incluir al menos una capa de realismo operativo o de accionabilidad.

**Ejemplo simple de pase**  
Estan presentes actionability profile e improvement constraints.

**Ejemplo simple de fallo**  
El prior contiene solo contexto y benchmarks, sin realismo operativo ni de accionabilidad.

#### G13. `sparse_case_pass`

**Que verifica**  
Si el sistema sigue produciendo un prior estructurado bajo muchos valores `unknown`.

**Por que importa**  
Si el engine no tolera input escaso, falla la funcion central de la Fase 1.

**Ejemplo simple de pase**  
El sparse case produce un prior de menor resolucion, pero estructurado, con supuestos e incertidumbre visibles.

**Ejemplo simple de fallo**  
El sparse case devuelve bundles vacios o colapsa a narrative fallback.

#### G14. `building_case_pass`

**Que verifica**  
Si el sistema pasa el caso building / compliance obligatorio.

**Por que importa**  
Un engine de Fase 1 que no puede manejar un caso building basico no esta listo operativamente.

**Ejemplo simple de pase**  
El caso NYC office produce candidate archetypes, benchmarks, regulacion, systems layer e incertidumbre.

**Ejemplo simple de fallo**  
El caso building no produce regulatory flags o no produce archetypes.

#### G15. `industrial_case_pass`

**Que verifica**  
Si el sistema pasa el caso industrial / reliability obligatorio.

**Por que importa**  
La Fase 1 no puede quedar silenciosamente limitada a edificios.

**Ejemplo simple de pase**  
El caso food processing produce archetypes proceso + refrigeracion, systems layer plausible, tensiones de continuidad y restricciones de uptime.

**Ejemplo simple de fallo**  
El caso industrial degenera en logica tipo office o no produce plausibilidad de sistemas.

#### 10.5.1 Gates criticos y no compensables

Los siguientes gates son criticos y no compensables:

- G1
- G2
- G3
- G4
- G5
- G6
- G7
- G8
- G13
- G14
- G15

Si cualquiera de estos falla, la Fase 1 no cierra.

### 10.6 Scores auxiliares computables

Los scores auxiliares miden calidad y madurez. No reemplazan gates.

#### S1. `bundle_completeness_score`

\[
S1 = \frac{\text{mandatory bundles present}}{\text{mandatory bundles required}}
\]

**Que mide**  
Completitud de bundles.

**Por que sirve**  
Cuantifica cobertura estructural.

**Ejemplo simple**  
Si hay 7 de 8 bundles obligatorios, `S1 = 0.875`.

**Por que no reemplaza gates**  
La ausencia de un bundle critico sigue fallando G2.

#### S2. `assumption_coverage_score`

\[
S2 = \frac{\text{components with explicit assumptions}}{\text{components requiring assumptions}}
\]

**Que mide**  
Visibilidad de cobertura de supuestos.

**Por que sirve**  
Cuantifica cuanto del cierre es honesto en lugar de silencioso.

**Ejemplo simple**  
Si 5 componentes requieren supuestos y solo 3 los declaran, `S2 = 0.60`.

**Por que no reemplaza gates**  
Un score moderado no salva el fallo de G5.

#### S3. `traceability_completeness_score`

\[
S3 = \frac{\text{major components with provenance}}{\text{major components total}}
\]

**Que mide**  
Completitud de provenance.

**Por que sirve**  
Cuantifica madurez de trazabilidad.

**Ejemplo simple**  
Si 9 de 10 componentes principales tienen provenance, `S3 = 0.90`.

**Por que no reemplaza gates**  
Fallar trazabilidad critica sigue fallando G4.

#### S4. `uncertainty_visibility_score`

\[
S4 = \frac{\text{uncertain components with visible marker}}{\text{uncertain components total}}
\]

**Que mide**  
Que tan consistentemente se expone la incertidumbre.

**Por que sirve**  
Cuantifica proporcionalidad semantica.

**Ejemplo simple**  
Si 4 componentes inciertos existen y 3 quedan marcados explicitamente, `S4 = 0.75`.

**Por que no reemplaza gates**  
Si falta incertidumbre donde debe existir, G6 sigue fallando.

#### S5. `input_efficiency_score`

\[
S5 = 1 - \frac{\max(0,\text{inputs used}-10)}{10}
\]

Truncado al intervalo \([0,1]\).

**Que mide**  
Eficiencia de intake.

**Por que sirve**  
Cuantifica si el engine sigue siendo compatible con el MVP.

**Ejemplos simples**
- 10 inputs → `1.0`
- 12 inputs → `0.8`
- 20 inputs → `0.0`

**Por que no reemplaza gates**  
Si el sistema requiere mas de 10 inputs obligatorios, G3 falla de todos modos.

#### S6. `archetype_resolution_score`

Una formulacion simple admisible es:

\[
S6 = \max\left(0, 1 - \frac{\max(0,\text{candidate archetypes}-3)}{6}\right)
\]

Truncado a \([0,1]\).

**Que mide**  
Restriccion razonable sin falsa exactitud.

**Por que sirve**  
Penaliza priors que quedan demasiado poco restringidos.

**Ejemplos simples**
- 2 candidate archetypes → score alto
- 3 candidate archetypes → aceptable
- 9 candidate archetypes → score muy bajo

**Por que no reemplaza gates**  
Un score alto no demuestra que los arquetipos elegidos sean “correctos”; solo refleja resolucion acotada.

#### S7. `unknown_burden_score`

\[
S7 = 1 - \frac{\text{critical fields marked unknown}}{\text{critical fields total}}
\]

**Que mide**  
Cuanto del prior permanece sin resolver en campos criticos.

**Por que sirve**  
Cuantifica la carga informacional restante.

**Ejemplo simple**  
Si 4 de 10 campos criticos quedan `unknown`, `S7 = 0.60`.

**Por que no reemplaza gates**  
Un sparse case puede seguir pasando con menor `S7` si la incertidumbre es honesta y la estructura se preserva.

#### S8. `actionability_readiness_score`

\[
S8 = \frac{\text{layers present among operational, actionability, constraints}}{3}
\]

**Que mide**  
Presencia de realismo operativo y de accionabilidad basico.

**Por que sirve**  
Cuantifica si el prior supera la pura descripcion contextual.

**Ejemplos simples**
- 2 de 3 capas presentes → `0.67`
- 3 de 3 capas presentes → `1.0`

**Por que no reemplaza gates**  
Un `S8` alto no rescata ausencia de provenance o incertidumbre.

### 10.7 Regla de no compensacion

La regla de no compensacion es estricta:

> Un score alto no compensa el fallo de una condicion critica. Un prior detallado, atractivo o estructuralmente rico no cierra la Fase 1 si le faltan trazabilidad minima, supuestos explicitos, incertidumbre visible, limites no verificatorios explicitos o robustez minima en casos de prueba obligatorios.

Ejemplos simples:

- aunque el prior tenga 95 por ciento de campos llenos, si no explicita supuestos, no pasa;
- aunque el benchmark bundle sea excelente, si falla el sparse case, la Fase 1 no cierra;
- aunque el caso industrial sea fuerte, si falta provenance, el cierre queda bloqueado.

### 10.8 Casos de prueba obligatorios

Los siguientes casos de prueba son obligatorios.

#### Test A — Building / compliance-driven

**Input**
- ubicacion: NYC
- tipo de instalacion: office
- tamano: 120,000 sq ft
- vintage: 1985
- horario: commercial hours
- energia: electricity + gas
- sistemas conocidos: HVAC, lighting, BMS unknown
- preocupacion principal: compliance

**Comportamiento minimo esperado**
- candidate archetypes plausibles;
- benchmark context util;
- regulatory flags plausibles;
- systems layer comun;
- tensiones operativas plausibles;
- incertidumbre visible.

#### Test B — Industrial / reliability-driven

**Input**
- ubicacion: zona industrial en Colombia
- tipo de instalacion: food processing
- horario: 24/7
- energia: electricidad + refrigeration + motors
- vintage: 2000s
- sistemas conocidos: refrigeration, motors, boilers unknown
- preocupacion principal: cost + reliability

**Comportamiento minimo esperado**
- arquetipos proceso + refrigeracion;
- benchmark context razonable;
- systems layer plausible;
- tensiones de mantenimiento, control y continuidad;
- constraints de uptime y proceso;
- sin fingir diagnostico.

#### Test C — Sparse data case

**Input**
- ciudad
- tipo de instalacion
- tamano
- uso principal
- preocupacion principal
- multiples campos criticos `unknown`

**Comportamiento minimo esperado**
- prior todavia util;
- menor resolucion;
- mas supuestos explicitos;
- mayor incertidumbre visible;
- estructura preservada.

Un sparse case no es fracaso si la fuerza semantica disminuye y la incertidumbre aumenta proporcionalmente.

### 10.9 Regla de pase, no pase y rebuild

#### 10.9.1 Condicion minima de pase

El pase minimo de Fase 1 requiere:

- todos los gates criticos = `1`.

#### 10.9.2 Calidad suficiente para avanzar

Ademas de pasar todos los gates criticos, aplican los siguientes umbrales minimos de score:

- \(S1 \ge 0.90\)
- \(S2 \ge 0.80\)
- \(S3 \ge 0.90\)
- \(S4 \ge 0.80\)
- \(S5 = 1.00\)
- \(S6 \ge 0.50\)
- \(S7 \ge 0.60\)
- \(S8 \ge 0.67\)

Estos umbrales no sustituyen gates criticos. Son indicadores minimos de madurez una vez presente la estructura critica.

#### 10.9.3 Estado `Rebuild Required`

`Rebuild Required` aplica cuando:

- algunos gates criticos pasan;
- pero el output falla uno o mas thresholds de score de manera material y la Fase 1 aun no es apta para cerrar;
- o uno o mas casos de prueba obligatorios fallan aunque alguna estructura exista.

Ejemplos simples:
- el prior existe, pero carga demasiados `unknown` en campos criticos;
- el building case pasa pero el sparse case falla;
- los bundles estan presentes pero la provenance sigue incompleta.

### 10.10 Que seria un falso cierre de la Fase 1

Lo siguiente no constituye cierre:

- “el documento ya esta escrito”;
- “ya tenemos muchas fuentes”;
- “ya tenemos dashboards”;
- “ya tenemos un summary convincente”;
- “ya tenemos un prior, pero requiere 18 preguntas y falla el sparse case”.

Todo eso es falso cierre porque no satisface el gate de aceptacion.

### 10.11 Que habilita exactamente la Fase 1 hacia Fase 2

La Fase 1 solo puede entregar a Fase 2:

- `facility_prior`
- bundles estructurados
- candidate archetypes
- assumptions pack
- uncertainty markers
- source dependencies
- systems layer plausible
- operational tension hypotheses
- actionability y constraint realism basico

La Fase 1 no entrega:

- evidencia local fuerte;
- verificacion;
- diagnostico final;
- causalidad cerrada;
- recomendacion final.

### 10.12 Criterio final de cierre de la Fase 1

La regla final de cierre es por tanto:

> El cierre de la Fase 1 no dependera de juicio subjetivo global. Dependera de un gate de aceptacion computable compuesto por condiciones binarias obligatorias y metricas auxiliares no compensatorias.

> No todo el sistema puede reducirse a una sola formula. Pero el gate de aceptacion de la Fase 1 puede volverse lo suficientemente computable para limitar sesgo, hacer explicitos los criterios de pase y evitar cierres por impresion.

> La Fase 1 queda formalmente cerrada cuando el Public Data Engine puede transformar fuentes publicas admitidas e inputs minimos en un `facility_prior` estructurado, trazable, no verificatorio y operacionalmente util bajo criterios computables explicitos, sin contradiccion epistemologica, sin sobreingenieria y sin dependencia analitica soberana del LLM.

## 11. Tipologia de fuentes publicas a considerar en desarrollo posterior de la Fase 1

Las siguientes categorias de fuente son candidatas admisibles para desarrollo posterior de la Fase 1 solo si pasan los gates definidos arriba:

- sistemas publicos de clasificacion sectorial y subsectorial;
- registros publicos de instalaciones industriales;
- benchmarks publicos de intensidad energetica y estudios de referencia;
- registros publicos de emisiones y cumplimiento;
- estructuras publicas de tarifas y clases de rate;
- climate zones y weather normals relevantes para el contexto;
- referencias publicas de arquetipos operativos o de edificio;
- documentos jurisdiccionales de aplicabilidad regulatoria;
- metadata publica de combustibles, red e infraestructura;
- literatura publica de benchmarking con relevancia acotada;
- y capas geoespaciales o administrativas canonicas.

## 12. Tipos de objetos estructurados que la Fase 1 debe producir

La Fase 1 debe converger hacia las siguientes familias de objeto:

- `facility_stub`
- `jurisdiction_bundle`
- `sector_bundle`
- `benchmark_bundle`
- `regulatory_flag_bundle`
- `archetype_candidate_set`
- `prior_assumption_set`
- `uncertainty_register`
- `source_trace_record`
- `dataset_version_record`
- `join_key_registry`
- `facility_prior`

## 13. Descripcion formal del `facility_prior`

El `facility_prior` es el objeto rector de salida de la Fase 1.

Es un prior acotado, trazable y de Decision-grade sobre la instalacion candidata construido desde input escaso del usuario mas contexto publico admisible. No expresa verdad verificada de sitio. Expresa el mejor prior publico restringido que el framework puede construir legitima y disciplinadamente antes de etapas mas profundas.

Su funcion es:

- acotar interpretaciones plausibles;
- identificar arquetipos candidatos;
- adjuntar familias de benchmark relevantes;
- adjuntar contexto jurisdiccional y regulatorio;
- registrar prior assumptions explicitamente;
- y definir limites de incertidumbre que fases posteriores deben resolver.

Su estatus minimo es:

- Decision-grade solamente;
- explicitamente no verificatorio;
- admisible solo como contexto previo acotado;
- e invalido si se usa como diagnostico fuerte o resultado de verificacion.

## 14. Frontera entre la Fase 1 y la Fase 2

La Fase 1 termina donde termina la construccion del prior publico acotado. La Fase 2 comienza donde inicia la construccion analitica especifica de instalacion.

La Fase 2 puede consumir el `facility_prior`, pero no heredarlo como verdad. Lo hereda como estructura inicial restringida. Todo claim mas fuerte en Fase 2 debe volver a ganarse mediante motores formales, evidencia especifica de instalacion, calculo explicito y logica de admisibilidad mas estricta.

## 15. Frontera entre la Fase 1 y la Fase 4

La Fase 1 no tiene autoridad para emitir outputs equivalentes a material de la Fase 4.

La Fase 4 es la capa visible downstream donde outputs, recomendaciones o artifacts de mayor peso circulan bajo gobernanza mas estricta. La Fase 1 solo puede alimentar esa capa de manera indirecta, a traves de fases posteriores que eleven soporte y reduzcan incertidumbre.

## 16. Riesgo principal: dataset sprawl

El principal failure mode de la Fase 1 es dataset sprawl.

Dataset sprawl ocurre cuando:

- los datos publicos se acumulan mas rapido de lo que se gobiernan;
- los objetos entran sin rol downstream claro;
- la abundancia documental se confunde con fuerza inferencial;
- la superficie de ingesta crece sin aumentar poder restrictivo;
- o el LLM se convierte en interprete practico de masa de datos subgobernada.

No es primero un problema de storage. Es un failure mode de control epistemologico.

## 17. Regla de recorte MVP

La regla MVP de la Fase 1 es severa por diseno:

Solo se conserva el conjunto minimo de familias de fuente y objetos estructurados necesarios para producir un primer `facility_prior` materialmente util a partir de inputs escasos.

Si un input, dataset, clase de fuente, familia de benchmark u objeto no es necesario para ese resultado, debe quedar fuera del perimetro MVP.

## 18. Criterio de terminado de la Fase 1

La Fase 1 se considera terminada cuando se cumplen todas las condiciones siguientes:

1. El perimetro de datos publicos fue cerrado bajo las reglas de 1A.
2. Las familias de fuente admitidas estan mapeadas, versionadas y trazables.
3. Los join keys y el esquema maestro son lo suficientemente estables para construccion repetible de priors.
4. El sistema puede tomar aproximadamente diez inputs materialmente relevantes del usuario y construir un primer `facility_prior`.
5. Ese `facility_prior` es coherente, acotado, trazable y explicitamente no verificatorio.
6. El output es materialmente util para restriccion downstream sin cruzar hacia verificacion, diagnostico fuerte ni recomendacion de alto peso.
7. El sistema demuestra resistencia a dataset sprawl bajo la regla anti-sprawl.
