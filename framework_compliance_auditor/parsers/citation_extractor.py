from __future__ import annotations

import re
from pathlib import Path

from models.datatypes import Citation, ReportUnit, SourceLocation


URL_RE = re.compile(r"https?://[^\s)\]]+")
BRACKET_RE = re.compile(r"\[(?:\d+|[A-Za-z][A-Za-z0-9_-]{1,30})\]")
AUTHOR_YEAR_RE = re.compile(r"\(([A-Z][A-Za-z]+(?: et al\.)?,\s*(?:19|20)\d{2})\)")


def extract_citations_from_text(text: str, source_path: str | Path) -> list[Citation]:
    citations: list[Citation] = []
    for index, match in enumerate(_iter_citation_matches(text), start=1):
        citations.append(
            Citation(
                citation_id=f"citation-{index:04d}",
                raw_text=match.group(0),
                normalized=match.group(0).strip("[]()"),
                location=SourceLocation(
                    file_path=str(source_path),
                    start_offset=match.start(),
                    end_offset=match.end(),
                ),
            )
        )
    return citations


def citation_ids_for_text(text: str, citations: list[Citation]) -> list[str]:
    found: list[str] = []
    for citation in citations:
        if citation.raw_text in text:
            found.append(citation.citation_id)
    return found


def unit_has_evidence_reference(unit: ReportUnit, citations: list[Citation]) -> bool:
    if citation_ids_for_text(unit.text, citations):
        return True
    lowered = unit.text.lower()
    return any(
        marker in lowered
        for marker in (
            "source:",
            "sources:",
            "according to",
            "as shown in table",
            "as shown below",
            "public filing",
            "public data",
            "appendix",
            "evidence",
        )
    )


def _iter_citation_matches(text: str):
    matches = list(URL_RE.finditer(text))
    matches.extend(BRACKET_RE.finditer(text))
    matches.extend(AUTHOR_YEAR_RE.finditer(text))
    return sorted(matches, key=lambda item: item.start())

