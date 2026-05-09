from __future__ import annotations

from typing import Any

from .schemas import CompetitiveComparisonRecord, StructuralEvidenceState


def _first_benchmark_context(structural_benchmark_register: list[dict[str, Any]]) -> str:
    row = dict(structural_benchmark_register[0] if structural_benchmark_register else {})
    peer_or_benchmark = str(row.get("peer_or_benchmark", "")).strip()
    dimension = str(row.get("dimension", "")).strip()
    if peer_or_benchmark and dimension:
        return f"Benchmark anchor: {peer_or_benchmark} ({dimension})."
    if peer_or_benchmark:
        return f"Benchmark anchor: {peer_or_benchmark}."
    return ""


def _comparison_row(
    *,
    better_performer: str,
    what_they_do_better: str,
    structural_advantage: str,
    why_it_matters: str,
    transferability: str,
    peer_type: str,
    what_it_proves: str,
    what_it_does_not_prove: str,
    evidence_needed: list[str],
    evidence_state: StructuralEvidenceState,
    comparison_mode: str,
    structural_benchmark_register: list[dict[str, Any]],
    peer_requirement_rows: list[dict[str, str]],
    candidate_peer_frame_register: list[dict[str, str]],
    better_practice_delta_register: list[dict[str, str]],
    peer_superiority_block_reason: str,
) -> dict[str, Any]:
    row = CompetitiveComparisonRecord(
        better_performer=better_performer,
        what_they_do_better=what_they_do_better,
        structural_advantage=structural_advantage,
        why_it_matters=why_it_matters,
        transferability=transferability,
        peer_type=peer_type,
        what_it_proves=what_it_proves,
        what_it_does_not_prove=what_it_does_not_prove,
        source_reference=_first_benchmark_context(structural_benchmark_register),
        evidence_needed=evidence_needed,
        evidence_state=evidence_state,
        comparison_mode=comparison_mode,
    ).to_dict()
    row.update(
        {
            "peer_requirement_rows": peer_requirement_rows,
            "candidate_peer_frame_register": candidate_peer_frame_register,
            "better_practice_delta_register": better_practice_delta_register,
            "peer_superiority_block_reason": peer_superiority_block_reason,
        }
    )
    return row


