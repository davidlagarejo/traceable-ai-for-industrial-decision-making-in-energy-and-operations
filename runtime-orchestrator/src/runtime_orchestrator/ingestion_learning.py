from __future__ import annotations

from typing import Any


_REPORT_TYPE_ORDER = {
    "Target Classification Brief": 0,
    "Entity Address Classification Brief": 0,
    "Decision-Blocked Asset Brief": 1,
    "Exploratory Prior Brief": 2,
    "Compliance / Investment Screening Brief": 3,
    "Full Technical Decision Intelligence Report": 4,
}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _unique_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def _report_rank(label: str) -> int:
    return _REPORT_TYPE_ORDER.get(str(label or "").strip(), -1)


def _net_progress_state(progress_signals: list[str], regression_signals: list[str], previous_run_id: str) -> str:
    if not previous_run_id:
        return "initial_run"
    if progress_signals and regression_signals:
        return "mixed"
    if progress_signals:
        return "improved"
    if regression_signals:
        return "regressed"
    return "unchanged"


def _current_snapshot(
    runtime: dict[str, Any],
    m20: dict[str, Any],
    m28: dict[str, Any],
    m34: dict[str, Any],
    report_preflight_register: dict[str, Any],
    phase_self_evaluation_register: dict[str, Any],
) -> dict[str, Any]:
    report_type_trace = _as_dict(runtime.get("report_type_trace"))
    routing_plan_compliance = _as_dict(m28.get("routing_plan_compliance"))
    maturity_summary = _as_dict(m34.get("maturity_summary"))
    source_register = _as_list(m28.get("source_register"))
    accepted_source_count = int(routing_plan_compliance.get("accepted_routed_sources", 0) or 0)
    if accepted_source_count <= 0:
        accepted_source_count = sum(1 for row in source_register if bool(row.get("accepted")))
    return {
        "recommended_report_type": str(
            report_type_trace.get("final_published_report_type")
            or runtime.get("recommended_report_type")
            or ""
        ).strip(),
        "phase_result": str(
            _as_dict(phase_self_evaluation_register.get("summary")).get("overall_result", "")
        ).strip(),
        "cluster_levels": _as_dict(maturity_summary.get("cluster_levels")),
        "key_variable_bottlenecks": _unique_strings(
            _as_list(maturity_summary.get("key_bottlenecks"))
        ),
        "mandatory_source_gaps": _unique_strings(
            _as_list(routing_plan_compliance.get("mandatory_sources_missing_from_executor"))
        ),
        "accepted_source_count": accepted_source_count,
        "belief_revision_count": len(_as_list(m20.get("belief_revision_register"))),
        "report_preflight_passed": bool(report_preflight_register.get("passed", False)),
        "critical_preflight_failure_count": int(
            report_preflight_register.get("critical_failure_count", 0) or 0
        ),
    }


