from __future__ import annotations

from typing import Any

from .schemas import text


def _token_set(*values: Any) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        queue = list(value) if isinstance(value, list) else [value]
        for item in queue:
            raw = text(item).lower()
            if not raw:
                continue
            for token in raw.replace("/", " ").replace("-", " ").split():
                token = token.strip()
                if len(token) >= 4:
                    tokens.add(token)
    return tokens


def _overlap_score(*values: Any) -> int:
    token_sets = [token_set for token_set in (_token_set(value) for value in values) if token_set]
    if len(token_sets) < 2:
        return 0
    running = token_sets[0]
    overlap = 0
    for token_set in token_sets[1:]:
        shared = running.intersection(token_set)
        overlap = max(overlap, len(shared))
    return overlap


def _supporting_correlation_register(
    *,
    contradiction_row: dict[str, Any],
    structural_correlation_graph: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    contradiction_layers = {
        text(layer)
        for layer in list(contradiction_row.get("layers", []) or [])
        if text(layer)
    }
    contradiction_text = " ".join(
        [
            text(contradiction_row.get("contradiction")),
            text(contradiction_row.get("strategic_risk")),
            " ".join(list(contradiction_layers)),
            " ".join(list(contradiction_row.get("evidence_needed", []) or [])),
        ]
    )
    supporting_rows: list[dict[str, Any]] = []
    for corr in list(structural_correlation_graph or []):
        corr_layers = {
            text(layer)
            for layer in list(corr.get("layers_connected", []) or [])
            if text(layer)
        }
        layer_overlap = len(contradiction_layers.intersection(corr_layers))
        text_overlap = _overlap_score(
            contradiction_text,
            text(corr.get("correlation")),
            text(corr.get("strategic_meaning")),
            list(corr.get("evidence_needed", []) or []),
        )
        if not layer_overlap and not text_overlap:
            continue
        supporting_rows.append(
            {
                "correlation_id": text(corr.get("correlation_id")),
                "correlation": text(corr.get("correlation")),
                "strategic_meaning": text(corr.get("strategic_meaning")),
                "evidence_needed": list(corr.get("evidence_needed", []) or []),
                "evidence_state": text(corr.get("evidence_state")),
                "layer_overlap_count": layer_overlap,
                "text_overlap_score": text_overlap,
                "support_score": layer_overlap * 3 + text_overlap,
            }
        )
    supporting_rows.sort(
        key=lambda row: (
            -int(row.get("support_score", 0) or 0),
            -int(row.get("layer_overlap_count", 0) or 0),
            text(row.get("correlation_id")),
        )
    )
    return supporting_rows[:3]


def _allows_conditional_archetypal_intelligence(
    asset_family_research_profile: dict[str, Any],
) -> bool:
    route_state = text(asset_family_research_profile.get("route_state"))
    asset_family = text(asset_family_research_profile.get("asset_family"))
    return route_state == "operational_asset_candidate" or (
        route_state == "target_not_yet_operationally_bounded"
        and bool(asset_family)
        and asset_family != "generic_operational_asset"
    )


def build_cross_layer_congruence_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    fair_comparison_profile: dict[str, Any],
    structural_correlation_register: list[dict[str, Any]],
    structural_correlation_graph: list[dict[str, Any]] | None = None,
    control_boundary_map: list[dict[str, Any]],
    maintenance_dependency_map: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    route_state = text(asset_family_research_profile.get("route_state"))
    rows: list[dict[str, Any]] = []
    if not _allows_conditional_archetypal_intelligence(asset_family_research_profile):
        return rows

    control_boundary_state = text((operational_intake_pack.get("control_boundary_pack", {}) or {}).get("current_state"))
    maintenance_state = text((operational_intake_pack.get("maintenance_maturity_pack", {}) or {}).get("current_state"))
    structural_correlation_graph = list(structural_correlation_graph or [])

    if asset_family == "commercial_building":
        rows.append(
            {
                "contradiction": "Regulation vs control boundary",
                "layers": ["regulation", "control", "finance"],
                "strategic_risk": "Owner-facing compliance and capital pressure may be interpreted as owner-capturable savings before the controllable load boundary is observed.",
                "evidence_needed": ["tenant metering map", "lease responsibility matrix", "LL97 filing basis"],
                "possible_redesign": "Control-boundary redesign, submetering and lease architecture before owner-only retrofit logic.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS" if control_boundary_map else "ARCHETYPAL_PRIOR",
            }
        )
        rows.append(
            {
                "contradiction": "Benchmark signal vs owner economics",
                "layers": ["benchmarking", "physics", "finance"],
                "strategic_risk": "A public benchmark can support screening while still being structurally too weak to support owner ROI logic.",
                "evidence_needed": ["utility bills", "central plant topology", "tenant schedule and metering evidence"],
                "possible_redesign": "Reframe from EUI problem to control-and-capture problem.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )

    if asset_family == "infrastructure_node":
        rows.append(
            {
                "contradiction": "Energy average vs service continuity burden",
                "layers": ["benchmarking", "operation", "continuity"],
                "strategic_risk": "Average-energy framing can label continuity duty or redundancy burden as waste before the node-level service obligation is normalized.",
                "evidence_needed": ["service continuity profile", "dispatch or uptime logs", "redundancy class", "utility bills and tariff structure"],
                "possible_redesign": "Normalize continuity and dispatch burden before diagnosing inefficiency or sizing optimization CAPEX.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
        rows.append(
            {
                "contradiction": "Tariff pressure vs reliability obligation",
                "layers": ["finance", "tariff", "operation"],
                "strategic_risk": "Demand or PF pressure can push optimization logic that conflicts with reliability or dispatch obligations.",
                "evidence_needed": ["tariff structure", "demand profile", "switching or dispatch rules", "maintenance or outage evidence"],
                "possible_redesign": "Sequence tariff optimization only after continuity and reliability boundaries are locally bounded.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )

    if asset_family == "utility_heavy_site":
        rows.append(
            {
                "contradiction": "Consumption framing vs demand-structure reality",
                "layers": ["finance", "tariff", "physics"],
                "strategic_risk": "Aggregate-consumption framing can miss that demand peaks, PF or reactive structure, and support-system sequencing are the real economic boundary.",
                "evidence_needed": ["utility bills with demand or PF charges", "tariff structure", "major motor inventory", "interval demand profile"],
                "possible_redesign": "Discriminate demand, PF and sequencing logic before broad consumption-reduction CAPEX.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
        rows.append(
            {
                "contradiction": "Tariff symptom vs support-system duty",
                "layers": ["tariff", "operation", "maintenance"],
                "strategic_risk": "Tariff pressure can be visible even when the deeper driver is structural support-duty or maintenance-driven instability rather than generic waste.",
                "evidence_needed": ["support-duty schedule", "maintenance logs", "CMMS history", "metering boundary"],
                "possible_redesign": "Separate structural support-duty from avoidable sequencing, maintenance drift and PF correction logic.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
        rows.append(
            {
                "contradiction": "Procurement economics vs maintenance reality",
                "layers": ["procurement", "maintenance", "operation"],
                "strategic_risk": "Lowest-first-cost decisions can transfer cost into downtime, spare risk and unstable utility-support performance.",
                "evidence_needed": ["preventive maintenance proof", "downtime records", "critical-spares evidence"],
                "possible_redesign": "Prioritize lifecycle and uptime logic over bare upfront cost logic.",
                "evidence_state": "ARCHETYPAL_PRIOR" if maintenance_state not in {"partially_evidenced", "evidenced"} else "CONDITIONAL_HYPOTHESIS",
            }
        )

    elif asset_family in {"industrial_manufacturing", "thermal_process_site"}:
        rows.append(
            {
                "contradiction": "Benchmark vs process reality",
                "layers": ["benchmarking", "process", "physics"],
                "strategic_risk": "Area or aggregate-consumption comparisons can mislabel structural process duty as avoidable waste.",
                "evidence_needed": ["throughput by shift", "process map", "utility baseline", "product mix or thermal duty proxy"],
                "possible_redesign": "Reframe from generic efficiency to process-load discrimination first.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
        rows.append(
            {
                "contradiction": "Finance framing vs physical dependency",
                "layers": ["finance", "physics", "operation"],
                "strategic_risk": "Savings framing can move capital before the system knows whether cost is driven by throughput, thermal duty, demand structure or controllable support-system loss.",
                "evidence_needed": ["utility bills", "throughput by shift", "demand profile", "equipment inventory"],
                "possible_redesign": "Separate process redesign, maintenance redesign and utility optimization before CAPEX framing.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )
        rows.append(
            {
                "contradiction": "Procurement economics vs maintenance reality",
                "layers": ["procurement", "maintenance", "operation"],
                "strategic_risk": "Lowest-first-cost decisions can transfer cost into downtime, spare risk and unstable operating performance.",
                "evidence_needed": ["preventive maintenance proof", "downtime records", "critical-spares evidence"],
                "possible_redesign": "Prioritize lifecycle and uptime logic over bare upfront cost logic.",
                "evidence_state": "ARCHETYPAL_PRIOR" if maintenance_state not in {"partially_evidenced", "evidenced"} else "CONDITIONAL_HYPOTHESIS",
            }
        )

    if asset_family in {"logistics_warehouse", "cold_chain"}:
        rows.append(
            {
                "contradiction": "Area benchmark vs service-level complexity",
                "layers": ["benchmarking", "operation", "logistics"],
                "strategic_risk": "Area-only logic can hide that movement intensity, charging windows, temperature duty or dock activity are the real cost drivers.",
                "evidence_needed": ["service-level proxy", "dock activity profile", "charging schedule", "temperature-duty map where relevant"],
                "possible_redesign": "Normalize operational intensity before diagnosing inefficiency.",
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        )

    for row in rows:
        layers = {text(layer) for layer in list(row.get("layers", []) or []) if text(layer)}
        supporting_rows = _supporting_correlation_register(
            contradiction_row=row,
            structural_correlation_graph=structural_correlation_graph,
        )
        comparison_state = text(fair_comparison_profile.get("comparison_state"))
        fair_comparison_pressure_score = 0
        if "benchmarking" in layers and comparison_state and comparison_state != "comparison_admissible":
            fair_comparison_pressure_score = 2
        boundary_pressure_score = 0
        if "control" in layers and control_boundary_state in {"public_context_only", "partially_evidenced", "not_yet_evidenced"}:
            boundary_pressure_score = 2
        maintenance_pressure_score = 0
        if "maintenance" in layers and maintenance_state in {"public_context_only", "partially_evidenced", "not_yet_evidenced"}:
            maintenance_pressure_score = 2
        correlation_constellation_score = (
            len(layers) * 2
            + sum(int(support.get("support_score", 0) or 0) for support in supporting_rows)
            + fair_comparison_pressure_score
            + boundary_pressure_score
            + maintenance_pressure_score
        )
        row["supporting_correlation_count"] = len(supporting_rows)
        row["supporting_correlation_register"] = supporting_rows
        row["supporting_correlation_ids"] = [text(support.get("correlation_id")) for support in supporting_rows if text(support.get("correlation_id"))]
        row["supporting_correlation_headlines"] = [text(support.get("correlation")) for support in supporting_rows if text(support.get("correlation"))]
        row["fair_comparison_pressure_score"] = fair_comparison_pressure_score
        row["boundary_pressure_score"] = boundary_pressure_score
        row["maintenance_pressure_score"] = maintenance_pressure_score
        row["correlation_constellation_score"] = correlation_constellation_score
    return sorted(
        rows,
        key=lambda row: (
            -int(row.get("correlation_constellation_score", 0) or 0),
            -int(row.get("supporting_correlation_count", 0) or 0),
            text(row.get("contradiction")),
        ),
    )


def build_invalid_problem_frame_register(
    *,
    asset_family_research_profile: dict[str, Any],
    fair_comparison_profile: dict[str, Any],
) -> list[dict[str, Any]]:
    asset_family = text(asset_family_research_profile.get("asset_family"))
    comparison_state = text(fair_comparison_profile.get("comparison_state"))
    if comparison_state == "inadmissible_until_asset_identity_bounded":
        return [
            {
                "apparent_problem": "premature_operating_diagnosis",
                "why_invalid_or_premature": "The target is not yet bounded as an operating asset, so congruence logic would be speculative.",
                "what_problem_should_be_tested_instead": "Asset identity and operating boundary first.",
                "evidence_needed": ["bounded operating asset evidence"],
                "evidence_state": "INADMISSIBLE_CLAIM",
            }
        ]

    if asset_family == "commercial_building":
        return [
            {
                "apparent_problem": "high_building_energy_means_owner_retrofit_opportunity",
                "why_invalid_or_premature": "The unresolved issue may be control boundary and owner economic capture, not aggregate whole-building energy alone.",
                "what_problem_should_be_tested_instead": "Whether the owner controls the dominant covered load and economic boundary.",
                "evidence_needed": ["tenant metering map", "lease responsibility matrix", "utility bills", "LL97 filing basis"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        ]
    if asset_family == "infrastructure_node":
        return [
            {
                "apparent_problem": "high_node_energy_automatically_means_waste",
                "why_invalid_or_premature": "The dominant driver may be service continuity burden, dispatch duty, redundancy class or tariff structure rather than avoidable waste.",
                "what_problem_should_be_tested_instead": "Which continuity or dispatch variable actually defines the fair comparison and cost boundary.",
                "evidence_needed": ["service continuity profile", "dispatch burden proxy", "redundancy class", "utility bills and tariff structure"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        ]
    if asset_family == "utility_heavy_site":
        return [
            {
                "apparent_problem": "high_site_consumption_automatically_means_main_utility_opportunity",
                "why_invalid_or_premature": "The dominant driver may be demand structure, PF or reactive exposure, support-system duty or sequencing rather than total consumption alone.",
                "what_problem_should_be_tested_instead": "Which demand, PF, sequencing or support-system variable actually defines the cost boundary.",
                "evidence_needed": ["utility bills with demand or PF charges", "tariff structure", "major motor inventory", "support-duty schedule"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        ]
    if asset_family in {"industrial_manufacturing", "thermal_process_site"}:
        return [
            {
                "apparent_problem": "high_site_energy_intensity_automatically_means_waste",
                "why_invalid_or_premature": "The dominant driver may be structural process duty, throughput, thermal load or demand structure rather than correctable waste.",
                "what_problem_should_be_tested_instead": "Which physical or operating dependency actually drives cost and whether it is controllable.",
                "evidence_needed": ["throughput by shift", "process map", "utility bills", "equipment inventory"],
                "evidence_state": "CONDITIONAL_HYPOTHESIS",
            }
        ]
    return [
        {
            "apparent_problem": "high_energy_per_area_means_warehouse_inefficiency",
            "why_invalid_or_premature": "Service level, movement intensity, charging windows or refrigeration duty may dominate the comparison.",
            "what_problem_should_be_tested_instead": "Which operational intensity variable defines a fair comparison basis.",
            "evidence_needed": ["service-level proxy", "dock activity profile", "charging schedule"],
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
        }
    ]
