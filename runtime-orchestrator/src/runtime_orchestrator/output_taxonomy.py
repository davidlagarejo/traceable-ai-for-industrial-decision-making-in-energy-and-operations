from __future__ import annotations

from typing import Any

COMPATIBILITY_OUTPUT_MODE_ALIAS_MAP = {
    "Address Candidate Brief": "Decision-Blocked Asset Brief",
    "Site Candidate Brief": "Decision-Blocked Asset Brief",
    "Asset Context Seed Brief": "Decision-Blocked Asset Brief",
    "Asset Context Insufficiency Brief": "Decision-Blocked Asset Brief",
    "Pre-Verification Asset Brief": "Decision-Blocked Asset Brief",
    "Issuer Context Memo": "Target Classification Brief",
    "Entity Address Classification Brief": "Target Classification Brief",
    "Target Clarification Brief": "Target Classification Brief",
    "Exploratory Prior / Minimum Evidence Report": "Exploratory Prior Brief",
    "Decision-Grade Asset Brief": "Full Technical Decision Intelligence Report",
    "Decision-Grade TDIR": "Full Technical Decision Intelligence Report",
    "TDIR Preliminary": "Full Technical Decision Intelligence Report",
}

CANONICAL_VISIBLE_OUTPUT_MODES = (
    "Target Classification Brief",
    "Decision-Blocked Asset Brief",
    "Exploratory Prior Brief",
    "Compliance / Investment Screening Brief",
    "Structural Contradiction Brief",
    "System Redesign Hypothesis Brief",
    "Competitive Positioning Brief",
    "TAD Action Priority Brief",
    "Full Technical Decision Intelligence Report",
)


def canonicalize_output_mode(label: Any) -> str:
    text = str(label or "").strip()
    return COMPATIBILITY_OUTPUT_MODE_ALIAS_MAP.get(text, text)


def canonicalize_output_mode_list(values: list[Any] | tuple[Any, ...] | None) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for item in list(values or []):
        label = canonicalize_output_mode(item)
        if not label or label in seen:
            continue
        seen.add(label)
        normalized.append(label)
    return normalized


def output_mode_alias_policy(label: Any) -> dict[str, Any]:
    raw = str(label or "").strip()
    canonical = canonicalize_output_mode(raw)
    return {
        "raw_label": raw,
        "canonical_label": canonical,
        "is_compatibility_alias": bool(raw and raw != canonical),
        "policy": (
            "Compatibility aliases are allowed at ingest/internal-contract boundaries only. "
            "Visible runtime, manifest, and report surfaces must render the canonical label."
        ),
    }
