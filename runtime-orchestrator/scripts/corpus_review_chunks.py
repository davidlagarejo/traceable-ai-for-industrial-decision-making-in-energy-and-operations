#!/usr/bin/env python3
"""CLI bulk reviewer for industry_corpus chunks_pending/.

Walks every pending chunk for a given asset_family (or all), shows the
text + source + page, and asks for a/r/s (approve / reject / skip).

Approved → moved to chunks_approved/<source_sha>/
Rejected → moved to chunks_rejected/<source_sha>/
Skipped  → left in chunks_pending/

Usage:
  python3 scripts/corpus_review_chunks.py
  python3 scripts/corpus_review_chunks.py --asset-family cold_chain_facility
  python3 scripts/corpus_review_chunks.py --batch-approve-source iiar_bulletin_109
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE / "src"))

from runtime_orchestrator.industry_corpus.manifest import (
    CANONICAL_ASSET_FAMILIES,
    corpus_root,
    load_chunk_json,
)


def _list_pending(corpus_dir: Path, asset_family: str | None,
                  source_id_filter: str | None) -> list[Path]:
    pending = corpus_dir / "chunks_pending"
    if not pending.exists():
        return []
    out: list[Path] = []
    for p in sorted(pending.rglob("*.json")):
        try:
            ch = load_chunk_json(p)
        except Exception:
            continue
        if asset_family and asset_family not in ch.asset_families:
            if "_shared" not in ch.asset_families:
                continue
        if source_id_filter and ch.source_id != source_id_filter:
            continue
        out.append(p)
    return out


def _move(src: Path, dest_root: Path, source_sha: str) -> Path:
    dest_dir = dest_root / source_sha
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    shutil.move(str(src), str(dest))
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-family", default=None,
                        choices=sorted(CANONICAL_ASSET_FAMILIES) + [None])
    parser.add_argument("--batch-approve-source", default=None,
                        help="Approve ALL pending chunks from this source_id (skip prompts)")
    parser.add_argument("--batch-reject-source", default=None,
                        help="Reject ALL pending chunks from this source_id (skip prompts)")
    args = parser.parse_args()

    corpus_dir = corpus_root()
    pending_files = _list_pending(corpus_dir, args.asset_family,
                                  args.batch_approve_source or args.batch_reject_source)
    if not pending_files:
        print("(no pending chunks match filter)")
        return 0

    approved_root = corpus_dir / "chunks_approved"
    rejected_root = corpus_dir / "chunks_rejected"

    # Batch mode — no prompts
    if args.batch_approve_source or args.batch_reject_source:
        target = approved_root if args.batch_approve_source else rejected_root
        action = "approved" if args.batch_approve_source else "rejected"
        moved = 0
        for p in pending_files:
            ch = load_chunk_json(p)
            _move(p, target, ch.source_sha)
            moved += 1
        print(f"  {moved} chunks {action} in batch")
        return 0

    # Interactive mode
    print(f"Reviewing {len(pending_files)} pending chunk(s).")
    print("Commands: [a]pprove  [r]eject  [s]kip  [q]uit  [enter]=skip")
    print()
    counts = {"a": 0, "r": 0, "s": 0}
    for i, p in enumerate(pending_files, 1):
        try:
            ch = load_chunk_json(p)
        except Exception as exc:
            print(f"  ✗ failed to load {p.name}: {exc}")
            continue
        print(f"── [{i}/{len(pending_files)}] {ch.chunk_id} ─────────────────────")
        print(f"  source:  {ch.source_id}  (page {ch.page})")
        print(f"  url:     {ch.source_url}")
        print(f"  family:  {ch.asset_families}")
        print(f"  tokens:  {ch.token_count}")
        print(f"  ─ text ─")
        print(f"  {ch.text[:600]}{'...' if len(ch.text) > 600 else ''}")
        print()
        ans = input("  decision (a/r/s/q): ").strip().lower() or "s"
        if ans == "q":
            print("  quitting.")
            break
        if ans == "a":
            _move(p, approved_root, ch.source_sha)
            counts["a"] += 1
        elif ans == "r":
            _move(p, rejected_root, ch.source_sha)
            counts["r"] += 1
        else:
            counts["s"] += 1
        print()
    print("─" * 60)
    print(f"  approved: {counts['a']}  rejected: {counts['r']}  skipped: {counts['s']}")
    print()
    print("  Re-build the index with:")
    print("    python3 scripts/build_industry_corpus_index.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
