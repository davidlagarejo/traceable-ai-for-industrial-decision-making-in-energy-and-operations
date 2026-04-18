from __future__ import annotations

from models.datatypes import Claim, NormalizedReport
from models.enums import ClaimType, ConfidenceLanguageLevel


HIGH_STAKES_TYPES = {
    ClaimType.CAUSAL,
    ClaimType.RECOMMENDATION,
    ClaimType.SAVINGS,
    ClaimType.VERIFICATION_LIKE,
    ClaimType.COMPLIANCE_LIKE,
}

HIGH_STRENGTH_LEVELS = {
    ConfidenceLanguageLevel.HIGH,
    ConfidenceLanguageLevel.ABSOLUTE,
    ConfidenceLanguageLevel.VERIFICATION_GRADE,
    ConfidenceLanguageLevel.COMPLIANCE_GRADE,
}


def evidence_coverage_metrics(report: NormalizedReport) -> dict[str, float | int]:
    claims = report.claims
    if not claims:
        return {
            "claim_count": 0,
            "claims_with_evidence": 0,
            "evidence_coverage": 0.0,
            "high_stakes_claims": 0,
            "high_stakes_with_evidence": 0,
            "high_stakes_evidence_coverage": 0.0,
        }

    with_evidence = [claim for claim in claims if claim.evidence_reference_presence]
    high_stakes = [claim for claim in claims if is_high_stakes_claim(claim)]
    high_stakes_with_evidence = [claim for claim in high_stakes if claim.evidence_reference_presence]
    return {
        "claim_count": len(claims),
        "claims_with_evidence": len(with_evidence),
        "evidence_coverage": len(with_evidence) / len(claims),
        "high_stakes_claims": len(high_stakes),
        "high_stakes_with_evidence": len(high_stakes_with_evidence),
        "high_stakes_evidence_coverage": (
            len(high_stakes_with_evidence) / len(high_stakes) if high_stakes else 1.0
        ),
    }


def is_high_stakes_claim(claim: Claim) -> bool:
    return claim.claim_type in HIGH_STAKES_TYPES or claim.confidence_language_level in HIGH_STRENGTH_LEVELS

