"""Retriever — single public API for motor_019.

retrieve(query, asset_family, k, min_similarity) → list[RetrievedChunk]

Guarantees:
  · Deterministic: same query + same index → same top-k (numpy dot product).
  · Read-only: never touches chunks_pending/.
  · Graceful: if index missing or deps unavailable → returns []. Never raises.
  · Phase 0 safe: zero LLM calls. Cosine similarity only.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from .manifest import CANONICAL_ASSET_FAMILIES, corpus_root

logger = logging.getLogger(__name__)


DEFAULT_K: int = 5
DEFAULT_MIN_SIMILARITY: float = 0.35


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id:        str
    source_id:       str
    source_url:      str
    page:            int
    text:            str
    similarity:      float
    asset_families:  tuple[str, ...]


# ── Index loading (cached) ─────────────────────────────────────────


@dataclass(frozen=True)
class _LoadedIndex:
    vectors:   np.ndarray       # (N, dim), L2-normalized
    manifest:  list[dict[str, Any]]
    model:     str
    dim:       int


@lru_cache(maxsize=8)
def _load_index(asset_family: str, corpus_dir_str: str) -> _LoadedIndex | None:
    """Load the index for one asset_family. Returns None if absent or invalid."""
    if asset_family not in CANONICAL_ASSET_FAMILIES:
        return None
    corpus_dir = Path(corpus_dir_str)
    idx_dir = corpus_dir / "index" / asset_family
    v_file = idx_dir / "vectors.npy"
    m_file = idx_dir / "manifest.json"
    if not v_file.exists() or not m_file.exists():
        return None
    try:
        vectors = np.load(v_file)
        manifest = json.loads(m_file.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("industry_corpus: failed to load index for %s: %s",
                       asset_family, exc)
        return None
    rows = manifest.get("rows") or []
    if vectors.shape[0] != len(rows):
        logger.warning("industry_corpus: index row mismatch for %s (vectors=%d, rows=%d)",
                       asset_family, vectors.shape[0], len(rows))
        return None
    # Ensure unit-norm (idempotent if already normalized)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors = (vectors / norms).astype(np.float32)
    return _LoadedIndex(
        vectors=vectors, manifest=rows,
        model=str(manifest.get("model_name", "")),
        dim=int(manifest.get("dim", vectors.shape[1])),
    )


def clear_cache() -> None:
    """Used in tests / after corpus rebuilds."""
    _load_index.cache_clear()


# ── Public API ─────────────────────────────────────────────────────


def retrieve(
    query: str,
    asset_family: str,
    *,
    k: int = DEFAULT_K,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    runtime_orchestrator_dir: Path | None = None,
) -> list[RetrievedChunk]:
    """Return top-k chunks for `query` filtered by `asset_family`.

    Behavior:
      · Empty / missing index → return [] (no error).
      · k <= 0 → return [].
      · sentence-transformers missing → return [], log once.
    """
    if not query or not query.strip() or k <= 0:
        return []
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    idx = _load_index(asset_family, str(corpus_dir))
    if idx is None:
        return []

    try:
        from .embedder import embed_one
        q = embed_one(query)
    except ImportError:
        logger.warning("industry_corpus: embedder unavailable → retrieve returns []")
        return []
    except Exception as exc:
        logger.warning("industry_corpus: query embed failed: %s", exc)
        return []
    if q.shape != (idx.dim,):
        logger.warning("industry_corpus: query dim mismatch (q=%d index=%d)",
                       q.shape[0], idx.dim)
        return []

    # cosine == dot product since both sides are L2-normalized
    sims = (idx.vectors @ q).astype(np.float32)
    # top-k via argpartition (faster than full sort for large N)
    n = sims.shape[0]
    if n == 0:
        return []
    k_eff = min(k, n)
    # argpartition gets the k highest; then sort those k descending
    top_idx = np.argpartition(-sims, k_eff - 1)[:k_eff]
    top_idx = top_idx[np.argsort(-sims[top_idx])]

    results: list[RetrievedChunk] = []
    for i in top_idx:
        s = float(sims[int(i)])
        if s < min_similarity:
            continue
        row = idx.manifest[int(i)]
        # Re-read the chunk to get its full text (we don't store text in
        # manifest.json to keep it small; it lives in chunks_approved/<sha>/)
        chunk_text = _read_chunk_text(corpus_dir, row)
        results.append(RetrievedChunk(
            chunk_id       = row["chunk_id"],
            source_id      = row["source_id"],
            source_url     = row.get("source_url", ""),
            page           = int(row.get("page", 0)),
            text           = chunk_text,
            similarity     = round(s, 4),
            asset_families = tuple(row.get("asset_families", []) or []),
        ))
    return results


def _read_chunk_text(corpus_dir: Path, row: dict[str, Any]) -> str:
    """Lazy-load chunk text from disk. Empty string if missing."""
    chunk_id = row.get("chunk_id", "")
    short = chunk_id.split("::")[-1] if chunk_id else ""
    if not short:
        return ""
    p = corpus_dir / "chunks_approved" / str(row.get("source_sha", "")) / f"{short}.json"
    if not p.exists():
        return ""
    try:
        return str(json.loads(p.read_text(encoding="utf-8")).get("text", ""))
    except Exception:
        return ""


# ── Diagnostics ────────────────────────────────────────────────────


def index_status(
    *, runtime_orchestrator_dir: Path | None = None,
) -> dict[str, Any]:
    """Return per-family stats — what's available right now."""
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    out: dict[str, Any] = {}
    for af in sorted(CANONICAL_ASSET_FAMILIES):
        if af == "_shared":
            continue
        idx = _load_index(af, str(corpus_dir))
        if idx is None:
            out[af] = {"available": False, "chunks": 0}
        else:
            out[af] = {
                "available": True,
                "chunks":    int(idx.vectors.shape[0]),
                "dim":       idx.dim,
                "model":     idx.model,
            }
    return out
