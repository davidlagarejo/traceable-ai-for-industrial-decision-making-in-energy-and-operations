"""Adapter for motor_018 — Chart Generation Engine.

Generates publication-quality analytical charts from pipeline data.
Each chart is designed to explain a specific analytical finding visually.

Chart inventory is asset-first:
  1. chart_asset_context_completeness — observable cluster coverage
  2. chart_source_scope_balance       — asset vs issuer/source scope mix
  3. chart_context_routing_status     — geocode / jurisdiction / climate / benchmark routing
  4. chart_system_typology_prior      — expected technical subsystems
  5. chart_inference_scores           — P/R/V scores for all inference cases
  6. chart_validation_priority        — urgency ranking
"""
from __future__ import annotations

import base64
import io
import re
from typing import Any

from ..chart_taxonomy import (
    CHART_TAXONOMY_CATALOG_VERSION,
    chart_category,
    chart_intent,
    chart_lane,
)
from ..congruence_intelligence.case_isolation import (
    build_case_namespace_register,
    stamp_chart_asset_case_context,
)
from .base import BaseMotorAdapter

_MAROON  = "#6A2E3E"
_RED     = "#B41E32"
_NAVY    = "#1A3A5C"
_GREEN   = "#2E7D32"
_AMBER   = "#F57C00"
_PURPLE  = "#5E35B1"
_TEAL    = "#00838F"
_LGRAY   = "#EEEEEE"
_DARK    = "#222222"

_PALETTE = [_MAROON, _NAVY, _GREEN, _AMBER, _PURPLE, _TEAL, _RED]


def _shorten(value: Any, limit: int = 120) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _chart_copy(chart_id: str, *, curation_mode: str = "structural") -> dict[str, str]:
    copies = {
        "chart_congruence_binding_state": {
            "structural": {
                "title_en": "Thesis Binding State",
                "title_es": "Estado de Amarre de la Tesis",
                "description_en": "Which congruence claims are already locally bounded strongly enough to support the thesis versus still only screening-grade",
                "description_es": "Qué claims de congruencia ya están acotados localmente con fuerza suficiente para sostener la tesis y cuáles siguen en nivel screening",
            },
            "exploratory": {
                "title_en": "Congruence Binding State",
                "title_es": "Estado de Amarre de Congruencia",
                "description_en": "Which congruence claims are locally bounded enough to survive screening versus still only prior-like",
                "description_es": "Qué claims de congruencia ya están lo bastante acotados localmente para sobrevivir el screening y cuáles siguen pareciéndose a un prior",
            },
            "blocked": {
                "title_en": "Screening-Grade Binding State",
                "title_es": "Estado de Amarre en Nivel Screening",
                "description_en": "Which congruence claims remain only screening-grade and therefore cannot yet support a stronger technical brief",
                "description_es": "Qué claims de congruencia siguen solo en nivel screening y por eso todavía no sostienen un brief técnico más fuerte",
            },
        },
        "chart_fair_comparison_gate": {
            "structural": {
                "title_en": "Peer Comparison Trust Gate",
                "title_es": "Filtro de Confianza para Comparación con Pares",
                "description_en": "Normalization requirements that must be satisfied before peer logic is allowed to shape the thesis",
                "description_es": "Normalizaciones que deben cumplirse antes de permitir que la lógica de pares moldee la tesis",
            },
            "exploratory": {
                "title_en": "Benchmark Trust Gate",
                "title_es": "Filtro de Confianza para Benchmark",
                "description_en": "Normalization requirements that must be satisfied before benchmark logic is even trusted for screening",
                "description_es": "Normalizaciones que deben cumplirse antes de confiar siquiera en la lógica de benchmark para screening",
            },
            "blocked": {
                "title_en": "Benchmark Invalidity Gate",
                "title_es": "Filtro de Invalidez del Benchmark",
                "description_en": "Normalization gaps that keep benchmark or peer logic from being decision-relevant yet",
                "description_es": "Brechas de normalización que todavía impiden que la lógica de benchmark o pares sea relevante para decidir",
            },
        },
        "chart_cross_layer_congruence_map": {
            "structural": {
                "title_en": "Dominant Cross-Layer Contradiction",
                "title_es": "Contradicción Dominante entre Capas",
                "description_en": "Where the dominant contradiction crosses layers and becomes the thesis driver",
                "description_es": "Dónde la contradicción dominante cruza capas y se vuelve el driver de la tesis",
            },
            "exploratory": {
                "title_en": "Cross-Layer Screening Conflict",
                "title_es": "Conflicto de Screening entre Capas",
                "description_en": "Where the screening problem frame breaks across layers before deeper technical modeling",
                "description_es": "Dónde el encuadre del problema en screening se rompe entre capas antes de profundizar el modelado técnico",
            },
            "blocked": {
                "title_en": "Cross-Layer Blocking Conflict",
                "title_es": "Conflicto Bloqueante entre Capas",
                "description_en": "Where a cross-layer inconsistency is already strong enough to block stronger claims",
                "description_es": "Dónde una inconsistencia entre capas ya es lo bastante fuerte como para bloquear claims más fuertes",
            },
        },
        "chart_measurement_minimality_path": {
            "structural": {
                "title_en": "Minimum Evidence Before Escalation",
                "title_es": "Evidencia Mínima antes de Escalar",
                "description_en": "Cheapest valid evidence path that can discriminate the dominant contradiction before hardware escalation",
                "description_es": "Ruta de evidencia válida más barata que puede discriminar la contradicción dominante antes de escalar a hardware",
            },
            "exploratory": {
                "title_en": "Minimum Evidence Before Technical Deepening",
                "title_es": "Evidencia Mínima antes de Profundizar",
                "description_en": "Cheapest valid evidence path before broad instrumentation or premature technical deepening",
                "description_es": "Ruta de evidencia válida más barata antes de instrumentación amplia o profundización técnica prematura",
            },
            "blocked": {
                "title_en": "Minimum Evidence Before New Instrumentation",
                "title_es": "Evidencia Mínima antes de Nueva Instrumentación",
                "description_en": "Cheapest valid evidence path before the case is allowed to ask for broader instrumentation",
                "description_es": "Ruta de evidencia válida más barata antes de permitir que el caso pida instrumentación más amplia",
            },
        },
        "chart_cost_driver_signal_profile": {
            "structural": {
                "title_en": "Capital Logic Signal Profile",
                "title_es": "Perfil de Señales de Lógica de Capital",
                "description_en": "Which cost-driver frame is strong enough to change the capital reading of the case",
                "description_es": "Qué encuadre del driver de costo es lo bastante fuerte como para cambiar la lectura de capital del caso",
            },
            "exploratory": {
                "title_en": "Cost Driver Signal Profile",
                "title_es": "Perfil de Señales del Driver de Costo",
                "description_en": "Which cost-driver frame is tentatively surfacing before the case is treated as decision-grade",
                "description_es": "Qué encuadre del driver de costo está emergiendo tentativamente antes de tratar el caso como decision-grade",
            },
            "blocked": {
                "title_en": "Premature Cost Framing Signal",
                "title_es": "Señal de Encuadre Prematuro de Costos",
                "description_en": "Which cost signals appear first but still remain too weak to justify stronger economic claims",
                "description_es": "Qué señales de costo aparecen primero pero todavía son demasiado débiles para justificar claims económicos más fuertes",
            },
        },
        "chart_gap_taxonomy_profile": {
            "blocked": {
                "title_en": "Blocking Gap Taxonomy",
                "title_es": "Taxonomía de Brechas Bloqueantes",
                "description_en": "Which evidence-gap classes are actually blocking the case right now instead of collapsing all missingness into one bucket",
                "description_es": "Qué clases de brecha de evidencia están bloqueando de verdad el caso ahora, en lugar de colapsar toda la falta de información en un solo bloque",
            },
            "exploratory_support": {
                "title_en": "Gap Taxonomy Profile",
                "title_es": "Perfil de Taxonomía de Brechas",
                "description_en": "How the case's uncertainty splits across comparability, operational context, control, tariff, maintenance, and identity gaps",
                "description_es": "Cómo la incertidumbre del caso se reparte entre brechas de comparabilidad, contexto operacional, control, tarifa, mantenimiento e identidad",
            },
            "structural_support": {
                "title_en": "Supporting Gap Taxonomy",
                "title_es": "Taxonomía de Brechas de Soporte",
                "description_en": "Which gap classes still sit under the structural thesis and what kind of evidence they still require",
                "description_es": "Qué clases de brecha siguen debajo de la tesis estructural y qué tipo de evidencia siguen requiriendo",
            },
        },
        "chart_next_best_search_path": {
            "blocked": {
                "title_en": "Next Search Targets Before Escalation",
                "title_es": "Próximas Búsquedas Antes de Escalar",
                "description_en": "What should still be searched publicly before asking the operator for more data",
                "description_es": "Qué conviene seguir buscando en público antes de pedir más datos al operador",
            },
            "exploratory_support": {
                "title_en": "Next-Best Search Path",
                "title_es": "Ruta de Próxima Mejor Búsqueda",
                "description_en": "Which search targets have the best remaining payoff before the case should escalate to local intake",
                "description_es": "Qué targets de búsqueda tienen el mejor retorno restante antes de que el caso deba escalar a intake local",
            },
            "structural_support": {
                "title_en": "Supporting Search Path",
                "title_es": "Ruta de Búsqueda de Soporte",
                "description_en": "Which search paths still matter under the thesis and how they connect to stop and downgrade conditions",
                "description_es": "Qué rutas de búsqueda todavía importan debajo de la tesis y cómo se conectan con condiciones de stop y downgrade",
            },
        },
        "chart_peer_requirement_readiness": {
            "blocked": {
                "title_en": "Peer Requirement Blockers",
                "title_es": "Bloqueadores de Requisitos de Pares",
                "description_en": "Which peer requirements are still blocked and therefore prohibit peer or benchmark claims",
                "description_es": "Qué requisitos de pares siguen bloqueados y por eso prohíben claims de benchmark o de pares",
            },
            "exploratory_support": {
                "title_en": "Peer Requirement Readiness",
                "title_es": "Preparación de Requisitos de Pares",
                "description_en": "Which peer requirements are already bounded and which still block a fair comparison frame",
                "description_es": "Qué requisitos de pares ya están acotados y cuáles todavía bloquean un frame de comparación justa",
            },
            "structural_support": {
                "title_en": "Supporting Peer Readiness",
                "title_es": "Preparación de Pares de Soporte",
                "description_en": "Which comparison requirements still sit under the structural reading before peer logic becomes defensible",
                "description_es": "Qué requisitos de comparación siguen debajo de la lectura estructural antes de que la lógica de pares sea defendible",
            },
        },
        "chart_asset_context_completeness": {
            "blocked": {
                "title_en": "Physical Context Coverage",
                "title_es": "Cobertura del Contexto Físico",
                "description_en": "Which physical context clusters are still missing and therefore keep the case at a blocked or pre-verification level",
                "description_es": "Qué clusters de contexto físico todavía faltan y por eso mantienen el caso en nivel bloqueado o de pre-verificación",
            },
            "exploratory_support": {
                "title_en": "Asset Context Completeness",
                "title_es": "Completitud del Contexto del Activo",
                "description_en": "Coverage of the physical observable clusters that support a stronger exploratory reading of the asset",
                "description_es": "Cobertura de los clusters observables físicos que sostienen una lectura exploratoria más fuerte del activo",
            },
            "structural_support": {
                "title_en": "Asset Context Support Coverage",
                "title_es": "Cobertura de Soporte del Contexto del Activo",
                "description_en": "Coverage of the physical observable clusters that support the structural thesis but remain subordinate to the main body logic",
                "description_es": "Cobertura de los clusters observables físicos que soportan la tesis estructural pero siguen subordinados a la lógica principal del body",
            },
        },
        "chart_source_scope_balance": {
            "blocked": {
                "title_en": "Scope Mismatch Exposure",
                "title_es": "Exposición por Desalineación de Alcance",
                "description_en": "Whether the case is still being driven by issuer or context evidence instead of bounded asset evidence",
                "description_es": "Si el caso todavía está siendo empujado por evidencia del emisor o de contexto en lugar de evidencia acotada del activo",
            },
            "exploratory_support": {
                "title_en": "Source Scope Balance",
                "title_es": "Balance del Alcance de Fuentes",
                "description_en": "How much of the reading is being driven by asset, jurisdiction, and issuer scopes during exploratory work",
                "description_es": "Cuánto de la lectura está siendo empujado por alcances de activo, jurisdicción y emisor durante el trabajo exploratorio",
            },
            "structural_support": {
                "title_en": "Supporting Source Scope Balance",
                "title_es": "Balance de Alcance de Fuentes de Soporte",
                "description_en": "How much of the supporting evidence still depends on issuer or context scope instead of direct asset scope",
                "description_es": "Cuánto de la evidencia de soporte todavía depende del alcance del emisor o del contexto en vez del alcance directo del activo",
            },
        },
        "chart_context_routing_status": {
            "blocked": {
                "title_en": "Routing Readiness Gate",
                "title_es": "Filtro de Preparación de Enrutamiento",
                "description_en": "Whether address, jurisdiction, climate, and benchmark routing are strong enough to justify any technical expectation yet",
                "description_es": "Si dirección, jurisdicción, clima y enrutamiento de benchmark ya son lo bastante fuertes como para justificar alguna expectativa técnica",
            },
            "exploratory_support": {
                "title_en": "Context Routing Status",
                "title_es": "Estado del Enrutamiento de Contexto",
                "description_en": "Address, jurisdiction, climate, and benchmark routing readiness that frames the exploratory reading",
                "description_es": "Preparación de dirección, jurisdicción, clima y benchmark que enmarca la lectura exploratoria",
            },
            "structural_support": {
                "title_en": "Supporting Routing Context",
                "title_es": "Contexto de Enrutamiento de Soporte",
                "description_en": "Address, jurisdiction, climate, and benchmark routing context that supports the structural thesis without dominating it",
                "description_es": "Contexto de dirección, jurisdicción, clima y benchmark que soporta la tesis estructural sin dominarla",
            },
        },
        "chart_system_typology_prior": {
            "blocked": {
                "title_en": "Expected System Prior",
                "title_es": "Prior del Sistema Esperado",
                "description_en": "Expected system families inferred from asset type before any claim is treated as field-confirmed",
                "description_es": "Familias de sistemas esperadas inferidas desde el tipo de activo antes de tratar cualquier claim como confirmado en campo",
            },
            "exploratory_support": {
                "title_en": "System Typology Prior",
                "title_es": "Prior de Tipología del Sistema",
                "description_en": "Expected system families inferred from asset type and energy archetype to support exploratory framing",
                "description_es": "Familias de sistemas esperadas inferidas desde el tipo de activo y el arquetipo energético para soportar el framing exploratorio",
            },
            "structural_support": {
                "title_en": "System Typology Support Prior",
                "title_es": "Prior de Soporte de Tipología del Sistema",
                "description_en": "Expected system families that support the structural thesis but still remain archetypal rather than field-confirmed",
                "description_es": "Familias de sistemas esperadas que soportan la tesis estructural pero siguen siendo arquetípicas y no confirmadas en campo",
            },
        },
        "chart_investment_uncertainty_map": {
            "default": {
                "title_en": "Investment Uncertainty Map",
                "title_es": "Mapa de Incertidumbre de Inversión",
                "description_en": "The critical uncertainties that still block stronger capital-facing reasoning",
                "description_es": "Las incertidumbres críticas que todavía bloquean una lógica de capital más fuerte",
            },
        },
        "chart_minimum_evidence_pack": {
            "default": {
                "title_en": "Minimum Evidence Pack",
                "title_es": "Paquete de Evidencia Mínima",
                "description_en": "Ordered evidence items that unlock the largest decision value first",
                "description_es": "Ítems de evidencia ordenados por el valor de decisión que desbloquean primero",
            },
        },
        "chart_decision_front_status": {
            "default": {
                "title_en": "Decision Front Status",
                "title_es": "Estado del Frente de Decisión",
                "description_en": "What can be acted on now, what must be validated, and what remains blocked",
                "description_es": "Qué se puede actuar ahora, qué debe validarse y qué sigue bloqueado",
            },
        },
        "chart_scenario_space": {
            "default": {
                "title_en": "Scenario Space",
                "title_es": "Espacio de Escenarios",
                "description_en": "Conditional futures under the current uncertainty state",
                "description_es": "Futuros condicionales bajo el estado actual de incertidumbre",
            },
        },
        "chart_inference_scores": {
            "default": {
                "title_en": "Inference Case Score Matrix",
                "title_es": "Matriz de Puntaje de Casos de Inferencia",
                "description_en": "Grouped bars showing plausibility, relevance, and validation scores for all inference cases",
                "description_es": "Barras agrupadas que muestran plausibilidad, relevancia y puntajes de validación para todos los casos de inferencia",
            },
        },
        "chart_validation_priority": {
            "default": {
                "title_en": "Validation Priority Ranking",
                "title_es": "Ranking de Prioridad de Validación",
                "description_en": "Horizontal ranking of which questions deserve validation first",
                "description_es": "Ranking horizontal de qué preguntas merecen validación primero",
            },
        },
        "chart_revenue_trend": {
            "default": {
                "title_en": "Revenue Trend",
                "title_es": "Tendencia de Ingresos",
                "description_en": "Annual revenue context from consolidated public reporting",
                "description_es": "Contexto anual de ingresos desde reporte público consolidado",
            },
        },
        "chart_revenue_composition": {
            "default": {
                "title_en": "Revenue Composition Estimate",
                "title_es": "Estimación de Composición de Ingresos",
                "description_en": "Indicative revenue mix derived from declared use mix rather than confirmed segment reporting",
                "description_es": "Mix indicativo de ingresos derivado del mix de usos declarado y no de segmentación confirmada",
            },
        },
        "chart_debt_discrepancy": {
            "default": {
                "title_en": "Debt Context Comparison",
                "title_es": "Comparación de Contexto de Deuda",
                "description_en": "Reported debt versus public leverage signal when both are visible",
                "description_es": "Deuda reportada versus señal pública de apalancamiento cuando ambas son visibles",
            },
        },
        "chart_tenant_concentration": {
            "default": {
                "title_en": "Tenant Concentration",
                "title_es": "Concentración de Inquilinos",
                "description_en": "Quick concentration view of anchor and major tenant dependence",
                "description_es": "Vista rápida de concentración de dependencia en anchor y principales inquilinos",
            },
        },
        "chart_ll97_scenario": {
            "default": {
                "title_en": "LL97 Penalty Exposure Scenarios",
                "title_es": "Escenarios de Exposición a Penalidades LL97",
                "description_en": "Bounded annual penalty scenarios under optimistic, moderate, and conservative emissions assumptions",
                "description_es": "Escenarios acotados de penalidad anual bajo supuestos optimistas, moderados y conservadores de emisiones",
            },
        },
        "chart_evidence_ladder": {
            "default": {
                "title_en": "Evidence Ladder",
                "title_es": "Escalera de Evidencia",
                "description_en": "Plausibility versus epistemic gap across inference cases",
                "description_es": "Plausibilidad versus brecha epistémica a través de los casos de inferencia",
            },
        },
        "chart_validation_effort_matrix": {
            "default": {
                "title_en": "Validation Effort Matrix",
                "title_es": "Matriz de Esfuerzo de Validación",
                "description_en": "Decision impact versus validation effort for the current case map",
                "description_es": "Impacto de decisión versus esfuerzo de validación para el mapa actual del caso",
            },
        },
        "chart_ll97_timeline": {
            "default": {
                "title_en": "LL97 Compliance Timeline",
                "title_es": "Línea de Tiempo de Cumplimiento LL97",
                "description_en": "Compliance windows and penalty ramp over time",
                "description_es": "Ventanas de cumplimiento y rampa de penalidades en el tiempo",
            },
        },
        "chart_causal_dependency": {
            "default": {
                "title_en": "Causal Dependency Map",
                "title_es": "Mapa de Dependencias Causales",
                "description_en": "Overlap of evidence dependencies across inference cases",
                "description_es": "Solapamiento de dependencias de evidencia entre casos de inferencia",
            },
        },
        "chart_scenario_decision": {
            "default": {
                "title_en": "Scenario Decision Matrix",
                "title_es": "Matriz de Decisión por Escenarios",
                "description_en": "How different resolution paths change the decision space",
                "description_es": "Cómo distintas rutas de resolución cambian el espacio de decisión",
            },
        },
    }
    family = copies.get(chart_id, {})
    selected = dict(
        family.get(curation_mode, family.get("default", family.get("structural", {})))
    )
    if not selected:
        fallback_title = chart_id.replace("chart_", "").replace("_", " ").title()
        return {
            "title_en": fallback_title,
            "title_es": fallback_title,
            "description_en": "",
            "description_es": "",
        }
    selected["title"] = selected.get("title_en", "")
    selected["description"] = selected.get("description_en", "")
    return selected


