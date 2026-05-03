from __future__ import annotations

from ..domain.enums import ConfidenceStatus
from ..domain.records import ResolutionConfidenceRecord, ResolutionEvidenceRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_resolution_evidence_record(
    resolution_evidence_record: ResolutionEvidenceRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if (
        resolution_evidence_record.source_provenance.normalized_record_ref is None
        and not resolution_evidence_record.source_provenance.normalized_field_refs
    ):
        collector.add(
            RuleCode.EVIDENCE_PROVENANCE_MISSING,
            "ResolutionEvidenceRecord must preserve normalized provenance.",
            field_ref="source_provenance",
        )


def validate_resolution_confidence_record(
    resolution_confidence_record: ResolutionConfidenceRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if (
        resolution_confidence_record.confidence_status is not ConfidenceStatus.INSUFFICIENT
        and resolution_confidence_record.confidence_value is None
    ):
        collector.add(
            RuleCode.CONFIDENCE_VALUE_REQUIRED,
            "ResolutionConfidenceRecord requires confidence_value unless confidence_status is INSUFFICIENT.",
            field_ref="confidence_value",
        )
    if resolution_confidence_record.confidence_status is ConfidenceStatus.INSUFFICIENT:
        collector.add(
            RuleCode.CONFIDENCE_INSUFFICIENT_DECLARED,
            "ResolutionConfidenceRecord declares insufficient confidence and must not be consumed as a strong identity basis.",
            field_ref="confidence_status",
        )
