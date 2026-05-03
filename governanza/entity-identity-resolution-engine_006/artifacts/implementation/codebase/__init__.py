"""Public entry point for the Entity Identity / Resolution Engine."""

from .engine import EntityIdentityResolutionEngine
from .errors import IdentityResolutionError
from .models import (
    AmbiguityFlag,
    CandidateMatch,
    EntityCluster,
    IdentityRecord,
    ResolutionConflict,
)

__all__ = [
    "AmbiguityFlag",
    "CandidateMatch",
    "EntityCluster",
    "EntityIdentityResolutionEngine",
    "IdentityRecord",
    "IdentityResolutionError",
    "ResolutionConflict",
]
