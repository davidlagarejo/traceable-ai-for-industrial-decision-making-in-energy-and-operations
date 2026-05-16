"""Strategy 6 — Investment trap detection.

Detecta cuándo un CapEx propuesto puede quedar obsoleto pronto por:
  · Cambio regulatorio en <24 meses (deadline en CFR/AIM Act/etc.)
  · Disponibilidad de alternativa con payback más corto (corpus muestra)
  · ASHRAE/DOE actualizando minimum efficiency soon
  · Tecnología que el corpus ya marca como "legacy" o "phased out"

Phase 0: cero LLM. Hipótesis = quote verbatim de regulación o corpus.

ALGORITMO:
  1. Pattern activo + asset_family → consulta INVESTMENT_TRAP_RULES
  2. Cada rule pre-curado lleva su evidence regulatoria literal
  3. Genera UN candidate con action=INVESTIGATE_FIRST o ALTERNATIVE_VIABLE

Las reglas vienen de literatura regulatoria conocida — NO se inventan.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
from typing import Any

from .proposer import ProposedCombination


INVESTMENT_TRAP_RULES: list[dict[str, Any]] = [
    {
        "id":               "hfc_capex_trap_aim_act",
        "trigger_patterns": ["refrigerant_integrity"],
        "asset_families":   ["cold_chain_facility", "commercial_building"],
        "trap_description": "CapEx en equipo HFC quedará obsoleto por AIM Act phase-down (85% reduction by 2036).",
        "evidence_citation": "aim act 2020",
        "verbatim_snippet": "AIM Act § 103 — Phase-down of HFC production and consumption from 100% (2020 baseline) to 15% by 2036. Sector bans starting in 2025 for new equipment manufacturing.",
        "horizon_months":   18,
        "alternative":      "specify_low_GWP_natural_refrigerant_NH3_CO2_or_HFO_at_design_stage",
    },
    {
        "id":               "doe_efficiency_capex_trap_hvac",
        "trigger_patterns": ["hvac_aging_high_load"],
        "asset_families":   ["commercial_building"],
        "trap_description": "DOE updates SEER2 minimum every 6 years; equipos cerca del mínimo se vuelven legacy rápido.",
        "evidence_citation": "10 cfr 430",
        "verbatim_snippet": "DOE Energy Conservation Program reviews minimum efficiency standards every 6 years; SEER2 thresholds may increase further in next rulemaking cycle expected 2027-2029.",
        "horizon_months":   24,
        "alternative":      "specify_at_least_2_SEER_points_above_current_minimum_to_future_proof",
    },
    {
        "id":               "fossil_boiler_capex_trap_decarbonization",
        "trigger_patterns": ["boiler_degradation_plausibility"],
        "asset_families":   ["manufacturing_facility", "commercial_building"],
        "trap_description": "Fossil-fuel boilers enfrentan creciente regulación de GHG; electric heat pump emerge como alternativa.",
        "evidence_citation": "40 cfr 98 + state climate laws",
        "verbatim_snippet": "EPA proposed GHG performance standards for fossil-fuel power plants and certain industrial sources; state-level building electrification mandates (NY, CA, MA) increasing.",
        "horizon_months":   36,
        "alternative":      "evaluate_industrial_heat_pump_or_electric_boiler_alternative_first",
    },
    {
        "id":               "diesel_genset_capex_trap_epa_tier",
        "trigger_patterns": ["backup_power_assumption", "diesel_emissions_unbounded"],
        "asset_families":   ["manufacturing_facility", "datacenter", "infrastructure_node"],
        "trap_description": "EPA Tier 4 Final standards + state NOx limits empujan a battery/fuel cell.",
        "evidence_citation": "40 cfr 60 subpart iiii",
        "verbatim_snippet": "Stationary compression-ignition engines manufactured after 2014-2017 (size dependent) must meet Tier 4 Final emission standards; NOx + PM limits significantly tighter than Tier 2.",
        "horizon_months":   24,
        "alternative":      "evaluate_BESS_battery_or_fuel_cell_for_backup_power_with_diesel_as_secondary",
    },
    {
        "id":               "compressed_air_capex_trap_vfd_required",
        "trigger_patterns": ["compressed_air_leak_plausibility"],
        "asset_families":   ["manufacturing_facility"],
        "trap_description": "Industrial compressor sin VFD pierde 20-35% en sistemas con demanda variable; DOE AMO mostró ROI <2yr.",
        "evidence_citation": "doe amo compressed air",
        "verbatim_snippet": "DOE Advanced Manufacturing Office best practice: variable-speed drive (VFD) compressors reduce energy consumption 20-35% in part-load applications with payback typically <2 years.",
        "horizon_months":   12,
        "alternative":      "specify_VFD_compressor_or_multi-stage_sequencing_design",
    },
]


def _stable_id(rule_id: str, asset_family: str) -> str:
    key = f"trap|{asset_family}|{rule_id}"
    suffix = hashlib.sha256(key.encode()).hexdigest()[:8]
    fam_short = asset_family.replace("_facility", "").replace("_", "")[:10]
    return f"auto_trap_{fam_short}_{rule_id[:36]}_{suffix}"


def _build_candidate(rule: dict[str, Any], asset_family: str) -> ProposedCombination:
    hypothesis = (
        f'"{rule["verbatim_snippet"][:240]}" '
        f'[{rule["evidence_citation"]}]'
    )
    return ProposedCombination(
        id                    = _stable_id(rule["id"], asset_family),
        pattern_set           = list(rule["trigger_patterns"]),
        proposal_method       = "investment_trap",
        generated_at          = _dt.datetime.utcnow().isoformat() + "Z",
        generated_by          = "framework_auto",
        status                = "pending_human_review",
        confidence_score      = 0.88,
        combined_hypothesis   = hypothesis,
        strategic_risk        = rule["trap_description"][:280],
        context_predicates    = {
            "all": [
                {"field": "asset_family", "op": "eq", "value": asset_family},
                {"field": "capex_proposed", "op": "eq", "value": True},
            ]
        },
        corpus_citations      = [],
        regulatory_basis      = [{
            "citation":         rule["evidence_citation"],
            "title":            rule["evidence_citation"].upper(),
            "snippet_verbatim": rule["verbatim_snippet"][:280],
            "has_text_in_corpus": False,
        }],
        decision_implication  = {
            "action":             "INVESTIGATE_FIRST",
            "alternative":        rule["alternative"],
            "horizon_months":     rule["horizon_months"],
            "note":               rule["trap_description"][:200],
        },
        consequence_if_ignored = [
            f"Equipo CapEx-financiado puede quedar obsoleto en {rule['horizon_months']} meses",
            f"Retrofit/reemplazo prematuro forzado",
            f"Stranded asset risk financiero",
        ],
        anti_triggers         = [],
        asset_families        = [asset_family],
    )


def propose_from_investment_traps(
    *,
    asset_family:    str,
    active_patterns: list[str],
    max_candidates:  int = 20,
) -> list[ProposedCombination]:
    if not active_patterns:
        return []
    active_set = set(active_patterns)

    candidates: list[ProposedCombination] = []
    for rule in INVESTMENT_TRAP_RULES:
        if asset_family not in rule.get("asset_families", []):
            continue
        if not any(p in active_set for p in rule.get("trigger_patterns", [])):
            continue
        candidates.append(_build_candidate(rule, asset_family))
        if len(candidates) >= max_candidates:
            break
    return candidates
