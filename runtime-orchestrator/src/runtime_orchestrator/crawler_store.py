"""Mutable, TTL-based cache for background crawler data.

Separate from ArtifactStore (which is immutable/content-addressed).
This store is keyed by (source_key, ctx_hash) and expires entries by age.

Schema:
    source_cache(
        source_key   TEXT,
        ctx_hash     TEXT,
        data         TEXT,      -- JSON
        fetched_at   REAL,      -- Unix timestamp
        ttl_seconds  INTEGER,
        PRIMARY KEY (source_key, ctx_hash)
    )
"""
from __future__ import annotations

import json
import sqlite3
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

_DEFAULT_TTL = {
    "sec_edgar":        86_400,   # 24 h
    "nyc_open_data":    43_200,   # 12 h
    "federal_api":      86_400,   # 24 h
    "energy_env":       86_400,   # 24 h
    "web_search":       21_600,   # 6 h  (news changes faster)
    "pdf_scraping":     43_200,   # 12 h
    "default":          43_200,   # 12 h fallback
}


def _source_ttl(source_key: str) -> int:
    if source_key.startswith("ws_"):
        return _DEFAULT_TTL["web_search"]
    if source_key.startswith(("sec_", "edgar_", "xbrl_")):
        return _DEFAULT_TTL["sec_edgar"]
    if source_key.startswith(("nyc_", "dob_", "acris_", "pluto_", "ll84_")):
        return _DEFAULT_TTL["nyc_open_data"]
    if source_key.startswith(("esrt_", "ir_", "10k_")):
        return _DEFAULT_TTL["pdf_scraping"]
    if source_key.startswith(("fred_", "bls_", "census_", "hud_", "fhfa_", "eia_")):
        return _DEFAULT_TTL["federal_api"]
    if source_key.startswith(("epa_", "noaa_", "fema_", "usgs_")):
        return _DEFAULT_TTL["energy_env"]
    return _DEFAULT_TTL["default"]


def _ctx_hash(ctx: dict) -> str:
    key_fields = {k: ctx.get(k) for k in ("cik", "ticker", "bbl", "bin", "state_code", "zip_code")}
    return sha256(json.dumps(key_fields, sort_keys=True).encode()).hexdigest()[:16]


class CrawlerStore:
    """Thread-safe SQLite cache for crawled source data."""

    def __init__(self, store_dir: Path) -> None:
        self._db_path = Path(store_dir) / "crawler_cache.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), check_same_thread=False, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS source_cache (
                    source_key   TEXT NOT NULL,
                    ctx_hash     TEXT NOT NULL,
                    data         TEXT NOT NULL,
                    fetched_at   REAL NOT NULL,
                    ttl_seconds  INTEGER NOT NULL,
                    PRIMARY KEY (source_key, ctx_hash)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fetched ON source_cache (fetched_at)
            """)

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, source_key: str, ctx: dict) -> Any | None:
        """Return cached data if fresh, else None."""
        ch = _ctx_hash(ctx)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data, fetched_at, ttl_seconds FROM source_cache "
                "WHERE source_key=? AND ctx_hash=?",
                (source_key, ch),
            ).fetchone()
        if not row:
            return None
        data_str, fetched_at, ttl = row
        if time.time() - fetched_at > ttl:
            return None  # expired
        return json.loads(data_str)

    def put(self, source_key: str, ctx: dict, data: Any, ttl_seconds: int | None = None) -> None:
        """Upsert data into cache."""
        ch = _ctx_hash(ctx)
        ttl = ttl_seconds if ttl_seconds is not None else _source_ttl(source_key)
        payload = json.dumps(data, default=str)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO source_cache "
                "(source_key, ctx_hash, data, fetched_at, ttl_seconds) "
                "VALUES (?,?,?,?,?)",
                (source_key, ch, payload, time.time(), ttl),
            )

    def acquisition_summary(self, source_key: str, ctx: dict) -> dict[str, Any]:
        """Return cached public-page acquisition metadata when present."""
        payload = self.get(source_key, ctx)
        if not isinstance(payload, dict):
            return {}
        acquisition = payload.get("public_page_acquisition", {})
        if not isinstance(acquisition, dict):
            return {}
        static_probe = acquisition.get("static_probe", {}) if isinstance(acquisition.get("static_probe", {}), dict) else {}
        browser_attempt = acquisition.get("browser_attempt", {}) if isinstance(acquisition.get("browser_attempt", {}), dict) else {}
        return {
            "selected_mode": str(acquisition.get("selected_mode", "")).strip(),
            "selection_reason": str(acquisition.get("selection_reason", "")).strip(),
            "static_probe_status": str(static_probe.get("status", "")).strip(),
            "static_render_mode": str(static_probe.get("render_mode", "")).strip(),
            "browser_attempt_status": str(browser_attempt.get("status", "")).strip(),
        }

    def is_stale(self, source_key: str, ctx: dict) -> bool:
        """True if entry is missing or expired."""
        return self.get(source_key, ctx) is None

    def staleness_report(self, ctx: dict) -> list[dict]:
        """Return freshness status for every cached entry matching this ctx."""
        ch = _ctx_hash(ctx)
        now = time.time()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT source_key, fetched_at, ttl_seconds FROM source_cache WHERE ctx_hash=?",
                (ch,),
            ).fetchall()
        report = []
        for key, fetched_at, ttl in rows:
            age = now - fetched_at
            report.append({
                "source_key":   key,
                "age_seconds":  round(age),
                "ttl_seconds":  ttl,
                "fresh":        age <= ttl,
                "pct_expired":  round(age / ttl * 100, 1),
            })
        return sorted(report, key=lambda r: r["pct_expired"], reverse=True)

    def evict_expired(self) -> int:
        """Delete all expired rows. Returns count of deleted rows."""
        now = time.time()
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM source_cache WHERE (? - fetched_at) > ttl_seconds", (now,)
            )
            return cur.rowcount
