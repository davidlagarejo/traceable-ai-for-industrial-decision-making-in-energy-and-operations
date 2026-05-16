"""Strategy 1 — Corpus co-occurrence.

Algoritmo (100% determinístico, sin LLM):

  Para cada par/triple de patterns en active_patterns:
    1. Query individual por pattern → top-K chunks (set A, set B, set C)
    2. Overlap = |A ∩ B (∩ C)| / max(|A|, |B|, |C|)
    3. Si overlap ≥ MIN_OVERLAP → los MISMOS chunks hablan de TODOS los
       patterns → evidencia fuerte de co-ocurrencia temática
    4. Refuerzo adicional: query combinado debe superar MIN_COMBINED_SIM

  Para cada candidate:
    · hipótesis = texto verbatim del chunk overlap con max similarity
    · corpus_citations = los chunks compartidos (overlap)
    · regulatory_basis = regs aplicables a asset_family (via evidence_wire)
    · confidence_score = overlap_ratio × combined_top_sim

Phase 0 inscribed: la hipótesis NUNCA se parafrasea. Se copia el chunk text.
"""
from __future__ import annotations

import itertools
import datetime as _dt
import hashlib
from typing import Any

from .proposer import ProposedCombination


# Thresholds (deterministic; mismo input → mismas combinations)
INDIVIDUAL_K:       int   = 8        # top-K chunks por query individual
MIN_OVERLAP_RATIO:  float = 0.20     # ≥20% de los top-K coinciden
MIN_COMBINED_SIM:   float = 0.30     # sim mínimo del top combined chunk
MAX_PAIRS_EVALUATED:   int = 50
MAX_TRIPLES_EVALUATED: int = 50


def _retrieve(query: str, asset_family: str, k: int = 3) -> list:
    """Wrapper sobre el retriever del corpus. Fail-silent si corpus
    no disponible (devuelve [])."""
    try:
        from runtime_orchestrator.industry_corpus.retriever import retrieve
    except Exception:
        return []
    try:
        return retrieve(query, asset_family, k=k, min_similarity=0.10) or []
    except Exception:
        return []


def _pattern_chunks(pattern_id: str, asset_family: str,
                    k: int = INDIVIDUAL_K) -> list:
    """Top-K chunks que matchean ESTE pattern solo. Cacheable per-run."""
    q = pattern_id.replace("_", " ")
    return _retrieve(q, asset_family, k=k)


def _overlap(sets: list[set[str]]) -> tuple[set[str], float]:
    """Return (intersection, overlap_ratio).

    overlap_ratio = |intersection| / max(|set|) — proporción de chunks
    que aparecen en TODAS las queries del grupo respecto al set más grande.
    """
    if not sets:
        return set(), 0.0
    intersection = set.intersection(*sets) if all(sets) else set()
    largest = max(len(s) for s in sets) or 1
    return intersection, len(intersection) / largest


def _stable_id(method: str, patterns: list[str], asset_family: str) -> str:
    """ID estable basado en sorted pattern_set + asset_family + method.
    Si mismo conjunto se propone otra vez → mismo id → dedup natural."""
    key = "|".join([method, asset_family, ",".join(sorted(patterns))])
    suffix = hashlib.sha256(key.encode()).hexdigest()[:8]
    fam_short = asset_family.replace("_facility", "").replace("_", "")[:10]
    pats_short = "_".join(sorted(p.split("_")[0] for p in patterns))[:50]
    return f"auto_corpus_{fam_short}_{pats_short}_{suffix}"


def _build_candidate_from_combined_hits(
    patterns: list[str],
    asset_family: str,
    combined_hits: list,
    individual_max: float,
    combined_top_sim: float,
) -> ProposedCombination:
    """Construye un ProposedCombination a partir de los hits del query
    combinado. La hipótesis es el texto VERBATIM del top chunk."""
    top = combined_hits[0]
    verbatim = (top.text or "").strip()
    # Cortar a primera oración o 300 chars (lo que pase primero)
    cut = min(300, len(verbatim))
    for end_char in (". ", "! ", "? "):
        idx = verbatim.find(end_char, 80, cut + 80)
        if idx > 0:
            cut = idx + 1
            break
    hypothesis_quote = verbatim[:cut].strip()
    hypothesis = (
        f'"{hypothesis_quote}" [{top.source_id}::{top.chunk_id}]'
    )

    corpus_citations = [
        {
            "chunk_id":   h.chunk_id,
            "source_id":  h.source_id,
            "source_url": h.source_url,
            "page":       h.page,
            "verbatim":   (h.text or "")[:600],
            "similarity": round(h.similarity, 4),
        }
        for h in combined_hits[:3]
    ]

    # Regulatory basis via evidence_wire (top 5)
    try:
        from runtime_orchestrator.industry_corpus.evidence_wire import (
            regulatory_applicability_for,
        )
        regs = regulatory_applicability_for(asset_family, max_entries=5) or []
        regulatory_basis = [
            {"citation": r.citation, "title": r.title,
             "has_text_in_corpus": r.has_text_in_corpus}
            for r in regs
        ]
    except Exception:
        regulatory_basis = []

    confidence = (combined_top_sim - individual_max) / max(1 - individual_max, 0.01)
    confidence = max(0.0, min(1.0, confidence))

    cand_id = _stable_id("corpus", patterns, asset_family)

    return ProposedCombination(
        id                    = cand_id,
        pattern_set           = sorted(patterns),
        proposal_method       = "corpus_cooccurrence",
        generated_at          = _dt.datetime.utcnow().isoformat() + "Z",
        generated_by          = "framework_auto",
        status                = "pending_human_review",
        confidence_score      = round(confidence, 4),
        combined_hypothesis   = hypothesis,
        strategic_risk        = (
            "Los patterns aparecen co-mencionados en literatura técnica "
            "del sector — investigarlos en conjunto puede revelar una "
            "causa raíz compartida no evidente al verlos por separado."
        ),
        context_predicates    = {},   # Strategy 1 no añade predicados
                                       # (eso lo hace Strategy 3)
        corpus_citations      = corpus_citations,
        regulatory_basis      = regulatory_basis,
        decision_implication  = {
            "action": "INVESTIGATE_TOGETHER",
            "note":   "Patterns con co-ocurrencia significativa en corpus.",
        },
        consequence_if_ignored = [
            "Análisis pattern-by-pattern puede no capturar la causa raíz "
            "compartida que la literatura sí reconoce."
        ],
        anti_triggers         = [],
        asset_families        = [asset_family],
    )


