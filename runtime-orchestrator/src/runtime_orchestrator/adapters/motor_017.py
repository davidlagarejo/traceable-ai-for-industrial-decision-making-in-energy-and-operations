"""Adapter for motor_017 — Document Rendering Engine (XeLaTeX).

Generates a governed report document using the
IPLeiria Thesis Template (Polytechnic University of Leiria) as the base
document class, then compiles it with xelatex.

Template: Polytechnic_University_of_Leiria_Thesis_Template/
Compiler: xelatex (two passes for correct ToC and cross-references)

Output: output/{render_job_id}/{case_slug}_{document_slug}.pdf
"""
from __future__ import annotations

import base64
import logging
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

from ..output_taxonomy import CANONICAL_VISIBLE_OUTPUT_MODES, canonicalize_output_mode
from .base import BaseMotorAdapter

_TEMPLATE_DIR = Path(__file__).resolve().parents[3] / \
    "Polytechnic_University_of_Leiria_Thesis_Template"
_OUTPUT_DIR   = Path(__file__).resolve().parents[3] / "output"

_SECTION_TITLE_ES = {
    "Framework Context & Executive Brief": "Contexto del Framework y Resumen Ejecutivo",
    "Executive Structural Thesis": "Tesis Estructural Ejecutiva",
    "Executive Structural Brief": "Resumen Estructural Ejecutivo",
    "Reframed Problem": "Problema Reencuadrado",
    "Dominant Structural Contradiction": "Contradicción Estructural Dominante",
    "What the Client Thinks the Problem Is": "Lo que el Cliente Cree que es el Problema",
    "What the System Thinks the Problem Might Actually Be": "Lo que el Sistema Cree que el Problema Podría Ser Realmente",
    "Operational Identity": "Identidad Operacional",
    "System Abstraction Snapshot": "Fotografía de la Abstracción del Sistema",
    "System Abstraction Map": "Mapa de Abstracción del Sistema",
    "Dominant Variables": "Variables Dominantes",
    "Evidence State by Layer": "Estado de Evidencia por Capa",
    "Cross-Layer Contradictions": "Contradicciones entre Capas",
    "Scenario Space": "Espacio de Escenarios",
    "Financial Exposure Under Uncertainty": "Exposición Financiera bajo Incertidumbre",
    "Peer / Competitive Comparison": "Comparación con Pares / Competitiva",
    "Competitive / Peer Comparison": "Comparación Competitiva / con Pares",
    "Conditional Redesign Pathway": "Ruta Condicional de Rediseño",
    "Conditional Redesign Pathways": "Rutas Condicionadas de Rediseño",
    "Minimum Evidence for Discrimination": "Evidencia Mínima para Discriminación",
    "TAD — Immediate Action Priority": "TAD — Prioridad de Acción Inmediata",
    "TAD — Action Priority": "TAD — Prioridad de Acción",
    "Claim Permissions / What Not To Do": "Permisos de Claims / Qué No Hacer",
    "What Not To Do Yet": "Qué No Hacer Aún",
    "Claim Permission Matrix": "Matriz de Permisos de Claims",
    "Source Traceability": "Trazabilidad de Fuentes",
    "System Consistency Check": "Chequeo de Consistencia del Sistema",
    "Blocking Conflicts": "Conflictos Bloqueantes",
    "Inference Case Map": "Mapa de Casos de Inferencia",
    "Energy Profile & Normative Constraints": "Perfil Energético y Restricciones Normativas",
    "Tension Map": "Mapa de Tensiones",
    "Validation Architecture": "Arquitectura de Validación",
    "Conditional Opportunities": "Oportunidades Condicionadas",
    "Financial Context": "Contexto Financiero",
    "Governance Status": "Estado de Gobernanza",
    "Evidence & Source Traceability": "Trazabilidad de Evidencia y Fuentes",
    "Asset Context Prior and Raw Source Map": "Prior de Contexto del Activo y Mapa Bruto de Fuentes",
    "Detailed Validation Questions": "Preguntas Detalladas de Validación",
    "Issuer Financial Context (Subordinated)": "Contexto Financiero del Emisor (Subordinado)",
    "Executive Decision-Admissibility Brief": "Resumen Ejecutivo de Admisibilidad de Decisión",
    "Investment Uncertainty Map": "Mapa de Incertidumbre de Inversión",
    "Minimum Evidence Pack": "Paquete Mínimo de Evidencia",
    "Scenario Space Under Current Uncertainty": "Espacio de Escenarios Bajo la Incertidumbre Actual",
    "Asset Context Readiness": "Estado de Preparación del Contexto del Activo",
    "Regulatory / Normative Screening": "Screening Regulatorio / Normativo",
    "TAD — Decision-Admissibility Layer": "TAD — Capa de Admisibilidad de Decisión",
    "Inference Case Register": "Registro de Casos de Inferencia",
    "Next Best Questions": "Mejores Preguntas Siguientes",
    "Governance Status": "Estado de Gobernanza",
    "Evidence & Source Traceability": "Trazabilidad de Evidencia y Fuentes",
    "Public Source Coverage Table": "Tabla de Cobertura de Fuentes Públicas",
    "Report Type Classifier Table": "Tabla del Clasificador de Tipo de Reporte",
    "Industry Adaptation Table": "Tabla de Adaptación Sectorial",
    "Case Adaptation Memo": "Memo de Adaptación del Caso",
    "Evidence Maturity & Claim Permission Matrix": "Madurez de Evidencia y Matriz de Permisos de Claims",
}

_SECTION_TITLE_ES_NORMALIZED = {
    str(key).strip().lower(): value
    for key, value in _SECTION_TITLE_ES.items()
}

_STRUCTURED_LABELS_ES = {
    "Framework": "Framework",
    "Document Type": "Tipo de Documento",
    "Case ID": "ID del Caso",
    "Date": "Fecha",
    "Analyst": "Analista",
    "Subject": "Sujeto",
    "Owner": "Propietario",
    "Asset Class": "Clase de Activo",
    "Landmark": "Estatus de Hito",
    "Blocking Conflicts": "Conflictos Bloqueantes",
    "Open Tensions": "Tensiones Abiertas",
    "Inference Cases": "Casos de Inferencia",
    "Opportunities": "Oportunidades",
    "Reasoning Path": "Ruta de Razonamiento",
    "Problem Frame": "Marco del Problema",
    "Mode Candidates": "Modos Candidatos",
    "Primary-Eligible": "Elegible como Primario",
    "Reframed Problem": "Problema Reencuadrado",
    "Dominant Conflict": "Conflicto Dominante",
    "Visible Output Mode": "Modo Visible de Salida",
    "Leading Structural Mode": "Modo Estructural Líder",
    "Dominant Risk": "Riesgo Dominante",
    "Priority Action": "Acción Prioritaria",
    "Not Admissible": "No Admisible",
    "Stated Problem": "Problema Declarado",
    "Why Reframe": "Por Qué Reencuadrar",
    "Strategic Risk": "Riesgo Estratégico",
    "Structural Action": "Acción Estructural",
    "Constraint": "Restricción",
    "Conflict": "Conflicto",
    "Layers Involved": "Capas Involucradas",
    "Evidence State": "Estado de Evidencia",
    "Why It Matters": "Por Qué Importa",
    "What Confirms It": "Qué lo Confirma",
    "What Falsifies It": "Qué lo Falsaría",
    "Potential Redesign": "Rediseño Potencial",
    "Scenario": "Escenario",
    "Plausibility": "Plausibilidad",
    "Financial Meaning": "Significado Financiero",
    "Evidence Needed": "Evidencia Necesaria",
    "Evidence Link": "Vínculo de Evidencia",
    "Decision Front": "Frente de Decisión",
    "Structural Assumption": "Supuesto Estructural",
    "Exposure If Wrong": "Exposición si es Incorrecto",
    "Allowed Output": "Salida Permitida",
    "Prohibited Output": "Salida Prohibida",
    "Dimension": "Dimensión",
    "Subject Asset": "Activo Analizado",
    "Peer / Benchmark": "Par / Benchmark",
    "Difference": "Diferencia",
    "Interpretation": "Interpretación",
    "Better Performer": "Actor con Mejor Desempeño",
    "What They Do Better": "Qué Hacen Mejor",
    "Structural Advantage": "Ventaja Estructural",
    "Transferability": "Transferibilidad",
    "Peer Type": "Tipo de Par",
    "What It Proves": "Qué Demuestra",
    "What It Does Not Prove": "Qué No Demuestra",
    "Hypothesis": "Hipótesis",
    "Trigger Hypothesis": "Hipótesis Gatillo",
    "Conflict Resolved": "Conflicto que Resuelve",
    "Economic Logic": "Lógica Económica",
    "If Confirmed": "Si se Confirma",
    "Redesign Direction": "Dirección de Rediseño",
    "If Falsified": "Si se Falsifica",
    "Kill Condition": "Condición de Muerte",
    "Next Evidence": "Siguiente Evidencia",
    "Rival Hypotheses": "Hipótesis Rivales",
    "Minimum Evidence": "Evidencia Mínima",
    "Source": "Fuente",
    "Unlocks": "Desbloquea",
    "Action": "Acción",
    "Status": "Estado",
    "Why": "Por Qué",
    "Financial Exposure": "Exposición Financiera",
    "Maps To": "Mapea a",
    "Prohibited Action": "Acción Prohibida",
    "Claim": "Claim",
    "Permission": "Permiso",
    "Evidence Required": "Evidencia Requerida",
    "Current Evidence": "Evidencia Actual",
    "Allowed Language": "Lenguaje Permitido",
    "Forbidden Language": "Lenguaje Prohibido",
    "Check": "Chequeo",
    "Passed": "Aprobado",
    "Failure": "Falla",
    "Severity": "Severidad",
    "Blocking": "Bloqueante",
    "Final Consistency Status": "Estado Final de Consistencia",
    "Critical Failure Count": "Cantidad de Fallas Críticas",
    "Validator Owner": "Motor Validador",
    "Case Finding": "Hallazgo del Caso",
    "Current bottlenecks": "Cuellos de botella actuales",
    "Supporting Sources": "Fuentes de Soporte",
    "Assumptions": "Supuestos",
    "Falsification Condition": "Condición de Falsación",
    "Minimum Evidence Required": "Evidencia Mínima Requerida",
    "Allowed Use": "Uso Permitido",
    "Prohibited Use": "Uso Prohibido",
    "Statement": "Declaración",
    "Linked Conflicts": "Conflictos Vinculados",
    "Linked Frames": "Marcos Vinculados",
    "Layer": "Capa",
    "Observed Support": "Soporte Observado",
    "Open Questions": "Preguntas Abiertas",
    "Structural Risk": "Riesgo Estructural",
    "Decision unlock": "Desbloqueo de Decisión",
    "Action Family": "Familia de Acción",
    "Claim Family": "Familia de Claim",
    "Conflict Type": "Tipo de Conflicto",
    "Blocking Status": "Estado de Bloqueo",
    "Conflict Statement": "Declaración del Conflicto",
    "Determination Status": "Estado de Determinación",
    "Description": "Descripción",
    "Used For": "Usado Para",
    "Source Routing Status": "Estado de Ruteo de Fuentes",
    "Template Contamination Failure": "Falla de Contaminación de Template",
}

