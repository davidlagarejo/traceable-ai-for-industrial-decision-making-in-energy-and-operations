"""Dataclasses + I/O helpers for industry_corpus sources & chunks.

Contracts:
  · CorpusSource: declares ONE public document (PDF) with provenance.
  · CorpusChunk:  one approved excerpt + its embedding metadata.

Both are frozen + JSON-serializable so they round-trip cleanly through
the curation pipeline.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# Trusted publishers eligible for auto-approval (chunks land directly in
# chunks_approved/, no human gate). Match is case-insensitive against
# `source.added_by` or domain in URL.
#
# Three tiers:
#   1. Federal / public-domain (US gov agencies + national labs)
#   2. Open-access scientific (arXiv, DOAJ — CC-licensed)
#   3. Trusted industrial vendors — companies whose technical reputation
#      depends on the accuracy of their publications. Adding a vendor here
#      means "we trust their whitepapers to be technically sound enough to
#      cite verbatim". Curated allowlist, NOT discoverable.
FEDERAL_AUTO_APPROVE_PUBLISHERS: frozenset[str] = frozenset({
    # ── Federal / national labs (public_domain) ──
    "doe", "eia", "epa", "nrel", "pnnl", "ornl", "lbnl", "nist", "doe_osti",
    "energy.gov", "eia.gov", "epa.gov", "nrel.gov", "pnnl.gov", "ornl.gov",
    "energystar.gov", "osti.gov", "nist.gov",
    # ── Open-access scientific (CC-licensed) ──
    "arxiv", "arxiv.org", "doaj", "doaj.org",
    # ── Trusted industrial vendors (whitepapers, technical bulletins) ──
    # Steam / thermal systems:
    "steamloc",     "spirax sarco", "armstrong international", "watson mcdaniel",
    # HVAC / refrigeration majors:
    "trane", "carrier", "johnson controls", "daikin", "danfoss", "bitzer",
    # Industrial automation / controls:
    "emerson", "abb", "siemens", "schneider electric", "honeywell",
    "rockwell automation", "yokogawa",
    # Compressors / motors / drives:
    "atlas copco", "ingersoll rand", "kaeser", "sullair", "gardner denver",
    # Chemicals / industrial gases:
    "linde", "air products", "air liquide", "praxair",
    # Pumps / mechanical:
    "grundfos", "ksb", "flowserve", "sulzer",
    # Heavy industrials / engines:
    "ge", "general electric", "caterpillar", "cummins", "mitsubishi heavy industries",
    # Process / energy equipment:
    "alfa laval", "doosan", "babcock wilcox",
})


# Subset that does NOT require special "added_by=system_verified" — corporate
# vendor whitepapers can be added by anyone (the publisher allowlist itself
# is the trust gate). Federal/scientific still require system_verified to
# guard against typos in user-added YAMLs.
VENDOR_TRUST_PUBLISHERS: frozenset[str] = frozenset({
    "steamloc", "spirax sarco", "armstrong international", "watson mcdaniel",
    "trane", "carrier", "johnson controls", "daikin", "danfoss", "bitzer",
    "emerson", "abb", "siemens", "schneider electric", "honeywell",
    "rockwell automation", "yokogawa",
    "atlas copco", "ingersoll rand", "kaeser", "sullair", "gardner denver",
    "linde", "air products", "air liquide", "praxair",
    "grundfos", "ksb", "flowserve", "sulzer",
    "ge", "general electric", "caterpillar", "cummins", "mitsubishi heavy industries",
    "alfa laval", "doosan", "babcock wilcox",
})


# 6 canonical asset families recognized by the framework. _shared = applies
# to multiple (e.g. ASHRAE 90.1).
CANONICAL_ASSET_FAMILIES: frozenset[str] = frozenset({
    "cold_chain_facility",
    "manufacturing_facility",
    "datacenter",
    "commercial_building",
    "warehouse_distribution",
    "infrastructure_node",
    "_shared",
})


@dataclass(frozen=True)
class CorpusSource:
    """Manifest for ONE document in the industry corpus."""
    source_id:       str         # "doe_better_plants_2022"
    title:           str
    url:             str         # HTTPS only
    license:         str         # "public_domain" | "fair_use_quote" | "permissive"
    asset_families:  tuple[str, ...]
    version:         str         # "2022-rev3"
    added_at:        str         # ISO8601 UTC
    added_by:        str         # "system_verified" | "davidsan" | "claude"
    publisher:       str = ""    # "doe" | "epa" | "iiar" | "ashrae" | …
    notes:           str = ""

    def is_auto_approvable(self) -> bool:
        """True iff this source can skip human curation.

        Three valid paths:
          1. Federal/public_domain + added_by=system_verified
          2. arxiv/open_access + added_by=system_verified
          3. Trusted industrial vendor (publisher in VENDOR_TRUST_PUBLISHERS,
             license in permissive set). The vendor allowlist itself is
             the trust gate — no system_verified requirement.

        Explicit NEVER-auto-approve:
          · license == "licensed_journal" — paywalled content (IEEE/Springer/
            Elsevier/Scopus). Always routes to chunks_pending/ for human
            review even when added_by=system_verified.
        """
        # Hard NO: paywall content always needs human review
        if self.license == "licensed_journal":
            return False

        pub = (self.publisher or "").lower().strip()
        u = (self.url or "").lower()

        # Path 3: trusted industrial vendor whitepapers
        if pub in VENDOR_TRUST_PUBLISHERS:
            if self.license in ("permissive_with_attribution",
                                "vendor_whitepaper",
                                "public_domain"):
                return True
            return False
        # Path 2: arxiv / open access
        if pub in ("arxiv", "arxiv.org", "doaj", "doaj.org") or "arxiv.org" in u:
            if self.license in ("open_access", "cc_by", "public_domain"):
                return self.added_by == "system_verified"
            return False
        # Path 1: federal / national labs
        if self.license != "public_domain":
            return False
        if self.added_by != "system_verified":
            return False
        if pub in FEDERAL_AUTO_APPROVE_PUBLISHERS:
            return True
        return any(dom in u for dom in FEDERAL_AUTO_APPROVE_PUBLISHERS)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["asset_families"] = list(self.asset_families)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CorpusSource":
        return cls(
            source_id      = str(d["source_id"]).strip(),
            title          = str(d.get("title", "")).strip(),
            url            = str(d["url"]).strip(),
            license        = str(d.get("license", "")).strip(),
            asset_families = tuple(d.get("asset_families", []) or []),
            version        = str(d.get("version", "")).strip(),
            added_at       = str(d.get("added_at", "")).strip(),
            added_by       = str(d.get("added_by", "")).strip(),
            publisher      = str(d.get("publisher", "")).strip(),
            notes          = str(d.get("notes", "")).strip(),
        )


@dataclass(frozen=True)
class CorpusChunk:
    """One indexable excerpt from a CorpusSource."""
    chunk_id:        str         # "<source_sha8>::chunk_NNNN"
    source_id:       str
    source_sha:      str         # sha256(url) — links to raw_pdfs/<sha>.pdf
    source_url:      str
    asset_families:  tuple[str, ...]
    page:            int
    text:            str
    token_count:     int
    text_sha:        str         # sha256(text) — idempotency key
    extracted_at:    str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["asset_families"] = list(self.asset_families)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CorpusChunk":
        return cls(
            chunk_id       = str(d["chunk_id"]),
            source_id      = str(d["source_id"]),
            source_sha     = str(d["source_sha"]),
            source_url     = str(d.get("source_url", "")),
            asset_families = tuple(d.get("asset_families", []) or []),
            page           = int(d.get("page", 0) or 0),
            text           = str(d.get("text", "")),
            token_count    = int(d.get("token_count", 0) or 0),
            text_sha       = str(d.get("text_sha", "")),
            extracted_at   = str(d.get("extracted_at", "")),
        )


# ── I/O helpers ────────────────────────────────────────────────────────


def corpus_root(runtime_orchestrator_dir: Path | None = None) -> Path:
    """Return the canonical industry_corpus/ root path."""
    if runtime_orchestrator_dir:
        return runtime_orchestrator_dir / "industry_corpus"
    # Default: walk up from this file → src/runtime_orchestrator/industry_corpus/__init__.py
    # → runtime-orchestrator/industry_corpus/
    return Path(__file__).resolve().parents[3] / "industry_corpus"


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_url(url: str) -> str:
    """Same hashing as pdf_url_fetcher — 32 chars of sha256(url).
    This is what binds a CorpusSource to its cached PDF."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]


def load_source_yaml(yaml_path: Path) -> CorpusSource:
    """Parse a source manifest YAML (flat key:value, no PyYAML dep)."""
    raw: dict[str, Any] = {}
    list_mode_key: str | None = None
    for line in yaml_path.read_text(encoding="utf-8").splitlines():
        s = line.rstrip()
        if not s or s.lstrip().startswith("#"):
            continue
        if list_mode_key and s.startswith("  - "):
            raw.setdefault(list_mode_key, []).append(s[4:].strip().strip('"').strip("'"))
            continue
        list_mode_key = None
        if ":" in s and not s.startswith(" "):
            k, _, v = s.partition(":")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if not v:
                # likely a list follows
                list_mode_key = k
                raw[k] = []
            else:
                raw[k] = v
    return CorpusSource.from_dict(raw)


def write_chunk_json(chunk: CorpusChunk, target_dir: Path) -> Path:
    """Write a chunk to <target_dir>/<chunk_id>.json (idempotent)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / f"{chunk.chunk_id.split('::')[-1]}.json"
    out.write_text(json.dumps(chunk.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def load_chunk_json(path: Path) -> CorpusChunk:
    return CorpusChunk.from_dict(json.loads(path.read_text(encoding="utf-8")))
