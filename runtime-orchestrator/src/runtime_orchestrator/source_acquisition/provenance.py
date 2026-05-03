from __future__ import annotations

import hashlib
from typing import Any


def _sha256_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8", errors="ignore")).hexdigest()


def build_provenance_manifest(
    *,
    acquisition_mode: str,
    requested_url: str,
    final_url: str,
    html: str,
    visible_text: str,
    selector_lineage: list[dict[str, Any]] | list[str] | None,
    attempt_outcome: str,
) -> dict[str, Any]:
    return {
        "acquisition_mode": acquisition_mode,
        "requested_url": str(requested_url or "").strip(),
        "final_url": str(final_url or requested_url or "").strip(),
        "dom_sha256": _sha256_text(html or ""),
        "visible_text_sha256": _sha256_text(visible_text or ""),
        "dom_length": len(html or ""),
        "visible_text_length": len(visible_text or ""),
        "selector_lineage": list(selector_lineage or []),
        "attempt_outcome": str(attempt_outcome or "").strip(),
    }
