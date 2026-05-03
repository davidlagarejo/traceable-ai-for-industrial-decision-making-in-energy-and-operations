"""Adapter for motor_013 — Inference Case Activation Engine.

Takes the facility_prior from motor_012 and activates inference cases from
the operational truth framework domain library.

Each latent case is evaluated against facility_prior triggers. Only cases
with satisfied applicability conditions are activated as Inference Cases.

Activation does NOT equate to confirmation or diagnosis. An activated case
means: "this warrants structured investigation and formal validation."

Domain library covers: revenue stability, leverage structure, regulatory compliance,
operational volatility, capital risk, market positioning, and tenant concentration.

Universal library: works for any asset, sector, or jurisdiction.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


# ── Universal Latent Case Domain Library — Operational Truth Framework ─────────
# 13 cases covering financial, operational, regulatory, and market dimensions.
# Each case has:
#   - conditional_statement_template: with {placeholders} filled from facility_prior
#   - trigger_fields: list of dotted paths checked for non-null values
#   - trigger_keywords: fallback text search in prior
#   - applies_to_sectors: ["*"] for universal, specific list otherwise
#   - validation_requirement_template: with {placeholders}

_LATENT_CASE_LIBRARY = [
    {
        "case_id": "LC-ASSET-01",
        "case_name": "Asset Technical Insufficiency and Scope Mismatch",
        "claim_family": "conflict",
        "_asset_readiness_trigger": [
            "issuer_context_only",
            "location_only",
            "asset_context_insufficient",
            "asset_context_minimal",
        ],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "{asset_name} is currently being read as an asset-scoped case, but the physical and "
            "operational substrate remains underpopulated. Current readiness is {asset_context_readiness}. "
            "Missing clusters include: {missing_observable_clusters}. "
            "Until the asset identity, scale, operating regime, fuel context, and system clues are better established, "
            "issuer-level context cannot be allowed to compensate for the missing technical substrate. "
            "This is a blocking limitation on any normal TDIR reading."
        ),
        "inference_logic": (
            "When an asset-scoped case is dominated by issuer context while physical observables remain sparse, "
            "the correct epistemic action is degradation of report identity and elevation of asset clarification work. "
            "This is a framework-protective conflict, not a cosmetic warning."
        ),
        "dependency_assumptions_template": [
            "Address or target identity is declared, but technical clusters remain materially incomplete.",
            "Issuer-level context may still be useful for finance and governance, but not for physical closure.",
            "A normal technical report is not admissible until core asset observables are populated.",
        ],
        "validation_requirement_template": (
            "Close the remaining asset-context gaps: {missing_cluster_validation_path}. "
            "If those cannot be established, degrade the deliverable and treat the case as an asset-context insufficiency brief."
        ),
        "base_support_traces_template": [
            "AssetIdentity.asset_context_readiness",
            "AssetIdentity.missing_observable_clusters",
        ],
    },
    # ── FINANCIAL ──────────────────────────────────────────────────────────────
    {
        "case_id": "LC-FIN-01",
        "case_name": "Revenue Stability and Income Quality",
        "claim_family": "plausible_hypothesis",
        "trigger_fields": ["SectorArchetype.revenues_annual_usd"],
        "trigger_keywords": ["revenue", "revenues_annual"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "Given that {asset_name} has reported annual revenues of approximately "
            "{revenues_usd} ({data_source}), the income quality — specifically the "
            "proportion of stable contractual revenue versus cyclical or discretionary revenue "
            "streams — cannot be confirmed from public data alone. "
            "Multi-stream revenue assets may present a blended figure that overstates stability "
            "if one stream is structurally more volatile. "
            "It is plausible that current revenue represents a near-ceiling for this asset mix "
            "absent major expansion events."
        ),
        "inference_logic": (
            "Assets with mixed revenue streams (contractual lease income + discretionary/cyclical income) "
            "tend to exhibit higher revenue volatility than the headline figure implies. "
            "Income quality assessment requires segment-level disclosure."
        ),
        "dependency_assumptions_template": [
            "Revenue figure is the reported consolidated figure for the owning entity, not asset-specific.",
            "Segment breakdown of revenue streams requires detailed financial disclosure.",
            "Cyclical revenue components (if any) are subject to macroeconomic and competitive conditions.",
        ],
        "validation_requirement_template": (
            "Obtain {asset_name}-specific segment revenue breakdown. "
            "Identify contractual vs. discretionary revenue proportions. "
            "Review revenue trend over 5 years to assess stability ceiling."
        ),
        "base_support_traces_template": [
            "SectorArchetype.revenues_annual_usd",
            "facility_inputs.input_04",
            "{data_source}",
        ],
    },
    {
        "case_id": "LC-FIN-02",
        "case_name": "Leverage Structure and Debt Scope Ambiguity",
        "claim_family": "conflict",
        "trigger_fields": ["SectorArchetype.total_debt_usd"],
        "trigger_keywords": ["total_debt", "leverage", "debt"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "The reported debt figure for {asset_name} is {debt_usd} ({data_source}). "
            "Where the ownership structure involves holding entities, JV structures, or "
            "complex financing arrangements, the reported figure may understate true consolidated "
            "leverage. Until the full debt scope is confirmed, any leverage-dependent analysis "
            "carries structural uncertainty exceeding the materiality threshold for "
            "epistemic advancement on debt-sensitive decisions."
        ),
        "inference_logic": (
            "Complex ownership structures (REITs, holding companies, JVs) frequently structure "
            "property-level debt in unconsolidated entities. Reported figures may reflect "
            "only one layer of a multi-tiered capital structure. "
            "Verification requires full financial statement review including footnotes."
        ),
        "dependency_assumptions_template": [
            "Reported debt figure reflects the declared financial data source.",
            "Ownership structure complexity determines likelihood of off-balance-sheet obligations.",
            "Asset-specific debt is embedded within entity-level reported figures.",
        ],
        "validation_requirement_template": (
            "Cross-reference full financial statements, footnotes, and any mortgage schedule. "
            "Review JV debt disclosures and off-balance-sheet items. "
            "Obtain {asset_name}-specific property loan details if available."
        ),
        "base_support_traces_template": [
            "SectorArchetype.total_debt_usd",
            "{data_source}",
        ],
    },
    {
        "case_id": "LC-FIN-03",
        "case_name": "Liquidity Position and Financing Readiness",
        "claim_family": "plausible_hypothesis",
        "trigger_fields": ["SectorArchetype.total_assets_usd"],
        "trigger_keywords": ["total_assets", "liquidity", "financing"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "{asset_name} is held by an entity with reported total assets of {assets_usd}. "
            "Liquidity position and financing readiness — including available credit facilities, "
            "cash on hand, and near-term debt obligations — cannot be confirmed from "
            "high-level balance sheet figures alone. "
            "Capital availability directly affects the entity's capacity to execute CapEx programs, "
            "respond to regulatory requirements, and service debt through market cycles."
        ),
        "inference_logic": (
            "Total assets as a headline figure does not reveal liquidity profile. "
            "An asset-heavy entity may carry constrained liquidity if assets are illiquid real estate "
            "or operating plant. Financing readiness must be assessed against near-term obligations."
        ),
        "dependency_assumptions_template": [
            "Total assets figure is from the declared financial data source.",
            "Liquidity profile (cash, credit facilities) requires detailed balance sheet review.",
            "Near-term debt maturities are not confirmed from public high-level data.",
        ],
        "validation_requirement_template": (
            "Obtain detailed balance sheet including current assets, cash, and credit facilities. "
            "Review debt maturity schedule. "
            "Assess financing capacity relative to planned CapEx and regulatory obligations."
        ),
        "base_support_traces_template": [
            "SectorArchetype.total_assets_usd",
            "{data_source}",
        ],
    },
    # ── OPERATIONAL ────────────────────────────────────────────────────────────
    {
        "case_id": "LC-OPS-01",
        "case_name": "Concentration Risk — Counterparty or Customer",
        "claim_family": "tension",
        "trigger_fields": ["SectorArchetype.anchor_tenant", "SectorArchetype.customer_concentration"],
        "trigger_keywords": ["anchor_tenant", "concentration", "customer_concentration"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "Counterparty concentration at {asset_name} represents a material tension. "
            "{concentration_description} "
            "A single counterparty representing this level of concentration creates a binary "
            "revenue event: retention preserves current baseline; departure creates a gap "
            "that cannot be replaced quickly without significant investment or concession. "
            "This concentration is further amplified by any portfolio rationalization trends "
            "in the counterparty's sector."
        ),
        "inference_logic": (
            "Operational assessment standards flag single counterparty concentration above 10-20% "
            "as a binary risk requiring term certainty before any leverage-dependent decision "
            "can be advanced. "
            "Concentration risk is structural and cannot be diversified at the asset level."
        ),
        "dependency_assumptions_template": [
            "Concentration figure sourced from facility inputs; not independently verified.",
            "Counterparty's strategic posture is inferred from sector patterns, not asset-specific confirmation.",
            "Subleasing or subletting activity not confirmed or denied from public sources.",
        ],
        "validation_requirement_template": (
            "Obtain counterparty contract expiry date, options, and renewal terms. "
            "Review any subleasing or subletting activity. "
            "Confirm counterparty's current operational plans for this location."
        ),
        "base_support_traces_template": [
            "SectorArchetype.anchor_tenant",
            "SectorArchetype.anchor_tenant_sqft",
            "facility_inputs.input_04",
        ],
    },
    {
        "case_id": "LC-OPS-02",
        "case_name": "Asset Age and Capital Expenditure Liability",
        "claim_family": "plausible_hypothesis",
        "trigger_fields": ["Facility.year_built", "Facility.years_old"],
        "trigger_keywords": ["year_built", "years_old", "CapEx", "renovation"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "At {years_old} years of operation (built {year_built}), {asset_name} carries "
            "structural CapEx obligations beyond any disclosed maintenance budgets. "
            "Legacy system interfaces with modern infrastructure, aging components, "
            "and deferred maintenance represent long-tail capital requirements. "
            "Disclosed CapEx reserves are plausible but cannot be independently confirmed "
            "as sufficient against a full-scope 10-year capital plan."
        ),
        "inference_logic": (
            "Older assets with renovation histories face structurally higher CapEx per unit area "
            "than modern equivalents due to: (a) custom-specification component replacements, "
            "(b) regulatory approval lead times for constrained assets, and "
            "(c) integration complexity between legacy structural systems and modern MEP."
        ),
        "dependency_assumptions_template": [
            "Renovation scope from public/operator disclosures; completeness not independently verified.",
            "Aging system component status derived from declared retrofit periods; granularity not specified.",
            "CapEx reserve adequacy from disclosed figures; independent verification not available.",
        ],
        "validation_requirement_template": (
            "Obtain capital expenditure history (5 years) from financial statements. "
            "Commission independent Property Condition Assessment (PCA). "
            "Review component replacement schedule for major systems."
        ),
        "base_support_traces_template": [
            "Facility.year_built",
            "Facility.major_renovations",
            "SystemAsset",
        ],
    },
    {
        "case_id": "LC-OPS-03",
        "case_name": "Operational Complexity and Multi-Function Interdependency",
        "claim_family": "plausible_hypothesis",
        "trigger_fields": [],
        "trigger_keywords": ["use_mix", "multi_use", "mixed_use"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "{asset_name} operates with a mixed-use profile: {use_mix_description}. "
            "Multi-function facilities face operational interdependency risks: "
            "system schedules, energy loads, regulatory applicability, and staffing "
            "requirements differ across use types. "
            "Optimizing one function may create adverse conditions for another, "
            "and service continuity for one function constrains the operational "
            "flexibility available to others."
        ),
        "inference_logic": (
            "Mixed-use facilities have non-linear operational complexity. Each additional use "
            "introduces a new set of operational requirements (schedules, safety codes, "
            "staffing, utility contracts) that must be balanced. "
            "This is especially relevant for energy management and capital planning."
        ),
        "dependency_assumptions_template": [
            "Use mix and approximate proportions sourced from facility inputs.",
            "Regulatory applicability per use type not individually confirmed.",
            "Energy metering segregation between uses not confirmed.",
        ],
        "validation_requirement_template": (
            "Verify operating schedules, metering segregation, and regulatory applicability per use. "
            "Assess operational staffing model and cross-function service level dependencies. "
            "Confirm energy allocation methodology between uses."
        ),
        "base_support_traces_template": [
            "SectorArchetype.use_mix",
            "facility_inputs.input_04",
            "OperationalPractice",
        ],
    },
    {
        "case_id": "LC-OPS-04",
        "case_name": "Critical System Reliability and Continuity Risk",
        "claim_family": "plausible_hypothesis",
        "trigger_fields": [],
        "trigger_keywords": ["known_systems", "HVAC", "BMS", "elevators", "power", "cooling"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "{asset_name} has declared {systems_count} known system(s): {systems_list}. "
            "Critical system reliability cannot be confirmed from public declarations alone. "
            "For facilities with high-criticality systems (BMS integration, cooling plant, "
            "power distribution), failure or degradation events create operational disruption "
            "that may exceed the direct cost of the system failure itself. "
            "Integration depth between systems introduces interdependency risk."
        ),
        "inference_logic": (
            "Declared systems provide a structural hypothesis about the facility's "
            "operational resilience, but performance, reliability, and redundancy "
            "cannot be verified from operator declarations. "
            "System age and integration complexity are key drivers of continuity risk."
        ),
        "dependency_assumptions_template": [
            "System declarations sourced from facility inputs; not independently verified.",
            "System performance, redundancy, and maintenance status not confirmed from public data.",
            "Integration between systems (BMS, HVAC, power) not independently assessed.",
        ],
        "validation_requirement_template": (
            "Obtain system maintenance records and reliability history. "
            "Assess redundancy and failover provisions for critical systems. "
            "Review BMS integration depth and historian availability."
        ),
        "base_support_traces_template": [
            "SystemAsset",
            "facility_inputs.input_09",
            "EnergyContext",
        ],
    },
    {
        "case_id": "LC-OPS-05",
        "case_name": "Data and Evidence Coverage Gap",
        "claim_family": "evidence_gap",
        "trigger_fields": [],
        "trigger_keywords": [],
        "applies_to_sectors": ["*"],
        # Always activates — every asset has some gaps
        "_always_activate": True,
        "conditional_statement_template": (
            "The analytical picture for {asset_name} contains evidence coverage gaps "
            "that limit epistemic advancement. {coverage_gap_description} "
            "These gaps are structural to Decision-grade public data analysis: "
            "they do not represent analytical failures but rather the boundaries of "
            "what can be determined without direct field access or privileged disclosure."
        ),
        "inference_logic": (
            "Every asset assessed at Decision-grade (Phase 1 public data) contains "
            "coverage gaps. The gaps define the validation agenda. "
            "Acknowledging them explicitly is an epistemic requirement, not a limitation."
        ),
        "dependency_assumptions_template": [
            "Coverage gaps identified from data enrichment and standard sector unknowns.",
            "Gap severity varies: some are blockers; others are reducers of confidence only.",
        ],
        "validation_requirement_template": (
            "Address each coverage gap through targeted data acquisition. "
            "Prioritize gaps linked to high-urgency inference cases. "
            "Document resolution status as evidence is obtained."
        ),
        "base_support_traces_template": [
            "uncertainty_markers",
            "facility_prior.coverage_gaps",
        ],
    },
    # ── REGULATORY ─────────────────────────────────────────────────────────────
    {
        "case_id": "LC-REG-01",
        "case_name": "Regulatory Compliance Exposure",
        "claim_family": "tension",
        "trigger_fields": ["RegulatoryContext.regulatory_flags"],
        "trigger_keywords": ["regulatory_flags", "regulation", "compliance", "law"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "{asset_name} operates under {primary_regulation} and is subject to "
            "applicable regulatory flags: {regulatory_flags_description}. "
            "Current compliance position cannot be confirmed from public data alone. "
            "At the scale of {gfa_description}, even a small per-unit non-compliance "
            "generates material exposure under applicable penalty structures. "
            "Non-compliance status could affect operational continuity, transaction structuring, "
            "and institutional positioning."
        ),
        "inference_logic": (
            "Large-scale assets face amplified regulatory exposure because penalties typically "
            "scale with floor area or emissions volume. "
            "Certification vintage (LEED, ISO 50001, etc.) does not guarantee current compliance "
            "under updated regulatory frameworks. "
            "Compliance determination requires current-period official reporting."
        ),
        "dependency_assumptions_template": [
            "Regulatory framework assignment based on jurisdiction codes.",
            "Compliance status requires official reporting; not determinable from public data.",
            "Penalty rate and threshold from publicly available regulatory text.",
        ],
        "validation_requirement_template": (
            "Request current compliance report under {primary_regulation}. "
            "Obtain actual measured performance data for regulated parameters. "
            "Calculate current-period compliance gap if available."
        ),
        "base_support_traces_template": [
            "RegulatoryContext",
            "EnergyContext",
            "Jurisdiction",
        ],
    },
    {
        "case_id": "LC-REG-02",
        "case_name": "Historical Certification vs. Current Compliance Gap",
        "claim_family": "tension",
        "trigger_fields": ["Facility.certifications"],
        "trigger_keywords": ["certification", "LEED", "ISO", "certified", "certifications"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "Declared certification(s) for {asset_name} ({certifications_list}) were achieved "
            "in prior periods. Current regulatory frameworks ({primary_regulation}) operate on "
            "updated methodologies that may differ materially from the certification scoring basis. "
            "Historical certification status does not confirm current compliance. "
            "The gap between certification-era performance and current regulatory requirements "
            "represents a plausible and material compliance risk."
        ),
        "inference_logic": (
            "Buildings certified under prior-era standards (pre-2015 LEED, early ISO 50001 cycles) "
            "face compliance gaps under updated frameworks because: "
            "(a) grid emissions factors change over time, affecting carbon calculations; "
            "(b) certification scope may not cover all regulated uses; "
            "(c) newer regulatory thresholds are typically stricter than certification requirements."
        ),
        "dependency_assumptions_template": [
            "Certification dates sourced from declared renovation history.",
            "Current compliance period methodology may differ from certification scoring.",
            "Certification scope coverage not independently verified.",
        ],
        "validation_requirement_template": (
            "Obtain current compliance report for the applicable regulatory period. "
            "Compare certification-era performance data with current regulatory thresholds. "
            "Confirm whether certification scope covers all regulated asset uses."
        ),
        "base_support_traces_template": [
            "Facility.certifications",
            "EnergyContext.certifications_declared",
            "RegulatoryContext",
        ],
    },
    # ── MARKET ─────────────────────────────────────────────────────────────────
    {
        "case_id": "LC-MKT-01",
        "case_name": "Market Positioning and Competitive Displacement Risk",
        "claim_family": "plausible_hypothesis",
        "trigger_fields": ["Facility.primary_classification"],
        "trigger_keywords": ["Class A", "trophy", "premium", "flagship", "Class-A"],
        "applies_to_sectors": ["commercial_real_estate", "hospitality", "retail", "data_center"],
        "conditional_statement_template": (
            "{asset_name} occupies a {primary_classification} market position in {jurisdiction}. "
            "Premium or Class A positioning supports above-market pricing power but introduces "
            "competitive displacement risk: new supply entering the submarket at lower effective "
            "cost, or a shift in occupier preferences toward newer or differently-located assets, "
            "may erode the positioning premium without structural asset changes. "
            "The durability of the premium must be assessed against current submarket supply pipeline."
        ),
        "inference_logic": (
            "Premium-positioned assets maintain higher relative occupancy during downturns "
            "(flight-to-quality effect) but face rent ceiling pressure when new Class A supply "
            "enters at lower effective rents. "
            "Market positioning premium is not permanent — it requires ongoing investment "
            "in amenity and service quality to sustain."
        ),
        "dependency_assumptions_template": [
            "Current occupancy figure not confirmed from public sources as of analysis date.",
            "Rent premium over market average not independently quantified.",
            "Submarket supply pipeline based on public market data.",
        ],
        "validation_requirement_template": (
            "Obtain current occupancy rate and rent roll from financial filings or market data. "
            "Compare effective rent to current submarket benchmark. "
            "Review lease expiry schedule and weighted average lease term."
        ),
        "base_support_traces_template": [
            "Facility.primary_classification",
            "SectorArchetype",
            "Jurisdiction",
        ],
    },
    {
        "case_id": "LC-MKT-02",
        "case_name": "Energy Transition and Carbon Cost Exposure",
        "claim_family": "tension",
        "trigger_fields": ["SectorArchetype.primary_fuel", "SectorArchetype.secondary_fuel"],
        "trigger_keywords": ["primary_fuel", "secondary_fuel", "natural_gas", "carbon", "emissions", "fuel"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "{asset_name} uses {primary_fuel} as primary energy source "
            "and {secondary_fuel} as secondary source. "
            "The accelerating energy transition creates a structural tension: "
            "fossil fuel-dependent assets face increasing carbon cost exposure through "
            "regulatory carbon pricing, stranded asset risk from energy efficiency mandates, "
            "and potential occupier/investor preference shifts. "
            "Transition investment requirements are not fully determinable without current "
            "metered performance data and a technology transition pathway study."
        ),
        "inference_logic": (
            "Assets with significant fossil fuel dependency face compounding transition risk: "
            "near-term regulatory exposure (carbon pricing, building performance standards) "
            "and medium-term capital intensity of fuel switching. "
            "The cost trajectory of natural gas vs. electrification is jurisdiction-dependent "
            "but the directional trend toward electrification is consistent globally."
        ),
        "dependency_assumptions_template": [
            "Fuel type from facility inputs; consumption quantities not confirmed.",
            "Carbon cost exposure calculation requires actual consumption data.",
            "Technology transition pathway requires site-specific engineering assessment.",
        ],
        "validation_requirement_template": (
            "Obtain actual fuel consumption data by type. "
            "Calculate carbon footprint under applicable reporting methodology. "
            "Commission technology transition pathway study with cost modeling."
        ),
        "base_support_traces_template": [
            "SectorArchetype.primary_fuel",
            "SectorArchetype.secondary_fuel",
            "EnergyContext",
            "RegulatoryContext",
        ],
    },
    {
        "case_id": "LC-MKT-03",
        "case_name": "Governance, Disclosure Adequacy",
        "claim_family": "plausible_hypothesis",
        "trigger_fields": ["SectorArchetype.owner_ticker", "SectorArchetype.owner_cik"],
        "trigger_keywords": ["owner_ticker", "owner_cik", "SEC", "EDGAR", "listed", "publicly_traded"],
        "applies_to_sectors": ["*"],
        "conditional_statement_template": (
            "{asset_name} is owned or operated by a publicly-disclosed entity "
            "({owner_entity}). Governance quality and disclosure adequacy affect "
            "the reliability of all public data used in this analysis. "
            "Public companies face mandatory disclosure requirements, but "
            "asset-level granularity is typically unavailable in consolidated filings. "
            "Governance risk — including management alignment, ESG disclosure quality, "
            "and forward commitment to capital programs — cannot be determined "
            "from public filings alone."
        ),
        "inference_logic": (
            "Publicly-disclosed entities are subject to regulatory disclosure requirements, "
            "providing a floor of data reliability. However, asset-level transparency within "
            "a portfolio entity is typically limited to material disclosures. "
            "Governance quality must be assessed at both entity and asset management levels."
        ),
        "dependency_assumptions_template": [
            "Owner/operator disclosure status from facility inputs.",
            "Asset-level governance quality not directly assessable from entity-level filings.",
            "ESG and sustainability governance not independently rated.",
        ],
        "validation_requirement_template": (
            "Review financial filings for material asset disclosures, sustainability reporting, "
            "and management commentary on the specific asset. "
            "Assess ESG/governance rating if available for the entity."
        ),
        "base_support_traces_template": [
            "SectorArchetype.owner_ticker",
            "SectorArchetype.owner_cik",
            "SectorArchetype.company_name_sec",
        ],
    },
]


def _canonical_asset_context_summary(facility_prior: dict[str, Any]) -> dict[str, Any]:
    summary = facility_prior.get("canonical_asset_context_summary", {})
    if isinstance(summary, dict):
        state = str(summary.get("canonical_asset_context_state", "")).strip()
        missing = [str(item).strip() for item in summary.get("missing_clusters", []) if str(item).strip()]
        supported = [str(item).strip() for item in summary.get("supported_clusters", []) if str(item).strip()]
        if state or missing or supported:
            return {
                "canonical_asset_context_state": state or str(facility_prior.get("asset_context_readiness", "unknown")).strip(),
                "missing_clusters": missing,
                "supported_clusters": supported,
                "screening_supported": bool(summary.get("screening_supported", False)),
            }

    asset_identity = facility_prior.get("entities", {}).get("AssetIdentity", {})
    missing = asset_identity.get("missing_observable_clusters", []) or facility_prior.get("missing_physical_observables_register", [])
    return {
        "canonical_asset_context_state": str(
            asset_identity.get("asset_context_readiness", facility_prior.get("asset_context_readiness", "unknown"))
        ).strip(),
        "missing_clusters": [str(item).strip() for item in missing if str(item).strip()],
        "supported_clusters": [],
        "screening_supported": False,
    }


def _missing_cluster_validation_path(missing_clusters: list[str], target_type: str) -> str:
    target_type = str(target_type or "").strip().lower()
    family = "building"
    if target_type in {
        "industrial_plant",
        "manufacturing_facility",
        "food_processing_facility",
        "cold_chain_facility",
    }:
        family = "manufacturing"
    elif target_type == "warehouse_distribution":
        family = "logistics"

    cluster_actions: dict[str, str] = {
        "identity_cluster": "confirm the target asset identity record",
        "geometry_size_cluster": (
            "confirm verified site / building area and process footprint"
            if family == "manufacturing"
            else "confirm verified GFA / building area and bounded scale"
        ),
        "vintage_structure_cluster": "confirm commissioning / year-built basis and major upgrade history",
        "operating_regime_cluster": (
            "confirm throughput, shift schedule, and process-duty profile"
            if family == "manufacturing"
            else "confirm operating schedule and occupancy / use mix"
        ),
        "fuel_energy_cluster": "confirm utility / fuel basis and recent billing records",
        "systems_cluster": (
            "confirm process, utility, and controls system inventory"
            if family == "manufacturing"
            else "confirm HVAC / BMS / central-plant inventory"
        ),
        "boundary_cluster": (
            "confirm operator, owner, and in-scope boundary responsibility"
            if family == "manufacturing"
            else "confirm owner / tenant boundary responsibility"
        ),
        "control_boundary_cluster": (
            "confirm process, metering, and operator control boundary"
            if family == "manufacturing"
            else "confirm tenant metering, lease responsibility, and control boundary"
        ),
        "tenant_control_cluster": "confirm tenant metering, lease responsibility, and control boundary",
        "regulatory_cluster": "confirm current regulatory applicability and filing basis",
        "financial_boundary_cluster": "confirm the in-scope financial boundary for asset-level economics",
    }
    actions = [cluster_actions[cluster] for cluster in missing_clusters if cluster in cluster_actions]
    if not actions:
        return "confirm the remaining bounded asset record, operating profile, fuel basis, and systems evidence"
    if len(actions) == 1:
        return actions[0]
    return ", ".join(actions[:-1]) + f", and {actions[-1]}"


def _extract_template_vars(facility_prior: dict) -> dict:
    """Extract template variable values from facility_prior for placeholder filling."""
    entities = facility_prior.get("entities", {})
    facility = entities.get("Facility", {})
    sector = entities.get("SectorArchetype", {})
    reg_ctx = entities.get("RegulatoryContext", {})
    bench = entities.get("BenchmarkContext", {})
    energy_ctx = entities.get("EnergyContext", {})
    asset_identity = entities.get("AssetIdentity", {})

    asset_name = facility_prior.get("asset_name") or facility_prior.get("case_title") or "the facility"
    revenues = sector.get("revenues_annual_usd")
    debt = sector.get("total_debt_usd")
    assets_usd = sector.get("total_assets_usd")
    anchor = sector.get("anchor_tenant", "")
    anchor_sqft = sector.get("anchor_tenant_sqft", 0)
    years_old = facility.get("years_old", "")
    year_built = facility.get("year_built", "")
    primary_classification = facility.get("primary_classification", "")
    jurisdiction_codes = facility.get("jurisdiction", [])
    jurisdiction = ", ".join(jurisdiction_codes) if jurisdiction_codes else "unknown jurisdiction"

    certs = facility.get("certifications", []) or energy_ctx.get("certifications_declared", [])
    use_mix = sector.get("use_mix", {})
    owner_ticker = sector.get("owner_ticker", "")
    owner_cik = sector.get("owner_cik", "")
    company_name = sector.get("company_name_sec", "")
    owner_entity = company_name or owner_ticker or owner_cik or "undisclosed entity"

    primary_fuel = sector.get("primary_fuel", "") or energy_ctx.get("primary_fuel", "") or "unspecified"
    secondary_fuel = sector.get("secondary_fuel", "") or energy_ctx.get("secondary_fuel", "") or "unspecified"

    primary_regulation = reg_ctx.get("primary_regulation", "applicable regulation")
    regulatory_flags = reg_ctx.get("regulatory_flags", [])
    canonical_context = _canonical_asset_context_summary(facility_prior)

    # Derive data_source label
    fin_signals = sector.get("financial_health_signals", {})
    data_source = fin_signals.get("data_source", "financial_enrichment") if fin_signals else "financial_enrichment"

    # System count and list
    sys_hyps = facility_prior.get("system_asset_hypotheses", [])
    systems_count = len(sys_hyps)
    systems_list = ", ".join(s.get("system", "") for s in sys_hyps if s.get("system")) or "no systems declared"

    # Coverage gaps from uncertainty_markers
    um = facility_prior.get("uncertainty_markers", [])
    if um:
        coverage_gap_description = f"{len(um)} uncertainty dimension(s) identified: " + "; ".join(
            m.get("dimension", "").replace("_", " ") for m in um[:3]
        ) + ("..." if len(um) > 3 else ".")
    else:
        coverage_gap_description = "Standard evidence gaps for Decision-grade public data analysis apply."
    missing_clusters = canonical_context.get("missing_clusters", [])
    missing_clusters_desc = ", ".join(missing_clusters) if missing_clusters else "none explicitly registered"
    missing_cluster_validation_path = _missing_cluster_validation_path(
        missing_clusters,
        _derive_target_type(facility_prior),
    )

    # Concentration description
    if anchor and anchor_sqft:
        gfa_sqft = facility.get("GFA_sqft") or 1
        rent_sqft = entities.get("SectorArchetype", {}).get("anchor_tenant_sqft") or anchor_sqft
        office_sqft = gfa_sqft
        pct = round(100 * anchor_sqft / max(office_sqft, 1), 1)
        concentration_description = (
            f"{anchor} occupies approximately {pct}% of rentable area (~{anchor_sqft:,} sqft)."
        )
    elif sector.get("customer_concentration"):
        pct = float(sector.get("customer_concentration") or 0) * 100
        concentration_description = f"Customer concentration at approximately {pct:.0f}% of revenue."
    else:
        concentration_description = "Counterparty concentration signals present in facility data."

    # Use mix description
    if use_mix:
        use_mix_desc = "; ".join(
            f"{k}: ~{v}%" if v else k for k, v in use_mix.items() if k
        )
    else:
        use_mix_desc = "single-use (details from facility inputs)"

    # GFA description
    gfa_sqft = facility.get("GFA_sqft")
    gfa_m2 = facility.get("GFA_m2")
    if gfa_sqft:
        gfa_description = f"{gfa_sqft:,} sqft"
    elif gfa_m2:
        gfa_description = f"{gfa_m2:,} m2"
    else:
        gfa_description = "area not specified"

    # Regulatory flags description
    if regulatory_flags:
        reg_flags_desc = "; ".join(str(f) for f in regulatory_flags[:3])
        if len(regulatory_flags) > 3:
            reg_flags_desc += f" (+ {len(regulatory_flags)-3} more)"
    else:
        reg_flags_desc = "no specific regulatory flags from available data"

    # Certifications list
    certs_list = ", ".join(str(c) for c in certs if c) if certs else "none declared"

    def _fmt_usd(v) -> str:
        if v is None:
            return "N/A"
        if abs(v) >= 1e9:
            return f"${v/1e9:.2f}B"
        if abs(v) >= 1e6:
            return f"${v/1e6:.1f}M"
        return f"${v:,.0f}"

    return {
        "asset_name": asset_name,
        "revenues_usd": _fmt_usd(revenues),
        "debt_usd": _fmt_usd(debt),
        "assets_usd": _fmt_usd(assets_usd),
        "data_source": data_source,
        "anchor_tenant": anchor,
        "concentration_description": concentration_description,
        "years_old": str(years_old) if years_old else "age not specified",
        "year_built": str(year_built) if year_built else "year not specified",
        "primary_classification": primary_classification or "asset class not specified",
        "jurisdiction": jurisdiction,
        "certifications_list": certs_list,
        "use_mix_description": use_mix_desc,
        "owner_entity": owner_entity,
        "primary_fuel": primary_fuel,
        "secondary_fuel": secondary_fuel,
        "primary_regulation": primary_regulation,
        "regulatory_flags_description": reg_flags_desc,
        "gfa_description": gfa_description,
        "systems_count": str(systems_count),
        "systems_list": systems_list,
        "coverage_gap_description": coverage_gap_description,
        "asset_context_readiness": canonical_context.get("canonical_asset_context_state", "unknown"),
        "missing_observable_clusters": missing_clusters_desc,
        "missing_cluster_validation_path": missing_cluster_validation_path,
    }


def _fill_template(template: str, vars_dict: dict) -> str:
    """Fill template string with values from vars_dict (safe — missing keys kept as-is)."""
    for key, value in vars_dict.items():
        placeholder = "{" + key + "}"
        template = template.replace(placeholder, str(value))
    return template


def _fill_templates(templates: list[str], vars_dict: dict) -> list[str]:
    return [_fill_template(t, vars_dict) for t in templates]


def _check_trigger_satisfaction(case: dict, facility_prior: dict) -> tuple[bool, list[str]]:
    """Check whether a latent case's triggers are satisfied by the facility_prior."""
    if case.get("_asset_readiness_trigger"):
        readiness = _canonical_asset_context_summary(facility_prior).get("canonical_asset_context_state", "")
        if readiness in set(case.get("_asset_readiness_trigger", [])):
            return True, [f"asset_context:{readiness}"]
        return False, []
    # Always-activate cases
    if case.get("_always_activate"):
        return True, ["always_active"]

    entities = facility_prior.get("entities", {})
    tensions = facility_prior.get("operational_tension_hypotheses", [])
    sector = entities.get("SectorArchetype", {})
    facility = entities.get("Facility", {})
    all_text = str(entities) + str(tensions) + str(facility_prior.get("prior_assumptions_pack", []))

    satisfied_terms: list[str] = []

    # Check trigger_fields: dotted paths like "SectorArchetype.revenues_annual_usd"
    for field_path in case.get("trigger_fields", []):
        parts = field_path.split(".")
        obj = entities
        value = None
        if len(parts) == 2:
            entity_obj = entities.get(parts[0], {})
            value = entity_obj.get(parts[1]) if isinstance(entity_obj, dict) else None
        elif len(parts) == 1:
            value = entities.get(parts[0])
        if value is not None and value != "" and value != [] and value != {}:
            satisfied_terms.append(field_path)

    # Check trigger_keywords: text search in serialized prior
    for keyword in case.get("trigger_keywords", []):
        if keyword in all_text:
            satisfied_terms.append(f"keyword:{keyword}")

    # Check sector applicability
    applies_to = case.get("applies_to_sectors", ["*"])
    if "*" not in applies_to:
        current_sector = entities.get("SectorArchetype", {}).get("sector", "")
        sector_match = current_sector in applies_to or any(
            s in current_sector for s in applies_to
        )
        if not sector_match:
            return False, []

    # Case activates if any field OR keyword trigger is satisfied
    field_count = len([t for t in satisfied_terms if not t.startswith("keyword:")])
    keyword_count = len([t for t in satisfied_terms if t.startswith("keyword:")])

    # Need at least one field trigger OR at least two keyword triggers for activation
    activated = field_count >= 1 or keyword_count >= 2

    entities = facility_prior.get("entities", {})
    sector = entities.get("SectorArchetype", {}) if isinstance(entities, dict) else {}
    facility = entities.get("Facility", {}) if isinstance(entities, dict) else {}
    energy = entities.get("EnergyContext", {}) if isinstance(entities, dict) else {}
    case_id = str(case.get("case_id", "")).strip()

    if case_id == "LC-OPS-01":
        anchor = str(sector.get("anchor_tenant", "") or "").strip()
        concentration = sector.get("customer_concentration")
        concentration_present = False
        if isinstance(concentration, (int, float)):
            concentration_present = concentration > 0
        elif str(concentration or "").strip():
            concentration_present = str(concentration).strip() not in {"0", "0.0"}
        if anchor or concentration_present:
            terms: list[str] = []
            if anchor:
                terms.append("field:SectorArchetype.anchor_tenant")
            if concentration_present:
                terms.append("field:SectorArchetype.customer_concentration")
            return True, terms
        return False, []

    if case_id == "LC-REG-02":
        certs = []
        for bucket in [
            facility.get("certifications", []),
            energy.get("certifications_declared", []),
        ]:
            if isinstance(bucket, list):
                certs.extend(str(item).strip() for item in bucket if str(item).strip())
        if certs:
            return True, ["field:Facility.certifications"]
        return False, []

    if case_id == "LC-MKT-02":
        primary_fuel = str(sector.get("primary_fuel", "") or energy.get("primary_fuel", "") or "").strip()
        secondary_fuel = str(sector.get("secondary_fuel", "") or energy.get("secondary_fuel", "") or "").strip()
        if primary_fuel or secondary_fuel:
            terms = []
            if primary_fuel:
                terms.append("field:primary_fuel")
            if secondary_fuel:
                terms.append("field:secondary_fuel")
            return True, terms
        return False, []

    return activated, satisfied_terms


