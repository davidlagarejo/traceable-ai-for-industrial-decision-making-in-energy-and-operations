#!/usr/bin/env python3
"""Build / refresh the per-asset_family vector indices.

Runs OFFLINE. No motor in the pipeline calls this at runtime.

Usage:
  python3 scripts/build_industry_corpus_index.py            # all families
  python3 scripts/build_industry_corpus_index.py --family manufacturing_facility
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE / "src"))

from runtime_orchestrator.industry_corpus.indexer import (
    build_all_indices, build_index,
)
from runtime_orchestrator.industry_corpus.manifest import CANONICAL_ASSET_FAMILIES


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", default=None,
                        choices=sorted(CANONICAL_ASSET_FAMILIES))
    args = parser.parse_args()

    if args.family:
        stats_list = [build_index(args.family)]
    else:
        stats_list = build_all_indices()

    print("─" * 70)
    print(f"{'asset_family':25s} {'chunks':>8s} {'new':>5s} {'cached':>7s} {'errors':>7s}")
    print("─" * 70)
    for s in stats_list:
        err = len(s.errors)
        print(f"{s.asset_family:25s} {s.chunks_indexed:>8d} {s.new_embeddings:>5d} "
              f"{s.cached_embeddings:>7d} {err:>7d}")
        for e in s.errors:
            print(f"    ✗ {e}")
    print("─" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
