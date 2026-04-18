from pathlib import Path

from engines.reference_comparator import compare_report_to_references
from engines.report_normalizer import normalize_report


ROOT = Path(__file__).resolve().parents[1]


def test_reference_comparator_reports_quality_gaps_not_normative_violations():
    report = normalize_report(ROOT / "sample_data/reports/example_report.md")
    gaps = compare_report_to_references(report, [ROOT / "sample_data/references"])

    assert gaps
    assert all("not a phase violation" in gap.gap_description for gap in gaps)