_STRUCTURED_TEXT_REPLACEMENTS_ES = [
    ("This Compliance / Investment Screening Brief is a governed materialization of Decision Core outputs.", "Este Informe de Screening de Cumplimiento / Inversión es una materialización gobernada de los outputs del Núcleo de Decisión."),
    ("It remains Decision-grade unless and until independent evidence upgrades the underlying objects.", "Permanece en grado de decisión hasta que evidencia independiente eleve los objetos subyacentes."),
    ("No statement constitutes a verified diagnosis, compliance determination, or investment recommendation.", "Ninguna afirmación constituye un diagnóstico verificado, una determinación de cumplimiento o una recomendación de inversión."),
    ("All claims remain conditional on validation requirements and", "Todos los claims permanecen condicionados por los requisitos de validación y"),
    ("Case Identification", "Identificación del Caso"),
    ("Decision State", "Estado de Decisión"),
    ("Structural Read", "Lectura Estructural"),
    ("Active Inference Cases -- Urgency Ranking", "Casos de Inferencia Activos -- Ranking de Urgencia"),
    ("Epistemic Grade", "Grado Epistemológico"),
    ("EPISTEMIC STATE", "ESTADO EPISTÉMICO"),
    ("SCREENING ADMISSIBLE", "SCREENING ADMISIBLE"),
    ("entity-level support only", "solo soporte a nivel entidad"),
    ("NOT OBSERVED", "NO OBSERVADO"),
    ("Current bottlenecks", "Cuellos de botella actuales"),
    ("No cross-layer contradictions were produced.", "No se produjeron contradicciones entre capas."),
    ("Plausible but unsupported", "Plausible pero no respaldado"),
    ("Not ruled out", "No descartado"),
    ("Currently dominant", "Actualmente dominante"),
    ("Plausible", "Plausible"),
    ("Request discriminating evidence pack", "Solicitar paquete de evidencia discriminante"),
    ("This brief remains bounded by the current evidence state and should not be read as verification-grade.", "Este informe permanece acotado por el estado actual de la evidencia y no debe leerse como de grado de verificación."),
    ("Compliance burden may sit with the owner while dominant loads and economic capture remain partly tenant-driven or contractually unresolved.", "La carga de compliance puede recaer sobre el propietario mientras que las cargas dominantes y la captura económica sigan estando parcialmente impulsadas por inquilinos o contractualmente no resueltas."),
    ("Retrofit CAPEX may reduce site energy without improving owner economics because dominant loads sit in tenant space or outside owner control.", "El CAPEX de retrofit puede reducir la energía del sitio sin mejorar la economía del propietario porque las cargas dominantes pueden estar en espacios de inquilinos o fuera del control del propietario."),
    ("Confirms that the target is a bounded operating asset rather than issuer context.", "Confirma que el objetivo es un activo operativo acotado y no solo contexto del emisor."),
    ("Savings claim for a candidate measure or operational change.", "Claim de savings para una medida candidata o un cambio operativo."),
    ("Directional economics or indicative ROI framing.", "Economía direccional o framing indicativo de ROI."),
    ("Preliminary ROI range with explicit low-confidence caveats.", "Rango preliminar de ROI con caveats explícitos de baja confianza."),
    ("Scenario-based ROI suitable for stronger decision framing.", "ROI basado en escenarios apto para un framing de decisión más fuerte."),
    ("Evidence request; Diligence scoping; Validation sequencing", "Solicitud de evidencia; Alcance de diligencia; Secuenciación de validación"),
    ("Investment recommendation; Compliance conclusion; Savings estimate; Bankability claim", "Recomendación de inversión; Conclusión de compliance; Estimación de savings; Claim de bancabilidad"),
    ("Need to distinguish whether the problem is efficiency, control-boundary design, tenant allocation, or penalty-avoidance strategy.", "Necesitamos distinguir si el problema real es eficiencia, diseño de la frontera de control, asignación a inquilinos o estrategia de evitación de penalidades."),
    ("The visible building question may collapse three different issues: owner control, tenant load allocation, and compliance-driven capital exposure.", "La pregunta visible sobre el edificio puede colapsar tres asuntos distintos: control del propietario, asignación de carga a inquilinos y exposición de capital impulsada por compliance."),
    ("Owner capital can be aimed at the wrong load boundary or the wrong compliance pathway.", "El capital del propietario puede apuntar a la frontera de carga equivocada o a la ruta de compliance equivocada."),
    ("Conditional peer comparator:", "Comparador condicional:"),
    ("Archetypal peer pattern:", "Patrón de par arquetípico:"),
    ("conditional_peer_pattern", "patrón_de_par_condicional"),
    ("archetypal_peer_pattern", "patrón_de_par_arquetípico"),
    ("Uses submetering and green-lease discipline to separate tenant and owner loads, tunes the BMS against actual occupancy, and frames LL97 as a control-and-contract problem before assuming retrofit savings.", "Usa submedición y disciplina de green leases para separar cargas de inquilinos y del propietario, ajusta el BMS contra la ocupación real y trata LL97 como un problema de control y contrato antes de asumir savings de retrofit."),
    ("The peer aligns metering, owner control, and compliance strategy more tightly than an unresolved owner/tenant boundary allows.", "Ese par alinea medición, control del propietario y estrategia de compliance de manera más estrecha de lo que permite una frontera propietario/inquilino todavía no resuelta."),
    ("This can change whether capital logic is retrofit savings, penalty avoidance, or contractual redesign.", "Esto puede cambiar si la lógica de capital es savings de retrofit, evitación de penalidades o rediseño contractual."),
    ("Medium if the subject asset can validate owner control boundary and implement lease / metering changes.", "Media si el activo analizado puede validar la frontera de control del propietario e implementar cambios de lease / medición."),
    ("It proves which control-boundary pattern would make peer screening decision-useful.", "Demuestra qué patrón de frontera de control haría útil el screening con pares para la decisión."),
    ("It does not prove that a named real competitor outperforms the asset or that savings are owner-capturable here.", "No demuestra que un competidor real identificado supere al activo ni que los savings sean capturables por el propietario aquí."),
    ("compliance and public screening context", "contexto de compliance y screening público"),
    ("NYC Class A tower with LL84/LL97 public-screening context", "torre Class A NYC con contexto público de screening LL84/LL97"),
    ("Class A NYC LL97-covered office towers", "torres de oficinas Class A NYC cubiertas por LL97"),
    ("Public screening is supportable, but closure remains blocked until owner-control and filing-grade evidence are bounded.", "El screening público es defendible, pero el cierre permanece bloqueado hasta acotar el control del propietario y la evidencia de grado filing."),
    ("Peer comparison is admissible for bounded screening, not for declaring retrofit economics or compliance closure.", "La comparación con pares es admisible para screening acotado, no para declarar economía de retrofit ni cierre de compliance."),
    ("owner control boundary vs peer control boundary", "frontera de control del propietario vs frontera de control del par"),
    ("Owner / tenant boundary remains unresolved", "la frontera propietario / inquilino permanece no resuelta"),
    ("Submetered, green-lease, continuously commissioned peer tower", "torre par con submedición, green leases y commissioning continuo"),
    ("A peer can outperform structurally by separating tenant and owner loads before pursuing owner-only retrofit logic.", "Un par puede superar estructuralmente al activo separando cargas de inquilinos y del propietario antes de perseguir lógica de retrofit solo del lado del propietario."),
    ("Do not treat benchmark EUI spread as owner-capturable value until control boundary is observed.", "No trates la brecha de EUI frente al benchmark como valor capturable por el propietario hasta observar la frontera de control."),
    ("base-building systems vs tenant-driven loads", "sistemas base-building vs cargas impulsadas por inquilinos"),
    ("Central-plant and tenant-load dominance remain only partially bounded by public data.", "La dominancia de la planta central y de las cargas de inquilinos sigue solo parcialmente acotada por datos públicos."),
    ("Peer tower with validated central-plant topology and tenant metering discipline", "torre par con topología validada de planta central y disciplina de medición de inquilinos"),
    ("The structural difference is not just EUI level; it is whether the dominant load sits in a controllable boundary.", "La diferencia estructural no es solo el nivel de EUI; es si la carga dominante está dentro de una frontera controlable."),
    ("Benchmarking is useful only to choose which evidence to request next.", "El benchmarking solo es útil para elegir qué evidencia pedir después."),
    ("Tenant-driven loads and unresolved control boundary weaken owner-only retrofit economics.", "Las cargas impulsadas por inquilinos y una frontera de control no resuelta debilitan la economía de un retrofit solo del lado del propietario."),
    ("Regulation sits with the owner while load control and savings capture may sit with tenants or unresolved contractual boundaries.", "La regulación recae sobre el propietario mientras que el control de la carga y la captura de savings pueden recaer en inquilinos o en fronteras contractuales no resueltas."),
    ("Owner CAPEX alone may not capture value until metering, lease, and control boundaries are redesigned.", "El CAPEX del propietario por sí solo puede no capturar valor hasta que se rediseñen la medición, los leases y las fronteras de control."),
    ("Owner-managed central plant and common-area systems dominate load and savings capture.", "La planta central y los sistemas de áreas comunes gestionados por el propietario dominan la carga y la captura de savings."),
    ("Do not treat owner-only retrofit as the primary answer; redesign the control and contract architecture first.", "No trates el retrofit solo del lado del propietario como la respuesta principal; primero rediseña la arquitectura de control y contrato."),
    ("Submetering, green leases, tenant after-hours policy, BMS schedule discipline, and clearer owner/tenant responsibility mapping.", "Submedición, green leases, política de uso fuera de horario por inquilinos, disciplina de horarios del BMS y un mapa más claro de responsabilidades entre propietario e inquilino."),
    ("Owner-managed central plant and BMS optimization may become investable before contractual redesign.", "La optimización de la planta central y del BMS gestionados por el propietario puede volverse invertible antes del rediseño contractual."),
    ("This evidence set discriminates the rival structural hypotheses with the highest value of information.", "Este set de evidencia discrimina las hipótesis estructurales rivales con el mayor valor de información."),
    ("Peer comparison can clarify whether the bottleneck is technology, control boundary, maintenance discipline, or process design.", "La comparación con pares puede aclarar si el cuello de botella es tecnología, frontera de control, disciplina de mantenimiento o diseño del proceso."),
    ("A redesign path is useful only as a falsifiable hypothesis under current evidence.", "Una ruta de rediseño solo es útil como hipótesis falsable bajo la evidencia actual."),
    ("Do not close savings, ROI, or redesign claims before this evidence arrives.", "No cierres claims de savings, ROI o rediseño antes de que llegue esta evidencia."),
    ("Do not state peer superiority as fact without evidence state and transferability bounds.", "No declares superioridad de un par como hecho sin estado de evidencia y límites de transferibilidad."),
    ("Do not present redesign as a final recommendation.", "No presentes el rediseño como recomendación final."),
    ("Compare against structural peers", "Comparar contra pares estructurales"),
    ("Advance bounded redesign hypothesis", "Avanzar una hipótesis acotada de rediseño"),
    ("structural_first", "estructural_primero"),
    ("Decision-grade (unresolved conflicts)", "Grado de decisión (conflictos no resueltos)"),
    ("ACT NOW", "ACTUAR AHORA"),
    ("VALIDATE FIRST", "VALIDAR PRIMERO"),
    ("INVESTIGATE", "INVESTIGAR"),
    ("DEFER", "DIFERIR"),
    ("DO NOT MODEL YET", "NO MODELAR AÚN"),
    ("COMPARE TO PEERS", "COMPARAR CON PARES"),
    ("REDESIGN HYPOTHESIS", "HIPÓTESIS DE REDISEÑO"),
    ("PASSED", "APROBADO"),
    ("FAILED", "FALLIDO"),
    ("OBSERVED_FACT", "HECHO_OBSERVADO"),
    ("ARCHETYPAL_PRIOR", "PRIOR_ARQUETÍPICO"),
    ("CONDITIONAL_HYPOTHESIS", "HIPÓTESIS_CONDICIONAL"),
    ("INADMISSIBLE_CLAIM", "CLAIM_INADMISIBLE"),
    ("NONE", "NINGUNO"),
    ("active", "activos"),
    ("conditional", "condicional"),
    ("Complete", "Completa"),
    ("Incomplete", "Incompleta"),
    ("blocked until resolved", "bloqueado hasta resolverse"),
    ("Hard Conflict [BLOCKING]", "Conflicto Duro [BLOQUEANTE]"),
    ("Plausible Hypothesis", "Hipótesis Plausible"),
    ("Need to determine whether owner-managed base-building systems, tenant-driven loads, or LL97 exposure actually dominate value and capital logic.", "Necesitamos determinar si los sistemas del edificio controlados por el propietario, las cargas impulsadas por inquilinos o la exposición a LL97 dominan realmente la lógica de valor y capital."),
    ("These structural readings remain conditional and do not override claim permissions, report type, or validation gates.", "Estas lecturas estructurales siguen siendo condicionales y no sobreescriben los permisos de claims, el tipo de reporte ni las compuertas de validación."),
    ("Regulation vs control boundary", "Regulación vs frontera de control"),
    ("Finance assumes owner-capturable savings before control is proven", "Finanzas asume ahorros capturables por el propietario antes de probar el control"),
    ("Benchmark disclosure vs physical load truth", "Benchmark público vs verdad física de la carga"),
    ("A. Energy upside is owner-controllable through central plant and common-area systems", "A. El upside energético es controlable por el propietario mediante planta central y sistemas de áreas comunes"),
    ("B. Energy use is structurally tenant-driven or use-mix driven", "B. El uso de energía está impulsado estructuralmente por inquilinos o por mezcla de uso"),
    ("C. Compliance or fuel-transition exposure dominates savings", "C. La exposición de cumplimiento o transición de combustible domina la lógica de ahorro"),
    ("D. Asset cannot yet be technically characterized from current evidence", "D. El activo todavía no puede caracterizarse técnicamente con la evidencia actual"),
    ("Retrofit CAPEX may become investable if central-plant and common-area control sits with the owner.", "El CAPEX de retrofit podría volverse invertible si el control de la planta central y de las áreas comunes está del lado del propietario."),
    ("Owner controls major HVAC, central plant, controls, or common-area loads and captures the resulting economics.", "El propietario controla el HVAC principal, la planta central, los controles o las cargas de áreas comunes y captura la economía resultante."),
    ("Tenant-controlled loads or submetered tenant spaces dominate the operating profile.", "Las cargas controladas por inquilinos o los espacios de inquilinos submedidos dominan el perfil operativo."),
    ("Owner energy upside is weaker than benchmark-based screening suggests and savings may not accrue to the underwriting boundary.", "El upside energético del propietario es más débil de lo que sugiere el screening basado en benchmarks y los ahorros podrían no acumularse dentro del perímetro de underwriting."),
    ("Tenant schedules, use mix, after-hours occupancy, and submetering explain most load behavior.", "Los horarios de los inquilinos, la mezcla de uso, la ocupación fuera de horario y la submedición explican la mayor parte del comportamiento de la carga."),
    ("Central owner-controlled systems dominate energy behavior and tenant variability is secondary.", "Los sistemas centrales controlados por el propietario dominan el comportamiento energético y la variabilidad de los inquilinos es secundaria."),
    ("Capital logic may be driven by avoided penalty or fuel-transition posture rather than operating savings.", "La lógica de capital puede estar impulsada por evitación de penalidades o por postura de transición de combustible, no por ahorros operativos."),
    ("Local rule applicability, area thresholds, and steam / gas / electrification exposure create a material trigger.", "La aplicabilidad de la regla local, los umbrales de superficie y la exposición a vapor / gas / electrificación crean un gatillo material."),
    ("Current filings or local facts show no material trigger or place the burden outside the owner-controlled boundary.", "Los filings actuales o los hechos locales no muestran un gatillo material o ubican la carga fuera de la frontera controlada por el propietario."),
    ("No strong underwriting, retrofit, or compliance decision is defendable yet.", "Aún no puede sostenerse una decisión firme de underwriting, retrofit o cumplimiento."),
    ("Critical clusters remain missing for One Vanderbilt.", "Siguen faltando clústeres críticos para One Vanderbilt."),
    ("Minimum evidence pack is received and major clusters are populated.", "Se recibe el paquete mínimo de evidencia y los clústeres principales quedan poblados."),
    ("Seller / operator evidence request", "Solicitud de evidencia a seller / operator"),
]

