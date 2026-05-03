from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from .results import ValidationSeverity


class RuleCode(str, Enum):
    OBSERVED_PRIMARY_NAME_REFERENCE_INVALID = "observed.primary_name_reference_invalid"
    OBSERVED_NAME_REFERENCE_INVALID = "observed.name_reference_invalid"
    OBSERVED_NAME_PARENT_MISMATCH = "observed.name_parent_mismatch"
    OBSERVED_NAME_PRIMARY_FLAG_INCOHERENT = "observed.name_primary_flag_incoherent"
    OBSERVED_NAME_OBSERVED_RECORD_REFERENCE_INVALID = "observed_name.observed_record_reference_invalid"
    ENTITY_NON_ACTIVE_DECLARED = "entity.non_active_declared"
    ALIAS_ENTITY_REFERENCE_INVALID = "alias.entity_reference_invalid"
    ALIAS_OBSERVED_NAME_REFERENCE_INVALID = "alias.observed_name_reference_invalid"
    CANDIDATE_MATCH_SET_REFERENCE_INVALID = "candidate_match.set_reference_invalid"
    CANDIDATE_MATCH_SOURCE_REFERENCE_INVALID = "candidate_match.source_reference_invalid"
    CANDIDATE_MATCH_CANDIDATE_REFERENCE_INVALID = "candidate_match.candidate_reference_invalid"
    CANDIDATE_MATCH_ENTITY_REFERENCE_INVALID = "candidate_match.entity_reference_invalid"
    CANDIDATE_MATCH_EVIDENCE_REFERENCE_INVALID = "candidate_match.evidence_reference_invalid"
    CANDIDATE_MATCH_CONFIDENCE_REFERENCE_INVALID = "candidate_match.confidence_reference_invalid"
    CANDIDATE_MATCH_SOURCE_NOT_ANCHORED = "candidate_match.source_not_anchored"
    CANDIDATE_MATCH_OPEN_DECLARED = "candidate_match.open_declared"
    CANDIDATE_SET_ANCHOR_REFERENCE_INVALID = "candidate_set.anchor_reference_invalid"
    CANDIDATE_SET_MATCH_REFERENCE_INVALID = "candidate_set.match_reference_invalid"
    CANDIDATE_SET_MATCH_SET_MISMATCH = "candidate_set.match_set_mismatch"
    CANDIDATE_SET_ANCHOR_COVERAGE_INVALID = "candidate_set.anchor_coverage_invalid"
    DECISION_CANDIDATE_SET_REFERENCE_INVALID = "decision.candidate_set_reference_invalid"
    DECISION_SCOPE_REFERENCE_INVALID = "decision.scope_reference_invalid"
    DECISION_EVIDENCE_REFERENCE_INVALID = "decision.evidence_reference_invalid"
    DECISION_CONFIDENCE_REFERENCE_INVALID = "decision.confidence_reference_invalid"
    DECISION_SET_STATUS_MISMATCH = "decision.set_status_mismatch"
    CONFIRMED_MATCH_DECISION_REFERENCE_INVALID = "confirmed_match.decision_reference_invalid"
    CONFIRMED_MATCH_DECISION_STATUS_MISMATCH = "confirmed_match.decision_status_mismatch"
    CONFIRMED_MATCH_ENTITY_REFERENCE_INVALID = "confirmed_match.entity_reference_invalid"
    CONFIRMED_MATCH_OBSERVED_REFERENCE_INVALID = "confirmed_match.observed_reference_invalid"
    CONFIRMED_MATCH_SCOPE_MISMATCH = "confirmed_match.scope_mismatch"
    NO_MATCH_DECISION_REFERENCE_INVALID = "no_match.decision_reference_invalid"
    NO_MATCH_DECISION_STATUS_MISMATCH = "no_match.decision_status_mismatch"
    NO_MATCH_SUBJECT_REFERENCE_INVALID = "no_match.subject_reference_invalid"
    NO_MATCH_REJECTED_REFERENCE_INVALID = "no_match.rejected_reference_invalid"
    NO_MATCH_ENTITY_REFERENCE_INVALID = "no_match.entity_reference_invalid"
    NO_MATCH_DECLARED = "no_match.declared"
    AMBIGUOUS_DECISION_REFERENCE_INVALID = "ambiguous.decision_reference_invalid"
    AMBIGUOUS_DECISION_STATUS_MISMATCH = "ambiguous.decision_status_mismatch"
    AMBIGUOUS_CANDIDATE_SET_REFERENCE_INVALID = "ambiguous.candidate_set_reference_invalid"
    AMBIGUOUS_OBSERVED_REFERENCE_INVALID = "ambiguous.observed_reference_invalid"
    AMBIGUOUS_ENTITY_REFERENCE_INVALID = "ambiguous.entity_reference_invalid"
    AMBIGUOUS_STATUS_INCOHERENT = "ambiguous.status_incoherent"
    AMBIGUOUS_DECLARED = "ambiguous.declared"
    RELATED_DECISION_REFERENCE_INVALID = "related.decision_reference_invalid"
    RELATED_DECISION_STATUS_MISMATCH = "related.decision_status_mismatch"
    RELATED_SOURCE_REFERENCE_INVALID = "related.source_reference_invalid"
    RELATED_OBSERVED_REFERENCE_INVALID = "related.observed_reference_invalid"
    RELATED_ENTITY_REFERENCE_INVALID = "related.entity_reference_invalid"
    RELATED_DECLARED = "related.declared"
    EVIDENCE_PROVENANCE_MISSING = "evidence.provenance_missing"
    CONFIDENCE_VALUE_REQUIRED = "confidence.value_required"
    CONFIDENCE_INSUFFICIENT_DECLARED = "confidence.insufficient_declared"
    MERGE_EVENT_DECISION_REFERENCE_INVALID = "merge_event.decision_reference_invalid"
    MERGE_EVENT_DECISION_STATUS_MISMATCH = "merge_event.decision_status_mismatch"
    MERGE_EVENT_ENTITY_REFERENCE_INVALID = "merge_event.entity_reference_invalid"
    SPLIT_EVENT_DECISION_REFERENCE_INVALID = "split_event.decision_reference_invalid"
    SPLIT_EVENT_DECISION_STATUS_MISMATCH = "split_event.decision_status_mismatch"
    SPLIT_EVENT_ENTITY_REFERENCE_INVALID = "split_event.entity_reference_invalid"
    HISTORY_ENTITY_REFERENCE_INVALID = "history.entity_reference_invalid"
    HISTORY_DECISION_REFERENCE_INVALID = "history.decision_reference_invalid"
    HISTORY_MERGE_REFERENCE_INVALID = "history.merge_reference_invalid"
    HISTORY_SPLIT_REFERENCE_INVALID = "history.split_reference_invalid"
    HISTORY_STATUS_EVENT_MISMATCH = "history.status_event_mismatch"
    HISTORY_EVENT_ENTITY_MISMATCH = "history.event_entity_mismatch"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    severity: ValidationSeverity
    blocking: bool


