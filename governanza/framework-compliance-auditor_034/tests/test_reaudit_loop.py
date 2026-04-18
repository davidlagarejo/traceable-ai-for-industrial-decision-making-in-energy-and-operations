import json
from pathlib import Path

from engines.re_audit_loop import compare_audit_runs


def test_reaudit_comparison_tracks_resolved_and_new_findings(tmp_path: Path):
    previous = tmp_path / "previous"
    current = tmp_path / "current"
    previous.mkdir()
    current.mkdir()

    (previous / "audit_scorecard.json").write_text(
        json.dumps(
            {
                "audit_run_id": "run-1",
                "overall_compliance_gate": "fail",
                "overall_quality_gate": "fail",
                "dimensions": [{"name": "phase1_scope_compliance", "score": 50}],
            }
        ),
        encoding="utf-8",
    )
    (previous / "claim_violation_register.json").write_text(
        json.dumps([{"finding_id": "old"}, {"finding_id": "same"}]),
        encoding="utf-8",
    )
    (current / "audit_scorecard.json").write_text(
        json.dumps(
            {
                "audit_run_id": "run-2",
                "overall_compliance_gate": "pass",
                "overall_quality_gate": "warn",
                "dimensions": [{"name": "phase1_scope_compliance", "score": 85}],
            }
        ),
        encoding="utf-8",
    )
    (current / "claim_violation_register.json").write_text(
        json.dumps([{"finding_id": "same"}, {"finding_id": "new"}]),
        encoding="utf-8",
    )

    comparison = compare_audit_runs(previous_output_dir=previous, current_output_dir=current)

    assert comparison.resolved_findings == ["old"]
    assert comparison.unresolved_findings == ["same"]
    assert comparison.newly_introduced_findings == ["new"]
    assert comparison.score_delta["phase1_scope_compliance"] == 35
    assert comparison.threshold_met is True

