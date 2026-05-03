from __future__ import annotations

from enum import Enum, IntEnum
from typing import Iterable


class EvidenceMaturityLevel(IntEnum):
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4

    @property
    def code(self) -> str:
        return f"L{int(self)}"

    @property
    def label(self) -> str:
        return {
            self.L0: "Not Observed / Not Admissible",
            self.L1: "Benchmark / Proxy / Archetype",
            self.L2: "Asset-Specific but Unverified",
            self.L3: "Local Measured / Documented",
            self.L4: "Verified / Hardened",
        }[self]

    @property
    def short_label(self) -> str:
        return {
            self.L0: "not_observed",
            self.L1: "benchmark_proxy",
            self.L2: "asset_specific_unverified",
            self.L3: "local_measured",
            self.L4: "verified_hardened",
        }[self]

    @classmethod
    def from_any(cls, value: int | str | "EvidenceMaturityLevel") -> "EvidenceMaturityLevel":
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        normalized = str(value).strip().upper()
        if normalized in {"0", "L0"}:
            return cls.L0
        if normalized in {"1", "L1"}:
            return cls.L1
        if normalized in {"2", "L2"}:
            return cls.L2
        if normalized in {"3", "L3"}:
            return cls.L3
        if normalized in {"4", "L4"}:
            return cls.L4
        raise ValueError(f"Unsupported evidence maturity value: {value!r}")


class SourceScope(str, Enum):
    ASSET_LEVEL = "ASSET_LEVEL"
    ENTITY_LEVEL = "ENTITY_LEVEL"
    PORTFOLIO_LEVEL = "PORTFOLIO_LEVEL"
    JURISDICTION_LEVEL = "JURISDICTION_LEVEL"
    BENCHMARK_LEVEL = "BENCHMARK_LEVEL"
    DERIVED_INTERNAL = "DERIVED_INTERNAL"
    UNKNOWN = "UNKNOWN"


class SourceAuthority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RecencyState(str, Enum):
    CURRENT = "current"
    RECENT = "recent"
    STALE = "stale"
    HISTORICAL = "historical"
    UNKNOWN = "unknown"


class PermissionState(str, Enum):
    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    PROHIBITED = "prohibited"
    DEFERRED = "deferred"


def weakest_level(levels: Iterable[EvidenceMaturityLevel | int | str]) -> EvidenceMaturityLevel:
    normalized = [EvidenceMaturityLevel.from_any(level) for level in levels]
    if not normalized:
        return EvidenceMaturityLevel.L0
    return min(normalized)