def _chart_story(chart_id: str, *, curation_mode: str = "default") -> dict[str, str]:
    stories = {
        "chart_congruence_binding_state": {
            "chart_role": (
                "Show which congruence claims are already bounded strongly enough to support the thesis."
                if curation_mode == "structural"
                else "Show which congruence claims are bounded enough for screening and which remain only prior-like."
            ),
            "reader_takeaway": (
                "The point is to separate thesis-grade local truth from weaker screening-grade support."
                if curation_mode == "structural"
                else "The point is to separate a bounded screening read from a merely plausible structural prior."
            ),
            "text_pairing_guidance": (
                "Use the prose to explain which claims now carry thesis weight and which still need binding evidence."
                if curation_mode == "structural"
                else "Use the prose to explain which claims are already bounded enough for screening and which still need local binding."
            ),
        },
        "chart_fair_comparison_gate": {
            "chart_role": (
                "Show what must be normalized before peer logic is allowed to influence the thesis."
                if curation_mode == "structural"
                else "Show what must be normalized before benchmark logic is even trusted for screening."
            ),
            "reader_takeaway": "The reader should see immediately why area-only or whole-building comparison can be structurally invalid.",
            "text_pairing_guidance": (
                "Use the prose to explain the top invalid comparison risk and the missing normalizations that still block thesis-grade peer logic."
                if curation_mode == "structural"
                else "Use the prose to explain the top invalid comparison risk and the one or two missing normalizations that matter most."
            ),
        },
        "chart_cross_layer_congruence_map": {
            "chart_role": (
                "Show where the contradiction crosses layers and becomes the thesis driver."
                if curation_mode == "structural"
                else "Show where the screening problem frame breaks across layers rather than living inside one subsystem."
            ),
            "reader_takeaway": "This chart should make the case feel like a system-boundary problem, not a single-variable problem.",
            "text_pairing_guidance": (
                "Use the prose to explain the dominant contradiction first and subordinate secondary ones to its capital or control consequences."
                if curation_mode == "structural"
                else "Use the prose to explain the dominant contradiction first and the secondary ones only if they materially change action."
            ),
        },
        "chart_measurement_minimality_path": {
            "chart_role": (
                "Show the cheapest valid evidence path before hardware escalation."
                if curation_mode == "structural"
                else "Show the cheapest valid evidence path before premature technical deepening."
            ),
            "reader_takeaway": "The next move should look like a bounded evidence request, not a reflex instrumentation rollout.",
            "text_pairing_guidance": (
                "Use the prose to explain why the first evidence request discriminates the dominant contradiction more cheaply than broad sensing."
                if curation_mode == "structural"
                else "Use the prose to explain why the first evidence request discriminates more value than broad sensing."
            ),
        },
        "chart_cost_driver_signal_profile": {
            "chart_role": (
                "Show what kind of cost logic is strong enough to change the capital reading of the case."
                if curation_mode == "structural"
                else "Show what kind of cost logic is actually surfacing in the case signals."
            ),
            "reader_takeaway": "The reader should see whether the case smells more like tariff, boundary, duty or maintenance logic than generic consumption logic.",
            "text_pairing_guidance": (
                "Use the prose to explain why the leading cost driver signal changes the capital reading rather than merely the energy narrative."
                if curation_mode == "structural"
                else "Use the prose to explain why the leading cost driver signal changes the framing of the case."
            ),
        },
        "chart_gap_taxonomy_profile": {
            "chart_role": "Show that not all missing evidence is the same kind of blocker.",
            "reader_takeaway": "The case is blocked by a specific mix of comparability, operational, control, tariff, maintenance, or identity gaps.",
            "text_pairing_guidance": "Use the prose to explain which blocker classes dominate before listing raw missing items.",
        },
        "chart_next_best_search_path": {
            "chart_role": "Show what should still be searched publicly before the case escalates to local intake.",
            "reader_takeaway": "The search program is ranked and bounded; it is not an open-ended scraping reflex.",
            "text_pairing_guidance": "Use the prose to connect the top search targets to stop conditions and escalation logic.",
        },
        "chart_peer_requirement_readiness": {
            "chart_role": "Show which comparison requirements are already bounded and which still prohibit peer logic.",
            "reader_takeaway": "Peer comparison should not be trusted until the blocked requirements change state.",
            "text_pairing_guidance": "Use the prose to explain why the blocked requirements matter more than the existence of generic peer datasets.",
        },
        "chart_investment_uncertainty_map": {
            "chart_role": "Show the few uncertainties that are actually blocking capital-facing logic.",
            "reader_takeaway": "The reader should see immediately that the issue is not lack of AI fluency but lack of asset evidence.",
            "text_pairing_guidance": "Use the prose to explain why these uncertainties block specific decisions and what evidence resolves them.",
        },
        "chart_minimum_evidence_pack": {
            "chart_role": "Show the minimum evidence pack as an ordered request surface.",
            "reader_takeaway": "The next evidence request should become obvious without forcing the reader through long prose.",
            "text_pairing_guidance": "Use the prose to explain why the top items unlock the most decision value first.",
        },
        "chart_decision_front_status": {
            "chart_role": "Show which decision fronts are blocked, deferred, or safe to act on now.",
            "reader_takeaway": "The reader should understand the action posture of the case in seconds.",
            "text_pairing_guidance": "Use the prose to connect blocked fronts to the evidence that would change their status.",
        },
        "chart_scenario_space": {
            "chart_role": "Show the current scenario space without inventing numeric probabilities.",
            "reader_takeaway": "The point is conditional plausibility, not false precision.",
            "text_pairing_guidance": "Use the prose to explain what would make each scenario stronger or weaker.",
        },
        "chart_inference_scores": {
            "chart_role": "Show which inference cases matter most and why.",
            "reader_takeaway": "The reader should see quickly which cases combine plausibility, relevance, and urgency.",
            "text_pairing_guidance": "Use the surrounding prose to explain the highest-scoring cases, not to restate every bar.",
        },
        "chart_asset_context_completeness": {
            "chart_role": "Show how much of the asset is actually known.",
            "reader_takeaway": "This chart makes the missing physical substrate visible before any higher-level conclusion is attempted.",
            "text_pairing_guidance": "Use the prose to explain which missing clusters are now blocking a stronger technical reading.",
        },
        "chart_source_scope_balance": {
            "chart_role": "Show whether the case is being driven by asset evidence or issuer context.",
            "reader_takeaway": "If issuer-level bars dominate, the reader should immediately expect a degraded asset brief rather than a strong technical report.",
            "text_pairing_guidance": "Use the prose to explain why scope mismatch limits what can be claimed today.",
        },
        "chart_context_routing_status": {
            "chart_role": "Show whether location, climate, and benchmark routing are actually established.",
            "reader_takeaway": "The point is not just where the asset is, but whether the system has enough context to route technical expectations correctly.",
            "text_pairing_guidance": "Use the prose to explain what routing succeeded and what still lacks local confirmation.",
        },
        "chart_system_typology_prior": {
            "chart_role": "Show the probable system families that govern the asset.",
            "reader_takeaway": "This is an archetypal technical prior, not a field-confirmed system inventory.",
            "text_pairing_guidance": "Use the prose to separate expected systems from confirmed systems.",
        },
        "chart_validation_priority": {
            "chart_role": "Show what should be validated first.",
            "reader_takeaway": "This chart compresses the validation queue into an action order the reader can scan in seconds.",
            "text_pairing_guidance": "Use the prose to explain why the top items matter and what they unlock.",
        },
        "chart_revenue_trend": {
            "chart_role": "Provide scale context without implying asset-level economics.",
            "reader_takeaway": "This is consolidated issuer context only; it helps size the case but does not close asset economics.",
            "text_pairing_guidance": "Use the prose to reinforce scope limits and readiness posture.",
        },
        "chart_revenue_composition": {
            "chart_role": "Translate use mix into a quick heuristic picture.",
            "reader_takeaway": "This is an explanatory estimate derived from declared use mix, not confirmed segment disclosure.",
            "text_pairing_guidance": "Use the prose to clarify that the chart is indicative, not closing evidence.",
        },
        "chart_debt_discrepancy": {
            "chart_role": "Make the debt ambiguity visible immediately.",
            "reader_takeaway": "The gap matters because leverage-dependent reasoning remains blocked until it is reconciled.",
            "text_pairing_guidance": "Use the prose to explain why this discrepancy freezes stronger financial conclusions.",
        },
        "chart_tenant_concentration": {
            "chart_role": "Show concentration risk faster than text alone.",
            "reader_takeaway": "The key point is not the exact percentage but the operational dependence on a concentrated tenant profile.",
            "text_pairing_guidance": "Use the prose to connect concentration to decision risk and validation needs.",
        },
        "chart_ll97_scenario": {
            "chart_role": "Show bounded regulatory exposure scenarios.",
            "reader_takeaway": "The chart is scenario-based and should be read as screening-grade exposure, not compliance closure.",
            "text_pairing_guidance": "Use the prose to explain what would need to be measured to harden these scenarios.",
        },
        "chart_evidence_ladder": {
            "chart_role": "Show how far each case is from stronger support.",
            "reader_takeaway": "The reader should see which cases remain hypothesis-like and which are closer to durable decision support.",
            "text_pairing_guidance": "Use the prose to explain the most material gaps rather than narrating the full ladder.",
        },
        "chart_validation_effort_matrix": {
            "chart_role": "Show validation sequencing as effort versus impact.",
            "reader_takeaway": "The most important point is sequencing: not every unresolved question deserves the same effort now.",
            "text_pairing_guidance": "Use the prose to explain which actions are quick wins versus hard prerequisites.",
        },
        "chart_ll97_timeline": {
            "chart_role": "Turn compliance timing into a readable timeline.",
            "reader_takeaway": "The reader should understand the tightening compliance windows and why timing changes exposure.",
            "text_pairing_guidance": "Use the prose to connect timing to applicability and hardening needs.",
        },
        "chart_causal_dependency": {
            "chart_role": "Expose overlap in evidence dependencies across cases.",
            "reader_takeaway": "The chart helps show that some conflicts are not isolated; they contaminate multiple downstream readings.",
            "text_pairing_guidance": "Use the prose to explain why shared dependencies increase the cost of unresolved gaps.",
        },
        "chart_scenario_decision": {
            "chart_role": "Show how different resolution paths change the decision space.",
            "reader_takeaway": "The point is conditionality: action space changes only if certain blockers resolve in specific directions.",
            "text_pairing_guidance": "Use the prose to explain conditions first and outcomes second.",
        },
    }
    return stories.get(chart_id, {
        "chart_role": "Explain the section visually.",
        "reader_takeaway": "This chart exists to shorten the path from evidence to understanding.",
        "text_pairing_guidance": "Use the prose to explain the implication, not to duplicate the picture.",
    })


