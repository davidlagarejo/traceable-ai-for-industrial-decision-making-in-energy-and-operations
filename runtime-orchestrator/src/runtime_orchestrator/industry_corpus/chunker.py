"""Deterministic page-aware text chunker for industry_corpus.

Why our own splitter (instead of langchain / llamaindex):
  · Determinism: same text → same chunks, byte-for-byte.
  · Zero deps: stdlib only.
  · Phase 0 respects: no LLM in the loop.

Strategy:
  1. Page boundaries are honored — `pdfplumber` separates pages with "\f".
     We don't merge across pages (a chunk = one page's content unless empty).
  2. Within a page, we accumulate words until `max_tokens` is reached, then
     extend to the next sentence boundary (`.` `!` `?`) so we don't cut
     mid-sentence.
  3. Overlap: last N tokens of chunk K appear as first N of chunk K+1.
  4. Token counting: prefer `tiktoken` if installed (cl100k); fallback to
     whitespace word count (~1.3× off but consistent run-to-run).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

DEFAULT_MAX_TOKENS: int = 512
DEFAULT_OVERLAP_TOKENS: int = 50
MIN_CHUNK_TOKENS: int = 40        # below this we drop a chunk (junk)

_SENTENCE_END = re.compile(r"[.!?](?:\s|$)")
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class TextChunk:
    page:        int    # 1-indexed page number (0 if unknown)
    text:        str
    token_count: int


# ── token counting ───────────────────────────────────────────────────


def _count_tokens(text: str) -> int:
    """Best-effort token count. Determinístico independientemente del backend."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Whitespace fallback. Roughly 1 word ≈ 1.3 tokens; we keep this
        # consistent so chunk sizes are stable across runs even without tiktoken.
        return len(_WHITESPACE.split(text.strip())) if text.strip() else 0


# ── page splitting ──────────────────────────────────────────────────


def _split_pages(text: str) -> list[tuple[int, str]]:
    """Split text by form-feed (pdfplumber page separator). Returns
    list[(page_no_1indexed, page_text)]. Empty pages are skipped."""
    parts = text.split("\f")
    out: list[tuple[int, str]] = []
    for i, p in enumerate(parts, start=1):
        if p.strip():
            out.append((i, p))
    if not out:
        # No form-feeds present → treat as single page
        if text.strip():
            out = [(1, text)]
    return out


# ── core splitter ──────────────────────────────────────────────────


def _split_page_into_chunks(
    page_no: int, page_text: str,
    max_tokens: int, overlap_tokens: int,
) -> list[TextChunk]:
    """Split a single page's text into <= max_tokens chunks with overlap."""
    words = page_text.split()
    if not words:
        return []

    chunks: list[TextChunk] = []
    i = 0
    while i < len(words):
        # Take a window of words approximating max_tokens. Whitespace fallback
        # tokens ≈ words, tiktoken tokens ≈ words * 1.3, so we start with
        # max_tokens words and trim if tiktoken says we overshot.
        window = words[i:i + max_tokens]
        candidate = " ".join(window)
        # Try to extend to next sentence end (but cap at +50 words)
        j = i + len(window)
        extension = 0
        while j < len(words) and extension < 50:
            if _SENTENCE_END.search(words[j - 1] + " "):
                break
            window.append(words[j])
            j += 1
            extension += 1
        candidate = " ".join(window)
        tok = _count_tokens(candidate)
        # If we overshot (tiktoken), trim words until under cap
        while tok > max_tokens and len(window) > 10:
            window = window[:-5]
            candidate = " ".join(window)
            tok = _count_tokens(candidate)
        if tok >= MIN_CHUNK_TOKENS:
            chunks.append(TextChunk(page=page_no, text=candidate, token_count=tok))
        # Advance with overlap
        consumed = len(window)
        step = max(1, consumed - overlap_tokens)
        i += step
        # Safety: if we somehow don't advance, force progress
        if step <= 0:
            i += 1
    return chunks


# ── public API ──────────────────────────────────────────────────────


def split(
    text: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap: int = DEFAULT_OVERLAP_TOKENS,
) -> list[TextChunk]:
    """Split `text` into deterministic, page-aware chunks.

    Returns list[TextChunk]. Empty input → []. Same input → same output.
    """
    if not text or not text.strip():
        return []
    out: list[TextChunk] = []
    for page_no, page_text in _split_pages(text):
        out.extend(_split_page_into_chunks(page_no, page_text, max_tokens, overlap))
    return out
