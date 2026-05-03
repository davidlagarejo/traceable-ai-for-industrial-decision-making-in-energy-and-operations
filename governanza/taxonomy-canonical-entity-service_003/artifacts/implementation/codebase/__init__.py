"""Deterministic implementation for motor_003.

The package exposes the Taxonomy + Canonical Entity Service without AI calls or
downstream normalization logic.
"""

from .service import (
    AliasCandidate,
    AliasMappings,
    BoundaryDefinition,
    CanonicalEntity,
    RawTermCandidate,
    SourceVocabularyManifest,
    TaxonomyCanonicalEntityService,
    TaxonomyNode,
    TaxonomyPublicationResult,
    TaxonomyValidationError,
)

__all__ = [
    "AliasCandidate",
    "AliasMappings",
    "BoundaryDefinition",
    "CanonicalEntity",
    "RawTermCandidate",
    "SourceVocabularyManifest",
    "TaxonomyCanonicalEntityService",
    "TaxonomyNode",
    "TaxonomyPublicationResult",
    "TaxonomyValidationError",
]
