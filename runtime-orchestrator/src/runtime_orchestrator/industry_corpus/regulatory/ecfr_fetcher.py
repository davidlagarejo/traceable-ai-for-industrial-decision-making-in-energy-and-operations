"""eCFR fetcher — descarga el texto real de regulaciones US federales.

API:  https://www.ecfr.gov/api/versioner/v1/
Docs: https://www.ecfr.gov/reader-aids/ecfr-developer-resources/rest-api-interactive-documentation

Cobertura: TODOS los CFRs (Title 1-50). Free, sin API key.

Pipeline:
  citation_extractor → list of "40 cfr 63", "29 cfr 1910.119", …
    ↓
  ecfr_fetcher.fetch_cfr_part(title, part) → XML/JSON con el texto
    ↓
  guarda como industry_corpus/regulatory_corpus/regulations/us_federal/<reg>.yaml
    + chunkea el texto regulatorio → industry_corpus/chunks_approved/
    (license=us_federal_regulation, auto-approve)
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ECFR_API_BASE = "https://www.ecfr.gov/api/versioner/v1"
ECFR_STRUCTURE_URL = "https://www.ecfr.gov/api/versioner/v1/structure/{date}/title-{title}.json"
ECFR_FULL_XML_URL = "https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
ECFR_PART_HTML_URL = "https://www.ecfr.gov/current/title-{title}/part-{part}"


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 "
    "ZLab-Regulatory/1.0 (contact: davidlagarejo@gmail.com)"
)


# Map of priority parts to download proactively, organized by relevance
# to our asset families. Driven by the citation_extractor's top results
# but seeded with our domain knowledge.
PRIORITY_CFR_PARTS: list[tuple[int, int, str, list[str]]] = [
    # (title, part, friendly_name, asset_families)
    (40, 60,   "NSPS — Standards of Performance for New Stationary Sources",
                ["manufacturing_facility", "infrastructure_node"]),
    (40, 63,   "NESHAP — Hazardous Air Pollutants",
                ["manufacturing_facility", "cold_chain_facility"]),
    (40, 70,   "State Operating Permits (Title V)",
                ["manufacturing_facility", "infrastructure_node"]),
    (40, 82,   "Protection of Stratospheric Ozone (ODS/HFCs)",
                ["cold_chain_facility", "_shared"]),
    (40, 98,   "Mandatory Greenhouse Gas Reporting",
                ["manufacturing_facility", "infrastructure_node", "_shared"]),
    (40, 122,  "EPA NPDES Permitting", ["manufacturing_facility"]),
    (29, 1910, "OSHA — Occupational Safety and Health (general industry)",
                ["manufacturing_facility", "cold_chain_facility",
                 "warehouse_distribution", "commercial_building"]),
    (29, 1926, "OSHA — Construction Industry",
                ["commercial_building", "infrastructure_node"]),
    (10, 433,  "DOE Energy Efficiency Standards — New Federal Commercial",
                ["commercial_building"]),
    (10, 434,  "DOE Energy Code — New Federal Commercial/Multi-Family High Rise",
                ["commercial_building"]),
    (10, 435,  "DOE Energy Code — New Federal Low-Rise Residential",
                ["commercial_building"]),
    (10, 436,  "Federal Energy Management & Planning Programs",
                ["commercial_building", "_shared"]),
    (10, 851,  "Worker Safety and Health Program (DOE contractors)",
                ["manufacturing_facility"]),
    (49, 192,  "PHMSA — Natural Gas Pipeline Safety",
                ["infrastructure_node"]),
    (49, 195,  "PHMSA — Hazardous Liquid Pipeline Safety",
                ["infrastructure_node"]),
]


@dataclass
class CFRFetchResult:
    title:        int
    part:         int
    name:         str
    fetched_at:   str = ""
    bytes_xml:    int = 0
    sections:     int = 0
    text_chars:   int = 0
    saved_path:   str = ""
    errors:       list[str] = field(default_factory=list)


def _today() -> str:
    return _dt.date.today().isoformat()


def _http_get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept":     "application/xml,application/json,*/*",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _strip_xml_tags(xml: str) -> str:
    """Crude but determinístic: drop XML tags, keep text. eCFR XML is
    well-structured so a regex is enough — no extra deps."""
    # Replace closing block tags with newlines for readability
    text = re.sub(r"</(?:P|HEAD|HD|SUBJECT|SECTNO|CITA)\b[^>]*>", "\n", xml,
                  flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    # Re-introduce paragraph breaks
    text = re.sub(r"\.\s+(?=[A-Z§])", ".\n", text)
    return text.strip()


def _output_dirs(runtime_dir: Path | None = None) -> tuple[Path, Path]:
    """Return (regulatory_corpus/regulations/us_federal, raw_cache) paths."""
    if runtime_dir is None:
        # ../../industry_corpus/ → ../../regulatory_corpus/
        from ..manifest import corpus_root
        base = corpus_root().parent
    else:
        base = runtime_dir
    regs_dir = base / "regulatory_corpus" / "regulations" / "us_federal"
    raw_dir = base / "regulatory_corpus" / "raw_xml"
    regs_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    return regs_dir, raw_dir


def fetch_cfr_part(
    title: int,
    part: int,
    *,
    name: str = "",
    asset_families: list[str] | None = None,
    runtime_orchestrator_dir: Path | None = None,
) -> CFRFetchResult:
    """Download ONE CFR Part as full XML from eCFR, persist it, and emit
    a YAML manifest under regulatory_corpus/regulations/us_federal/.
    """
    result = CFRFetchResult(title=title, part=part, name=name,
                            fetched_at=_dt.datetime.utcnow().isoformat() + "Z")
    date = _today()
    # First check that the title actually has this part on `date`
    # — eCFR's full/<date>/title-<n>.xml is the entire title, big.
    # We only need one part, but the API doesn't expose part-only XML.
    # We fetch the part's "current" HTML version and parse from there.
    url_html = ECFR_PART_HTML_URL.format(title=title, part=part)
    try:
        body = _http_get(url_html, timeout=45)
    except urllib.error.HTTPError as exc:
        result.errors.append(f"HTTP {exc.code} {exc.reason}")
        return result
    except Exception as exc:
        result.errors.append(f"{type(exc).__name__}: {exc}")
        return result
    result.bytes_xml = len(body)

    html = body.decode("utf-8", errors="replace")
    text = _strip_xml_tags(html)
    result.text_chars = len(text)
    if result.text_chars < 500:
        result.errors.append(f"suspiciously short text ({result.text_chars} chars)")
        return result

    # Count section markers
    result.sections = len(re.findall(r"§\s*\d+\.\d+", text))

    regs_dir, raw_dir = _output_dirs(runtime_orchestrator_dir)
    # Persist raw HTML (for reproducibility) and a clean text version
    raw_html = raw_dir / f"{title:02d}_cfr_{part:04d}.html"
    raw_html.write_text(html, encoding="utf-8")
    txt_file = raw_dir / f"{title:02d}_cfr_{part:04d}.txt"
    txt_file.write_text(text, encoding="utf-8")

    # YAML manifest — compatible with industry_corpus.manifest.CorpusSource
    fams = asset_families or ["_shared"]
    yaml_path = regs_dir / f"{title:02d}_cfr_{part:04d}.yaml"
    yaml_lines = [
        f"source_id: us_federal_{title:02d}_cfr_{part:04d}",
        f"title: \"{(name or f'{title} CFR Part {part}').replace(chr(34), chr(39))}\"",
        f"url: https://www.ecfr.gov/current/title-{title}/part-{part}",
        f"license: us_federal_regulation",
        f"publisher: ecfr",
        f"version: \"{date}\"",
        f"added_at: \"{_dt.datetime.utcnow().isoformat()}Z\"",
        f"added_by: system_verified",
        f"notes: \"Auto-fetched from eCFR API. {result.sections} §-marked sections. {result.text_chars:,} chars.\"",
        "asset_families:",
    ]
    for af in fams:
        yaml_lines.append(f"  - {af}")
    yaml_path.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    result.saved_path = str(yaml_path)
    return result


def fetch_priority_cfr_parts(
    *, runtime_orchestrator_dir: Path | None = None,
) -> list[CFRFetchResult]:
    """Download the priority list of CFR parts that touch our asset families."""
    out: list[CFRFetchResult] = []
    for title, part, name, fams in PRIORITY_CFR_PARTS:
        r = fetch_cfr_part(
            title, part, name=name, asset_families=fams,
            runtime_orchestrator_dir=runtime_orchestrator_dir,
        )
        out.append(r)
    return out


# ── ETL into the industry_corpus chunks pipeline ────────────────────────


def ingest_fetched_regulations(
    *,
    runtime_orchestrator_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Walk regulatory_corpus/regulations/us_federal/*.yaml and run the
    standard ETL → chunks → embeddings → index. The text was already
    extracted by fetch_cfr_part(); we point ingest at the .txt cache.
    """
    from ..manifest import corpus_root, load_source_yaml, sha256_url, sha256_text, write_chunk_json, CorpusChunk
    from ..chunker import split as _split
    import shutil

    corpus = corpus_root(runtime_orchestrator_dir)
    regs_dir, raw_dir = _output_dirs(runtime_orchestrator_dir)
    now = _dt.datetime.utcnow().isoformat() + "Z"

    outcomes: list[dict[str, Any]] = []
    for yp in sorted(regs_dir.glob("*.yaml")):
        src = load_source_yaml(yp)
        source_sha = sha256_url(src.url)
        # text was written by fetch_cfr_part — pick by filename pattern
        # yaml name like 40_cfr_0063.yaml → text file with same stem
        txt_path = raw_dir / f"{yp.stem}.txt"
        if not txt_path.exists():
            outcomes.append({"source_id": src.source_id,
                             "error": f"missing raw text {txt_path.name}"})
            continue
        full_text = txt_path.read_text(encoding="utf-8")

        # Mirror text into industry_corpus/extracted_text for retriever consistency
        mirror = corpus / "extracted_text" / f"{source_sha}.txt"
        mirror.parent.mkdir(parents=True, exist_ok=True)
        if not mirror.exists():
            shutil.copy2(txt_path, mirror)

        # Chunk + write to chunks_approved/ (regulations are public_domain federal → auto-approve)
        chunks = _split(full_text, max_tokens=512, overlap=50)
        target = corpus / "chunks_approved" / source_sha
        target.mkdir(parents=True, exist_ok=True)
        written = 0
        # Build set of existing text_shas for idempotency
        existing: set[str] = set()
        for sub in ("chunks_pending", "chunks_approved", "chunks_rejected"):
            d = corpus / sub / source_sha
            if d.exists():
                for j in d.glob("*.json"):
                    try:
                        existing.add(json.loads(j.read_text(encoding="utf-8")).get("text_sha", ""))
                    except Exception:
                        continue

        for idx, tc in enumerate(chunks, start=1):
            ts = sha256_text(tc.text)
            if ts in existing:
                continue
            chunk = CorpusChunk(
                chunk_id       = f"{source_sha[:8]}::chunk_{idx:04d}",
                source_id      = src.source_id,
                source_sha     = source_sha,
                source_url     = src.url,
                asset_families = src.asset_families,
                page           = tc.page,
                text           = tc.text,
                token_count    = tc.token_count,
                text_sha       = ts,
                extracted_at   = now,
            )
            write_chunk_json(chunk, target)
            written += 1
        outcomes.append({
            "source_id": src.source_id, "chunks_total": len(chunks),
            "chunks_written": written, "text_chars": len(full_text),
        })
    return outcomes