def _previous_snapshot(previous_run_summary: dict[str, Any]) -> dict[str, Any]:
    if not previous_run_summary:
        return {}
    evidence_maturity_summary = _as_dict(previous_run_summary.get("evidence_maturity_summary"))
    report_type_trace = _as_dict(previous_run_summary.get("report_type_trace"))
    source_yield_memory_summary = _as_dict(previous_run_summary.get("source_yield_memory_summary"))
    base_snapshot = {
        "recommended_report_type": str(
            report_type_trace.get("final_published_report_type")
            or previous_run_summary.get("recommended_report_type")
            or ""
        ).strip(),
        "phase_result": str(
            _as_dict(previous_run_summary.get("phase_self_evaluation_summary")).get("overall_result", "")
        ).strip(),
        "cluster_levels": _as_dict(evidence_maturity_summary.get("cluster_levels")),
        "key_variable_bottlenecks": _unique_strings(
            _as_list(previous_run_summary.get("key_variable_bottlenecks"))
            or _as_list(evidence_maturity_summary.get("key_bottlenecks"))
        ),
        "mandatory_source_gaps": _unique_strings(
            _as_list(_as_dict(previous_run_summary.get("case_delta_summary")).get("current_snapshot", {}).get("mandatory_source_gaps"))
            or _as_list(_as_dict(previous_run_summary.get("pipeline_health_summary")).get("mandatory_sources_missing_from_executor"))
        ),
        "accepted_source_count": int(
            source_yield_memory_summary.get("productive_source_count", 0)
            or _as_dict(previous_run_summary.get("pipeline_health_summary")).get("accepted_source_count", 0)
            or 0
        ),
        "belief_revision_count": int(
            _as_dict(previous_run_summary.get("ingestion_learning_summary")).get("belief_revision_count", 0)
            or 0
        ),
        "report_preflight_passed": bool(
            _as_dict(previous_run_summary.get("ingestion_learning_summary")).get("report_preflight_passed", True)
        ),
        "critical_preflight_failure_count": int(
            _as_dict(previous_run_summary.get("ingestion_learning_summary")).get("critical_preflight_failure_count", 0)
            or 0
        ),
    }
    case_delta_snapshot = _as_dict(_as_dict(previous_run_summary.get("case_delta_summary")).get("current_snapshot"))
    if case_delta_snapshot:
        merged = dict(base_snapshot)
        merged.update(case_delta_snapshot)
        if not merged.get("key_variable_bottlenecks"):
            merged["key_variable_bottlenecks"] = base_snapshot.get("key_variable_bottlenecks", [])
        if not merged.get("cluster_levels"):
            merged["cluster_levels"] = base_snapshot.get("cluster_levels", {})
        if not merged.get("recommended_report_type"):
            merged["recommended_report_type"] = base_snapshot.get("recommended_report_type", "")
        if not merged.get("phase_result"):
            merged["phase_result"] = base_snapshot.get("phase_result", "")
        return merged
    return base_snapshot


