from __future__ import annotations

from collections import Counter

from engines.evidence_linker import evidence_coverage_metrics
from models.datatypes import (
    AuditFinding,
    AuditScorecard,
    NormalizedReport,
    PhaseEvaluation,
    ReferenceGap,
    ScoreDimension,
)
from models.enums import GateStatus, ReferenceDimension, Severity


PHASE_DIMENSIONS = {
    "phase0": "phase0_epistemic_compliance",
    "phase1": "phase1_scope_compliance",
    "phase3": "phase3_reporting_compliance",
    "phase4": "phase4_upgrade_compliance",
}

REFERENCE_TO_SCORE_DIMENSION = {
    ReferenceDimension.TECHNICAL_DENSITY: "technical_density",
    ReferenceDimension.METHODOLOGICAL_EXPLICITNESS: "methodological_rigor",
    ReferenceDimension.UNCERTAINTY_HANDLING_MATURITY: "uncertainty_handling",
    ReferenceDimension.FINANCIAL_SERIOUSNESS: "financial_seriousness",
    ReferenceDimension.REGULATORY_SERIOUSNESS: "regulatory_seriousness",
    ReferenceDimension.MARKET_COMPARISON_SHARPNESS: "market_comparison_sharpness",
    ReferenceDimension.SENIOR_REPORT_FEEL: "senior_report_quality",
}


def build_scorecard(
    report: NormalizedReport,
    audit_run_id: str,
    phase_evaluations: list[PhaseEvaluation],
    reference_gaps: list[ReferenceGap],
    settings: dict,
) -> AuditScorecard:
    dimensions: list[ScoreDimension] = []

    phase_by_id = {evaluation.phase_id.lower(): evaluation for evaluation in phase_evaluations}
    for phase_id, dimension_name in PHASE_DIMENSIONS.items():
        evaluation = phase_by_id.get(phase_id)
        if evaluation:
            dimensions.append(_phase_score_dimension(dimension_name, evaluation))
        else:
            dimensions.append(
                ScoreDimension(
                    name=dimension_name,
                    score=0,
                    rationale=f"No {phase_id} contract was loaded.",
                    key_failures=[f"Missing {phase_id} normative contract"],
                    improvement_priority="high",
                )
            )

    dimensions.extend(_quality_dimensions(report, reference_gaps, phase_evaluations))

    compliance_gate = _compliance_gate(dimensions, phase_evaluations, settings)
    quality_gate = _quality_gate(dimensions, settings)
    next_action = _recommended_next_action(compliance_gate, quality_gate, phase_evaluations, reference_gaps)
    return AuditScorecard(
        report_id=report.report_id,
        audit_run_id=audit_run_id,
        dimensions=dimensions,
        overall_compliance_gate=compliance_gate,
        overall_quality_gate=quality_gate,
        recommended_next_action=next_action,
    )


def _phase_score_dimension(name: str, evaluation: PhaseEvaluation) -> ScoreDimension:
    findings = evaluation.findings
    score = score_findings(findings)
    failures = [finding.why_flagged for finding in findings[:5]]
    strengths = [] if findings else ["No deterministic violations found for this phase."]
    priority = "critical" if score < 60 else "high" if score < 80 else "medium" if score < 90 else "low"
    return ScoreDimension(
        name=name,
        score=score,
        rationale=evaluation.summary,
        key_failures=failures,
        key_strengths=strengths,
        improvement_priority=priority,
    )


def score_findings(findings: list[AuditFinding]) -> int:
    penalties = {
        Severity.CRITICAL: 35,
        Severity.HIGH: 22,
        Severity.MEDIUM: 10,
        Severity.LOW: 3,
    }
    score = 100
    for finding in findings:
        score -= penalties[finding.severity]
    return max(score, 0)


def _quality_dimensions(
    report: NormalizedReport,
    reference_gaps: list[ReferenceGap],
    phase_evaluations: list[PhaseEvaluation],
) -> list[ScoreDimension]:
    gap_by_dimension = {
        REFERENCE_TO_SCORE_DIMENSION[gap.dimension_name]: gap
        for gap in reference_gaps
        if gap.dimension_name in REFERENCE_TO_SCORE_DIMENSION
    }
    dimensions: list[ScoreDimension] = []
    for dimension_name in [
        "technical_density",
        "methodological_rigor",
        "uncertainty_handling",
        "financial_seriousness",
        "regulatory_seriousness",
        "market_comparison_sharpness",
        "senior_report_quality",
    ]:
        gap = gap_by_dimension.get(dimension_name)
        dimensions.append(_dimension_from_gap(dimension_name, gap))

    coverage = evidence_coverage_metrics(report)
    traceability_score = int(coverage["high_stakes_evidence_coverage"] * 100)
    traceability_findings = _findings_by_type_text(phase_evaluations, "traceability")
    if traceability_findings:
        traceability_score = min(traceability_score, 75)
    dimensions.append(
        ScoreDimension(
            name="traceability_clarity",
            score=traceability_score,
            rationale=(
                f"High-stakes evidence coverage is "
                f"{coverage['high_stakes_evidence_coverage']:.0%}."
            ),
            key_failures=traceability_findings[:5],
            key_strengths=[] if traceability_findings else ["High-stakes claims are adequately linked."],
            improvement_priority="high" if traceability_score < 80 else "medium",
        )
    )

    validation_failures = _findings_by_type_text(phase_evaluations, "verification")
    validation_score = max(0, 100 - len(validation_failures) * 15)
    dimensions.append(
        ScoreDimension(
            name="validation_honesty",
            score=validation_score,
            rationale="Measures whether validation and verification language stays within support.",
            key_failures=validation_failures[:5],
            key_strengths=[] if validation_failures else ["No unsupported validation closure found."],
            improvement_priority="high" if validation_score < 80 else "medium",
        )
    )
    return dimensions


def _dimension_from_gap(dimension_name: str, gap: ReferenceGap | None) -> ScoreDimension:
    if not gap:
        return ScoreDimension(
            name=dimension_name,
            score=90,
            rationale="No material reference-anchor gap detected for this dimension.",
            key_strengths=["At or near reference anchor level under deterministic metrics."],
            improvement_priority="low",
        )
    score = {Severity.HIGH: 55, Severity.MEDIUM: 72, Severity.LOW: 84, Severity.CRITICAL: 40}[gap.severity]
    return ScoreDimension(
        name=dimension_name,
        score=score,
        rationale=gap.gap_description,
        key_failures=[gap.targeted_improvement_suggestion],
        key_strengths=[],
        improvement_priority="high" if gap.severity == Severity.HIGH else "medium",
    )


def _findings_by_type_text(phase_evaluations: list[PhaseEvaluation], needle: str) -> list[str]:
    failures: list[str] = []
    for evaluation in phase_evaluations:
        for finding in evaluation.findings:
            if needle in finding.violation_type.value:
                failures.append(f"{evaluation.phase_id}: {finding.evidence_excerpt}")
    return failures


def _compliance_gate(
    dimensions: list[ScoreDimension],
    phase_evaluations: list[PhaseEvaluation],
    settings: dict,
) -> GateStatus:
    threshold = int(settings.get("compliance_min_score", 80))
    allow_critical = bool(settings.get("allow_critical_findings", False))
    if not allow_critical and any(
        finding.severity == Severity.CRITICAL
        for evaluation in phase_evaluations
        for finding in evaluation.findings
    ):
        return GateStatus.FAIL
    phase_scores = [dimension.score for dimension in dimensions if dimension.name.endswith("_compliance")]
    if any(score < threshold for score in phase_scores):
        return GateStatus.FAIL
    if any(score < threshold + 8 for score in phase_scores):
        return GateStatus.WARN
    return GateStatus.PASS


def _quality_gate(dimensions: list[ScoreDimension], settings: dict) -> GateStatus:
    threshold = int(settings.get("quality_min_score", 70))
    quality_scores = [dimension.score for dimension in dimensions if not dimension.name.endswith("_compliance")]
    if any(score < threshold for score in quality_scores):
        return GateStatus.FAIL
    if any(score < threshold + 8 for score in quality_scores):
        return GateStatus.WARN
    return GateStatus.PASS


def _recommended_next_action(
    compliance_gate: GateStatus,
    quality_gate: GateStatus,
    phase_evaluations: list[PhaseEvaluation],
    reference_gaps: list[ReferenceGap],
) -> str:
    severity_counts = Counter(
        finding.severity.value
        for evaluation in phase_evaluations
        for finding in evaluation.findings
    )
    if compliance_gate == GateStatus.FAIL:
        return (
            "Revise blocked phase violations before quality polishing. "
            f"Finding distribution: {dict(severity_counts)}."
        )
    if quality_gate == GateStatus.FAIL:
        high_gaps = [gap.dimension_name.value for gap in reference_gaps if gap.severity == Severity.HIGH]
        return f"Improve reference-grade quality gaps: {', '.join(high_gaps) or 'see gap report'}."
    if compliance_gate == GateStatus.WARN or quality_gate == GateStatus.WARN:
        return "Re-audit after targeted revisions to clear warning-level residual issues."
    return "Report passes deterministic compliance and quality gates."

