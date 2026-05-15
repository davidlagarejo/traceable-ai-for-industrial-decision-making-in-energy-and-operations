"""Local PDF ingestor — para PDFs que el usuario ya tiene en disco
(whitepapers de vendors descargados manualmente, papers, reportes
internos públicos, etc.).

Uso típico:
  · Usuario arrastra PDFs a una carpeta (default: industry_corpus/drop_zone/)
  · ingest_local_directory() los procesa: hash sha256(contenido) como
    source_id, copia a raw_pdfs/, extrae texto, chunkea, y los manda a
    chunks_pending/ para revisión humana (NO auto-aprueba — el usuario
    decide).

Diferencia con etl.ingest_source():
  · etl.ingest_source consume un YAML de sources/ y fetcha por URL.
  · Local ingestor toma archivos ya en disco, sin URL.

Phase 0: zero LLM, solo extracción determinista.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import (
    CorpusChunk,
    corpus_root,
    sha256_text,
    write_chunk_json,
)
from .chunker import split as _chunker_split


@dataclass
class LocalIngestResult:
    file_path:           str
    source_id:           str
    file_sha:            str
    title:               str
    asset_families:      list[str]
    pdf_bytes:           int = 0
    text_chars:          int = 0
    chunks_total:        int = 0
    chunks_written:      int = 0
    chunks_skipped_dup:  int = 0
    target_dir:          str = ""
    errors:              list[str] = field(default_factory=list)


def _sha256_file(p: Path, *, n_bytes: int = 1024 * 1024) -> str:
    """sha256 of file contents (chunked read for big PDFs)."""
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while True:
            buf = fh.read(n_bytes)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def _slugify_title(name: str) -> str:
    """Filename → human-readable title."""
    out = name.replace("_", " ").replace("-", " ")
    return " ".join(w.capitalize() for w in out.split()).strip()[:200]


def _existing_text_shas(corpus_dir: Path, source_sha: str) -> set[str]:
    """Same logic as etl: skip chunks whose text already lives somewhere."""
    seen: set[str] = set()
    for sub in ("chunks_pending", "chunks_approved", "chunks_rejected"):
        d = corpus_dir / sub / source_sha
        if not d.exists():
            continue
        for j in d.glob("*.json"):
            try:
                ts = json.loads(j.read_text(encoding="utf-8")).get("text_sha")
                if ts:
                    seen.add(ts)
            except Exception:
                continue
    return seen


def ingest_local_pdf(
    pdf_path: Path,
    *,
    asset_families: list[str],
    title: str | None = None,
    source_id: str | None = None,
    auto_approve: bool = False,
    runtime_orchestrator_dir: Path | None = None,
) -> LocalIngestResult:
    """Ingest ONE local PDF into the corpus.

    Routing:
      · auto_approve=True  → chunks land in chunks_approved/<sha>/
      · auto_approve=False → chunks land in chunks_pending/<sha>/   (default)
        The user reviews via /corpus_curar before they reach the index.

    Idempotente: re-running the same PDF doesn't duplicate chunks (text_sha dedup).
    """
    pdf_path = pdf_path.resolve()
    file_sha = _sha256_file(pdf_path)
    short_sha = file_sha[:32]

    # If caller didn't supply explicit source_id, derive from filename slug + sha
    if not source_id:
        stem = pdf_path.stem.lower().replace(" ", "_")
        stem = "".join(c if (c.isalnum() or c in "_-") else "_" for c in stem)[:60]
        source_id = f"local_{stem}_{short_sha[:8]}"

    if not title:
        title = _slugify_title(pdf_path.stem)

    result = LocalIngestResult(
        file_path=str(pdf_path),
        source_id=source_id,
        file_sha=short_sha,
        title=title,
        asset_families=list(asset_families),
    )

    if not pdf_path.exists():
        result.errors.append("file not found")
        return result
    if pdf_path.suffix.lower() != ".pdf":
        result.errors.append(f"not a PDF: {pdf_path.suffix}")
        return result

    corpus_dir = corpus_root(runtime_orchestrator_dir)
    target_subdir = "chunks_approved" if auto_approve else "chunks_pending"
    result.target_dir = str(corpus_dir / target_subdir / short_sha)

    # Mirror PDF to industry_corpus/raw_pdfs/<sha>.pdf (so the corpus stays
    # self-contained even if the user moves the original)
    raw_target = corpus_dir / "raw_pdfs" / f"{short_sha}.pdf"
    if not raw_target.exists():
        raw_target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(pdf_path, raw_target)
        except Exception as exc:
            result.errors.append(f"copy failed: {exc}")
    result.pdf_bytes = raw_target.stat().st_size if raw_target.exists() else pdf_path.stat().st_size

    # Reuse the same extractor as ETL
    try:
        from runtime_orchestrator.zlab_skill.local_pdf_autodraft import extract_bounded_pdf_text
    except Exception as exc:
        result.errors.append(f"import extractor failed: {exc}")
        return result
    text_result = extract_bounded_pdf_text(
        artifact_path=str(raw_target if raw_target.exists() else pdf_path),
        max_pages=100, max_chars=400_000,
    )
    if text_result.get("status") != "success":
        result.errors.append(f"text extraction failed: {text_result.get('status')}")
        return result
    full_text = text_result.get("visible_text", "") or ""
    if not full_text.strip():
        result.errors.append("extracted text empty")
        return result
    result.text_chars = len(full_text)

    txt_target = corpus_dir / "extracted_text" / f"{short_sha}.txt"
    if not txt_target.exists():
        txt_target.parent.mkdir(parents=True, exist_ok=True)
        txt_target.write_text(full_text, encoding="utf-8")

    text_chunks = _chunker_split(full_text)
    result.chunks_total = len(text_chunks)
    if not text_chunks:
        result.errors.append("chunker returned 0 chunks")
        return result

    existing = _existing_text_shas(corpus_dir, short_sha)
    target_dir = corpus_dir / target_subdir / short_sha
    target_dir.mkdir(parents=True, exist_ok=True)
    now = _dt.datetime.utcnow().isoformat() + "Z"

    written = 0
    skipped = 0
    for idx, tc in enumerate(text_chunks, start=1):
        ts = sha256_text(tc.text)
        if ts in existing:
            skipped += 1
            continue
        chunk = CorpusChunk(
            chunk_id       = f"{short_sha[:8]}::chunk_{idx:04d}",
            source_id      = source_id,
            source_sha     = short_sha,
            source_url     = f"local://{pdf_path.name}",
            asset_families = tuple(asset_families),
            page           = tc.page,
            text           = tc.text,
            token_count    = tc.token_count,
            text_sha       = ts,
            extracted_at   = now,
        )
        write_chunk_json(chunk, target_dir)
        written += 1

    result.chunks_written = written
    result.chunks_skipped_dup = skipped
    return result


def ingest_local_directory(
    directory: Path,
    *,
    asset_families: list[str],
    auto_approve: bool = False,
    runtime_orchestrator_dir: Path | None = None,
) -> list[LocalIngestResult]:
    """Walk a directory and ingest every .pdf in it (recursive).

    Use this when you have a folder of vendor whitepapers, internal reports,
    or other local PDFs you want in the corpus.
    """
    if not directory.exists() or not directory.is_dir():
        return [LocalIngestResult(
            file_path=str(directory), source_id="<dir_not_found>",
            file_sha="", title="", asset_families=list(asset_families),
            errors=[f"directory does not exist or is not a dir: {directory}"],
        )]
    out: list[LocalIngestResult] = []
    for pdf_path in sorted(directory.rglob("*.pdf")):
        out.append(ingest_local_pdf(
            pdf_path,
            asset_families=asset_families,
            auto_approve=auto_approve,
            runtime_orchestrator_dir=runtime_orchestrator_dir,
        ))
    return out