def build_case_delta_register(
    runtime: dict[str, Any],
    m20: dict[str, Any],
    m28: dict[str, Any],
    m34: dict[str, Any],
    report_preflight_register: dict[str, Any],
    phase_self_evaluation_register: dict[str, Any],
) -> dict[str, Any]:
    previous_run_summary = _as_dict(runtime.get("previous_run_summary"))
    previous_run_id = str(previous_run_summary.get("run_id", "")).strip()
    current_snapshot = _current_snapshot(
        runtime,
        m20,
        m28,
        m34,
        report_preflight_register,
        phase_self_evaluation_register,
    )
    previous_snapshot = _previous_snapshot(previous_run_summary)

    current_clusters = _as_dict(current_snapshot.get("cluster_levels"))
    previous_clusters = _as_dict(previous_snapshot.get("cluster_levels"))
    clusters_upgraded: list[str] = []
    clusters_downgraded: list[str] = []
    for cluster_name in sorted(set(current_clusters) | set(previous_clusters)):
        current_level = str(current_clusters.get(cluster_name, "")).strip()
        previous_level = str(previous_clusters.get(cluster_name, "")).strip()
        if current_level > previous_level:
            clusters_upgraded.append(cluster_name)
        elif previous_level > current_level:
            clusters_downgraded.append(cluster_name)

    current_blockers = set(_as_list(current_snapshot.get("key_variable_bottlenecks")))
    previous_blockers = set(_as_list(previous_snapshot.get("key_variable_bottlenecks")))
    blockers_removed = sorted(previous_blockers - current_blockers)
    blockers_added = sorted(current_blockers - previous_blockers)

    current_gaps = set(_as_list(current_snapshot.get("mandatory_source_gaps")))
    previous_gaps = set(_as_list(previous_snapshot.get("mandatory_source_gaps")))
    mandatory_source_gaps_resolved = sorted(previous_gaps - current_gaps)
    mandatory_source_gaps_added = sorted(current_gaps - previous_gaps)

    previous_report_type = str(previous_snapshot.get("recommended_report_type", "")).strip()
    current_report_type = str(current_snapshot.get("recommended_report_type", "")).strip()
    previous_phase = str(previous_snapshot.get("phase_result", "")).strip()
    current_phase = str(current_snapshot.get("phase_result", "")).strip()

    progress_signals: list[str] = []
    regression_signals: list[str] = []

    if _report_rank(current_report_type) > _report_rank(previous_report_type):
        progress_signals.append("report_type_upgraded")
    elif _report_rank(current_report_type) < _report_rank(previous_report_type):
        regression_signals.append("report_type_downgraded")

    if clusters_upgraded:
        progress_signals.append("cluster_maturity_up")
    if clusters_downgraded:
        regression_signals.append("cluster_maturity_down")
    if blockers_removed:
        progress_signals.append("blockers_removed")
    if blockers_added:
        regression_signals.append("blockers_added")
    if mandatory_source_gaps_resolved:
        progress_signals.append("mandatory_source_gaps_resolved")
    if mandatory_source_gaps_added:
        regression_signals.append("mandatory_source_gaps_added")

    accepted_source_delta = int(current_snapshot.get("accepted_source_count", 0) or 0) - int(
        previous_snapshot.get("accepted_source_count", 0) or 0
    )
    if accepted_source_delta > 0:
        progress_signals.append("accepted_source_coverage_up")
    elif accepted_source_delta < 0:
        regression_signals.append("accepted_source_coverage_down")

    belief_revision_delta = int(current_snapshot.get("belief_revision_count", 0) or 0) - int(
        previous_snapshot.get("belief_revision_count", 0) or 0
    )
    if belief_revision_delta < 0:
        progress_signals.append("belief_revision_pressure_down")
    elif belief_revision_delta > 0 and previous_run_id:
        regression_signals.append("belief_revision_pressure_up")

    current_preflight_failures = int(current_snapshot.get("critical_preflight_failure_count", 0) or 0)
    previous_preflight_failures = int(previous_snapshot.get("critical_preflight_failure_count", 0) or 0)
    if current_preflight_failures < previous_preflight_failures:
        progress_signals.append("preflight_failures_down")
    elif current_preflight_failures > previous_preflight_failures:
        regression_signals.append("preflight_failures_up")

    if previous_phase and current_phase and previous_phase != current_phase:
        if current_phase == "resolved" or (current_phase == "partially_resolved" and previous_phase == "unresolved"):
            progress_signals.append("phase_self_evaluation_up")
        elif previous_phase == "resolved" or (previous_phase == "partially_resolved" and current_phase == "unresolved"):
            regression_signals.append("phase_self_evaluation_down")

    net_progress_state = _net_progress_state(progress_signals, regression_signals, previous_run_id)

    return {
        "previous_run_id": previous_run_id,
        "current_run_id": str(runtime.get("run_id", "")).strip(),
        "previous_snapshot": previous_snapshot,
        "current_snapshot": current_snapshot,
        "report_type_transition": {
            "from": previous_report_type,
            "to": current_report_type,
            "changed": previous_report_type != current_report_type,
        },
        "clusters_upgraded": clusters_upgraded,
        "clusters_downgraded": clusters_downgraded,
        "blockers_removed": blockers_removed,
        "blockers_added": blockers_added,
        "mandatory_source_gaps_resolved": mandatory_source_gaps_resolved,
        "mandatory_source_gaps_added": mandatory_source_gaps_added,
        "accepted_source_count_delta": accepted_source_delta,
        "belief_revision_count_delta": belief_revision_delta,
        "progress_signals": progress_signals,
        "regression_signals": regression_signals,
        "net_progress_state": net_progress_state,
    }


def _yield_score(row: dict[str, Any]) -> int:
    score = 0
    if bool(row.get("queried", False)):
        score += 1
    if bool(row.get("found", False)):
        score += 2
    score += min(len(_as_list(row.get("fields_extracted"))), 4)
    score -= min(len(_as_list(row.get("missing"))), 3)
    note = str(row.get("support_note", "")).lower()
    if "identity only" in note:
        score -= 1
    return score


def _yield_band(row: dict[str, Any], score: int) -> str:
    note = str(row.get("support_note", "")).lower()
    if "identity only" in note and not _as_list(row.get("fields_extracted")):
        return "identity_only"
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    if bool(row.get("queried", False)):
        return "low"
    return "not_executed"


