from __future__ import annotations

from pathlib import Path

from models.datatypes import Citation, ReportSection, ReportUnit, Table
from parsers.citation_extractor import extract_citations_from_text
from parsers.section_segmenter import segment_text
from parsers.table_extractor import extract_markdown_tables


def parse_markdown_file(path: str | Path) -> tuple[list[ReportSection], list[ReportUnit], list[Table], list[Citation]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    sections, units = segment_text(text, source, markdown=True)
    tables = extract_markdown_tables(text, source)
    citations = extract_citations_from_text(text, source)
    return sections, units, tables, citations

