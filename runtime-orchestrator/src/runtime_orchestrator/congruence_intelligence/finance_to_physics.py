from __future__ import annotations

from typing import Any

from .schemas import text


def _exposure(
    *,
    exposure_type: str,
    trigger: str,
    why_it_matters: str,
    evidence_needed: list[str],
    tad_consequence: str,
) -> dict[str, Any]:
    return {
        "financial_exposure_type": text(exposure_type),
        "trigger": text(trigger),
        "why_it_matters": text(why_it_matters),
        "evidence_needed": list(evidence_needed or []),
        "tad_consequence": text(tad_consequence),
    }


def build_finance_physics_dependency_register(
    *,
    asset_family_research_profile: dict[str, Any],
    fair_comparison_profile: dict[str, Any],
    cross_layer_congruence_register: list[dict[str, Any]],
    measurement_strategy_register: list[dict[str, Any]],
    maintenance_reality_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    asset_family = text(asset_family_research_profile.get("asset_family"))
    rows: list[dict[str, Any]] = []

    if asset_family == "commercial_building":
        rows.append(
            {
                "financial_assumption": "owner economics track whole-building performance pressure",
                "physical_dependency": "owner control over the dominant covered load and schedule boundary",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "risk_if_wrong": "Owner-side CAPEX can improve site metrics without improving owner-capturable economics.",
                "evidence_needed": ["utility bills", "tenant metering map", "lease responsibility matrix", "central plant topology"],
            }
        )
        rows.append(
            {
                "financial_assumption": "benchmark-exposed asset implies owner retrofit value",
                "physical_dependency": "the benchmarked load must sit in a controllable owner boundary rather than tenant behavior or contract structure",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "risk_if_wrong": "The case becomes a control-boundary or compliance-architecture problem, not a simple retrofit case.",
                "evidence_needed": ["tenant schedule evidence", "LL97 filing basis", "control-boundary map"],
            }
        )

    if asset_family == "infrastructure_node":
        rows.append(
            {
                "financial_assumption": "headline energy or demand cost is the main economic problem",
                "physical_dependency": "service continuity burden, dispatch duty and redundancy class must not be the real drivers of the visible cost structure",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "risk_if_wrong": "Optimization capital can target a secondary utility symptom while the real economic boundary remains uptime, continuity or constrained dispatch.",
                "evidence_needed": ["utility bills", "tariff structure", "service continuity or dispatch logs", "equipment inventory"],
            }
        )
        rows.append(
            {
                "financial_assumption": "tariff pressure can be optimized without affecting reliability posture",
                "physical_dependency": "switching logic, redundancy policy and maintenance reality must allow tariff-aware operational changes",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "risk_if_wrong": "The case can optimize PF, demand or sequencing on paper while increasing reliability or service risk in practice.",
                "evidence_needed": ["tariff structure", "demand profile", "maintenance logs", "continuity or outage history"],
            }
        )

    if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"}:
        rows.append(
            {
                "financial_assumption": "headline energy cost is the main economic problem",
                "physical_dependency": "cost must be driven by controllable support-system loss rather than structural process duty, throughput or thermal load",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "risk_if_wrong": "CAPEX can target a secondary symptom while margin leakage stays in throughput, reliability or thermal duty.",
                "evidence_needed": ["utility bills", "throughput by shift", "process map", "equipment inventory"],
            }
        )
        rows.append(
            {
                "financial_assumption": "maintenance is secondary to utility economics",
                "physical_dependency": "downtime, scrap and failure cost must be immaterial relative to the utility or tariff story",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "risk_if_wrong": "The business funds utility-oriented action while the real value leak remains in uptime, scrap or maintenance discipline.",
                "evidence_needed": ["maintenance logs", "downtime records", "failure history", "critical-spares evidence"],
            }
        )

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        rows.append(
            {
                "financial_assumption": "area-normalized energy captures the economics",
                "physical_dependency": "service level, temperature duty, movement intensity and charging profile must not dominate cost logic",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
                "risk_if_wrong": "Optimization can target area-based symptoms while the real cost driver is service complexity or duty boundary.",
                "evidence_needed": ["service-level proxy", "dock activity profile", "charging schedule", "temperature-duty map where relevant"],
            }
        )

    _ = fair_comparison_profile
    _ = cross_layer_congruence_register
    _ = measurement_strategy_register
    _ = maintenance_reality_register
    return rows


def build_cost_driver_dependency_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_value_flow_register: list[dict[str, Any]],
    power_quality_hypothesis_register: list[dict[str, Any]],
    maintenance_reality_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    asset_family = text(asset_family_research_profile.get("asset_family"))
    base_driver = "service continuity and compliant operations" if asset_family == "commercial_building" else "throughput, uptime and process-duty economics" if asset_family in {"industrial_manufacturing", "thermal_process_site", "utility_heavy_site"} else "service continuity, dispatch burden and redundancy economics" if asset_family == "infrastructure_node" else "service level and movement / storage integrity"
    rows = [
        {
            "cost_driver": base_driver,
            "physical_dependency": text((operational_value_flow_register or [{}])[0].get("value_logic")) or "dominant system boundary still needs local evidence",
            "evidence_state": text((operational_value_flow_register or [{}])[0].get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
        }
    ]
    if power_quality_hypothesis_register:
        rows.append(
            {
                "cost_driver": "tariff and demand structure",
                "physical_dependency": "inductive-load behavior, sequencing and demand peaks",
                "evidence_state": text((power_quality_hypothesis_register or [{}])[0].get("evidence_state")) or "CONDITIONAL_HYPOTHESIS",
            }
        )
    if any("downtime economics" in text(row.get("reality_claim")).lower() for row in maintenance_reality_register):
        rows.append(
            {
                "cost_driver": "downtime and failure cost",
                "physical_dependency": "maintenance maturity and critical-system reliability",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
    return rows


def build_capital_logic_register(
    *,
    asset_family_research_profile: dict[str, Any],
    regulatory_constraint_register: list[dict[str, Any]],
    finance_physics_dependency_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    rows: list[dict[str, Any]] = []
    for row in finance_physics_dependency_register[:3]:
        rows.append(
            {
                "capital_logic": text(row.get("financial_assumption")),
                "current_admissibility": "validate_first",
                "why": text(row.get("risk_if_wrong")),
                "minimum_evidence_before_capex": list(row.get("evidence_needed", []) or []),
            }
        )
    if regulatory_constraint_register:
        rows.append(
            {
                "capital_logic": "regulatory or permit pressure may constrain redesign sequencing",
                "current_admissibility": "validate_first",
                "why": "Regulatory context can shape which physical systems or redesign paths are feasible before capital is sized.",
                "minimum_evidence_before_capex": [
                    "filing basis or permit context",
                    "affected system boundary",
                    "physical dependency evidence",
                ],
            }
        )
    return rows


def build_financial_exposure_type_register(
    *,
    asset_family_research_profile: dict[str, Any],
    finance_physics_dependency_register: list[dict[str, Any]],
    invalid_comparison_risk_register: list[dict[str, Any]],
    comparison_not_yet_valid_register: list[dict[str, Any]],
    regulatory_constraint_register: list[dict[str, Any]],
    structural_correlation_graph: list[dict[str, Any]],
    maintenance_reality_register: list[dict[str, Any]],
    measurement_strategy_register: list[dict[str, Any]],
    hardware_minimality_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    asset_family = text(asset_family_research_profile.get("asset_family"))
    rows: list[dict[str, Any]] = []

    for row in list(finance_physics_dependency_register or [])[:2]:
        rows.append(
            _exposure(
                exposure_type="CAPEX_misallocated",
                trigger=text(row.get("financial_assumption")),
                why_it_matters=text(row.get("risk_if_wrong")),
                evidence_needed=list(row.get("evidence_needed", []) or []),
                tad_consequence="DO_NOT_INVEST_YET until the physical dependency is locally bounded.",
            )
        )

    if invalid_comparison_risk_register or comparison_not_yet_valid_register:
        evidence_needed = []
        if comparison_not_yet_valid_register:
            evidence_needed = list((comparison_not_yet_valid_register[0] or {}).get("required_before_comparison", []) or [])
        elif invalid_comparison_risk_register:
            evidence_needed = list((invalid_comparison_risk_register[0] or {}).get("required_normalization", []) or [])
        rows.append(
            _exposure(
                exposure_type="wrong_peer_valuation",
                trigger="comparison not yet valid",
                why_it_matters="Underwriting or retrofit logic can be anchored to the wrong denominator or wrong peer family.",
                evidence_needed=evidence_needed,
                tad_consequence="BUILD_FAIR_PEER_SET before making superiority, underwriting or transferable-ROI claims.",
            )
        )

    if asset_family in {"logistics_warehouse", "cold_chain", "utility_heavy_site", "industrial_manufacturing", "infrastructure_node"}:
        if any("demand tariff" in text(row.get("correlation")).lower() or "tariff" in text(row.get("correlation")).lower() for row in structural_correlation_graph):
            rows.append(
                _exposure(
                    exposure_type="tariff_exposure_hidden",
                    trigger="tariff-linked structural correlation detected",
                    why_it_matters="The visible cost story may be driven by tariff structure rather than generic energy inefficiency.",
                    evidence_needed=["utility bills", "tariff structure", "interval demand profile"],
                    tad_consequence="VALIDATE_TARIFF_EXPOSURE before efficiency-first CAPEX framing.",
                )
            )
        if asset_family in {"logistics_warehouse", "cold_chain"}:
            rows.append(
                _exposure(
                    exposure_type="demand_charge_exposure",
                    trigger="warehouse/cold-chain logistics with charging or temperature-duty uncertainty",
                    why_it_matters="Demand peaks can dominate cost even when annual consumption looks ordinary.",
                    evidence_needed=["utility bills with demand charges", "charging schedule", "MHE inventory"],
                    tad_consequence="VALIDATE_TARIFF_EXPOSURE before generic retrofit underwriting.",
                )
            )

    if asset_family in {"commercial_building", "logistics_warehouse", "cold_chain"}:
        rows.append(
            _exposure(
                exposure_type="operational_savings_not_capturable",
                trigger="control-boundary or payer/operator mismatch remains unresolved",
                why_it_matters="Physical savings may exist while value capture leaks across lease, meter, or operator boundaries.",
                evidence_needed=["lease responsibility matrix", "metering boundary", "utility payer evidence"],
                tad_consequence="VALIDATE_CONTROL_BOUNDARY before owner-side ROI logic.",
            )
        )
        rows.append(
            _exposure(
                exposure_type="tenant_operator_value_leakage",
                trigger="operator controls dominant drivers while another party pays utility or CAPEX",
                why_it_matters="The business can fund the right technical action and still fail to capture the value.",
                evidence_needed=["lease responsibility matrix", "operator control evidence", "billing responsibility map"],
                tad_consequence="REDESIGN_HYPOTHESIS around boundary and capture before retrofit sizing.",
            )
        )

    if maintenance_reality_register:
        rows.append(
            _exposure(
                exposure_type="maintenance_downtime_exposure",
                trigger="maintenance reality or proof gaps remain material",
                why_it_matters="The dominant business loss may be downtime, scrap or failure cost rather than direct utility savings.",
                evidence_needed=["maintenance logs", "downtime records", "work orders", "critical-spares evidence"],
                tad_consequence="VALIDATE_MAINTENANCE_REALITY before utility-first capital prioritization.",
            )
        )

    if regulatory_constraint_register:
        rows.append(
            _exposure(
                exposure_type="compliance_exposure_misunderstood",
                trigger="regulatory or permit pressure present",
                why_it_matters="Compliance pressure can be mistaken for a straightforward efficiency case when the physical and economic boundary is different.",
                evidence_needed=["filing basis or permit context", "affected system boundary", "control/capture evidence"],
                tad_consequence="REQUEST_MINIMUM_EVIDENCE before converting compliance burden into retrofit ROI logic.",
            )
        )

    if measurement_strategy_register:
        rows.append(
            _exposure(
                exposure_type="over_modeling_cost",
                trigger="decision logic still depends on first-order hypothesis discrimination",
                why_it_matters="A digital twin or heavy model can precisely model the wrong system if the dominant driver is still unbounded.",
                evidence_needed=["minimum discriminating evidence from measurement strategy"],
                tad_consequence="DO_NOT_MODEL_YET until the dominant variable is identified.",
            )
        )
    if hardware_minimality_register:
        rows.append(
            _exposure(
                exposure_type="under_instrumentation_risk",
                trigger="cheap evidence routes may fail to discriminate a material hypothesis",
                why_it_matters="The framework can remain blind if it never escalates beyond document-level evidence where the case needs targeted measurement.",
                evidence_needed=["measurement strategy", "temporary study trigger", "hardware escalation path"],
                tad_consequence="REQUEST_MINIMUM_EVIDENCE first, then escalate narrowly if needed.",
            )
        )
        rows.append(
            _exposure(
                exposure_type="wrong_retrofit_sequencing",
                trigger="measurement and comparison gates still unresolved",
                why_it_matters="Retrofit capital can sequence around the visible symptom instead of the dominant driver.",
                evidence_needed=["peer requirements", "minimum measurement path", "claim impact map"],
                tad_consequence="DO_NOT_INVEST_YET until comparison, boundary and driver discrimination gates pass.",
            )
        )

    return rows


def build_underwriting_misread_register(
    *,
    financial_exposure_type_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    keep = {"CAPEX_misallocated", "wrong_peer_valuation", "compliance_exposure_misunderstood", "wrong_retrofit_sequencing"}
    return [
        {
            "financial_exposure_type": text(row.get("financial_exposure_type")),
            "trigger": text(row.get("trigger")),
            "why_it_matters": text(row.get("why_it_matters")),
            "tad_consequence": text(row.get("tad_consequence")),
        }
        for row in list(financial_exposure_type_register or [])
        if text(row.get("financial_exposure_type")) in keep
    ]


def build_value_leakage_register(
    *,
    financial_exposure_type_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    keep = {"operational_savings_not_capturable", "tenant_operator_value_leakage", "maintenance_downtime_exposure"}
    return [
        {
            "financial_exposure_type": text(row.get("financial_exposure_type")),
            "trigger": text(row.get("trigger")),
            "why_it_matters": text(row.get("why_it_matters")),
            "evidence_needed": list(row.get("evidence_needed", []) or []),
        }
        for row in list(financial_exposure_type_register or [])
        if text(row.get("financial_exposure_type")) in keep
    ]
