#!/usr/bin/env python3
"""Populate knowledge_memory/pending with REAL knowledge extracted from
public PDFs (DOE, EPA, ENERGY STAR, EIA, national labs).

Pipeline:
  knowledge_seed_urls.yaml
      ↓ (HTTPS download, 30MB cap, content-type check, cache by URL hash)
  pdf_cache/<sha256>.pdf
      ↓ (pdfplumber extracts up to 60K chars / 20 pages)
  search_text
      ↓ (deterministic keyword match against 30 registered pattern_specs)
  matched patterns
      ↓ (propose_extracted_pattern → industrial_research_engine)
  knowledge_memory/pending/pattern/<pattern_id>__from_<source>__<pdf_slug>.json

Usage:
  python3 scripts/populate_knowledge_from_public_urls.py
  python3 scripts/populate_knowledge_from_public_urls.py --dry-run
  python3 scripts/populate_knowledge_from_public_urls.py --limit 3

No API keys. No paid sources. Only public US-federal / state / lab PDFs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make src importable when run as a script
_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE / "src"))

from runtime_orchestrator.zlab_skill.pdf_url_fetcher import fetch_pdf_from_url


def _load_yaml(path: Path) -> dict:
    """Minimal YAML parser for our flat list format (no PyYAML dependency).
    Supports: top-level `sources:` key with a list of dicts."""
    out: dict = {"sources": []}
    current: dict = {}
    in_sources = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line == "sources:":
            in_sources = True
            continue
        if not in_sources:
            continue
        if line.startswith("- "):
            # New dict entry
            if current:
                out["sources"].append(current)
            current = {}
            line = line[2:]
        # key: value pair (could be indented for next-line continuation,
        # but for our file every value is on the same line)
        stripped = line.lstrip()
        if ":" in stripped:
            k, _, v = stripped.partition(":")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and v:
                current[k] = v
    if current:
        out["sources"].append(current)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--urls-file", type=Path,
                        default=_HERE / "knowledge_seed_urls.yaml",
                        help="YAML with public PDF URLs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only download + parse — do NOT call propose_knowledge")
    parser.add_argument("--limit", type=int, default=0,
                        help="Process at most N sources (0 = all)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Re-download even if cached")
    args = parser.parse_args()

    if not args.urls_file.exists():
        print(f"ERROR: URL file not found: {args.urls_file}")
        return 2

    config = _load_yaml(args.urls_file)
    sources = config.get("sources", [])
    if args.limit > 0:
        sources = sources[: args.limit]
    if not sources:
        print("No sources to process.")
        return 0

    print(f"Procesando {len(sources)} sources públicos...")
    print("─" * 70)

    summary = {
        "fetched": 0, "cached": 0, "rejected": 0, "blocked": 0, "errors": 0,
        "extracted": 0, "patterns_matched": 0, "proposed": 0,
        "skipped_no_match": 0,
    }
    # Per-URL outcome log so the user can SEE which URLs were actually
    # investigated and which were silently blocked. Written to disk so we
    # don't lose visibility after the run.
    outcomes: list[dict] = []

    # Import the existing extractor / pipeline
    from runtime_orchestrator.zlab_skill.local_pdf_autodraft import (
        extract_bounded_pdf_text,
        _evaluate_pattern_rule,
        _extract_excerpt,
        _AUTO_PATTERN_RULES,
    )
    from runtime_orchestrator.industrial_research_engine import (
        propose_extracted_pattern,
        load_pattern_spec,
        KnowledgeValidationError,
    )

    # Re-use the heavy lifting in scripts/extract_from_local_pdf.py
    sys.path.insert(0, str(_HERE / "scripts"))
    from extract_from_local_pdf import (  # type: ignore
        _all_registry_pattern_ids,
        _resolve_rule_for_pattern,
    )

    pattern_ids = _all_registry_pattern_ids()
    print(f"  Patterns registrados disponibles: {len(pattern_ids)}\n")

    for i, src in enumerate(sources, 1):
        url        = src.get("url", "").strip()
        source_id  = src.get("source_id", f"unnamed_{i}")
        title      = src.get("title", "(no title)")
        topic      = src.get("topic", "")
        af         = src.get("asset_family", "")
        print(f"[{i}/{len(sources)}] {source_id}")
        print(f"          title: {title[:90]}")
        print(f"          url:   {url[:90]}")

        if not url:
            print("          ✗ no URL — skip")
            summary["errors"] += 1
            continue

        # Step 1: download
        fr = fetch_pdf_from_url(url, use_cache=not args.no_cache)
        via = f" via={fr.fetched_via}" if fr.fetched_via else ""
        if fr.status == "ok":
            summary["fetched"] += 1
            print(f"          ✓ downloaded {fr.bytes_written:,} bytes in {fr.elapsed_s:.1f}s{via} → {fr.local_path}")
            outcomes.append({"source_id": source_id, "url": url, "status": "ok",
                             "via": fr.fetched_via, "error": ""})
        elif fr.status == "cached":
            summary["cached"] += 1
            print(f"          ✓ from cache: {fr.local_path}")
            outcomes.append({"source_id": source_id, "url": url, "status": "cached",
                             "via": "cache", "error": ""})
        elif fr.status == "blocked":
            summary["blocked"] += 1
            print(f"          ⛔ BLOQUEADO{via}: {fr.error}")
            outcomes.append({"source_id": source_id, "url": url, "status": "blocked",
                             "via": fr.fetched_via, "error": fr.error})
            continue
        elif fr.status == "rejected":
            summary["rejected"] += 1
            print(f"          ✗ rejected: {fr.error}")
            outcomes.append({"source_id": source_id, "url": url, "status": "rejected",
                             "via": fr.fetched_via, "error": fr.error})
            continue
        else:
            summary["errors"] += 1
            print(f"          ✗ error: {fr.error}")
            outcomes.append({"source_id": source_id, "url": url, "status": "error",
                             "via": fr.fetched_via, "error": fr.error})
            continue

        pdf_path = Path(fr.local_path)

        # Step 2: extract text
        text_result = extract_bounded_pdf_text(
            artifact_path=str(pdf_path), max_pages=20, max_chars=60000,
        )
        if text_result["status"] != "success":
            print(f"          ✗ pdfplumber: {text_result['status']}")
            summary["errors"] += 1
            continue
        summary["extracted"] += 1
        print(f"          ✓ extracted {text_result['char_count']:,} chars / {text_result['page_count_scanned']} pages")

        search_text = text_result["visible_text"].lower()

        # Step 3: match every registered pattern_spec
        matched_count = 0
        landed_count = 0
        pdf_slug = "".join(
            c if (c.isalnum() or c in "_-") else "_"
            for c in pdf_path.stem.lower()
        )[:40].strip("_")
        for pattern_id in pattern_ids:
            rule, spec, rule_source = _resolve_rule_for_pattern(pattern_id)
            if rule is None or spec is None:
                continue
            evaluation = _evaluate_pattern_rule(search_text, rule)
            if not evaluation:
                continue
            matched_count += 1
            summary["patterns_matched"] += 1
            matched_terms = evaluation["matched_terms"]
            excerpt = _extract_excerpt(search_text, matched_terms)
            bridged_id = f"{pattern_id}__from_{source_id}__{pdf_slug}"

            if args.dry_run:
                print(f"          [dry-run] would propose: {bridged_id}  (score={evaluation['score']})")
                continue
            try:
                proposed = propose_extracted_pattern(
                    pattern_spec=spec,
                    source_id=source_id,
                    supporting_excerpt=excerpt,
                    source_locator=f"public_url::{url}::{pattern_id}",
                    matched_terms=matched_terms,
                    pdf_path=str(pdf_path),
                    override_id=bridged_id,
                )
                landed_count += 1
                summary["proposed"] += 1
                print(f"          ✓ proposed: {proposed['id']}  score={evaluation['score']}")
            except FileExistsError:
                print(f"          ~ already exists: {bridged_id}")
            except KnowledgeValidationError as exc:
                summary["errors"] += 1
                print(f"          ✗ validation failed: {exc}")
            except Exception as exc:
                summary["errors"] += 1
                print(f"          ✗ {type(exc).__name__}: {exc}")

        if matched_count == 0:
            summary["skipped_no_match"] += 1
            print("          (no patterns matched in this PDF)")
        print()

    print("─" * 70)
    print("RESUMEN:")
    for k, v in summary.items():
        print(f"  {k:<20} {v}")
    print()

    # ── LOUD report: URLs that were blocked/errored ─────────────────────
    # The point: if a URL was blocked, the user MUST see it. Otherwise it
    # looks like "research happened" when in fact nothing was investigated.
    blocked = [o for o in outcomes if o["status"] in ("blocked", "error")]
    if blocked:
        print("⚠ " + "═" * 68)
        print(f"⚠  {len(blocked)} URL(s) NO se pudieron investigar:")
        print("⚠ " + "═" * 68)
        for o in blocked:
            tag = "BLOQUEADO" if o["status"] == "blocked" else "ERROR"
            print(f"⚠  [{tag}] {o['source_id']}")
            print(f"⚠     url:   {o['url']}")
            print(f"⚠     why:   {o['error']}")
            if o["status"] == "blocked" and o["via"] != "playwright":
                print("⚠     hint:  install Playwright para reintentar con navegador real:")
                print("⚠            pip install playwright && playwright install chromium")
            print("⚠")
        print("⚠ " + "═" * 68)
        print("⚠  Estas fuentes NO contribuyeron al knowledge_memory.")
        print("⚠  Si necesitas su contenido, descárgalo manualmente y úsalo con")
        print("⚠  scripts/extract_from_local_pdf.py.")
        print("⚠ " + "═" * 68)
        print()

    # Always persist the per-URL outcome log so it's auditable later.
    report_path = _HERE / "pdf_cache" / "_last_run_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    import datetime as _dt
    report_path.write_text(json.dumps({
        "ran_at":   _dt.datetime.utcnow().isoformat() + "Z",
        "summary":  summary,
        "outcomes": outcomes,
    }, indent=2), encoding="utf-8")
    print(f"  reporte por-URL guardado en: {report_path}")

    if not args.dry_run:
        pending_dir = _HERE.parent / "knowledge_memory" / "pending" / "pattern"
        if pending_dir.exists():
            n = len(list(pending_dir.glob("*.json")))
            print(f"  knowledge_memory/pending/pattern/ ahora contiene {n} archivos")
    # Exit non-zero if anything was blocked, so CI / dashboards can flag it.
    return 0 if summary["blocked"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