def propose_from_corpus(
    *,
    asset_family:    str,
    active_patterns: list[str],
    max_candidates:  int = 30,
) -> list[ProposedCombination]:
    """Generate candidates via Strategy 1 (corpus co-occurrence).

    Algoritmo de overlap:
      Para cada pair/triple: si las top-K chunks que mencionan a cada
      pattern individualmente OVERLAP ≥ 20% → los mismos chunks hablan
      de todos los patterns → fuerte señal de co-mención temática.
    """
    if len(active_patterns) < 2:
        return []
    patterns = list(set(active_patterns))[:12]   # cap inputs

    # Pre-fetch top-K chunks per pattern (1 query c/u)
    per_pattern_chunks: dict[str, list] = {
        p: _pattern_chunks(p, asset_family) for p in patterns
    }
    # Overlap a nivel de SOURCE (mismo documento menciona el pattern).
    # Más realista que chunk-level: dos patterns mencionados en el mismo
    # PDF/source son co-ocurrentes aunque sean párrafos distintos.
    per_pattern_source_ids: dict[str, set[str]] = {
        p: {h.source_id for h in hits} for p, hits in per_pattern_chunks.items()
    }
    per_pattern_chunk_ids: dict[str, set[str]] = {
        p: {h.chunk_id for h in hits} for p, hits in per_pattern_chunks.items()
    }

    candidates: list[ProposedCombination] = []
    seen_pattern_sets: set[tuple[str, ...]] = set()

    def _make_candidate(
        patterns_in: list[str],
        intersection_chunk_ids: set[str],
        overlap_ratio: float,
    ) -> ProposedCombination | None:
        """Build candidate from chunks shared across all patterns."""
        # Recoger los chunks de la intersección (con su similarity más alta
        # entre los pattern-queries)
        shared_hits: dict[str, Any] = {}
        for p in patterns_in:
            for h in per_pattern_chunks.get(p, []):
                if h.chunk_id not in intersection_chunk_ids:
                    continue
                prev = shared_hits.get(h.chunk_id)
                if prev is None or h.similarity > prev.similarity:
                    shared_hits[h.chunk_id] = h
        if not shared_hits:
            return None
        # Ordena por similarity descendente
        ordered = sorted(shared_hits.values(), key=lambda h: -h.similarity)
        top = ordered[0]
        if top.similarity < MIN_COMBINED_SIM:
            return None
        return _build_candidate_from_combined_hits(
            patterns       = patterns_in,
            asset_family   = asset_family,
            combined_hits  = ordered[:3],
            individual_max = top.similarity,   # placeholder
            combined_top_sim = top.similarity * overlap_ratio + top.similarity * (1 - overlap_ratio),
        )

    # ── Pairs ──
    for pair in list(itertools.combinations(patterns, 2))[:MAX_PAIRS_EVALUATED]:
        if len(candidates) >= max_candidates:
            break
        signature = tuple(sorted(pair))
        if signature in seen_pattern_sets:
            continue
        source_sets = [per_pattern_source_ids[p] for p in pair]
        common_sources, source_ratio = _overlap(source_sets)
        if source_ratio < MIN_OVERLAP_RATIO or not common_sources:
            continue
        # Para construir el candidate, recoger los chunks de los patterns
        # cuyo source_id está en common_sources
        intersection_chunks: set[str] = set()
        for p in pair:
            for h in per_pattern_chunks[p]:
                if h.source_id in common_sources:
                    intersection_chunks.add(h.chunk_id)
        cand = _make_candidate(list(pair), intersection_chunks, source_ratio)
        if cand is None:
            continue
        cand.confidence_score = round(source_ratio, 4)
        candidates.append(cand)
        seen_pattern_sets.add(signature)

    # ── Triples ──
    if len(candidates) < max_candidates:
        for trip in list(itertools.combinations(patterns, 3))[:MAX_TRIPLES_EVALUATED]:
            if len(candidates) >= max_candidates:
                break
            signature = tuple(sorted(trip))
            if signature in seen_pattern_sets:
                continue
            source_sets = [per_pattern_source_ids[p] for p in trip]
            common_sources, source_ratio = _overlap(source_sets)
            # Triples requieren overlap ligeramente mayor
            if source_ratio < MIN_OVERLAP_RATIO + 0.05 or not common_sources:
                continue
            intersection_chunks: set[str] = set()
            for p in trip:
                for h in per_pattern_chunks[p]:
                    if h.source_id in common_sources:
                        intersection_chunks.add(h.chunk_id)
            cand = _make_candidate(list(trip), intersection_chunks, source_ratio)
            if cand is None:
                continue
            cand.confidence_score = round(source_ratio, 4)
            candidates.append(cand)
            seen_pattern_sets.add(signature)

    return candidates
