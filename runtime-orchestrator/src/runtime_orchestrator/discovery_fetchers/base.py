"""Base contracts for discovery fetchers."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FetcherStatus(str, Enum):
    OK            = "ok"             # data found and admitted
    NO_DATA       = "no_data"        # source queried, no relevant data
    SKIP          = "skip"           # not applicable for this context
    ERROR         = "error"          # fetch failed (network, parse, etc.)
    RATE_LIMITED  = "rate_limited"   # API rate limit hit


@dataclass(frozen=True)
class FetcherContext:
    """Context passed to every fetcher. Some fields may be empty."""
    address:        str = ""
    city:           str = ""
    state:          str = ""        # 2-letter US state code (IL, CA, etc.)
    zip_code:       str = ""
    lat:            float | None = None
    lon:            float | None = None
    naics:          str = ""        # 6-digit NAICS code if known
    asset_family:   str = ""        # cold_chain_facility, manufacturing_facility, ...
    facility_name:  str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "address":       self.address,
            "city":          self.city,
            "state":         self.state,
            "zip_code":      self.zip_code,
            "lat":           self.lat,
            "lon":           self.lon,
            "naics":         self.naics,
            "asset_family":  self.asset_family,
            "facility_name": self.facility_name,
        }


@dataclass(frozen=True)
class FetcherResult:
    """Standardized result from any fetcher."""
    source_key:     str
    status:         FetcherStatus
    payload:        dict[str, Any] = field(default_factory=dict)
    error:          str = ""
    locator:        str = ""       # URL or query string used
    record_count:   int = 0
    fetched_at:     str = ""        # ISO8601 timestamp

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_key":    self.source_key,
            "status":        self.status.value if isinstance(self.status, FetcherStatus) else self.status,
            "payload":       dict(self.payload),
            "error":         self.error,
            "locator":       self.locator,
            "record_count":  self.record_count,
            "fetched_at":    self.fetched_at,
        }


# ── HTTP helper used by all fetchers ──────────────────────────────


DEFAULT_TIMEOUT_SECONDS: int = 15
DEFAULT_USER_AGENT: str = (
    "ZLab-Discovery/1.0 (operational truth framework; "
    "https://github.com/davidlagarejo/traceable-ai-for-industrial-decision-making-in-energy-and-operations)"
)


def http_get_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[Any, str]:
    """GET + JSON parse. Returns (data, final_url). Raises urllib.error.URLError on transport failure."""
    if params:
        q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if q:
            url = url + ("&" if "?" in url else "?") + q
    req = urllib.request.Request(url)
    req.add_header("User-Agent", DEFAULT_USER_AGENT)
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    try:
        return json.loads(raw), url
    except json.JSONDecodeError:
        # Some APIs return JSON wrapped in HTML — strip to first {
        text = raw.decode("utf-8", errors="replace")
        try:
            start = text.index("{")
            end = text.rindex("}")
            return json.loads(text[start:end + 1]), url
        except (ValueError, json.JSONDecodeError):
            raise


def http_get_text(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[str, str]:
    """GET + decode to text. Returns (text, final_url)."""
    if params:
        q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if q:
            url = url + ("&" if "?" in url else "?") + q
    req = urllib.request.Request(url)
    req.add_header("User-Agent", DEFAULT_USER_AGENT)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace"), url
