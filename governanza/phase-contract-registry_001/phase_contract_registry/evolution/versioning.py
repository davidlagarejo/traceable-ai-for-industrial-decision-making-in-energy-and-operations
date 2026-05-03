from __future__ import annotations

from ..domain.value_objects import ContractVersion
from .models import VersionChangeKind, VersionDelta


def compare_versions(source: ContractVersion, target: ContractVersion) -> VersionDelta:
    if target == source:
        return VersionDelta(source=source, target=target, change_kind=VersionChangeKind.UNCHANGED)
    if target < source:
        return VersionDelta(source=source, target=target, change_kind=VersionChangeKind.DOWNGRADE)
    if target.major != source.major:
        return VersionDelta(source=source, target=target, change_kind=VersionChangeKind.MAJOR)
    if target.minor != source.minor:
        return VersionDelta(source=source, target=target, change_kind=VersionChangeKind.MINOR)
    return VersionDelta(source=source, target=target, change_kind=VersionChangeKind.PATCH)