def _recommended_acquisition_mode(entry: dict[str, Any]) -> str:
    static_success_count = int(entry.get("static_success_count", 0) or 0)
    static_failure_count = int(entry.get("static_failure_count", 0) or 0)
    browser_success_count = int(entry.get("browser_success_count", 0) or 0)
    browser_failure_count = int(entry.get("browser_failure_count", 0) or 0)
    if browser_success_count > 0 and static_failure_count >= max(static_success_count, 1):
        return "prefer_browser"
    if browser_failure_count >= 2 and browser_success_count == 0:
        return "avoid_browser"
    if static_success_count > 0 and browser_success_count == 0:
        return "prefer_static"
    return "undecided"


def _build_acquisition_yield_entry(
    row: dict[str, Any],
    previous_entry: dict[str, Any],
) -> dict[str, Any]:
    selected_mode = str(row.get("selected_acquisition_mode", "")).strip()
    static_probe_attempted = bool(row.get("static_probe_attempted", False))
    static_usable = bool(row.get("static_usable", False))
    browser_attempted = bool(row.get("browser_attempted", False))
    browser_success = bool(row.get("browser_success", False))
    browser_failure = bool(row.get("browser_failure", False))
    browser_justified = bool(row.get("browser_justified", False) and browser_success)
    browser_waste = bool(browser_failure and not browser_success)

    entry = {
        "selected_acquisition_mode": selected_mode or str(previous_entry.get("selected_acquisition_mode", "")).strip(),
        "static_success_count": int(previous_entry.get("static_success_count", 0) or 0) + (1 if static_usable else 0),
        "static_failure_count": int(previous_entry.get("static_failure_count", 0) or 0) + (
            1 if static_probe_attempted and not static_usable else 0
        ),
        "browser_success_count": int(previous_entry.get("browser_success_count", 0) or 0) + (1 if browser_success else 0),
        "browser_failure_count": int(previous_entry.get("browser_failure_count", 0) or 0) + (1 if browser_failure else 0),
        "browser_justified_count": int(previous_entry.get("browser_justified_count", 0) or 0) + (
            1 if browser_justified else 0
        ),
        "browser_waste_count": int(previous_entry.get("browser_waste_count", 0) or 0) + (1 if browser_waste else 0),
        "latest_static_render_mode": str(row.get("static_render_mode", "")).strip(),
        "latest_browser_attempt_status": str(row.get("browser_attempt_status", "")).strip(),
    }
    entry["recommended_acquisition_mode"] = _recommended_acquisition_mode(entry)
    return entry


