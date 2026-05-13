"""V6 P2 — source_execution_auditor tests."""
from __future__ import annotations

from runtime_orchestrator.source_execution_auditor import (
    audit_source_execution,
    gaps_block_render,
)


def _compliance(
    total: int = 10,
    missing: list[str] | None = None,
    rows: list[dict] | None = None,
) -> dict:
    return {
        "total_routed_sources": total,
        "mandatory_sources_missing_from_executor": missing or [],
        "rows": rows or [],
    }


def _row(key: str, priority: str = "mandatory", status: str = "attempted_found") -> dict:
    return {"source_key": key, "priority": priority, "status": status}


# ── empty / clean cases ────────────────────────────────────────────


def test_audit_no_missing_passes():
    rows = [_row("doe_iac"), _row("eia_mecs"), _row("ashrae_climate")]
    report = audit_source_execution(_compliance(missing=[], rows=rows))
    assert report.passed
    assert report.mandatory_missing == 0
    assert report.executed_ratio == 1.0
    assert gaps_block_render(report) is False


def test_audit_no_routing_plan_compliance_passes():
    report = audit_source_execution(None)
    assert report.passed
    assert report.mandatory_missing == 0


# ── unjustified gaps block ─────────────────────────────────────────


def test_unjustified_gap_blocks():
    rows = [
        _row("doe_iac", status="not_executed_by_executor"),
        _row("eia_mecs"),
    ]
    report = audit_source_execution(_compliance(missing=["doe_iac"], rows=rows))
    assert not report.passed
    assert len(report.unjustified_gaps) == 1
    assert report.unjustified_gaps[0].source_key == "doe_iac"
    assert gaps_block_render(report) is True


def test_multiple_unjustified_gaps_all_listed():
    rows = [_row("a", status="not_executed_by_executor"),
            _row("b", status="not_executed_by_executor")]
    report = audit_source_execution(_compliance(missing=["a", "b"], rows=rows))
    assert not report.passed
    assert len(report.unjustified_gaps) == 2


# ── justification: skip_reason ─────────────────────────────────────


def test_explicit_skip_reason_justifies_gap():
    rows = [_row("doe_iac", status="not_executed_by_executor")]
    compliance = _compliance(missing=["doe_iac"], rows=rows)
    routing_plan = {"skip_reasons": {"doe_iac": "asset is residential — DOE IAC not applicable"}}
    report = audit_source_execution(compliance, routing_plan=routing_plan)
    assert report.passed
    assert len(report.justified_gaps) == 1
    assert report.justified_gaps[0].justification_kind == "skip_reason"
    assert "residential" in report.justified_gaps[0].justification_detail


# ── justification: fallback event ──────────────────────────────────


def test_coverage_gap_event_justifies_gap():
    rows = [_row("ashrae_handbook_refrigeration", status="not_executed_by_executor")]
    compliance = _compliance(missing=["ashrae_handbook_refrigeration"], rows=rows)
    fallback_events = [
        {
            "motor_id": "motor_028",
            "kind": "source_coverage_gap_logged",
            "reason": "ASHRAE handbook API offline at run time",
            "metadata": {"source_keys": ["ashrae_handbook_refrigeration"]},
        }
    ]
    report = audit_source_execution(
        compliance, fallback_events=fallback_events,
    )
    assert report.passed
    assert report.justified_gaps[0].justification_kind == "coverage_gap_logged"


def test_coverage_gap_event_with_wrong_key_does_not_justify():
    rows = [_row("doe_iac", status="not_executed_by_executor")]
    compliance = _compliance(missing=["doe_iac"], rows=rows)
    fallback_events = [
        {
            "motor_id": "motor_028",
            "kind": "source_coverage_gap_logged",
            "metadata": {"source_keys": ["different_source"]},
        }
    ]
    report = audit_source_execution(compliance, fallback_events=fallback_events)
    assert not report.passed


# ── justification: non-US jurisdiction ─────────────────────────────


def test_non_us_source_keys_self_justify():
    """Per user direction (2026-05-13): case discovery is US-only.
    UPME/CREG/IDAE/Fenercom etc. are catalog-only — no runtime fetcher.
    These should auto-justify."""
    rows = [
        _row("upme_guia_alimentos", status="not_executed_by_executor"),
        _row("creg_resolucion_075_2021", status="not_executed_by_executor"),
        _row("idae_bombas_calor", status="not_executed_by_executor"),
        _row("fenercom_guia_iluminacion", status="not_executed_by_executor"),
        _row("olade_get_2022", status="not_executed_by_executor"),
    ]
    missing = [r["source_key"] for r in rows]
    report = audit_source_execution(_compliance(missing=missing, rows=rows))
    assert report.passed
    assert len(report.justified_gaps) == 5
    for gap in report.justified_gaps:
        assert gap.justification_kind == "non_us_jurisdiction"


def test_us_source_does_not_get_non_us_justification():
    rows = [_row("doe_better_plants", status="not_executed_by_executor")]
    report = audit_source_execution(_compliance(missing=["doe_better_plants"], rows=rows))
    assert not report.passed
    assert len(report.unjustified_gaps) == 1


# ── mixed scenarios ────────────────────────────────────────────────


def test_mixed_justified_and_unjustified():
    rows = [
        _row("upme_pen_2020_2050", status="not_executed_by_executor"),  # non-US auto
        _row("doe_iac", status="not_executed_by_executor"),             # unjustified
        _row("ashrae_climate", status="not_executed_by_executor"),      # skip_reason
        _row("eia_mecs", status="attempted_found"),                     # not missing
    ]
    compliance = _compliance(missing=["upme_pen_2020_2050", "doe_iac", "ashrae_climate"], rows=rows)
    routing_plan = {"skip_reasons": {"ashrae_climate": "asset has no thermal envelope"}}
    report = audit_source_execution(compliance, routing_plan=routing_plan)
    assert not report.passed
    assert len(report.justified_gaps) == 2
    assert len(report.unjustified_gaps) == 1
    assert report.unjustified_gaps[0].source_key == "doe_iac"


# ── executed_ratio ─────────────────────────────────────────────────


def test_executed_ratio_partial():
    rows = [
        _row("a", status="attempted_found"),
        _row("b", status="attempted_found"),
        _row("c", status="not_executed_by_executor"),
        _row("d", status="not_executed_by_executor"),
    ]
    report = audit_source_execution(_compliance(missing=["c", "d"], rows=rows))
    assert report.executed_ratio == 0.5


def test_executed_ratio_no_mandatory_yields_one():
    rows = [_row("a", priority="high_priority")]
    report = audit_source_execution(_compliance(missing=[], rows=rows))
    assert report.executed_ratio == 1.0
