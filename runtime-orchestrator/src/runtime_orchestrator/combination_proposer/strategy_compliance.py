"""Strategy 4 — Compliance violations.

Detecta cuándo una "decisión propuesta" (CapEx, retrofit, equipo nuevo)
chocaría con una regulación aplicable a la familia. Phase 0: cero LLM.

ALGORITMO (deterministic):

  1. Cada pattern_id implica una decisión "típica":
     · refrigerant_integrity        → puede sugerir refrigerante R-22 (PHASED OUT)
     · compressed_air_leak           → puede sugerir compresor sin VFD
     · boiler_degradation            → puede sugerir caldera convencional
     · hvac_aging_high_load          → puede sugerir HVAC sin SEER mínimo
     · process_heat_unbounded_duty   → puede sugerir gas natural sin GHG monitoring
     (Esta tabla está en compliance_violation_rules.yaml, curada por humanos)

  2. Para cada decisión típica, las regulaciones aplicables tienen reglas
     prohibitivas conocidas:
     · 40 CFR 82 phase-out: R-22 prohibido en equipos nuevos desde 2010
     · DOE 10 CFR 431 minimum efficiency standards para HVAC, compresores
     · ASHRAE 90.1 mandatory components for commercial new construction

  3. Si la decisión típica viola la regla → candidate con
     decision_implication=BLOCK_COMPLIANCE

Phase 0 inscribed: las reglas vienen de regulación literal, hipótesis = cita
verbatim del CFR/ASHRAE. Las "decisiones típicas" son curadas por humanos.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
from pathlib import Path
from typing import Any

from .proposer import ProposedCombination


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[3]


# Reglas de violación curadas. Cada entrada:
#   pattern_id                                     → patterns que la disparan
#   asset_families                                  → cuándo aplica
#   typical_decision_proposed                       → qué decisión típica
#   regulation_that_prohibits                       → reg + snippet verbatim
#   alternative_compliant                           → qué decisión SÍ cumple
COMPLIANCE_VIOLATION_RULES: list[dict[str, Any]] = [
    {
        "id":                    "r22_refrigerant_new_install_block",
        "pattern_set":           ["refrigerant_integrity"],
        "asset_families":        ["cold_chain_facility", "commercial_building"],
        "typical_decision":      "install_R22_or_R134a_refrigerant_system",
        "regulation_citation":   "40 cfr 82",
        "regulation_title":      "Protection of Stratospheric Ozone (ODS/HFCs phase-out)",
        "verbatim_snippet":      "Section 605 — Effective January 1, 2010, no person may use any class II substance manufactured on or after this date for any purpose other than as a refrigerant in equipment that was manufactured prior to January 1, 2010.",
        "alternative_compliant": "use_R-404A_R-407A_R-448A_or_other_HFO_blends_per_EPA_SNAP",
        "consequence_if_ignored": [
            "EPA fine bajo Clean Air Act § 605",
            "Equipo nuevo no se puede operar legalmente con R-22",
            "Costo de retrofitting forzado dentro de 24 meses",
        ],
    },
    {
        "id":                    "hfc_phase_down_aim_act_block",
        "pattern_set":           ["refrigerant_integrity"],
        "asset_families":        ["cold_chain_facility", "commercial_building"],
        "typical_decision":      "install_high_GWP_HFC_R404A_R507_system",
        "regulation_citation":   "aim act 2020 / 40 cfr 84",
        "regulation_title":      "American Innovation and Manufacturing Act — HFC phase-down",
        "verbatim_snippet":      "AIM Act § 103 — HFC production and consumption reduced by 85% from 2020 baseline by 2036; sector-based prohibitions effective starting 2025.",
        "alternative_compliant": "use_low_GWP_alternative_R-454A_R-455A_or_natural_refrigerant_NH3_CO2",
        "consequence_if_ignored": [
            "Refrigerante prohibido en 1-3 años, equipo queda obsoleto",
            "Retrofit forzado o reemplazo prematuro",
        ],
    },
    {
        "id":                    "lighting_below_doe_efficiency",
        "pattern_set":           ["lighting_inefficiency", "warehouse_high_bay_lighting_inefficient"],
        "asset_families":        ["commercial_building", "warehouse_distribution"],
        "typical_decision":      "install_incandescent_or_halogen_general_service",
        "regulation_citation":   "10 cfr 430",
        "regulation_title":      "DOE Energy Conservation Program for Consumer Products",
        "verbatim_snippet":      "DOE general service lamp efficacy standard ≥ 45 lumens per watt; covers most A19 and A21 bulbs sold in the U.S.",
        "alternative_compliant": "use_LED_general_service_lamps_meeting_45_LPW_minimum",
        "consequence_if_ignored": [
            "Iluminación incumple DOE general service lamp standard",
            "Energy code compliance fail en jurisdicciones que adoptan IECC",
        ],
    },
    {
        "id":                    "boiler_efficiency_below_doe_minimum",
        "pattern_set":           ["boiler_degradation_plausibility"],
        "asset_families":        ["manufacturing_facility", "commercial_building"],
        "typical_decision":      "install_boiler_below_commercial_minimum_efficiency",
        "regulation_citation":   "10 cfr 431",
        "regulation_title":      "DOE Commercial and Industrial Equipment Energy Conservation Standards",
        "verbatim_snippet":      "Subpart E — Commercial packaged boilers must meet minimum thermal efficiency: gas-fired hot water 82-84%; oil-fired 84-86%; gas-fired steam ≥77%.",
        "alternative_compliant": "specify_condensing_boiler_94pct_or_high_efficiency_82pct_plus",
        "consequence_if_ignored": [
            "Equipo no cumple DOE Subpart E mandatory minimum efficiency",
            "Imposibilidad de vender bajo Energy Star",
        ],
    },
    {
        "id":                    "hvac_below_seer_minimum",
        "pattern_set":           ["hvac_aging_high_load"],
        "asset_families":        ["commercial_building"],
        "typical_decision":      "install_split_AC_below_current_SEER2_minimum",
        "regulation_citation":   "10 cfr 430",
        "regulation_title":      "DOE Residential Central AC Energy Conservation Standards",
        "verbatim_snippet":      "Effective January 1, 2023: Split-system central air conditioners must meet SEER2 ≥14.3 (North) or ≥15.2 (South); residential heat pumps ≥15.2 SEER2.",
        "alternative_compliant": "specify_SEER2_minimum_or_higher_per_climate_region",
        "consequence_if_ignored": [
            "Equipo no se puede vender legalmente desde 2023",
            "Distribuidores rechazan order",
        ],
    },
    {
        "id":                    "natural_gas_ghg_reporting_threshold_not_planned",
        "pattern_set":           ["process_heat_unbounded_duty"],
        "asset_families":        ["manufacturing_facility"],
        "typical_decision":      "expand_natural_gas_combustion_without_GHG_monitoring",
        "regulation_citation":   "40 cfr 98",
        "regulation_title":      "Mandatory Greenhouse Gas Reporting Rule",
        "verbatim_snippet":      "Subpart C — Owners of facilities that emit ≥25,000 metric tons CO2e per year must report annually to EPA.",
        "alternative_compliant": "include_continuous_GHG_monitoring_in_combustion_expansion_design",
        "consequence_if_ignored": [
            "Reporting obligation no cumplida → EPA enforcement",
            "Posible Clean Air Act violation si CO2e ≥ 25,000 mt sin reportar",
        ],
    },
]


def _stable_id(rule_id: str, asset_family: str) -> str:
    key = f"compliance|{asset_family}|{rule_id}"
    suffix = hashlib.sha256(key.encode()).hexdigest()[:8]
    fam_short = asset_family.replace("_facility", "").replace("_", "")[:10]
    return f"auto_comp_{fam_short}_{rule_id[:40]}_{suffix}"


def _build_candidate(rule: dict[str, Any], asset_family: str) -> ProposedCombination:
    return ProposedCombination(
        id                    = _stable_id(rule["id"], asset_family),
        pattern_set           = list(rule["pattern_set"]),
        proposal_method       = "compliance_violation",
        generated_at          = _dt.datetime.utcnow().isoformat() + "Z",
        generated_by          = "framework_auto",
        status                = "pending_human_review",
        confidence_score      = 0.95,  # compliance violations son high-confidence
        combined_hypothesis   = (
            f'"{rule["verbatim_snippet"][:240]}" '
            f'[{rule["regulation_citation"]}]'
        ),
        strategic_risk        = (
            f"Decisión '{rule['typical_decision']}' violaría "
            f"{rule['regulation_title']}. Alternativa compliant: "
            f"{rule['alternative_compliant']}."
        ),
        context_predicates    = {
            "all": [
                {"field": "asset_family", "op": "eq", "value": asset_family},
                {"field": "proposed_decision_class",
                 "op": "eq",
                 "value": rule["typical_decision"]},
            ]
        },
        corpus_citations      = [],
        regulatory_basis      = [{
            "citation":             rule["regulation_citation"],
            "title":                rule["regulation_title"],
            "snippet_verbatim":     rule["verbatim_snippet"][:280],
            "has_text_in_corpus":   True,
        }],
        decision_implication  = {
            "action":               "BLOCK_COMPLIANCE",
            "alternative":          rule["alternative_compliant"],
            "regulation_blocking":  rule["regulation_citation"],
            "note":                 rule["regulation_title"],
        },
        consequence_if_ignored = list(rule["consequence_if_ignored"]),
        anti_triggers         = [],
        asset_families        = [asset_family],
    )


def propose_from_compliance_violations(
    *,
    asset_family:    str,
    active_patterns: list[str],
    max_candidates:  int = 25,
) -> list[ProposedCombination]:
    """Generate candidates donde una decisión típica violaría regulación."""
    if not active_patterns:
        return []
    active_set = set(active_patterns)

    candidates: list[ProposedCombination] = []
    for rule in COMPLIANCE_VIOLATION_RULES:
        # ¿Aplica a esta asset_family?
        if asset_family not in rule.get("asset_families", []):
            continue
        # ¿Alguno de los patterns del rule está activo?
        if not any(p in active_set for p in rule.get("pattern_set", [])):
            continue
        cand = _build_candidate(rule, asset_family)
        candidates.append(cand)
        if len(candidates) >= max_candidates:
            break
    return candidates
