from pathlib import Path

from contracts.loader import compile_contract
from engines.phase_compliance_engine import evaluate_phase_compliance
from engines.report_normalizer import normalize_report
from models.enums import ViolationType


ROOT = Path(__file__).resolve().parents[1]


def test_phase_compliance_flags_verification_language_against_sample_contract():
    compiled = compile_contract([ROOT / "sample_data/contracts"])
    report = normalize_report(
        ROOT / "sample_data/reports/example_report.md",
        phase_ids=[phase.phase_id for phase in compiled.phases],
    )

    evaluations = evaluate_phase_compliance(report, compiled.phases)
    findings = [finding for evaluation in evaluations for finding in evaluation.findings]

    assert findings
    assert any(
        finding.violation_type == ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION
        for finding in findings
    )

