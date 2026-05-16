"""industry_evidence_wire — API ÚNICA que cualquier motor importa para
obtener evidence (corpus + regulatory) sobre un objeto del pipeline.

Diseño: opt-in, side-effect-free, fail-silent. Si el corpus o el
regulatory layer no están disponibles, devuelve estructuras vacías —
los motors siguen funcionando idénticos a antes.

Funciones públicas:
  · evidence_for_pattern(pattern_id, asset_family) → EvidenceBundle
  · evidence_for_combination(combination, asset_family) → EvidenceBundle
  · regulatory_applicability_for(asset_family) → list[reg dicts]
  · industry_support_score(claim_text, asset_family) → float (0-1)

Cada Bundle lleva:
  · corpus_citations: list de chunks con sim > umbral
  · regulatory_basis: regs aplicables al asset_family que mencionan al menos
                      uno de los pattern_ids del combo (vía citation_extractor)
  · support_score: 0-1 — fuerza relativa del soporte
  · TAD signals: counts que el TAD usa para priorizar

Phase 0 doctrine:
  · Determinístico, cero LLM.
  · Feature flag INDUSTRY_CORPUS_ENABLED ya gobierna activación (auto/true/false).
  · Phase 0 inscribed: este módulo NO toma decisiones — solo aporta material
    citable a quien lo pida. Los motors siguen tomando sus decisiones bajo
    sus propias reglas; este wire les da con qué citar la justificación.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Lazy imports + caching for perf — retriever load is ~1s
try:
    from .retriever import retrieve as _corpus_retrieve, index_status as _index_status
    _CORPUS_OK = True
except Exception:
    _CORPUS_OK = False
    _corpus_retrieve = None
    _index_status = None


def _corpus_enabled() -> bool:
    """Same gate as motor_019: auto/true → on, false → off."""
    raw = os.environ.get("INDUSTRY_CORPUS_ENABLED", "auto").strip().lower()
    if raw in ("false", "0", "off", "no"):
        return False
    if raw in ("true", "1", "on", "yes"):
        return True
    if not _CORPUS_OK or _index_status is None:
        return False
    try:
        status = _index_status() or {}
    except Exception:
        return False
    return any(bool(s.get("available")) for s in status.values())


# ── Dataclasses ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class EvidenceCitation:
    chunk_id:    str
    source_id:   str
    source_url:  str
    page:        int
    text:        str
    similarity:  float


@dataclass(frozen=True)
class RegulatoryBasisEntry:
    citation:           str          # "40 cfr 63"
    title:              str
    has_text_in_corpus: bool         # True if we already downloaded its fulltext
    regulation_source_id: str        # if downloaded, the source_id
    mention_count_in_corpus: int


@dataclass
class EvidenceBundle:
    asset_family:       str = ""
    query:              str = ""
    corpus_citations:   list[EvidenceCitation] = field(default_factory=list)
    regulatory_basis:   list[RegulatoryBasisEntry] = field(default_factory=list)
    support_score:      float = 0.0
    # TAD priority signals — counts only, motors apply their own weighting
    tad_signals:        dict[str, int | float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_family":    self.asset_family,
            "query":           self.query,
            "corpus_citations": [
                {"chunk_id": c.chunk_id, "source_id": c.source_id,
                 "source_url": c.source_url, "page": c.page,
                 "text": c.text[:600], "similarity": c.similarity}
                for c in self.corpus_citations
            ],
            "regulatory_basis": [
                {"citation": r.citation, "title": r.title,
                 "has_text_in_corpus": r.has_text_in_corpus,
                 "regulation_source_id": r.regulation_source_id,
                 "mention_count_in_corpus": r.mention_count_in_corpus}
                for r in self.regulatory_basis
            ],
            "support_score":  round(self.support_score, 4),
            "tad_signals":    dict(self.tad_signals),
        }


# ── Regulatory applicability loader ────────────────────────────────────


def _applicability_path(corpus_root_dir: Path | None = None) -> Path | None:
    """Path to regulatory_corpus/applicability/."""
    try:
        from .manifest import corpus_root
        base = corpus_root(corpus_root_dir).parent
    except Exception:
        return None
    return base / "regulatory_corpus" / "applicability"


def regulatory_applicability_for(
    asset_family: str,
    *,
    runtime_orchestrator_dir: Path | None = None,
    max_entries: int = 25,
) -> list[RegulatoryBasisEntry]:
    """Load regulatory_corpus/applicability/<asset_family>.json and return
    the top-N regulations sorted by mention frequency.

    If the file isn't built yet (or applicability_mapper hasn't run),
    returns []. Caller can re-build via dashboard /api/corpus/...
    """
    if not asset_family:
        return []
    ap_dir = _applicability_path(runtime_orchestrator_dir)
    if ap_dir is None:
        return []
    p = ap_dir / f"{asset_family}.json"
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    regs = data.get("regulations") or []
    out: list[RegulatoryBasisEntry] = []
    for r in regs[:max_entries]:
        out.append(RegulatoryBasisEntry(
            citation              = str(r.get("citation", "")),
            title                 = str(r.get("title", "")),
            has_text_in_corpus    = bool(r.get("regulation_in_corpus", False)),
            regulation_source_id  = str(r.get("regulation_source_id", "")),
            mention_count_in_corpus = int(r.get("mention_count_in_corpus", 0)),
        ))
    return out


# ── Corpus retrieval wrappers ─────────────────────────────────────────


def _safe_retrieve(query: str, asset_family: str, *,
                   k: int = 3, min_sim: float = 0.30) -> list:
    if not _corpus_enabled() or _corpus_retrieve is None:
        return []
    try:
        return _corpus_retrieve(query, asset_family, k=k, min_similarity=min_sim) or []
    except Exception:
        return []


def evidence_for_pattern(
    pattern_id: str,
    asset_family: str,
    *,
    k: int = 3,
    min_similarity: float = 0.30,
    extra_query_terms: str = "",
) -> EvidenceBundle:
    """Find supporting evidence in the industry corpus for ONE pattern_id.

    Query is built from pattern_id (slug → text) + asset_family + optional
    extra terms. Returns top-k chunks above similarity threshold.
    """
    query_text = pattern_id.replace("_", " ").strip()
    if extra_query_terms:
        query_text = f"{query_text} {extra_query_terms}".strip()
    bundle = EvidenceBundle(asset_family=asset_family, query=query_text)
    hits = _safe_retrieve(query_text, asset_family, k=k, min_sim=min_similarity)
    bundle.corpus_citations = [
        EvidenceCitation(
            chunk_id=h.chunk_id, source_id=h.source_id,
            source_url=h.source_url, page=h.page,
            text=h.text, similarity=h.similarity,
        ) for h in hits
    ]
    if bundle.corpus_citations:
        bundle.support_score = sum(c.similarity for c in bundle.corpus_citations) / len(bundle.corpus_citations)
    bundle.tad_signals = {
        "corpus_citation_count": len(bundle.corpus_citations),
        "max_similarity":        max((c.similarity for c in bundle.corpus_citations), default=0.0),
        "mean_similarity":       bundle.support_score,
    }
    return bundle


def evidence_for_combination(
    combination: dict[str, Any],
    asset_family: str,
    *,
    k_per_pattern: int = 2,
    min_similarity: float = 0.30,
    max_total_citations: int = 6,
) -> EvidenceBundle:
    """Find supporting evidence for a combination (dict with pattern_ids).

    1. Retrieve top-k chunks for the combination's `combined_hypothesis`
       as a single query → captures cross-pattern semantic signal.
    2. Also retrieve top-(k_per_pattern) for each pattern_id individually.
    3. Dedup, cap at `max_total_citations`.
    4. Pull regulatory_basis for the asset_family.
    5. Surface TAD signals: how well-supported is this combo?
    """
    combo_id = str(combination.get("id") or combination.get("name") or "combination")
    combined_hypothesis = str(combination.get("combined_hypothesis") or "")
    pattern_ids: list[str] = list(combination.get("pattern_ids") or [])
    if not pattern_ids:
        return EvidenceBundle(asset_family=asset_family, query=combo_id)
    bundle = EvidenceBundle(asset_family=asset_family, query=combo_id)

    # Aggregate retrieval
    seen_chunks: set[str] = set()
    all_citations: list[EvidenceCitation] = []
    # Combined-hypothesis query (best semantic signal)
    if combined_hypothesis:
        hits = _safe_retrieve(combined_hypothesis, asset_family,
                              k=k_per_pattern + 1, min_sim=min_similarity)
        for h in hits:
            if h.chunk_id in seen_chunks:
                continue
            seen_chunks.add(h.chunk_id)
            all_citations.append(EvidenceCitation(
                chunk_id=h.chunk_id, source_id=h.source_id,
                source_url=h.source_url, page=h.page,
                text=h.text, similarity=h.similarity,
            ))
    # Per-pattern retrieval
    for pid in pattern_ids:
        if len(all_citations) >= max_total_citations:
            break
        hits = _safe_retrieve(
            pid.replace("_", " "), asset_family,
            k=k_per_pattern, min_sim=min_similarity,
        )
        for h in hits:
            if h.chunk_id in seen_chunks:
                continue
            seen_chunks.add(h.chunk_id)
            all_citations.append(EvidenceCitation(
                chunk_id=h.chunk_id, source_id=h.source_id,
                source_url=h.source_url, page=h.page,
                text=h.text, similarity=h.similarity,
            ))
            if len(all_citations) >= max_total_citations:
                break
    # Sort descending by similarity
    all_citations.sort(key=lambda c: -c.similarity)
    bundle.corpus_citations = all_citations[:max_total_citations]

    # Regulatory basis — filter to regs whose canonical citation matches
    # any of the pattern keywords, OR (default) top-N for the asset_family
    all_regs = regulatory_applicability_for(asset_family, max_entries=50)
    pattern_keywords = {p.lower().replace("_", " ") for p in pattern_ids}
    # Try matching pattern_keywords against reg titles
    matched_regs = []
    for reg in all_regs:
        title_lc = reg.title.lower()
        if any(kw[:15] in title_lc for kw in pattern_keywords if len(kw) > 4):
            matched_regs.append(reg)
    # If nothing matched, take top-5 by mention_count (most cited regs for family)
    bundle.regulatory_basis = matched_regs[:8] if matched_regs else all_regs[:5]

    if bundle.corpus_citations:
        bundle.support_score = sum(c.similarity for c in bundle.corpus_citations) / len(bundle.corpus_citations)

    bundle.tad_signals = {
        "corpus_citation_count":     len(bundle.corpus_citations),
        "max_similarity":            max((c.similarity for c in bundle.corpus_citations), default=0.0),
        "mean_similarity":           bundle.support_score,
        "regulatory_basis_count":    len(bundle.regulatory_basis),
        "regulatory_mandate_count":  sum(1 for r in bundle.regulatory_basis if r.has_text_in_corpus),
    }
    return bundle


def industry_support_score(
    claim_text: str,
    asset_family: str,
    *,
    min_similarity: float = 0.35,
) -> float:
    """Quick TAD signal: how well does the corpus support this claim?
    Returns the top-1 similarity. 0.0 if no support.
    """
    hits = _safe_retrieve(claim_text, asset_family, k=1, min_sim=min_similarity)
    if not hits:
        return 0.0
    return float(hits[0].similarity)


# ── TAD priority decorator ────────────────────────────────────────────


def decorate_tad_priority(
    base_priority_score: float,
    *,
    bundle: EvidenceBundle | None = None,
    asset_family: str = "",
    claim_text: str = "",
    weight_corpus: float = 0.15,
    weight_regulatory: float = 0.10,
) -> dict[str, Any]:
    """Bump a TAD priority score using industry+regulatory evidence.

    Bonus = weight_corpus × min(mean_similarity, 1.0)
          + weight_regulatory × min(mandate_count / 5, 1.0)

    Returns dict for traceability:
      {original, bonus, decorated, breakdown: {…}, evidence_summary: {…}}
    """
    if bundle is None and claim_text and asset_family:
        bundle = evidence_for_pattern(claim_text, asset_family)
    if bundle is None:
        return {
            "original": base_priority_score,
            "bonus":    0.0,
            "decorated": base_priority_score,
            "breakdown": {"corpus_bonus": 0.0, "regulatory_bonus": 0.0,
                          "note": "no evidence bundle"},
        }
    corpus_signal = float(bundle.tad_signals.get("mean_similarity", 0.0))
    reg_mandate = int(bundle.tad_signals.get("regulatory_mandate_count", 0))
    corpus_bonus = weight_corpus * min(corpus_signal, 1.0)
    reg_bonus    = weight_regulatory * min(reg_mandate / 5.0, 1.0)
    bonus = corpus_bonus + reg_bonus
    return {
        "original":  round(base_priority_score, 4),
        "bonus":     round(bonus, 4),
        "decorated": round(base_priority_score + bonus, 4),
        "breakdown": {
            "corpus_bonus":     round(corpus_bonus, 4),
            "regulatory_bonus": round(reg_bonus, 4),
            "weight_corpus":    weight_corpus,
            "weight_regulatory": weight_regulatory,
        },
        "evidence_summary": {
            "corpus_citation_count":    bundle.tad_signals.get("corpus_citation_count", 0),
            "regulatory_mandate_count": reg_mandate,
            "mean_similarity":          corpus_signal,
        },
    }
