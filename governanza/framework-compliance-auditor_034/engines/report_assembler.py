from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from models.datatypes import (
    AuditManifest,
    AuditScorecard,
    CompiledContract,
    NormalizedReport,
    PhaseEvaluation,
    ReferenceGap,
    RevisionPacket,
    to_jsonable,
)
from models.enums import Severity


def write_audit_artifacts(
    output_dir: str | Path,
    *,
    audit_run_id: str,
    compiled_contract: CompiledContract,
    report: NormalizedReport,
    phase_evaluations: list[PhaseEvaluation],
    reference_gaps: list[ReferenceGap],
    revision_packet: RevisionPacket,
    scorecard: AuditScorecard,
    settings: dict[str, Any],
) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    findings = [finding for evaluation in phase_evaluations for finding in evaluation.findings]
    artifacts: dict[str, Any] = {
        "phase_compliance_report.json": _phase_compliance_payload(
            audit_run_id, report, phase_evaluations, scorecard, settings
        ),
        "claim_violation_register.json": _claim_register_payload(findings),
        "reference_gap_report.json": [to_jsonable(gap) for gap in reference_gaps],
        "revision_packet.json": to_jsonable(revision_packet),
        "audit_scorecard.json": to_jsonable(scorecard),
        "normalized_report.json": to_jsonable(report),
        "compiled_contract.json": to_jsonable(compiled_contract),
    }

    locations: dict[str, str] = {}
    for filename, payload in artifacts.items():
        path = out / filename
        write_json(path, payload)
        locations[filename] = str(path)

    summary_path = out / "audit_summary.md"
    summary_path.write_text(
        build_audit_summary_markdown(
            audit_run_id=audit_run_id,
            report=report,
            phase_evaluations=phase_evaluations,
            reference_gaps=reference_gaps,
            scorecard=scorecard,
            revision_packet=revision_packet,
        ),
        encoding="utf-8",
    )
    locations["audit_summary.md"] = str(summary_path)
    return locations


def write_manifest(output_dir: str | Path, manifest: AuditManifest) -> str:
    path = Path(output_dir) / "audit_manifest.json"
    write_json(path, to_jsonable(manifest))
    return str(path)


def write_json(path: str | Path, payload: Any) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _phase_compliance_payload(
    audit_run_id: str,
    report: NormalizedReport,
    phase_evaluations: list[PhaseEvaluation],
    scorecard: AuditScorecard,
    settings: dict[str, Any],
) -> dict[str, Any]:
    violations_by_phase: dict[str, list[dict[str, Any]]] = defaultdict(list)
    severity_counter: Counter[str] = Counter()
    excerpts: list[dict[str, str | None]] = []
    for evaluation in phase_evaluations:
        for finding in evaluation.findings:
            violations_by_phase[evaluation.phase_id].append(to_jsonable(finding))
            severity_counter[finding.severity.value] += 1
            if len(excerpts) < 10:
                excerpts.append(
                    {
                        "phase_id": evaluation.phase_id,
                        "claim_id": finding.claim_id,
                        "severity": finding.severity.value,
                        "excerpt": finding.evidence_excerpt,
                    }
                )

    return {
        "report_id": report.report_id,
        "audit_run_id": audit_run_id,
        "per_phase_verdict": [
            {
                "phase_id": evaluation.phase_id,
                "phase_name": evaluation.phase_name,
                "verdict": evaluation.verdict.value,
                "summary": evaluation.summary,
                "severity_distribution": evaluation.severity_distribution,
            }
            for evaluation in phase_evaluations
        ],
        "violations_grouped_by_phase": dict(violations_by_phase),
        "severity_distribution": dict(severity_counter),
        "representative_evidence_excerpts": excerpts,
        "pass_fail_thresholds": {
            "compliance_min_score": settings.get("compliance_min_score"),
            "quality_min_score": settings.get("quality_min_score"),
            "allow_critical_findings": settings.get("allow_critical_findings"),
        },
        "overall_contract_compliance_summary": {
            "gate": scorecard.overall_compliance_gate.value,
            "recommended_next_action": scorecard.recommended_next_action,
        },
    }


def _claim_register_payload(findings) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for finding in findings:
        rows.append(
            {
                "finding_id": finding.finding_id,
                "claim_id": finding.claim_id,
                "claim_text": finding.evidence_excerpt,
                "section_id": (
                    " > ".join(finding.source_location.section_path)
                    if finding.source_location and finding.source_location.section_path
                    else None
                ),
                "page_ref": finding.source_location.page_number if finding.source_location else None,
                "phase_id": finding.phase_id,
                "violation_type": finding.violation_type.value,
                "severity": finding.severity.value,
                "why_flagged": finding.why_flagged,
                "recommended_fix_type": finding.recommended_fix_type.value,
                "rewrite_guidance": finding.rewrite_guidance,
                "whether_human_review_is_recommended": finding.human_review_recommended,
            }
        )
    return rows


def build_audit_summary_markdown(
    *,
    audit_run_id: str,
    report: NormalizedReport,
    phase_evaluations: list[PhaseEvaluation],
    reference_gaps: list[ReferenceGap],
    scorecard: AuditScorecard,
    revision_packet: RevisionPacket,
) -> str:
    findings = [finding for evaluation in phase_evaluations for finding in evaluation.findings]
    severity_counts = Counter(finding.severity.value for finding in findings)
    phase_lines = "\n".join(
        f"- {evaluation.phase_id} ({evaluation.phase_name}): {evaluation.verdict.value}"
        for evaluation in phase_evaluations
    )
    score_lines = "\n".join(
        f"- {dimension.name}: {dimension.score} - {dimension.rationale}"
        for dimension in scorecard.dimensions
    )
    top_findings = "\n".join(
        f"- {finding.severity.value}: {finding.evidence_excerpt}"
        for finding in sorted(findings, key=lambda item: _severity_order(item.severity), reverse=True)[:8]
    )
    top_gaps = "\n".join(
        f"- {gap.severity.value}: {gap.dimension_name.value} - {gap.gap_description}"
        for gap in reference_gaps[:8]
    )
    return f"""# Audit Summary

Audit run: `{audit_run_id}`

Report: `{report.source_path}`

Compliance gate: **{scorecard.overall_compliance_gate.value}**

Quality gate: **{scorecard.overall_quality_gate.value}**

Recommended next action: {scorecard.recommended_next_action}

## Phase Verdicts

{phase_lines or "- No phase evaluations produced."}

## Severity Distribution

{dict(severity_counts)}

## Highest-Priority Findings

{top_findings or "- No deterministic phase violations found."}

## Reference Quality Gaps

{top_gaps or "- No material reference-anchor gaps detected."}

## Scorecard

{score_lines}

## Revision Packet

Revision batch: `{revision_packet.revision_batch_id}`

Grouped sections requiring revision: {len(revision_packet.grouped_fixes_by_section)}
"""


def _severity_order(severity: Severity) -> int:
    return {
        Severity.LOW: 1,
        Severity.MEDIUM: 2,
        Severity.HIGH: 3,
        Severity.CRITICAL: 4,
    }[severity]

