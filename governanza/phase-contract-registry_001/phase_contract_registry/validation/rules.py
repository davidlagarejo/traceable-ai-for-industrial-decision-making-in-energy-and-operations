from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from ..domain.enums import ViolationSeverity


class RuleCode(str, Enum):
    PHASE_DECLARED_OBJECT_MISSING = "phase.declared_object_missing"
    PHASE_OBJECT_PHASE_MISMATCH = "phase.object_phase_mismatch"
    PHASE_UNDECLARED_OBJECT_PROVIDED = "phase.undeclared_object_provided"
    PHASE_DECLARED_TRANSITION_MISSING = "phase.declared_transition_missing"
    PHASE_TRANSITION_PHASE_MISMATCH = "phase.transition_phase_mismatch"
    PHASE_UNDECLARED_TRANSITION_PROVIDED = "phase.undeclared_transition_provided"
    OBJECT_PHASE_REFERENCE_MISMATCH = "object.phase_reference_mismatch"
    OBJECT_NOT_DECLARED_BY_PHASE = "object.not_declared_by_phase"
    OBJECT_EMPTY_FIELD_SHAPE = "object.empty_field_shape"
    OBJECT_EMPTY_EPISTEMIC_TOKEN_SET = "object.empty_epistemic_token_set"
    METADATA_REQUIRED_KEY_MISSING = "metadata.required_key_missing"
    METADATA_IMMUTABLE_KEY_DROPPED = "metadata.immutable_key_dropped"
    METADATA_IMMUTABLE_KEY_CHANGED = "metadata.immutable_key_changed"
    METADATA_PASSTHROUGH_KEY_DROPPED = "metadata.passthrough_key_dropped"
    TRANSITION_SOURCE_PHASE_MISMATCH = "transition.source_phase_mismatch"
    TRANSITION_TARGET_PHASE_MISMATCH = "transition.target_phase_mismatch"
    TRANSITION_SELF_HANDOFF = "transition.self_handoff"
    TRANSITION_NOT_DECLARED_BY_SOURCE_PHASE = "transition.not_declared_by_source_phase"
    TRANSITION_NOT_DECLARED_BY_TARGET_PHASE = "transition.not_declared_by_target_phase"
    TRANSITION_SOURCE_OBJECT_MISSING = "transition.source_object_missing"
    TRANSITION_TARGET_OBJECT_MISSING = "transition.target_object_missing"
    TRANSITION_SOURCE_OBJECT_PHASE_MISMATCH = "transition.source_object_phase_mismatch"
    TRANSITION_TARGET_OBJECT_PHASE_MISMATCH = "transition.target_object_phase_mismatch"
    TRANSITION_REQUIRED_PRECONDITION_MISSING = "transition.required_precondition_missing"
    TRANSITION_STATUS_TRANSFORM_BLOCKED = "transition.status_transform_blocked"
    TRANSITION_STATUS_TRANSFORM_NOT_ALLOWED = "transition.status_transform_not_allowed"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    severity: ViolationSeverity
    blocking: bool


RULE_PROFILES: dict[RuleCode, RuleProfile] = {
    RuleCode.PHASE_DECLARED_OBJECT_MISSING: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.PHASE_OBJECT_PHASE_MISMATCH: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.PHASE_UNDECLARED_OBJECT_PROVIDED: RuleProfile(ViolationSeverity.WARNING, False),
    RuleCode.PHASE_DECLARED_TRANSITION_MISSING: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.PHASE_TRANSITION_PHASE_MISMATCH: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.PHASE_UNDECLARED_TRANSITION_PROVIDED: RuleProfile(ViolationSeverity.WARNING, False),
    RuleCode.OBJECT_PHASE_REFERENCE_MISMATCH: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.OBJECT_NOT_DECLARED_BY_PHASE: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.OBJECT_EMPTY_FIELD_SHAPE: RuleProfile(ViolationSeverity.WARNING, False),
    RuleCode.OBJECT_EMPTY_EPISTEMIC_TOKEN_SET: RuleProfile(ViolationSeverity.WARNING, False),
    RuleCode.METADATA_REQUIRED_KEY_MISSING: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.METADATA_IMMUTABLE_KEY_DROPPED: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.METADATA_IMMUTABLE_KEY_CHANGED: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.METADATA_PASSTHROUGH_KEY_DROPPED: RuleProfile(ViolationSeverity.WARNING, False),
    RuleCode.TRANSITION_SOURCE_PHASE_MISMATCH: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_TARGET_PHASE_MISMATCH: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_SELF_HANDOFF: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_NOT_DECLARED_BY_SOURCE_PHASE: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_NOT_DECLARED_BY_TARGET_PHASE: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_SOURCE_OBJECT_MISSING: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_TARGET_OBJECT_MISSING: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_SOURCE_OBJECT_PHASE_MISMATCH: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_TARGET_OBJECT_PHASE_MISMATCH: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_REQUIRED_PRECONDITION_MISSING: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_STATUS_TRANSFORM_BLOCKED: RuleProfile(ViolationSeverity.ERROR, True),
    RuleCode.TRANSITION_STATUS_TRANSFORM_NOT_ALLOWED: RuleProfile(ViolationSeverity.ERROR, True),
}


def profile_for(rule_code: RuleCode) -> RuleProfile:
    return RULE_PROFILES[rule_code]
