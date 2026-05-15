"""arXiv discoverer — scientific papers via the arXiv API.

API:   http://export.arxiv.org/api/query  (Atom feed)
Docs:  https://info.arxiv.org/help/api/index.html
License: arXiv allows redistribution under CC BY 4.0 or similar for most
         papers (each paper specifies). We treat them as `open_access` and
         auto-approve only if the user explicitly allows arxiv in the
         FEDERAL_AUTO_APPROVE_PUBLISHERS list (set in manifest.py — added
         to the trusted set in this PR).

Search categories mapped to asset_families:
  · cold_chain        → cs.SY (systems) + physics.flu-dyn + eess.SY
  · manufacturing     → cs.SY + eess.SY + physics.ao-ph + cond-mat.mtrl-sci
  · datacenter        → cs.DC + cs.NI + cs.PF
  · commercial_bldg   → eess.SY + physics.ao-ph
  · warehouse_dist    → cs.SY + cs.RO (robotics for warehouse automation)
  · infrastructure    → eess.SY + physics.app-ph

We further filter by keywords (industrial energy, heat transfer, etc.)
so the corpus stays on-topic.

Phase 0: deterministic keyword filtering, no LLM.
"""
from __future__ import annotations

import datetime as _dt
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .osti_discoverer import USER_AGENT


ARXIV_API = "http://export.arxiv.org/api/query"


# asset_family → (category list, keyword list) tuned for industrial energy
ARXIV_CATEGORIES: dict[str, list[str]] = {
    "cold_chain_facility": ["eess.SY", "physics.flu-dyn"],
    "manufacturing_facility": ["eess.SY", "cond-mat.mtrl-sci"],
    "datacenter": ["cs.DC", "cs.PF"],
    "commercial_building": ["eess.SY", "physics.ao-ph"],
    "warehouse_distribution": ["cs.SY", "cs.RO"],
    "infrastructure_node": ["eess.SY", "physics.app-ph"],
}

ARXIV_KEYWORDS: dict[str, list[str]] = {
    "cold_chain_facility": [
        "refrigeration system optimization",
        "ammonia heat pump",
        "industrial cold storage energy",
    ],
    "manufacturing_facility": [
        "industrial energy efficiency",
        "heat recovery manufacturing",
        "process integration energy",
        "industrial waste heat recovery",
    ],
    "datacenter": [
        "data center energy efficiency",
        "server farm thermal management",
        "PUE optimization",
    ],
    "commercial_building": [
        "commercial HVAC energy",
        "building thermal model",
        "model predictive control HVAC",
    ],
    "warehouse_distribution": [
        "warehouse energy optimization",
        "automated material handling energy",
    ],
    "infrastructure_node": [
        "grid integration renewable",
        "transmission system stability",
        "industrial power quality",
    ],
}


@dataclass(frozen=True)
class ArxivCandidate:
    publisher:        str               # "arxiv"
    source_id:        str               # "arxiv_2403.12345"
    title:            str
    url:              str               # PDF URL (always works for arxiv)
    asset_families:   tuple[str, ...]
    publication_date: str
    arxiv_id:         str
    abstract:         str
    categories:       tuple[str, ...]


_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
_ENTRY_RE = re.compile(r"<entry>(.*?)</entry>", re.DOTALL)
_ID_RE = re.compile(r"<id>(.*?)</id>")
_PUBLISHED_RE = re.compile(r"<published>(.*?)</published>")
_SUMMARY_RE = re.compile(r"<summary>(.*?)</summary>", re.DOTALL)
_CATEGORY_RE = re.compile(r'<category term="([^"]+)"')


def _parse_arxiv_atom(xml_bytes: bytes) -> list[dict[str, Any]]:
    """Minimal Atom parser for arXiv API responses (no XML deps)."""
    xml = xml_bytes.decode("utf-8", errors="replace")
    out: list[dict[str, Any]] = []
    for m in _ENTRY_RE.finditer(xml):
        body = m.group(1)
        title_m = _TITLE_RE.search(body)
        id_m = _ID_RE.search(body)
        pub_m = _PUBLISHED_RE.search(body)
        sum_m = _SUMMARY_RE.search(body)
        cats = _CATEGORY_RE.findall(body)
        if not id_m or not title_m:
            continue
        arxiv_url = id_m.group(1).strip()
        # arxiv URL: http://arxiv.org/abs/2403.12345v1 — strip version
        arxiv_id_m = re.search(r"abs/([\d.]+)", arxiv_url)
        if not arxiv_id_m:
            continue
        arxiv_id = arxiv_id_m.group(1)
        out.append({
            "arxiv_id":  arxiv_id,
            "title":     " ".join(title_m.group(1).split())[:200],
            "published": (pub_m.group(1)[:10] if pub_m else ""),
            "summary":   " ".join((sum_m.group(1) if sum_m else "").split())[:400],
            "categories": cats,
            "pdf_url":   f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        })
    return out


def _query_arxiv(
    keyword: str, category: str,
    *, max_results: int = 10, sort: str = "relevance",
) -> list[dict[str, Any]]:
    """Hit arXiv API. Returns parsed entries.

    arXiv quirk: the API's `search_query` parameter uses literal `+AND+`
    as a separator (NOT a URL-encoded space). urlencode would escape the
    plus signs to %2B and break the search. So we build the URL manually
    with quote_plus on the inner terms only.
    """
    # Inner terms (keyword) get URL-encoded so spaces become +; category is safe ASCII.
    # Use phrase matching (quotes) only for keywords that are already short.
    # For longer multi-word keywords, drop quotes so arxiv applies implicit-AND
    # across terms — much wider recall (1 → 10+ relevant hits per query).
    if len(keyword.split()) >= 3:
        kw_encoded = urllib.parse.quote_plus(keyword)
    else:
        kw_encoded = urllib.parse.quote_plus('"' + keyword + '"')
    inner = f'all:{kw_encoded}+AND+cat:{category}'
    url = (
        f"{ARXIV_API}?search_query={inner}"
        f"&start=0&max_results={max_results}"
        f"&sortBy={sort}&sortOrder=descending"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return _parse_arxiv_atom(r.read())
    except Exception:
        return []


def discover_for_family(
    asset_family: str,
    *,
    max_per_keyword: int = 5,
    max_candidates: int = 25,
) -> list[ArxivCandidate]:
    """Discover recent arXiv papers for one asset_family."""
    cats = ARXIV_CATEGORIES.get(asset_family, [])
    kws  = ARXIV_KEYWORDS.get(asset_family, [])
    if not cats or not kws:
        return []
    seen: set[str] = set()
    out: list[ArxivCandidate] = []
    for cat in cats:
        for kw in kws:
            if len(out) >= max_candidates:
                break
            for entry in _query_arxiv(kw, cat, max_results=max_per_keyword):
                aid = entry["arxiv_id"]
                if aid in seen:
                    continue
                seen.add(aid)
                out.append(ArxivCandidate(
                    publisher="arxiv",
                    source_id=f"arxiv_{aid.replace('.', '_')}",
                    title=entry["title"],
                    url=entry["pdf_url"],
                    asset_families=(asset_family,),
                    publication_date=entry["published"],
                    arxiv_id=aid,
                    abstract=entry["summary"],
                    categories=tuple(entry["categories"][:5]),
                ))
                if len(out) >= max_candidates:
                    break
    return out
