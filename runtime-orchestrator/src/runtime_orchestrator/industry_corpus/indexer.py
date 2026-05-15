"""Indexer — builds per-asset_family vector indices from approved chunks.

For each asset_family in CANONICAL_ASSET_FAMILIES:
  1. Read every chunk JSON under industry_corpus/chunks_approved/ whose
     asset_families includes (asset_family OR "_shared").
  2. For each chunk: compute embedding (or load cached) → save to
     industry_corpus/embeddings/<source_sha>/<chunk_id_short>.npy.
  3. Concatenate into industry_corpus/index/<asset_family>/vectors.npy
     and write a manifest.json with row→chunk_id mapping.

Determinism:
  · Embeddings are L2-normalized → cosine = dot product.
  · Row order = sorted(chunk_id). Same input → same vectors.npy bytes.

This module is run OFFLINE via scripts/build_industry_corpus_index.py.
No motor in the pipeline calls it at runtime.
"""
from __future__ import annotations

import datetime as _dt
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .manifest import (
    CANONICAL_ASSET_FAMILIES,
    CorpusChunk,
    corpus_root,
    load_chunk_json,
)
from .embedder import (
    DEFAULT_EMBED_DIM,
    DEFAULT_MODEL_NAME,
    embed_batch,
    write_model_manifest,
)


@dataclass
class IndexStats:
    asset_family:        str
    chunks_indexed:      int          = 0
    new_embeddings:      int          = 0
    cached_embeddings:   int          = 0
    vectors_file:        str          = ""
    manifest_file:       str          = ""
    dim:                 int          = 0
    errors:              list[str]    = field(default_factory=list)


def _chunk_filename_for_embedding(chunk: CorpusChunk) -> str:
    """Filename to use under embeddings/<source_sha>/. Stable per chunk."""
    # chunk_id is "<source_sha8>::chunk_NNNN" — take the second part
    short = chunk.chunk_id.split("::")[-1]
    return f"{short}.npy"


def _gather_approved_chunks(
    corpus_dir: Path, asset_family: str,
) -> list[CorpusChunk]:
    """Return chunks under chunks_approved/ that match the asset_family
    OR _shared. Sorted by chunk_id for deterministic ordering."""
    out: list[CorpusChunk] = []
    approved_root = corpus_dir / "chunks_approved"
    if not approved_root.exists():
        return out
    for json_file in sorted(approved_root.rglob("*.json")):
        try:
            ch = load_chunk_json(json_file)
        except Exception:
            continue
        if asset_family in ch.asset_families or "_shared" in ch.asset_families:
            out.append(ch)
    out.sort(key=lambda c: c.chunk_id)
    return out


def _embed_or_load(
    chunk: CorpusChunk, corpus_dir: Path, model_name: str,
) -> tuple[np.ndarray, bool]:
    """Load cached embedding or compute fresh. Returns (vec, was_new)."""
    target_dir = corpus_dir / "embeddings" / chunk.source_sha
    target_file = target_dir / _chunk_filename_for_embedding(chunk)
    if target_file.exists():
        try:
            v = np.load(target_file)
            if v.shape == (DEFAULT_EMBED_DIM,) and v.dtype == np.float32:
                return v, False
        except Exception:
            pass
    # Fresh compute
    v = embed_batch([chunk.text], model_name=model_name)[0]
    target_dir.mkdir(parents=True, exist_ok=True)
    np.save(target_file, v)
    return v, True


def build_index(
    asset_family: str,
    *,
    runtime_orchestrator_dir: Path | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> IndexStats:
    """Build (or refresh) the index for ONE asset_family."""
    if asset_family not in CANONICAL_ASSET_FAMILIES:
        return IndexStats(
            asset_family=asset_family,
            errors=[f"unknown asset_family {asset_family!r}"],
        )
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    stats = IndexStats(asset_family=asset_family)

    chunks = _gather_approved_chunks(corpus_dir, asset_family)
    if not chunks:
        stats.errors.append("no approved chunks for this asset_family")
        return stats

    # Embed each chunk (cached if already on disk)
    vectors: list[np.ndarray] = []
    manifest_rows: list[dict] = []
    for ch in chunks:
        try:
            v, was_new = _embed_or_load(ch, corpus_dir, model_name)
        except Exception as exc:
            stats.errors.append(f"embed failed for {ch.chunk_id}: {exc}")
            continue
        if was_new:
            stats.new_embeddings += 1
        else:
            stats.cached_embeddings += 1
        vectors.append(v)
        manifest_rows.append({
            "row":            len(vectors) - 1,
            "chunk_id":       ch.chunk_id,
            "source_id":      ch.source_id,
            "source_sha":     ch.source_sha,
            "source_url":     ch.source_url,
            "page":           ch.page,
            "asset_families": list(ch.asset_families),
            "text_sha":       ch.text_sha,
            "token_count":    ch.token_count,
        })

    if not vectors:
        stats.errors.append("0 embeddings produced")
        return stats

    matrix = np.vstack(vectors).astype(np.float32)
    stats.dim = matrix.shape[1]
    stats.chunks_indexed = matrix.shape[0]

    # Write index
    idx_dir = corpus_dir / "index" / asset_family
    idx_dir.mkdir(parents=True, exist_ok=True)
    vectors_file = idx_dir / "vectors.npy"
    manifest_file = idx_dir / "manifest.json"
    np.save(vectors_file, matrix)
    manifest_file.write_text(json.dumps({
        "asset_family":  asset_family,
        "built_at":      _dt.datetime.utcnow().isoformat() + "Z",
        "model_name":    model_name,
        "dim":           stats.dim,
        "chunk_count":   stats.chunks_indexed,
        "rows":          manifest_rows,
    }, indent=2), encoding="utf-8")
    stats.vectors_file = str(vectors_file)
    stats.manifest_file = str(manifest_file)

    # Persist model manifest globally (so retriever can verify compatibility)
    write_model_manifest(corpus_dir, model_name)
    return stats


def build_all_indices(
    *,
    runtime_orchestrator_dir: Path | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[IndexStats]:
    """Build indices for every canonical asset_family that has approved chunks."""
    out: list[IndexStats] = []
    for af in sorted(CANONICAL_ASSET_FAMILIES):
        if af == "_shared":
            continue   # _shared is included in every other family's index
        out.append(build_index(
            af, runtime_orchestrator_dir=runtime_orchestrator_dir,
            model_name=model_name,
        ))
    return out
