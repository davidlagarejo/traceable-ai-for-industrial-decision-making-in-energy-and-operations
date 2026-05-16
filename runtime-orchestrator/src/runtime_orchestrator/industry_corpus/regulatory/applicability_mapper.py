"""Applicability mapper — cruza el corpus con la regulatory_corpus para
producir, por asset_family, qué regulaciones aplican Y dónde aparecen
referenciadas.

Output: regulatory_corpus/applicability/<asset_family>.json con:
  [
    {
      "citation": "40 cfr 63",
      "title": "NESHAP — Hazardous Air Pollutants",
      "regulation_in_corpus": true|false,    # ¿descargada via eCFR?
      "regulation_source_id": "us_federal_40_cfr_0063",
      "mention_count_in_corpus": 12,
      "asset_families_inferred": [...],
      "evidence": [
        {"chunk_id": "...", "source_id": "...", "snippet": "..."}
      ]
    }
  ]

Esto es lo que motor_028 / motor_012 puede consultar al armar el
facility_prior para decir: "este facility de manufacturing está sujeto
a 40 CFR 63, 29 CFR 1910, 10 CFR 433, ASHRAE 90.1…"
"""
from __future__ import annotations

import datetime as _dt
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..manifest import CANONICAL_ASSET_FAMILIES, corpus_root
from .citation_extractor import extract_all_citations, _title_for


def _regs_in_corpus(corpus_dir: Path) -> dict[str, str]:
    """Map canonical citation form → source_id of the eCFR YAML we already
    downloaded. Used to know if we already have the regulation's text.
    """
    regs_dir = corpus_dir.parent / "regulatory_corpus" / "regulations" / "us_federal"
    out: dict[str, str] = {}
    if not regs_dir.exists():
        return out
    for yp in regs_dir.glob("*.yaml"):
        # filename pattern: NN_cfr_PPPP.yaml
        stem = yp.stem  # e.g. "40_cfr_0060"
        parts = stem.split("_")
        if len(parts) >= 3 and parts[1].lower() == "cfr":
            try:
                title = int(parts[0])
                part = int(parts[2])
                # citation_extractor canonical: "cfr {title} {part}"
                canonical_a = f"cfr {title} {part}"
                canonical_b = f"cfr {title}.0 {part}"
                source_id = f"us_federal_{title:02d}_cfr_{part:04d}"
                out[canonical_a] = source_id
                out[canonical_b] = source_id
                # alternative: full-text form may show as "{title} cfr {part}"
                out[f"{title} cfr {part}"] = source_id
            except Exception:
                continue
    return out


def build_applicability_map(
    *,
    runtime_orchestrator_dir: Path | None = None,
    write_per_family: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Run the citation extractor + cross-reference with downloaded regs.

    Returns {asset_family: [{citation, title, ...}, ...]} sorted by
    mention frequency (descending).
    """
    report = extract_all_citations(
        runtime_orchestrator_dir=runtime_orchestrator_dir,
        write_report=False,
    )
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    have_regs = _regs_in_corpus(corpus_dir)

    # Bucket every citation hit by every asset_family it touches
    by_family: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for citation, hits in report.by_citation.items():
        for h in hits:
            fams = h.asset_families or ("_shared",)
            for fam in fams:
                by_family[fam][citation].append(h)

    # Convert to JSON-friendly structure, sorted by mention count
    out: dict[str, list[dict[str, Any]]] = {}
    for fam, citations in by_family.items():
        rows = []
        for citation, hits in sorted(citations.items(), key=lambda kv: -len(kv[1])):
            rows.append({
                "citation":              citation,
                "title":                 _title_for(citation),
                "regulation_in_corpus":  citation in have_regs,
                "regulation_source_id":  have_regs.get(citation, ""),
                "mention_count_in_corpus": len(hits),
                "asset_families_inferred": sorted({
                    af for h in hits for af in (h.asset_families or [])
                }),
                "evidence_sources":      sorted({h.source_id for h in hits})[:10],
                "sample_snippets":       [h.snippet for h in hits[:3]],
            })
        out[fam] = rows

    if write_per_family:
        target_dir = corpus_dir.parent / "regulatory_corpus" / "applicability"
        target_dir.mkdir(parents=True, exist_ok=True)
        for fam, rows in out.items():
            if fam not in CANONICAL_ASSET_FAMILIES:
                continue
            (target_dir / f"{fam}.json").write_text(
                json.dumps({
                    "ran_at":         _dt.datetime.utcnow().isoformat() + "Z",
                    "asset_family":   fam,
                    "regulations":    rows,
                    "total":          len(rows),
                    "with_text":      sum(1 for r in rows if r["regulation_in_corpus"]),
                }, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
    return out


def applicability_for(
    asset_family: str,
    *,
    runtime_orchestrator_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Convenience reader — load the applicability JSON for one family.
    Returns [] if it hasn't been built yet.
    """
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    p = corpus_dir.parent / "regulatory_corpus" / "applicability" / f"{asset_family}.json"
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("regulations", [])
    except Exception:
        return []