def _admissibility_allows_case(
    case_id: str,
    target_admissibility_state: str,
    subject_gate_passed: bool,
) -> tuple[bool, str]:
    """Prevent company/market-style cases from surfacing before the subject is a bounded asset."""
    if not target_admissibility_state:
        return True, ""
    if subject_gate_passed and target_admissibility_state in {
        "bounded_asset",
        "bounded_asset_with_operable_context",
    }:
        return True, ""
    if case_id in {"LC-ASSET-01", "LC-OPS-05"}:
        return True, ""
    return (
        False,
        f"Suppressed while target_admissibility_state is {target_admissibility_state}; "
        "the case is not yet admissible as a bounded asset.",
    )


def _target_family_allows_case(case_id: str, target_type: str) -> tuple[bool, str]:
    manufacturing_like = {
        "industrial_plant",
        "manufacturing_facility",
        "food_processing_facility",
        "cold_chain_facility",
    }
    if case_id == "LC-OPS-01" and target_type in manufacturing_like:
        return (
            False,
            "Suppressed for manufacturing-family assets because leasing/subletting semantics "
            "are not admissible as the default operational concentration frame.",
        )
    return True, ""


def _apply_target_family_case_overrides(
    activated_case: dict[str, Any],
    target_type: str,
    asset_name: str,
) -> dict[str, Any]:
    building_like = {
        "commercial_building",
        "multifamily_building",
        "warehouse_distribution",
        "hospital",
        "hotel",
        "data_center",
    }
    case_id = str(activated_case.get("case_id", "")).strip()

    if case_id == "LC-OPS-01" and target_type in building_like:
        activated_case = {
            **activated_case,
            "case_name": "Lease Concentration and Control-Boundary Exposure",
            "conditional_statement": (
                f"Lease concentration and control-boundary ambiguity at {asset_name or 'the asset'} "
                "represent a material tension. Where a major tenant, use cluster, or after-hours load concentration "
                "dominates the building, occupancy stability does not automatically translate into owner-capturable "
                "energy upside or retrofit value. If the dominant loads sit behind tenant metering or lease-controlled "
                "boundaries, energy performance may remain visible at the asset while the economic capture remains weak."
            ),
            "inference_logic": (
                "For large commercial buildings, concentration is not only a rent-roll issue. It is also a control-boundary "
                "issue: tenant metering, lease responsibility, and central-plant topology determine whether observed "
                "energy behavior can be acted on by the owner. Screening-grade occupancy signals do not resolve that boundary."
            ),
            "dependency_assumptions": [
                "Major tenant or use concentration may be present but is not independently verified from a current rent roll.",
                "Lease responsibility and submetering basis are not yet confirmed.",
                "After-hours tenant load and central-plant control boundary remain unresolved.",
            ],
            "validation_requirement": (
                "Obtain the current rent roll or major-tenant schedule, tenant metering basis, lease responsibility matrix, "
                "and the central-plant / owner-control boundary for in-scope loads."
            ),
        }
    return activated_case


