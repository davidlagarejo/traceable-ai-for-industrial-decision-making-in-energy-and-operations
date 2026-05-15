"""PDF URL fetcher — download public technical PDFs for the
deterministic extractor (V4 P3 bridge).

Rules:
  · HTTPS only.
  · Max size: 30 MB per PDF (cap).
  · Timeout: 60s.
  · Content-Type must be application/pdf OR URL ends in .pdf.
  · Cache to disk under `pdf_cache/<sha256-of-url>.pdf` so re-runs are fast.

This is the network sibling of local_pdf_autodraft. The extractor expects
a LOCAL path → this module gives you that path from a URL.

No API keys required. Uses only stdlib.
"""
from __future__ import annotations

import hashlib
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_TIMEOUT_SECONDS: int = 60
# 50 MB — accommodates large DOE OSTI technical reports (some are 35-45 MB).
# Anything beyond this is almost always image-heavy and not worth chunking.
MAX_BYTES: int = 50 * 1024 * 1024  # 50 MB
USER_AGENT: str = (
    # Browser-like UA — some federal sites (EPA, PNNL) block obvious bot UAs
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15 ZLab-Discovery/1.0"
)


@dataclass(frozen=True)
class PDFFetchResult:
    url:           str
    local_path:    str
    status:        str            # "ok" | "cached" | "error" | "rejected" | "blocked"
    bytes_written: int
    content_type:  str
    error:         str = ""
    elapsed_s:     float = 0.0
    # How we got it: "stdlib" (urllib direct) | "playwright" (browser fallback)
    # | "cache" (already on disk) | "" (never fetched).
    fetched_via:   str = ""


# HTTP statuses that typically mean "server actively blocked the bot" rather
# than "URL is gone". For these we try the Playwright fallback before giving up.
_BLOCK_STATUS_CODES = frozenset({401, 403, 406, 429, 451, 503})


def _cache_root() -> Path:
    # runtime-orchestrator/pdf_cache/
    return Path(__file__).resolve().parents[3] / "pdf_cache"


def _cache_path_for(url: str) -> Path:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
    return _cache_root() / f"{h}.pdf"


def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def _fetch_pdf_with_playwright(
    url: str, cache_path: Path, max_bytes: int, timeout_s: int,
) -> PDFFetchResult:
    """Fallback: use headless Chromium to fetch a PDF when the stdlib client
    is blocked (Cloudflare interstitial, bot detection, JS-gated download, …).

    Playwright presents a full browser fingerprint, so federal/state portals
    that 403 plain urllib will usually serve the file here.

    Returns status="ok" on success, "blocked" if still blocked, "error" otherwise.
    """
    started = time.time()
    if not _playwright_available():
        return PDFFetchResult(
            url=url, local_path="", status="blocked", bytes_written=0,
            content_type="",
            error=("blocked by server AND playwright is not installed — "
                   "run: pip install playwright && playwright install chromium"),
            elapsed_s=time.time() - started,
            fetched_via="",
        )
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 800},
                accept_downloads=True,
            )
            # Use Playwright's APIRequestContext — it shares cookies / TLS
            # fingerprint with the browser but lets us stream raw bytes.
            api = context.request
            resp = api.get(url, timeout=timeout_s * 1000)
            status_code = resp.status
            ctype = (resp.headers.get("content-type", "") or "").lower()
            if status_code >= 400:
                browser.close()
                return PDFFetchResult(
                    url=url, local_path="", status="blocked",
                    bytes_written=0, content_type=ctype,
                    error=f"playwright also got HTTP {status_code}",
                    elapsed_s=time.time() - started,
                    fetched_via="playwright",
                )
            body = resp.body()
            browser.close()
            if len(body) > max_bytes:
                return PDFFetchResult(
                    url=url, local_path="", status="rejected",
                    bytes_written=len(body), content_type=ctype,
                    error=f"PDF exceeds max size ({max_bytes} bytes)",
                    elapsed_s=time.time() - started,
                    fetched_via="playwright",
                )
            is_pdf = (
                "application/pdf" in ctype
                or "octet-stream" in ctype
                or body[:4] == b"%PDF"
            )
            if not is_pdf:
                return PDFFetchResult(
                    url=url, local_path="", status="blocked",
                    bytes_written=len(body), content_type=ctype,
                    error=(f"playwright got non-PDF response (content-type={ctype!r}) "
                           "— probably an interstitial/login wall"),
                    elapsed_s=time.time() - started,
                    fetched_via="playwright",
                )
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(body)
            return PDFFetchResult(
                url=url, local_path=str(cache_path), status="ok",
                bytes_written=len(body), content_type=ctype,
                elapsed_s=time.time() - started,
                fetched_via="playwright",
            )
    except Exception as exc:
        return PDFFetchResult(
            url=url, local_path="", status="error", bytes_written=0,
            content_type="",
            error=f"playwright fallback failed: {type(exc).__name__}: {exc}",
            elapsed_s=time.time() - started,
            fetched_via="playwright",
        )