_L10N = {
    "en": {
        "framework_name": "Operational Truth Framework",
        "school": "Autonomous Decision Pipeline",
        "decision_grade": "Decision Grade",
        "thesis_type": "Confidential — Decision-grade output. Publication ceiling: {publication_ceiling}.",
        "case": "Case",
        "analyst": "Analyst",
        "date": "Date",
        "publication_ceiling": "Publication Ceiling",
        "traceability_chain": "Traceability Chain",
        "traceability_complete": "Complete",
        "traceability_incomplete": "Incomplete",
        "decision_state": "Decision State",
        "main_warning": "Main Warning",
        "allowed_use": "Use",
        "prohibited_use": "Not Use",
        "confidential_note": "Confidential — Decision-grade output. Not for external distribution.",
        "document_type": "Document Type",
        "epistemic_grade": "Epistemic Grade",
        "framework": "Framework",
        "executive_brief": "Executive Brief",
        "full_analysis_note": "Full analysis begins in Chapter~1. All claims remain conditional on the validation requirements and evidence requests stated in the body.",
        "chart": "Chart",
        "epistemic": "Epistemic",
        "support": "Support",
        "copyright_note": "This document was generated by the ZLab Operational Truth Framework autonomous analytical pipeline. No part of this document may be cited as verified, final, or self-sufficient without independent field validation.",
    },
    "es": {
        "framework_name": "Framework de Verdad Operacional",
        "school": "Pipeline Autónomo de Decisión",
        "decision_grade": "Grado de decisión",
        "thesis_type": "Confidencial — salida de grado de decisión. Techo de publicación: {publication_ceiling}.",
        "case": "Caso",
        "analyst": "Analista",
        "date": "Fecha",
        "publication_ceiling": "Techo de Publicación",
        "traceability_chain": "Cadena de Trazabilidad",
        "traceability_complete": "Completa",
        "traceability_incomplete": "Incompleta",
        "decision_state": "Estado de Decisión",
        "main_warning": "Advertencia Principal",
        "allowed_use": "Uso",
        "prohibited_use": "No usar para",
        "confidential_note": "Confidencial — salida de grado de decisión. No distribuir externamente.",
        "document_type": "Tipo de Documento",
        "epistemic_grade": "Grado Epistemológico",
        "framework": "Framework",
        "executive_brief": "Resumen Ejecutivo",
        "full_analysis_note": "El análisis completo comienza en el Capítulo~1. Todas las afirmaciones siguen condicionadas por los requisitos de validación y los pedidos de evidencia declarados en el cuerpo.",
        "chart": "Gráfico",
        "epistemic": "Estado epistemológico",
        "support": "Soporte",
        "copyright_note": "Este documento fue generado por el pipeline analítico autónomo del ZLab Operational Truth Framework. Ninguna parte de este documento puede citarse como verificada, final o autosuficiente sin validación de campo independiente.",
    },
}


def _tr(language: str, key: str, **kwargs: Any) -> str:
    table = _L10N.get(language, _L10N["en"])
    return table.get(key, _L10N["en"].get(key, key)).format(**kwargs)


def _localize_title(title: str, language: str) -> str:
    if language == "es":
        normalized = str(title or "").strip()
        return (
            _SECTION_TITLE_ES.get(normalized)
            or _SECTION_TITLE_ES_NORMALIZED.get(normalized.lower())
            or title
        )
    return title


def _localize_output_modes_in_text(text: str, language: str) -> str:
    if language != "es":
        return str(text or "")
    localized = str(text or "")
    modes = sorted(CANONICAL_VISIBLE_OUTPUT_MODES, key=len, reverse=True)
    for mode in modes:
        localized = localized.replace(mode, _localize_document_type(mode, "es"))
    return localized


def _localize_inline_text(text: str, language: str) -> str:
    localized = str(text or "")
    if language != "es" or not localized:
        return localized
    localized = _localize_output_modes_in_text(localized, language)
    for source, target in _STRUCTURED_TEXT_REPLACEMENTS_ES:
        localized = localized.replace(source, target)
    return localized


