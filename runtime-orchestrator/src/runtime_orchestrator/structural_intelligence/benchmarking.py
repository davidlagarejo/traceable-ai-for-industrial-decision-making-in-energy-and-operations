from __future__ import annotations

from typing import Any

from .schemas import StructuralBenchmarkRecord, StructuralEvidenceState


def _var_map(dominant_variable_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("variable", "")).strip(): row
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
    }


def _dataset_keys(dataset_coverage_register: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in dataset_coverage_register:
        key = str(row.get("dataset_key", "")).strip().lower()
        if key:
            keys.add(key)
    return keys


def build_structural_benchmark_register(
    *,
    target_definition: dict[str, Any],
    archetype_resolution: dict[str, Any],
    system_abstraction: dict[str, Any],
    dominant_variable_register: list[dict[str, Any]],
    dataset_coverage_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    selected_archetype_id = str(archetype_resolution.get("selected_archetype_id", "")).strip()
    variables = _var_map(dominant_variable_register)
    dataset_keys = _dataset_keys(dataset_coverage_register)
    rows: list[dict[str, Any]] = []

    if target_type == "commercial_building":
        ll97_state = str(variables.get("LL97_pathway", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        tenant_state = str(variables.get("tenant_metering", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        control_state = str(variables.get("owner_control_boundary", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        if selected_archetype_id == "commercial_office_tower_nyc":
            rows.append(
                StructuralBenchmarkRecord(
                    dimension="compliance and public screening context",
                    subject_asset="NYC Class A tower with LL84/LL97 public-screening context",
                    peer_or_benchmark="Class A NYC LL97-covered office towers",
                    difference="Public screening is supportable, but closure remains blocked until owner-control and filing-grade evidence are bounded.",
                    evidence_state=StructuralEvidenceState.OBSERVED_FACT if ll97_state == "OBSERVED_FACT" else StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                    interpretation="Peer comparison is admissible for bounded screening, not for declaring retrofit economics or compliance closure.",
                ).to_dict()
            )
        rows.append(
            StructuralBenchmarkRecord(
                dimension="owner control boundary vs peer control boundary",
                subject_asset=(
                    "Owner / tenant boundary remains unresolved"
                    if control_state != "OBSERVED_FACT" or tenant_state != "OBSERVED_FACT"
                    else "Owner / tenant boundary is more clearly bounded"
                ),
                peer_or_benchmark="Submetered, green-lease, continuously commissioned peer tower",
                difference="A peer can outperform structurally by separating tenant and owner loads before pursuing owner-only retrofit logic.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                interpretation="Do not treat benchmark EUI spread as owner-capturable value until control boundary is observed.",
            ).to_dict()
        )
        rows.append(
            StructuralBenchmarkRecord(
                dimension="base-building systems vs tenant-driven loads",
                subject_asset="Central-plant and tenant-load dominance remain only partially bounded by public data.",
                peer_or_benchmark="Peer tower with validated central-plant topology and tenant metering discipline",
                difference="The structural difference is not just EUI level; it is whether the dominant load sits in a controllable boundary.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if "nyc_ll84_energy_benchmarking" in dataset_keys else StructuralEvidenceState.ARCHETYPAL_PRIOR,
                interpretation="Benchmarking is useful only to choose which evidence to request next.",
            ).to_dict()
        )

    if target_type == "manufacturing_facility":
        throughput_state = str(variables.get("throughput", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        thermal_state = str(variables.get("thermal_duty", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        downtime_state = str(variables.get("downtime", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        rows.append(
            StructuralBenchmarkRecord(
                dimension="process vs process structural intensity",
                subject_asset="Laminate process intensity is not yet separated into structural thermal duty vs avoidable waste.",
                peer_or_benchmark="thermal-process laminate manufacturers with validated throughput and cure-duty baselines",
                difference="A peer may look better not because it uses less total energy, but because it manages thermal integration, schedule discipline, and yield more effectively.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if throughput_state == "CONDITIONAL_HYPOTHESIS" or thermal_state == "CONDITIONAL_HYPOTHESIS" else StructuralEvidenceState.ARCHETYPAL_PRIOR,
                interpretation="Do not map benchmark intensity directly to waste before bounding throughput and thermal duty.",
            ).to_dict()
        )
        rows.append(
            StructuralBenchmarkRecord(
                dimension="maintenance and uptime discipline",
                subject_asset="Downtime, failure cost, and maintenance discipline remain under-observed.",
                peer_or_benchmark="Peer plant with disciplined uptime management, spare-parts readiness, and stable schedule execution",
                difference="A structural peer advantage may come from uptime and scrap discipline rather than lower utility spend alone.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if downtime_state == "CONDITIONAL_HYPOTHESIS" else StructuralEvidenceState.ARCHETYPAL_PRIOR,
                interpretation="Maintenance benchmarking matters before assuming an energy-first capital story.",
            ).to_dict()
        )
        rows.append(
            StructuralBenchmarkRecord(
                dimension="support-system discipline vs process redesign need",
                subject_asset="Compressed air and support systems are plausible levers but not yet proven dominant.",
                peer_or_benchmark="Peer operation with verified compressed-air discipline and thermal integration practices",
                difference="The structural comparison is about where the dominant avoidable loss sits, not about adopting generic best practice blindly.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                interpretation="Use this comparison to discriminate hypotheses, not to assert superiority.",
            ).to_dict()
        )

    _ = system_abstraction
    return rows
