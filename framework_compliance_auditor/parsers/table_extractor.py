from __future__ import annotations

from pathlib import Path

from models.datatypes import SourceLocation, Table


def extract_markdown_tables(text: str, source_path: str | Path) -> list[Table]:
    tables: list[Table] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if _looks_like_table_start(lines, index):
            start = index
            block: list[str] = []
            while index < len(lines) and "|" in lines[index].strip():
                block.append(lines[index])
                index += 1
            headers, rows = _parse_markdown_table(block)
            tables.append(
                Table(
                    table_id=f"table-{len(tables) + 1:04d}",
                    raw_text="\n".join(block),
                    headers=headers,
                    rows=rows,
                    location=SourceLocation(file_path=str(source_path), start_offset=start + 1),
                )
            )
            continue
        index += 1
    return tables


def text_mentions_table(text: str) -> bool:
    lowered = text.lower()
    return "table" in lowered or "| " in text or "\t" in text


def _looks_like_table_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    first = lines[index].strip()
    second = lines[index + 1].strip()
    return "|" in first and "|" in second and set(second.replace("|", "").strip()) <= {"-", ":", " "}


def _parse_markdown_table(block: list[str]) -> tuple[list[str], list[list[str]]]:
    if not block:
        return [], []
    headers = _split_row(block[0])
    rows = [_split_row(line) for line in block[2:] if "|" in line]
    return headers, rows


def _split_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]

