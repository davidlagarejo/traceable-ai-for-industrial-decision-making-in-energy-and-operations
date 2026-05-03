from __future__ import annotations

from runtime_orchestrator.source_acquisition.provenance import (
    build_provenance_manifest,
)


def test_provenance_manifest_hashes_and_selector_lineage_are_stable() -> None:
    manifest_one = build_provenance_manifest(
        acquisition_mode="playwright_public_page",
        requested_url="https://www.dallascad.org/SearchOwner.aspx",
        final_url="https://www.dallascad.org/SearchOwner.aspx",
        html="<html><body><main>Dallas CAD Search</main></body></html>",
        visible_text="Dallas CAD Search",
        selector_lineage=[{"selector": "main", "match_count": 1}],
        attempt_outcome="success",
    )
    manifest_two = build_provenance_manifest(
        acquisition_mode="playwright_public_page",
        requested_url="https://www.dallascad.org/SearchOwner.aspx",
        final_url="https://www.dallascad.org/SearchOwner.aspx",
        html="<html><body><main>Dallas CAD Search</main></body></html>",
        visible_text="Dallas CAD Search",
        selector_lineage=[{"selector": "main", "match_count": 1}],
        attempt_outcome="success",
    )

    assert manifest_one["dom_sha256"] == manifest_two["dom_sha256"]
    assert manifest_one["visible_text_sha256"] == manifest_two["visible_text_sha256"]
    assert manifest_one["selector_lineage"] == [{"selector": "main", "match_count": 1}]
    assert manifest_one["attempt_outcome"] == "success"