def _localize_block_label(label: str, language: str) -> str:
    normalized = str(label or "").strip()
    if language != "es":
        return normalized
    return _STRUCTURED_LABELS_ES.get(normalized, normalized)


def _localize_document_type(document_type: str, language: str) -> str:
    document_type = canonicalize_output_mode(document_type)
    if language != "es":
        return document_type
    mapping = {
        "Target Classification Brief": "Informe de Clasificación del Objetivo",
        "Decision-Blocked Asset Brief": "Informe de Activo con Decisión Bloqueada",
        "Exploratory Prior Brief": "Informe Exploratorio de Priors",
        "Compliance / Investment Screening Brief": "Informe de Screening de Cumplimiento / Inversión",
        "Structural Contradiction Brief": "Informe de Contradicciones Estructurales",
        "System Redesign Hypothesis Brief": "Informe de Hipótesis de Rediseño del Sistema",
        "Competitive Positioning Brief": "Informe de Posicionamiento Competitivo",
        "TAD Action Priority Brief": "Informe de Prioridad de Acción TAD",
        "Full Technical Decision Intelligence Report": "Informe Técnico Integral de Inteligencia para la Decisión",
        "Asset Decision-Admissibility Brief": "Informe de Admisibilidad de Decisión del Activo",
    }
    return mapping.get(document_type, document_type)


def _localize_publication_ceiling(publication_ceiling: str, language: str) -> str:
    raw = str(publication_ceiling or "").replace("_", " ").strip().lower()
    if language != "es":
        return raw.title()
    mapping = {
        "publish bounded": "Publicación acotada",
        "publish with degradation": "Publicación con degradación",
        "hold for validation": "Retenido para validación",
    }
    return mapping.get(raw, raw.title())


def _localize_epistemic_grade(epistemic_grade: str, language: str) -> str:
    grade = str(epistemic_grade or "").strip()
    if language != "es":
        return grade
    mapping = {
        "Decision-grade": "Grado de decisión",
        "Decision-grade (unresolved conflicts)": "Grado de decisión (conflictos no resueltos)",
        "Decision-grade — preparatory analysis only": "Grado de decisión — análisis preparatorio únicamente",
    }
    return mapping.get(grade, grade)


def _localize_analyst(analyst: str, language: str) -> str:
    value = str(analyst or "").strip()
    if language != "es":
        return value
    mapping = {
        "Autonomous Research System": "Sistema Autónomo de Investigación",
        "Autonomous Decision System": "Sistema Autónomo de Decisión",
    }
    return mapping.get(value, value)


def _localize_framework_constraint(constraint: str, language: str) -> str:
    value = str(constraint or "").strip()
    if language != "es":
        return value
    canonical = (
        "Este informe es una materialización gobernada de los outputs del Núcleo de Decisión. "
        "Permanece en grado de decisión hasta que evidencia independiente eleve los objetos subyacentes. "
        "Ninguna afirmación constituye un diagnóstico verificado, una determinación de cumplimiento o una recomendación de inversión. "
        "Todos los claims permanecen condicionados por los requisitos de validación y el estado de la evidencia."
    )
    if not value:
        return canonical
    if "Decision Core outputs" in value:
        return canonical
    localized = _localize_inline_text(value, language)
    return localized


def _validate_render_section_contract(
    render_section_contract: dict[str, Any],
    body_sections: list[dict[str, Any]],
    appendix_sections: list[dict[str, Any]],
) -> None:
    if not render_section_contract:
        return
    body_titles = [
        str(section.get("title", "")).strip()
        for section in body_sections
        if str(section.get("title", "")).strip()
    ]
    appendix_titles = [
        str(section.get("title", "")).strip()
        for section in appendix_sections
        if str(section.get("title", "")).strip()
    ]
    required_body = {
        str(title).strip()
        for title in list(render_section_contract.get("required_body_sections", []) or [])
        if str(title).strip()
    }
    required_appendix = {
        str(title).strip()
        for title in list(render_section_contract.get("required_appendix_sections", []) or [])
        if str(title).strip()
    }
    missing_body = sorted(required_body - set(body_titles))
    misplaced_body = sorted(required_body & set(appendix_titles))
    missing_appendix = sorted(required_appendix - set(appendix_titles))
    if missing_body or misplaced_body or missing_appendix:
        raise ValueError(
            "Render section contract violated before render: "
            f"missing_body={missing_body} misplaced_body={misplaced_body} missing_appendix={missing_appendix}"
        )
    expected_body_titles = list(render_section_contract.get("resolved_body_sections", []) or [])
    expected_appendix_titles = list(render_section_contract.get("resolved_appendix_sections", []) or [])
    if expected_body_titles and body_titles != expected_body_titles:
        raise ValueError(
            "Render body ordering diverges from resolved section contract: "
            f"expected {expected_body_titles} got {body_titles}"
        )
    if expected_appendix_titles and appendix_titles != expected_appendix_titles:
        raise ValueError(
            "Render appendix ordering diverges from resolved section contract: "
            f"expected {expected_appendix_titles} got {appendix_titles}"
        )


def _brand_header(org: str, language: str) -> str:
    brand = str(org or "ZLab").strip()
    lowered = brand.lower()
    if "operational truth framework" in lowered or "framework de verdad operacional" in lowered:
        brand = "ZLab"
    return f"{brand} | {_tr(language, 'framework_name')}"


def _section_llm_text(sec: dict[str, Any], language: str) -> str:
    if language == "es":
        return sec.get("llm_text_es") or sec.get("llm_text", "")
    return sec.get("llm_text_en") or sec.get("llm_text", "")


# ── Chart PNG helper ──────────────────────────────────────────────────────────

def _save_chart_png(b64: str, dest: Path) -> bool:
    """Decode base64 PNG and write to dest. Returns True on success."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(base64.b64decode(b64))
        return True
    except Exception:
        return False


# ── LaTeX escape ───────────────────────────────────────────────────────────────

def _e(text: str) -> str:
    """Single-pass LaTeX escape of special characters."""
    out: list[str] = []
    for c in str(text):
        if   c == "\\":  out.append("\\textbackslash{}")
        elif c == "&":   out.append("\\&")
        elif c == "%":   out.append("\\%")
        elif c == "$":   out.append("\\$")
        elif c == "#":   out.append("\\#")
        elif c == "_":   out.append("\\_")
        elif c == "{":   out.append("\\{")
        elif c == "}":   out.append("\\}")
        elif c == "~":   out.append("\\textasciitilde{}")
        elif c == "^":   out.append("\\textasciicircum{}")
        else:            out.append(c)
    return "".join(out)


# ── LLM narrative → LaTeX ─────────────────────────────────────────────────────

def _narrative_to_latex(text: str) -> str:
    """Convert LLM prose (with **bold**) to LaTeX paragraphs."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    out: list[str] = []

    for para in paragraphs:
        full = " ".join(l.strip() for l in para.split("\n"))

        # Split on **bold** markers, escape each part, wrap bold in \textbf
        parts = re.split(r"\*\*(.+?)\*\*", full)
        rendered: list[str] = []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                rendered.append(_e(part))
            else:
                rendered.append(f"\\textbf{{{_e(part)}}}")
        full_tex = "".join(rendered)

        # Detect standalone heading: entire para was **heading** or looks like a title
        heading_m = re.match(r"^\\textbf\{([^}]+)\}$", full_tex.strip())
        if heading_m:
            out.append(f"\\subsection*{{{heading_m.group(1)}}}\n")
        elif len(full) < 80 and not full.endswith(".") and not full.startswith("**"):
            # Short line without period — treat as subsection
            out.append(f"\\subsection*{{{full_tex}}}\n")
        else:
            out.append(full_tex + "\n")

    return "\n\n".join(out)


# ── Structured block → LaTeX ──────────────────────────────────────────────────

_ALPHA_RE = re.compile(r"[a-zA-Z]")
_SCORE_BAR_RE = re.compile(r"\[[\#=\-\s]{3,}\]\s*[\d.]*")


def _block_to_latex(content: str, language: str = "en") -> str:
    """Convert structured block text (from motor_016) to LaTeX markup."""
    lines = content.split("\n")
    out: list[str] = []
    in_itemize   = False
    in_enumerate = False

    def close_lists() -> None:
        nonlocal in_itemize, in_enumerate
        if in_itemize:
            out.append("\\end{itemize}")
            in_itemize = False
        if in_enumerate:
            out.append("\\end{enumerate}")
            in_enumerate = False

    for raw in lines:
        stripped = raw.rstrip()

        if not stripped.strip():
            close_lists()
            out.append("")
            continue

        s = stripped.strip()

        # Remove embedded score bars
        s = _SCORE_BAR_RE.sub("", s).strip()
        if not s:
            continue

        # Skip pure separator lines
        if set(s) <= set("=-_*"):
            continue

        alpha_chars = _ALPHA_RE.findall(s)

        # ALL-CAPS header → subsection
        if (
            s == s.upper()
            and 4 <= len(s) <= 80
            and not s.endswith(".")
            and not s.startswith("[")
            and not s.startswith("$")
            and " " in s
            and len(alpha_chars) >= 3
        ):
            close_lists()
            out.append(f"\n\\subsection*{{{_e(_localize_title(_localize_inline_text(s.title(), language), language))}}}")
            continue

        # Bullet item
        if s.startswith("- ") or s.startswith("* "):
            if not in_itemize:
                close_lists()
                out.append("\\begin{itemize}")
                in_itemize = True
                out.append(f"  \\item {_e(_localize_inline_text(s[2:].strip(), language))}")
            continue

        # Numbered item
        if len(s) > 2 and s[0].isdigit() and s[1] == ".":
            if not in_enumerate:
                close_lists()
                out.append("\\begin{enumerate}")
                in_enumerate = True
                out.append(f"  \\item {_e(_localize_inline_text(s[2:].strip(), language))}")
            continue

        close_lists()

        # Label: value (colon within first 35 chars, simple label)
        colon = s.find(":")
        label_candidate = re.sub(r"\s+", " ", s[:colon].strip()) if colon > 0 else ""
        if (
            0 < colon <= 35
            and colon < len(s) - 1
            and label_candidate.count(" ") <= 4
            and not s.startswith("[")
            and not s.startswith("$")
        ):
            label = _e(_localize_block_label(label_candidate, language))
            value = _e(_localize_inline_text(s[colon + 1:].strip(), language))
            out.append(f"\\noindent\\textbf{{{label}:}} {value}\\par\\smallskip")
            continue

        # Default paragraph
        out.append(f"\\noindent {_e(_localize_inline_text(s, language))}\\par")

    close_lists()
    return "\n".join(out)


