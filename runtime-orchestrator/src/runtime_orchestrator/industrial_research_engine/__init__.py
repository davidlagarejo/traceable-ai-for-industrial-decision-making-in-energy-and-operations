"""Industrial Research Engine — V4 Phase 0 infrastructure.

Per RECOVERY_V4_PHASE0_BACKLOG.md: this package defines the rails for
the framework to extract industrial knowledge from authoritative sources
(IIAR / ASHRAE / DOE / EPA / vendor handbooks) and route it through
human approval into the operational registries.

In V4 Phase 0 the actual extraction is a STUB (NotImplementedError).
Everything else — schemas, validators, family scope, source confidence,
routing taxonomy, approval workflow, memory states — is real and
testable.

Public surface (what other modules import):

  from runtime_orchestrator.industrial_research_engine import (
      KnowledgeKind, KnowledgeObject, CombinationObject,
      validate_knowledge, validate_combination,
      enforce_family_scope, route_research_for_family,
      promote_to_memory, deprecate, supersede, reject,
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
    extract_knowledge,  # STUB — raises NotImplementedError
    propose_knowledge,
)
from .pdf_extraction_interface import (
    NotImplementedPDFExtractor,
    PDFExtractionResult,
    PDFExtractor,
    default_pdf_extractor,
)
from .llm_extraction_interface import (
    LLMExtractionRequest,
    LLMExtractionResult,
    LLMExtractor,
    NotImplementedLLMExtractor,
    default_llm_extractor,
)
from .extraction_orchestrator import (
    ExtractionOrchestrator,
    ExtractionPlan,
    ExtractionResult,
)
from .pdfplumber_extractor import (
    PDFPlumberExtractor,
    make_pdfplumber_extractor,
)
from .anthropic_llm_extractor import (
    AnthropicLLMExtractor,
    AnthropicSettings,
    make_anthropic_extractor,
    DEFAULT_MODEL as ANTHROPIC_DEFAULT_MODEL,
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
    # V4 P1 extraction infrastructure
    "PDFExtractor",
    "PDFExtractionResult",
    "NotImplementedPDFExtractor",
    "default_pdf_extractor",
    "LLMExtractor",
    "LLMExtractionRequest",
    "LLMExtractionResult",
    "NotImplementedLLMExtractor",
    "default_llm_extractor",
    "ExtractionOrchestrator",
    "ExtractionPlan",
    "ExtractionResult",
    # V4 P2 real extractors
    "PDFPlumberExtractor",
    "make_pdfplumber_extractor",
    "AnthropicLLMExtractor",
    "AnthropicSettings",
    "make_anthropic_extractor",
    "ANTHROPIC_DEFAULT_MODEL",
]
