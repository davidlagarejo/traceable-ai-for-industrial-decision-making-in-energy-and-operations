from __future__ import annotations

import re
import subprocess
from pathlib import Path

from models.datatypes import Citation, ReportSection, ReportUnit, Table
from parsers.citation_extractor import extract_citations_from_text
from parsers.section_segmenter import segment_text
from parsers.table_extractor import extract_markdown_tables


def parse_pdf_file(path: str | Path) -> tuple[list[ReportSection], list[ReportUnit], list[Table], list[Citation]]:
    source = Path(path)
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on optional package
        return _parse_pdf_without_pypdf(source, exc)

    reader = PdfReader(str(source))
    all_sections: list[ReportSection] = []
    all_units: list[ReportUnit] = []
    text_parts: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
        sections, units = segment_text(
            page_text,
            source,
            markdown=False,
            page_number=page_index,
            section_prefix=f"p{page_index}-",
        )
        all_sections.extend(sections)
        all_units.extend(units)

    combined_text = "\n\n".join(text_parts)
    tables = extract_markdown_tables(combined_text, source)
    citations = extract_citations_from_text(combined_text, source)
    return all_sections, all_units, tables, citations


def _parse_pdf_without_pypdf(
    source: Path,
    original_error: Exception,
) -> tuple[list[ReportSection], list[ReportUnit], list[Table], list[Citation]]:
    extracted = _try_pymupdf(source)
    if extracted:
        sections, units = segment_text(extracted, source, markdown=False)
        tables = extract_markdown_tables(extracted, source)
        citations = extract_citations_from_text(extracted, source)
        return sections, units, tables, citations

    extracted = _try_pdftotext(source)
    if extracted:
        sections, units = segment_text(extracted, source, markdown=False)
        tables = extract_markdown_tables(extracted, source)
        citations = extract_citations_from_text(extracted, source)
        return sections, units, tables, citations

    sibling_tex = source.with_name("main.tex")
    if sibling_tex.exists():
        latex_text = sibling_tex.read_text(encoding="utf-8")
        plain_text = strip_latex_markup(latex_text)
        sections, units = segment_text(plain_text, source, markdown=True)
        tables = extract_markdown_tables(plain_text, source)
        citations = extract_citations_from_text(plain_text, source)
        return sections, units, tables, citations

    raise RuntimeError(
        "PDF parsing requires optional dependency pypdf, a pdftotext binary, "
        "or a sibling main.tex fallback next to the PDF"
    ) from original_error


def _try_pymupdf(source: Path) -> str | None:
    try:
        import fitz  # type: ignore
    except Exception:
        return None
    try:
        parts: list[str] = []
        with fitz.open(str(source)) as document:
            for page_index, page in enumerate(document, start=1):
                text = page.get_text("text") or ""
                if text.strip():
                    parts.append(f"\n\nPage {page_index}\n{text}")
        extracted = "\n\n".join(parts)
    except Exception:
        return None
    return extracted if extracted.strip() else None


def _try_pdftotext(source: Path) -> str | None:
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(source), "-"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout


def strip_latex_markup(text: str) -> str:
    """Minimal LaTeX-to-text fallback for auditable source extraction."""

    cleaned = text
    cleaned = re.sub(r"%.*", "", cleaned)
    cleaned = re.sub(r"\\documentclass(?:\[[^\]]*\])?\{[^}]+\}", "", cleaned)
    cleaned = re.sub(r"\\usepackage(?:\[[^\]]*\])?\{[^}]+\}", "", cleaned)
    cleaned = re.sub(r"\\geometry\{[^}]+\}", "", cleaned)
    cleaned = re.sub(r"\\title\{([^}]*)\}", r"# \1", cleaned)
    cleaned = re.sub(r"\\author\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\date\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\section\{([^}]*)\}", r"# \1", cleaned)
    cleaned = re.sub(r"\\subsection\{([^}]*)\}", r"## \1", cleaned)
    cleaned = re.sub(r"\\subsubsection\{([^}]*)\}", r"### \1", cleaned)
    cleaned = re.sub(r"\\paragraph\{([^}]*)\}", r"#### \1", cleaned)
    cleaned = cleaned.replace(r"\textbf", "").replace(r"\emph", "").replace(r"\item", "- ")
    cleaned = re.sub(r"\\(?:maketitle|tableofcontents|newpage)", "", cleaned)
    cleaned = re.sub(r"\\begin\{[^}]+\}", "\n", cleaned)
    cleaned = re.sub(r"\\end\{[^}]+\}", "\n", cleaned)
    cleaned = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", cleaned)
    cleaned = re.sub(r"[{}]", "", cleaned)
    cleaned = cleaned.replace(r"\&", "&").replace(r"\%", "%").replace(r"\_", "_")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned
