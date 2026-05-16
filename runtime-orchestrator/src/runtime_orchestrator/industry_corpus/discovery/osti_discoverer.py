"""DOE OSTI discoverer — proactively finds new technical reports on
osti.gov via their public JSON API.

API:    https://www.osti.gov/api/v1/records
Docs:   https://www.osti.gov/api/v1
Filter we use:
  · product_type=Technical Report   (only OSTI-hosted PDFs, never paywalled
    journal articles whose `servlets/purl/<id>` would 404)
  · publication_date_start (last 24 months by default)
  · q=<keywords for asset_family>

Each result yields a candidate source with:
  · osti_id        → source_id = "doe_osti_<id>"
  · title          → CorpusSource.title
  · subjects       → asset_families derivation
  · purl URL       → https://www.osti.gov/servlets/purl/<osti_id>
                     (verified 200 before yielding via HEAD)

Determinism: same query parameters → same result list (OSTI returns
sorted by recency; we paginate stably).

Phase 0: zero LLM. Keyword-based filtering only.
"""
from __future__ import annotations

import datetime as _dt
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


OSTI_API = "https://www.osti.gov/api/v1/records"
PURL_BASE = "https://www.osti.gov/servlets/purl"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15 ZLab-Discoverer/1.0"
)


# asset_family → search keywords. Tuned empirically against actual OSTI
# subject vocabulary. Each list of keywords is OR'd in the OSTI query.
SUBJECT_KEYWORDS: dict[str, list[str]] = {
    "cold_chain_facility": [
        "cold storage", "refrigerated warehouse", "ammonia refrigeration",
        "blast freezing", "frozen food", "cold chain logistics",
        "industrial refrigeration system", "evaporator coil",
        "freezer compressor", "condenser refrigeration",
        "defrost cycle energy", "cold storage envelope insulation",
        "vapor compression cycle", "two-stage compressor refrigeration",
        "secondary loop refrigeration", "CO2 cascade refrigeration",
        "cold dock loading",
    ],
    "manufacturing_facility": [
        "industrial energy efficiency", "process heating",
        "compressed air manufacturing", "motor systems energy",
        "pulp paper manufacturing", "cement manufacturing kiln",
        "steel manufacturing efficiency", "chemical process plant",
        "industrial boiler efficiency", "steam system audit",
        "heat exchanger fouling", "waste heat recovery industrial",
        "VFD pump industrial", "pump system industrial",
        "industrial combustion control", "process furnace efficiency",
        "industrial cooling tower", "metal casting energy",
        "glass manufacturing energy", "food processing energy",
        "pharmaceutical manufacturing utilities",
        "automotive plant energy", "textile mill energy",
    ],
    "datacenter": [
        "data center energy efficiency", "data center cooling",
        "server farm thermal management", "PUE data center",
        "data center liquid cooling", "free cooling data center",
        "hot aisle containment", "data center power architecture",
        "UPS efficiency", "data center economizer",
        "computer room air handler", "data center waste heat reuse",
    ],
    "commercial_building": [
        "commercial building energy", "office building HVAC",
        "building envelope retrofit", "ASHRAE building",
        "chiller plant optimization", "BAS building automation system",
        "VRF variable refrigerant flow", "rooftop unit RTU",
        "demand controlled ventilation", "building benchmark EUI",
        "ENERGY STAR building",
        "deep energy retrofit", "lighting controls daylight",
        "retro-commissioning", "fault detection diagnostics",
        "thermal energy storage building",
    ],
    "warehouse_distribution": [
        "warehouse distribution energy", "fulfillment center",
        "logistics facility lighting", "warehouse high bay",
        "dock door warehouse", "LED warehouse lighting",
        "warehouse energy audit", "material handling energy",
        "AS/RS automated storage", "battery charging warehouse",
        "warehouse roof insulation",
    ],
    "infrastructure_node": [
        "electrical substation transformer", "transmission grid",
        "natural gas pipeline compression", "rail freight operations",
        "power transformer efficiency", "transformer no-load losses",
        "distribution feeder loss", "smart grid SCADA",
        "pipeline pumping station", "compressor station",
        "renewable integration grid", "battery energy storage system",
    ],
}


