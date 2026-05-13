"""V6 P7 — claim_synchronization_auditor tests."""
from __future__ import annotations

from runtime_orchestrator.claim_synchronization_auditor import (
    audit_claim_synchronization,
    claim_sync_blocks_render,
)


def _make_outputs(*, ids: list[str], gov_count: int | None = None,
                  m025_extra: list[str] | None = None) -> dict:
    """Build the 5 motor outputs with given claim_ids."""
    return {
        "motor_014_output": {
            "inference_records": [{"case_id": cid} for cid in ids],
        },
        "motor_034_output": {
            "claim_permission_register": [{"claim_name": cid} for cid in ids],
        },
        "motor_054_output": {
            "congruence_claim_contract_register": [{"claim_id": cid} for cid in ids],
        },
        "motor_025_output": {
            "epistemic_status_register": [
                {"output_id": cid} for cid in (ids + (m025_extra or []))
            ],
        },
        "motor_016_output": {
            "report_package": {
                "governance_summary": {
                    "claim_count": gov_count if gov_count is not None else len(ids),
                },
            },
        },
    }


# ── Clean sync ──────────────────────────────────────────────────────


def test_audit_all_5_motors_in_sync_passes():
    outputs = _make_outputs(ids=["CL-1", "CL-2", "CL-3"])
    report = audit_claim_synchronization(**outputs)
    assert report.consistent
    assert report.expected_baseline == 3
    assert report.motor_014_count == 3
    assert claim_sync_blocks_render(report) is False


def test_audit_motor_025_with_extra_rows_OK():
    """motor_025 may legitimately have extra status rows (one per output
    type). Extra rows beyond claim count are NOT a divergence."""
    outputs = _make_outputs(
        ids=["CL-1", "CL-2"],
        m025_extra=["O-3", "O-4"],  # extra output_ids beyond claims
    )
    report = audit_claim_synchronization(**outputs)
    assert report.consistent


def test_audit_governance_summary_count_higher_OK():
    """governance_summary count can be higher than claim base."""
    outputs = _make_outputs(ids=["CL-1", "CL-2"], gov_count=5)
    report = audit_claim_synchronization(**outputs)
    assert report.consistent


# ── Divergence detection ───────────────────────────────────────────


def test_audit_motor_014_vs_034_divergence_blocks():
    """motor_034 missing one claim → divergence."""
    outputs = _make_outputs(ids=["CL-1", "CL-2", "CL-3"])
    # Remove one from motor_034
    outputs["motor_034_output"]["claim_permission_register"] = [
        {"claim_name": "CL-1"}, {"claim_name": "CL-2"}
    ]
    report = audit_claim_synchronization(**outputs)
    assert not report.consistent
    assert claim_sync_blocks_render(report)
    assert "motor_014_not_in_034" in report.divergent_ids_by_motor


def test_audit_motor_054_extra_claims_blocks():
    """motor_054 has MORE claims than motor_014 → divergence."""
    outputs = _make_outputs(ids=["CL-1", "CL-2"])
    outputs["motor_054_output"]["congruence_claim_contract_register"].append(
        {"claim_id": "CL-3-PHANTOM"}
    )
    report = audit_claim_synchronization(**outputs)
    assert not report.consistent


def test_audit_motor_025_fewer_rows_blocks():
    """motor_025 with FEWER rows than expected → block."""
    outputs = _make_outputs(ids=["CL-1", "CL-2", "CL-3"])
    outputs["motor_025_output"]["epistemic_status_register"] = [
        {"output_id": "CL-1"}, {"output_id": "CL-2"},  # missing CL-3
    ]
    report = audit_claim_synchronization(**outputs)
    assert not report.consistent


def test_audit_governance_summary_fewer_blocks():
    """governance_summary.claim_count LOWER than expected → block."""
    outputs = _make_outputs(ids=["CL-1", "CL-2", "CL-3"], gov_count=2)
    report = audit_claim_synchronization(**outputs)
    assert not report.consistent


# ── Empty / missing inputs ─────────────────────────────────────────


def test_audit_all_empty_inputs_returns_consistent():
    """Zero claims everywhere = consistent (trivially)."""
    report = audit_claim_synchronization()
    assert report.consistent
    assert report.expected_baseline == 0
    assert report.motor_014_count == 0


def test_audit_partial_inputs_use_zero_baseline():
    report = audit_claim_synchronization(
        motor_014_output={"inference_records": []},
        motor_034_output={"claim_permission_register": []},
    )
    assert report.consistent


# ── Report fields ──────────────────────────────────────────────────


def test_report_carries_all_motor_counts():
    outputs = _make_outputs(ids=["CL-1", "CL-2"])
    report = audit_claim_synchronization(**outputs)
    assert report.motor_014_count == 2
    assert report.motor_034_count == 2
    assert report.motor_054_count == 2
    assert report.motor_025_count == 2
    assert report.governance_summary_count == 2


def test_report_divergence_breakdown_per_motor():
    """divergence_breakdown shows delta per motor."""
    outputs = _make_outputs(ids=["CL-1", "CL-2", "CL-3"])
    outputs["motor_034_output"]["claim_permission_register"] = [
        {"claim_name": "CL-1"}, {"claim_name": "CL-2"}
    ]  # -1
    report = audit_claim_synchronization(**outputs)
    assert report.divergence_breakdown["motor_034_claim_permission"] == -1
    assert report.max_divergence == 1


def test_report_divergent_ids_shows_missing_claims():
    outputs = _make_outputs(ids=["CL-1", "CL-2", "CL-3"])
    outputs["motor_034_output"]["claim_permission_register"] = [
        {"claim_name": "CL-1"}
    ]
    report = audit_claim_synchronization(**outputs)
    missing = report.divergent_ids_by_motor.get("motor_014_not_in_034", [])
    assert "CL-2" in missing
    assert "CL-3" in missing
