from __future__ import annotations

import re

from engines.severity_engine import classify_severity
from models.datatypes import AuditFinding, Claim, PhaseContract, PhaseRule
from models.enums import (
    ClaimType,
    ComplianceVerdict,
    ConfidenceLanguageLevel,
    FixAction,
    RuleCategory,
    RuleKind,
    ViolationType,
)


BOUNDARY_KINDS = {
    RuleKind.FORBIDDEN,
    RuleKind.HARD_BOUNDARY,
    RuleKind.ESCALATION_BOUNDARY,
    RuleKind.SEMANTIC_OVERREACH,
    RuleKind.CERTAINTY_CONSTRAINT,
    RuleKind.VERIFICATION_BOUNDARY,
}


def audit_claim_against_phase(claim: Claim, phase: PhaseContract) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    phase_text = " ".join(rule.text for rule in phase.rules).lower()

    for flag in claim.suspected_violation_flags:
        if not _flag_relevant_to_phase(flag, phase_text, phase):
            continue
        rule = _best_matching_rule(claim, phase, flag)
        findings.append(_build_finding(claim, phase, rule, flag))

    findings.extend(_audit_contract_rule_matches(claim, phase))
    findings.extend(_audit_required_traceability(claim, phase))
    findings.extend(_audit_required_caveats(claim, phase))
    return _dedupe_findings(findings)


def _audit_contract_rule_matches(claim: Claim, phase: PhaseContract) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    claim_text = claim.normalized_text.lower()
    for rule in phase.rules:
        if rule.kind not in BOUNDARY_KINDS:
            continue
        if rule.kind in {RuleKind.EXAMPLE, RuleKind.NOTE}:
            continue
        if _boundary_rule_triggered(rule, claim, claim_text):
            violation = _violation_from_rule(rule, claim)
            findings.append(_build_finding(claim, phase, rule, violation))
    return findings


def _audit_required_traceability(claim: Claim, phase: PhaseContract) -> list[AuditFinding]:
    has_traceability_rule = any(
        rule.category in {RuleCategory.TRACEABILITY, RuleCategory.EVIDENCE}
        or rule.kind == RuleKind.TRACEABILITY_EXPECTATION
        for rule in phase.rules
    )
    if not has_traceability_rule:
        return []

    high_stakes = claim.claim_type in {
        ClaimType.CAUSAL,
        ClaimType.RECOMMENDATION,
        ClaimType.SAVINGS,
        ClaimType.VERIFICATION_LIKE,
        ClaimType.COMPLIANCE_LIKE,
    } or claim.confidence_language_level in {
        ConfidenceLanguageLevel.HIGH,
        ConfidenceLanguageLevel.ABSOLUTE,
        ConfidenceLanguageLevel.VERIFICATION_GRADE,
        ConfidenceLanguageLevel.COMPLIANCE_GRADE,
    }
    if high_stakes and not claim.evidence_reference_presence:
        rule = _first_rule_by_category(phase, RuleCategory.TRACEABILITY) or _first_rule_by_kind(
            phase, RuleKind.TRACEABILITY_EXPECTATION
        )
        return [_build_finding(claim, phase, rule, ViolationType.TRACEABILITY_WEAKENING)]
    return []


def _audit_required_caveats(claim: Claim, phase: PhaseContract) -> list[AuditFinding]:
    has_certainty_rule = any(
        rule.category == RuleCategory.CERTAINTY
        or rule.kind in {RuleKind.CERTAINTY_CONSTRAINT, RuleKind.SEMANTIC_OVERREACH}
        for rule in phase.rules
    )
    if not has_certainty_rule:
        return []
    lowered = claim.normalized_text.lower()
    strong_without_caveat = claim.confidence_language_level in {
        ConfidenceLanguageLevel.HIGH,
        ConfidenceLanguageLevel.ABSOLUTE,
        ConfidenceLanguageLevel.VERIFICATION_GRADE,
        ConfidenceLanguageLevel.COMPLIANCE_GRADE,
    } and not any(term in lowered for term in ("preliminary", "public data", "not verified", "subject to"))
    if strong_without_caveat and claim.claim_type not in {ClaimType.UNCERTAINTY, ClaimType.VALIDATION_PATH}:
        rule = _first_rule_by_category(phase, RuleCategory.CERTAINTY)
        return [_build_finding(claim, phase, rule, ViolationType.UNCERTAINTY_SUPPRESSION)]
    return []