# ── Chapter .tex generator ─────────────────────────────────────────────────────

def _chapter_tex(
    sec: dict,
    chap_label: str,
    chart_png_rel: str = "",
    chart_png_rel_list: list[str] | None = None,
    language: str = "en",
) -> str:
    """Generate the content of a single chapter .tex file."""
    title          = _localize_title(sec.get("title", ""), language)
    llm_text       = _section_llm_text(sec, language)
    blocks         = sec.get("blocks", [])
    epistemic      = sec.get("epistemic_marker", "")
    section_type   = sec.get("section_type", "body")
    chapter_id     = sec.get("chapter_id", chap_label)

    # Normalise chart list: prefer explicit list, fall back to single path
    all_chart_rels: list[str] = [
        p for p in (chart_png_rel_list or ([chart_png_rel] if chart_png_rel else []))
        if p
    ]
    chart_assets: list[dict[str, Any]] = sec.get("chart_assets", [])

    parts: list[str] = []

    # LLM narrative as primary body
    if llm_text:
        parts.append(_narrative_to_latex(llm_text))
        parts.append("\n")

    # Chart figures (all charts for this section)
    for idx, rel_path_raw in enumerate(all_chart_rels):
        chart_asset = chart_assets[idx] if idx < len(chart_assets) else {}
        rel_path = _e(rel_path_raw.replace("\\", "/"))
        chart_title = (
            chart_asset.get(f"title_{language}")
            or chart_asset.get("title", "")
        )
        chart_description = (
            chart_asset.get(f"description_{language}")
            or chart_asset.get("description", "")
        )
        parts.append(
            "\\begin{figure}[H]\n"
            "  \\centering\n"
            f"  \\includegraphics[width=0.96\\textwidth]{{{rel_path}}}\n"
            "\\end{figure}\n"
            "\\vspace{0.5em}\n"
        )
        caption_bits = []
        if chart_title:
            caption_bits.append(f"{_tr(language, 'chart')}: {chart_title}")
        if chart_description:
            caption_bits.append(str(chart_description))
        if caption_bits:
            parts.append(
                "{\\footnotesize\\color{black!70}\\noindent "
                + _e(" | ".join(caption_bits))
                + "\\par}\n\\vspace{0.4em}\n"
            )

    # Structured data blocks
    if blocks:
        raw_blocks = []
        for block in blocks:
            localized_content = (
                block.get("content_es")
                if language == "es"
                else block.get("content_en")
            )
            content = localized_content or block.get("content", "")
            if content:
                raw_blocks.append(content)
        if raw_blocks:
            # When a substantial LLM narrative is present, blocks are subordinated
            # reference data — rendered compact and visually distinct, not full-width.
            has_narrative = bool(llm_text and len(llm_text.strip()) > 200)
            if llm_text or all_chart_rels:
                parts.append(
                    "\n\\vspace{0.8em}\n"
                    "\\noindent{\\color{black!35}\\rule{\\linewidth}{0.3pt}}\n"
                    "\\vspace{0.2em}\n"
                )
            if has_narrative:
                # Compact subordinated block: footnotesize, muted color
                parts.append(
                    "\\begingroup\n"
                    "\\footnotesize\\color{black!65}\n"
                )
            for raw in raw_blocks:
                parts.append(_block_to_latex(raw, language=language))
                parts.append("\n")
            if has_narrative:
                parts.append("\\endgroup\n")

    body = "\n".join(parts)

    if section_type == "appendix":
        return (
            f"\\chapter{{{_e(title)}}}\n"
            f"\\label{{app:{chap_label.lower()}}}\n\n"
            f"{body}\n"
        )
    return (
        f"\\chapter{{{_e(title)}}}\n"
        f"\\label{{chap:{chap_label.lower()}}}\n\n"
        f"{body}\n"
    )


# ── Metadata.tex generator ────────────────────────────────────────────────────

def _metadata_tex(meta: dict, language: str = "en") -> str:
    case_id   = _e(meta.get("case_id", ""))
    title     = _e(meta.get("case_title", "Governed Asset Brief"))
    document_type_raw = meta.get(f"document_type_{language}", meta.get("document_type", "Asset Decision-Admissibility Brief"))
    document_type = _e(_localize_document_type(str(document_type_raw), language))
    subtitle  = _e(meta.get(f"case_subtitle_{language}", meta.get("case_subtitle", document_type)))
    analyst   = _e(_localize_analyst(meta.get("analyst", "Autonomous Decision System"), language))
    org       = _e(meta.get("organization", "ZLab"))
    publication_ceiling = _e(_localize_publication_ceiling(meta.get("publication_ceiling", "publish_bounded"), language))
    date_str  = meta.get("produced_at", datetime.now(timezone.utc).isoformat())[:10]
    year      = date_str[:4]
    month_day = date_str[5:]

    return (
        f"\\FirstAuthor{{{analyst}}}\n"
        f"\\FirstAuthorNumber{{ZLab-ADS}}\n"
        f"\n"
        f"\\Title{{{title}}}\n"
        f"\\Subtitle{{{subtitle}}}\n"
        f"\n"
        f"\\Supervisor{{{_e(_tr(language, 'framework_name'))}}}\n"
        f"\\SupervisorTitle{{{_e(_tr(language, 'school'))} — {_e(_tr(language, 'decision_grade'))}}}\n"
        f"\n"
        f"\\University{{{org}}}\n"
        f"\\School{{{_e(_tr(language, 'school'))} | {_e(_tr(language, 'decision_grade'))} | {publication_ceiling}}}\n"
        f"\\Department{{{_e(_tr(language, 'case'))}: {case_id}}}\n"
        f"\\Degree{{{document_type}}}\n"
        f"\\ThesisType{{{_e(_tr(language, 'thesis_type', publication_ceiling=publication_ceiling))}}}\n"
        f"\n"
        f"\\Date{{{date_str}}}\n"
        f"\\AcademicYear{{{year}}}\n"
    )


# ── Custom front page (no IPLeiria logo/background) ───────────────────────────

def _frontpage_tex(meta: dict, language: str = "en") -> str:
    """Minimal white ZLab cover page — overrides Matter/01-Front-Page.tex."""
    title    = _e(meta.get("case_title", "Governed Asset Brief"))
    subtitle = _e(meta.get(f"case_subtitle_{language}", meta.get("case_subtitle", meta.get("document_type", "Asset Decision-Admissibility Brief"))))
    document_type_raw = meta.get(f"document_type_{language}", meta.get("document_type", "Asset Decision-Admissibility Brief"))
    document_type = _e(_localize_document_type(str(document_type_raw), language))
    case_id  = _e(meta.get("case_id", ""))
    analyst  = _e(_localize_analyst(meta.get("analyst", "Autonomous Decision System"), language))
    org_raw  = str(meta.get("organization", "ZLab"))
    publication_ceiling = _e(_localize_publication_ceiling(meta.get("publication_ceiling", "publish_bounded"), language))
    traceability_note = _tr(language, "traceability_complete") if meta.get("traceability_chain_complete", False) else _tr(language, "traceability_incomplete")
    decision_state = _e(_localize_inline_text(meta.get(f"decision_state_{language}", meta.get("decision_state", "")), language))
    main_warning = _e(_localize_inline_text(meta.get(f"main_warning_{language}", meta.get("main_warning", "")), language))
    allowed_use_raw = meta.get(f"allowed_use_{language}", meta.get("allowed_use", []))
    prohibited_use_raw = meta.get(f"prohibited_use_{language}", meta.get("prohibited_use", []))
    allowed_use = allowed_use_raw if isinstance(allowed_use_raw, list) else [str(allowed_use_raw)]
    prohibited_use = prohibited_use_raw if isinstance(prohibited_use_raw, list) else [str(prohibited_use_raw)]
    date_str = meta.get("produced_at", "")[:10]

    return (
        "\\newgeometry{margin=3cm, top=4cm, bottom=3cm}\n"
        "\\begin{titlepage}\n"
        "\\color{black}\n"
        "\\raggedright\n"
        "\n"
        f"{{\\fontsize{{9}}{{11}}\\selectfont\\texttt{{{_e(_brand_header(org_raw, language))}}}}}\n"
        "\\vspace{1.2cm}\n\n"
        f"{{\\fontsize{{11}}{{13}}\\bfseries\\selectfont {document_type}\\par}}\n"
        "\\vspace{0.8cm}\n\n"
        f"{{\\fontsize{{24}}{{30}}\\bfseries\\selectfont {title}\\par}}\n"
        "\\vspace{0.8cm}\n\n"
        f"{{\\fontsize{{14}}{{18}}\\selectfont {subtitle}\\par}}\n"
        "\\vspace{1.4cm}\n\n"
        "\\noindent\\rule{\\linewidth}{0.6pt}\n"
        "\\vspace{0.4cm}\n\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'case'))}:}} {case_id}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'analyst'))}:}} {analyst}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'date'))}:}} {date_str}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'publication_ceiling'))}:}} {publication_ceiling}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'decision_state'))}:}} {decision_state}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'main_warning'))}:}} {main_warning}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'allowed_use'))}:}} {_e('; '.join(_localize_inline_text(str(item), language) for item in allowed_use if item))}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'prohibited_use'))}:}} {_e('; '.join(_localize_inline_text(str(item), language) for item in prohibited_use if item))}\\par}}\n"
        f"{{\\fontsize{{10}}{{14}}\\selectfont\\textbf{{{_e(_tr(language, 'traceability_chain'))}:}} {_e(traceability_note)}\\par}}\n"
        "\\vspace{0.3cm}\n"
        "\\noindent\\rule{\\linewidth}{0.4pt}\n"
        "\n"
        "\\vfill\n"
        "{\\fontsize{8}{10}\\itshape\\selectfont "
        f"{_e(_tr(language, 'confidential_note'))}"
        "}\n"
        "\\end{titlepage}\n"
        "\\restoregeometry\n"
        "\\MediaOptionLogicBlank\n"
    )


# ── main.tex generator ─────────────────────────────────────────────────────────

