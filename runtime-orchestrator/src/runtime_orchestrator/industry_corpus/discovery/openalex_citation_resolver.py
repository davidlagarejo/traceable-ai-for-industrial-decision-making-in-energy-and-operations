"""Citation-driven discovery via OpenAlex API.

OpenAlex (https://api.openalex.org) is a free, open scholarly metadata
service — successor to Microsoft Academic. No API key required.

Pipeline:
  1. Scan chunks_approved/ for citation markers:
     · DOI patterns: 10.\\d+/...
     · "References" section + author/year tokens
  2. Query OpenAlex by DOI or title → returns metadata + open access PDF URL
  3. For each OA paper found, materialize a source YAML pointing to the
     freely-redistributable PDF (license = open_access_journal)
  4. Standard ETL ingests + indexes

Phase 0:
  · regex-based DOI extraction (no LLM)
  · OpenAlex is read-only metadata lookup
  · Only OA papers (oa_status in {gold, hybrid, green, diamond}) are
    materialized — closed papers are skipped (cannot legally redistribute).
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


OPENALEX_API = "https://api.openalex.org/works"
USER_AGENT = (
    "Mozilla/5.0 ZLab-CitationResolver/1.0 "
    "(contact: davidlagarejo@gmail.com; framework: zlab-otf)"
)


# DOI: 10.{registry}/{suffix}
_DOI_RE = re.compile(
    r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+",
)


@dataclass(frozen=True)
class OpenAlexCandidate:
    publisher:        str = "openalex"
    source_id:        str = ""
    title:            str = ""
    url:              str = ""           # pdf_url (open access)
    doi:              str = ""
    asset_families:   tuple[str, ...] = ()
    publication_date: str = ""
    abstract:         str = ""
    oa_status:        str = ""           # gold / hybrid / green / closed
    cited_by_count:   int = 0
    raw_subjects:     tuple[str, ...] = ()


def _http_get_json(url: str, timeout: int = 15) -> Any:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept":     "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def extract_dois_from_corpus(
    *, runtime_orchestrator_dir: Path | None = None,
    max_dois: int = 500,
) -> list[tuple[str, list[str]]]:
    """Scan chunks_approved/ for DOI patterns. Returns
    [(doi, [source_ids_where_seen])] de-duplicated.
    """
    from ..manifest import corpus_root
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    root = corpus_dir / "chunks_approved"
    if not root.exists():
        return []
    by_doi: dict[str, set[str]] = defaultdict(set)
    for p in root.rglob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        text = str(d.get("text") or "")
        for m in _DOI_RE.finditer(text):
            doi = m.group(0).rstrip(".,;)")
            by_doi[doi].add(str(d.get("source_id") or ""))
            if len(by_doi) >= max_dois:
                break
        if len(by_doi) >= max_dois:
            break
    return [(d, sorted(srcs)) for d, srcs in by_doi.items()]


def resolve_doi(doi: str) -> OpenAlexCandidate | None:
    """Query OpenAlex by DOI. Returns OpenAlexCandidate if OA available."""
    url = f"{OPENALEX_API}/https://doi.org/{urllib.parse.quote(doi, safe='/')}"
    try:
        data = _http_get_json(url)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    oa = data.get("open_access") or {}
    oa_status = str(oa.get("oa_status") or "")
    # Only keep papers with a usable OA PDF link
    pdf_url = oa.get("oa_url") or ""
    if not pdf_url or oa_status in ("closed", ""):
        return None
    # Build OpenAlex candidate
    title = (data.get("title") or "").strip()[:250]
    pub_date = str(data.get("publication_date") or "")[:10]
    aid = data.get("id", "").rsplit("/", 1)[-1]   # 'W123456'
    # Asset family inference: we can't infer well from OpenAlex concepts,
    # so default to ("_shared",); the caller can override.
    concepts = data.get("concepts") or []
    raw_subjects = tuple(c.get("display_name", "") for c in concepts[:5] if c)
    abstract_inv = data.get("abstract_inverted_index") or {}
    # OpenAlex's abstract is inverted-indexed; reconstruct
    abstract = ""
    if isinstance(abstract_inv, dict) and abstract_inv:
        positions: list[tuple[int, str]] = []
        for word, idxs in abstract_inv.items():
            for i in idxs:
                positions.append((i, word))
        positions.sort()
        abstract = " ".join(w for _, w in positions)[:400]
    return OpenAlexCandidate(
        publisher        = "openalex",
        source_id        = f"openalex_{aid.lower()}",
        title            = title,
        url              = pdf_url,
        doi              = doi,
        asset_families   = ("_shared",),
        publication_date = pub_date,
        abstract         = abstract,
        oa_status        = oa_status,
        cited_by_count   = int(data.get("cited_by_count") or 0),
        raw_subjects     = raw_subjects,
    )


def discover_from_corpus_citations(
    *,
    asset_family: str = "_shared",
    max_dois: int = 100,
    max_resolved: int = 30,
    runtime_orchestrator_dir: Path | None = None,
) -> list[OpenAlexCandidate]:
    """Walk every DOI in the corpus, resolve via OpenAlex, return only
    open-access papers we can ingest.
    """
    dois = extract_dois_from_corpus(
        runtime_orchestrator_dir=runtime_orchestrator_dir,
        max_dois=max_dois,
    )
    out: list[OpenAlexCandidate] = []
    for doi, _sources in dois:
        if len(out) >= max_resolved:
            break
        cand = resolve_doi(doi)
        if not cand:
            continue
        # Re-tag with the requested asset_family
        out.append(OpenAlexCandidate(
            publisher=cand.publisher, source_id=cand.source_id,
            title=cand.title, url=cand.url, doi=cand.doi,
            asset_families=(asset_family,) if asset_family != "_shared" else ("_shared",),
            publication_date=cand.publication_date,
            abstract=cand.abstract, oa_status=cand.oa_status,
            cited_by_count=cand.cited_by_count,
            raw_subjects=cand.raw_subjects,
        ))
    return out
