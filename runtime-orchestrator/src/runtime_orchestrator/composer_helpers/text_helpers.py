"""Text utilities, token extraction, concept markers, semantic redundancy.

Extracted verbatim from executive_thesis.py during composer slim
(RECOVERY_BACKLOG.md R-70/R-71). Behaviour is unchanged.

The `_CONCEPT_MARKER_MAP` here is the legacy in-process map used by
`_concept_markers` and `_is_semantically_redundant`. The richer
asset-family Pattern Library lives in `runtime_orchestrator.pattern_library`
and is not a drop-in replacement for these markers, so both coexist for
now (R-33 will retire the legacy map once the composer is fully
re-pointed).
"""
from __future__ import annotations

import re
from typing import Any


_TOKEN_STOPWORDS = {
    "and",
    "the",
    "with",
    "from",
    "into",
    "this",
    "that",
    "what",
    "when",
    "where",
    "while",
    "under",
    "over",
    "before",
    "after",
    "against",
    "between",
    "rather",
    "than",
    "does",
    "doesnt",
    "not",
    "yet",
    "can",
    "may",
    "remain",
    "remains",
    "wrong",
    "because",
    "being",
    "have",
    "has",
    "will",
    "until",
    "current",
    "main",
    "problem",
    "need",
    "needs",
}


_CONCEPT_MARKER_MAP = {
    "denominator_reframe": {"denominator", "benchmark", "comparison", "peer"},
    "boundary_reframe": {"boundary", "owner", "tenant", "control", "capture", "meter"},
    "tariff_logic": {"tariff", "demand", "peak", "charging"},
    "thermal_exchange": {"dock", "infiltration", "thermal", "refrigeration", "hvac"},
    "maintenance_reality": {"maintenance", "downtime", "reliability", "uptime"},
    "model_prematurity": {"model", "sensor", "digital", "instrumentation"},
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _list_text(values: Any) -> list[str]:
    if isinstance(values, list):
        return [str(value).strip() for value in values if str(value).strip()]
    text = _text(values)
    return [text] if text else []


def _split_compound_evidence(value: Any) -> list[str]:
    text = _text(value)
    if not text:
        return []
    if " + " in text:
        return [item.strip() for item in text.split(" + ") if item.strip()]
    return [text]


def _format_label(value: Any) -> str:
    text = _text(value).replace("_", " ")
    return " ".join(text.split())


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = _text(value)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _join_sentences(*parts: Any) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for part in parts:
        text = _text(part)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return " ".join(out)


def _tokens(*values: Any) -> set[str]:
    merged = " ".join(_text(value).lower() for value in values if _text(value))
    raw_tokens = re.findall(r"[a-z0-9]+", merged)
    return {
        token
        for token in raw_tokens
        if len(token) >= 3 and token not in _TOKEN_STOPWORDS
    }


def _overlap_score(*groups: Any) -> int:
    token_sets = [_tokens(group) for group in groups if _tokens(group)]
    if len(token_sets) < 2:
        return 0
    base = token_sets[0]
    score = 0
    for candidate in token_sets[1:]:
        score += len(base.intersection(candidate))
    return score


def _overlap_ratio(left: Any, right: Any) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    shared = len(left_tokens.intersection(right_tokens))
    return shared / max(min(len(left_tokens), len(right_tokens)), 1)


def _shared_token_count(left: Any, right: Any) -> int:
    return len(_tokens(left).intersection(_tokens(right)))


def _concept_markers(*values: Any) -> set[str]:
    tokens = _tokens(*values)
    markers: set[str] = set()
    for marker, required_tokens in _CONCEPT_MARKER_MAP.items():
        if tokens.intersection(required_tokens):
            markers.add(marker)
    return markers


def _is_semantically_redundant(
    candidate: Any,
    existing_values: list[Any],
    *,
    threshold: float = 0.7,
    allow_marker_collapse: bool = True,
    marker_overlap_token_floor: int = 1,
) -> bool:
    candidate_markers = _concept_markers(candidate)
    for existing in list(existing_values or []):
        if _overlap_ratio(candidate, existing) >= threshold:
            return True
        if not allow_marker_collapse:
            continue
        shared_markers = candidate_markers.intersection(_concept_markers(existing))
        if shared_markers and _shared_token_count(candidate, existing) >= marker_overlap_token_floor:
            return True
    return False
