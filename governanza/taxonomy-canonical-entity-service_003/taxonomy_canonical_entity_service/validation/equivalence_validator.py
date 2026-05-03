from __future__ import annotations

from ..domain.records import CandidateMatchRecord, EquivalenceRecord
from ..domain.enums import EquivalenceStatus, MatchStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_equivalence_record(
    equivalence_record: EquivalenceRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not equivalence_record.equivalence_record_id.value:
        collector.add(
            RuleCode.EQUIVALENCE_ID_INVALID,
            "equivalence_record_id must be present.",
            field_ref="equivalence_record_id",
        )
    if context is None or not context.contains_locator(equivalence_record.left_ref):
        collector.add(
            RuleCode.EQUIVALENCE_REF_UNRESOLVED,
            "equivalence_record.left_ref must resolve to an existing semantic object.",
            field_ref="left_ref",
        )
    if context is None or not context.contains_locator(equivalence_record.right_ref):
        collector.add(
            RuleCode.EQUIVALENCE_REF_UNRESOLVED,
            "equivalence_record.right_ref must resolve to an existing semantic object.",
            field_ref="right_ref",
        )
    if equivalence_record.equivalence_status is not EquivalenceStatus.CONFIRMED:
        collector.add(
            RuleCode.EQUIVALENCE_NON_CONFIRMED_DECLARED,
            f"equivalence is declared as {equivalence_record.equivalence_status.value}.",
            field_ref="equivalence_status",
        )


def validate_candidate_match_record(
    candidate_match_record: CandidateMatchRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not candidate_match_record.candidate_match_record_id.value:
        collector.add(
            RuleCode.MATCH_ID_INVALID,
            "candidate_match_record_id must be present.",
            field_ref="candidate_match_record_id",
        )
    if context is None or not context.contains_locator(candidate_match_record.candidate_ref):
        collector.add(
            RuleCode.MATCH_TARGET_UNRESOLVED,
            "candidate_match_record must target an existing semantic object.",
            field_ref="candidate_ref",
        )
    if candidate_match_record.match_status is not MatchStatus.CONFIRMED:
        collector.add(
            RuleCode.MATCH_PENDING_DECLARED,
            f"candidate match is declared as {candidate_match_record.match_status.value}.",
            field_ref="match_status",
        )

