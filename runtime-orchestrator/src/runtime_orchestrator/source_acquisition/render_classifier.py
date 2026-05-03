from __future__ import annotations

import re
from typing import Any

_SHELL_MARKERS = (
    "__next_data__",
    "enable javascript",
    "javascript required",
    "loading...",
    "app-root",
    "data-reactroot",
    "jimu-primary-loading-app",
    "systemjs-importmap",
)


def _visible_text(html: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return re.sub(r"<[^>]+>", " ", html or "").strip()
    soup = BeautifulSoup(html or "", "html.parser")
    return soup.get_text(separator=" ", strip=True)


def classify_static_render_candidate(
    *,
    html: str,
    selector_plan: list[str] | None = None,
    status_code: int | None = None,
) -> dict[str, Any]:
    html = str(html or "")
    lowered = html.lower()
    visible_text = _visible_text(html)
    selector_plan = list(selector_plan or [])
    selector_hits: list[str] = []

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        soup = None
    else:
        soup = BeautifulSoup(html, "html.parser")

    if soup is not None:
        for selector in selector_plan:
            try:
                if soup.select_one(selector):
                    selector_hits.append(selector)
            except Exception:
                continue

    shell_markers = [marker for marker in _SHELL_MARKERS if marker in lowered]
    visible_text_length = len(visible_text)
    html_length = len(html)

    if not html.strip():
        render_mode = "empty"
        why = ["empty_html"]
    elif status_code and status_code >= 400:
        render_mode = "shell_or_sparse"
        why = [f"http_{status_code}"]
    elif shell_markers and visible_text_length < 240:
        render_mode = "shell_or_sparse"
        why = ["shell_marker_detected", "visible_text_sparse"]
    elif visible_text_length < 120 and not selector_hits:
        render_mode = "shell_or_sparse"
        why = ["visible_text_sparse", "no_selector_hits"]
    else:
        render_mode = "static_usable"
        why = ["selector_hits_present" if selector_hits else "visible_text_sufficient"]

    return {
        "render_mode": render_mode,
        "why": why,
        "selector_hits": selector_hits,
        "shell_markers": shell_markers,
        "html_length": html_length,
        "visible_text_length": visible_text_length,
        "visible_text": visible_text,
    }