def build_source_yield_memory(
    source_family_coverage_table: list[dict[str, Any]],
    previous_run_summary: dict[str, Any],
) -> dict[str, Any]:
    previous_rows = _as_dict(_as_dict(previous_run_summary.get("source_yield_memory_summary")).get("by_source_family"))
    previous_acquisition_rows = _as_dict(
        _as_dict(
            _as_dict(previous_run_summary.get("source_yield_memory_summary")).get(
                "source_acquisition_yield_memory"
            )
        ).get("by_source_family")
    )
    by_source_family: dict[str, Any] = {}
    acquisition_by_source_family: dict[str, Any] = {}
    productive_sources: list[str] = []
    low_yield_sources: list[str] = []
    identity_only_sources: list[str] = []
    browser_justified_source_families: list[str] = []
    browser_waste_source_families: list[str] = []
    static_only_source_families: list[str] = []
    static_success_count = 0
    static_failure_count = 0
    browser_success_count = 0
    browser_failure_count = 0

    for row in source_family_coverage_table:
        source_family = str(row.get("source_family", "")).strip()
        if not source_family:
            continue
        score = _yield_score(row)
        band = _yield_band(row, score)
        previous_score = int(_as_dict(previous_rows.get(source_family)).get("yield_score", 0) or 0)
        trend = "new_source"
        if source_family in previous_rows:
            if score > previous_score:
                trend = "improved"
            elif score < previous_score:
                trend = "degraded"
            else:
                trend = "unchanged"
        entry = {
            "source_family": source_family,
            "queried": bool(row.get("queried", False)),
            "found": bool(row.get("found", False)),
            "authority": str(row.get("authority", "")).strip(),
            "scope": str(row.get("scope", "")).strip(),
            "fields_extracted": _unique_strings(_as_list(row.get("fields_extracted"))),
            "missing": _unique_strings(_as_list(row.get("missing"))),
            "yield_score": score,
            "yield_band": band,
            "trend": trend,
        }
        by_source_family[source_family] = entry
        if band in {"high", "medium"}:
            productive_sources.append(source_family)
        if band == "low":
            low_yield_sources.append(source_family)
        if band == "identity_only":
            identity_only_sources.append(source_family)

        acquisition_entry = _build_acquisition_yield_entry(
            row,
            _as_dict(previous_acquisition_rows.get(source_family)),
        )
        acquisition_by_source_family[source_family] = acquisition_entry
        if acquisition_entry["recommended_acquisition_mode"] == "prefer_browser":
            browser_justified_source_families.append(source_family)
        if acquisition_entry["recommended_acquisition_mode"] == "avoid_browser":
            browser_waste_source_families.append(source_family)
        if acquisition_entry["recommended_acquisition_mode"] == "prefer_static":
            static_only_source_families.append(source_family)
        if bool(row.get("static_usable", False)):
            static_success_count += 1
        elif bool(row.get("static_probe_attempted", False)):
            static_failure_count += 1
        if bool(row.get("browser_success", False)):
            browser_success_count += 1
        elif bool(row.get("browser_failure", False)):
            browser_failure_count += 1

    return {
        "by_source_family": by_source_family,
        "source_acquisition_yield_memory": {
            "by_source_family": acquisition_by_source_family,
            "browser_justified_source_families": browser_justified_source_families[:6],
            "browser_waste_source_families": browser_waste_source_families[:6],
            "static_only_source_families": static_only_source_families[:6],
        },
        "static_success_failure_summary": {
            "success_count": static_success_count,
            "failure_count": static_failure_count,
            "attempted_count": static_success_count + static_failure_count,
        },
        "browser_success_failure_summary": {
            "success_count": browser_success_count,
            "failure_count": browser_failure_count,
            "attempted_count": browser_success_count + browser_failure_count,
        },
        "productive_source_count": len(productive_sources),
        "productive_sources": productive_sources[:6],
        "low_yield_sources": low_yield_sources[:6],
        "identity_only_sources": identity_only_sources[:6],
        "browser_justified_source_families": browser_justified_source_families[:6],
        "browser_waste_source_families": browser_waste_source_families[:6],
        "static_only_source_families": static_only_source_families[:6],
        "sources_evaluated": len(by_source_family),
    }


