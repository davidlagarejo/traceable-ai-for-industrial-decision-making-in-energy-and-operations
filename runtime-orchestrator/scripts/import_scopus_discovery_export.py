#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_runtime_root() / "src"))

from runtime_orchestrator.zlab_skill import (  # noqa: E402
    load_registry_bundle,
    materialize_licensed_discovery_candidate_queue,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import a licensed discovery export and materialize candidate PDF queue + sidecars."
    )
    parser.add_argument("--export-path", required=True)
    parser.add_argument("--intake-dir", required=True)
    parser.add_argument("--provider-key", default="scopus")
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--retrieval-purpose", default="pattern_seed_discovery")
    parser.add_argument("--source-basis-id", default="licensed_research_public_technical_priors")
    args = parser.parse_args()

    payload = materialize_licensed_discovery_candidate_queue(
        export_path=str(args.export_path).strip(),
        intake_dir=str(args.intake_dir).strip(),
        provider_key=str(args.provider_key).strip().lower(),
        registry_bundle=load_registry_bundle(),
        top_k=int(args.top_k),
        retrieval_purpose=str(args.retrieval_purpose).strip(),
        source_basis_id=str(args.source_basis_id).strip(),
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
