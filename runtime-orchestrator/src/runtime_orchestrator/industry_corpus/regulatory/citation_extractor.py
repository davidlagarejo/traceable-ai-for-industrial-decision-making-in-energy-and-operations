"""Regulatory citation extractor — runs over chunks_approved/ to find
every regulation/standard reference mentioned.

What it catches (deterministic regex, no LLM):
  · CFR:        "40 CFR §63.7530", "29 CFR Part 1910"
  · OSHA:       "OSHA 1910.119", "29 CFR 1910.119"
  · ASHRAE:     "ASHRAE 90.1", "ASHRAE Standard 62.1-2019"
  · NFPA:       "NFPA 70", "NFPA 13"
  · IIAR:       "IIAR Bulletin 109", "IIAR 2-2014"
  · ISO:        "ISO 50001", "ISO 14001:2015"
  · IEC:        "IEC 60079-10-1"
  · ASME:       "ASME B31.5", "ASME PTC 19.1"
  · IEEE:       "IEEE 1547", "IEEE Std 519"
  · ANSI:       "ANSI/AHRI 550"
  · DOE codes:  "10 CFR 433", "10 CFR 434", "Energy Policy Act"
  · State:      "Title 24" (California), "Local Law 97" (NYC)

Output: regulatory_corpus/citations_extracted/<run_id>.json with
  {
    "citation": "40 CFR §63",
    "type": "us_federal_cfr",
    "title": "Title 40 — Protection of Environment",
    "mentions": [
      {"chunk_id": "...", "source_id": "...", "snippet": "..."}
    ],
    "asset_families": ["manufacturing_facility", "cold_chain_facility"]
  }

This map becomes the input for ecfr_fetcher (download the actual reg
text) and applicability_mapper (which regs apply to which asset_family).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# Reuse corpus path resolution
from ..manifest import corpus_root


# ── Regex catalog ──────────────────────────────────────────────────────


_REG_PATTERNS: list[tuple[str, str, re.Pattern]] = [
    # (citation_type, jurisdiction, compiled regex)
    ("cfr", "us_federal", re.compile(
        r"\b(\d{1,2})\s*CFR\s*(?:Part\s*)?[§]?\s*(\d{1,4}(?:\.\d+(?:\([a-z0-9]+\))?)?)",
        re.IGNORECASE,
    )),
    ("osha", "us_federal", re.compile(
        r"\bOSHA\s*(?:\d+\s*CFR\s*)?(\d{4}\.\d+(?:\([a-z0-9]+\))?)",
        re.IGNORECASE,
    )),
    ("ashrae", "industry_standard", re.compile(
        r"\bASHRAE\s+(?:Standard\s+)?(\d{2,3}(?:\.\d{1,2})?(?:-\d{4})?)",
        re.IGNORECASE,
    )),
    ("nfpa", "industry_standard", re.compile(
        r"\bNFPA\s+(\d{1,4}[A-Z]?(?:-\d{4})?)",
        re.IGNORECASE,
    )),
    ("iiar", "industry_standard", re.compile(
        r"\bIIAR\s+(?:Bulletin\s+)?(\d{1,4}(?:-\d{4})?)",
        re.IGNORECASE,
    )),
    ("iso", "international_standard", re.compile(
        r"\bISO\s+(\d{3,6}(?::\d{4})?)",
    )),
    ("iec", "international_standard", re.compile(
        r"\bIEC\s+(\d{4,5}(?:-\d+)*(?::\d{4})?)",
    )),
    ("asme", "industry_standard", re.compile(
        r"\bASME\s+([A-Z]{1,4}\.?\d+(?:\.\d+)?(?:-\d{4})?)",
        re.IGNORECASE,
    )),
    ("ieee", "industry_standard", re.compile(
        r"\bIEEE\s+(?:Std\s+)?(\d{3,4}(?:\.\d+)?(?:-\d{4})?)",
        re.IGNORECASE,
    )),
    ("ansi", "industry_standard", re.compile(
        r"\bANSI(?:/[A-Z]{2,5})*\s+(\d{1,4}(?:\.\d+)?(?:-\d{4})?)",
        re.IGNORECASE,
    )),
    ("ll97_nyc", "us_local", re.compile(
        r"\bLocal\s+Law\s+(\d{1,3})(?:\s+of\s+\d{4})?",
        re.IGNORECASE,
    )),
    ("title24_ca", "us_state", re.compile(
        r"\bTitle\s+24\b(?:\s+Part\s+\d)?",
        re.IGNORECASE,
    )),
    ("epa_neshap", "us_federal", re.compile(
        r"\bNESHAP\b",
        re.IGNORECASE,
    )),
    ("doe_eis", "us_federal", re.compile(
        r"\bEnergy\s+Independence\s+and\s+Security\s+Act\b|\bEISA\s+\d{4}\b",
        re.IGNORECASE,
    )),
]


# Title hints for known regs (for human readability)
_REG_TITLES: dict[str, str] = {
    "40 cfr 60":   "Standards of Performance for New Stationary Sources",
    "40 cfr 63":   "NESHAP — National Emission Standards for Hazardous Air Pollutants",
    "40 cfr 82":   "Protection of Stratospheric Ozone (ODS/HFCs)",
    "40 cfr 98":   "Mandatory Greenhouse Gas Reporting Rule",
    "29 cfr 1910": "Occupational Safety and Health Standards (general industry)",
    "29 cfr 1910.119": "OSHA Process Safety Management of Highly Hazardous Chemicals",
    "10 cfr 433":  "Energy Efficiency Standards for New Federal Commercial Buildings",
    "10 cfr 434":  "Energy Code for New Federal Commercial and Multi-Family High Rise Residential Buildings",
    "10 cfr 110":  "Export and Import of Nuclear Equipment and Material",
    "ashrae 90.1": "Energy Standard for Buildings Except Low-Rise Residential",
    "ashrae 62.1": "Ventilation for Acceptable Indoor Air Quality",
    "ashrae 15":   "Safety Standard for Refrigeration Systems",
    "ashrae 34":   "Designation and Classification of Refrigerants",
    "iiar 2":      "Standard for Design of Safe Closed-Circuit Ammonia Refrigeration Systems",
    "iiar 109":   "Minimum System Safety Requirements for Existing Closed-Circuit Ammonia Refrigeration Systems",
    "iso 50001":  "Energy management systems — Requirements with guidance for use",
    "iso 14001":  "Environmental management systems",
    "iso 9001":   "Quality management systems",
    "nfpa 70":    "National Electrical Code (NEC)",
    "nfpa 13":    "Standard for the Installation of Sprinkler Systems",
    "nfpa 70e":   "Standard for Electrical Safety in the Workplace",
    "asme b31.5": "Refrigeration Piping and Heat Transfer Components",
    "asme b31.3": "Process Piping",
    "ieee 1547":  "Standard for Interconnection and Interoperability of Distributed Energy Resources",
    "ll97":       "NYC Local Law 97 — building emissions limits",
    "title 24":   "California Building Standards Code (Title 24 CCR)",
}


@dataclass
class CitationHit:
    citation:        str        # canonical form e.g. "40 cfr 63"
    citation_type:   str        # cfr / osha / ashrae / ...
    jurisdiction:    str        # us_federal / industry_standard / ...
    title:           str        # human-readable
    chunk_id:        str
    source_id:       str
    source_url:      str
    snippet:         str        # context (±80 chars around the match)
    asset_families:  tuple[str, ...] = ()


@dataclass
class CitationExtractionReport:
    ran_at:          str = ""
    chunks_scanned:  int = 0
    citations_total: int = 0
    by_citation:     dict[str, list[CitationHit]] = field(default_factory=lambda: defaultdict(list))
    by_type:         dict[str, int] = field(default_factory=lambda: defaultdict(int))


def _canonicalize(citation_type: str, raw_match: str) -> str:
    """Make citation comparable across runs (lowercase, normalized spaces)."""
    text = re.sub(r"\s+", " ", raw_match.strip()).lower()
    text = text.replace("§", "").replace("part ", "").strip()
    return f"{citation_type} {text}".strip() if citation_type == "cfr" else text


def _extract_from_text(text: str) -> list[tuple[str, str, str, str]]:
    """Return list of (citation_canonical, citation_type, jurisdiction, snippet)."""
    out: list[tuple[str, str, str, str]] = []
    if not text:
        return out
    for ctype, jur, regex in _REG_PATTERNS:
        for m in regex.finditer(text):
            raw = m.group(0)
            # Build a canonical form: "<type> <captured number>"
            if m.groups():
                # use the most specific captured group
                captured = " ".join(g for g in m.groups() if g)
                canonical = _canonicalize(ctype, captured)
            else:
                canonical = _canonicalize(ctype, raw)
            start = max(0, m.start() - 80)
            end = min(len(text), m.end() + 80)
            snippet = text[start:end].replace("\n", " ").strip()
            out.append((canonical, ctype, jur, snippet))
    return out


def _title_for(canonical: str) -> str:
    """Look up a human title, or fall back to title-casing the canonical."""
    return _REG_TITLES.get(canonical, canonical.title())


def _iter_approved_chunks(corpus_dir: Path) -> Iterable[dict]:
    """Walk every approved chunk JSON."""
    root = corpus_dir / "chunks_approved"
    if not root.exists():
        return
    for p in sorted(root.rglob("*.json")):
        try:
            yield json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue


def extract_all_citations(
    *,
    runtime_orchestrator_dir: Path | None = None,
    write_report: bool = True,
) -> CitationExtractionReport:
    """Scan every approved chunk and produce a regulatory citation map.

    Returns a CitationExtractionReport. Idempotent — same corpus → same map.
    """
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    report = CitationExtractionReport(
        ran_at=_dt.datetime.utcnow().isoformat() + "Z",
    )

    for chunk in _iter_approved_chunks(corpus_dir):
        report.chunks_scanned += 1
        text = str(chunk.get("text") or "")
        for canonical, ctype, jur, snippet in _extract_from_text(text):
            hit = CitationHit(
                citation       = canonical,
                citation_type  = ctype,
                jurisdiction   = jur,
                title          = _title_for(canonical),
                chunk_id       = str(chunk.get("chunk_id") or ""),
                source_id      = str(chunk.get("source_id") or ""),
                source_url     = str(chunk.get("source_url") or ""),
                snippet        = snippet[:280],
                asset_families = tuple(chunk.get("asset_families") or []),
            )
            report.by_citation[canonical].append(hit)
            report.by_type[ctype] += 1
            report.citations_total += 1

    if write_report:
        out_dir = corpus_dir.parent / "regulatory_corpus" / "citations_extracted"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{report.ran_at[:19].replace(':','-')}.json"
        payload = {
            "ran_at":          report.ran_at,
            "chunks_scanned":  report.chunks_scanned,
            "citations_total": report.citations_total,
            "by_type":         dict(report.by_type),
            "by_citation": [
                {
                    "citation":       cit,
                    "type":           hits[0].citation_type if hits else "",
                    "jurisdiction":   hits[0].jurisdiction if hits else "",
                    "title":          hits[0].title if hits else "",
                    "mention_count":  len(hits),
                    "asset_families": sorted({fam for h in hits for fam in (h.asset_families or [])}),
                    "sources":        sorted({h.source_id for h in hits})[:20],
                    "sample_snippets": [h.snippet for h in hits[:3]],
                }
                for cit, hits in sorted(
                    report.by_citation.items(),
                    key=lambda kv: -len(kv[1]),
                )
            ],
        }
        out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                            encoding="utf-8")

    return report


def top_citations(report: CitationExtractionReport, n: int = 20) -> list[tuple[str, int, str]]:
    """Return top-N (citation, mention_count, title) tuples."""
    rows = sorted(
        report.by_citation.items(), key=lambda kv: -len(kv[1])
    )[:n]
    return [(cit, len(hits), _title_for(cit)) for cit, hits in rows]
