"""V5 P7 — narrator_validator tests.

Verifies the orphan-claim detector that motor_019 uses to enforce
Phase 0's "the LLM doesn't invent" rule at sentence granularity.
"""
from __future__ import annotations

from runtime_orchestrator.narrator_validator import (
    _significant_tokens,
    _split_sentences,
    check_orphan_claims,
    summarize_orphan_findings,
)


# ── Tokenization ────────────────────────────────────────────────────


def test_significant_tokens_drops_stopwords():
    tokens = _significant_tokens("The compressor in the cold chain facility")
    assert "compressor" in tokens
    assert "facility" in tokens
    assert "chain" in tokens
    # Stopwords dropped
    assert "the" not in tokens
    assert "in" not in tokens


def test_significant_tokens_drops_short_tokens():
    tokens = _significant_tokens("X is at A")
    # All <4 chars or stopword
    assert tokens == set()


def test_significant_tokens_handles_spanish_stopwords():
    tokens = _significant_tokens("La refrigeración del edificio está activa")
    assert "refrigeración" in tokens
    assert "edificio" in tokens
    # Spanish stopwords dropped
    assert "del" not in tokens
    assert "está" not in tokens


# ── Sentence splitting ──────────────────────────────────────────────


def test_split_sentences_basic():
    text = "First sentence. Second sentence. Third one."
    sentences = _split_sentences(text)
    assert len(sentences) == 3


def test_split_sentences_handles_question_exclamation():
    text = "Is this clear? Yes! Then proceed."
    sentences = _split_sentences(text)
    assert len(sentences) == 3


def test_split_sentences_empty():
    assert _split_sentences("") == []
    assert _split_sentences("   ") == []


# ── check_orphan_claims ─────────────────────────────────────────────


def test_no_orphan_when_text_fully_grounded():
    source_facts = {
        "asset_family": "cold_chain_facility",
        "evidence": ["refrigeration plant", "compressor inventory"],
    }
    text = "The refrigeration plant is the dominant load. Compressor inventory is unresolved."
    findings = check_orphan_claims(source_facts, text)
    assert findings == []


def test_detects_orphan_sentence():
    source_facts = {
        "asset_family": "cold_chain_facility",
        "evidence": ["refrigeration plant"],
    }
    text = (
        "Refrigeration plant dominates the load profile. "
        "Cryptocurrency mining hardware operates in the basement."
    )
    findings = check_orphan_claims(source_facts, text)
    assert len(findings) == 1
    finding = findings[0]
    assert finding["sentence_index"] == 1
    assert "cryptocurrency" in finding["sentence_excerpt"].lower()
    assert finding["reason"] == "no_token_overlap_with_source_facts"


def test_allow_list_extends_supported_tokens():
    source_facts = {"evidence": ["refrigeration"]}
    text = "The Wilsonart facility has refrigeration equipment."
    # Without allow_list, 'wilsonart' is orphan
    findings = check_orphan_claims(source_facts, text)
    # Sentence may still pass because 'refrigeration' anchors it.
    # But if we wrote a sentence ONLY about Wilsonart it would orphan:
    text2 = "Wilsonart owns this site."
    findings2 = check_orphan_claims(source_facts, text2)
    # Now allow_list rescues
    findings3 = check_orphan_claims(source_facts, text2, allow_list=["Wilsonart"])
    assert len(findings3) < len(findings2) or len(findings2) == 0


def test_short_sentences_skipped():
    source_facts = {"evidence": ["compressor"]}
    text = "Yes. Of course. Compressor reads ok."
    findings = check_orphan_claims(source_facts, text)
    # 'Yes' and 'Of course' have <2 significant tokens → skipped
    # 'Compressor reads ok' matches → not orphan
    assert findings == []


def test_empty_inputs_return_empty():
    assert check_orphan_claims({}, "") == []
    assert check_orphan_claims({}, "Some text without source") != []  # all orphan


def test_min_significant_tokens_threshold():
    source_facts = {"evidence": ["refrigeration"]}
    # Two significant tokens but no overlap
    text = "Unrelated content here."  # 'unrelated', 'content', 'here' (here<4)
    findings = check_orphan_claims(source_facts, text, min_significant_tokens=2)
    assert len(findings) == 1
    # With higher threshold, may be filtered
    findings_high = check_orphan_claims(source_facts, text, min_significant_tokens=5)
    assert findings_high == []


# ── summarize_orphan_findings ───────────────────────────────────────


def test_summarize_empty():
    assert summarize_orphan_findings([]) == ""


def test_summarize_packs_findings_compactly():
    findings = [
        {"sentence_index": 0, "sentence_excerpt": "Foo.", "significant_tokens": []},
        {"sentence_index": 5, "sentence_excerpt": "Bar.", "significant_tokens": []},
    ]
    summary = summarize_orphan_findings(findings)
    assert "orphan_claims=2" in summary
    assert "#0" in summary
    assert "#5" in summary


def test_summarize_truncates_when_many_findings():
    findings = [
        {"sentence_index": i, "sentence_excerpt": f"S{i}.", "significant_tokens": []}
        for i in range(10)
    ]
    summary = summarize_orphan_findings(findings)
    assert "orphan_claims=10" in summary
    assert summary.endswith("…")


# ── motor_019 integration ───────────────────────────────────────────


def test_motor_019_lint_includes_orphan_check():
    """motor_019._lint_text must now flag orphan sentences in its
    violations list."""
    from runtime_orchestrator.adapters.motor_019 import _lint_text

    packet = {
        "source_facts": {
            "evidence": ["refrigeration plant", "compressor inventory"],
        },
        "style_contract": {"max_words": 100},
    }
    bad_text = (
        "Refrigeration plant dominates. "
        "Cryptocurrency mining occupies the basement."
    )
    verdict = _lint_text(packet, bad_text)
    # The cryptocurrency sentence should orphan
    assert "orphan_claim_findings" in verdict
    assert verdict["orphan_claim_findings"], (
        "expected orphan finding for unrelated sentence"
    )
    # And it should appear as a violation summary
    assert any("orphan_claims=" in v for v in verdict["violations"])


def test_motor_019_lint_passes_when_text_grounded():
    from runtime_orchestrator.adapters.motor_019 import _lint_text

    packet = {
        "source_facts": {
            "asset_family": "cold_chain_facility",
            "evidence": ["refrigeration duty", "compressor staging"],
            "tension": "production schedule conflicts with refrigeration setpoint",
        },
        "style_contract": {"max_words": 100},
    }
    good_text = (
        "Refrigeration duty is the dominant load in this cold chain facility. "
        "Compressor staging must be characterized before equipment-first logic."
    )
    verdict = _lint_text(packet, good_text)
    # May have other violations but not orphan
    assert not any("orphan_claims" in v for v in verdict["violations"]), (
        f"unexpected orphan violations: {verdict['violations']}"
    )
