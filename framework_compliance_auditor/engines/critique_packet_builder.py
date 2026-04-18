from __future__ import annotations

import uuid

from models.datatypes import (
    AuditFinding,
    CompiledContract,
    ReferenceGap,
    RevisionInstruction,
    RevisionPacket,
)
from models.enums import FixAction, Severity


def build_revision_packet(
    report_id: str,
    audit_run_id: str,
    findings: list[AuditFinding],
    compiled_contract: CompiledContract,
    reference_gaps: list[ReferenceGap],
) -> RevisionPacket:
    grouped: dict[str, list[RevisionInstruction]] = {}
    rule_index = compiled_contract.rule_index
    for finding in findings:
        section_id = _section_id_for_finding(finding)
        rule = rule_index.get(finding.rule_id or "")
        instruction = RevisionInstruction(
            section_id=section_id,
            claim_id=finding.claim_id,
            problem_description=finding.why_flagged,
            why_it_matters=_why_it_matters(finding),
            normative_source=f"{rule.rule_id}: {rule.text}" if rule else finding.phase_id,
            comparative_source=None,
            explicit_rewrite_instruction=finding.rewrite_guidance,
            action=finding.recommended_fix_type,
            safer_language_examples=_safer_language_examples(finding),
        )
        grouped.setdefault(section_id or "GLOBAL", []).append(instruction)

    for gap in reference_gaps:
        if gap.severity not in {Severity.HIGH, Severity.MEDIUM}:
            continue
        grouped.setdefault("GLOBAL_REFERENCE_GAPS", []).append(
            RevisionInstruction(
                section_id="GLOBAL_REFERENCE_GAPS",
                claim_id=None,
                problem_description=gap.gap_description,
                why_it_matters=(
                    "Reference anchors are not normative law, but this gap lowers senior-grade quality."
                ),
                normative_source=None,
                comparative_source=f"{gap.dimension_name.value}: {gap.reference_anchor_expectation}",
                explicit_rewrite_instruction=gap.targeted_improvement_suggestion,
                action=FixAction.QUALIFY,
                safer_language_examples=[],
            )
        )

    return RevisionPacket(
        revision_batch_id=f"revision-{uuid.uuid4().hex[:12]}",
        report_id=report_id,
        audit_run_id=audit_run_id,
        grouped_fixes_by_section=grouped,
        unresolved_critical_count=sum(1 for finding in findings if finding.severity == Severity.CRITICAL),
    )


def _section_id_for_finding(finding: AuditFinding) -> str | None:
    if finding.source_location and finding.source_location.section_path:
        return " > ".join(finding.source_location.section_path)
    return None


def _why_it_matters(finding: AuditFinding) -> str:
    if finding.severity == Severity.CRITICAL:
        return "The issue can mislead executive readers or create false phase-boundary closure."
    if finding.severity == Severity.HIGH:
        return "The issue can contaminate recommendations or imply unsupported verification."
    if finding.severity == Severity.MEDIUM:
        return "The issue weakens traceability, uncertainty treatment, or phase discipline."
    return "The issue should be cleaned up to keep the audit trail precise."


def _safer_language_examples(finding: AuditFinding) -> list[str]:
    examples = {
        FixAction.SOFTEN: [
            "Public-data indicators suggest this risk may be present.",
            "This remains Decision-grade and has not been field-verified.",
        ],
        FixAction.ADD_TRACEABILITY: [
            "According to [source/table], the observed indicator is...",
            "The claim is supported by the cited public-data signal, not by site verification.",
        ],
        FixAction.ADD_CAVEAT: [
            "This conclusion is preliminary and subject to validation.",
            "The available evidence supports prioritization, not verification-grade closure.",
        ],
        FixAction.ADD_HARDENING_PATH: [
            "Upgrade would require field measurement, source reconciliation, and owner confirmation.",
        ],
        FixAction.QUALIFY: [
            "Treat this as a candidate finding pending validation.",
            "Frame this as an option, not a mandated action.",
        ],
    }
    return examples.get(finding.recommended_fix_type, [])