def build_next_ingestion_priority_update(
    m12: dict[str, Any],
    m14: dict[str, Any],
    m20: dict[str, Any],
    m28: dict[str, Any],
    case_delta_register: dict[str, Any],
    source_yield_memory_register: dict[str, Any],
) -> dict[str, Any]:
    priorities: list[dict[str, Any]] = []
    seen_targets: set[str] = set()

    def _push(action_type: str, target: str, reason: str, expected_unlock: str, basis: str) -> None:
        key = f"{action_type}:{target}".strip()
        if not target or key in seen_targets:
            return
        seen_targets.add(key)
        priorities.append(
            {
                "priority_rank": len(priorities) + 1,
                "action_type": action_type,
                "target": target,
                "reason": reason,
                "expected_unlock": expected_unlock,
                "basis": basis,
            }
        )

    routing_plan_compliance = _as_dict(m28.get("routing_plan_compliance"))
    for source_key in _unique_strings(_as_list(routing_plan_compliance.get("mandatory_sources_missing_from_executor"))):
        _push(
            "execute_missing_mandatory_source",
            source_key,
            "Routing plan still has a mandatory execution gap.",
            "Restores required public-source coverage before the next admissibility pass.",
            "routing_plan_compliance",
        )

    for row in _as_list(m14.get("minimum_evidence_unlock_map")):
        if len(priorities) >= 7:
            break
        priority = str(row.get("priority", "")).strip().lower()
        evidence_item = str(row.get("evidence_item", "")).strip()
        if priority not in {"critical", "high"} or not evidence_item:
            continue
        unlocks = ", ".join(_unique_strings(_as_list(row.get("unlocks"))[:3]))
        _push(
            "request_missing_evidence",
            evidence_item,
            str(row.get("why_needed", "")).strip() or "Missing evidence is still blocking defensible decision progress.",
            unlocks or "Improves admissible decision range.",
            str(row.get("source", "")).strip() or "minimum_evidence_unlock_map",
        )

    low_yield_sources = _unique_strings(_as_list(source_yield_memory_register.get("low_yield_sources")))
    identity_only_sources = _unique_strings(_as_list(source_yield_memory_register.get("identity_only_sources")))
    browser_waste_sources = _unique_strings(_as_list(source_yield_memory_register.get("browser_waste_source_families")))
    for source_key in low_yield_sources[:2] + identity_only_sources[:2]:
        if len(priorities) >= 7:
            break
        source_row = _as_dict(_as_dict(source_yield_memory_register.get("by_source_family")).get(source_key))
        _push(
            "improve_anchor_and_requery",
            source_key,
            "Current source execution produced weak or identity-only coverage.",
            "Can raise source yield on the next ingest with better anchors or scope refinement.",
            source_row.get("yield_band", "source_yield_memory"),
        )

    for source_key in browser_waste_sources[:2]:
        if len(priorities) >= 7:
            break
        _push(
            "refine_anchor_before_browser_retry",
            source_key,
            "Browser fallback is consuming discovery budget without producing admissible public-page yield.",
            "Tightens the anchor or escalates to operator evidence instead of repeating low-value browser attempts.",
            "browser_acquisition_yield_memory",
        )

    for row in _as_list(m20.get("belief_revision_register")):
        if len(priorities) >= 7:
            break
        if str(row.get("recommended_action", "")).strip() != "upgrade_candidate":
            continue
        case_name = str(row.get("case_name", "")).strip() or str(row.get("case_id", "")).strip()
        _push(
            "re_score_upgrade_candidate",
            case_name,
            "New evidence may justify an upward re-score on the next ingest.",
            "Potentially upgrades claim admissibility or report posture.",
            "belief_revision_register",
        )

    net_progress_state = str(case_delta_register.get("net_progress_state", "")).strip()
    return {
        "priorities": priorities,
        "priority_count": len(priorities),
        "top_priority_action": priorities[0]["action_type"] if priorities else "",
        "case_progress_state": net_progress_state,
    }


def build_ingestion_learning_register(
    runtime: dict[str, Any],
    case_delta_register: dict[str, Any],
    source_yield_memory_register: dict[str, Any],
    next_ingestion_priority_update: dict[str, Any],
    report_preflight_register: dict[str, Any],
    m20: dict[str, Any],
) -> dict[str, Any]:
    previous_run_id = str(case_delta_register.get("previous_run_id", "")).strip()
    summary = {
        "current_run_id": str(runtime.get("run_id", "")).strip(),
        "previous_run_id": previous_run_id,
        "net_progress_state": str(case_delta_register.get("net_progress_state", "")).strip(),
        "productive_source_count": int(source_yield_memory_register.get("productive_source_count", 0) or 0),
        "sources_evaluated": int(source_yield_memory_register.get("sources_evaluated", 0) or 0),
        "browser_justified_source_count": len(
            _as_list(source_yield_memory_register.get("browser_justified_source_families"))
        ),
        "browser_waste_source_count": len(
            _as_list(source_yield_memory_register.get("browser_waste_source_families"))
        ),
        "priority_count": int(next_ingestion_priority_update.get("priority_count", 0) or 0),
        "top_priority_action": str(next_ingestion_priority_update.get("top_priority_action", "")).strip(),
        "belief_revision_count": len(_as_list(m20.get("belief_revision_register"))),
        "report_preflight_passed": bool(report_preflight_register.get("passed", False)),
        "critical_preflight_failure_count": int(report_preflight_register.get("critical_failure_count", 0) or 0),
    }
    return {
        "summary": summary,
        "case_delta": case_delta_register,
        "source_yield_memory": source_yield_memory_register,
        "next_ingestion_priority_update": next_ingestion_priority_update,
    }
