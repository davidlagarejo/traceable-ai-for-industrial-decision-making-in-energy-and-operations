from __future__ import annotations

import re
from pathlib import Path

from models.datatypes import ReportSection, ReportUnit, SourceLocation
from models.enums import SourceUnitType


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PLAIN_HEADING_RE = re.compile(r"^(?:\d+(?:\.\d+)*\.?\s+)?[A-Z][A-Za-z0-9 ,:/()&-]{3,90}$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.+)$")


def segment_text(
    text: str,
    source_path: str | Path,
    *,
    markdown: bool = False,
    page_number: int | None = None,
    section_prefix: str = "",
) -> tuple[list[ReportSection], list[ReportUnit]]:
    sections: list[ReportSection] = []
    units: list[ReportUnit] = []
    heading_stack: list[tuple[int, str, str]] = []
    paragraph_lines: list[str] = []
    paragraph_start_line: int | None = None
    current_section = _new_section(
        sections,
        source_path,
        title="Document",
        level=0,
        path=["Document"],
        line_number=1,
        page_number=page_number,
        section_prefix=section_prefix,
    )

    def flush_paragraph(line_number: int) -> None:
        nonlocal paragraph_lines, paragraph_start_line
        if not paragraph_lines:
            return
        paragraph_text = " ".join(line.strip() for line in paragraph_lines).strip()
        if paragraph_text:
            unit = _new_unit(
                units,
                source_path,
                SourceUnitType.PARAGRAPH,
                paragraph_text,
                current_section,
                paragraph_start_line or line_number,
                page_number,
            )
            current_section.units.append(unit)
        paragraph_lines = []
        paragraph_start_line = None

    lines = text.splitlines()
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph(line_number)
            continue
        if _is_table_line(stripped):
            flush_paragraph(line_number)
            unit = _new_unit(
                units,
                source_path,
                SourceUnitType.TABLE,
                stripped,
                current_section,
                line_number,
                page_number,
            )
            current_section.units.append(unit)
            continue

        heading_match = HEADING_RE.match(line) if markdown else None
        if heading_match:
            flush_paragraph(line_number)
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            heading_stack = [item for item in heading_stack if item[0] < level]
            section_id = f"{section_prefix}section-{len(sections) + 1:04d}"
            heading_stack.append((level, title, section_id))
            current_section = _new_section(
                sections,
                source_path,
                title=title,
                level=level,
                path=[item[1] for item in heading_stack],
                line_number=line_number,
                page_number=page_number,
                section_prefix=section_prefix,
                forced_id=section_id,
            )
            continue

        if not markdown and PLAIN_HEADING_RE.match(stripped) and len(stripped.split()) <= 10:
            flush_paragraph(line_number)
            current_section = _new_section(
                sections,
                source_path,
                title=stripped,
                level=1,
                path=[stripped],
                line_number=line_number,
                page_number=page_number,
                section_prefix=section_prefix,
            )
            continue

        bullet_match = BULLET_RE.match(line)
        if bullet_match:
            flush_paragraph(line_number)
            unit = _new_unit(
                units,
                source_path,
                SourceUnitType.BULLET,
                bullet_match.group(1).strip(),
                current_section,
                line_number,
                page_number,
            )
            current_section.units.append(unit)
            continue

        if paragraph_start_line is None:
            paragraph_start_line = line_number
        paragraph_lines.append(stripped)

    flush_paragraph(len(lines) + 1)
    return sections, units


def _new_section(
    sections: list[ReportSection],
    source_path: str | Path,
    *,
    title: str,
    level: int,
    path: list[str],
    line_number: int,
    page_number: int | None,
    section_prefix: str,
    forced_id: str | None = None,
) -> ReportSection:
    section = ReportSection(
        section_id=forced_id or f"{section_prefix}section-{len(sections) + 1:04d}",
        title=title,
        level=level,
        path=path,
        location=SourceLocation(
            file_path=str(source_path),
            page_number=page_number,
            section_path=path,
            start_offset=line_number,
        ),
    )
    sections.append(section)
    return section


def _new_unit(
    units: list[ReportUnit],
    source_path: str | Path,
    unit_type: SourceUnitType,
    text: str,
    section: ReportSection,
    line_number: int,
    page_number: int | None,
) -> ReportUnit:
    unit = ReportUnit(
        unit_id=f"unit-{len(units) + 1:05d}",
        unit_type=unit_type,
        text=text,
        parent_section_id=section.section_id,
        location=SourceLocation(
            file_path=str(source_path),
            page_number=page_number,
            section_path=section.path,
            paragraph_index=len(units) + 1,
            start_offset=line_number,
        ),
    )
    units.append(unit)
    return unit


def _is_table_line(stripped: str) -> bool:
    return "|" in stripped and stripped.count("|") >= 2