def build_competitive_comparison_register(
    *,
    target_definition: dict[str, Any],
    archetype_resolution: dict[str, Any],
    structural_benchmark_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    selected_archetype_id = str(archetype_resolution.get("selected_archetype_id", "")).strip()
    rows: list[dict[str, Any]] = []

    if target_type in {"warehouse_distribution", "cold_chain_facility"}:
        comparison_mode = "conditional_comparison" if selected_archetype_id in {"logistics_warehouse_generic", "cold_chain_generic"} else "archetypal_best_practice"
        cold_chain = target_type == "cold_chain_facility" or selected_archetype_id == "cold_chain_generic"
        rows.append(
            _comparison_row(
                better_performer=(
                    "Conditional peer comparator: high-service logistics node with dock discipline, charging orchestration, and explicit thermal / control boundary separation"
                    if comparison_mode == "conditional_comparison"
                    else "Archetypal peer pattern: high-service logistics node with dock discipline, charging orchestration, and explicit thermal / control boundary separation"
                ),
                what_they_do_better=(
                    "Normalizes service intensity first, separates charging peaks from generic EUI, and treats dock exchange, scheduling, and tariff structure as economic drivers before calling the asset inefficient."
                    if not cold_chain
                    else "Separates refrigeration duty from generic warehouse load, enforces dock-seal and thermal-boundary discipline, and treats charging and tariff exposure as distinct cost lanes."
                ),
                structural_advantage=(
                    "The peer frame is superior because it discriminates movement intensity, dock exchange, charging peaks, and value-capture boundary before targeting HVAC or lighting CAPEX."
                    if not cold_chain
                    else "The peer frame is superior because it distinguishes refrigeration duty, dock thermal exchange, charging peaks, and capture boundary before treating the whole site as one warehouse denominator."
                ),
                why_it_matters="This changes whether the right next move is tariff orchestration, dock-loss validation, thermal-boundary separation, or owner/operator redesign rather than a generic retrofit.",
                transferability="Medium only after subtype, service intensity, charging profile, and control boundary are bounded.",
                peer_type="conditional_peer_pattern" if comparison_mode == "conditional_comparison" else "archetypal_peer_pattern",
                what_it_proves="It proves what a valid logistics peer frame would require and which better-practice deltas could plausibly explain different cost behavior.",
                what_it_does_not_prove="It does not prove that this asset is worse than a named warehouse, that any competitor is superior, or that the same CAPEX would transfer locally.",
                evidence_needed=[
                    "subtype / service model",
                    "dock density and service intensity",
                    "charging profile and tariff interval context",
                    "control boundary and meter responsibility",
                ],
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if comparison_mode == "conditional_comparison" else StructuralEvidenceState.ARCHETYPAL_PRIOR,
                comparison_mode=comparison_mode,
                structural_benchmark_register=structural_benchmark_register,
                peer_requirement_rows=[
                    {
                        "peer_requirement": "Subtype and service model",
                        "status": "required",
                        "why_it_matters": "Dry storage, fulfillment, cross-dock, and cold-chain assets do not share the same denominator.",
                        "missing_evidence": "service model, temperature regime, fulfillment intensity",
                    },
                    {
                        "peer_requirement": "Dock density and service intensity",
                        "status": "required",
                        "why_it_matters": "Area-normalized peer logic breaks when dock cycles and movement intensity dominate cost.",
                        "missing_evidence": "dock count, dock cycles, operating hours, throughput proxy",
                    },
                    {
                        "peer_requirement": "Charging and tariff profile",
                        "status": "required",
                        "why_it_matters": "Charging windows can create structurally different cost behavior without any generic efficiency gap.",
                        "missing_evidence": "fleet profile, charging windows, demand tariff structure",
                    },
                    {
                        "peer_requirement": "Control boundary and value capture",
                        "status": "required",
                        "why_it_matters": "The owner can fund CAPEX while the operator controls the dominant variable.",
                        "missing_evidence": "lease responsibility, metering boundary, operating control map",
                    },
                ],
                candidate_peer_frame_register=[
                    {
                        "candidate_peer_frame": "high-service dry fulfillment node",
                        "candidate_state": "conditional_until_service_intensity_is_bounded",
                        "why_it_matters": "Tests whether movement intensity and charging windows invalidate EUI-first logic.",
                    },
                    {
                        "candidate_peer_frame": "cross-dock / rapid-turn logistics node",
                        "candidate_state": "conditional_until_dock_cycle_and_schedule_evidence_is_bounded",
                        "why_it_matters": "Tests whether dock exchange and continuity duty dominate thermal and cost behavior.",
                    },
                    {
                        "candidate_peer_frame": "managed cold-chain logistics peer" if cold_chain else "temperature-sensitive logistics peer",
                        "candidate_state": "conditional_until_thermal_regime_is_bounded",
                        "why_it_matters": "Tests whether refrigeration duty creates a separate denominator and practice stack.",
                    },
                ],
                better_practice_delta_register=[
                    {
                        "practice_delta": "Charging-window orchestration",
                        "why_plausible": "A peer can look better because demand peaks are scheduled, not because annual energy is lower.",
                        "evidence_needed": "charger timing, tariff intervals, fleet turnover profile",
                    },
                    {
                        "practice_delta": "Dock-seal / infiltration discipline",
                        "why_plausible": "A peer can look better because dock exchange is controlled, not because HVAC equipment is newer.",
                        "evidence_needed": "dock discipline evidence, seal condition, thermal boundary observations",
                    },
                    {
                        "practice_delta": "Boundary-aware cost capture",
                        "why_plausible": "A peer can outperform economically because control, payment, and capture align across owner and operator.",
                        "evidence_needed": "lease/control matrix, metering boundary, operating accountability map",
                    },
                ],
                peer_superiority_block_reason="Peer superiority remains prohibited until subtype, service intensity, charging profile, and value-capture boundary are bounded for both subject and comparator.",
            )
        )

    if target_type == "commercial_building":
        comparison_mode = "conditional_comparison" if selected_archetype_id == "commercial_office_tower_nyc" else "archetypal_best_practice"
        rows.append(
            _comparison_row(
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
                structural_benchmark_register=structural_benchmark_register,
                peer_requirement_rows=[
                    {
                        "peer_requirement": "Owner / tenant control boundary",
                        "status": "required",
                        "why_it_matters": "Whole-building peers are misleading if owner burden and controllable load diverge.",
                        "missing_evidence": "tenant metering map, lease responsibility matrix",
                    },
                    {
                        "peer_requirement": "Occupancy and after-hours burden",
                        "status": "required",
                        "why_it_matters": "A tower with atypical after-hours duty is not comparable on raw EUI.",
                        "missing_evidence": "occupancy pattern, after-hours load shape, tenant operations profile",
                    },
                    {
                        "peer_requirement": "Plant topology and BMS maturity",
                        "status": "required",
                        "why_it_matters": "Peers differ because of plant architecture and control discipline, not just retrofit age.",
                        "missing_evidence": "central plant map, BMS topology, commissioning posture",
                    },
                ],
                candidate_peer_frame_register=[
                    {
                        "candidate_peer_frame": "Class A tower with aligned lease / metering discipline",
                        "candidate_state": "conditional_until_boundary_is_bounded",
                        "why_it_matters": "Tests whether the case is governance-led rather than technology-led.",
                    },
                    {
                        "candidate_peer_frame": "continuous-commissioning office tower",
                        "candidate_state": "conditional_until BMS and occupancy patterns are bounded",
                        "why_it_matters": "Tests whether better control hygiene, not retrofit intensity, explains the gap.",
                    },
                ],
                better_practice_delta_register=[
                    {
                        "practice_delta": "Green-lease and submetering discipline",
                        "why_plausible": "A peer can outperform because owner and tenant signals are separated before capital is deployed.",
                        "evidence_needed": "lease clauses, submeter layout, billing boundary",
                    },
                    {
                        "practice_delta": "Continuous commissioning against real occupancy",
                        "why_plausible": "A peer can look better because controls match occupancy reality rather than schedule assumptions.",
                        "evidence_needed": "BMS trend points, occupancy pattern, after-hours load evidence",
                    },
                ],
                peer_superiority_block_reason="Peer superiority remains prohibited until owner/tenant boundary, occupancy burden, and plant control context are normalized.",
            )
        )

    if target_type == "manufacturing_facility":
        comparison_mode = "conditional_comparison" if selected_archetype_id == "manufacturing_laminate" else "archetypal_best_practice"
        rows.append(
            _comparison_row(
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
                structural_benchmark_register=structural_benchmark_register,
                peer_requirement_rows=[
                    {
                        "peer_requirement": "Process type and thermal lane",
                        "status": "required",
                        "why_it_matters": "A fair peer must share the dominant process and thermal burden, not just NAICS labels.",
                        "missing_evidence": "process map, thermal lane, utility topology",
                    },
                    {
                        "peer_requirement": "Throughput and product mix",
                        "status": "required",
                        "why_it_matters": "Production intensity can dominate economics before generic efficiency does.",
                        "missing_evidence": "throughput by shift, product mix, duty cycle",
                    },
                    {
                        "peer_requirement": "Maintenance and downtime maturity",
                        "status": "required",
                        "why_it_matters": "A peer can look better because downtime and support-system discipline are different, not because the plant is intrinsically more efficient.",
                        "missing_evidence": "downtime logs, PM evidence, maintenance maturity",
                    },
                ],
                candidate_peer_frame_register=[
                    {
                        "candidate_peer_frame": "thermal-process manufacturer with stronger uptime discipline",
                        "candidate_state": "conditional_until_process_and_downtime_evidence_are_bounded",
                        "why_it_matters": "Tests whether economics are reliability-led before energy-led.",
                    },
                    {
                        "candidate_peer_frame": "support-system-optimized laminate peer",
                        "candidate_state": "conditional_until compressed-air / steam / utility stack is bounded",
                        "why_it_matters": "Tests whether support-system control, not core process inefficiency, explains the gap.",
                    },
                ],
                better_practice_delta_register=[
                    {
                        "practice_delta": "Thermal integration and sequencing discipline",
                        "why_plausible": "A peer can outperform because thermal duty is better orchestrated, not because installed equipment is radically different.",
                        "evidence_needed": "process heat map, recovery topology, duty sequencing evidence",
                    },
                    {
                        "practice_delta": "Maintenance maturity and uptime control",
                        "why_plausible": "A peer can outperform because reliability discipline protects economics before energy savings do.",
                        "evidence_needed": "PM records, downtime logs, CMMS/work-order evidence",
                    },
                    {
                        "practice_delta": "Compressed-air / support-system discipline",
                        "why_plausible": "A peer can look better because hidden support-system waste is bounded and managed.",
                        "evidence_needed": "utility stack map, compressor duty, leak-management evidence",
                    },
                ],
                peer_superiority_block_reason="Peer superiority remains prohibited until process lane, throughput context, and maintenance reality are normalized.",
            )
        )

    if not rows:
        for benchmark in structural_benchmark_register:
            rows.append(
                _comparison_row(
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
                    structural_benchmark_register=structural_benchmark_register,
                    peer_requirement_rows=[
                        {
                            "peer_requirement": "Comparable operating pattern",
                            "status": "required",
                            "why_it_matters": "A benchmark lens alone does not define a fair peer.",
                            "missing_evidence": "operating pattern, denominator, control boundary",
                        }
                    ],
                    candidate_peer_frame_register=[
                        {
                            "candidate_peer_frame": "archetypal structural peer frame",
                            "candidate_state": "blocked_pending_requirements",
                            "why_it_matters": "The system can name the peer family before it can claim comparability.",
                        }
                    ],
                    better_practice_delta_register=[
                        {
                            "practice_delta": "bounded better-practice delta still unknown",
                            "why_plausible": "The benchmark lens exists, but the practice explanation is not yet bounded.",
                            "evidence_needed": "peer operational evidence, control-boundary evidence",
                        }
                    ],
                    peer_superiority_block_reason="Peer superiority remains prohibited because the framework only has an archetypal benchmark lens, not a bounded comparator.",
                )
            )
            break

    return rows
