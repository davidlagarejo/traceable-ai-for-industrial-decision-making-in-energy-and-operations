from __future__ import annotations

from collections import Counter

from engines.claim_auditor import audit_claim_against_phase
from models.datatypes import AuditFinding, NormalizedReport, PhaseContract, PhaseEvaluation
from models.enums import ComplianceVerdict, FixAction, Severity, ViolationType


def evaluate_phase_compliance(
    report: NormalizedReport,
    phases: list[PhaseContract],
) -> list[PhaseEvaluation]:
    evaluations: list[PhaseEvaluation] = []
    for phase in phases:
        findings: list[AuditFinding] = []
        for claim in report.claims:
            findings.extend(audit_claim_against_phase(claim, phase))
        findings.extend(_audit_section_level_patterns(report, phase))
        severity_distribution = Counter(finding.severity.value for finding in findings)
        verdict = _verdict_for_findings(findings)
        evaluations.append(
            PhaseEvaluation(
                phase_id=phase.phase_id,
                phase_name=phase.phase_name,
                verdict=verdict,
                findings=findings,
                severity_distribution=dict(severity_distribution),
                summary=_phase_summary(phase, verdict, findings),
            )
        )
    return evaluations


def _audit_section_level_patterns(report: NormalizedReport, phase: PhaseContract) -> list[AuditFinding]:
    phase_text = " ".join(rule.text for rule in phase.rules).lower()
    if not any(term in phase_text for term in ("visible output", "report", "verification", "compliance")):
        return []

    findings: list[AuditFinding] = []
    inflated_terms = (
        "approved",
        "certificate",
        "certified",
        "compliance closure",
        "datos verificado",
        "guaranteed savings",
        "validated",
        "verified",
        "verified conclusion",
        "verificado",
    )
    for section in report.sections:
        title = section.title.lower()
        if any(term in title for term in inflated_terms):
            findings.append(
                AuditFinding(
                    finding_id=f"{phase.phase_id}:{section.section_id}:report_package_inflation",
                    claim_id=None,
                    phase_id=phase.phase_id,
                    rule_id=None,
                    violation_type=ViolationType.REPORT_PACKAGE_INFLATION,
                    severity=Severity.HIGH,
                    verdict=ComplianceVerdict.NON_COMPLIANT,
                    why_flagged="Section title presents package-level closure that can exceed upstream support.",
                    evidence_excerpt=section.title,
                    recommended_fix_type=FixAction.RELOCATE,
                    rewrite_guidance=(
                        "Rename or relocate the section so it does not imply verification, certification, "
                        "or compliance closure unless the phase contract authorizes it."
                    ),
                    human_review_recommended=True,
                    source_location=section.location,
                )
            )
    for unit in report.units:
        text = unit.text.strip()
        lowered = text.lower()
        if len(text) <= 80 and any(term in lowered for term in inflated_terms):
            findings.append(
                AuditFinding(
                    finding_id=f"{phase.phase_id}:{unit.unit_id}:visible_verification_callout",
                    claim_id=None,
                    phase_id=phase.phase_id,
                    rule_id=None,
                    violation_type=ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION,
                    severity=Severity.HIGH,
                    verdict=ComplianceVerdict.NON_COMPLIANT,
                    why_flagged="Short visible callout implies verification, approval, certification, or compliance closure.",
                    evidence_excerpt=text,
                    recommended_fix_type=FixAction.SOFTEN,
                    rewrite_guidance=(
                        "Replace the callout with bounded status language such as "
                        "'public-data support only', 'source data present', or 'requires validation'."
                    ),
                    human_review_recommended=True,
                    source_location=unit.location,
                )
            )
    return findings


def _verdict_for_findings(findings: list[AuditFinding]) -> ComplianceVerdict:
    if not findings:
        return ComplianceVerdict.COMPLIANT
    severities = {finding.severity for finding in findings}
    if Severity.CRITICAL in severities or Severity.HIGH in severities:
        return ComplianceVerdict.NON_COMPLIANT
    if Severity.MEDIUM in severities or Severity.LOW in severities:
        return ComplianceVerdict.PARTIALLY_COMPLIANT
    return ComplianceVerdict.INDETERMINATE


def _phase_summary(
    phase: PhaseContract,
    verdict: ComplianceVerdict,
    findings: list[AuditFinding],
) -> str:
    if not findings:
        return f"{phase.phase_id} is compliant under deterministic checks."
    counts = Counter(finding.severity.value for finding in findings)
    distribution = ", ".join(f"{severity}: {count}" for severity, count in sorted(counts.items()))
    return f"{phase.phase_id} is {verdict.value}; findings by severity: {distribution}."
