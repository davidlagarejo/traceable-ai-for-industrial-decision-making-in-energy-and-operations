#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_runtime_root() / "src"))

from runtime_orchestrator.zlab_skill.licensed_playwright_fetch import (  # noqa: E402
    _load_playwright_sync_api,
)
from runtime_orchestrator.zlab_skill.provider_sessions import build_provider_session_plan  # noqa: E402


def _open_session(
    *,
    url: str,
    provider_session_plan: dict,
    timeout_ms: int,
    headless: bool,
) -> int:
    profile_plan = dict(provider_session_plan.get("profile_plan", {}) or {})
    profile_path = Path(str(profile_plan.get("profile_path", "")).strip()).expanduser()
    profile_path.mkdir(parents=True, exist_ok=True)
    sync_playwright, _ = _load_playwright_sync_api()
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
        )
        try:
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 6_000))
            except Exception:
                pass
            print(
                json.dumps(
                    {
                        "ok": True,
                        "provider_key": provider_session_plan.get("provider_key", ""),
                        "profile_path": str(profile_path),
                        "final_url": str(page.url or url),
                        "headless": headless,
                    },
                    indent=2,
                )
            )
            if not headless:
                input("Provider session open. Complete login if needed, then press Enter to close...")
        finally:
            context.close()
    return 0


def _validate_auth(
    *,
    url: str,
    provider_session_plan: dict,
    timeout_ms: int,
    headless: bool,
) -> int:
    from runtime_orchestrator.zlab_skill.licensed_playwright_fetch import (  # noqa: E402
        fetch_licensed_document_with_persistent_session,
    )

    result = fetch_licensed_document_with_persistent_session(
        url=url,
        provider_session_plan=provider_session_plan,
        timeout_ms=timeout_ms,
        headless=headless,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "success" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a persistent Playwright session for a licensed provider.")
    parser.add_argument("--provider-key", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--validate-url", default="")
    parser.add_argument("--session-label", default="licensed")
    parser.add_argument("--timeout-ms", type=int, default=12_000)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--headful", action="store_true")
    parser.add_argument("--validate-auth", action="store_true")
    args = parser.parse_args()

    headless = bool(args.headless)
    if args.headful:
        headless = False

    session_plan = build_provider_session_plan(
        url=args.url,
        retrieval_purpose="provider_session_bootstrap",
        session_label=args.session_label,
        provider_key_override=args.provider_key,
    )
    if args.provider_key.strip().lower() != str(session_plan.get("provider_key", "")).strip().lower():
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "provider_key_mismatch_for_url",
                    "requested_provider_key": args.provider_key,
                    "resolved_provider_key": session_plan.get("provider_key", ""),
                    "url": args.url,
                },
                indent=2,
            )
        )
        return 2
    if args.validate_auth:
        return _validate_auth(
            url=str(args.validate_url or args.url),
            provider_session_plan=session_plan,
            timeout_ms=args.timeout_ms,
            headless=headless,
        )
    return _open_session(
        url=args.url,
        provider_session_plan=session_plan,
        timeout_ms=args.timeout_ms,
        headless=headless,
    )


if __name__ == "__main__":
    raise SystemExit(main())