def _chart_strategic_value(chart_id: str, *, curation_mode: str = "default") -> dict[str, Any]:
    policy = {
        "chart_congruence_binding_state": (10, "thesis_critical", "Directly governs whether the visible thesis is bounded strongly enough to stand."),
        "chart_fair_comparison_gate": (10, "thesis_critical", "Can invalidate the denominator and reframe the whole comparison logic."),
        "chart_cross_layer_congruence_map": (10, "thesis_critical", "Shows the contradiction that should change interpretation."),
        "chart_measurement_minimality_path": (9, "thesis_critical", "Defines the minimum evidence path before escalation or instrumentation waste."),
        "chart_cost_driver_signal_profile": (9, "thesis_critical", "Can shift the case from generic energy logic to tariff, duty, boundary, or maintenance logic."),
        "chart_peer_requirement_readiness": (8, "strategic_support", "Makes explicit which peer requirements still prohibit fair comparison."),
        "chart_gap_taxonomy_profile": (7, "strategic_support", "Separates blocker types instead of collapsing all missing evidence into one bucket."),
        "chart_next_best_search_path": (7, "strategic_support", "Shows the remaining public-search path before local evidence should be requested."),
        "chart_investment_uncertainty_map": (7, "strategic_support", "Compresses the uncertainties still blocking capital-facing logic."),
        "chart_minimum_evidence_pack": (7, "strategic_support", "Turns the evidence request into a bounded decision surface."),
        "chart_decision_front_status": (6, "strategic_support", "Clarifies which decision fronts are blocked, deferred, or safe to advance."),
        "chart_scenario_space": (6, "strategic_support", "Shows how bounded scenarios change the decision frame without inventing probabilities."),
        "chart_validation_priority": (6, "strategic_support", "Helps sequence validation, but is secondary to contradiction and denominator charts."),
        "chart_causal_dependency": (6, "strategic_support", "Shows when one evidence dependency contaminates several downstream readings."),
        "chart_asset_context_completeness": (5, "supportive_context", "Useful context, but it does not usually change the strategic reading by itself."),
        "chart_source_scope_balance": (5, "supportive_context", "Useful scope hygiene, but not usually the chart that changes interpretation directly."),
        "chart_context_routing_status": (5, "supportive_context", "Useful routing hygiene, but mainly a support condition for stronger charts."),
        "chart_system_typology_prior": (5, "supportive_context", "Shows likely system families, but mainly supports rather than drives the thesis."),
        "chart_inference_scores": (5, "supportive_context", "Useful ranking context, but less interpretively sharp than contradiction or denominator charts."),
        "chart_evidence_ladder": (4, "supportive_context", "Helpful support context, but can read as methodology unless tightly tied to the thesis."),
        "chart_validation_effort_matrix": (4, "supportive_context", "Useful for work planning, but not usually the chart that changes the client's interpretation."),
        "chart_scenario_decision": (4, "supportive_context", "Potentially useful, but vulnerable to becoming derivative if the scenario lane is thin."),
        "chart_debt_discrepancy": (4, "supportive_context", "Useful blockage context, but not usually central to the asset thesis."),
        "chart_revenue_trend": (3, "decorative_risk", "Can drift into issuer context unless tightly bound to the asset decision."),
        "chart_revenue_composition": (3, "decorative_risk", "Can drift into descriptive company context without changing the asset interpretation."),
        "chart_tenant_concentration": (3, "decorative_risk", "Can be useful, but often reads as side context unless directly linked to the contradiction."),
        "chart_ll97_scenario": (3, "decorative_risk", "Useful only when regulatory framing is dominant; otherwise it risks decorative compliance energy."),
        "chart_ll97_timeline": (2, "decorative_risk", "Timing context alone rarely changes interpretation unless the case is regulation-led."),
    }
    score, tier, reason = policy.get(
        chart_id,
        (4, "supportive_context", "This chart currently acts as support context more than as a thesis-moving surface."),
    )
    if curation_mode == "blocked" and tier == "decorative_risk":
        score = min(score, 2)
    return {
        "strategic_value_score": int(score),
        "strategic_value_tier": str(tier),
        "strategic_value_reason": str(reason),
    }


def _chart_intelligence_binding(chart_id: str, executive_thesis: dict[str, Any]) -> dict[str, Any]:
    executive_thesis = dict(executive_thesis or {})
    dominant_contradiction = str(executive_thesis.get("dominant_contradiction", "")).strip()
    thesis_constellation_register = list(executive_thesis.get("thesis_constellation_register", []) or [])
    top_gold_nuggets = list(executive_thesis.get("top_gold_nuggets", []) or [])

    challenger_row = next(
        (
            row for row in thesis_constellation_register
            if str((row or {}).get("element_type", "")).strip()
            in {"challenger_hypothesis", "alternative_variable_candidate"}
        ),
        {},
    )
    first_nugget_row = next(
        (
            row for row in top_gold_nuggets
            if str((row or {}).get("gold_nugget", "")).strip()
        ),
        {},
    )

    contradiction_id = "dominant_contradiction" if dominant_contradiction else ""
    contradiction_label = dominant_contradiction
    hypothesis_id = str(challenger_row.get("element_type", "")).strip() or ""
    hypothesis_label = str(challenger_row.get("statement") or challenger_row.get("title") or "").strip()
    if not hypothesis_id:
        fallback_hypothesis_label = (
            str(executive_thesis.get("dominant_loss_logic", "")).strip()
            or str(executive_thesis.get("what_reality_feature_changes_the_decision", "")).strip()
        )
        if fallback_hypothesis_label:
            hypothesis_id = "bounded_structural_hypothesis"
            hypothesis_label = fallback_hypothesis_label
    nugget_id = str(first_nugget_row.get("nugget_id", "")).strip() or ""
    nugget_label = str(first_nugget_row.get("gold_nugget", "")).strip()

    chart_binding_policy = {
        "chart_cross_layer_congruence_map": ("contradiction", "This chart exists to make the dominant contradiction visible."),
        "chart_fair_comparison_gate": ("contradiction", "This chart should bind directly to the contradiction that blocks fair comparison."),
        "chart_cost_driver_signal_profile": ("hypothesis", "This chart should bind to the alternative variable or challenger hypothesis driving the case."),
        "chart_measurement_minimality_path": ("hypothesis", "This chart should bind to the bounded hypothesis that determines the next minimum evidence move."),
        "chart_peer_requirement_readiness": ("contradiction", "This chart should bind to the contradiction that invalidates peer comparison."),
        "chart_scenario_space": ("hypothesis", "This chart should bind to the bounded structural hypothesis that forks the decision space."),
        "chart_validation_priority": ("hypothesis", "This chart should bind to the structural hypothesis that orders validation effort."),
        "chart_next_best_search_path": ("hypothesis", "This chart should bind to the hypothesis that governs the next best search lane."),
        "chart_gap_taxonomy_profile": ("contradiction", "This chart should bind to the contradiction that still blocks closure."),
    }
    anchor_type, binding_reason = chart_binding_policy.get(
        chart_id,
        ("nugget", "This chart is support context and must still tie back to a bounded strategic nugget.")
    )

    if anchor_type == "contradiction" and contradiction_id:
        return {
            "binding_anchor_type": "contradiction",
            "binding_state": "bound",
            "binding_reason": binding_reason,
            "contradiction_id": contradiction_id,
            "contradiction_label": contradiction_label,
            "hypothesis_id": "",
            "hypothesis_label": "",
            "nugget_id": "",
            "nugget_label": "",
        }
    if anchor_type == "hypothesis" and hypothesis_id:
        return {
            "binding_anchor_type": "hypothesis",
            "binding_state": "bound",
            "binding_reason": binding_reason,
            "contradiction_id": contradiction_id if not contradiction_label else "",
            "contradiction_label": "" if hypothesis_id else contradiction_label,
            "hypothesis_id": hypothesis_id,
            "hypothesis_label": hypothesis_label,
            "nugget_id": "",
            "nugget_label": "",
        }
    if nugget_id or nugget_label:
        return {
            "binding_anchor_type": "nugget",
            "binding_state": "bound",
            "binding_reason": binding_reason,
            "contradiction_id": "",
            "contradiction_label": "",
            "hypothesis_id": "",
            "hypothesis_label": "",
            "nugget_id": nugget_id or "bounded_strategic_nugget",
            "nugget_label": nugget_label,
        }
    if contradiction_id:
        return {
            "binding_anchor_type": "contradiction_fallback",
            "binding_state": "bound_fallback",
            "binding_reason": "The chart falls back to the dominant contradiction because no richer binding lane is available.",
            "contradiction_id": contradiction_id,
            "contradiction_label": contradiction_label,
            "hypothesis_id": "",
            "hypothesis_label": "",
            "nugget_id": "",
            "nugget_label": "",
        }
    return {
        "binding_anchor_type": "unbound",
        "binding_state": "unbound",
        "binding_reason": "No bounded contradiction, hypothesis, or nugget anchor was available for this chart.",
        "contradiction_id": "",
        "contradiction_label": "",
        "hypothesis_id": "",
        "hypothesis_label": "",
        "nugget_id": "",
        "nugget_label": "",
    }


def _make_fig(w: float = 7.5, h: float = 4.2):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(w, h), dpi=130)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#CCCCCC")
    ax.tick_params(colors="#555555", labelsize=8)
    return fig, ax


def _to_b64(fig) -> str:
    import matplotlib.pyplot as plt
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return b64


def _parse_money_signal(text: str | int | float | None) -> float | None:
    if isinstance(text, (int, float)):
        return float(text)
    if not text:
        return None
    s = str(text)
    money_match = re.search(r"\$([\d,]+(?:\.\d+)?)\s*(million|billion|m|b)?", s, re.IGNORECASE)
    if not money_match:
        money_match = re.search(r"\b([\d,]+(?:\.\d+)?)\s*(million|billion)\b", s, re.IGNORECASE)
    if not money_match:
        return None
    value = float(money_match.group(1).replace(",", ""))
    suffix = (money_match.group(2) or "").lower()
    if suffix in {"billion", "b"}:
        value *= 1_000_000_000
    elif suffix in {"million", "m"}:
        value *= 1_000_000
    return value


def _extract_public_debt_signal(ext_sources: dict[str, Any], reported_debt: float | None) -> tuple[float | None, str]:
    ws_debt = ext_sources.get("ws_debt_leverage", {}) if isinstance(ext_sources.get("ws_debt_leverage", {}), dict) else {}
    candidates: list[float] = []
    for raw in ws_debt.get("numeric_extracts", []) or []:
        parsed = _parse_money_signal(raw)
        if parsed:
            candidates.append(parsed)
    for result in ws_debt.get("results", []) or []:
        parsed = _parse_money_signal(result.get("snippet", ""))
        if parsed:
            candidates.append(parsed)
    unique_candidates: list[float] = []
    for value in candidates:
        if value not in unique_candidates:
            unique_candidates.append(value)
    for value in unique_candidates:
        if not reported_debt:
            return value, "Public leverage signal"
        if abs(value - reported_debt) / max(reported_debt, 1.0) >= 0.10:
            return value, "Public leverage signal"
    return None, ""


def _state_value_and_color(state: Any) -> tuple[float, str]:
    value = str(state or "").strip().lower()
    if not value:
        return 0.10, _LGRAY
    if value in {"sufficiently_bound", "evidenced", "bounded_strong_local_truth", "decision_grade"}:
        return 1.00, _GREEN
    if "partial" in value:
        return 0.65, _AMBER
    if value in {"public_context_seeded", "screening_only", "bounded_screening_only"}:
        return 0.40, _NAVY
    if "not_yet" in value or "unbound" in value or "inadmissible" in value:
        return 0.15, _RED
    return 0.50, _TEAL


def _signal_score(text_blob: str, *, tokens: tuple[str, ...]) -> int:
    blob = (text_blob or "").lower()
    return 1 if any(token in blob for token in tokens) else 0


def _executive_thesis_signal_blob(executive_thesis: dict[str, Any]) -> str:
    executive_thesis = dict(executive_thesis or {})
    return " ".join(
        str(executive_thesis.get(key, "")).strip()
        for key in [
            "dominant_contradiction",
            "why_current_question_is_premature",
            "what_reality_feature_changes_the_decision",
            "dominant_operational_misunderstanding",
            "hidden_system_boundary_error",
            "invalid_comparison_risk",
            "dominant_loss_logic",
            "surprising_but_evidenced_takeaway",
        ]
        if str(executive_thesis.get(key, "")).strip()
    ).strip()


def _fallback_comparison_requirements_from_thesis(executive_thesis: dict[str, Any]) -> list[dict[str, Any]]:
    blob = _executive_thesis_signal_blob(executive_thesis)
    if not blob:
        return []
    return [
        {
            "normalization_dimension": "comparison denominator and operating intensity",
            "current_state": "not_yet_evidenced",
        },
        {
            "normalization_dimension": "control boundary and value capture",
            "current_state": "not_yet_evidenced" if "boundary" in blob.lower() or "control" in blob.lower() else "conditional",
        },
        {
            "normalization_dimension": "tariff / duty / demand structure",
            "current_state": "conditional" if any(token in blob.lower() for token in ("tariff", "demand", "charging", "duty")) else "not_yet_evidenced",
        },
    ]


def _fallback_cross_layer_rows_from_thesis(executive_thesis: dict[str, Any]) -> list[dict[str, Any]]:
    executive_thesis = dict(executive_thesis or {})
    contradiction = str(executive_thesis.get("dominant_contradiction", "")).strip()
    if not contradiction:
        return []
    ranked = list(executive_thesis.get("thesis_ranked_conflict_register", []) or [])
    first_ranked = dict(ranked[0] if ranked else {})
    layers = list(first_ranked.get("layers_involved", []) or [])
    if not layers:
        blob = _executive_thesis_signal_blob(executive_thesis).lower()
        layer_map = [
            ("finance", ("capital", "roi", "tariff", "cost", "financial")),
            ("operation", ("service", "throughput", "movement", "dock", "charging", "schedule")),
            ("control", ("control", "metering", "boundary", "owner", "tenant")),
            ("regulation", ("regulation", "compliance", "permit", "ll97")),
            ("benchmarking", ("benchmark", "denominator", "comparison", "peer")),
        ]
        for layer_name, tokens in layer_map:
            if any(token in blob for token in tokens):
                layers.append(layer_name)
    if not layers:
        layers = ["benchmarking", "operation"]
    return [
        {
            "contradiction": contradiction,
            "layers": layers[:4],
            "evidence_state": str(executive_thesis.get("evidence_state", "")).strip() or "CONDITIONAL_HYPOTHESIS",
        }
    ]