def fetch_pdf_from_url(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = MAX_BYTES,
    use_cache: bool = True,
) -> PDFFetchResult:
    """Download a public PDF safely. Returns local_path on success."""
    started = time.time()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        return PDFFetchResult(
            url=url, local_path="", status="rejected", bytes_written=0,
            content_type="",
            error="only HTTPS URLs allowed (got scheme={!r})".format(parsed.scheme),
            elapsed_s=time.time() - started,
        )

    cache = _cache_path_for(url)
    if use_cache and cache.exists() and cache.stat().st_size > 0:
        return PDFFetchResult(
            url=url, local_path=str(cache), status="cached",
            bytes_written=cache.stat().st_size,
            content_type="application/pdf",
            elapsed_s=time.time() - started,
            fetched_via="cache",
        )
    cache.parent.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/pdf,*/*;q=0.5")
    # Follow up to 5 redirects manually so we can validate each hop is HTTPS
    redirects = 0
    final_url = url
    try:
        while True:
            try:
                resp = urllib.request.urlopen(req, timeout=timeout)
                break
            except urllib.error.HTTPError as exc:
                if exc.code in (301, 302, 303, 307, 308) and redirects < 5:
                    loc = exc.headers.get("Location", "")
                    if loc.startswith("/"):
                        # Relative redirect — build full URL
                        loc = f"{parsed.scheme}://{parsed.netloc}{loc}"
                    if not loc.startswith("https://"):
                        raise urllib.error.HTTPError(
                            url, exc.code, "redirect to non-HTTPS denied",
                            exc.headers, None,
                        )
                    redirects += 1
                    final_url = loc
                    req = urllib.request.Request(loc)
                    req.add_header("User-Agent", USER_AGENT)
                    req.add_header("Accept", "application/pdf,*/*;q=0.5")
                    parsed = urllib.parse.urlparse(loc)
                    continue
                raise
        # Continue with resp (we have to re-enter the `with` block — refactor)
        with resp:
            ctype = resp.headers.get("Content-Type", "").lower()
            # Some servers don't set application/pdf but URL ends in .pdf
            is_pdf = (
                "application/pdf" in ctype
                or "octet-stream" in ctype
                or url.lower().split("?")[0].endswith(".pdf")
            )
            if not is_pdf:
                # Server returned HTML (probably interstitial / bot check).
                # Try Playwright — a real browser usually clears those.
                pw = _fetch_pdf_with_playwright(url, cache, max_bytes, timeout)
                if pw.status == "ok":
                    return pw
                # Playwright also didn't get a PDF → genuinely blocked.
                return PDFFetchResult(
                    url=url, local_path="", status="blocked",
                    bytes_written=0, content_type=ctype,
                    error=(f"stdlib got non-PDF ({ctype!r}); "
                           f"playwright fallback: {pw.error or pw.status}"),
                    elapsed_s=time.time() - started,
                    fetched_via=pw.fetched_via or "stdlib",
                )
            # Stream in chunks, cap at max_bytes
            total = 0
            tmp = cache.with_suffix(".pdf.partial")
            with tmp.open("wb") as fh:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        tmp.unlink(missing_ok=True)
                        return PDFFetchResult(
                            url=url, local_path="", status="rejected",
                            bytes_written=total, content_type=ctype,
                            error=f"PDF exceeds max size ({max_bytes} bytes)",
                            elapsed_s=time.time() - started,
                        )
                    fh.write(chunk)
            tmp.rename(cache)
            return PDFFetchResult(
                url=url, local_path=str(cache), status="ok",
                bytes_written=total, content_type=ctype,
                elapsed_s=time.time() - started,
                fetched_via="stdlib",
            )
    except urllib.error.HTTPError as exc:
        # If the server actively blocked us (403/429/etc.), try Playwright
        # — a real browser fingerprint clears most federal-site bot walls.
        if exc.code in _BLOCK_STATUS_CODES:
            pw = _fetch_pdf_with_playwright(url, cache, max_bytes, timeout)
            if pw.status == "ok":
                return pw
            return PDFFetchResult(
                url=url, local_path="", status="blocked",
                bytes_written=0, content_type="",
                error=(f"stdlib HTTP {exc.code} {exc.reason}; "
                       f"playwright fallback: {pw.error or pw.status}"),
                elapsed_s=time.time() - started,
                fetched_via=pw.fetched_via or "stdlib",
            )
        return PDFFetchResult(
            url=url, local_path="", status="error", bytes_written=0,
            content_type="", error=f"HTTP {exc.code}: {exc.reason}",
            elapsed_s=time.time() - started,
            fetched_via="stdlib",
        )
    except Exception as exc:
        return PDFFetchResult(
            url=url, local_path="", status="error", bytes_written=0,
            content_type="", error=f"{type(exc).__name__}: {exc}",
            elapsed_s=time.time() - started,
            fetched_via="stdlib",
        )