# Map subject keywords back to asset_families for tag inference.
def _families_for_subjects(subjects: list[str], asset_family_hint: str) -> list[str]:
    """Given OSTI subject tags, decide which asset_families this PDF
    belongs to. Always includes the family that triggered the search,
    plus '_shared' if the topic is broad."""
    out = {asset_family_hint}
    text = " ".join(s.lower() for s in (subjects or []))
    if any(kw in text for kw in ("policy", "overview", "national", "sector wide")):
        out.add("_shared")
    return sorted(out)


@dataclass(frozen=True)
class CandidateSource:
    """A discovered (not yet ingested) source from a publisher API."""
    publisher:       str               # "doe_osti"
    source_id:       str               # "doe_osti_3020107"
    title:           str
    url:             str               # purl PDF download URL
    asset_families:  tuple[str, ...]
    publication_date: str
    osti_record_id:  str
    raw_subjects:    tuple[str, ...]


def _http_get_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _head_ok(url: str, timeout: int = 8) -> bool:
    """Confirm purl/<id> resolves to a real PDF before yielding the candidate."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ctype = r.headers.get("Content-Type", "").lower()
            return r.status == 200 and (
                "pdf" in ctype or "octet-stream" in ctype
                or url.lower().endswith(".pdf")
            )
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False


def _query_osti(keyword: str, *, rows: int = 25, since_days: int = 365) -> list[dict]:
    """Hit OSTI API for technical reports matching `keyword`.

    Always restricts to product_type=Technical Report so the purl PDF
    download will work (journal articles 404 on /servlets/purl/).
    """
    since = (_dt.date.today() - _dt.timedelta(days=since_days)).strftime("%m/%d/%Y")
    qs = urllib.parse.urlencode({
        "q":                       keyword,
        "rows":                    rows,
        "product_type":            "Technical Report",
        "publication_date_start":  since,
    })
    try:
        return _http_get_json(f"{OSTI_API}?{qs}") or []
    except Exception:
        return []


def discover_for_family(
    asset_family: str,
    *,
    rows_per_keyword: int = 10,
    since_days: int = 540,
    max_candidates: int = 30,
    head_verify: bool = True,
) -> list[CandidateSource]:
    """Return new OSTI technical reports relevant to `asset_family`.

    Pipeline:
      1. For each keyword in SUBJECT_KEYWORDS[asset_family], query OSTI.
      2. Build CandidateSource for each result.
      3. HEAD-verify purl URL (drop dead links).
      4. Dedup by osti_id.
      5. Cap at `max_candidates`.

    Does NOT write anything to disk — caller decides whether to materialize
    each candidate into a sources/*.yaml.
    """
    keywords = SUBJECT_KEYWORDS.get(asset_family, [])
    if not keywords:
        return []
    seen_ids: set[str] = set()
    out: list[CandidateSource] = []
    for kw in keywords:
        if len(out) >= max_candidates:
            break
        records = _query_osti(kw, rows=rows_per_keyword, since_days=since_days)
        for r in records:
            osti_id = str(r.get("osti_id") or "").strip()
            if not osti_id or osti_id in seen_ids:
                continue
            seen_ids.add(osti_id)
            title = (r.get("title") or "").strip()
            subjects = list(r.get("subjects") or [])
            pub_date = (r.get("publication_date") or "")[:10]
            url = f"{PURL_BASE}/{osti_id}"
            if head_verify and not _head_ok(url):
                continue
            out.append(CandidateSource(
                publisher="doe_osti",
                source_id=f"doe_osti_{osti_id}",
                title=title[:200],
                url=url,
                asset_families=tuple(_families_for_subjects(subjects, asset_family)),
                publication_date=pub_date,
                osti_record_id=osti_id,
                raw_subjects=tuple(subjects[:10]),
            ))
            if len(out) >= max_candidates:
                break
    return out
