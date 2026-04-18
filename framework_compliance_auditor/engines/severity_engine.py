from __future__ import annotations

from models.datatypes import Claim, PhaseRule, SourceLocation
from models.enums import ClaimType, ConfidenceLanguageLevel, RuleKind, Severity, ViolationType


EXECUTIVE_SECTION_TERMS = {
    "board",
    "conclusion",
    "decision",
    "executive",
    "finding",
    "recommendation",
    "summary",
}


BASE_SEVERITY = {
    ViolationType.SEMANTIC_OVERREACH: Severity.HIGH,
    ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION: Severity.HIGH,
    ViolationType.CAUSAL_CLOSURE_WITHOUT_SUPPORT: Severity.MEDIUM,
    ViolationType.RECOMMENDATION_ESCALATION: Severity.HIGH,
    ViolationType.NARRATIVE_STRENGTHENING: Severity.MEDIUM,
    ViolationType.UNCERTAINTY_SUPPRESSION: Severity.HIGH,
    ViolationType.REPORT_PACKAGE_INFLATION: Severity.HIGH,
    ViolationType.BENCHMARK_TO_SITE_SLIPPAGE: Severity.MEDIUM,
    ViolationType.PROXY_TO_HARD_CLAIM_SLIPPAGE: Severity.HIGH,
    ViolationType.MISSING_VALIDATION_CAVEAT: Severity.MEDIUM,
    ViolationType.HARDENING_PATH_OMISSION: Severity.MEDIUM,
    ViolationType.TRACEABILITY_WEAKENING: Severity.MEDIUM,
    ViolationType.CONTRACT_RULE_MATCH: Severity.MEDIUM,
}


def classify_severity(
    violation_type: ViolationType,
    claim: Claim | None,
    *,
    rule: PhaseRule | None = None,
    location: SourceLocation | None = None,
) -> Severity:
    severity = BASE_SEVERITY.get(violation_type, Severity.MEDIUM)
    if rule and rule.kind in {
        RuleKind.FORBIDDEN,
        RuleKind.HARD_BOUNDARY,
        RuleKind.ESCALATION_BOUNDARY,
        RuleKind.VERIFICATION_BOUNDARY,
    }:
        severity = _raise_to_at_least(severity, Severity.HIGH)
    if claim:
        if claim.confidence_language_level in {
            ConfidenceLanguageLevel.VERIFICATION_GRADE,
            ConfidenceLanguageLevel.COMPLIANCE_GRADE,
        }:
            severity = _raise_to_at_least(severity, Severity.HIGH)
        if claim.confidence_language_level == ConfidenceLanguageLevel.ABSOLUTE and not claim.evidence_reference_presence:
            severity = _raise_to_at_least(severity, Severity.HIGH)
        if claim.claim_type in {ClaimType.SAVINGS, ClaimType.COMPLIANCE_LIKE} and not claim.evidence_reference_presence:
            severity = _raise_to_at_least(severity, Severity.HIGH)
        if _is_executive_location(claim.source_location or location):
            if severity == Severity.HIGH and violation_type in {
                ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION,
                ViolationType.RECOMMENDATION_ESCALATION,
                ViolationType.SEMANTIC_OVERREACH,
                ViolationType.UNCERTAINTY_SUPPRESSION,
            }:
                return Severity.CRITICAL
            severity = _raise_to_at_least(severity, Severity.MEDIUM)
    return severity


def _is_executive_location(location: SourceLocation | None) -> bool:
    if not location:
        return False
    path = " ".join(location.section_path).lower()
    return any(term in path for term in EXECUTIVE_SECTION_TERMS)


def _raise_to_at_least(current: Severity, floor: Severity) -> Severity:
    order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
    return order[max(order.index(current), order.index(floor))]

