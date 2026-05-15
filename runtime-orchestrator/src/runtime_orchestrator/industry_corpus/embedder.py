"""Embedder — wraps sentence-transformers MiniLM for the corpus.

Model: `sentence-transformers/all-MiniLM-L6-v2`
  · 384-dim float32 vectors
  · Determinístico en CPU (greedy decoding, no sampling)
  · ~80 MB, baja UNA vez a ~/.cache/huggingface

Why MiniLM (not text-embedding-3-small or BGE):
  · Local-first: no API key, no per-query cost.
  · Determinístico: necesario para reproducibility de retrieval.
  · Bueno para English technical text (industry corpus es 95% inglés).

Fallback: si sentence-transformers no está instalado, las funciones
levantan ImportError con un mensaje claro. El indexer/retriever capturan
y degradan silenciosamente (corpus deshabilitado en runtime).
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

# numpy is a hard dep — already in framework
import numpy as np


DEFAULT_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBED_DIM:  int = 384


# ── Model wrapper ───────────────────────────────────────────────────


@lru_cache(maxsize=2)
def _load_model(model_name: str):
    """Lazy, cached. Falla con ImportError claro si sentence-transformers
    no está instalado."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "sentence-transformers is required for industry_corpus embeddings. "
            "Install: pip install sentence-transformers"
        ) from exc
    return SentenceTransformer(model_name, device="cpu")


@dataclass(frozen=True)
class EmbedderInfo:
    model_name: str
    dim:        int
    backend:    str = "sentence-transformers"


def model_info(model_name: str = DEFAULT_MODEL_NAME) -> EmbedderInfo:
    m = _load_model(model_name)
    return EmbedderInfo(model_name=model_name, dim=m.get_sentence_embedding_dimension())


# ── Embedding ───────────────────────────────────────────────────────


def embed_one(text: str, *, model_name: str = DEFAULT_MODEL_NAME) -> np.ndarray:
    """Return a L2-normalized float32 vector for `text`. Shape: (dim,)."""
    if not text or not text.strip():
        return np.zeros(DEFAULT_EMBED_DIM, dtype=np.float32)
    m = _load_model(model_name)
    v = m.encode([text], convert_to_numpy=True, normalize_embeddings=True,
                 show_progress_bar=False)
    return np.asarray(v[0], dtype=np.float32)


def embed_batch(texts: list[str], *, model_name: str = DEFAULT_MODEL_NAME,
                batch_size: int = 32) -> np.ndarray:
    """Return (N, dim) float32 L2-normalized matrix."""
    if not texts:
        return np.zeros((0, DEFAULT_EMBED_DIM), dtype=np.float32)
    m = _load_model(model_name)
    arr = m.encode(texts, convert_to_numpy=True, normalize_embeddings=True,
                   batch_size=batch_size, show_progress_bar=False)
    return np.asarray(arr, dtype=np.float32)


# ── Manifest written next to embeddings/ for auditability ──────────


def write_model_manifest(corpus_dir: Path,
                         model_name: str = DEFAULT_MODEL_NAME) -> Path:
    """Persist the model identity. If this file changes, all embeddings
    must be rebuilt."""
    info = model_info(model_name)
    target = corpus_dir / "embeddings" / "_model_manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "model_name": info.model_name,
        "dim":        info.dim,
        "backend":    info.backend,
        "manifest_sha": hashlib.sha256(info.model_name.encode()).hexdigest()[:16],
    }, indent=2), encoding="utf-8")
    return target


def read_model_manifest(corpus_dir: Path) -> dict[str, Any] | None:
    p = corpus_dir / "embeddings" / "_model_manifest.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