def _main_tex(
    body_sections: list[dict],
    appendix_sections: list[dict],
    llm_model: str,
    framework_constraint: str,
    document_type: str,
    language: str = "en",
) -> str:
    body_includes = "\n".join(
        f"\\include{{Chapters/{sec['chapter_id']}}}"
        for sec in body_sections
    )
    appendix_includes = "\n".join(
        f"\\include{{Chapters/{sec['chapter_id']}}}"
        for sec in appendix_sections
    )
    constraint_escaped = _e(framework_constraint[:300]) if framework_constraint else ""
    model_note = f"\\textit{{LLM narratives produced by {_e(llm_model)}.}}" if llm_model else ""

    return (
        f"%%% ZLab {document_type} — auto-generated by motor_017 %%%\n"
        "\\documentclass[\n"
        f"    language={'spanish' if language == 'es' else 'english'},\n"
        "    school=estg,\n"
        "    docstage=final,\n"
        "    media=paper,\n"
        "    bookprint=false,\n"
        "    linkcolor=red!45!black,\n"
        "    chapterstyle=classic,\n"
        "    coverstyle=classic,\n"
        "    aiacknowledgement=false,\n"
        "    listprefix=false\n"
        "]{IPLeiriaThesis}\n\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage{float}\n"
        "\\input{Metadata/Metadata}\n\n"
        "\\begin{document}\n\n"
        "%%% Cover & Front Matter %%%\n"
        "\\include{Matter/01-Front-Page}\n"
        "\\include{Matter/02-Copyright}\n\n"
        "\\pagenumbering{roman}\n\n"
        "%%% Executive Brief (Abstract position) %%%\n"
        "\\include{Chapters/00-Brief}\n\n"
        "\\bookmarktocentry\\tableofcontents\n\n"
        "\\pagenumbering{arabic}\n\n"
        "%%% Body Chapters %%%\n"
        f"{body_includes}\n\n"
    ) + (
        "%%% Appendices %%%\n"
        "\\appendix\n"
        f"{appendix_includes}\n\n"
        if appendix_sections else ""
    ) + (
        "%%% Back matter %%%\n"
        "\\include{Matter/10-Back-Page}\n\n"
        "\\end{document}\n"
    )


# ── Copyright page generator ──────────────────────────────────────────────────

def _copyright_tex(meta: dict, language: str = "en") -> str:
    org   = _e(meta.get("organization", "ZLab"))
    year  = meta.get("produced_at", "2026")[:4]
    constraint = _e(_localize_framework_constraint(meta.get("framework_constraint", "")[:400], language))
    return (
        "\\thispagestyle{plain}\n"
        f"\\vspace*{{\\fill}}\n"
        f"\\noindent\\textbf{{Copyright {year} {org}.}}\\\\\n\n"
        f"\\noindent {constraint}\n\n"
        "\\vspace{1em}\n"
        f"\\noindent {_e(_tr(language, 'copyright_note'))}\n"
        "\\vspace*{\\fill}\n"
        "\\newpage\n"
    )


def _reset_governed_chapters_dir(chapters_dir: Path) -> None:
    if not chapters_dir.exists():
        chapters_dir.mkdir(parents=True, exist_ok=True)
        return
    for item in chapters_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
            continue
        if item.suffix.lower() == ".tex":
            item.unlink()


def _written_chapter_inventory(chapters_dir: Path) -> list[str]:
    if not chapters_dir.exists():
        return []
    return sorted(
        item.name
        for item in chapters_dir.iterdir()
        if item.is_file() and item.suffix.lower() == ".tex"
    )


# ── Abstract page (Executive Brief) ──────────────────────────────────────────

def _abstract_tex(
    body_sections: list[dict],
    governance_summary: dict[str, Any] | None = None,
    document_type: str = "Asset Decision-Admissibility Brief",
    language: str = "en",
) -> str:
    """Generate the Executive Brief page.

    Uses the LLM narrative (llm_text) from C1 as the primary body when
    substantial (>200 chars). Falls back to a curated extract of key decision
    state signals from the structured block — never the raw full machine dump.
    """
    c1 = next((s for s in body_sections if s.get("chapter_id") == "C1"), {})
    llm_text = _section_llm_text(c1, language)
    blocks   = c1.get("blocks", [])
    raw      = blocks[0].get("content", "") if blocks else ""

    # Primary content: LLM narrative preferred over raw block dump
    if llm_text and len(llm_text.strip()) > 200:
        primary = _narrative_to_latex(llm_text)
    else:
        # Curated fallback: extract only decision-state signal lines
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        keep: list[str] = []
        for l in lines:
            if set(l) <= set("=-_*"):
                continue
            upper = l.upper()
            if any(tok in upper for tok in (
                "BLOCKING", "INFERENCE CASES", "URGENCY",
                "OPEN TENSIONS", "OPPORTUNITIES", "DECISION STATE",
                "EPISTEMIC LIMIT",
            )):
                keep.append(_localize_inline_text(l, language))
            if len(keep) >= 20:
                break
        primary = (
            "{\\small\n"
            + "\n".join(f"\\noindent {_e(dl)}\\par\\smallskip" for dl in keep[:15])
            + "\n}"
        )

    # Decision state summary — 4–6 lines max, extracted from block
    decision_lines: list[str] = []
    in_ds = False
    for line in raw.split("\n"):
        s = line.strip()
        if not s or set(s) <= set("=-_*"):
            continue
        if "DECISION STATE" in s.upper():
            in_ds = True
            continue
        if in_ds:
            if any(h in s.upper() for h in ("ACTIVE INFERENCE", "EPISTEMIC LIMIT", "URGENCY RANKING")):
                break
            if s:
                decision_lines.append(_localize_inline_text(s, language))
        if len(decision_lines) >= 6:
            break

    ds_block = ""
    if decision_lines:
        ds_block = (
            "\\vspace{0.6em}\n"
            "{\\small\n"
            + "\n".join(f"\\noindent {_e(dl)}\\par\\smallskip" for dl in decision_lines[:5])
            + "\n}\n"
        )

    return (
        "\\thispagestyle{plain}\n"
        f"\\pdfbookmark[1]{{{_e(_tr(language, 'executive_brief'))}}}{{brief}}\n"
        f"\\chapter*{{{_e(_tr(language, 'executive_brief'))}}}\n\n"
        f"\\noindent\\textbf{{{_e(_tr(language, 'document_type'))}:}} {_e(_localize_document_type(document_type, language))}\\\\\n"
        f"\\noindent\\textbf{{{_e(_tr(language, 'epistemic_grade'))}:}} {_e(_localize_epistemic_grade(str((governance_summary or {}).get('epistemic_grade', 'Decision-grade')), language))}\\\\\n"
        f"\\noindent\\textbf{{{_e(_tr(language, 'publication_ceiling'))}:}} {_e(_localize_publication_ceiling((governance_summary or {}).get('publication_ceiling', 'publish_bounded'), language))}\\\\\n"
        f"\\noindent\\textbf{{{_e(_tr(language, 'framework'))}:}} ZLab Operational Truth Framework\n\n"
        "\\vspace{1em}\n\n"
        f"{primary}\n\n"
        f"{ds_block}\n"
        "\\vspace{0.8em}\n"
        f"\\noindent\\textit{{{_e(_tr(language, 'full_analysis_note'))}}}\n"
        "\\newpage\n"
    )


