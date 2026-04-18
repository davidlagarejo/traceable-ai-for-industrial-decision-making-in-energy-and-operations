from __future__ import annotations

from pathlib import Path

from contracts.loader import hash_file
from models.datatypes import NormalizedReport
from models.enums import DocumentRole
from parsers.claim_segmenter import extract_claims
from parsers.markdown_parser import parse_markdown_file
from parsers.pdf_parser import parse_pdf_file
from parsers.text_parser import parse_text_file


SUPPORTED_REPORT_EXTENSIONS = {".md", ".markdown", ".txt", ".pdf"}


def normalize_report(
    report_path: str | Path,
    *,
    role: DocumentRole = DocumentRole.OBJECT_UNDER_REVIEW,
    phase_ids: list[str] | None = None,
) -> NormalizedReport:
    path = Path(report_path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() not in SUPPORTED_REPORT_EXTENSIONS:
        raise ValueError(f"unsupported report extension: {path.suffix}")

    if path.suffix.lower() in {".md", ".markdown"}:
        sections, units, tables, citations = parse_markdown_file(path)
    elif path.suffix.lower() == ".pdf":
        sections, units, tables, citations = parse_pdf_file(path)
    else:
        sections, units, tables, citations = parse_text_file(path)

    claims = extract_claims(units, citations, tables, phase_ids=phase_ids)
    file_hash = hash_file(path)
    return NormalizedReport(
        report_id=f"{path.stem}-{file_hash[:10]}",
        source_path=str(path),
        role=role,
        file_hash=file_hash,
        sections=sections,
        units=units,
        tables=tables,
        citations=citations,
        claims=claims,
        metadata={
            "section_count": len(sections),
            "unit_count": len(units),
            "table_count": len(tables),
            "citation_count": len(citations),
            "claim_count": len(claims),
        },
    )

