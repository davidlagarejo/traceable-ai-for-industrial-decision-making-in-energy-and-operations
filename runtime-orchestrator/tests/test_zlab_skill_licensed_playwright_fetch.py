from __future__ import annotations

from pathlib import Path

import runtime_orchestrator.zlab_skill.licensed_playwright_fetch as licensed_fetch_module
from runtime_orchestrator.zlab_skill import (
    build_provider_session_plan,
    execute_licensed_document_acquisition,
    fetch_licensed_document_with_persistent_session,
)


class _FakeLocator:
    def __init__(self, text: str, count: int = 1) -> None:
        self._text = text
        self._count = count
        self.first = self

    def count(self) -> int:
        return self._count

    def inner_text(self, timeout: int | None = None) -> str:
        _ = timeout
        return self._text


class _FakePage:
    def __init__(self, *, final_url: str, html: str, selector_text: dict[str, str]) -> None:
        self.url = final_url
        self._html = html
        self._selector_text = selector_text

    def goto(self, url: str, wait_until: str = "", timeout: int = 0) -> None:
        _ = (url, wait_until, timeout)

    def wait_for_load_state(self, state: str, timeout: int = 0) -> None:
        _ = (state, timeout)

    def content(self) -> str:
        return self._html

    def locator(self, selector: str) -> _FakeLocator:
        return _FakeLocator(self._selector_text.get(selector, ""))


class _FakeContext:
    def __init__(self, page: _FakePage) -> None:
        self._page = page
        self.closed = False

    def new_page(self) -> _FakePage:
        return self._page

    def close(self) -> None:
        self.closed = True


class _FakeChromium:
    def __init__(self, page: _FakePage) -> None:
        self._page = page

    def launch_persistent_context(self, user_data_dir: str, headless: bool = True) -> _FakeContext:
        _ = (user_data_dir, headless)
        return _FakeContext(self._page)


class _FakePlaywrightRuntime:
    def __init__(self, page: _FakePage) -> None:
        self.chromium = _FakeChromium(page)


class _FakePlaywrightManager:
    def __init__(self, page: _FakePage) -> None:
        self._runtime = _FakePlaywrightRuntime(page)

    def __enter__(self) -> _FakePlaywrightRuntime:
        return self._runtime

    def __exit__(self, exc_type, exc, tb) -> bool:
        _ = (exc_type, exc, tb)
        return False


def test_fetch_licensed_document_with_persistent_session_succeeds_when_profile_and_domain_are_valid(
    monkeypatch,
    tmp_path: Path,
) -> None:
    fake_page = _FakePage(
        final_url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        html="<html><body><main>Demand orchestration article</main></body></html>",
        selector_text={"main": "Demand orchestration article", "body": "Demand orchestration article"},
    )
    monkeypatch.setattr(
        licensed_fetch_module,
        "_load_playwright_sync_api",
        lambda: (lambda: _FakePlaywrightManager(fake_page), RuntimeError),
    )
    session_plan = build_provider_session_plan(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        retrieval_purpose="pattern_seed_discovery",
    )
    session_plan["profile_plan"]["profile_path"] = str(tmp_path / "elsevier_profile")

    result = fetch_licensed_document_with_persistent_session(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        provider_session_plan=session_plan,
        headless=True,
    )

    assert result["status"] == "success"
    assert result["provider_key"] == "elsevier"
    assert result["visible_text"] == "Demand orchestration article"
    assert result["selector_lineage"][0]["selector"] == "article"


def test_fetch_licensed_document_with_persistent_session_detects_login_gate(monkeypatch, tmp_path: Path) -> None:
    fake_page = _FakePage(
        final_url="https://id.elsevier.com/as/authorization.oauth2?signin=true",
        html="<html><body><main>Sign in through your institution</main></body></html>",
        selector_text={"main": "Sign in through your institution", "body": "Sign in through your institution"},
    )
    monkeypatch.setattr(
        licensed_fetch_module,
        "_load_playwright_sync_api",
        lambda: (lambda: _FakePlaywrightManager(fake_page), RuntimeError),
    )
    session_plan = build_provider_session_plan(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        retrieval_purpose="pattern_seed_discovery",
    )
    session_plan["profile_plan"]["profile_path"] = str(tmp_path / "elsevier_profile")

    result = fetch_licensed_document_with_persistent_session(
        url="https://www.sciencedirect.com/science/article/pii/S0360544218311234",
        provider_session_plan=session_plan,
    )

    assert result["status"] == "login_required"
    assert result["error"] == "provider_session_not_authenticated"


def test_execute_licensed_document_acquisition_returns_manifest_for_playwright_session(monkeypatch) -> None:
    monkeypatch.setattr(
        licensed_fetch_module,
        "_load_playwright_sync_api",
        lambda: (
            lambda: _FakePlaywrightManager(
                _FakePage(
                    final_url="https://ieeexplore.ieee.org/document/1234567",
                    html="<html><body><article>Power quality article</article></body></html>",
                    selector_text={"article": "Power quality article", "body": "Power quality article"},
                )
            ),
            RuntimeError,
        ),
    )

    result = execute_licensed_document_acquisition(
        url="https://ieeexplore.ieee.org/document/1234567",
        retrieval_purpose="combination_seed_review",
        technical_scraping_allowed=True,
        route_allowed=True,
        metadata={"title": "Power Quality Article", "journal": "IEEE Journal", "published_year": "2026"},
        env={"ZLAB_ENABLE_LICENSED_RESEARCH_ACQUISITION": "1"},
    )

    assert result["acquisition_plan"]["allowed"] is True
    assert result["acquisition_result"]["status"] == "success"
    assert result["research_document_manifest"]["provider_key"] == "ieee"
    assert result["research_document_manifest"]["provenance_manifest"]["attempt_outcome"] == "success"
