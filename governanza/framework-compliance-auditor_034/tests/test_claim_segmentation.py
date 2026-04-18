from models.datatypes import ReportUnit, SourceLocation
from models.enums import ClaimType, ConfidenceLanguageLevel, SourceUnitType, ViolationType
from parsers.claim_segmenter import extract_claims


def test_claim_segmentation_detects_auditable_overclaim():
    unit = ReportUnit(
        unit_id="unit-1",
        unit_type=SourceUnitType.PARAGRAPH,
        text="The facility is verified compliant and will achieve 18% savings.",
        parent_section_id="executive",
        location=SourceLocation(file_path="report.md", section_path=["Executive Summary"]),
    )

    claims = extract_claims([unit], citations=[], tables=[], phase_ids=["phase1", "phase4"])

    assert len(claims) == 1
    claim = claims[0]
    assert claim.claim_type == ClaimType.SAVINGS
    assert claim.confidence_language_level == ConfidenceLanguageLevel.VERIFICATION_GRADE
    assert ViolationType.SEMANTIC_OVERREACH in claim.suspected_violation_flags

