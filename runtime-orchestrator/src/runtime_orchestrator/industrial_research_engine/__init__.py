"""Industrial Research Engine — Knowledge Schema + Proposal Layer.

This package is the canonical SCHEMA + WRITE PATH for industrial
knowledge entering the framework. It defines what a valid
KnowledgeObject / CombinationObject looks like, validates them, and
lands proposals in `knowledge_pending/<kind>/` for human review at
the dashboard.

What this package IS:
  - Schemas (KnowledgeObject, CombinationObject) and dataclasses
  - Validators (validate_knowledge, validate_combination,
    enforce_family_scope, source confidence bands)
  - Taxonomy (11 canonical industrial topics × keywords/machines/systems)
  - Family scope (16 canonical asset families)
  - Routing (research_priority_for: structural priority plan)
  - Memory state machine (5 states: pending/approved/deprecated/
    superseded/rejected)
  - Engine entrypoints (propose_knowledge, propose_knowledge_from_manual_text)

What this package IS NOT:
  - Not an extractor. Automated extraction is deterministic and lives
    in `runtime_orchestrator.zlab_skill` (local_pdf_autodraft, extractor,
    research_loop_controller). The Phase 0 constitution forbids the LLM
    from being the analytical engine.
  - Not a writer. Report writing happens in motor_019 (LLM-as-narrator,
    bounded by upstream objects) and motor_017 (LaTeX render).

Public surface — what other modules import:

    from runtime_orchestrator.industrial_research_engine import (
        KnowledgeKind, KnowledgeObject, CombinationObject,
        validate_knowledge, validate_combination,
        enforce_family_scope, route_research_for_family,
        promote_to_memory, deprecate, supersede, reject,
        propose_knowledge, propose_knowledge_from_manual_text,
    )
"""
from __future__ import annotations

from .schemas import (
    KnowledgeKind,
    KnowledgeObject,
    CombinationObject,
    KNOWLEDGE_KINDS,
    CLAIM_CEILINGS,
)
from .validators import (
    KnowledgeValidationError,
    validate_knowledge,
    validate_combination,
)
from .family_scope import (
    enforce_family_scope,
    families_conflict,
    ALL_KNOWN_ASSET_FAMILIES,
)
from .source_confidence import (
    source_confidence_for,
    SOURCE_CONFIDENCE_TIERS,
)
from .taxonomy import (
    INDUSTRIAL_TAXONOMY,
    topics_for_family,
    family_for_topic,
)
from .routing import (
    research_priority_for,
    NotImplementedExtractor,
)
from .memory import (
    MemoryState,
    promote_to_memory,
    deprecate,
    supersede,
    reject,
    list_in_state,
)
from .engine import (
    extract_knowledge,  # INTENTIONAL STUB — redirects to zlab_skill
    propose_knowledge,
    propose_knowledge_from_manual_text,
)
from .deterministic_bridge import (
    load_pattern_spec,
    pattern_spec_to_knowledge_object,
    propose_extracted_pattern,
)
from .authority_classifier import (
    audit_catalog_against_classifier,
    classify_authority_tier,
)

__all__ = [
    # schemas
    "KnowledgeKind",
    "KnowledgeObject",
    "CombinationObject",
    "KNOWLEDGE_KINDS",
    "CLAIM_CEILINGS",
    # validation
    "KnowledgeValidationError",
    "validate_knowledge",
    "validate_combination",
    # family scope
    "enforce_family_scope",
    "families_conflict",
    "ALL_KNOWN_ASSET_FAMILIES",
    # source confidence
    "source_confidence_for",
    "SOURCE_CONFIDENCE_TIERS",
    # taxonomy
    "INDUSTRIAL_TAXONOMY",
    "topics_for_family",
    "family_for_topic",
    # routing
    "research_priority_for",
    "NotImplementedExtractor",
    # memory
    "MemoryState",
    "promote_to_memory",
    "deprecate",
    "supersede",
    "reject",
    "list_in_state",
    # engine
    "extract_knowledge",
    "propose_knowledge",
    "propose_knowledge_from_manual_text",
    # deterministic bridge (V5 P3)
    "load_pattern_spec",
    "pattern_spec_to_knowledge_object",
    "propose_extracted_pattern",
    # authority_tier classifier (V5 P4)
    "classify_authority_tier",
    "audit_catalog_against_classifier",
]
