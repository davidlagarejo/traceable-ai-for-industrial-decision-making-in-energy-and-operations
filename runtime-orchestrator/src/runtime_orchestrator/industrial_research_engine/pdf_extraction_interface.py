"""PDF extraction interface (V4 P1).

Protocol for any PDF-to-text extractor the framework wires in. Real
implementations land when the user installs pdfminer / pdfplumber and
the first PDF arrives. Until then, all calls raise NotImplementedError.

Design rationale:
  - Decouple PDF format handling from the rest of the pipeline.
  - Keep the contract minimal so swapping pdfminer ↔ pdfplumber ↔
    PyMuPDF later is trivial.
  - The output is RAW TEXT (or structured text blocks) — NOT
    interpreted knowledge. Interpretation belongs to the LLM extractor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class PDFExtractionResult:
    """Structured output of a PDF extraction pass."""
    source_url: str
    text: str
    page_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    page_texts: list[str] = field(default_factory=list)
    extraction_method: str = ""  # "pdfminer" | "pdfplumber" | "manual" | etc.


class PDFExtractor(Protocol):
    """Anything that converts a PDF (path or URL) into structured text."""

    def extract(self, source_url: str, **opts: Any) -> PDFExtractionResult: ...


class NotImplementedPDFExtractor:
    """Default V4 P1 extractor. Raises when called. The first concrete
    implementation lands when the user provides a real PDF + chooses a
    parsing library (pdfminer.six recommended for V4 P2)."""

    def extract(self, source_url: str, **opts: Any) -> PDFExtractionResult:
        raise NotImplementedError(
            "PDF extraction is not implemented in V4 Phase 1. The contract "
            "is locked; a real implementation (pdfminer / pdfplumber) lands "
            "when the first PDF source is registered with the framework. "
            f"Requested URL: {source_url!r}."
        )


def default_pdf_extractor() -> PDFExtractor:
    """Factory — returns the NotImplemented stub today; later returns
    a real extractor configured from settings."""
    return NotImplementedPDFExtractor()
