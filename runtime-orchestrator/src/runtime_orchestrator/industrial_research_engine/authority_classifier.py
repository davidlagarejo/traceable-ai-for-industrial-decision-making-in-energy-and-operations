"""V5 P4 — deterministic authority_tier classifier.

S6 scaffolding (industrial_source_catalog.json) records each source's
authority_tier (1/2/3) but the curation was hand-assigned by Claude.
This module pays down that scaffolding: it classifies a source into
tier 1/2/3 from OBSERVABLE SIGNALS (publisher class, type, jurisdiction)
deterministically.

Tier definitions (Phase 0 / catalog `tier_definitions`):
  1 — Regulatory, codes, mandatory standards. Highest evidentiary weight.
  2 — Peer-reviewed engineering handbooks, national-lab reports, official
      industry consensus standards.
  3 — Vendor application guides, industry whitepapers, trade-association
      case studies, market reports. Lower evidentiary weight.

This module does NOT modify the catalog. It can:
  - Classify a NEW source proposed via motor_028 discovery
  - Audit an EXISTING catalog entry (deterministic_tier vs. recorded_tier)

Phase 0 anchor: no LLM. Pure rule-based classification.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..source_catalog import load_catalog


# Signal vocabularies. Each set holds normalized tokens that, when
# detected in a source's publisher / type / name, push it toward a tier.

# Tier 1 — regulators, code-issuing bodies, statutory standards orgs.
_TIER_1_PUBLISHER_TOKENS: tuple[str, ...] = (
    # US federal
    "epa", "doe", "eia", "ferc", "osha", "nrc", "nist", "us treasury", "irs",
    "us department", "us doe", "us energy information", "us congress",
    "u.s. environmental", "federal energy",
    # Standards bodies + codes
    "iso", "iec", "ieee", "ashrae", "ansi", "astm", "nfpa", "ul",
    "iiar", "ashe", "smacna", "icc", "asme", "api ",
    "international institute of ammonia",  # IIAR full name
    "international institute of refrigeration",  # IIR full name (also tier 1 as global standards body)
    # International / multilateral
    "iea", "unfccc", "ipcc", "olade", "wri", "world bank",
    # National (non-US)
    "upme", "creg", "minminas", "ministerio", "national renewable",
    "nrel", "lbnl", "lawrence berkeley",
    "comisión", "ministerio de",
    # Industry-mandated trade associations operating under code
    "association of american railroads",
)

_TIER_1_TYPES: frozenset[str] = frozenset({
    "regulation", "regulatory", "policy", "standard", "code",
})

_TIER_2_PUBLISHER_TOKENS: tuple[str, ...] = (
    # National labs (non-regulator)
    "pacific northwest", "argonne", "oak ridge", "sandia", "pnnl",
    # Engineering societies (handbook publishers)
    "aiche", "ccps", "ashrae handbook",
    # Industry-association handbooks
    "fenercom", "idae", "agencia andaluza",
    "garrigues", "corpoema",
    # Peer-reviewed publishers
    "elsevier", "springer", "wiley", "taylor", "iir",
    # International district energy consortia
    "idea", "international district energy",
    # University / research
    "university", "universidad", "polytechnic",
)

_TIER_2_TYPES: frozenset[str] = frozenset({
    "handbook", "guideline", "research_paper", "webinar",
    "training", "report", "thesis",
})

_TIER_3_PUBLISHER_TOKENS: tuple[str, ...] = (
    # Vendors / OEMs
    "johnson controls", "schneider electric", "siemens", "danfoss",
    "honeywell", "mitsubishi electric", "mhi", "bitzer", "emerson",
    "trane", "carrier", "york", "abb", "rockwell", "ingersoll rand",
    "goodyear", "atlas copco", "kaeser",
    # Utilities (vendor-adjacent case studies)
    "pacific gas", "consolidated edison", "duke energy",
    # Market research
    "arc advisory", "frost & sullivan", "navigant", "guidehouse",
)

_TIER_3_TYPES: frozenset[str] = frozenset({
    "whitepaper", "case_study",
})


def _norm(value: Any) -> str:
    return str(value or "").lower().strip()


def _publisher_signal(publisher: str) -> int | None:
    """Return the tier signalled by the publisher token alone, or None.

    Checks tier 1 first (most authoritative wins on overlap).
    """
    p = _norm(publisher)
    if not p:
        return None
    for token in _TIER_1_PUBLISHER_TOKENS:
        if token in p:
            return 1
    for token in _TIER_2_PUBLISHER_TOKENS:
        if token in p:
            return 2
    for token in _TIER_3_PUBLISHER_TOKENS:
        if token in p:
            return 3
    return None


def _type_signal(source_type: str) -> int | None:
    """Return the tier signalled by the source `type` value, or None.

    Type alone does not promote to tier 1 — only regulator/code types do.
    """
    t = _norm(source_type)
    if t in _TIER_1_TYPES:
        return 1
    if t in _TIER_3_TYPES:
        return 3
    if t in _TIER_2_TYPES:
        return 2
    return None


def classify_authority_tier(source_entry: Mapping[str, Any]) -> dict[str, Any]:
    """Classify a source into authority_tier 1/2/3 deterministically.

    Strategy:
      1. Publisher token wins (most specific signal)
      2. Type signal as tie-breaker if publisher is unknown
      3. Default to tier 3 (most conservative — vendor/whitepaper)

    Returns:
      {
        "deterministic_tier": 1 | 2 | 3,
        "signals": {"publisher": int|None, "type": int|None},
        "rationale": str,
      }
    """
    publisher = source_entry.get("publisher", "")
    source_type = source_entry.get("type", "")
    pub_signal = _publisher_signal(publisher)
    type_signal = _type_signal(source_type)

    if pub_signal is not None:
        tier = pub_signal
        rationale = f"publisher token matched tier {tier}: {publisher!r}"
    elif type_signal is not None:
        tier = type_signal
        rationale = f"type signal matched tier {tier}: {source_type!r}"
    else:
        tier = 3
        rationale = (
            f"no publisher / type signal matched — defaulting to "
            f"conservative tier 3 (publisher={publisher!r}, type={source_type!r})"
        )

    return {
        "deterministic_tier": tier,
        "signals": {"publisher": pub_signal, "type": type_signal},
        "rationale": rationale,
    }


def audit_catalog_against_classifier() -> dict[str, Any]:
    """Run the classifier across every catalog entry and report
    deterministic_tier vs. recorded_tier divergences.

    Useful to spot S6 scaffolding mistakes (Claude assigned tier 2 to
    a vendor that the classifier would put at tier 3, etc.).

    Returns:
      {
        "total": int,
        "aligned": int,
        "divergent": [{"source_id", "recorded_tier", "deterministic_tier",
                       "rationale"}, ...],
        "tier_promoted": int,    # recorded < deterministic (catalog more conservative)
        "tier_demoted": int,     # recorded > deterministic (catalog optimistic)
      }
    """
    catalog = load_catalog()
    sources = catalog.get("sources", []) or []
    aligned = 0
    divergent: list[dict[str, Any]] = []
    promoted = 0
    demoted = 0
    for entry in sources:
        recorded = int(entry.get("authority_tier", 0) or 0)
        verdict = classify_authority_tier(entry)
        det = int(verdict["deterministic_tier"])
        if det == recorded:
            aligned += 1
            continue
        if recorded > det:
            promoted += 1
        else:
            demoted += 1
        divergent.append({
            "source_id": entry.get("source_id", ""),
            "publisher": entry.get("publisher", ""),
            "type": entry.get("type", ""),
            "recorded_tier": recorded,
            "deterministic_tier": det,
            "rationale": verdict["rationale"],
        })
    return {
        "total": len(sources),
        "aligned": aligned,
        "divergent": divergent,
        "tier_promoted": promoted,
        "tier_demoted": demoted,
    }
