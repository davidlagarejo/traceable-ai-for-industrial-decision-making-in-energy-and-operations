#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_runtime_root() / "src"))

from runtime_orchestrator.zlab_skill import (  # noqa: E402
    ingest_local_licensed_artifact_batch,
    load_registry_bundle,
)


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest local licensed PDFs into extraction/review/promotion surfaces."
    )
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--retrieval-purpose", default="pattern_seed_discovery")
    parser.add_argument("--source-basis-id", default="licensed_research_public_technical_priors")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser()
    output_dir = (
        Path(args.output_dir).expanduser()
        if str(args.output_dir).strip()
        else _runtime_root() / "run-registry" / "licensed-research-local" / _utc_tag()
    )
    bundle = load_registry_bundle()
    payload = ingest_local_licensed_artifact_batch(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        registry_bundle=bundle,
        retrieval_purpose=str(args.retrieval_purpose).strip(),
        source_basis_id=str(args.source_basis_id).strip(),
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