def _chart_asset_context_completeness(asset_identity_bundle: dict[str, Any]) -> str | None:
    clusters = asset_identity_bundle.get("observable_cluster_register", {}) if isinstance(asset_identity_bundle, dict) else {}
    if not clusters:
        return None
    import matplotlib.pyplot as plt

    order = [
        "location_cluster",
        "jurisdiction_cluster",
        "geometry_size_cluster",
        "vintage_structure_cluster",
        "use_program_cluster",
        "operating_regime_cluster",
        "fuel_energy_cluster",
        "systems_cluster",
        "regulatory_cluster",
        "benchmark_mapping_cluster",
    ]
    labels = []
    values = []
    colors = []
    for cid in order:
        cluster = clusters.get(cid, {})
        labels.append(cid.replace("_cluster", "").replace("_", " ").title())
        populated = bool(cluster.get("populated"))
        values.append(cluster.get("populated_count", 0) if populated else 0)
        colors.append(_GREEN if populated else _RED)
    fig, ax = _make_fig(w=8.3, h=4.6)
    bars = ax.barh(labels, [max(v, 0.15) for v in values], color=colors, edgecolor="none")
    for bar, cid, value in zip(bars, order, values):
        status = "present" if value else "missing"
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"{status} ({value})",
            va="center",
            fontsize=7.5,
            color=_DARK,
        )
    ax.set_xlim(0, max(max(values, default=0), 4) + 1.4)
    ax.set_xlabel("Observable signal count by cluster", fontsize=8)
    ax.set_title("Asset Context Completeness — What Is Actually Known", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_source_scope_balance(discovery_summary: dict[str, Any]) -> str | None:
    scope_counts = discovery_summary.get("scope_counts", {}) if isinstance(discovery_summary, dict) else {}
    if not scope_counts:
        return None
    import matplotlib.pyplot as plt

    labels = [k.replace("_", " ").title() for k in scope_counts]
    values = list(scope_counts.values())
    colors = []
    for key in scope_counts:
        if "issuer" in key or "entity" in key:
            colors.append(_MAROON)
        elif "asset" in key:
            colors.append(_NAVY)
        else:
            colors.append(_TEAL)
    fig, ax = _make_fig(w=8.0, h=max(3.8, 0.55 * len(labels) + 1.8))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, value in zip(bars, values):
        ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=7.5, color=_DARK)
    ax.set_xlabel("Sources attempted by scope", fontsize=8)
    ax.set_title("Source Scope Balance — Asset Evidence vs Issuer Context", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_context_routing_status(
    target_definition: dict[str, Any],
    geocoder: dict[str, Any],
    climate_zone: Any,
    benchmark_routing_register: dict[str, Any],
) -> str | None:
    if not isinstance(target_definition, dict):
        return None
    import matplotlib.pyplot as plt

    statuses = {
        "Target Declared": bool(target_definition.get("target_identifier")),
        "Geocoded": bool(geocoder),
        "Jurisdiction Routed": bool(target_definition.get("jurisdiction_scope")),
        "Climate Routed": bool(climate_zone),
        "Benchmark Routed": bool((benchmark_routing_register or {}).get("selected_source_type")),
    }
    labels = list(statuses.keys())
    values = [1 if statuses[k] else 0 for k in labels]
    colors = [_GREEN if v else _RED for v in values]
    fig, ax = _make_fig(w=7.4, h=3.6)
    bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor="none")
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Missing", "Established"], fontsize=8)
    for bar, ok in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, "OK" if ok else "Gap", ha="center", fontsize=8, fontweight="bold", color=_DARK)
    selected = (benchmark_routing_register or {}).get("selected_source_type", "not routed")
    ax.set_title(f"Asset Routing Status — benchmark route: {selected}", fontsize=9.2, fontweight="bold", color=_DARK, pad=10)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_system_typology_prior(system_typology_prior: dict[str, Any], asset_energy_behavior_prior: dict[str, Any]) -> str | None:
    expected = system_typology_prior.get("expected_system_families", []) if isinstance(system_typology_prior, dict) else []
    if not expected:
        return None
    import matplotlib.pyplot as plt

    labels = [s.replace("_", " ").title() for s in expected[:6]]
    mode = system_typology_prior.get("system_prior_mode", "archetypal_only")
    base = 0.52 if mode == "archetypal_only" else 0.72
    values = [base + (0.03 * (i % 2)) for i in range(len(labels))]
    fig, ax = _make_fig(w=8.0, h=max(3.4, 0.55 * len(labels) + 1.6))
    bars = ax.barh(labels, values, color=_NAVY, edgecolor="none", alpha=0.88)
    for bar, label in zip(bars, labels):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2, "expected", va="center", fontsize=7.5, color=_DARK)
    climate = (asset_energy_behavior_prior or {}).get("climate_sensitivity_expectation", "unresolved")
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Prior confidence (bounded, not field-confirmed)", fontsize=8)
    ax.set_title(f"System Typology Prior — mode: {mode} | climate: {climate}", fontsize=9.2, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_investment_uncertainty_map(
    readiness_summary: dict[str, Any],
    decision_front_register: list[dict[str, Any]],
) -> str | None:
    rows = []
    if isinstance(readiness_summary, dict):
        rows = readiness_summary.get("rows", []) or readiness_summary.get("cluster_rows", [])
    if not rows:
        return None
    import matplotlib.pyplot as plt

    blocked_front = next(
        (row.get("decision_front", "") for row in decision_front_register if row.get("current_status") in {"NO-GO", "VALIDATE FIRST"}),
        "",
    )
    candidates = []
    for row in rows:
        status = str(row.get("status", "")).upper()
        if status in {"OBSERVED", "POPULATED", "AVAILABLE"}:
            continue
        severity = 4.0 if "BLOCK" in status or "NOT_OBSERVED" in status else 2.5
        candidates.append(
            (
                str(row.get("cluster", "Unknown Cluster")).replace("_", " ").title(),
                severity,
                row.get("consequence", ""),
            )
        )
    if not candidates:
        return None
    candidates = candidates[:6]
    labels = [c[0] for c in candidates]
    values = [c[1] for c in candidates]
    notes = [c[2] for c in candidates]
    colors = [_RED if v >= 4 else _AMBER for v in values]

    fig, ax = _make_fig(w=8.4, h=max(4.0, 0.6 * len(labels) + 1.8))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, note in zip(bars, notes):
        ax.text(
            min(bar.get_width() + 0.08, 4.55),
            bar.get_y() + bar.get_height() / 2,
            _shorten(note, 78),
            va="center",
            fontsize=7.2,
            color=_DARK,
        )
    ax.set_xlim(0, 4.8)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["Low", "Moderate", "High", "Critical"], fontsize=8)
    ax.set_xlabel("Uncertainty severity under current evidence", fontsize=8)
    title = "Investment Uncertainty Map — What Is Blocking a Stronger Decision"
    if blocked_front:
        title += f"\n(primary blocked front: {blocked_front[:42]})"
    ax.set_title(title, fontsize=9.2, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_minimum_evidence_pack(minimum_evidence_unlock_map: list[dict[str, Any]]) -> str | None:
    if not minimum_evidence_unlock_map:
        return None
    import matplotlib.pyplot as plt

    effort_scores = {"CRITICAL": 4.0, "HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}
    rows = minimum_evidence_unlock_map[:6]
    labels = [_shorten(row.get("evidence_item", "Evidence item"), 42) for row in rows]
    values = [effort_scores.get(str(row.get("effort", "")).upper(), 2.0) for row in rows]
    colors = [_RED if v >= 4 else _AMBER if v >= 3 else _NAVY for v in values]

    fig, ax = _make_fig(w=8.5, h=max(4.0, 0.62 * len(labels) + 1.8))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, row in zip(bars, rows):
        ax.text(
            min(bar.get_width() + 0.08, 4.55),
            bar.get_y() + bar.get_height() / 2,
            _shorten(row.get("decision_unlock", ""), 72),
            va="center",
            fontsize=7.1,
            color=_DARK,
        )
    ax.set_xlim(0, 4.8)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["Low", "Medium", "High", "Critical"], fontsize=8)
    ax.set_xlabel("Evidence priority / urgency", fontsize=8)
    ax.set_title("Minimum Evidence Pack — Ordered by Decision Unlock Value", fontsize=9.2, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_decision_front_status(decision_front_register: list[dict[str, Any]]) -> str | None:
    if not decision_front_register:
        return None
    import matplotlib.pyplot as plt

    status_scale = {
        "ACT NOW": 4.0,
        "VALIDATE FIRST": 3.0,
        "INVESTIGATE THEN DECIDE": 2.0,
        "DEFER": 1.0,
        "NO-GO": 0.4,
    }
    status_colors = {
        "ACT NOW": _GREEN,
        "VALIDATE FIRST": _AMBER,
        "INVESTIGATE THEN DECIDE": _TEAL,
        "DEFER": _PURPLE,
        "NO-GO": _RED,
    }
    rows = decision_front_register[:6]
    labels = [_shorten(row.get("decision_front", "Decision front"), 38) for row in rows]
    statuses = [str(row.get("current_status", "")).upper() for row in rows]
    values = [status_scale.get(status, 2.0) for status in statuses]
    colors = [status_colors.get(status, _NAVY) for status in statuses]

    fig, ax = _make_fig(w=8.4, h=max(4.0, 0.62 * len(labels) + 1.8))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, status, row in zip(bars, statuses, rows):
        ax.text(
            min(bar.get_width() + 0.08, 4.55),
            bar.get_y() + bar.get_height() / 2,
            f"{status} — {_shorten(row.get('admissible_action', ''), 56)}",
            va="center",
            fontsize=7.1,
            color=_DARK,
        )
    ax.set_xlim(0, 4.8)
    ax.set_xticks([0.4, 1, 2, 3, 4])
    ax.set_xticklabels(["No-go", "Defer", "Investigate", "Validate", "Act"], fontsize=8)
    ax.set_xlabel("Current admissible action posture", fontsize=8)
    ax.set_title("Decision Front Status — What Can Be Done Now", fontsize=9.2, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_scenario_space(scenario_space: list[dict[str, Any]]) -> str | None:
    if not scenario_space:
        return None
    import matplotlib.pyplot as plt

    plausibility_scale = {
        "CURRENTLY DOMINANT": 4.0,
        "PLAUSIBLE": 3.2,
        "PLAUSIBLE BUT UNSUPPORTED": 2.7,
        "NOT RULED OUT": 2.2,
        "POSSIBLE BUT UNSUPPORTED": 1.8,
        "REDUCED": 1.0,
    }
    rows = scenario_space[:5]
    labels = [_shorten(row.get("scenario", "Scenario"), 34) for row in rows]
    statuses = [str(row.get("plausibility_status", "")).upper() for row in rows]
    values = [plausibility_scale.get(status, 2.0) for status in statuses]
    colors = [
        _RED if value >= 4 else _AMBER if value >= 2.5 else _NAVY
        for value in values
    ]

    fig, ax = _make_fig(w=8.5, h=max(4.0, 0.62 * len(labels) + 1.8))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, row in zip(bars, rows):
        ax.text(
            min(bar.get_width() + 0.08, 4.55),
            bar.get_y() + bar.get_height() / 2,
            _shorten(row.get("evidence_needed", ""), 68),
            va="center",
            fontsize=7.0,
            color=_DARK,
        )
    ax.set_xlim(0, 4.8)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["Reduced", "Open", "Plausible", "Dominant"], fontsize=8)
    ax.set_xlabel("Scenario plausibility status", fontsize=8)
    ax.set_title("Scenario Space — Conditional Futures Under Current Evidence", fontsize=9.2, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 1: Inference Case Score Matrix ──────────────────────────────────────

def _chart_inference_scores(inference_records: list[dict]) -> str | None:
    if not inference_records:
        return None
    import matplotlib.pyplot as plt
    import numpy as np

    records = sorted(inference_records, key=lambda x: x.get("validation_urgency_score", 0), reverse=True)
    labels = [f"{r['case_id']}" for r in records]
    full_names = [r['case_name'][:32] + ("..." if len(r['case_name']) > 32 else "") for r in records]
    p_scores = [r.get("plausibility_score", 0) for r in records]
    r_scores = [r.get("decision_relevance_score", 0) for r in records]
    v_scores = [r.get("validation_urgency_score", 0) for r in records]

    n = len(records)
    x = np.arange(n)
    width = 0.26

    fig, ax = _make_fig(w=9, h=4.5)

    bars_p = ax.bar(x - width, p_scores, width, label="Plausibility (P)", color=_NAVY, alpha=0.88)
    bars_r = ax.bar(x,         r_scores, width, label="Decision Relevance (R)", color=_MAROON, alpha=0.88)
    bars_v = ax.bar(x + width, v_scores, width, label="Validation Urgency (V)", color=_AMBER, alpha=0.88)

    # Value labels on bars
    for bar_group in [bars_p, bars_r, bars_v]:
        for bar in bar_group:
            h = bar.get_height()
            ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 2), textcoords="offset points",
                        ha="center", va="bottom", fontsize=6.5, color="#444444")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Score (0.0 – 1.0)", fontsize=8)
    ax.axhline(y=0.85, color=_RED, linestyle="--", linewidth=0.8, alpha=0.6, label="Critical threshold (0.85)")
    ax.axhline(y=0.65, color=_AMBER, linestyle=":", linewidth=0.8, alpha=0.5)
    ax.legend(fontsize=7.5, loc="upper right", framealpha=0.9)
    ax.set_title("Inference Case Score Matrix — P / R / V by Case", fontsize=9.5,
                 fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    # Secondary axis with abbreviated case names
    ax2 = ax.secondary_xaxis("top")
    ax2.set_xticks(x)
    ax2.set_xticklabels([r["case_name"].split()[0:3] for r in records],
                        fontsize=6.5, rotation=15, ha="left", color="#666666")

    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 2: Validation Priority Ranking ─────────────────────────────────────

def _chart_validation_priority(inference_records: list[dict]) -> str | None:
    if not inference_records:
        return None
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    records = sorted(inference_records, key=lambda x: x.get("validation_urgency_score", 0))
    labels = [f"[{r['case_id']}] {r['case_name'][:38]}" for r in records]
    v_scores = [r.get("validation_urgency_score", 0) for r in records]
    families = [r.get("claim_family", "") for r in records]

    color_map = {
        "conflict": _RED,
        "tension": _AMBER,
        "plausible_hypothesis": _NAVY,
        "opportunity": _GREEN,
    }
    colors = [color_map.get(f, _TEAL) for f in families]

    fig, ax = _make_fig(w=8.5, h=4.0)

    bars = ax.barh(labels, v_scores, color=colors, edgecolor="none", height=0.6)
    ax.axvline(x=0.85, color=_RED, linestyle="--", linewidth=1, alpha=0.7, label="Critical (0.85)")
    ax.axvline(x=0.65, color=_AMBER, linestyle=":", linewidth=1, alpha=0.6, label="High (0.65)")
    ax.set_xlim(0, 1.1)
    ax.set_xlabel("Validation Urgency Score", fontsize=8)

    for bar, score in zip(bars, v_scores):
        urgency = "CRITICAL" if score >= 0.85 else "HIGH" if score >= 0.65 else "MEDIUM"
        ax.text(score + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{score:.2f}  {urgency}", va="center", fontsize=7.5, color=_DARK)

    legend_patches = [
        mpatches.Patch(color=_RED, label="Conflict"),
        mpatches.Patch(color=_AMBER, label="Tension"),
        mpatches.Patch(color=_NAVY, label="Hypothesis"),
        mpatches.Patch(color=_GREEN, label="Opportunity"),
    ]
    ax.legend(handles=legend_patches, fontsize=7.5, loc="lower right", framealpha=0.9)
    ax.set_title("Validation Priority Ranking — by Urgency Score", fontsize=9.5,
                 fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 3: Revenue Trend ────────────────────────────────────────────────────

def _chart_revenue_trend(revenues_series: list[dict], company_label: str) -> str | None:
    if len(revenues_series) < 2:
        return None
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    seen = {}
    dedup = []
    for entry in revenues_series:
        yr = entry["end"][:4]
        if yr not in seen:
            seen[yr] = entry["val"]
            dedup.append({"year": yr, "val": entry["val"]})
    dedup.sort(key=lambda x: x["year"])

    years = [e["year"] for e in dedup]
    vals = [e["val"] for e in dedup]

    fig, ax = _make_fig(w=7, h=3.8)
    ax.plot(years, vals, color=_MAROON, linewidth=2.2, marker="o", markersize=5, zorder=3)
    ax.fill_between(range(len(years)), vals, alpha=0.07, color=_MAROON)

    for i, (yr, val) in enumerate(zip(years, vals)):
        ax.annotate(f"${val/1e6:.0f}M", xy=(i, val),
                    xytext=(0, 7), textcoords="offset points",
                    ha="center", fontsize=7.5, color=_MAROON, fontweight="bold")

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, fontsize=8)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M"))
    ax.set_ylabel("Revenue (USD)", fontsize=8)
    ax.set_title(f"{company_label} Total Revenue — Annual Trend (SEC EDGAR XBRL)", fontsize=9.5,
                 fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 4: Revenue Composition Estimate ─────────────────────────────────────

def _chart_revenue_composition(revenues_annual: float | None, use_mix: dict) -> str | None:
    if not revenues_annual:
        return None
    import matplotlib.pyplot as plt

    labels = []
    values = []
    for use, pct in use_mix.items():
        if pct and isinstance(pct, (int, float)):
            labels.append(use[:30])
            values.append(pct)

    if not values:
        labels = ["Office (~75%)", "Observatory (~17%)", "Retail (~8%)"]
        values = [75, 17, 8]

    colors = [_MAROON, _NAVY, _TEAL][:len(values)]

    fig, ax = _make_fig(w=6, h=4)
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.0f%%",
        colors=colors, startangle=90,
        pctdistance=0.75, textprops={"fontsize": 8.5},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")

    ax.set_aspect("equal")
    ax.set_title(
        f"Revenue Mix Estimate — Annual {f'${revenues_annual/1e6:.0f}M' if revenues_annual else 'N/A'} Total\n"
        "(derived from use-mix inputs — NOT confirmed segment disclosure)",
        fontsize=8.5, fontweight="bold", color=_DARK, pad=8,
    )
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 5: Debt Discrepancy ─────────────────────────────────────────────────

def _chart_debt_discrepancy(
    total_debt: float | None,
    public_debt_signal: float | None,
    public_signal_label: str,
) -> str | None:
    if not total_debt or not public_debt_signal:
        return None
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    labels = ["XBRL Reported Debt\n(us-gaap:LongTermDebt)", f"{public_signal_label}\n(unverified)"]
    values = [total_debt, public_debt_signal]
    colors = [_NAVY, _RED]

    fig, ax = _make_fig(w=5.5, h=3.8)
    bars = ax.bar(labels, values, color=colors, width=0.42, edgecolor="none")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1e9:.1f}B"))

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30_000_000,
                f"${val/1e9:.2f}B", ha="center", fontsize=9, fontweight="bold",
                color=bar.get_facecolor())

    gap = values[1] - values[0]
    ax.annotate(
        f"Gap: ${gap/1e9:.1f}B\n(REQUIRES VALIDATION)",
        xy=(1, values[1]),
        xytext=(0.5, values[1] * 0.85),
        arrowprops=dict(arrowstyle="->", color=_RED, lw=1.2),
        fontsize=8, color=_RED, fontweight="bold", ha="center",
    )

    ax.set_ylim(0, max(values) * 1.25)
    ax.set_ylabel("Total Debt (USD)", fontsize=8)
    ax.set_title("Debt Context Comparison — Reported vs Public Signal\n[bounded leverage context only]",
                 fontsize=9, fontweight="bold", color=_RED, pad=8)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 6: Tenant Concentration ────────────────────────────────────────────

def _chart_tenant_concentration(tenants: dict, rentable_sqft: int) -> str | None:
    if not tenants or not rentable_sqft:
        return None
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    anchor = tenants.get("anchor_tenant", "LinkedIn")
    anchor_sqft = tenants.get("anchor_tenant_approx_sqft", 453500)
    others_sqft = rentable_sqft - anchor_sqft

    known_others = [t for t in tenants.get("major_tenants_known", []) if t != anchor]
    if known_others:
        each = int(others_sqft / (len(known_others) + 1))
        rows = [(anchor, anchor_sqft)] + [(t, each) for t in known_others[:3]] + [("Other Tenants", others_sqft - each * min(3, len(known_others)))]
    else:
        rows = [(anchor, anchor_sqft), ("Other Tenants", others_sqft)]

    labels = [r[0][:22] for r in rows]
    values = [r[1] for r in rows]
    colors = [_RED if i == 0 else _PALETTE[i % len(_PALETTE)] for i in range(len(rows))]

    fig, ax = _make_fig(w=7, h=3.6)
    bars = ax.barh(labels, values, color=colors, edgecolor="none", height=0.55)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x/1e3:.0f}K sqft"))

    for bar, val in zip(bars, values):
        pct = 100 * val / rentable_sqft
        ax.text(val + 5000, bar.get_y() + bar.get_height() / 2,
                f"{val:,} sqft  ({pct:.1f}%)", va="center", fontsize=7.5, color=_DARK)

    ax.axvline(x=anchor_sqft, color=_RED, linestyle="--", linewidth=0.9, alpha=0.6)
    ax.set_xlim(0, rentable_sqft * 1.18)
    ax.set_xlabel("Rentable Office Area (sqft)", fontsize=8)
    ax.set_title(
        f"Tenant Concentration — Office GFA Breakdown\n"
        f"[{anchor} = {100*anchor_sqft/rentable_sqft:.1f}% of office GFA — IC-04 CRITICAL]",
        fontsize=8.5, fontweight="bold", color=_DARK, pad=8,
    )
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 7: LL97 Compliance Scenario ────────────────────────────────────────

def _chart_ll97_scenario(gfa_sqft: int) -> str | None:
    if not gfa_sqft:
        return None
    import matplotlib.pyplot as plt
    import numpy as np

    scenarios = [
        ("Optimistic\n(0.006 tCO2e/sqft)", 0.006),
        ("Moderate\n(0.009 tCO2e/sqft)", 0.009),
        ("Conservative\n(0.012 tCO2e/sqft)", 0.012),
    ]
    limit_2024 = 0.00846
    limit_2030 = 0.00453
    penalty_per_ton = 268

    categories = [s[0] for s in scenarios]
    penalties_2024 = []
    penalties_2030 = []

    for _, intensity in scenarios:
        over_2024 = max(0, (intensity - limit_2024) * gfa_sqft * penalty_per_ton)
        over_2030 = max(0, (intensity - limit_2030) * gfa_sqft * penalty_per_ton)
        penalties_2024.append(over_2024)
        penalties_2030.append(over_2030)

    x = np.arange(len(categories))
    width = 0.36

    fig, ax = _make_fig(w=7.5, h=4.0)
    import matplotlib.ticker as mtick

    b1 = ax.bar(x - width / 2, [p / 1e6 for p in penalties_2024], width,
                label="2024–2029 Penalty (USD)", color=_AMBER, alpha=0.88)
    b2 = ax.bar(x + width / 2, [p / 1e6 for p in penalties_2030], width,
                label="2030–2034 Penalty (USD)", color=_RED, alpha=0.88)

    for bar_group in [b1, b2]:
        for bar in bar_group:
            h = bar.get_height()
            if h > 0:
                ax.annotate(f"${h:.1f}M", xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", fontsize=7.5, color="#333333")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=8)
    ax.set_ylabel("Annual Penalty Exposure (USD M)", fontsize=8)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"${v:.0f}M"))
    ax.legend(fontsize=8, loc="upper left", framealpha=0.9)
    ax.set_title(
        f"NYC LL97 Penalty Exposure Scenarios — {gfa_sqft/1e6:.1f}M sqft\n"
        "(Illustrative — actual emissions require official LL97 annual report)",
        fontsize=8.5, fontweight="bold", color=_DARK, pad=8,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 8: Evidence Ladder ─────────────────────────────────────────────────

def _chart_evidence_ladder(inference_records: list[dict]) -> str | None:
    if not inference_records:
        return None
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    records = sorted(inference_records, key=lambda x: x.get("plausibility_score", 0))
    labels  = [f"[{r['case_id']}] {r['case_name'][:36]}" for r in records]
    p_vals  = [r.get("plausibility_score", 0) for r in records]
    gap_vals = [1 - p for p in p_vals]

    fig, ax = _make_fig(w=9, h=max(3.5, 0.55 * len(records) + 1.5))

    bars_p   = ax.barh(labels, p_vals,   color=_GREEN,  height=0.52, label="Plausibility (confirmed)")
    bars_gap = ax.barh(labels, gap_vals, left=p_vals, color=_LGRAY, height=0.52, label="Epistemic gap (unresolved)")

    for bar, p in zip(bars_p, p_vals):
        ax.text(p / 2, bar.get_y() + bar.get_height() / 2,
                f"{p:.2f}", va="center", ha="center", fontsize=7, color="white", fontweight="bold")

    ax.axvline(x=0.85, color=_RED,   linestyle="--", linewidth=0.9, alpha=0.7, label="Verification threshold (0.85)")
    ax.axvline(x=0.65, color=_AMBER, linestyle=":",  linewidth=0.9, alpha=0.6, label="Inference threshold (0.65)")
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Plausibility Score", fontsize=8)
    ax.legend(fontsize=7, loc="lower right", framealpha=0.9)
    ax.set_title("Evidence Ladder — Plausibility vs Epistemic Gap by Case",
                 fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 9: Validation Effort Matrix ────────────────────────────────────────

def _chart_validation_effort_matrix(inference_records: list[dict]) -> str | None:
    if not inference_records:
        return None
    import matplotlib.pyplot as plt
    import numpy as np

    # Effort proxy: 1 − validation_urgency (high urgency = low effort needed = easy win)
    effort  = [round(1 - r.get("validation_urgency_score", 0), 2) for r in inference_records]
    impact  = [r.get("decision_relevance_score", 0) for r in inference_records]
    gap     = [1 - r.get("plausibility_score", 0) for r in inference_records]
    labels  = [r["case_id"] for r in inference_records]
    families = [r.get("claim_family", "") for r in inference_records]

    color_map = {"conflict": _RED, "tension": _AMBER, "plausible_hypothesis": _NAVY, "opportunity": _GREEN}
    colors = [color_map.get(f, _TEAL) for f in families]
    sizes  = [max(60, g * 400) for g in gap]

    fig, ax = _make_fig(w=7.5, h=5.5)
    sc = ax.scatter(effort, impact, s=sizes, c=colors, alpha=0.82, edgecolors="white", linewidths=0.7, zorder=3)

    for i, lbl in enumerate(labels):
        ax.annotate(lbl, (effort[i], impact[i]),
                    xytext=(5, 4), textcoords="offset points", fontsize=7.5, color=_DARK)

    ax.axvline(x=0.5, color="#CCCCCC", linestyle="--", linewidth=0.8)
    ax.axhline(y=0.5, color="#CCCCCC", linestyle="--", linewidth=0.8)

    ax.text(0.18, 0.97, "QUICK WINS\n(low effort / high impact)", transform=ax.transAxes,
            fontsize=7, color=_GREEN, alpha=0.8, ha="center", va="top")
    ax.text(0.78, 0.97, "HARD REQUIRED\n(high effort / high impact)", transform=ax.transAxes,
            fontsize=7, color=_RED, alpha=0.8, ha="center", va="top")
    ax.text(0.18, 0.05, "DEFER\n(low effort / low impact)", transform=ax.transAxes,
            fontsize=7, color="#888888", ha="center")
    ax.text(0.78, 0.05, "BACKGROUND\n(high effort / low impact)", transform=ax.transAxes,
            fontsize=7, color="#888888", ha="center")

    ax.set_xlabel("Validation Effort (1 − urgency score)", fontsize=8)
    ax.set_ylabel("Decision Relevance", fontsize=8)
    ax.set_xlim(-0.05, 1.15)
    ax.set_ylim(-0.05, 1.15)
    ax.set_title("Validation Effort Matrix — Impact vs Effort per Case\n(bubble size = epistemic gap)",
                 fontsize=9, fontweight="bold", color=_DARK, pad=10)
    ax.grid(linestyle="--", alpha=0.25)

    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=l)
        for l, c in [("Conflict", _RED), ("Tension", _AMBER), ("Hypothesis", _NAVY), ("Opportunity", _GREEN)]
    ]
    ax.legend(handles=legend_handles, fontsize=7.5, loc="lower right", framealpha=0.9)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 10: LL97 Compliance Timeline ───────────────────────────────────────

