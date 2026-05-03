"""Background crawler for motor_028 source data.

Runs as a daemon thread that periodically refreshes all sources in
_EXTENDED_SOURCE_REGISTRY that have stale or missing cache entries.

Usage:
    from runtime_orchestrator.background_crawler import BackgroundCrawler
    from runtime_orchestrator.crawler_store import CrawlerStore
    from pathlib import Path

    store = CrawlerStore(Path("/var/zlab/crawler_cache"))
    ctx   = {"cik": "1560327", "ticker": "ESRT", ...}

    crawler = BackgroundCrawler(store=store, ctx=ctx)
    crawler.start()          # launches daemon thread
    ...
    crawler.stop()           # graceful shutdown

The pipeline (motor_028) calls:
    result = crawler.get_cached_or_live(source_key, fn, ctx)
which returns cached data when fresh, otherwise calls fn(ctx) live and
writes the result into the cache before returning.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable

from .crawler_store import CrawlerStore

logger = logging.getLogger(__name__)

# How often the sweep loop checks for stale entries (seconds).
_SWEEP_INTERVAL = 300   # 5 minutes


class BackgroundCrawler:
    """Daemon thread that keeps CrawlerStore fresh by re-fetching stale sources."""

    def __init__(
        self,
        store: CrawlerStore,
        ctx: dict,
        sweep_interval: int = _SWEEP_INTERVAL,
    ) -> None:
        self._store = store
        self._ctx = ctx
        self._sweep_interval = sweep_interval
        self._registry: list[dict] = []   # populated via register()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    # ── Registry ──────────────────────────────────────────────────────────────

    def register_sources(self, registry: list[dict]) -> None:
        """Register source specs from _EXTENDED_SOURCE_REGISTRY."""
        with self._lock:
            self._registry = list(registry)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._sweep_loop,
            name="zlab-background-crawler",
            daemon=True,
        )
        self._thread.start()
        logger.info("BackgroundCrawler started (sweep_interval=%ds)", self._sweep_interval)

    def stop(self, timeout: float = 10.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        logger.info("BackgroundCrawler stopped")

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    # ── Core: cached-or-live fetch ────────────────────────────────────────────

    def get_cached_or_live(
        self,
        source_key: str,
        fn: Callable[[dict], Any],
        ctx: dict,
    ) -> Any:
        """Return cached data if fresh; otherwise call fn(ctx), cache, and return."""
        cached = self._store.get(source_key, ctx)
        if cached is not None:
            return cached
        data = fn(ctx)
        if data is not None:
            self._store.put(source_key, ctx, data)
        return data

    # ── Background sweep ──────────────────────────────────────────────────────

    def _sweep_loop(self) -> None:
        logger.info("BackgroundCrawler sweep loop running")
        while not self._stop_event.is_set():
            try:
                self._refresh_stale()
                self._store.evict_expired()
            except Exception as exc:
                logger.warning("BackgroundCrawler sweep error: %s", exc)
            self._stop_event.wait(timeout=self._sweep_interval)

    def _refresh_stale(self) -> None:
        with self._lock:
            specs = list(self._registry)

        refreshed = 0
        skipped   = 0
        errors    = 0

        for spec in specs:
            if self._stop_event.is_set():
                break

            key = spec.get("key", "")
            fn  = spec.get("fn")
            if not key or not callable(fn):
                continue

            if not self._store.is_stale(key, self._ctx):
                skipped += 1
                continue

            try:
                data = fn(self._ctx)
                if data is not None:
                    self._store.put(key, self._ctx, data)
                    refreshed += 1
                    logger.debug("BackgroundCrawler refreshed: %s", key)
                # If data is None the source is unavailable (no key, 404, etc.)
                # We do NOT cache None — next sweep will retry.
            except Exception as exc:
                errors += 1
                logger.debug("BackgroundCrawler fetch error [%s]: %s", key, exc)

            # Small sleep between sources to avoid hammering APIs
            time.sleep(0.5)

        logger.info(
            "BackgroundCrawler sweep done — refreshed=%d skipped=%d errors=%d",
            refreshed, skipped, errors,
        )

    # ── Introspection ─────────────────────────────────────────────────────────

    def staleness_report(self) -> list[dict]:
        return self._store.staleness_report(self._ctx)

    def cache_status(self) -> dict:
        report = self.staleness_report()
        fresh  = [r for r in report if r["fresh"]]
        stale  = [r for r in report if not r["fresh"]]
        return {
            "total_cached": len(report),
            "fresh":        len(fresh),
            "stale":        len(stale),
            "registered":   len(self._registry),
            "is_running":   self.is_running(),
        }