def _warning() -> RuleProfile:
    return RuleProfile(ValidationSeverity.WARNING, False)


def _error() -> RuleProfile:
    return RuleProfile(ValidationSeverity.ERROR, True)


RULE_PROFILES: dict[RuleCode, RuleProfile] = {
    RuleCode.OBSERVED_PRIMARY_NAME_REFERENCE_INVALID: _error(),
    RuleCode.OBSERVED_NAME_REFERENCE_INVALID: _error(),
    RuleCode.OBSERVED_NAME_PARENT_MISMATCH: _error(),
    RuleCode.OBSERVED_NAME_PRIMARY_FLAG_INCOHERENT: _error(),
    RuleCode.OBSERVED_NAME_OBSERVED_RECORD_REFERENCE_INVALID: _error(),
    RuleCode.ENTITY_NON_ACTIVE_DECLARED: _warning(),
    RuleCode.ALIAS_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.ALIAS_OBSERVED_NAME_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_MATCH_SET_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_MATCH_SOURCE_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_MATCH_CANDIDATE_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_MATCH_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_MATCH_EVIDENCE_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_MATCH_CONFIDENCE_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_MATCH_SOURCE_NOT_ANCHORED: _error(),
    RuleCode.CANDIDATE_MATCH_OPEN_DECLARED: _warning(),
    RuleCode.CANDIDATE_SET_ANCHOR_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_SET_MATCH_REFERENCE_INVALID: _error(),
    RuleCode.CANDIDATE_SET_MATCH_SET_MISMATCH: _error(),
    RuleCode.CANDIDATE_SET_ANCHOR_COVERAGE_INVALID: _error(),
    RuleCode.DECISION_CANDIDATE_SET_REFERENCE_INVALID: _error(),
    RuleCode.DECISION_SCOPE_REFERENCE_INVALID: _error(),
    RuleCode.DECISION_EVIDENCE_REFERENCE_INVALID: _error(),
    RuleCode.DECISION_CONFIDENCE_REFERENCE_INVALID: _error(),
    RuleCode.DECISION_SET_STATUS_MISMATCH: _error(),
    RuleCode.CONFIRMED_MATCH_DECISION_REFERENCE_INVALID: _error(),
    RuleCode.CONFIRMED_MATCH_DECISION_STATUS_MISMATCH: _error(),
    RuleCode.CONFIRMED_MATCH_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.CONFIRMED_MATCH_OBSERVED_REFERENCE_INVALID: _error(),
    RuleCode.CONFIRMED_MATCH_SCOPE_MISMATCH: _error(),
    RuleCode.NO_MATCH_DECISION_REFERENCE_INVALID: _error(),
    RuleCode.NO_MATCH_DECISION_STATUS_MISMATCH: _error(),
    RuleCode.NO_MATCH_SUBJECT_REFERENCE_INVALID: _error(),
    RuleCode.NO_MATCH_REJECTED_REFERENCE_INVALID: _error(),
    RuleCode.NO_MATCH_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.NO_MATCH_DECLARED: _warning(),
    RuleCode.AMBIGUOUS_DECISION_REFERENCE_INVALID: _error(),
    RuleCode.AMBIGUOUS_DECISION_STATUS_MISMATCH: _error(),
    RuleCode.AMBIGUOUS_CANDIDATE_SET_REFERENCE_INVALID: _error(),
    RuleCode.AMBIGUOUS_OBSERVED_REFERENCE_INVALID: _error(),
    RuleCode.AMBIGUOUS_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.AMBIGUOUS_STATUS_INCOHERENT: _error(),
    RuleCode.AMBIGUOUS_DECLARED: _warning(),
    RuleCode.RELATED_DECISION_REFERENCE_INVALID: _error(),
    RuleCode.RELATED_DECISION_STATUS_MISMATCH: _error(),
    RuleCode.RELATED_SOURCE_REFERENCE_INVALID: _error(),
    RuleCode.RELATED_OBSERVED_REFERENCE_INVALID: _error(),
    RuleCode.RELATED_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.RELATED_DECLARED: _warning(),
    RuleCode.EVIDENCE_PROVENANCE_MISSING: _error(),
    RuleCode.CONFIDENCE_VALUE_REQUIRED: _error(),
    RuleCode.CONFIDENCE_INSUFFICIENT_DECLARED: _warning(),
    RuleCode.MERGE_EVENT_DECISION_REFERENCE_INVALID: _error(),
    RuleCode.MERGE_EVENT_DECISION_STATUS_MISMATCH: _error(),
    RuleCode.MERGE_EVENT_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.SPLIT_EVENT_DECISION_REFERENCE_INVALID: _error(),
    RuleCode.SPLIT_EVENT_DECISION_STATUS_MISMATCH: _error(),
    RuleCode.SPLIT_EVENT_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.HISTORY_ENTITY_REFERENCE_INVALID: _error(),
    RuleCode.HISTORY_DECISION_REFERENCE_INVALID: _error(),
    RuleCode.HISTORY_MERGE_REFERENCE_INVALID: _error(),
    RuleCode.HISTORY_SPLIT_REFERENCE_INVALID: _error(),
    RuleCode.HISTORY_STATUS_EVENT_MISMATCH: _error(),
    RuleCode.HISTORY_EVENT_ENTITY_MISMATCH: _error(),
}


def profile_for(rule_code: RuleCode) -> RuleProfile:
    return RULE_PROFILES[rule_code]