def _flag_relevant_to_phase(flag: ViolationType, phase_text: str, phase: PhaseContract) -> bool:
    if flag == ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION:
        return any(term in phase_text for term in ("verification", "validation", "decision-grade", "upgrade"))
    if flag == ViolationType.RECOMMENDATION_ESCALATION:
        return "recommend" in phase_text or "escalation" in phase_text or "scope" in phase_text
    if flag == ViolationType.CAUSAL_CLOSURE_WITHOUT_SUPPORT:
        return "evidence" in phase_text or "support" in phase_text or "causal" in phase_text
    if flag == ViolationType.SEMANTIC_OVERREACH:
        return any(term in phase_text for term in ("claim", "certainty", "overreach", "scope"))
    if flag == ViolationType.UNCERTAINTY_SUPPRESSION:
        return "uncertainty" in phase_text or "certainty" in phase_text or "caveat" in phase_text
    if flag == ViolationType.BENCHMARK_TO_SITE_SLIPPAGE:
        return "benchmark" in phase_text or "site" in phase_text or "scope" in phase_text
    if flag == ViolationType.PROXY_TO_HARD_CLAIM_SLIPPAGE:
        return "proxy" in phase_text or "hard" in phase_text or "claim" in phase_text
    return bool(phase.rules)


def _best_matching_rule(claim: Claim, phase: PhaseContract, flag: ViolationType) -> PhaseRule | None:
    candidates = sorted(
        phase.rules,
        key=lambda rule: _rule_score(rule, claim, flag),
        reverse=True,
    )
    return candidates[0] if candidates and _rule_score(candidates[0], claim, flag) > 0 else None


def _rule_score(rule: PhaseRule, claim: Claim, flag: ViolationType) -> int:
    text = claim.normalized_text.lower()
    score = 0
    score += sum(1 for keyword in rule.keywords if keyword and keyword in text)
    if rule.kind in BOUNDARY_KINDS:
        score += 2
    if flag == ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION and rule.category in {
        RuleCategory.VERIFICATION,
        RuleCategory.VALIDATION,
        RuleCategory.ESCALATION,
    }:
        score += 4
    if flag == ViolationType.TRACEABILITY_WEAKENING and rule.category == RuleCategory.TRACEABILITY:
        score += 4
    if flag == ViolationType.UNCERTAINTY_SUPPRESSION and rule.category == RuleCategory.CERTAINTY:
        score += 4
    return score


def _boundary_rule_triggered(rule: PhaseRule, claim: Claim, claim_text: str) -> bool:
    if rule.kind in {RuleKind.FORBIDDEN, RuleKind.HARD_BOUNDARY}:
        if _keyword_overlap(rule, claim_text) >= 2:
            return True
    if rule.kind in {RuleKind.VERIFICATION_BOUNDARY, RuleKind.ESCALATION_BOUNDARY}:
        if _is_negated_verification_caveat(claim_text):
            return False
        return claim.claim_type in {ClaimType.VERIFICATION_LIKE, ClaimType.COMPLIANCE_LIKE} or any(
            term in claim_text for term in ("verification-grade", "validated", "verified", "compliant")
        )
    if rule.kind in {RuleKind.CERTAINTY_CONSTRAINT, RuleKind.SEMANTIC_OVERREACH}:
        return claim.confidence_language_level in {
            ConfidenceLanguageLevel.HIGH,
            ConfidenceLanguageLevel.ABSOLUTE,
            ConfidenceLanguageLevel.VERIFICATION_GRADE,
            ConfidenceLanguageLevel.COMPLIANCE_GRADE,
        }
    return False


def _keyword_overlap(rule: PhaseRule, claim_text: str) -> int:
    return sum(1 for keyword in rule.keywords if re.search(rf"\b{re.escape(keyword)}\b", claim_text))


