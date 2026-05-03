from __future__ import annotations

from typing import Any

from .schemas import CompetitiveComparisonRecord, StructuralEvidenceState


def build_competitive_comparison_register(
    *,
    target_definition: dict[str, Any],
    archetype_resolution: dict[str, Any],
    structural_benchmark_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    selected_archetype_id = str(archetype_resolution.get("selected_archetype_id", "")).strip()
    rows: list[dict[str, Any]] = []

    if target_type == "commercial_building":
        comparison_mode = "conditional_comparison" if selected_archetype_id == "commercial_office_tower_nyc" else "archetypal_best_practice"
        rows.append(
            CompetitiveComparisonRecord(
                better_performer=(
                    "Conditional peer comparator: Class A NYC tower with submetering, green-lease discipline, and continuous commissioning"
                    if comparison_mode == "conditional_comparison"
                    else "Archetypal peer pattern: Class A NYC tower with submetering, green-lease discipline, and continuous commissioning"
                ),
                what_they_do_better="Uses submetering and green-lease discipline to separate tenant and owner loads, tunes the BMS against actual occupancy, and frames LL97 as a control-and-contract problem before assuming retrofit savings.",
                structural_advantage="The peer aligns metering, owner control, and compliance strategy more tightly than an unresolved owner/tenant boundary allows.",
                why_it_matters="This can change whether capital logic is retrofit savings, penalty avoidance, or contractual redesign.",
                transferability="Medium if the subject asset can validate owner control boundary and implement lease / metering changes.",
                peer_type="conditional_peer_pattern" if comparison_mode == "conditional_comparison" else "archetypal_peer_pattern",
                what_it_proves="It proves which control-boundary pattern would make peer screening decision-useful.",
                what_it_does_not_prove="It does not prove that a named real competitor outperforms the asset or that savings are owner-capturable here.",
                evidence_needed=[
                    "tenant metering map",
                    "lease responsibility matrix",
                    "BMS / central plant topology",
                    "LL97 filing basis",
                ],
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                comparison_mode=comparison_mode,
            ).to_dict()
        )

    if target_type == "manufacturing_facility":
        comparison_mode = "conditional_comparison" if selected_archetype_id == "manufacturing_laminate" else "archetypal_best_practice"
        rows.append(
            CompetitiveComparisonRecord(
                better_performer=(
                    "Conditional peer comparator: laminate or thermal-process manufacturer with stronger thermal integration, uptime discipline, and support-system control"
                    if comparison_mode == "conditional_comparison"
                    else "Archetypal peer pattern: laminate or thermal-process manufacturer with stronger thermal integration, uptime discipline, and support-system control"
                ),
                what_they_do_better="Bounds throughput and cure-duty first, then targets compressed air, thermal recovery, scheduling, and maintenance where they actually move economics.",
                structural_advantage="The peer advantage may come from process control, uptime, scrap reduction, and thermal integration rather than generic energy retrofit alone.",
                why_it_matters="This changes whether the right next move is process redesign, maintenance redesign, or targeted utility optimization.",
                transferability="Medium only after process map, throughput, utility baseline, and downtime evidence are observed.",
                peer_type="conditional_peer_pattern" if comparison_mode == "conditional_comparison" else "archetypal_peer_pattern",
                what_it_proves="It proves which operating pattern would justify process redesign, maintenance redesign, or targeted utility optimization.",
                what_it_does_not_prove="It does not prove observed competitive superiority, transferable ROI, or a named competitor advantage without source-bounded evidence.",
                evidence_needed=[
                    "process map",
                    "throughput by shift",
                    "utility baseline",
                    "downtime logs",
                    "equipment inventory",
                ],
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if selected_archetype_id == "manufacturing_laminate" else StructuralEvidenceState.ARCHETYPAL_PRIOR,
                comparison_mode=comparison_mode,
            ).to_dict()
        )

    if not rows:
        for benchmark in structural_benchmark_register:
            rows.append(
                CompetitiveComparisonRecord(
                    better_performer=str(benchmark.get("peer_or_benchmark", "")).strip() or "Archetypal peer pattern",
                    what_they_do_better="No bounded competitive comparison is admissible yet beyond the benchmark context.",
                    structural_advantage="Comparison remains too weak to attribute structural superiority.",
                    why_it_matters="Premature competitive claims would overstate the evidence.",
                    transferability="Low until better peer evidence is observed.",
                    peer_type="archetypal_peer_pattern",
                    what_it_proves="It proves only that a benchmark lens exists for bounded comparison.",
                    what_it_does_not_prove="It does not prove a real better performer, competitive superiority, or transferable economics.",
                    evidence_needed=["peer operational evidence", "peer control-boundary evidence"],
                    evidence_state=StructuralEvidenceState.ARCHETYPAL_PRIOR,
                    comparison_mode="archetypal_best_practice",
                ).to_dict()
            )
            break

    return rows