def _chart_ll97_timeline(gfa_sqft: int) -> str | None:
    if not gfa_sqft:
        return None
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    fig, axes = plt.subplots(2, 1, figsize=(9, 5.5), dpi=130,
                              gridspec_kw={"height_ratios": [1.2, 2]})
    fig.patch.set_facecolor("white")

    # ── Top panel: timeline bar ────────────────────────────────────────────
    ax0 = axes[0]
    ax0.set_facecolor("#FAFAFA")
    ax0.spines[["top", "right", "bottom"]].set_visible(False)

    periods = [
        (2024, 2029, "2024–2029\nPhase 1", _AMBER,  0.00846),
        (2030, 2034, "2030–2034\nPhase 2", _RED,    0.00453),
        (2035, 2040, "2035–\nFinal",       "#8B0000", 0.00000),
    ]
    for start, end, label, color, limit in periods:
        ax0.barh(0, end - start, left=start, height=0.5, color=color, alpha=0.8, edgecolor="white")
        ax0.text(start + (end - start) / 2, 0,
                 f"{label}\n≤{limit:.5f} tCO₂e/sqft" if limit else f"{label}\nTBD",
                 ha="center", va="center", fontsize=7.5, fontweight="bold", color="white")

    ax0.axvline(x=2026, color=_NAVY, linewidth=1.5, linestyle="--", label="Analysis date (2026)")
    ax0.set_xlim(2022, 2042)
    ax0.set_ylim(-0.6, 0.6)
    ax0.set_yticks([])
    ax0.set_title("NYC Local Law 97 — Compliance Timeline & Penalty Exposure",
                  fontsize=9.5, fontweight="bold", color=_DARK, pad=8)
    ax0.legend(fontsize=7, loc="upper right")

    # ── Bottom panel: penalty ramp across emission intensities ─────────────
    ax1 = axes[1]
    ax1.set_facecolor("#FAFAFA")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.spines[["left", "bottom"]].set_color("#CCCCCC")

    intensities = np.linspace(0.004, 0.018, 100)
    penalty_rate = 268

    for limit_val, label, color, style in [
        (0.00846, "2024–2029 limit", _AMBER, "-"),
        (0.00453, "2030–2034 limit", _RED,   "--"),
    ]:
        penalties = [max(0, (i - limit_val) * gfa_sqft * penalty_rate) / 1e6 for i in intensities]
        ax1.plot(intensities * 1000, penalties, color=color, linewidth=2, linestyle=style, label=label)
        ax1.axvline(x=limit_val * 1000, color=color, linewidth=0.8, linestyle=":", alpha=0.6)

    ax1.fill_between(intensities * 1000,
                     [max(0, (i - 0.00453) * gfa_sqft * penalty_rate) / 1e6 for i in intensities],
                     alpha=0.08, color=_RED)

    ax1.set_xlabel("Actual Emissions Intensity (tCO₂e / sqft × 1000)", fontsize=8)
    ax1.set_ylabel("Annual Penalty (USD M)", fontsize=8)
    ax1.legend(fontsize=8, framealpha=0.9)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    ax1.set_title(f"Annual Penalty vs Intensity — {gfa_sqft/1e6:.1f}M sqft  |  $268/tCO₂e",
                  fontsize=8.5, color=_DARK)

    plt.tight_layout(pad=1.5)
    return _to_b64(fig)


# ── Chart 11: Causal Dependency Map ──────────────────────────────────────────

def _chart_causal_dependency(inference_records: list[dict]) -> str | None:
    if len(inference_records) < 2:
        return None
    import matplotlib.pyplot as plt
    import numpy as np

    n = len(inference_records)
    ids = [r["case_id"] for r in inference_records]
    traces = [set(r.get("base_support_traces", [])) for r in inference_records]

    # Build overlap matrix (Jaccard-like: shared traces / union)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            elif traces[i] | traces[j]:
                matrix[i][j] = len(traces[i] & traces[j]) / len(traces[i] | traces[j])

    fig, ax = _make_fig(w=7, h=6)
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Evidence Overlap (Jaccard)")

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(ids, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(ids, fontsize=8)

    for i in range(n):
        for j in range(n):
            val = matrix[i][j]
            if val > 0.01:
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=6.5, color="black" if val < 0.7 else "white")

    ax.set_title("Causal Dependency Map — Evidence Trace Overlap Between Cases\n"
                 "(1.0 = same evidence base; 0.0 = independent)",
                 fontsize=9, fontweight="bold", color=_DARK, pad=10)
    plt.tight_layout()
    return _to_b64(fig)


# ── Chart 12: Scenario Decision Matrix ───────────────────────────────────────

