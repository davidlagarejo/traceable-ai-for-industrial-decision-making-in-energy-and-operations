#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_runtime_root() / "src"))

from runtime_orchestrator.zlab_skill import scaffold_local_licensed_artifact_templates  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold metadata and extraction templates for local licensed PDFs."
    )
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--provider-key", default="scopus")
    parser.add_argument("--retrieval-purpose", default="pattern_seed_discovery")
    args = parser.parse_args()

    payload = scaffold_local_licensed_artifact_templates(
        input_dir=str(args.input_dir).strip(),
        provider_key=str(args.provider_key).strip(),
        retrieval_purpose=str(args.retrieval_purpose).strip(),
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
