from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from .results import ValidationSeverity


class RuleCode(str, Enum):
    REGISTRY_ID_INVALID = "registry.id_invalid"
    REGISTRY_NON_ACTIVE_DECLARED = "registry.non_active_declared"
    VERSION_ID_INVALID = "version.id_invalid"
    VERSION_REGISTRY_REFERENCE_INVALID = "version.registry_reference_invalid"
    VERSION_NON_ACTIVE_DECLARED = "version.non_active_declared"
    NODE_ID_INVALID = "node.id_invalid"
    NODE_VERSION_REFERENCE_INVALID = "node.version_reference_invalid"
    NODE_TERM_REFERENCE_INVALID = "node.term_reference_invalid"
    NODE_PARENT_INVALID = "node.parent_invalid"
    NODE_PARENT_VERSION_MISMATCH = "node.parent_version_mismatch"
    NODE_PROVISIONAL_DECLARED = "node.provisional_declared"
    TERM_ID_INVALID = "term.id_invalid"
    TERM_NODE_REFERENCE_INVALID = "term.node_reference_invalid"
    TERM_DUPLICATE_LABEL_IN_VERSION = "term.duplicate_label_in_version"
    TERM_NON_ACTIVE_DECLARED = "term.non_active_declared"
    ALIAS_ID_INVALID = "alias.id_invalid"
    ALIAS_TARGET_UNRESOLVED = "alias.target_unresolved"
    ALIAS_SCOPE_CONFLICT = "alias.scope_conflict"
    ALIAS_NON_CONFIRMED_DECLARED = "alias.non_confirmed_declared"
    LEGACY_ID_INVALID = "legacy.id_invalid"
    LEGACY_TERM_REFERENCE_INVALID = "legacy.term_reference_invalid"
    LEGACY_COLLIDES_WITH_CANONICAL = "legacy.collides_with_canonical"
    LEGACY_DECLARED = "legacy.declared"
    ENTITY_ID_INVALID = "entity.id_invalid"
    ENTITY_NON_ACTIVE_DECLARED = "entity.non_active_declared"
    MEMBERSHIP_ID_INVALID = "membership.id_invalid"
    MEMBERSHIP_ENTITY_REFERENCE_INVALID = "membership.entity_reference_invalid"
    MEMBERSHIP_NODE_REFERENCE_INVALID = "membership.node_reference_invalid"
    MEMBERSHIP_NON_ACTIVE_DECLARED = "membership.non_active_declared"
    EQUIVALENCE_ID_INVALID = "equivalence.id_invalid"
    EQUIVALENCE_REF_UNRESOLVED = "equivalence.ref_unresolved"
    EQUIVALENCE_NON_CONFIRMED_DECLARED = "equivalence.non_confirmed_declared"
    MATCH_ID_INVALID = "match.id_invalid"
    MATCH_TARGET_UNRESOLVED = "match.target_unresolved"
    MATCH_PENDING_DECLARED = "match.pending_declared"
    BOUNDARY_ID_INVALID = "boundary.id_invalid"
    BOUNDARY_NODE_REFERENCE_INVALID = "boundary.node_reference_invalid"
    BOUNDARY_NEAREST_REF_UNRESOLVED = "boundary.nearest_ref_unresolved"
    BOUNDARY_NON_FINAL_DECLARED = "boundary.non_final_declared"
    JOIN_ID_INVALID = "join.id_invalid"
    JOIN_TARGET_UNRESOLVED = "join.target_unresolved"
    JOIN_NOT_SAFE_DECLARED = "join.not_safe_declared"
    DEPRECATION_ID_INVALID = "deprecation.id_invalid"
    DEPRECATION_TARGET_UNRESOLVED = "deprecation.target_unresolved"
    DEPRECATION_REPLACEMENT_UNRESOLVED = "deprecation.replacement_unresolved"
    DEPRECATION_REPLACEMENT_KIND_MISMATCH = "deprecation.replacement_kind_mismatch"
    CHANGE_ID_INVALID = "change.id_invalid"
    CHANGE_SOURCE_VERSION_UNRESOLVED = "change.source_version_unresolved"
    CHANGE_TARGET_VERSION_UNRESOLVED = "change.target_version_unresolved"
    CHANGE_AFFECTED_REF_UNRESOLVED = "change.affected_ref_unresolved"
    CHANGE_COMPARABILITY_INCOHERENT = "change.comparability_incoherent"
    INTEGRITY_ID_INVALID = "integrity.id_invalid"
    INTEGRITY_VERSION_UNRESOLVED = "integrity.version_unresolved"
    INTEGRITY_ALIAS_UNRESOLVED = "integrity.alias_unresolved"
    INTEGRITY_MATCH_UNRESOLVED = "integrity.match_unresolved"
    INTEGRITY_CONFLICT_REF_UNRESOLVED = "integrity.conflict_ref_unresolved"
    INTEGRITY_OK_BUT_PENDING_ISSUES = "integrity.ok_but_pending_issues"
    INTEGRITY_ISSUES_DECLARED = "integrity.issues_declared"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    severity: ValidationSeverity
    blocking: bool


RULE_PROFILES: dict[RuleCode, RuleProfile] = {
    RuleCode.REGISTRY_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REGISTRY_NON_ACTIVE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.VERSION_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.VERSION_REGISTRY_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.VERSION_NON_ACTIVE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.NODE_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.NODE_VERSION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.NODE_TERM_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.NODE_PARENT_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.NODE_PARENT_VERSION_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.NODE_PROVISIONAL_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.TERM_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.TERM_NODE_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.TERM_DUPLICATE_LABEL_IN_VERSION: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.TERM_NON_ACTIVE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.ALIAS_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.ALIAS_TARGET_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.ALIAS_SCOPE_CONFLICT: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.ALIAS_NON_CONFIRMED_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.LEGACY_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LEGACY_TERM_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LEGACY_COLLIDES_WITH_CANONICAL: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LEGACY_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.ENTITY_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.ENTITY_NON_ACTIVE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.MEMBERSHIP_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.MEMBERSHIP_ENTITY_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.MEMBERSHIP_NODE_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.MEMBERSHIP_NON_ACTIVE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.EQUIVALENCE_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EQUIVALENCE_REF_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EQUIVALENCE_NON_CONFIRMED_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.MATCH_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.MATCH_TARGET_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.MATCH_PENDING_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.BOUNDARY_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BOUNDARY_NODE_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BOUNDARY_NEAREST_REF_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BOUNDARY_NON_FINAL_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.JOIN_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.JOIN_TARGET_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.JOIN_NOT_SAFE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.DEPRECATION_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.DEPRECATION_TARGET_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.DEPRECATION_REPLACEMENT_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.DEPRECATION_REPLACEMENT_KIND_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.CHANGE_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.CHANGE_SOURCE_VERSION_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.CHANGE_TARGET_VERSION_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.CHANGE_AFFECTED_REF_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.CHANGE_COMPARABILITY_INCOHERENT: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.INTEGRITY_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.INTEGRITY_VERSION_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.INTEGRITY_ALIAS_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.INTEGRITY_MATCH_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.INTEGRITY_CONFLICT_REF_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.INTEGRITY_OK_BUT_PENDING_ISSUES: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.INTEGRITY_ISSUES_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
}


def profile_for(rule_code: RuleCode) -> RuleProfile:
    return RULE_PROFILES[rule_code]