def _document_slug(document_type: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", str(document_type).strip().lower()).strip("_")
    return slug or "report"


def _hydrated_system_consistency_section(
    body_sections: list[dict[str, Any]],
    consistency_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    if not consistency_summary:
        return body_sections
    hydrated: list[dict[str, Any]] = []
    checks = list(consistency_summary.get("checks", []) or [])
    failures = list(consistency_summary.get("critical_failures", []) or [])
    status = "PASSED" if consistency_summary.get("can_render_pdf", True) else "FAILED"
    content = [
        "=" * 68,
        "SYSTEM CONSISTENCY CHECK",
        "=" * 68,
        "",
        f"  Final Consistency Status : {status}",
        f"  Critical Failure Count   : {int(consistency_summary.get('critical_failure_count', 0) or 0)}",
        "  Validator Owner         : motor_036",
        "",
    ]
    if failures:
        content += ["  Blocking Failures:", *[
            f"    - [{str(row.get('check_id', '')).strip()}] {str(row.get('message', '')).strip()}"
            for row in failures[:8]
        ], ""]
    passed_checks = [row for row in checks if bool(row.get("passed", False))]
    if passed_checks:
        content += ["  Passed Critical Contracts:"]
        for row in passed_checks[:12]:
            content.append(f"    - [{str(row.get('check_id', '')).strip()}] {str(row.get('severity', '')).strip()}")
        content.append("")
    for sec in body_sections:
        if str(sec.get("title", "")).strip() != "System Consistency Check":
            hydrated.append(sec)
            continue
        sec_copy = dict(sec)
        sec_copy["blocks"] = [{"block_id": sec.get("block_ref", "b_structural_system_consistency_check"), "content": "\n".join(content)}]
        hydrated.append(sec_copy)
    return hydrated


def _resolve_gold_nugget_authority(report_package: dict[str, Any]) -> tuple[str, str]:
    authority_state = ""
    source_register = ""
    for key in (
        "main_report_outline",
        "structural_executive_summary",
        "structural_intelligence_summary",
        "executive_thesis",
    ):
        row = report_package.get(key, {})
        if not isinstance(row, dict):
            continue
        if not authority_state:
            authority_state = str(row.get("gold_nugget_authority_state", "") or "").strip()
        if not source_register:
            source_register = str(row.get("gold_nugget_source_register", "") or "").strip()
        if authority_state and source_register:
            break
    return (
        authority_state or "legacy_primary_skill_shadow",
        source_register or "motor_054.strategic_gold_nugget_register",
    )


# ── Adapter ───────────────────────────────────────────────────────────────────

class Motor017Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_017"

    @property
    def input_motor_ids(self) -> list[str]:
        return [
            "motor_014", "motor_016", "motor_036",
            "motor_055", "motor_056", "motor_057", "motor_058", "motor_059",
            "motor_061", "motor_062", "motor_063",
        ]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        report_package = inputs.get("motor_016", {}).get("report_package")
        if not report_package:
            raise ValueError("motor_016 did not produce a report_package")
        gold_nugget_authority_state, gold_nugget_source_register = _resolve_gold_nugget_authority(report_package)
        consistency_summary = inputs.get("motor_036", {}) if isinstance(inputs.get("motor_036", {}), dict) else {}
        # Recovery R-66: allow opt-in render under warnings via pipeline input.
        # Set `__pipeline__.__force_render__ = true` to bypass motor_036's
        # can_render_pdf=False gate. The render proceeds and the resulting
        # output carries the warnings in `consistency_summary` for the
        # composer / readers to inspect. Default behaviour (no flag) is
        # unchanged: motor_036 still blocks when it detects critical failures.
        pipeline_inputs = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        force_render_under_warnings = bool(pipeline_inputs.get("__force_render__", False))

        # Recovery 2026-05-09 prompt: integrate motor_061 (Asset Family
        # Isolation) and motor_063 (Chart Validity) into the render gate.
        # Their critical_count > 0 signals contamination that would degrade
        # report quality. Honors the same __force_render__ escape.
        m061 = inputs.get("motor_061", {}) if isinstance(inputs.get("motor_061", {}), dict) else {}
        m062 = inputs.get("motor_062", {}) if isinstance(inputs.get("motor_062", {}), dict) else {}
        m063 = inputs.get("motor_063", {}) if isinstance(inputs.get("motor_063", {}), dict) else {}
        family_contamination = bool(m061.get("contamination_detected", False))
        scenario_justification_failed = bool(m062.get("scenario_justification_failed", False))
        chart_contamination = bool(m063.get("chart_contamination_detected", False))

        block_reasons: list[str] = []
        if consistency_summary and not consistency_summary.get("can_render_pdf", True):
            failures = list(consistency_summary.get("critical_failures", []) or [])
            block_reasons.append(
                "; ".join(str(row.get("message", "consistency failure")) for row in failures[:4])
                or "Blocked by system consistency validator."
            )
        if family_contamination:
            warns = list(m061.get("asset_family_isolation_warnings", []) or [])
            block_reasons.append(
                "Asset-family contamination detected by motor_061: "
                + "; ".join(str(w.get("description", "")) for w in warns[:2])
            )
        if chart_contamination:
            warns = list(m063.get("chart_validity_warnings", []) or [])
            block_reasons.append(
                "Chart-validity contamination detected by motor_063: "
                + "; ".join(str(w.get("description", "")) for w in warns[:2])
            )
        if scenario_justification_failed:
            warns = list(m062.get("scenario_justification_warnings", []) or [])
            block_reasons.append(
                "Scenario justification failure detected by motor_062: "
                + "; ".join(str(w.get("description", "")) for w in warns[:2])
            )

        # V3 G1: wire validators 055-059 into the render gate.
        # Each emits warnings only (no critical_count today). We promote
        # specific rules to "blocking" when their semantic implies the
        # report would mislead a reader if rendered. Thresholds are
        # configurable via __pipeline__.validator_thresholds (dict) so the
        # regression / CI can keep its behavior while production tightens.
        thresholds = pipeline_inputs.get("validator_thresholds") or {}

        def _rule_hits(warnings: list[dict], rule_id: str) -> int:
            return sum(1 for w in warnings if isinstance(w, dict) and w.get("rule_id") == rule_id)

        m055 = inputs.get("motor_055", {}) if isinstance(inputs.get("motor_055", {}), dict) else {}
        m056 = inputs.get("motor_056", {}) if isinstance(inputs.get("motor_056", {}), dict) else {}
        m057 = inputs.get("motor_057", {}) if isinstance(inputs.get("motor_057", {}), dict) else {}
        m058 = inputs.get("motor_058", {}) if isinstance(inputs.get("motor_058", {}), dict) else {}
        m059 = inputs.get("motor_059", {}) if isinstance(inputs.get("motor_059", {}), dict) else {}

        m055_w = list(m055.get("hypothesis_diversity_warnings", []) or [])
        m056_w = list(m056.get("evidence_repetition_warnings", []) or [])
        m057_w = list(m057.get("gold_nugget_quality_warnings", []) or [])
        m058_w = list(m058.get("report_uniqueness_warnings", []) or [])
        m059_w = list(m059.get("strategic_intelligence_warnings", []) or [])

        # motor_055 — Hypothesis Diversity: block on duplicate claim signature
        if _rule_hits(m055_w, "HD2_duplicate_claim_signature") >= int(thresholds.get("m055_HD2", 1)):
            block_reasons.append(
                "Hypothesis diversity failure (motor_055.HD2): duplicate claim signature in output."
            )
        # motor_056 — Evidence Repetition: block when evidence packs are reused across patterns
        if _rule_hits(m056_w, "ER1_pack_repetition") >= int(thresholds.get("m056_ER1", 2)):
            block_reasons.append(
                "Evidence repetition (motor_056.ER1): same evidence pack reused ≥2 times across patterns."
            )
        # motor_057 — Gold Nugget Quality: block on archetype replay (verbatim reuse from prior)
        if _rule_hits(m057_w, "GN1_archetype_replay") >= int(thresholds.get("m057_GN1", 1)):
            block_reasons.append(
                "Gold nugget archetype replay (motor_057.GN1): nugget reused verbatim from a prior archetype."
            )
        # motor_058 — Report Uniqueness: block on verbatim nugget reuse across runs
        if _rule_hits(m058_w, "RU2_verbatim_nugget_reuse") >= int(thresholds.get("m058_RU2", 1)):
            block_reasons.append(
                "Report uniqueness failure (motor_058.RU2): nugget reused verbatim from a prior run."
            )
        # motor_059 — Strategic Intelligence: block on severity=error (warnings/info pass)
        m059_errors = [w for w in m059_w if isinstance(w, dict) and w.get("severity") == "error"]
        if m059_errors:
            block_reasons.append(
                "Strategic intelligence error (motor_059): "
                + "; ".join(str(w.get("description", "")) for w in m059_errors[:2])
            )

        # V2-CRITICAL course correction: dashboard review gate.
        # Seed the per-case scenario_review file with this run's scenarios
        # so the dashboard can show them, then check whether the user has
        # approved them. Render is blocked until ready_to_render=True
        # unless the regression / CI runner opts into auto-approval.
        from .. import scenario_review as _sr
        m014 = inputs.get("motor_014", {}) if isinstance(inputs.get("motor_014", {}), dict) else {}
        case_meta_for_review = report_package.get("case_metadata", {}) if isinstance(report_package.get("case_metadata", {}), dict) else {}
        case_id_for_review = str(case_meta_for_review.get("case_id") or "").strip()
        case_family_for_review = ""
        m061_safe = inputs.get("motor_061", {}) if isinstance(inputs.get("motor_061", {}), dict) else {}
        case_family_for_review = str(m061_safe.get("asset_family_evaluated") or "").strip()
        scenarios_for_review = list(m014.get("scenario_space", []) or [])
        # Detect bypass mode (regression / CI). Two ways to bypass:
        #   1. __pipeline__.scenario_review_mode = "auto"
        #   2. env var ZLAB_AUTO_APPROVE_SCENARIOS=1
        review_mode = str(pipeline_inputs.get("scenario_review_mode") or "").strip().lower()
        env_bypass = os.environ.get("ZLAB_AUTO_APPROVE_SCENARIOS", "").strip() == "1"
        auto_approve = review_mode == "auto" or env_bypass
        scenario_review_blocked = False
        scenario_review_summary: dict[str, Any] = {}
        if case_id_for_review and scenarios_for_review:
            try:
                if auto_approve:
                    review_state = _sr.auto_approve_for_regression(
                        case_id_for_review,
                        scenarios_for_review,
                        asset_family=case_family_for_review,
                    )
                else:
                    review_state = _sr.upsert_scenarios(
                        case_id_for_review,
                        scenarios_for_review,
                        asset_family=case_family_for_review,
                    )
                    review_state = _sr.get_case(case_id_for_review)
                ready = bool(review_state.get("ready_to_render"))
                pending_count = sum(
                    1 for sc in (review_state.get("scenarios") or {}).values()
                    if str(sc.get("state") or "pending") in {"pending", "edited"}
                )
                scenario_review_summary = {
                    "case_id": case_id_for_review,
                    "ready_to_render": ready,
                    "pending_count": pending_count,
                    "mode": "auto" if auto_approve else "manual",
                }
                if not ready:
                    scenario_review_blocked = True
                    block_reasons.append(
                        f"Scenario review pending — {pending_count} scenario(s) "
                        f"awaiting human approval in the dashboard. Open "
                        f"http://localhost:7474/scenarios and approve/reject/edit "
                        f"each one. Case: {case_id_for_review}."
                    )
            except Exception as exc:  # noqa: BLE001 - never crash the pipeline on review errors
                log.warning(
                    "[motor_017] scenario_review seeding/check failed for case %s: %s",
                    case_id_for_review,
                    exc,
                )

        if block_reasons and not force_render_under_warnings:
            return {
                "pdf_path": "",
                "pdf_paths": {},
                "compilation_status": "blocked",
                "render_job_id": "",
                "package_id": report_package.get("package_id", "unknown"),
                "available_languages": ["en"],
                "gold_nugget_authority_state": gold_nugget_authority_state,
                "gold_nugget_source_register": gold_nugget_source_register,
                "blocking_reason": " | ".join(block_reasons)[:1000],
                "consistency_summary": consistency_summary,
                "asset_family_isolation_summary": {
                    "contamination_detected": family_contamination,
                    "warning_count": int(m061.get("warning_count", 0) or 0),
                    "critical_count": int(m061.get("critical_count", 0) or 0),
                },
                "chart_validity_summary": {
                    "chart_contamination_detected": chart_contamination,
                    "warning_count": int(m063.get("warning_count", 0) or 0),
                    "critical_count": int(m063.get("critical_count", 0) or 0),
                },
                "scenario_justification_summary": {
                    "scenario_justification_failed": scenario_justification_failed,
                    "warning_count": int(m062.get("warning_count", 0) or 0),
                    "critical_count": int(m062.get("critical_count", 0) or 0),
                    "mode": str(m062.get("mode") or "warn"),
                },
                "scenario_review_summary": scenario_review_summary,
                # V3 G1: surface validator 055-059 summaries when blocking
                "hypothesis_diversity_summary": {
                    "warning_count": int(m055.get("warning_count", 0) or 0),
                    "rules_evaluated": list(m055.get("rules_evaluated", []) or []),
                },
                "evidence_repetition_summary": {
                    "warning_count": int(m056.get("warning_count", 0) or 0),
                    "rules_evaluated": list(m056.get("rules_evaluated", []) or []),
                },
                "gold_nugget_quality_summary": {
                    "warning_count": int(m057.get("warning_count", 0) or 0),
                    "nugget_count_evaluated": int(m057.get("nugget_count_evaluated", 0) or 0),
                    "rules_evaluated": list(m057.get("rules_evaluated", []) or []),
                },
                "report_uniqueness_summary": {
                    "warning_count": int(m058.get("warning_count", 0) or 0),
                    "prior_runs_compared": int(m058.get("prior_runs_compared", 0) or 0),
                    "rules_evaluated": list(m058.get("rules_evaluated", []) or []),
                },
                "strategic_intelligence_summary": {
                    "warning_count": int(m059.get("warning_count", 0) or 0),
                    "warning_count_by_severity": dict(m059.get("warning_count_by_severity", {}) or {}),
                    "rules_evaluated": list(m059.get("rules_evaluated", []) or []),
                },
            }

        meta      = report_package.get("case_metadata", {})
        case_id   = meta.get("case_id", "unknown")
        pkg_id    = report_package.get("package_id", "unknown")
        constraint = report_package.get("framework_constraint", "")
        governance_summary = report_package.get("governance_summary", {})
        context_integrity_scan = report_package.get("context_integrity_scan", {})
        meta_with_governance = {
            **meta,
            "document_type": report_package.get("document_type", meta.get("document_type", "Asset Decision-Admissibility Brief")),
            "publication_ceiling": report_package.get("publication_ceiling", meta.get("publication_ceiling", "publish_bounded")),
            "traceability_chain_complete": governance_summary.get("traceability_chain_complete", False),
        }

        approved_views = report_package.get("approved_views", {})
        primary_view_key = report_package.get("primary_view_key", "report_view")
        report_view = approved_views.get(primary_view_key) or approved_views.get("report_view") or approved_views.get("tdir_view", {})
        body_sections = _hydrated_system_consistency_section(
            list(report_view.get("body_sections", []) or []),
            consistency_summary,
        )
        appendix_sections = report_view.get("appendix_sections", [])
        render_section_contract = dict(report_package.get("render_section_contract", {}) or {})
        llm_model = report_view.get("llm_model", "")
        document_type = report_package.get("document_type", report_view.get("document_type", "Asset Decision-Admissibility Brief"))
        if context_integrity_scan and not context_integrity_scan.get("render_eligible", True):
            issues = context_integrity_scan.get("issues", [])
            issue_summary = "; ".join(issue.get("message", "integrity issue") for issue in issues[:4])
            if not force_render_under_warnings:
                raise ValueError(
                    "Report rendering blocked by context integrity scan: "
                    + (issue_summary or "unknown integrity issue")
                )
            log.warning(
                "[motor_017] context integrity scan flagged %d issues but "
                "__force_render__ is set; proceeding. Issue summary: %s",
                len(issues),
                issue_summary[:200],
            )
        try:
            _validate_render_section_contract(render_section_contract, body_sections, appendix_sections)
        except ValueError as exc:
            if not force_render_under_warnings:
                raise
            log.warning(
                "[motor_017] render section contract violated but "
                "__force_render__ is set; proceeding. Reason: %s",
                str(exc)[:300],
            )

        # Output job directory
        render_id = f"motor_017_render_job_{pkg_id}"
        job_dir   = _OUTPUT_DIR / render_id
        if job_dir.exists():
            shutil.rmtree(job_dir)
        job_dir.mkdir(parents=True, exist_ok=True)

        # Copy entire template to job directory
        if _TEMPLATE_DIR.exists():
            for item in _TEMPLATE_DIR.iterdir():
                dest = job_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

        # Ensure required subdirs exist
        for subdir in ("Metadata", "Chapters", "Bibliography", "Matter", "Configurations",
                       "Figures/Charts"):
            (job_dir / subdir).mkdir(parents=True, exist_ok=True)
        _reset_governed_chapters_dir(job_dir / "Chapters")

        # Empty bibliography (avoids biber/biblatex errors if loaded)
        bib_file = job_dir / "Bibliography" / "References.bib"
        if not bib_file.exists():
            bib_file.write_text("")

        # Override 00-Fonts.sty with absolute font paths (TeX Live fonts not in fc-cache)
        _TEXLIVE_OTF = "/usr/local/texlive/2026/texmf-dist/fonts/opentype"
        _TEXLIVE_TTF = "/usr/local/texlive/2026/texmf-dist/fonts/truetype"
        fonts_sty = (
            "%%% Fonts — ZLab override (uses TeX Live font file paths) %%%\n"
            "\\usepackage[T1]{fontenc}\n"
            "\\usepackage{newpxmath}\n"
            "\\usepackage{fvextra}\n"
            "\\usepackage{csquotes}\n"
            "\\usepackage{fontspec}\n"
            "\\linespread{1.2}\n"
            f"\\setmainfont{{texgyrepagella-regular.otf}}[\n"
            f"  Path={_TEXLIVE_OTF}/public/tex-gyre/,\n"
            "  BoldFont=texgyrepagella-bold.otf,\n"
            "  ItalicFont=texgyrepagella-italic.otf,\n"
            "  BoldItalicFont=texgyrepagella-bolditalic.otf,\n"
            "  Ligatures=TeX, LetterSpace=0.7\n"
            "]\n"
            f"\\newcommand{{\\garamondfont}}{{\\fontspec[Path={_TEXLIVE_OTF}/public/ebgaramond/]{{EBGaramond-Regular.otf}}}}\n"
            f"\\newcommand{{\\latofont}}{{\\fontspec[Path={_TEXLIVE_TTF}/typoland/lato/]{{Lato-Regular.ttf}}}}\n"
            f"\\newcommand{{\\crimsonfont}}{{\\fontspec[Path={_TEXLIVE_OTF}/kosch/crimson/,LetterSpace=-0.5]{{Crimson-Roman.otf}}}}\n"
        )
        (job_dir / "Configurations" / "00-Fonts.sty").write_text(fonts_sty, encoding="utf-8")

        # Save chart PNGs and build section → relative path list map
        _chart_png_map: dict[str, str] = {}
        _chart_png_list_map: dict[str, list[str]] = {}
        for sec in body_sections + appendix_sections:
            sid = sec.get("section_id", sec.get("chapter_id", "unknown"))
            b64_list = sec.get("chart_b64_list") or (
                [sec["chart_b64"]] if sec.get("chart_b64") else []
            )
            saved: list[str] = []
            for idx, b64 in enumerate(b64_list):
                if not b64:
                    continue
                suffix = f"_{idx}" if idx > 0 else ""
                png_dest = job_dir / "Figures" / "Charts" / f"{sid}{suffix}.png"
                if _save_chart_png(b64, png_dest):
                    saved.append(f"Figures/Charts/{sid}{suffix}.png")
            if saved:
                _chart_png_map[sid] = saved[0]
                _chart_png_list_map[sid] = saved

        available_languages = report_view.get("available_languages") or ["en"]
        case_slug = re.sub(r"[^\w\-]", "-", case_id).strip("-").lower()
        document_slug = _document_slug(document_type)
        pdf_paths: dict[str, str] = {}
        compile_log = ""
        compile_success = False
        planned_chapter_inventory = dict(report_package.get("planned_chapter_inventory", {}) or {})
        expected_chapter_files = list(planned_chapter_inventory.get("chapter_files", []) or [])

        def _render_language(language: str) -> Path:
            (job_dir / "Metadata" / "Metadata.tex").write_text(
                _metadata_tex(meta_with_governance, language=language), encoding="utf-8"
            )
            (job_dir / "Matter" / "01-Front-Page.tex").write_text(
                _frontpage_tex(meta_with_governance, language=language), encoding="utf-8"
            )
            (job_dir / "Matter" / "02-Copyright.tex").write_text(
                _copyright_tex({**meta, "framework_constraint": constraint}, language=language),
                encoding="utf-8",
            )
            (job_dir / "Chapters" / "00-Brief.tex").write_text(
                _abstract_tex(body_sections, governance_summary, document_type=document_type, language=language), encoding="utf-8"
            )

            for sec in body_sections:
                chapter_id = sec.get("chapter_id", "CX")
                sid = sec.get("section_id", chapter_id)
                tex_content = _chapter_tex(
                    sec,
                    chapter_id,
                    chart_png_rel=_chart_png_map.get(sid, ""),
                    chart_png_rel_list=_chart_png_list_map.get(sid),
                    language=language,
                )
                (job_dir / "Chapters" / f"{chapter_id}.tex").write_text(tex_content, encoding="utf-8")

            for sec in appendix_sections:
                chapter_id = sec.get("chapter_id", "AX")
                sid = sec.get("section_id", chapter_id)
                tex_content = _chapter_tex(
                    sec,
                    chapter_id,
                    chart_png_rel=_chart_png_map.get(sid, ""),
                    chart_png_rel_list=_chart_png_list_map.get(sid),
                    language=language,
                )
                (job_dir / "Chapters" / f"{chapter_id}.tex").write_text(tex_content, encoding="utf-8")

            written_chapters = _written_chapter_inventory(job_dir / "Chapters")
            if expected_chapter_files and written_chapters != sorted(expected_chapter_files):
                raise ValueError(
                    "Governed chapter inventory mismatch before render: "
                    f"expected {sorted(expected_chapter_files)} got {written_chapters}"
                )

            (job_dir / "main.tex").write_text(
                _main_tex(body_sections, appendix_sections, llm_model, constraint, document_type=document_type, language=language),
                encoding="utf-8",
            )

            xelatex_cmd = [
                "xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "main.tex",
            ]
            nonlocal compile_log
            for _pass in range(2):
                result = subprocess.run(
                    xelatex_cmd,
                    cwd=str(job_dir),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                compile_log = result.stdout[-3000:] if result.stdout else ""
                if result.returncode != 0:
                    (job_dir / f"xelatex.{language}.log.txt").write_text(
                        result.stdout + "\n" + result.stderr, encoding="utf-8"
                    )
                    raise RuntimeError(
                        f"xelatex[{language}] pass {_pass+1} failed (exit {result.returncode}).\n"
                        f"Log tail: {compile_log[-800:]}"
                    )
            raw_pdf = job_dir / "main.pdf"
            suffix = f"_{language}" if len(available_languages) > 1 else ""
            pdf_name = f"{case_slug}_{document_slug}{suffix}.pdf" if case_slug else f"{document_slug}{suffix}.pdf"
            pdf_path = job_dir / pdf_name
            if raw_pdf.exists():
                raw_pdf.replace(pdf_path)
            return pdf_path

        for language in available_languages:
            rendered_pdf = _render_language(language)
            pdf_paths[language] = str(rendered_pdf)
        compile_success = True

        primary_pdf = pdf_paths.get("en") or next(iter(pdf_paths.values()), "")
        return {
            "pdf_path": primary_pdf,
            "pdf_paths": pdf_paths,
            "compilation_status": "success" if compile_success else "failed",
            "render_job_id": render_id,
            "package_id": pkg_id,
            "available_languages": available_languages,
            "gold_nugget_authority_state": gold_nugget_authority_state,
            "gold_nugget_source_register": gold_nugget_source_register,
            "written_chapter_inventory": _written_chapter_inventory(job_dir / "Chapters"),
        }
