"""ETL — ingest ONE CorpusSource end-to-end.

Pipeline:
  source.yaml
    ↓  load_source_yaml()
  CorpusSource
    ↓  pdf_url_fetcher.fetch_pdf_from_url()  ← REUSES Playwright-fallback logic
  raw_pdfs/<sha>.pdf
    ↓  local_pdf_autodraft.extract_bounded_pdf_text()
  extracted_text/<sha>.txt
    ↓  chunker.split()
  list[TextChunk]
    ↓  write_chunk_json() — to chunks_pending/<sha>/ OR chunks_approved/<sha>/
  IngestionResult

Routing:
  · If source.is_auto_approvable() (federal whitelist, public_domain,
    added_by=system_verified) → chunks go DIRECTLY to chunks_approved/.
  · Otherwise → chunks_pending/, awaiting human review.

Idempotence:
  · Skips chunks whose text_sha already exists in approved/pending/rejected.
  · Re-running the same source is safe — no duplicates.
"""
from __future__ import annotations

import datetime as _dt
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import (
    CorpusChunk,
    CorpusSource,
    corpus_root,
    load_source_yaml,
    sha256_text,
    sha256_url,
    write_chunk_json,
)
from .chunker import split as _chunker_split


@dataclass
class IngestionResult:
    source_id:           str
    url:                 str
    source_sha:          str
    auto_approved:       bool
    pdf_fetched:         bool         = False
    fetched_via:         str          = ""    # "stdlib" | "playwright" | "cache" | ""
    pdf_bytes:           int          = 0
    text_extracted:      bool         = False
    text_chars:          int          = 0
    chunks_total:        int          = 0
    chunks_written:      int          = 0
    chunks_skipped_dup:  int          = 0
    target_dir:          str          = ""    # which subdir got the chunks
    errors:              list[str]    = field(default_factory=list)


def _existing_text_shas(corpus_dir: Path, source_sha: str) -> set[str]:
    """Read text_sha from every chunk JSON already on disk under this source
    (pending OR approved OR rejected), so we don't ingest duplicates."""
    seen: set[str] = set()
    for sub in ("chunks_pending", "chunks_approved", "chunks_rejected"):
        d = corpus_dir / sub / source_sha
        if not d.exists():
            continue
        for j in d.glob("*.json"):
            try:
                import json
                data = json.loads(j.read_text(encoding="utf-8"))
                ts = data.get("text_sha")
                if ts:
                    seen.add(ts)
            except Exception:
                continue
    return seen


def ingest_source(
    yaml_path: Path,
    *,
    runtime_orchestrator_dir: Path | None = None,
) -> IngestionResult:
    """Run the full ingest pipeline for one source YAML.

    Returns an IngestionResult with counts + outcomes. Idempotent.
    """
    src: CorpusSource = load_source_yaml(yaml_path)
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    source_sha = sha256_url(src.url)

    result = IngestionResult(
        source_id     = src.source_id,
        url           = src.url,
        source_sha    = source_sha,
        auto_approved = src.is_auto_approvable(),
    )
    target_subdir = "chunks_approved" if result.auto_approved else "chunks_pending"
    result.target_dir = str(corpus_dir / target_subdir / source_sha)

    # ── Step 1: fetch PDF (REUSE existing fetcher with Playwright fallback) ──
    try:
        from runtime_orchestrator.zlab_skill.pdf_url_fetcher import fetch_pdf_from_url
    except Exception as exc:
        result.errors.append(f"import pdf_url_fetcher failed: {exc}")
        return result

    fr = fetch_pdf_from_url(src.url)
    result.fetched_via = fr.fetched_via
    if fr.status not in ("ok", "cached"):
        result.errors.append(f"pdf fetch status={fr.status}: {fr.error}")
        return result
    result.pdf_fetched = True
    result.pdf_bytes = fr.bytes_written or Path(fr.local_path).stat().st_size

    # Mirror the binary into industry_corpus/raw_pdfs/<sha>.pdf so the
    # corpus is self-contained even if pdf_cache is wiped.
    raw_target = corpus_dir / "raw_pdfs" / f"{source_sha}.pdf"
    if not raw_target.exists():
        raw_target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(fr.local_path, raw_target)
        except Exception as exc:
            result.errors.append(f"raw_pdf copy failed: {exc}")

    # ── Step 2: extract text (REUSE existing extractor) ──
    try:
        from runtime_orchestrator.zlab_skill.local_pdf_autodraft import extract_bounded_pdf_text
    except Exception as exc:
        result.errors.append(f"import extractor failed: {exc}")
        return result

    text_result = extract_bounded_pdf_text(
        artifact_path=str(raw_target if raw_target.exists() else fr.local_path),
        max_pages=100,        # corpus → tomamos más páginas que el extractor de patterns
        max_chars=400_000,    # ~400 KB texto por documento
    )
    if text_result.get("status") != "success":
        result.errors.append(f"text extraction failed: {text_result.get('status')}")
        return result
    full_text: str = text_result.get("visible_text", "") or ""
    if not full_text.strip():
        result.errors.append("extracted text is empty")
        return result
    result.text_extracted = True
    result.text_chars = len(full_text)

    # Persist extracted text (reuses cache key)
    txt_target = corpus_dir / "extracted_text" / f"{source_sha}.txt"
    if not txt_target.exists():
        txt_target.parent.mkdir(parents=True, exist_ok=True)
        txt_target.write_text(full_text, encoding="utf-8")

    # ── Step 3: chunk ──
    text_chunks = _chunker_split(full_text)
    result.chunks_total = len(text_chunks)
    if not text_chunks:
        result.errors.append("chunker returned 0 chunks")
        return result

    # ── Step 4: route to pending/approved (with idempotence) ──
    existing_text_shas = _existing_text_shas(corpus_dir, source_sha)
    target_dir = corpus_dir / target_subdir / source_sha
    target_dir.mkdir(parents=True, exist_ok=True)
    now = _dt.datetime.utcnow().isoformat() + "Z"

    written = 0
    skipped = 0
    for idx, tc in enumerate(text_chunks, start=1):
        text_sha = sha256_text(tc.text)
        if text_sha in existing_text_shas:
            skipped += 1
            continue
        chunk_id = f"{source_sha[:8]}::chunk_{idx:04d}"
        chunk = CorpusChunk(
            chunk_id       = chunk_id,
            source_id      = src.source_id,
            source_sha     = source_sha,
            source_url     = src.url,
            asset_families = src.asset_families,
            page           = tc.page,
            text           = tc.text,
            token_count    = tc.token_count,
            text_sha       = text_sha,
            extracted_at   = now,
        )
        write_chunk_json(chunk, target_dir)
        written += 1

    result.chunks_written = written
    result.chunks_skipped_dup = skipped
    return result


def ingest_all_sources(
    sources_root: Path | None = None,
    *,
    runtime_orchestrator_dir: Path | None = None,
) -> list[IngestionResult]:
    """Walk every *.yaml under industry_corpus/sources/ and ingest each one."""
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    sroot = sources_root or (corpus_dir / "sources")
    if not sroot.exists():
        return []
    results: list[IngestionResult] = []
    for yaml_path in sorted(sroot.rglob("*.yaml")):
        try:
            results.append(ingest_source(
                yaml_path, runtime_orchestrator_dir=runtime_orchestrator_dir,
            ))
        except Exception as exc:
            results.append(IngestionResult(
                source_id="<load_failed>", url=str(yaml_path),
                source_sha="", auto_approved=False,
                errors=[f"{type(exc).__name__}: {exc}"],
            ))
    return results
