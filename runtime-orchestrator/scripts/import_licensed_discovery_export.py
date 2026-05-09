#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy


def _script_path() -> Path:
    return Path(__file__).resolve().with_name("import_scopus_discovery_export.py")


if __name__ == "__main__":
    runpy.run_path(str(_script_path()), run_name="__main__")