def _chart_scenario_decision(inference_records: list[dict]) -> str | None:
    if not inference_records:
        return None
    import matplotlib.pyplot as plt
    import numpy as np

    # Scenarios: what if each top-3 blocking/tension case is resolved?
    top = sorted(inference_records,
                 key=lambda x: x.get("validation_urgency_score", 0), reverse=True)[:5]

    scenarios = [f"Resolve\n{r['case_id']}" for r in top]
    outcomes  = ["Leverage\nAnalysis", "Tenant\nRisk Δ", "LL97\nClarity",
                 "CapEx\nReserve", "Decision\nGrade"]

    # Score matrix: does resolving this case improve each outcome?
    # Logic: conflict cases → leverage; tension cases → tenant/LL97; hypothesis → CapEx/grade
    def _score(rec: dict, outcome: str) -> float:
        family = rec.get("claim_family", "")
        cid    = rec.get("case_id", "")
        r_score = rec.get("decision_relevance_score", 0.5)
        p_score = rec.get("plausibility_score", 0.5)
        gain = r_score * (1 - p_score)  # potential gain from resolution
        if outcome == "Leverage\nAnalysis":
            return gain if family == "conflict" else gain * 0.3
        if outcome == "Tenant\nRisk Δ":
            return gain if "IC-04" in cid or "IC-07" in cid else gain * 0.25
        if outcome == "LL97\nClarity":
            return gain if "IC-03" in cid or "IC-05" in cid else gain * 0.2
        if outcome == "CapEx\nReserve":
            return gain if "IC-05" in cid or "IC-06" in cid else gain * 0.15
        if outcome == "Decision\nGrade":
            return gain  # any resolution improves overall grade
        return 0.0

    matrix = np.array([[_score(r, o) for o in outcomes] for r in top])

    fig, ax = _make_fig(w=8.5, h=max(4.0, 0.7 * len(scenarios) + 2))
    im = ax.imshow(matrix, cmap="Greens", vmin=0, vmax=0.5, aspect="auto")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Decision Impact Gain")

    ax.set_xticks(range(len(outcomes)))
    ax.set_yticks(range(len(scenarios)))
    ax.set_xticklabels(outcomes, fontsize=8.5)
    ax.set_yticklabels(scenarios, fontsize=8.5)

    for i in range(len(scenarios)):
        for j in range(len(outcomes)):
            v = matrix[i][j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=8, color="black" if v < 0.3 else "white", fontweight="bold")

    ax.set_title("Scenario Decision Matrix — Resolution Impact by Outcome\n"
                 "(higher = more decision value unlocked by resolving this case)",
                 fontsize=9, fontweight="bold", color=_DARK, pad=10)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_congruence_binding_state(local_truth_confidence_register: list[dict[str, Any]]) -> str | None:
    rows = [dict(row) for row in list(local_truth_confidence_register or [])[:6]]
    if not rows:
        return None
    import matplotlib.pyplot as plt

    labels = [_shorten(row.get("research_claim") or row.get("claim_key") or "claim", 42) for row in rows]
    values: list[float] = []
    colors: list[str] = []
    for row in rows:
        score, color = _state_value_and_color(row.get("binding_state") or row.get("local_truth_confidence"))
        values.append(score)
        colors.append(color)

    fig, ax = _make_fig(w=8.2, h=max(4.0, 0.70 * len(rows) + 1.6))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, row in zip(bars, rows):
        ax.text(
            min(bar.get_width() + 0.03, 1.02),
            bar.get_y() + bar.get_height() / 2,
            _shorten(row.get("local_truth_confidence") or row.get("binding_state") or "screening_only", 28),
            va="center",
            fontsize=7.5,
            color=_DARK,
        )
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("Local binding strength", fontsize=8)
    ax.set_title("Congruence Binding State — Which Claims Are Actually Locally Bounded", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_fair_comparison_gate(
    normalization_requirements_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    executive_thesis: dict[str, Any] | None = None,
) -> str | None:
    rows = [dict(row) for row in list(normalization_requirements_register or [])[:6]]
    if not rows:
        rows = _fallback_comparison_requirements_from_thesis(dict(executive_thesis or {}))
    if not rows:
        return None
    import matplotlib.pyplot as plt

    labels = [_shorten(str(row.get("normalization_dimension") or "").replace("_", " ").title(), 34) for row in rows]
    values: list[float] = []
    colors: list[str] = []
    states: list[str] = []
    for row in rows:
        state = row.get("current_state") or "not_yet_evidenced"
        score, color = _state_value_and_color(state)
        values.append(score)
        colors.append(color)
        states.append(_shorten(state, 26))

    top_risk = _shorten((invalid_comparison_risk_register or [{}])[0].get("risk_name") or "invalid comparison risk", 42)
    thesis_risk = _shorten(
        str(dict(executive_thesis or {}).get("invalid_comparison_risk", "")).strip(),
        92,
    )
    wrong_variable = _shorten(
        str(dict(executive_thesis or {}).get("dominant_operational_misunderstanding", "")).strip(),
        92,
    )
    fig, ax = _make_fig(w=8.3, h=max(4.0, 0.72 * len(rows) + 2.0))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, state in zip(bars, states):
        ax.text(
            min(bar.get_width() + 0.03, 1.02),
            bar.get_y() + bar.get_height() / 2,
            state,
            va="center",
            fontsize=7.5,
            color=_DARK,
        )
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("Normalization readiness", fontsize=8)
    ax.set_title("Fair Comparison Gate — What Must Be Normalized First", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.text(0.0, -0.16, f"Top invalid comparison risk: {top_risk}", transform=ax.transAxes, fontsize=7.4, color="#555555")
    if thesis_risk and thesis_risk.lower() != "not observed":
        ax.text(0.0, -0.26, f"Strategic comparison signal: {thesis_risk}", transform=ax.transAxes, fontsize=7.1, color="#555555")
    if wrong_variable and wrong_variable.lower() != "not observed":
        ax.text(0.0, -0.36, f"Wrong-variable warning: {wrong_variable}", transform=ax.transAxes, fontsize=7.1, color="#555555")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_cross_layer_congruence_map(
    cross_layer_congruence_register: list[dict[str, Any]],
    executive_thesis: dict[str, Any] | None = None,
) -> str | None:
    rows = [dict(row) for row in list(cross_layer_congruence_register or [])[:5]]
    if not rows:
        rows = _fallback_cross_layer_rows_from_thesis(dict(executive_thesis or {}))
    if not rows:
        return None
    import matplotlib.pyplot as plt

    layer_order: list[str] = []
    for row in rows:
        for layer in list(row.get("layers", []) or []):
            layer_text = str(layer or "").strip()
            if layer_text and layer_text not in layer_order:
                layer_order.append(layer_text)
    if not layer_order:
        return None

    matrix = [
        [1 if layer in list(row.get("layers", []) or []) else 0 for layer in layer_order]
        for row in rows
    ]
    labels = [_shorten(row.get("contradiction") or "cross-layer contradiction", 38) for row in rows]
    states = [_shorten(row.get("evidence_state") or "CONDITIONAL_HYPOTHESIS", 26) for row in rows]
    hidden_boundary = _shorten(
        str(dict(executive_thesis or {}).get("hidden_system_boundary_error", "")).strip(),
        94,
    )
    premature = _shorten(
        str(dict(executive_thesis or {}).get("why_current_question_is_premature", "")).strip(),
        94,
    )

    fig, ax = _make_fig(w=max(7.8, 1.25 * len(layer_order) + 4.8), h=max(4.2, 0.78 * len(rows) + 2.0))
    im = ax.imshow(matrix, cmap="Reds", vmin=0, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Layer engaged")
    ax.set_xticks(range(len(layer_order)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels([_shorten(layer.replace("_", " ").title(), 18) for layer in layer_order], fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_title("Cross-Layer Congruence Map — Where the Case Changes Shape", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.set_xlim(-0.5, len(layer_order) + 0.9)
    for i, state in enumerate(states):
        ax.text(len(layer_order) + 0.1, i, state, va="center", fontsize=7.2, color=_DARK)
    ax.text(len(layer_order) + 0.1, -0.65, "State", fontsize=7.2, color="#666666", fontweight="bold")
    if hidden_boundary and hidden_boundary.lower() != "not observed":
        ax.text(0.0, -0.16, f"Boundary signal: {hidden_boundary}", transform=ax.transAxes, fontsize=7.1, color="#555555")
    if premature and premature.lower() != "not observed":
        ax.text(0.0, -0.26, f"Why premature: {premature}", transform=ax.transAxes, fontsize=7.1, color="#555555")
    plt.tight_layout()
    return _to_b64(fig)


def _measurement_intrusiveness(source: str, upgrade_path: str) -> tuple[float, str]:
    source_l = (source or "").lower()
    upgrade_l = (upgrade_path or "").lower()
    if "utility bill" in source_l or "tariff" in source_l:
        return 1.0, _GREEN
    if "operator document" in source_l or "matrix" in source_l or "existing operational" in source_l:
        return 1.4, _TEAL
    if "bms" in source_l:
        return 1.8, _NAVY
    if "temporary" in source_l or "temporary" in upgrade_l or "analyzer" in source_l:
        return 2.8, _AMBER
    return 2.1, _PURPLE


def _chart_measurement_minimality_path(
    measurement_strategy_register: list[dict[str, Any]],
    hardware_minimality_register: list[dict[str, Any]],
) -> str | None:
    measurement_rows = [dict(row) for row in list(measurement_strategy_register or [])[:5]]
    if not measurement_rows:
        return None
    import matplotlib.pyplot as plt

    hardware_rows = [dict(row) for row in list(hardware_minimality_register or [])]
    labels: list[str] = []
    values: list[float] = []
    colors: list[str] = []
    sources: list[str] = []
    for idx, row in enumerate(measurement_rows):
        hardware = hardware_rows[idx] if idx < len(hardware_rows) else {}
        cheapest_source = hardware.get("cheapest_valid_source") or row.get("minimum_measurement") or "existing operational record"
        intrusiveness, color = _measurement_intrusiveness(
            str(cheapest_source or ""),
            str(hardware.get("upgrade_path") or row.get("hardware_trigger") or ""),
        )
        labels.append(_shorten(row.get("hypothesis") or f"evidence path {idx + 1}", 38))
        values.append(intrusiveness)
        colors.append(color)
        sources.append(_shorten(cheapest_source, 42))

    fig, ax = _make_fig(w=8.4, h=max(4.0, 0.72 * len(labels) + 1.9))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, source in zip(bars, sources):
        ax.text(
            min(bar.get_width() + 0.05, 3.15),
            bar.get_y() + bar.get_height() / 2,
            source,
            va="center",
            fontsize=7.3,
            color=_DARK,
        )
    ax.set_xlim(0, 3.3)
    ax.set_xticks([1.0, 2.0, 3.0], ["docs / bills", "existing systems", "targeted temporary"])
    ax.set_xlabel("Evidence intrusiveness", fontsize=8)
    ax.set_title("Minimum Evidence Before Hardware — Cheapest Valid Path First", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_cost_driver_signal_profile(
    utility_charge_breakdown_register: list[dict[str, Any]],
    tariff_exposure_register: list[dict[str, Any]],
    cost_driver_dependency_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
    executive_thesis: dict[str, Any] | None = None,
) -> str | None:
    bill_rows = [dict(row) for row in list(utility_charge_breakdown_register or [])]
    tariff_rows = [dict(row) for row in list(tariff_exposure_register or [])]
    cost_rows = [dict(row) for row in list(cost_driver_dependency_register or [])]
    finance_rows = [dict(row) for row in list(finance_physics_dependency_register or [])]
    import matplotlib.pyplot as plt

    signals = {
        "Consumption": 0,
        "Demand / Tariff": 0,
        "PF / Reactive": 0,
        "Boundary / Control": 0,
        "Operational Duty": 0,
        "Maintenance / Uptime": 0,
    }

    for row in bill_rows:
        row_text = " ".join(str(v or "") for v in row.values())
        signals["Consumption"] += _signal_score(row_text, tokens=("energy", "consumption", "kwh"))
        signals["Demand / Tariff"] += _signal_score(row_text, tokens=("demand", "kw", "charge"))
        signals["PF / Reactive"] += _signal_score(row_text, tokens=("pf", "power factor", "reactive"))
    for row in tariff_rows:
        exposure = str(row.get("exposure_type") or "")
        signals["Demand / Tariff"] += _signal_score(exposure, tokens=("demand", "time_of_use", "tariff"))
        signals["PF / Reactive"] += _signal_score(exposure, tokens=("pf", "reactive"))
    for row in cost_rows + finance_rows:
        blob = " ".join(str(v or "") for v in row.values())
        signals["Consumption"] += _signal_score(blob, tokens=("consumption", "energy cost"))
        signals["Demand / Tariff"] += _signal_score(blob, tokens=("demand", "tariff", "sequencing"))
        signals["PF / Reactive"] += _signal_score(blob, tokens=("pf", "reactive", "power factor"))
        signals["Boundary / Control"] += _signal_score(blob, tokens=("boundary", "control", "owner", "tenant", "metering"))
        signals["Operational Duty"] += _signal_score(blob, tokens=("continuity", "dispatch", "service level", "movement", "throughput", "temperature duty", "process duty"))
        signals["Maintenance / Uptime"] += _signal_score(blob, tokens=("maintenance", "downtime", "reliability", "failure", "uptime"))

    thesis_blob = _executive_thesis_signal_blob(dict(executive_thesis or {}))
    if thesis_blob:
        signals["Consumption"] += _signal_score(thesis_blob, tokens=("consumption", "energy problem", "energy inefficiency"))
        signals["Demand / Tariff"] += _signal_score(thesis_blob, tokens=("demand", "tariff", "charging", "power factor", "reactive"))
        signals["PF / Reactive"] += _signal_score(thesis_blob, tokens=("pf", "reactive", "power factor"))
        signals["Boundary / Control"] += _signal_score(thesis_blob, tokens=("boundary", "control", "owner", "tenant", "metering", "value capture"))
        signals["Operational Duty"] += _signal_score(thesis_blob, tokens=("service", "throughput", "movement", "dock", "charging", "schedule", "process duty"))
        signals["Maintenance / Uptime"] += _signal_score(thesis_blob, tokens=("maintenance", "uptime", "downtime", "reliability"))
        thesis = dict(executive_thesis or {})
        if str(thesis.get("hidden_system_boundary_error", "")).strip():
            signals["Boundary / Control"] += 1
        if str(thesis.get("invalid_comparison_risk", "")).strip():
            signals["Boundary / Control"] += 1
        if str(thesis.get("dominant_operational_misunderstanding", "")).strip():
            signals["Operational Duty"] += 1
        if str(thesis.get("dominant_loss_logic", "")).strip():
            signals["Operational Duty"] += 1
            signals["Demand / Tariff"] += _signal_score(
                str(thesis.get("dominant_loss_logic", "")),
                tokens=("demand", "tariff", "charging"),
            )
        if str(thesis.get("surprising_but_evidenced_takeaway", "")).strip():
            signals["Consumption"] += _signal_score(
                str(thesis.get("surprising_but_evidenced_takeaway", "")),
                tokens=("energy", "inefficiency", "waste"),
            )

    if not any(signals.values()):
        return None

    labels = list(signals.keys())
    values = [signals[label] for label in labels]
    colors = [_NAVY, _MAROON, _PURPLE, _TEAL, _AMBER, _GREEN]
    wrong_variable = _shorten(str(dict(executive_thesis or {}).get("dominant_operational_misunderstanding", "")).strip(), 92)
    dominant_loss_logic = _shorten(str(dict(executive_thesis or {}).get("dominant_loss_logic", "")).strip(), 92)
    surprising_takeaway = _shorten(str(dict(executive_thesis or {}).get("surprising_but_evidenced_takeaway", "")).strip(), 92)

    fig, ax = _make_fig(w=8.2, h=4.9)
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, value in zip(bars, values):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=7.5, color=_DARK)
    ax.set_xlabel("Signal count across bills, tariff, finance and operating logic", fontsize=8)
    ax.set_title("Cost Driver Signal Profile — What Looks More Material Than Consumption Alone", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    if wrong_variable and wrong_variable.lower() != "not observed":
        ax.text(0.0, -0.16, f"Wrong-variable warning: {wrong_variable}", transform=ax.transAxes, fontsize=7.1, color="#555555")
    if dominant_loss_logic and dominant_loss_logic.lower() != "not observed":
        ax.text(0.0, -0.26, f"Loss logic: {dominant_loss_logic}", transform=ax.transAxes, fontsize=7.1, color="#555555")
    if surprising_takeaway and surprising_takeaway.lower() != "not observed":
        ax.text(0.0, -0.36, f"Strategic takeaway: {surprising_takeaway}", transform=ax.transAxes, fontsize=7.1, color="#555555")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_gap_taxonomy_profile(gap_taxonomy_register: list[dict[str, Any]]) -> str | None:
    rows = [dict(row) for row in list(gap_taxonomy_register or [])]
    if not rows:
        return None
    import matplotlib.pyplot as plt

    counts: dict[str, int] = {}
    for row in rows:
        label = _shorten(str(row.get("gap_type") or row.get("gap_family") or "unclassified_gap").replace("_", " ").title(), 34)
        counts[label] = counts.get(label, 0) + 1
    labels = list(counts.keys())[:6]
    values = [counts[label] for label in labels]
    colors = [_MAROON, _NAVY, _AMBER, _TEAL, _PURPLE, _GREEN][: len(labels)]

    fig, ax = _make_fig(w=8.2, h=max(4.0, 0.70 * len(labels) + 1.8))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, value in zip(bars, values):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=7.5, color=_DARK)
    ax.set_xlabel("Active blocker count", fontsize=8)
    ax.set_title("Gap Taxonomy Profile — What Kind of Missingness Is Blocking", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    plt.tight_layout()
    return _to_b64(fig)


def _search_likelihood_value(value: str) -> tuple[float, str]:
    normalized = str(value or "").lower()
    if normalized == "high":
        return 1.0, _GREEN
    if normalized == "medium":
        return 0.65, _AMBER
    if normalized == "low":
        return 0.35, _RED
    return 0.5, _TEAL


def _chart_next_best_search_path(
    next_best_search_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
) -> str | None:
    rows = [dict(row) for row in list(next_best_search_register or [])[:5]]
    if not rows:
        return None
    import matplotlib.pyplot as plt

    stop_by_need = {
        str(row.get("path_id") or "").strip(): dict(row)
        for row in list(stop_condition_register or [])
        if str(row.get("path_id") or "").strip()
    }
    labels: list[str] = []
    values: list[float] = []
    colors: list[str] = []
    notes: list[str] = []
    for row in rows:
        need_id = str(row.get("need_id") or "").strip()
        score, color = _search_likelihood_value(str(row.get("public_source_likelihood") or ""))
        stop_row = stop_by_need.get(need_id, {})
        labels.append(_shorten(row.get("next_search_target") or need_id or "next search target", 40))
        values.append(score)
        colors.append(color)
        notes.append(_shorten(stop_row.get("stop_condition") or row.get("if_not_found") or "bounded search path", 44))

    fig, ax = _make_fig(w=8.4, h=max(4.1, 0.76 * len(labels) + 2.1))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, note in zip(bars, notes):
        ax.text(min(bar.get_width() + 0.03, 1.02), bar.get_y() + bar.get_height() / 2, note, va="center", fontsize=7.1, color=_DARK)
    ax.set_xlim(0, 1.08)
    ax.set_xticks([0.35, 0.65, 1.0], ["low", "medium", "high"])
    ax.set_xlabel("Public-search payoff before intake escalation", fontsize=8)
    ax.set_title("Next-Best Search Path — What To Search Before Asking Locally", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_peer_requirement_readiness(
    peer_requirement_register: list[dict[str, Any]],
    comparison_blocker_register: list[dict[str, Any]],
) -> str | None:
    rows = [dict(row) for row in list(peer_requirement_register or [])[:6]]
    if not rows:
        return None
    import matplotlib.pyplot as plt

    blocked_codes = {
        str(row.get("blocker_code") or "").strip()
        for row in list(comparison_blocker_register or [])
        if str(row.get("blocker_code") or "").strip()
    }
    labels: list[str] = []
    values: list[float] = []
    colors: list[str] = []
    states: list[str] = []
    for row in rows:
        requirement_key = str(row.get("requirement_key") or "").strip()
        status = str(row.get("comparison_status") or "conditional").strip()
        current = str(row.get("current_evidence") or status).strip()
        score, color = _state_value_and_color(current)
        if requirement_key in blocked_codes or status == "blocked":
            score = min(score, 0.3)
            color = _RED
        labels.append(_shorten(row.get("peer_requirement") or requirement_key or "peer requirement", 40))
        values.append(score)
        colors.append(color)
        states.append(_shorten(status or current, 24))

    fig, ax = _make_fig(w=8.4, h=max(4.0, 0.74 * len(labels) + 1.9))
    bars = ax.barh(labels, values, color=colors, edgecolor="none")
    for bar, state in zip(bars, states):
        ax.text(min(bar.get_width() + 0.03, 1.02), bar.get_y() + bar.get_height() / 2, state, va="center", fontsize=7.3, color=_DARK)
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("Peer requirement readiness", fontsize=8)
    ax.set_title("Peer Requirement Readiness — What Still Blocks Fair Comparison", fontsize=9.5, fontweight="bold", color=_DARK, pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    plt.tight_layout()
    return _to_b64(fig)


def _chart_governance(spec_id: str) -> dict[str, Any]:
    mapping: dict[str, dict[str, Any]] = {
        "chart_congruence_binding_state": {
            "epistemic_marker": "BOUNDED_LOCAL_TRUTH | EVIDENCE_BINDING",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_049.local_truth_confidence_register"],
        },
        "chart_fair_comparison_gate": {
            "epistemic_marker": "COMPARISON_GOVERNANCE | REQUIRES_NORMALIZATION",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_051.normalization_requirements_register", "motor_051.invalid_comparison_risk_register", "motor_047.executive_thesis"],
        },
        "chart_cross_layer_congruence_map": {
            "epistemic_marker": "CONDITIONAL | CROSS_LAYER",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_051.cross_layer_congruence_register", "motor_047.executive_thesis"],
        },
        "chart_measurement_minimality_path": {
            "epistemic_marker": "REQUIRES_VALIDATION | MINIMUM_EVIDENCE",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_052.measurement_strategy_register", "motor_052.hardware_minimality_register"],
        },
        "chart_cost_driver_signal_profile": {
            "epistemic_marker": "CONDITIONAL | FINANCE_TO_PHYSICS",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_049.utility_charge_breakdown_register", "motor_049.tariff_exposure_register", "motor_053.cost_driver_dependency_register", "motor_053.finance_physics_dependency_register", "motor_047.executive_thesis"],
        },
        "chart_gap_taxonomy_profile": {
            "epistemic_marker": "REQUIRES_VALIDATION | GAP_TAXONOMY",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_049.gap_taxonomy_register"],
        },
        "chart_next_best_search_path": {
            "epistemic_marker": "SEARCH_PROGRAM | REQUIRES_VALIDATION",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_049.next_best_search_register", "motor_049.stop_condition_register"],
        },
        "chart_peer_requirement_readiness": {
            "epistemic_marker": "COMPARISON_GATE | REQUIRES_VALIDATION",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_051.peer_requirement_register", "motor_051.comparison_blocker_register"],
        },
        "chart_inference_scores": {
            "epistemic_marker": "INFERRED",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_014.inference_records"],
        },
        "chart_asset_context_completeness": {
            "epistemic_marker": "DIRECT_EVIDENCE | ASSET_CONTEXT",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_012.facility_prior.asset_identity_bundle.observable_cluster_register"],
        },
        "chart_source_scope_balance": {
            "epistemic_marker": "DIRECT_EVIDENCE | SOURCE_SCOPE",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_028.discovery_summary.scope_counts"],
        },
        "chart_context_routing_status": {
            "epistemic_marker": "DIRECT_EVIDENCE | ROUTING_CONTEXT",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_028.enriched_data.target_definition", "motor_028.enriched_data.benchmark_routing_register", "motor_028.enriched_data.asset_geocoder"],
        },
        "chart_investment_uncertainty_map": {
            "epistemic_marker": "BLOCKING_FIELDS | REQUIRES_VALIDATION",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_014.asset_context_readiness_summary", "motor_014.decision_front_register"],
        },
        "chart_minimum_evidence_pack": {
            "epistemic_marker": "REQUIRES_VALIDATION",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_014.minimum_evidence_unlock_map"],
        },
        "chart_decision_front_status": {
            "epistemic_marker": "DECISION_GRADE | ACTION_POSTURE",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_014.decision_front_register"],
        },
        "chart_scenario_space": {
            "epistemic_marker": "CONDITIONAL",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_014.scenario_space"],
        },
        "chart_system_typology_prior": {
            "epistemic_marker": "ARCHETYPAL_PRIOR | REQUIRES_VALIDATION",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_012.facility_prior.system_typology_prior", "motor_012.facility_prior.asset_energy_behavior_prior"],
        },
        "chart_validation_priority": {
            "epistemic_marker": "REQUIRES_VALIDATION",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_014.inference_records"],
        },
        "chart_revenue_trend": {
            "epistemic_marker": "DIRECT_EVIDENCE | CONSOLIDATED_ONLY",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_028.enriched_data.financials.revenues_series"],
        },
        "chart_revenue_composition": {
            "epistemic_marker": "HYPOTHESIS | REQUIRES_VALIDATION",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_028.enriched_data.financials.revenues_annual", "__pipeline__.facility_inputs.input_04_primary_use"],
        },
        "chart_debt_discrepancy": {
            "epistemic_marker": "BLOCKING_CONFLICT | REQUIRES_VALIDATION",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_028.enriched_data.financials.total_debt", "motor_028.enriched_data.extended_sources.ws_debt_leverage"],
        },
        "chart_tenant_concentration": {
            "epistemic_marker": "INFERRED",
            "support_state": "decision_grade",
            "data_dependencies": ["__pipeline__.facility_inputs.input_04_primary_use", "__pipeline__.facility_inputs.input_05_size"],
        },
        "chart_ll97_scenario": {
            "epistemic_marker": "HYPOTHESIS | REQUIRES_VALIDATION",
            "support_state": "screening_grade",
            "data_dependencies": ["__pipeline__.facility_inputs.input_05_size"],
        },
        "chart_evidence_ladder": {
            "epistemic_marker": "INFERRED",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_014.inference_records"],
        },
        "chart_validation_effort_matrix": {
            "epistemic_marker": "REQUIRES_VALIDATION",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_014.inference_records"],
        },
        "chart_ll97_timeline": {
            "epistemic_marker": "DIRECT_EVIDENCE | REGULATORY_CONTEXT",
            "support_state": "decision_grade",
            "data_dependencies": ["__pipeline__.facility_inputs.input_05_size"],
        },
        "chart_causal_dependency": {
            "epistemic_marker": "INFERRED",
            "support_state": "decision_grade",
            "data_dependencies": ["motor_014.inference_records"],
        },
        "chart_scenario_decision": {
            "epistemic_marker": "CONDITIONAL",
            "support_state": "screening_grade",
            "data_dependencies": ["motor_014.inference_records"],
        },
    }
    return mapping.get(spec_id, {
        "epistemic_marker": "DECISION_GRADE",
        "support_state": "decision_grade",
        "data_dependencies": [],
    })


# ── Adapter ────────────────────────────────────────────────────────────────────

class Motor018Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_018"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_008", "motor_004", "motor_005", "motor_006", "motor_007",
                "motor_012", "motor_028", "motor_014", "motor_047", "motor_049", "motor_051", "motor_052", "motor_053"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m28 = inputs.get("motor_028", {})
        m07 = inputs.get("motor_007", {})
        m14 = inputs.get("motor_014", {})
        m47 = inputs.get("motor_047", {})
        executive_thesis = m47.get("executive_thesis", {}) if isinstance(m47.get("executive_thesis", {}), dict) else {}
        m49 = inputs.get("motor_049", {})
        m51 = inputs.get("motor_051", {})
        m52 = inputs.get("motor_052", {})
        m53 = inputs.get("motor_053", {})
        enriched = inputs.get("motor_028", {}).get("enriched_data", {})
        facility_prior = inputs.get("motor_012", {}).get("facility_prior", {})
        financials = enriched.get("financials", {})
        ext_sources = enriched.get("extended_sources", {}) if isinstance(enriched.get("extended_sources", {}), dict) else {}
        inference_records = m14.get("inference_records", [])
        pipeline = inputs.get("__pipeline__", {})
        fi = pipeline.get("facility_inputs", {})
        target_definition = facility_prior.get("target_definition", {}) if isinstance(facility_prior.get("target_definition", {}), dict) else {}
        asset_identity_bundle = facility_prior.get("asset_identity_bundle", {}) if isinstance(facility_prior.get("asset_identity_bundle", {}), dict) else {}
        system_typology_prior = facility_prior.get("system_typology_prior", {}) if isinstance(facility_prior.get("system_typology_prior", {}), dict) else {}
        asset_energy_behavior_prior = facility_prior.get("asset_energy_behavior_prior", {}) if isinstance(facility_prior.get("asset_energy_behavior_prior", {}), dict) else {}
        technical_prior_ceiling = facility_prior.get("technical_prior_ceiling", "")
        company_label = enriched.get("company_name") or pipeline.get("case_title") or "Company"
        asset_label = target_definition.get("target_name") or target_definition.get("target_identifier") or company_label
        benchmark_routing_register = enriched.get("benchmark_routing_register", {}) if isinstance(enriched.get("benchmark_routing_register", {}), dict) else {}
        asset_geocoder = enriched.get("asset_geocoder", {}) if isinstance(enriched.get("asset_geocoder", {}), dict) else {}
        asset_climate_zone = enriched.get("asset_climate_zone")
        discovery_summary = m28.get("discovery_summary", {}) if isinstance(m28.get("discovery_summary", {}), dict) else {}
        decision_front_register = m14.get("decision_front_register", []) if isinstance(m14.get("decision_front_register", []), list) else []
        minimum_evidence_unlock_map = m14.get("minimum_evidence_unlock_map", []) if isinstance(m14.get("minimum_evidence_unlock_map", []), list) else []
        scenario_space = m14.get("scenario_space", []) if isinstance(m14.get("scenario_space", []), list) else []
        asset_context_readiness_summary = m14.get("asset_context_readiness_summary", {}) if isinstance(m14.get("asset_context_readiness_summary", {}), dict) else {}
        weak_asset_identity = technical_prior_ceiling in {"issuer_context_only", "location_only", "asset_context_insufficient"}
        report_identity_state = m07.get("report_identity_state", "")
        thesis_report_mode = m47.get("report_mode", "")
        blocked_report_surface = report_identity_state in {
            "Issuer Context Memo",
            "Address Candidate Brief",
            "Site Candidate Brief",
            "Asset Context Seed Brief",
            "Asset Context Insufficiency Brief",
            "Decision-Blocked Asset Brief",
            "Pre-Verification Asset Brief",
        } or weak_asset_identity
        jurisdiction = [str(x).upper() for x in (target_definition.get("jurisdiction_scope") or [])]
        ll97_applicable_context = any("US-NY" in item or "NYC" in item or "NEW YORK" in item for item in jurisdiction)

        revenues_series = financials.get("revenues_series", [])
        revenues_annual = financials.get("revenues_annual")
        total_debt = financials.get("total_debt")
        public_debt_signal, public_debt_label = _extract_public_debt_signal(ext_sources, total_debt)

        local_truth_confidence_register = m49.get("local_truth_confidence_register", []) if isinstance(m49.get("local_truth_confidence_register", []), list) else []
        utility_charge_breakdown_register = m49.get("utility_charge_breakdown_register", []) if isinstance(m49.get("utility_charge_breakdown_register", []), list) else []
        tariff_exposure_register = m49.get("tariff_exposure_register", []) if isinstance(m49.get("tariff_exposure_register", []), list) else []
        next_best_search_register = m49.get("next_best_search_register", []) if isinstance(m49.get("next_best_search_register", []), list) else []
        stop_condition_register = m49.get("stop_condition_register", []) if isinstance(m49.get("stop_condition_register", []), list) else []
        gap_taxonomy_register = m49.get("gap_taxonomy_register", []) if isinstance(m49.get("gap_taxonomy_register", []), list) else []
        normalization_requirements_register = m51.get("normalization_requirements_register", []) if isinstance(m51.get("normalization_requirements_register", []), list) else []
        invalid_comparison_risk_register = m51.get("invalid_comparison_risk_register", []) if isinstance(m51.get("invalid_comparison_risk_register", []), list) else []
        cross_layer_congruence_register = m51.get("cross_layer_congruence_register", []) if isinstance(m51.get("cross_layer_congruence_register", []), list) else []
        peer_requirement_register = m51.get("peer_requirement_register", []) if isinstance(m51.get("peer_requirement_register", []), list) else []
        comparison_blocker_register = m51.get("comparison_blocker_register", []) if isinstance(m51.get("comparison_blocker_register", []), list) else []
        measurement_strategy_register = m52.get("measurement_strategy_register", []) if isinstance(m52.get("measurement_strategy_register", []), list) else []
        hardware_minimality_register = m52.get("hardware_minimality_register", []) if isinstance(m52.get("hardware_minimality_register", []), list) else []
        finance_physics_dependency_register = m53.get("finance_physics_dependency_register", []) if isinstance(m53.get("finance_physics_dependency_register", []), list) else []
        cost_driver_dependency_register = m53.get("cost_driver_dependency_register", []) if isinstance(m53.get("cost_driver_dependency_register", []), list) else []

        use_structural_section_hints = thesis_report_mode in {
            "Compliance / Investment Screening Brief",
            "System Redesign Hypothesis Brief",
        } or report_identity_state in {
            "Compliance / Investment Screening Brief",
            "System Redesign Hypothesis Brief",
        }
        congruence_section_hints = (
            {
                "binding": "cf_minimum_evidence",
                "comparison": "cf_peer_comparison",
                "contradiction": "cf_dominant_structural_contradiction",
                "measurement": "cf_minimum_evidence",
                "finance": "cf_financial_exposure",
            }
            if use_structural_section_hints
            else {
                "binding": "cf_minimum_evidence",
                "comparison": "cf_peer_comparison",
                "contradiction": "cf_dominant_structural_contradiction",
                "measurement": "cf_minimum_evidence",
                "finance": "cf_financial_exposure",
            }
        )
        congruence_chart_curation_mode = (
            "blocked"
            if blocked_report_surface
            else "structural"
            if use_structural_section_hints
            else "exploratory"
        )
        legacy_chart_curation_mode = (
            "blocked"
            if blocked_report_surface
            else "structural_support"
            if use_structural_section_hints
            else "exploratory_support"
        )

        tenants = fi.get("input_04_primary_use", {})
        size = fi.get("input_05_size", {})
        rentable_sqft = size.get("rentable_office_sqft_approx", 1870000)
        gfa_sqft = size.get("GFA_sqft", 2800118)

        use_mix = {
            tenants.get("use_1", "Office")[:20]: tenants.get("use_1_approx_pct"),
            tenants.get("use_2", "Observatory")[:20]: tenants.get("use_2_approx_pct"),
            tenants.get("use_3", "Retail")[:20]: tenants.get("use_3_approx_pct"),
        }

        congruence_chart_specs = [
            {
                "id": "chart_congruence_binding_state",
                **_chart_copy("chart_congruence_binding_state", curation_mode=congruence_chart_curation_mode),
                "chart_curation_mode": congruence_chart_curation_mode,
                "section_hint": congruence_section_hints["binding"],
                "fn": lambda: _chart_congruence_binding_state(local_truth_confidence_register),
            },
            {
                "id": "chart_fair_comparison_gate",
                **_chart_copy("chart_fair_comparison_gate", curation_mode=congruence_chart_curation_mode),
                "chart_curation_mode": congruence_chart_curation_mode,
                "section_hint": congruence_section_hints["comparison"],
                "fn": lambda: _chart_fair_comparison_gate(
                    normalization_requirements_register,
                    invalid_comparison_risk_register,
                    executive_thesis,
                ),
            },
            {
                "id": "chart_cross_layer_congruence_map",
                **_chart_copy("chart_cross_layer_congruence_map", curation_mode=congruence_chart_curation_mode),
                "chart_curation_mode": congruence_chart_curation_mode,
                "section_hint": congruence_section_hints["contradiction"],
                "fn": lambda: _chart_cross_layer_congruence_map(cross_layer_congruence_register, executive_thesis),
            },
            {
                "id": "chart_measurement_minimality_path",
                **_chart_copy("chart_measurement_minimality_path", curation_mode=congruence_chart_curation_mode),
                "chart_curation_mode": congruence_chart_curation_mode,
                "section_hint": congruence_section_hints["measurement"],
                "fn": lambda: _chart_measurement_minimality_path(
                    measurement_strategy_register,
                    hardware_minimality_register,
                ),
            },
            {
                "id": "chart_cost_driver_signal_profile",
                **_chart_copy("chart_cost_driver_signal_profile", curation_mode=congruence_chart_curation_mode),
                "chart_curation_mode": congruence_chart_curation_mode,
                "section_hint": congruence_section_hints["finance"],
                "fn": lambda: _chart_cost_driver_signal_profile(
                    utility_charge_breakdown_register,
                    tariff_exposure_register,
                    cost_driver_dependency_register,
                    finance_physics_dependency_register,
                    executive_thesis,
                ),
            },
        ]

        dynamic_support_chart_specs = [
            {
                "id": "chart_gap_taxonomy_profile",
                **_chart_copy("chart_gap_taxonomy_profile", curation_mode=legacy_chart_curation_mode),
                "chart_curation_mode": legacy_chart_curation_mode,
                "section_hint": "c3_blocking_conflicts",
                "fn": lambda: _chart_gap_taxonomy_profile(gap_taxonomy_register),
            },
            {
                "id": "chart_next_best_search_path",
                **_chart_copy("chart_next_best_search_path", curation_mode=legacy_chart_curation_mode),
                "chart_curation_mode": legacy_chart_curation_mode,
                "section_hint": "c7_validation_architecture",
                "fn": lambda: _chart_next_best_search_path(
                    next_best_search_register,
                    stop_condition_register,
                ),
            },
            {
                "id": "chart_peer_requirement_readiness",
                **_chart_copy("chart_peer_requirement_readiness", curation_mode=legacy_chart_curation_mode),
                "chart_curation_mode": legacy_chart_curation_mode,
                "section_hint": "c10_competitive_peer",
                "fn": lambda: _chart_peer_requirement_readiness(
                    peer_requirement_register,
                    comparison_blocker_register,
                ),
            },
        ]

        if blocked_report_surface:
            chart_specs = [
                {
                    "id": "chart_source_scope_balance",
                    **_chart_copy("chart_source_scope_balance", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c1_framework_brief",
                    "fn": lambda: _chart_source_scope_balance(discovery_summary),
                },
                {
                    "id": "chart_asset_context_completeness",
                    **_chart_copy("chart_asset_context_completeness", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c2_operational_identity",
                    "fn": lambda: _chart_asset_context_completeness(asset_identity_bundle),
                },
                {
                    "id": "chart_investment_uncertainty_map",
                    **_chart_copy("chart_investment_uncertainty_map", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c4_inference_case_map",
                    "fn": lambda: _chart_investment_uncertainty_map(asset_context_readiness_summary, decision_front_register),
                },
                {
                    "id": "chart_minimum_evidence_pack",
                    **_chart_copy("chart_minimum_evidence_pack", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c7_validation_architecture",
                    "fn": lambda: _chart_minimum_evidence_pack(minimum_evidence_unlock_map),
                },
                {
                    "id": "chart_scenario_space",
                    **_chart_copy("chart_scenario_space", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c6_tension_map",
                    "fn": lambda: _chart_scenario_space(scenario_space),
                },
                {
                    "id": "chart_decision_front_status",
                    **_chart_copy("chart_decision_front_status", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c8_conditional_opportunities",
                    "fn": lambda: _chart_decision_front_status(decision_front_register),
                },
                {
                    "id": "chart_context_routing_status",
                    **_chart_copy("chart_context_routing_status", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c5_energy_normative",
                    "fn": lambda: _chart_context_routing_status(target_definition, asset_geocoder, asset_climate_zone, benchmark_routing_register),
                },
                {
                    "id": "chart_system_typology_prior",
                    **_chart_copy("chart_system_typology_prior", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c5_energy_normative",
                    "fn": lambda: _chart_system_typology_prior(system_typology_prior, asset_energy_behavior_prior),
                },
            ] + congruence_chart_specs + dynamic_support_chart_specs
        else:
            chart_specs = [
                {
                    "id": "chart_asset_context_completeness",
                    **_chart_copy("chart_asset_context_completeness", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c2_operational_identity",
                    "fn": lambda: _chart_asset_context_completeness(asset_identity_bundle),
                },
                {
                    "id": "chart_source_scope_balance",
                    **_chart_copy("chart_source_scope_balance", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c1_framework_brief",
                    "fn": lambda: _chart_source_scope_balance(discovery_summary),
                },
                {
                    "id": "chart_context_routing_status",
                    **_chart_copy("chart_context_routing_status", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c5_energy_normative",
                    "fn": lambda: _chart_context_routing_status(target_definition, asset_geocoder, asset_climate_zone, benchmark_routing_register),
                },
                {
                    "id": "chart_system_typology_prior",
                    **_chart_copy("chart_system_typology_prior", curation_mode=legacy_chart_curation_mode),
                    "chart_curation_mode": legacy_chart_curation_mode,
                    "section_hint": "c5_energy_normative",
                    "fn": lambda: _chart_system_typology_prior(system_typology_prior, asset_energy_behavior_prior),
                },
                {
                    "id": "chart_inference_scores",
                    **_chart_copy("chart_inference_scores", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c4_inference_case_map",
                    "fn": lambda: _chart_inference_scores(inference_records),
                },
                {
                    "id": "chart_validation_priority",
                    **_chart_copy("chart_validation_priority", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c7_validation_architecture",
                    "fn": lambda: _chart_validation_priority(inference_records),
                },
                {
                    "id": "chart_revenue_trend",
                    **_chart_copy("chart_revenue_trend", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "title": f"{company_label} Revenue Trend",
                    "title_es": f"Tendencia de Ingresos de {company_label}",
                    "section_hint": "c9_financial_context",
                    "fn": lambda: None if weak_asset_identity else _chart_revenue_trend(revenues_series, company_label),
                },
                {
                    "id": "chart_revenue_composition",
                    **_chart_copy("chart_revenue_composition", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c9_financial_context",
                    "fn": lambda: None if weak_asset_identity else _chart_revenue_composition(revenues_annual, use_mix),
                },
                {
                    "id": "chart_debt_discrepancy",
                    **_chart_copy("chart_debt_discrepancy", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c3_blocking_conflicts",
                    "fn": lambda: None if weak_asset_identity else _chart_debt_discrepancy(total_debt, public_debt_signal, public_debt_label),
                },
                {
                    "id": "chart_tenant_concentration",
                    **_chart_copy("chart_tenant_concentration", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c6_tension_map",
                    "fn": lambda: None if weak_asset_identity else _chart_tenant_concentration(tenants, rentable_sqft),
                },
                {
                    "id": "chart_ll97_scenario",
                    **_chart_copy("chart_ll97_scenario", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c5_energy_normative",
                    "fn": lambda: _chart_ll97_scenario(gfa_sqft) if ll97_applicable_context else None,
                },
                {
                    "id": "chart_evidence_ladder",
                    **_chart_copy("chart_evidence_ladder", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c4_inference_case_map",
                    "fn": lambda: _chart_evidence_ladder(inference_records),
                },
                {
                    "id": "chart_validation_effort_matrix",
                    **_chart_copy("chart_validation_effort_matrix", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c7_validation_architecture",
                    "fn": lambda: _chart_validation_effort_matrix(inference_records),
                },
                {
                    "id": "chart_ll97_timeline",
                    **_chart_copy("chart_ll97_timeline", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c5_energy_normative",
                    "fn": lambda: _chart_ll97_timeline(gfa_sqft) if ll97_applicable_context else None,
                },
                {
                    "id": "chart_causal_dependency",
                    **_chart_copy("chart_causal_dependency", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c3_blocking_conflicts",
                    "fn": lambda: _chart_causal_dependency(inference_records),
                },
                {
                    "id": "chart_scenario_decision",
                    **_chart_copy("chart_scenario_decision", curation_mode="default"),
                    "chart_curation_mode": "default",
                    "section_hint": "c8_conditional_opportunities",
                    "fn": lambda: _chart_scenario_decision(inference_records),
                },
            ] + congruence_chart_specs + dynamic_support_chart_specs

        chart_assets = []
        chart_errors = []

        for original_chart_index, spec in enumerate(chart_specs):
            try:
                b64 = spec["fn"]()
                if b64:
                    governance = _chart_governance(spec["id"])
                    story = _chart_story(
                        spec["id"],
                        curation_mode=spec.get("chart_curation_mode", "default"),
                    )
                    strategic_value = _chart_strategic_value(
                        spec["id"],
                        curation_mode=spec.get("chart_curation_mode", "default"),
                    )
                    binding = _chart_intelligence_binding(spec["id"], executive_thesis)
                    chart_assets.append({
                        "asset_id": spec["id"],
                        "asset_type": "chart",
                        "chart_category": chart_category(spec["id"]),
                        "chart_lane": chart_lane(spec["id"]),
                        "chart_intent": chart_intent(spec["id"]),
                        "chart_category_catalog_version": CHART_TAXONOMY_CATALOG_VERSION,
                        "chart_taxonomy_catalog_version": CHART_TAXONOMY_CATALOG_VERSION,
                        "title": spec["title"],
                        "description": spec["description"],
                        "title_en": spec.get("title_en", spec["title"]),
                        "title_es": spec.get("title_es", ""),
                        "description_en": spec.get("description_en", spec["description"]),
                        "description_es": spec.get("description_es", ""),
                        "chart_curation_mode": spec.get("chart_curation_mode", "default"),
                        "section_hint": spec["section_hint"],
                        "data_source": "motor_018 — pipeline analytical data",
                        "epistemic_marker": governance["epistemic_marker"],
                        "support_state": governance["support_state"],
                        "data_dependencies": governance["data_dependencies"],
                        "chart_role": story["chart_role"],
                        "reader_takeaway": story["reader_takeaway"],
                        "text_pairing_guidance": story["text_pairing_guidance"],
                        "strategic_value_score": strategic_value["strategic_value_score"],
                        "strategic_value_tier": strategic_value["strategic_value_tier"],
                        "strategic_value_reason": strategic_value["strategic_value_reason"],
                        "binding_anchor_type": binding["binding_anchor_type"],
                        "binding_state": binding["binding_state"],
                        "binding_reason": binding["binding_reason"],
                        "contradiction_id": binding["contradiction_id"],
                        "contradiction_label": binding["contradiction_label"],
                        "hypothesis_id": binding["hypothesis_id"],
                        "hypothesis_label": binding["hypothesis_label"],
                        "nugget_id": binding["nugget_id"],
                        "nugget_label": binding["nugget_label"],
                        "original_chart_index": original_chart_index,
                        "image_b64": b64,
                        "width_mm": 170,
                        "height_mm": 90,
                        "produced_by_motor": "motor_018",
                    })
            except Exception as exc:
                chart_errors.append({"id": spec["id"], "error": str(exc)})

        case_namespace_register = build_case_namespace_register(
            target_definition=target_definition,
            case_title=str(pipeline.get("case_title", "")).strip() if isinstance(pipeline, dict) else "",
            document_visible_type=report_identity_state or thesis_report_mode,
        )
        chart_assets = stamp_chart_asset_case_context(
            chart_assets=chart_assets,
            case_namespace_register=case_namespace_register,
        )
        chart_assets = sorted(
            list(chart_assets or []),
            key=lambda row: (
                -int(row.get("strategic_value_score", 0) or 0),
                int(row.get("original_chart_index", 0) or 0),
            ),
        )
        chart_strategic_value_register = [
            {
                "asset_id": str(asset.get("asset_id", "")).strip(),
                "strategic_value_score": int(asset.get("strategic_value_score", 0) or 0),
                "strategic_value_tier": str(asset.get("strategic_value_tier", "")).strip(),
                "strategic_value_reason": str(asset.get("strategic_value_reason", "")).strip(),
                "binding_anchor_type": str(asset.get("binding_anchor_type", "")).strip(),
                "binding_state": str(asset.get("binding_state", "")).strip(),
                "contradiction_id": str(asset.get("contradiction_id", "")).strip(),
                "hypothesis_id": str(asset.get("hypothesis_id", "")).strip(),
                "nugget_id": str(asset.get("nugget_id", "")).strip(),
                "chart_curation_mode": str(asset.get("chart_curation_mode", "")).strip(),
                "section_hint": str(asset.get("section_hint", "")).strip(),
            }
            for asset in chart_assets
        ]
        chart_strategic_value_summary = {
            "thesis_critical_count": sum(
                1 for asset in chart_assets if str(asset.get("strategic_value_tier", "")).strip() == "thesis_critical"
            ),
            "strategic_support_count": sum(
                1 for asset in chart_assets if str(asset.get("strategic_value_tier", "")).strip() == "strategic_support"
            ),
            "supportive_context_count": sum(
                1 for asset in chart_assets if str(asset.get("strategic_value_tier", "")).strip() == "supportive_context"
            ),
            "decorative_risk_count": sum(
                1 for asset in chart_assets if str(asset.get("strategic_value_tier", "")).strip() == "decorative_risk"
            ),
        }

        return {
            "chart_assets": chart_assets,
            "total_charts": len(chart_assets),
            "chart_errors": chart_errors,
            "chart_strategic_value_register": chart_strategic_value_register,
            "chart_strategic_value_summary": chart_strategic_value_summary,
            "case_namespace_register": case_namespace_register,
        }
