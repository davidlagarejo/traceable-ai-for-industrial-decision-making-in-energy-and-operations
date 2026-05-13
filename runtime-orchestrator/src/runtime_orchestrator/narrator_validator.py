"""V5 P7 — narrator orphan-claim validator.

motor_019 (LLM Writing Engine) already enforces Phase 0's "no soberanía
LLM" rule via `_lint_text`:
  - forbidden phrases (transaction / underwriting / due diligence)
  - closure phrases (verified, confirmed, certified)
  - instruction-leakage phrases
  - unsupported numeric tokens
  - word-count limit

V5 P7 adds the **orphan-claim detector**: a sentence-level check that
flags any sentence whose significant tokens have NO overlap with the
`source_facts` packet. Each orphan sentence is a candidate hallucination
— the LLM wrote something the upstream framework didn't supply.

This is pure additive validation. No prompt or LLM-call change. Drops
into `_lint_text` as one extra violation source.

Phase 0 anchor: the framework refuses to publish prose the upstream
context cannot support. The LLM is a writer, not an analyst.
"""
from __future__ import annotations

import json
import re
from typing import Any, Iterable, Mapping


# Words too common to count as "semantic anchor" between source and prose.
_COMMON_STOPWORDS: frozenset[str] = frozenset({
    "the", "a", "an", "of", "to", "in", "on", "at", "for", "by", "with",
    "and", "or", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "their", "them", "they",
    "we", "our", "us", "you", "your", "i", "me", "my",
    "but", "not", "no", "yes", "if", "then", "than", "so", "such",
    "can", "could", "may", "might", "should", "would", "will", "shall",
    "do", "does", "did", "have", "has", "had", "having",
    "any", "all", "some", "each", "every", "both", "more", "less", "most",
    "very", "much", "many", "few", "several",
    "el", "la", "los", "las", "un", "una", "y", "o", "de", "del", "en", "con", "por",
    "para", "que", "este", "esta", "estos", "estas", "su", "sus", "lo",
    "es", "son", "ser", "estar", "ha", "han", "haber", "no", "si",
    "está", "están", "estoy", "estamos", "estuvo", "estuvieron", "eran",
    "fueron", "fue", "sido", "siendo", "será", "serán",
    "muy", "más", "menos", "también", "tampoco", "ya", "aún", "todavía",
    # Framework-domain stopwords (very generic — would always match)
    "framework", "report", "analysis", "case", "system", "section", "view",
    "data", "information", "context", "evidence",
})


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])")
_TOKEN_RE = re.compile(r"[a-záéíóúñ0-9]+", re.IGNORECASE)


def _significant_tokens(text: str) -> set[str]:
    """Tokenize text and drop stopwords + very short tokens."""
    if not text:
        return set()
    tokens = set()
    for match in _TOKEN_RE.findall(text.lower()):
        if len(match) < 4:
            continue
        if match in _COMMON_STOPWORDS:
            continue
        tokens.add(match)
    return tokens


def _split_sentences(text: str) -> list[str]:
    """Crude sentence splitter — good enough for orphan detection."""
    if not text or not text.strip():
        return []
    pieces = _SENTENCE_SPLIT_RE.split(text.strip())
    return [p.strip() for p in pieces if p.strip()]


def _flatten_source_text(source_facts: Mapping[str, Any] | Any) -> str:
    """Serialize source_facts to one searchable text blob."""
    if source_facts is None:
        return ""
    try:
        return json.dumps(source_facts, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(source_facts)


def check_orphan_claims(
    source_facts: Mapping[str, Any] | Any,
    text: str,
    *,
    min_significant_tokens: int = 2,
    allow_list: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Return a list of orphan-sentence findings.

    Each finding:
      {
        "sentence_index": int,
        "sentence_excerpt": str (max 120 chars),
        "significant_tokens": [str, ...],
        "reason": "no_token_overlap_with_source_facts",
      }

    Args:
      source_facts: the packet["source_facts"] dict that the LLM had access to.
      text: the LLM-generated prose to audit.
      min_significant_tokens: a sentence with fewer significant tokens
        than this is skipped (too short to assess).
      allow_list: extra tokens to consider always-supported (e.g., the
        target_type, target asset family name).
    """
    source_text = _flatten_source_text(source_facts)
    source_tokens = _significant_tokens(source_text)
    if allow_list:
        for term in allow_list:
            source_tokens.update(_significant_tokens(str(term)))

    findings: list[dict[str, Any]] = []
    for idx, sentence in enumerate(_split_sentences(text)):
        sentence_tokens = _significant_tokens(sentence)
        if len(sentence_tokens) < min_significant_tokens:
            continue
        if sentence_tokens & source_tokens:
            continue
        excerpt = sentence[:120] + ("…" if len(sentence) > 120 else "")
        findings.append({
            "sentence_index": idx,
            "sentence_excerpt": excerpt,
            "significant_tokens": sorted(sentence_tokens)[:8],
            "reason": "no_token_overlap_with_source_facts",
        })
    return findings


def summarize_orphan_findings(
    findings: list[dict[str, Any]],
) -> str:
    """Compact summary string suitable for embedding in violations list."""
    if not findings:
        return ""
    return (
        f"orphan_claims={len(findings)}:"
        + ",".join(
            f"#{f['sentence_index']}({f['sentence_excerpt'][:40]})"
            for f in findings[:3]
        )
        + ("…" if len(findings) > 3 else "")
    )
