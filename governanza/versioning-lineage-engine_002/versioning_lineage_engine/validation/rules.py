from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from .results import ValidationSeverity


class RuleCode(str, Enum):
    IDENTITY_ID_INVALID = "identity.id_invalid"
    IDENTITY_KIND_INVALID = "identity.object_kind_invalid"
    IDENTITY_PHASE_SCOPE_INVALID = "identity.phase_scope_invalid"
    IDENTITY_STATUS_INVALID = "identity.status_invalid"
    IDENTITY_REPLACEMENT_STATE_INCOHERENT = "identity.replacement_state_incoherent"
    VERSION_ID_INVALID = "version.id_invalid"
    VERSION_IDENTITY_REFERENCE_INVALID = "version.identity_reference_invalid"
    VERSION_STATUS_INVALID = "version.status_invalid"
    EDGE_ID_INVALID = "edge.id_invalid"
    EDGE_ORIGIN_INVALID = "edge.origin_invalid"
    EDGE_TARGET_INVALID = "edge.target_invalid"
    EDGE_TARGET_UNRESOLVED = "edge.target_unresolved"
    EDGE_SELF_REFERENCE_FORBIDDEN = "edge.self_reference_forbidden"
    EDGE_SEMANTIC_MISMATCH = "edge.semantic_mismatch"
    SNAPSHOT_ID_INVALID = "snapshot.id_invalid"
    SNAPSHOT_OBJECT_VERSION_INVALID = "snapshot.object_version_invalid"
    SNAPSHOT_EDGE_MISSING = "snapshot.edge_missing"
    SNAPSHOT_EDGE_ORIGIN_MISMATCH = "snapshot.edge_origin_mismatch"
    REFERENCE_ID_INVALID = "reference.id_invalid"
    REFERENCE_KIND_INVALID = "reference.kind_invalid"
    REFERENCE_VERSION_EMPTY = "reference.version_empty"
    LINEAGE_OBJECT_VERSION_INVALID = "lineage.object_version_invalid"
    LINEAGE_STATUS_INVALID = "lineage.status_invalid"
    LINEAGE_COMPLETE_BUT_MISSING_REQUIRED_REF = "lineage.complete_but_missing_required_ref"
    LINEAGE_BROKEN_EDGE_UNRESOLVED = "lineage.broken_edge_unresolved"
    LINEAGE_INCOMPLETE_DECLARED = "lineage.incomplete_declared"
    LINEAGE_BROKEN_DECLARED = "lineage.broken_declared"
    STALE_OBJECT_VERSION_INVALID = "stale.object_version_invalid"
    STALE_STATUS_INVALID = "stale.status_invalid"
    STALE_TRIGGER_UNRESOLVED = "stale.trigger_unresolved"
    STALE_DECLARED = "stale.declared"
    REBUILD_TARGET_VERSION_INVALID = "rebuild.target_version_invalid"
    REBUILD_REQUIRED_REF_UNRESOLVED = "rebuild.required_ref_unresolved"
    REBUILD_EXTERNAL_REF_UNRESOLVED = "rebuild.external_ref_unresolved"
    REBUILD_EXTERNAL_REF_KIND_MISMATCH = "rebuild.external_ref_kind_mismatch"
    REBUILD_VERSION_ALIGNMENT_MISMATCH = "rebuild.version_alignment_mismatch"
    REBUILD_PARTIAL = "rebuild.partial"
    REBUILD_NOT_REBUILDABLE = "rebuild.not_rebuildable"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    severity: ValidationSeverity
    blocking: bool


RULE_PROFILES: dict[RuleCode, RuleProfile] = {
    RuleCode.IDENTITY_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.IDENTITY_KIND_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.IDENTITY_PHASE_SCOPE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.IDENTITY_STATUS_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.IDENTITY_REPLACEMENT_STATE_INCOHERENT: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.VERSION_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.VERSION_IDENTITY_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.VERSION_STATUS_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EDGE_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EDGE_ORIGIN_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EDGE_TARGET_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EDGE_TARGET_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EDGE_SELF_REFERENCE_FORBIDDEN: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EDGE_SEMANTIC_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.SNAPSHOT_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.SNAPSHOT_OBJECT_VERSION_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.SNAPSHOT_EDGE_MISSING: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.SNAPSHOT_EDGE_ORIGIN_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REFERENCE_ID_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REFERENCE_KIND_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REFERENCE_VERSION_EMPTY: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LINEAGE_OBJECT_VERSION_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LINEAGE_STATUS_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LINEAGE_COMPLETE_BUT_MISSING_REQUIRED_REF: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LINEAGE_BROKEN_EDGE_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.LINEAGE_INCOMPLETE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.LINEAGE_BROKEN_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.STALE_OBJECT_VERSION_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.STALE_STATUS_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.STALE_TRIGGER_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.STALE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.REBUILD_TARGET_VERSION_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REBUILD_REQUIRED_REF_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REBUILD_EXTERNAL_REF_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REBUILD_EXTERNAL_REF_KIND_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REBUILD_VERSION_ALIGNMENT_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REBUILD_PARTIAL: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.REBUILD_NOT_REBUILDABLE: RuleProfile(ValidationSeverity.WARNING, False),
}


def profile_for(rule_code: RuleCode) -> RuleProfile:
    return RULE_PROFILES[rule_code]
