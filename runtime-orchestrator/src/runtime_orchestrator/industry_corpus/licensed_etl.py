"""Licensed-journal ETL — uses the existing Playwright persistent session
machinery to fetch HTML fulltext from IEEE/Springer/Scopus/Elsevier papers,
then chunks the visible text and routes to chunks_pending/ (NEVER auto-approve).

This is the licensed sibling of `etl.ingest_source()`:
  · etl.ingest_source     → for PDF sources (DOE OSTI, EIA, arxiv, vendor)
  · licensed_etl.ingest_  → for paywall HTML papers (IEEE, Springer, …)

Phase 0 doctrine intact:
  · Paywall content NEVER auto-approves (license="licensed_journal" enforced).
  · Chunks land in chunks_pending/ for explicit human review.
  · Verbatim quotes ≤ Regla 11's 300-char cap (fair use).
"""
from __future__ import annotations

import datetime as _dt
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
class LicensedIngestResult:
    source_id:           str
    url:                 str
    source_sha:          str
    publisher:           str
    fetch_status:        str = ""
    final_url:           str = ""
    login_gate_detected: bool = False
    text_chars:          int = 0
    chunks_total:        int = 0
    chunks_written:      int = 0
    chunks_skipped_dup:  int = 0
    target_dir:          str = ""
    errors:              list[str] = field(default_factory=list)


def _existing_text_shas(corpus_dir: Path, source_sha: str) -> set[str]:
    """Same idempotency check used in etl.py."""
    import json
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


def ingest_licensed_source(
    yaml_path: Path,
    *,
    runtime_orchestrator_dir: Path | None = None,
) -> LicensedIngestResult:
    """Ingest one licensed-journal source. Always routes to chunks_pending/.

    Uses fetch_licensed_document_with_persistent_session under the hood,
    so the provider's persistent Playwright profile (with login cookies)
    must already exist.
    """
    src: CorpusSource = load_source_yaml(yaml_path)
    corpus_dir = corpus_root(runtime_orchestrator_dir)
    source_sha = sha256_url(src.url)
    result = LicensedIngestResult(
        source_id=src.source_id, url=src.url, source_sha=source_sha,
        publisher=src.publisher,
    )
    result.target_dir = str(corpus_dir / "chunks_pending" / source_sha)

    # Step 1: fetch HTML via licensed Playwright session
    try:
        from runtime_orchestrator.zlab_skill.licensed_playwright_fetch import (
            fetch_licensed_document_with_persistent_session,
        )
        from runtime_orchestrator.zlab_skill.provider_sessions import (
            build_provider_session_plan,
        )
    except Exception as exc:
        result.errors.append(f"import_failed: {exc}")
        return result

    plan = build_provider_session_plan(
        url=src.url, retrieval_purpose="industry_corpus_licensed_ingest",
        session_label="licensed",
    )
    fetched = fetch_licensed_document_with_persistent_session(
        url=src.url,
        provider_session_plan=plan,
        timeout_ms=25_000,
        headless=True,
    )
    result.fetch_status = str(fetched.get("status") or "")
    result.final_url = str(fetched.get("final_url") or "")
    text = (fetched.get("visible_text") or "").strip()
    result.text_chars = len(text)

    # Detect login gate / interstitial
    body_html = (fetched.get("html") or "").lower()
    login_signals = ("sign in", "log in", "institutional access",
                     "access through your institution")
    if any(s in text.lower() for s in login_signals) and result.text_chars < 2000:
        result.login_gate_detected = True
        result.errors.append(
            "login gate detected — session expired? re-authenticate with "
            f"scripts/bootstrap_licensed_provider_session.py --provider {src.publisher}"
        )
        return result

    if result.fetch_status != "success" or not text:
        result.errors.append(f"fetch_failed: status={result.fetch_status} text_len={result.text_chars}")
        return result

    # Step 2: persist raw text mirror so curation/audit has the original
    txt_target = corpus_dir / "extracted_text" / f"{source_sha}.txt"
    txt_target.parent.mkdir(parents=True, exist_ok=True)
    if not txt_target.exists():
        txt_target.write_text(text, encoding="utf-8")

    # Step 3: chunk
    text_chunks = _chunker_split(text)
    result.chunks_total = len(text_chunks)
    if not text_chunks:
        result.errors.append("chunker returned 0 chunks")
        return result

    # Step 4: write to chunks_pending (NEVER chunks_approved for licensed)
    existing = _existing_text_shas(corpus_dir, source_sha)
    target_dir = corpus_dir / "chunks_pending" / source_sha
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
        write_chunk_json(chunk, target_dir)
        written += 1
    result.chunks_written = written
    result.chunks_skipped_dup = skipped
    return result
