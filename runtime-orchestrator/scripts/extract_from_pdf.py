#!/usr/bin/env python3
"""Automated PDF → knowledge extraction CLI (V4 Phase 2).

Chains PDFPlumberExtractor → AnthropicLLMExtractor → propose_knowledge.
The output lands in knowledge_pending/<kind>/ for human review at
http://localhost:7474/knowledge.

Prerequisites:
  pip install pdfplumber anthropic
  export ANTHROPIC_API_KEY=sk-ant-...

Usage:
  python3 scripts/extract_from_pdf.py \\
    --pdf-path /path/to/IIAR-Bulletin-109.pdf \\
    --source-id iiar_bulletin_109 \\
    --topic refrigeration \\
    --kind pattern \\
    --pages 1-5

  # Optional flags:
  #   --proposed-by claude_v4_p2
  #   --model claude-sonnet-4-5
  #   --asset-families-hint cold_chain_facility,manufacturing_facility
  #   --max-chars 60000

Exit codes:
  0  proposal accepted (now in knowledge_pending/<kind>/)
  2  invalid input or extraction failure
  3  conflict (knowledge_id already pending)
  4  prerequisite missing (no API key, anthropic SDK not installed, etc.)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from runtime_orchestrator.industrial_research_engine import (  # noqa: E402
    ANTHROPIC_DEFAULT_MODEL,
    AnthropicLLMExtractor,
    AnthropicSettings,
    ExtractionOrchestrator,
    KNOWLEDGE_KINDS,
    KnowledgeValidationError,
    PDFPlumberExtractor,
    URLFetchError,
    fetch_pdf,
    is_url,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Full V4 P2 extraction pipeline: PDF → LLM → propose. "
            "Requires anthropic SDK installed + ANTHROPIC_API_KEY set."
        )
    )
    parser.add_argument("--pdf-path", required=True,
                        help="Local PDF path OR https:// URL. URLs are fetched to "
                             "a temp file before extraction.")
    parser.add_argument("--source-id", required=True,
                        help="Catalog source_id (e.g. iiar_bulletin_109).")
    parser.add_argument("--topic", required=True,
                        help="Industrial topic (refrigeration, thermal_process, ...).")
    parser.add_argument("--kind", required=True, choices=KNOWLEDGE_KINDS,
                        help="Target knowledge_kind for the extracted object.")
    parser.add_argument("--pages", default="",
                        help="Page range like '1-5' or '3,7-9'. Default: ALL pages.")
    parser.add_argument("--max-chars", type=int, default=60_000,
                        help="Text truncation budget (LLM context). Default: 60000.")
    parser.add_argument("--asset-families-hint", default="",
                        help="Comma-separated families hint to the LLM.")
    parser.add_argument("--model", default=ANTHROPIC_DEFAULT_MODEL,
                        help=f"Anthropic model id. Default: {ANTHROPIC_DEFAULT_MODEL}")
    parser.add_argument("--proposed-by", default="claude_v4_p2_pdf_extraction",
                        help="Identifier for who proposed.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run PDF + LLM stages but DO NOT propose to pending/. "
                             "Useful to inspect the extracted JSON before commit.")
    parser.add_argument("--max-retries", type=int, default=2,
                        help="LLM retry attempts on validation failure. Default: 2.")
    return parser.parse_args()


def _prereq_check() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        print(
            "error: ANTHROPIC_API_KEY is not set.\n"
            "  Set it: export ANTHROPIC_API_KEY=sk-ant-...\n",
            file=sys.stderr,
        )
        sys.exit(4)
    try:
        import anthropic  # noqa: F401
    except ImportError:
        print(
            "error: anthropic SDK is not installed.\n"
            "  Install: pip install anthropic\n",
            file=sys.stderr,
        )
        sys.exit(4)
    try:
        import pdfplumber  # noqa: F401
    except ImportError:
        print(
            "error: pdfplumber is not installed.\n"
            "  Install: pip install pdfplumber\n",
            file=sys.stderr,
        )
        sys.exit(4)


def main() -> int:
    args = _parse_args()
    _prereq_check()

    # V4 P3: accept URL or local path. If URL, fetch to temp file first.
    pdf_source = str(args.pdf_path)
    if is_url(pdf_source):
        try:
            fetched = fetch_pdf(pdf_source)
            print(f"fetched: {pdf_source}", file=sys.stderr)
            print(f"  → {fetched.local_path} ({fetched.bytes_downloaded} bytes, {fetched.content_type})", file=sys.stderr)
            pdf_local_path = str(fetched.local_path)
        except URLFetchError as exc:
            print(f"error fetching URL: {exc}", file=sys.stderr)
            return 2
    else:
        pdf_local_path = pdf_source
        if not Path(pdf_local_path).exists():
            print(f"error: PDF not found: {pdf_local_path}", file=sys.stderr)
            return 2

    pdf = PDFPlumberExtractor(max_chars=args.max_chars)
    llm = AnthropicLLMExtractor(AnthropicSettings(model_id=args.model))

    families_hint = [
        f.strip() for f in args.asset_families_hint.split(",") if f.strip()
    ]

    orch = ExtractionOrchestrator(pdf_extractor=pdf, llm_extractor=llm)

    try:
        if args.dry_run:
            # Run stages 2+3 only, skip propose
            from runtime_orchestrator.industrial_research_engine import (
                LLMExtractionRequest,
            )
            pdf_result = pdf.extract(pdf_local_path, pages=args.pages)
            llm_result = llm.extract(LLMExtractionRequest(
                raw_text=pdf_result.text,
                topic=args.topic,
                source_id=args.source_id,
                target_kind=args.kind,
                asset_families_hint=families_hint,
            ))
            print("=== DRY RUN: extracted JSON (NOT proposed) ===")
            print(json.dumps(llm_result.knowledge_payload, indent=2, ensure_ascii=False))
            print(f"\nmodel: {llm_result.model_id}")
            print(f"self_confidence: {llm_result.confidence_self_assessment}")
            if llm_result.extraction_warnings:
                print(f"warnings: {llm_result.extraction_warnings}")
            return 0

        # Full orchestrated path
        result = orch.orchestrate(
            source_id=args.source_id,
            source_url=pdf_local_path,
            topic=args.topic,
            target_kind=args.kind,
            asset_families_hint=families_hint,
            proposed_by=args.proposed_by,
            max_retries=args.max_retries,
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KnowledgeValidationError as exc:
        print(f"validation failed: {exc}\n", file=sys.stderr)
        print("The LLM produced output but it failed the schema validator. "
              "Re-run with --dry-run to inspect the raw extraction.",
              file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"conflict: {exc}", file=sys.stderr)
        return 3
    except (ImportError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    proposed = result.propose_result or {}
    print(
        f"extracted (pdf+llm): id={proposed.get('id','?')} "
        f"kind={args.kind} source={args.source_id} topic={args.topic} "
        f"pages={args.pages or 'all'} model={args.model} "
        f"retry_count={result.retry_count} "
        f"by={proposed.get('__proposed_by__','?')} "
        f"at={proposed.get('__proposed_at__','?')}"
    )
    if result.validation_errors:
        print(f"  validation_errors_during_retry: {result.validation_errors}")
    print("Review and approve at: http://localhost:7474/knowledge")
    return 0


if __name__ == "__main__":
    sys.exit(main())
