"""Schemas — knowledge object data model.

Defines the canonical shape of every knowledge entry that enters the
framework via the Industrial Research Engine. Validators enforce these
shapes; without them, no knowledge can reach approved memory.

Two principal kinds:
  KnowledgeObject  — a pattern, archetype, process_logic block, etc.
  CombinationObject — a higher-order combination of patterns

Both share the base epistemic surface (id, falsification, evidence,
claim_ceiling, source_basis, asset_families, anti_families).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Enumerations ────────────────────────────────────────────────────────


KNOWLEDGE_KINDS: tuple[str, ...] = (
    "pattern",
    "combination",
    "archetype",
    "process_logic",
    "tariff",
    "maintenance",
    "refrigeration",
    "compressed_air",
    "thermal_process",
    "logistics",
    "power_quality",
    "control_boundary",
)


# Maps knowledge_kind → registry subdirectory under knowledge_pending/
# and combination_registry/ (only kinds that have a folder there).
_KIND_TO_FOLDER: dict[str, str] = {kind: kind for kind in KNOWLEDGE_KINDS}


# Claim ceiling levels per the framework's epistemic governance.
# L0 = pure prior / no evidence; L1 = bounded inference; L2 = structural
# discrimination; nothing above L2 is allowed.
CLAIM_CEILINGS: tuple[str, ...] = ("L0", "L1", "L2")


# Memory states (also see memory.py for transitions).
MEMORY_STATES: tuple[str, ...] = (
    "pending",
    "approved",
    "deprecated",
    "superseded",
    "rejected",
)


# ── KnowledgeKind helper ────────────────────────────────────────────────


class KnowledgeKind:
    """Namespace + helpers for knowledge kind values. Not a real enum
    (we keep raw strings for JSON compatibility)."""

    KINDS: tuple[str, ...] = KNOWLEDGE_KINDS

    @staticmethod
    def is_valid(kind: str) -> bool:
        return kind in KNOWLEDGE_KINDS

    @staticmethod
    def folder_for(kind: str) -> str:
        if kind not in _KIND_TO_FOLDER:
            raise ValueError(f"unknown knowledge kind: {kind!r}")
        return _KIND_TO_FOLDER[kind]


# ── Knowledge object (dataclass — JSON in/out via .to_dict / .from_dict) ─


@dataclass
class KnowledgeObject:
    """A single piece of industrial knowledge entering the framework.

    Subclasses MAY add more fields (see CombinationObject) but the base
    epistemic surface defined here is MANDATORY for every entry.
    """
    # identity
    id: str
    version: str
    knowledge_kind: str
    # asset-family scope
    asset_families: list[str] = field(default_factory=list)
    anti_families: list[str] = field(default_factory=list)
    # epistemic surface
    trigger_conditions: list[str] = field(default_factory=list)
    anti_triggers: list[str] = field(default_factory=list)
    falsification_conditions: list[str] = field(default_factory=list)
    evidence_required: list[str] = field(default_factory=list)
    # framing
    financial_translation: str = ""
    tad_actions: list[str] = field(default_factory=list)
    allowed_language: str = ""
    prohibited_language: list[str] = field(default_factory=list)
    claim_ceiling: str = "L2"
    # provenance
    source_basis: list[dict[str, Any]] = field(default_factory=list)
    extraction_metadata: dict[str, Any] = field(default_factory=dict)
    # optional free-form
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "knowledge_kind": self.knowledge_kind,
            "asset_families": list(self.asset_families),
            "anti_families": list(self.anti_families),
            "trigger_conditions": list(self.trigger_conditions),
            "anti_triggers": list(self.anti_triggers),
            "falsification_conditions": list(self.falsification_conditions),
            "evidence_required": list(self.evidence_required),
            "financial_translation": self.financial_translation,
            "tad_actions": list(self.tad_actions),
            "allowed_language": self.allowed_language,
            "prohibited_language": list(self.prohibited_language),
            "claim_ceiling": self.claim_ceiling,
            "source_basis": [dict(s) for s in self.source_basis],
            "extraction_metadata": dict(self.extraction_metadata),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "KnowledgeObject":
        return cls(
            id=str(payload.get("id", "")),
            version=str(payload.get("version", "")),
            knowledge_kind=str(payload.get("knowledge_kind", "")),
            asset_families=list(payload.get("asset_families", []) or []),
            anti_families=list(payload.get("anti_families", []) or []),
            trigger_conditions=list(payload.get("trigger_conditions", []) or []),
            anti_triggers=list(payload.get("anti_triggers", []) or []),
            falsification_conditions=list(payload.get("falsification_conditions", []) or []),
            evidence_required=list(payload.get("evidence_required", []) or []),
            financial_translation=str(payload.get("financial_translation", "")),
            tad_actions=list(payload.get("tad_actions", []) or []),
            allowed_language=str(payload.get("allowed_language", "")),
            prohibited_language=list(payload.get("prohibited_language", []) or []),
            claim_ceiling=str(payload.get("claim_ceiling", "L2")),
            source_basis=list(payload.get("source_basis", []) or []),
            extraction_metadata=dict(payload.get("extraction_metadata", {}) or {}),
            notes=str(payload.get("notes", "")),
        )


@dataclass
class CombinationObject(KnowledgeObject):
    """Combinations layer additional fields on top of KnowledgeObject."""
    required_patterns: list[str] = field(default_factory=list)
    combined_hypothesis: str = ""
    evidence_pack: dict[str, Any] = field(default_factory=dict)
    gold_nugget: str = ""
    prohibited_claims: list[str] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    conditional_clause: str = ""
    layers_combined: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({
            "required_patterns": list(self.required_patterns),
            "combined_hypothesis": self.combined_hypothesis,
            "evidence_pack": dict(self.evidence_pack),
            "gold_nugget": self.gold_nugget,
            "prohibited_claims": list(self.prohibited_claims),
            "preconditions": list(self.preconditions),
            "conditional_clause": self.conditional_clause,
            "layers_combined": list(self.layers_combined),
        })
        return d

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CombinationObject":
        base = KnowledgeObject.from_dict(payload)
        return cls(
            **{k: getattr(base, k) for k in base.__dataclass_fields__},
            required_patterns=list(payload.get("required_patterns", []) or []),
            combined_hypothesis=str(payload.get("combined_hypothesis", "")),
            evidence_pack=dict(payload.get("evidence_pack", {}) or {}),
            gold_nugget=str(payload.get("gold_nugget", "")),
            prohibited_claims=list(payload.get("prohibited_claims", []) or []),
            preconditions=list(payload.get("preconditions", []) or []),
            conditional_clause=str(payload.get("conditional_clause", "")),
            layers_combined=list(payload.get("layers_combined", []) or []),
        )