def _is_negated_verification_caveat(claim_text: str) -> bool:
    patterns = (
        r"\bnot\s+(?:been\s+)?field-verified\b",
        r"\bnot\s+(?:been\s+)?verified\b",
        r"\bnot\s+(?:been\s+)?validated\b",
        r"\bhas\s+not\s+been\s+field-verified\b",
        r"\bhas\s+not\s+been\s+verified\b",
        r"\bhas\s+not\s+been\s+validated\b",
    )
    return any(re.search(pattern, claim_text) for pattern in patterns)


def _violation_from_rule(rule: PhaseRule, claim: Claim) -> ViolationType:
    if rule.kind in {RuleKind.VERIFICATION_BOUNDARY, RuleKind.ESCALATION_BOUNDARY}:
        return ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION
    if rule.kind in {RuleKind.CERTAINTY_CONSTRAINT, RuleKind.SEMANTIC_OVERREACH}:
        return ViolationType.SEMANTIC_OVERREACH
    if claim.claim_type == ClaimType.RECOMMENDATION:
        return ViolationType.RECOMMENDATION_ESCALATION
    return ViolationType.CONTRACT_RULE_MATCH


def _build_finding(
    claim: Claim,
    phase: PhaseContract,
    rule: PhaseRule | None,
    violation_type: ViolationType,
) -> AuditFinding:
    severity = classify_severity(violation_type, claim, rule=rule, location=claim.source_location)
    action, guidance = _fix_guidance(violation_type, claim)
    source = f" against {rule.rule_id}" if rule else ""
    return AuditFinding(
        finding_id=f"{phase.phase_id}:{claim.claim_id}:{violation_type.value}:{rule.rule_id if rule else 'heuristic'}",
        claim_id=claim.claim_id,
        phase_id=phase.phase_id,
        rule_id=rule.rule_id if rule else None,
        violation_type=violation_type,
        severity=severity,
        verdict=ComplianceVerdict.NON_COMPLIANT,
        why_flagged=f"Claim triggered {violation_type.value}{source}.",
        evidence_excerpt=claim.raw_text,
        recommended_fix_type=action,
        rewrite_guidance=guidance,
        human_review_recommended=severity.value in {"high", "critical"},
        source_location=claim.source_location,
    )


def _fix_guidance(violation_type: ViolationType, claim: Claim) -> tuple[FixAction, str]:
    if violation_type == ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION:
        return (
            FixAction.SOFTEN,
            "Remove verification/compliance closure language unless the report cites an explicit hardening route and verified evidence.",
        )
    if violation_type == ViolationType.TRACEABILITY_WEAKENING:
        return (
            FixAction.ADD_TRACEABILITY,
            "Attach a specific source, table, citation, or upstream support note; otherwise soften or remove the claim.",
        )
    if violation_type == ViolationType.UNCERTAINTY_SUPPRESSION:
        return (
            FixAction.ADD_CAVEAT,
            "Add visible uncertainty and public-data limitation language near the claim.",
        )
    if violation_type == ViolationType.RECOMMENDATION_ESCALATION:
        return (
            FixAction.QUALIFY,
            "Reframe as a decision-grade option or validation candidate unless the phase contract authorizes stronger action.",
        )
    if violation_type == ViolationType.HARDENING_PATH_OMISSION:
        return (
            FixAction.ADD_HARDENING_PATH,
            "State the concrete verification or validation route required before upgrading the claim.",
        )
    if claim.claim_type == ClaimType.SAVINGS:
        return (
            FixAction.QUALIFY,
            "Distinguish modeled, proxy, benchmark, and site-validated financial logic; do not present estimates as confirmed savings.",
        )
    return (
        FixAction.QUALIFY,
        "Constrain the statement to what the cited upstream support actually authorizes.",
    )


def _first_rule_by_category(phase: PhaseContract, category: RuleCategory) -> PhaseRule | None:
    return next((rule for rule in phase.rules if rule.category == category), None)


def _first_rule_by_kind(phase: PhaseContract, kind: RuleKind) -> PhaseRule | None:
    return next((rule for rule in phase.rules if rule.kind == kind), None)


def _dedupe_findings(findings: list[AuditFinding]) -> list[AuditFinding]:
    seen: set[tuple[str, str | None, str]] = set()
    unique: list[AuditFinding] = []
    for finding in findings:
        key = (finding.phase_id, finding.claim_id, finding.violation_type.value)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique
