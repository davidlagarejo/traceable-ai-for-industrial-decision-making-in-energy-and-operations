from __future__ import annotations

import statistics
from pathlib import Path

from engines.report_normalizer import SUPPORTED_REPORT_EXTENSIONS, normalize_report
from models.datatypes import NormalizedReport, ReferenceGap
from models.enums import DocumentRole, ReferenceDimension, Severity


TERM_SETS = {
    ReferenceDimension.TECHNICAL_DENSITY: {
        "baseline",
        "capacity",
        "constraint",
        "degradation",
        "efficiency",
        "metric",
        "operational",
        "threshold",
        "variance",
    },
    ReferenceDimension.METHODOLOGICAL_EXPLICITNESS: {
        "assumption",
        "dataset",
        "method",
        "methodology",
        "model",
        "proxy",
        "sample",
        "scope",
    },
    ReferenceDimension.UNCERTAINTY_HANDLING_MATURITY: {
        "caveat",
        "confidence",
        "decision-grade",
        "limitation",
        "not been field-verified",
        "not field-verified",
        "not verified",
        "preliminary",
        "uncertain",
        "uncertainty",
        "unknown",
    },
    ReferenceDimension.FINANCIAL_SERIOUSNESS: {
        "capex",
        "cost",
        "dollars",
        "financial",
        "margin",
        "opex",
        "payback",
        "roi",
        "savings",
    },
    ReferenceDimension.REGULATORY_SERIOUSNESS: {
        "compliance",
        "legal",
        "permit",
        "policy",
        "regulation",
        "regulatory",
        "standard",
    },
    ReferenceDimension.MARKET_COMPARISON_SHARPNESS: {
        "alternative",
        "benchmark",
        "competitor",
        "market",
        "peer",
        "substitute",
        "versus",
    },
    ReferenceDimension.STRUCTURE_QUALITY: {
        "appendix",
        "finding",
        "method",
        "recommendation",
        "summary",
    },
    ReferenceDimension.RECOMMENDATION_MATURITY: {
        "dependency",
        "next step",
        "owner",
        "prerequisite",
        "priority",
        "recommend",
        "sequence",
    },
    ReferenceDimension.EVIDENCE_DISCUSSION_DEPTH: {
        "citation",
        "evidence",
        "source",
        "table",
        "trace",
        "upstream",
    },
    ReferenceDimension.SENIOR_REPORT_FEEL: {
        "assumption",
        "evidence",
        "limitation",
        "method",
        "recommendation",
        "tradeoff",
        "uncertainty",
    },
}


def compare_report_to_references(
    report: NormalizedReport,
    reference_paths: list[str | Path],
) -> list[ReferenceGap]:
    reference_files = discover_reference_files(reference_paths)
    if not reference_files:
        return [
            ReferenceGap(
                dimension_name=ReferenceDimension.SENIOR_REPORT_FEEL,
                current_state="No reference anchors were supplied.",
                reference_anchor_expectation="Provide curated reference documents to calibrate quality.",
                gap_description=(
                    "Reference comparison was skipped. This does not affect normative phase compliance."
                ),
                severity=Severity.LOW,
                targeted_improvement_suggestion=(
                    "Add reference reports when quality benchmarking is required."
                ),
            )
        ]

    reference_reports = [
        normalize_report(path, role=DocumentRole.REFERENCE_ANCHOR, phase_ids=[]) for path in reference_files
    ]
    report_metrics = compute_quality_metrics(report)
    reference_metrics = [compute_quality_metrics(reference) for reference in reference_reports]
    gaps: list[ReferenceGap] = []
    for dimension in ReferenceDimension:
        current = report_metrics[dimension.value]
        anchor = statistics.median(metrics[dimension.value] for metrics in reference_metrics)
        severity = _severity_from_ratio(current, anchor)
        if severity == Severity.LOW and current >= anchor * 0.85:
            continue
        gaps.append(
            ReferenceGap(
                dimension_name=dimension,
                current_state=f"Measured local signal: {current:.2f}",
                reference_anchor_expectation=f"Reference median signal: {anchor:.2f}",
                gap_description=_gap_description(dimension, current, anchor),
                severity=severity,
                targeted_improvement_suggestion=_improvement_suggestion(dimension),
            )
        )
    return gaps


