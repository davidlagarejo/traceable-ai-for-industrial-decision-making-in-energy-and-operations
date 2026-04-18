from pathlib import Path

from engines.reference_comparator import build_reference_anchor_profiles, compare_report_to_references
from engines.report_normalizer import normalize_report


ROOT = Path(__file__).resolve().parents[1]


def test_reference_comparator_reports_quality_gaps_not_normative_violations():
    report = normalize_report(ROOT / "sample_data/reports/example_report.md")
    gaps = compare_report_to_references(report, [ROOT / "sample_data/references"])

    assert gaps
    assert all("not a phase violation" in gap.gap_description for gap in gaps)


def test_reference_anchor_profiles_preserve_each_document_strengths():
    profiles = build_reference_anchor_profiles([ROOT / "sample_data/references"])

    assert len(profiles) == 1
    assert profiles[0].document_id.startswith("reference_anchor-")
    assert profiles[0].strongest_dimensions
    assert profiles[0].useful_as