def _derive_target_type(facility_prior: dict[str, Any]) -> str:
    target_type = str(facility_prior.get("target_type", "")).strip().lower()
    if target_type:
        return target_type
    target_definition = facility_prior.get("target_definition", {})
    if isinstance(target_definition, dict):
        target_type = str(target_definition.get("target_type", "")).strip().lower()
        if target_type:
            return target_type
    entities = facility_prior.get("entities", {})
    asset_identity = entities.get("AssetIdentity", {}) if isinstance(entities, dict) else {}
    if isinstance(asset_identity, dict):
        target_type = str(asset_identity.get("target_type", "")).strip().lower()
        if target_type:
            return target_type
    return ""


class Motor013Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_013"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_012", "motor_011", "motor_007"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        facility_prior = inputs.get("motor_012", {}).get("facility_prior", {})
        subject_gate = inputs.get("motor_007", {})
        target_type = _derive_target_type(facility_prior)
        target_admissibility_state = str(subject_gate.get("target_admissibility_state", "")).strip()
        subject_gate_passed = bool(subject_gate.get("subject_gate_passed", False))
        produced_at = datetime.now(timezone.utc).isoformat()

        # Extract template variables once for all cases
        tpl_vars = _extract_template_vars(facility_prior)

        inference_case_register = []
        activation_log = []

        for latent in _LATENT_CASE_LIBRARY:
            allowed, suppressed_reason = _admissibility_allows_case(
                latent.get("case_id", ""),
                target_admissibility_state,
                subject_gate_passed,
            )
            if not allowed:
                activation_log.append({
                    "case_id": latent["case_id"],
                    "status": "suppressed_by_subject_gate",
                    "reason": suppressed_reason,
                })
                continue
            family_allowed, family_reason = _target_family_allows_case(
                latent.get("case_id", ""),
                target_type,
            )
            if not family_allowed:
                activation_log.append({
                    "case_id": latent["case_id"],
                    "status": "suppressed_by_target_family",
                    "reason": family_reason,
                })
                continue
            satisfied, satisfied_terms = _check_trigger_satisfaction(latent, facility_prior)

            if satisfied:
                # Fill template strings with actual values from facility_prior
                filled_statement = _fill_template(
                    latent["conditional_statement_template"], tpl_vars
                )
                filled_validation = _fill_template(
                    latent["validation_requirement_template"], tpl_vars
                )
                filled_deps = _fill_templates(
                    latent["dependency_assumptions_template"], tpl_vars
                )
                filled_traces = _fill_templates(
                    latent["base_support_traces_template"], tpl_vars
                )
                filled_inference = latent.get("inference_logic", "")

                activated_case = {
                    "case_id": latent["case_id"],
                    "case_name": latent["case_name"],
                    "claim_family": latent["claim_family"],
                    "conditional_statement": filled_statement,
                    "inference_logic": filled_inference,
                    "dependency_assumptions": filled_deps,
                    "validation_requirement": filled_validation,
                    "base_support_traces": filled_traces,
                    "case_status": "activated",
                    "activation_basis": satisfied_terms,
                    "activated_at": produced_at,
                    "facility_prior_id": facility_prior.get("facility_prior_id", ""),
                    "produced_by_motor": "motor_013",
                }
                activated_case = _apply_target_family_case_overrides(
                    activated_case,
                    target_type,
                    tpl_vars.get("asset_name", ""),
                )
                inference_case_register.append(activated_case)
                activation_log.append({
                    "case_id": latent["case_id"],
                    "status": "activated",
                    "satisfied_triggers": satisfied_terms,
                })
            else:
                activation_log.append({
                    "case_id": latent["case_id"],
                    "status": "not_activated",
                    "reason": (
                        f"Trigger fields {latent.get('trigger_fields', [])} and keywords "
                        f"{latent.get('trigger_keywords', [])} not satisfied in facility_prior, "
                        f"or sector {latent.get('applies_to_sectors')} does not match."
                    ),
                })

        by_family: dict[str, list[str]] = {}
        for case in inference_case_register:
            family = case.get("claim_family", "unknown")
            by_family.setdefault(family, []).append(case["case_id"])

        return {
            "inference_case_register": inference_case_register,
            "total_activated": len(inference_case_register),
            "total_latent": len(_LATENT_CASE_LIBRARY),
            "activation_rate": round(len(inference_case_register) / len(_LATENT_CASE_LIBRARY), 2),
            "target_admissibility_state": target_admissibility_state,
            "subject_gate_passed": subject_gate_passed,
            "cases_by_family": by_family,
            "activation_log": activation_log,
            "facility_prior_id": facility_prior.get("facility_prior_id", ""),
            "produced_at": produced_at,
        }
