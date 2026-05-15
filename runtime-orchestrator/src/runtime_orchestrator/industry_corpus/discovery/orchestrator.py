"""Discovery orchestrator — full proactive pipeline:

  for each asset_family:
    1. discover_for_family() → list[CandidateSource]   (OSTI API)
    2. for each candidate not already in sources/<family>/:
         · write sources/<family>/<source_id>.yaml
    3. etl.ingest_source() on each new YAML
         · downloads PDF (Playwright fallback if blocked)
         · extracts text
         · chunks + auto-approves (federal whitelist)
    4. indexer.build_index(asset_family)  (only if any new chunks landed)

Designed to be called from:
  · dashboard POST /api/corpus/discover-sources
  · scripts/discover_industry_corpus.py (cron / scheduled)
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path

from ..etl import ingest_source
from ..licensed_etl import ingest_licensed_source
from ..indexer import build_index
from ..manifest import (
    CANONICAL_ASSET_FAMILIES,
    corpus_root,
)
from .osti_discoverer import CandidateSource, discover_for_family as _osti_discover
from .arxiv_discoverer import ArxivCandidate, discover_for_family as _arxiv_discover
from .licensed_journal_discoverer import (
    LicensedJournalCandidate,
    discover_for_family as _licensed_discover,
    session_status as licensed_session_status,
)


def _candidates_for_family(
    asset_family: str,
    *,
    max_per_source: int,
    include_licensed: bool = False,
) -> list:
    """Aggregate candidates from all enabled discoverers for one family.

    Sources:
      · OSTI    — always
      · arXiv   — always (cheap, no session)
      · IEEE / Springer / Scopus — only if `include_licensed=True`
        (slow; requires Playwright sessions to be authenticated)

    Returns a unified list. Each item has `source_id`, `title`, `url`,
    `asset_families`, `publisher`, `publication_date` — duck-typed across
    discoverer types.
    """
    out = []
    try:
        out.extend(_osti_discover(asset_family, max_candidates=max_per_source))
    except Exception:
        pass
    try:
        out.extend(_arxiv_discover(asset_family, max_candidates=max_per_source))
    except Exception:
        pass
    if include_licensed:
        try:
            out.extend(_licensed_discover(asset_family, max_candidates=max_per_source))
        except Exception:
            pass
    return out


def discover_for_family(asset_family: str, *, max_candidates: int = 30):
    """Wrapper kept for back-compat (OSTI-only). New callers should use
    _candidates_for_family for multi-source discovery."""
    return _osti_discover(asset_family, max_candidates=max_candidates)


@dataclass
class DiscoveryResult:
    asset_family:       str
    candidates_found:   int          = 0
    yamls_written:      int          = 0
    yamls_skipped_existing: int      = 0
    sources_ingested:   int          = 0
    chunks_added:       int          = 0
    chunks_indexed:     int          = 0
    errors:             list[str]    = field(default_factory=list)
    new_sources:        list[dict]   = field(default_factory=list)


def _yaml_path_for(corpus_dir: Path, candidate: CandidateSource) -> Path:
    """sources/<first_family>/<source_id>.yaml"""
    first_family = candidate.asset_families[0]
    return corpus_dir / "sources" / first_family / f"{candidate.source_id}.yaml"


def _yaml_already_anywhere(corpus_dir: Path, source_id: str) -> bool:
    """True if any YAML under sources/ OR sources_quarantine/ has this source_id."""
    for sub in ("sources", "sources_quarantine"):
        for p in (corpus_dir / sub).rglob(f"{source_id}.yaml"):
            if p.exists():
                return True
    return False


def _write_candidate_yaml(candidate, corpus_dir: Path) -> Path:
    """Write a YAML for ANY discoverer's candidate (OSTI or arxiv).

    License decision (controls auto-approve eligibility):
      · OSTI       → license="public_domain"        (federal)
      · arxiv      → license="open_access"          (CC license)
      · vendor     → license="vendor_whitepaper"   (trusted allowlist)
    """
    target = _yaml_path_for(corpus_dir, candidate)
    target.parent.mkdir(parents=True, exist_ok=True)

    publisher = getattr(candidate, "publisher", "")
    if publisher == "arxiv":
        license_str = "open_access"
        cats = getattr(candidate, "categories", ())
        abstract = (getattr(candidate, "abstract", "") or "")[:240]
        notes = f"Auto-discovered via arXiv API. Categories: {', '.join(cats[:3])}. Abstract: {abstract}"
    elif publisher in ("ieee", "springer", "scopus", "elsevier"):
        # Paywalled journal — license tagged so it goes to chunks_pending/
        # (NOT auto-approved). Citations must respect fair use (≤300 chars).
        license_str = "licensed_journal"
        abstract = (getattr(candidate, "abstract", "") or "")[:240]
        doi = (getattr(candidate, "doi", "") or "")[:80]
        notes = (
            f"Discovered via {publisher} licensed search. DOI: {doi}. "
            f"Abstract: {abstract}"
        )
    else:
        # OSTI / federal default
        license_str = "public_domain"
        subjects = getattr(candidate, "raw_subjects", ())
        notes = f"Auto-discovered via {publisher} API. Subjects: " + (
            ", ".join(subjects[:5]).replace('"', "'")[:200]
        )

    lines = [
        f"source_id: {candidate.source_id}",
        f"title: \"{candidate.title.replace(chr(34), chr(39))}\"",
        f"url: {candidate.url}",
        f"license: {license_str}",
        f"publisher: {publisher}",
        f"version: \"{(candidate.publication_date or 'unknown')[:10]}\"",
        f"added_at: \"{_dt.datetime.utcnow().isoformat()}Z\"",
        f"added_by: system_verified",
        f"notes: \"{notes[:280].replace(chr(34), chr(39))}\"",
        "asset_families:",
    ]
    for af in candidate.asset_families:
        lines.append(f"  - {af}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def discover_and_ingest_family(
    asset_family: str,
    *,
    max_new: int = 10,
    rebuild_index: bool = True,
    include_licensed: bool = False,
    runtime_orchestrator_dir: Path | None = None,
) -> DiscoveryResult:
    """Full proactive cycle for ONE asset_family."""
    result = DiscoveryResult(asset_family=asset_family)
    if asset_family not in CANONICAL_ASSET_FAMILIES or asset_family == "_shared":
        result.errors.append(f"invalid asset_family: {asset_family}")
        return result

    corpus_dir = corpus_root(runtime_orchestrator_dir)

    # Step 1: discover candidates from ALL enabled discoverers
    try:
        candidates = _candidates_for_family(
            asset_family, max_per_source=max_new * 2,
            include_licensed=include_licensed,
        )
    except Exception as exc:
        result.errors.append(f"discoverer_failed: {type(exc).__name__}: {exc}")
        return result
    result.candidates_found = len(candidates)

    # Step 2: filter to candidates NOT already on disk
    new_candidates: list[CandidateSource] = []
    for c in candidates:
        if _yaml_already_anywhere(corpus_dir, c.source_id):
            result.yamls_skipped_existing += 1
            continue
        new_candidates.append(c)
        if len(new_candidates) >= max_new:
            break
    if not new_candidates:
        return result

    # Step 3: write YAMLs + ingest each
    for c in new_candidates:
        try:
            yaml_path = _write_candidate_yaml(c, corpus_dir)
            result.yamls_written += 1
        except Exception as exc:
            result.errors.append(f"yaml_write_failed for {c.source_id}: {exc}")
            continue
        try:
            # Route paywall sources to licensed_etl (HTML+Playwright session);
            # everything else uses standard ingest_source (PDF+url_fetcher).
            if getattr(c, "publisher", "") in ("ieee", "springer", "scopus", "elsevier"):
                ling = ingest_licensed_source(
                    yaml_path,
                    runtime_orchestrator_dir=runtime_orchestrator_dir,
                )
                if ling.errors:
                    result.errors.append(
                        f"licensed_ingest_errors for {c.source_id}: {ling.errors[0][:140]}"
                    )
                if ling.chunks_written > 0:
                    result.sources_ingested += 1
                    result.chunks_added += ling.chunks_written
                    result.new_sources.append({
                        "source_id":        c.source_id,
                        "title":            c.title,
                        "url":              c.url,
                        "asset_families":   list(c.asset_families),
                        "publication_date": c.publication_date,
                        "chunks_written":   ling.chunks_written,
                        "auto_approved":    False,   # licensed → human review
                        "license_routed":   "chunks_pending",
                    })
            else:
                ingest = ingest_source(yaml_path,
                                       runtime_orchestrator_dir=runtime_orchestrator_dir)
                if ingest.errors:
                    result.errors.append(
                        f"ingest_errors for {c.source_id}: {ingest.errors[0][:120]}"
                    )
                if ingest.chunks_written > 0:
                    result.sources_ingested += 1
                    result.chunks_added += ingest.chunks_written
                    result.new_sources.append({
                        "source_id":      c.source_id,
                        "title":          c.title,
                        "url":            c.url,
                        "asset_families": list(c.asset_families),
                        "publication_date": c.publication_date,
                        "chunks_written": ingest.chunks_written,
                        "auto_approved":  ingest.auto_approved,
                    })
        except Exception as exc:
            result.errors.append(
                f"ingest_exception for {c.source_id}: {type(exc).__name__}: {exc}"
            )

    # Step 4: rebuild the affected family's index (only if new chunks landed)
    if rebuild_index and result.chunks_added > 0:
        try:
            stats = build_index(asset_family,
                                runtime_orchestrator_dir=runtime_orchestrator_dir)
            result.chunks_indexed = stats.chunks_indexed
            if stats.errors:
                result.errors.append(f"index_build_errors: {stats.errors[:2]}")
        except Exception as exc:
            result.errors.append(f"index_build_failed: {type(exc).__name__}: {exc}")

    return result


def discover_all_families(
    *,
    max_new_per_family: int = 5,
    runtime_orchestrator_dir: Path | None = None,
) -> list[DiscoveryResult]:
    """Run the discovery cycle across every canonical asset_family."""
    out: list[DiscoveryResult] = []
    for af in sorted(CANONICAL_ASSET_FAMILIES):
        if af == "_shared":
            continue
        out.append(discover_and_ingest_family(
            af, max_new=max_new_per_family,
            runtime_orchestrator_dir=runtime_orchestrator_dir,
        ))
    return out