def compute_quality_metrics(report: NormalizedReport) -> dict[str, float]:
    text = " ".join(unit.text for unit in report.units)
    lowered = text.lower()
    words = [word for word in lowered.replace("$", " dollars ").split() if word.strip()]
    word_count = max(len(words), 1)
    per_1000 = word_count / 1000

    metrics: dict[str, float] = {}
    for dimension, terms in TERM_SETS.items():
        count = sum(lowered.count(term) for term in terms)
        metrics[dimension.value] = count / per_1000

    metrics[ReferenceDimension.TECHNICAL_DENSITY.value] += _number_density(text) * 10
    metrics[ReferenceDimension.STRUCTURE_QUALITY.value] += min(len(report.sections) / max(word_count / 800, 1), 8)
    metrics[ReferenceDimension.EVIDENCE_DISCUSSION_DEPTH.value] += (
        len(report.citations) + len(report.tables) * 2
    ) / per_1000
    metrics[ReferenceDimension.SENIOR_REPORT_FEEL.value] = statistics.mean(
        [
            metrics[ReferenceDimension.TECHNICAL_DENSITY.value],
            metrics[ReferenceDimension.METHODOLOGICAL_EXPLICITNESS.value],
            metrics[ReferenceDimension.UNCERTAINTY_HANDLING_MATURITY.value],
            metrics[ReferenceDimension.EVIDENCE_DISCUSSION_DEPTH.value],
            metrics[ReferenceDimension.RECOMMENDATION_MATURITY.value],
        ]
    )
    return metrics


def discover_reference_files(paths: list[str | Path]) -> list[Path]:
    files: list[Path] = []
    for item in paths:
        path = Path(item)
        if path.is_dir():
            files.extend(
                child
                for child in sorted(path.rglob("*"))
                if child.is_file() and child.suffix.lower() in SUPPORTED_REPORT_EXTENSIONS
            )
        elif path.is_file() and path.suffix.lower() in SUPPORTED_REPORT_EXTENSIONS:
            files.append(path)
    return sorted(dict.fromkeys(files))


def _number_density(text: str) -> float:
    words = max(len(text.split()), 1)
    digits = sum(1 for token in text.split() if any(char.isdigit() for char in token))
    return digits / words


def _severity_from_ratio(current: float, anchor: float) -> Severity:
    if anchor <= 0:
        return Severity.LOW
    ratio = current / anchor
    if ratio < 0.4:
        return Severity.HIGH
    if ratio < 0.75:
        return Severity.MEDIUM
    return Severity.LOW


def _gap_description(dimension: ReferenceDimension, current: float, anchor: float) -> str:
    if anchor <= 0:
        return f"The report has weak {dimension.value} signals, but reference anchors are also sparse."
    ratio = current / anchor
    return (
        f"The report is thinner than reference anchors for {dimension.value}; "
        f"local signal is {ratio:.0%} of the reference median. This is a quality gap, not a phase violation."
    )


def _improvement_suggestion(dimension: ReferenceDimension) -> str:
    suggestions = {
        ReferenceDimension.TECHNICAL_DENSITY: (
            "Add concrete measurements, constraints, thresholds, and operational specifics."
        ),
        ReferenceDimension.METHODOLOGICAL_EXPLICITNESS: (
            "Make assumptions, data sources, proxy limits, and method steps explicit."
        ),
        ReferenceDimension.UNCERTAINTY_HANDLING_MATURITY: (
            "Add visible uncertainty treatment and distinguish preliminary support from verified fact."
        ),
        ReferenceDimension.FINANCIAL_SERIOUSNESS: (
            "Separate modeled economics, proxies, assumptions, ranges, and validation requirements."
        ),
        ReferenceDimension.REGULATORY_SERIOUSNESS: (
            "Name relevant regulatory constraints without implying compliance closure."
        ),
        ReferenceDimension.MARKET_COMPARISON_SHARPNESS: (
            "Add peer, market, or alternative comparisons with caveats about comparability."
        ),
        ReferenceDimension.STRUCTURE_QUALITY: (
            "Improve sectioning so findings, methods, evidence, and recommendations are easy to audit."
        ),
        ReferenceDimension.RECOMMENDATION_MATURITY: (
            "Tie recommendations to prerequisites, owners, sequencing, and verification conditions."
        ),
        ReferenceDimension.EVIDENCE_DISCUSSION_DEPTH: (
            "Expose source quality, evidence limits, citations, and table provenance."
        ),
        ReferenceDimension.SENIOR_REPORT_FEEL: (
            "Increase disciplined density: method, evidence, uncertainty, and decision consequences."
        ),
    }
    return suggestions[dimension]
