"""URL → local PDF fetcher (V4 P3).

Fetches a PDF from a remote URL into a local temp file, then the
existing PDFPlumberExtractor handles parsing. Standard library only —
no `requests` or other heavy dependencies.

Safety hard rules (enforced by code, not docs):
  - HTTPS only (no http://, no ftp://, no file://)
  - Max content size (default 50 MB) — refuses larger
  - Connection + read timeout (default 30s)
  - Content-Type must be application/pdf OR octet-stream with .pdf ext
  - User-Agent header set (some servers reject blank UA)

The fetcher is intentionally minimal. V4 P4 may add caching,
authentication, robots.txt handling, etc. — none of that is needed yet.
"""
from __future__ import annotations

import tempfile
import urllib.request
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_MAX_BYTES = 50 * 1024 * 1024  # 50 MB
DEFAULT_TIMEOUT_S = 30.0
DEFAULT_USER_AGENT = (
    "ZLab-Operational-Truth-Framework/1.0 (Industrial Research Engine V4 P3)"
)
_ALLOWED_SCHEMES = {"https"}


class URLFetchError(RuntimeError):
    """Raised when the URL cannot be fetched safely (scheme, size, type)."""


@dataclass
class FetchedPDF:
    url: str
    local_path: Path
    bytes_downloaded: int
    content_type: str


def is_url(maybe_url: str) -> bool:
    """Quick check — does this look like a URL we'd fetch?"""
    if not maybe_url:
        return False
    parsed = urllib.parse.urlparse(maybe_url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def fetch_pdf(
    url: str,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    user_agent: str = DEFAULT_USER_AGENT,
    dest_dir: Optional[Path] = None,
) -> FetchedPDF:
    """Fetch a PDF from a remote URL into a local temp file.

    Returns the FetchedPDF record with the local path. Caller is
    responsible for cleanup if `dest_dir` is None (the temp file will
    be cleaned up by the OS but you can also unlink it manually).

    Raises URLFetchError on any safety violation.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise URLFetchError(
            f"URL scheme {parsed.scheme!r} not allowed. Allowed: {sorted(_ALLOWED_SCHEMES)}"
        )
    if not parsed.netloc:
        raise URLFetchError(f"URL has no host: {url!r}")

    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            content_type = (resp.headers.get("Content-Type") or "").lower()
            content_length = resp.headers.get("Content-Length")

            # Size check from header (advisory — actual download still bounded)
            if content_length is not None:
                try:
                    expected = int(content_length)
                    if expected > max_bytes:
                        raise URLFetchError(
                            f"PDF too large: Content-Length={expected} > max_bytes={max_bytes}"
                        )
                except ValueError:
                    pass

            # Content-Type sanity (allow application/pdf or octet-stream IF
            # url ends in .pdf — some servers are lazy)
            if not _is_pdf_content_type(content_type, url):
                raise URLFetchError(
                    f"Content-Type {content_type!r} is not a PDF "
                    f"(url path: {parsed.path!r})"
                )

            # Stream-read with size guard
            chunk_size = 64 * 1024
            buf = bytearray()
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                buf.extend(chunk)
                if len(buf) > max_bytes:
                    raise URLFetchError(
                        f"PDF exceeded max_bytes={max_bytes} during download"
                    )
    except URLFetchError:
        raise
    except Exception as exc:  # noqa: BLE001 — urllib raises many
        raise URLFetchError(f"failed to fetch {url!r}: {exc}") from exc

    # Persist to a temp file
    dest_dir_path = Path(dest_dir) if dest_dir else Path(tempfile.gettempdir())
    dest_dir_path.mkdir(parents=True, exist_ok=True)
    safe_name = _slug_from_url(url)
    out_path = dest_dir_path / f"{safe_name}.pdf"
    out_path.write_bytes(bytes(buf))

    return FetchedPDF(
        url=url,
        local_path=out_path,
        bytes_downloaded=len(buf),
        content_type=content_type,
    )


def _is_pdf_content_type(content_type: str, url: str) -> bool:
    ct = (content_type or "").lower()
    if "application/pdf" in ct:
        return True
    if "octet-stream" in ct and url.lower().endswith(".pdf"):
        return True
    return False


def _slug_from_url(url: str) -> str:
    """Build a filesystem-safe slug from the URL for the temp filename."""
    parsed = urllib.parse.urlparse(url)
    base = parsed.path.rsplit("/", 1)[-1] or parsed.netloc
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in base)
    if not safe.endswith(".pdf"):
        safe = (safe[:-4] if "." in safe else safe) + ".pdf"
    return safe.lstrip("_")[:120] or "downloaded.pdf"
