"""Industry Corpus — RAG layer for motor_019 narrator (V10 P0).

This package adds an optional, additive retrieval layer that enriches
motor_019's narrative with verbatim citations from public industry PDFs.

CRITICAL CONSTRAINTS (Phase 0 doctrine):
  · Only motor_019 may import `retriever`.
  · Retrieval is deterministic (numpy cosine similarity, no LLM).
  · Only `chunks_approved/` is indexed. `chunks_pending/` is never reachable.
  · Feature flag `INDUSTRY_CORPUS_ENABLED=false` by default → zero impact.

Layout:
  industry_corpus/
    sources/<asset_family>/*.yaml   — source manifests
    raw_pdfs/<sha>.pdf              — downloaded binaries
    extracted_text/<sha>.txt        — pdfplumber output
    chunks_pending/<sha>/           — awaiting human approval
    chunks_approved/<sha>/          — indexed
    chunks_rejected/<sha>/          — auditable
    embeddings/<sha>/<chunk>.npy    — float32[384] per chunk
    index/<asset_family>/           — consolidated vectors.npy + manifest.json
"""
from __future__ import annotations

__all__ = ["manifest", "etl", "chunker", "embedder", "indexer", "retriever"]
