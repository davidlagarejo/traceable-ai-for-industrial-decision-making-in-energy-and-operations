"""Real PDF extractor using pdfplumber (V4 P2).

Implements the V4 P1 PDFExtractor Protocol with actual text extraction.
The `pdfplumber` library is already in the project's environment
(verified 2026-05-12, v0.11.8). If the lib is missing at runtime, the
extractor raises a clear ImportError instead of a cryptic failure.

Supported:
  - Local file paths (absolute or relative)
  - Page-range filter (e.g., "1-5", "3", "10-20")
  - Per-page text returned in `page_texts`
  - PDF metadata surfaced in `metadata`

Out of scope:
  - URL fetching (V4 P3 plugs in motor_028 discovery)
  - Image / chart OCR (would need pytesseract)
  - Table extraction (pdfplumber supports it but we don't expose it yet)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .pdf_extraction_interface import PDFExtractionResult


def _parse_page_range(spec: str, total_pages: int) -> list[int]:
    """Parse '1-5,7,10-12' into a sorted unique list of 0-indexed page nums."""
    if not spec:
        return list(range(total_pages))
    pages: set[int] = set()
    for chunk in str(spec).split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, _, b = chunk.partition("-")
            try:
                start = max(1, int(a.strip()))
                end = min(total_pages, int(b.strip()))
            except ValueError as exc:
                raise ValueError(f"invalid page range chunk: {chunk!r}") from exc
            pages.update(range(start - 1, end))
        else:
            try:
                p = int(chunk)
            except ValueError as exc:
                raise ValueError(f"invalid page number: {chunk!r}") from exc
            if 1 <= p <= total_pages:
                pages.add(p - 1)
    return sorted(pages)


class PDFPlumberExtractor:
    """V4 P2 real PDF extractor.

    Configurable per-call:
      pages: str — page range spec like "1-5"; defaults to ALL pages
      max_chars: int — truncate the concatenated text (LLM context budget)
    """

    def __init__(self, *, max_chars: int = 60_000) -> None:
        self.max_chars = max_chars

    def extract(self, source_url: str, **opts: Any) -> PDFExtractionResult:
        try:
            import pdfplumber  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "pdfplumber is required for V4 P2 PDF extraction. "
                "Install via: pip install pdfplumber"
            ) from exc

        # source_url here is a LOCAL FILE PATH (V4 P2 doesn't fetch URLs).
        # V4 P3 will plug motor_028 for URL handling.
        path = Path(source_url)
        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found at: {source_url}. "
                "V4 P2 expects a local file path; remote URL fetching "
                "lands in V4 P3 via motor_028."
            )

        pages_spec = str(opts.get("pages", "") or "")
        max_chars = int(opts.get("max_chars", self.max_chars))

        page_texts: list[str] = []
        metadata: dict[str, Any] = {}
        with pdfplumber.open(str(path)) as pdf:
            total_pages = len(pdf.pages)
            metadata = dict(pdf.metadata or {})
            wanted_pages = _parse_page_range(pages_spec, total_pages)
            for idx in wanted_pages:
                try:
                    page_text = pdf.pages[idx].extract_text() or ""
                except Exception as exc:  # noqa: BLE001 — pdfplumber raises various
                    page_text = f"[pdfplumber extraction error on page {idx + 1}: {exc}]"
                page_texts.append(page_text)

        combined = "\n\n".join(page_texts)
        truncated = combined[:max_chars]
        return PDFExtractionResult(
            source_url=source_url,
            text=truncated,
            page_count=len(page_texts),
            metadata=metadata,
            page_texts=page_texts,
            extraction_method="pdfplumber",
        )


def make_pdfplumber_extractor(**opts: Any) -> PDFPlumberExtractor:
    return PDFPlumberExtractor(**opts)
