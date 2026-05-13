"""V5 — auto-derive autodraft rules from pattern_spec metadata.

`zlab_skill.local_pdf_autodraft._AUTO_PATTERN_RULES` currently has 20
hand-authored rules. The remaining 10 registry patterns (S4 cold-chain
specs plus a few manufacturing patterns) lacked rules. Rather than
adding 10 more hand-written rules (which would be scaffolding), this
module DERIVES the rules deterministically from each pattern_spec's
own `trigger_conditions` + `applicable_contexts` fields.

Algorithm (deterministic, no LLM, no scaffolding):

  Per trigger_condition string →
    1. Normalize: lowercase, strip
    2. Expand parenthesized alternatives: "(time/demand/ambient)" →
       ["time", "demand", "ambient"]
    3. Split on coordinating conjunctions: "or", "vs.", "/"
    4. Strip stopword tails: "X unknown" / "X unresolved" / "X present" →
       keep "X"
    5. Filter trivially short tokens
    6. Result is one required_group (any term in the list matches)

  applicable_contexts → flat optional_terms list (boost score).

The output is shape-compatible with `_AUTO_PATTERN_RULES` so it can be
merged into the autodraft layer transparently.

This is machinery, not content. The pattern_spec's natural-language
trigger_conditions ARE the spec's authoritative truth (already in
AI_SCAFFOLDING_REGISTRY S4). Deriving keyword rules from them is
deterministic transcription, not new content authoring.
"""
from __future__ import annotations

import re
from typing import Any, Mapping


# Words that carry no information for matching (epistemic / stative).
# Stripped both as standalone tokens and as suffix tails.
_STOPWORDS: frozenset[str] = frozenset({
    "a", "an", "the", "is", "in", "on", "for", "with", "of", "to", "at",
    "by", "as", "be", "or", "and", "vs",
    "present", "unknown", "unresolved", "undocumented", "unclear",
    "plausible", "visible", "confirmed", "characterized", "documented",
    "could", "dominant", "but", "yet", "still", "before", "after",
    "until", "while", "than", "more", "less", "some", "any", "all",
    "this", "that", "these", "those", "its", "their", "his", "her",
    "history", "exposure", "scope", "evidence",
})


# Words that bridge phrases (split on these to extract per-sub-phrase
# noun chunks).
_SPLIT_PATTERN = re.compile(
    r"\s+or\s+|\s+vs\.?\s+|/(?![\w])",  # ' or ', ' vs ', '/'
    re.IGNORECASE,
)


# Pattern to find parenthesized alternatives e.g. "(time/demand/ambient)"
_PAREN_RE = re.compile(r"\(([^)]+)\)")


def _normalize_phrase(phrase: str) -> str:
    """Lowercase, strip surrounding whitespace, normalize internal spaces."""
    s = (phrase or "").lower().strip()
    return re.sub(r"\s+", " ", s)


def _strip_stopword_tail(phrase: str) -> str:
    """Drop trailing stopwords. 'X unresolved' → 'X'."""
    words = phrase.split()
    while words and words[-1] in _STOPWORDS:
        words.pop()
    return " ".join(words)


def _split_paren_alternatives(phrase: str) -> list[str]:
    """Expand 'foo (a/b/c) bar' into ['foo a bar', 'foo b bar', 'foo c bar'].

    If no parens, return [phrase] unchanged. If parens with single token,
    return [phrase without parens].
    """
    match = _PAREN_RE.search(phrase)
    if not match:
        return [phrase]
    inside = match.group(1)
    options = [opt.strip() for opt in inside.split("/") if opt.strip()]
    if not options:
        return [_PAREN_RE.sub("", phrase, count=1).strip()]
    head = phrase[: match.start()].strip()
    tail = phrase[match.end():].strip()
    # Emit just the alternative tokens themselves (most useful for keyword
    # matching). Plus the variant without the paren entirely.
    out: list[str] = []
    for opt in options:
        composed = (head + " " + opt + " " + tail).strip()
        composed = re.sub(r"\s+", " ", composed)
        if composed:
            out.append(composed)
        # Also include the bare alternative as a standalone match target
        # (e.g. "HFC", "HFO", "NH3" each as their own match candidate)
        if opt not in _STOPWORDS and len(opt) >= 2:
            out.append(opt)
    if head and not out:
        out.append(head + (" " + tail if tail else ""))
    return out or [phrase]


def _trigger_to_required_group(trigger_condition: str) -> list[str]:
    """Convert one trigger_condition string into ONE required_group list.

    Each member is an alternative phrase; matching any one satisfies the
    group.

    Algorithm produces THREE tiers of alternatives:
      1. Full phrase (high specificity, low recall)
      2. Head noun bigram (medium specificity / recall)
      3. Each individual non-stopword (low specificity, high recall)

    This matches the granularity of hand-authored rules in
    _AUTO_PATTERN_RULES (which typically use single nouns like
    'compressor', 'boiler', 'defrost').
    """
    text = _normalize_phrase(trigger_condition)
    if not text:
        return []

    expanded = _split_paren_alternatives(text)

    alternatives: list[str] = []

    def _add(candidate: str) -> None:
        c = candidate.strip()
        if not c or len(c) < 3:
            return
        if c in _STOPWORDS:
            return
        if c not in alternatives:
            alternatives.append(c)

    for chunk in expanded:
        # Split each expanded chunk on 'or'/'/' etc.
        sub_chunks = _SPLIT_PATTERN.split(chunk)
        for sub in sub_chunks:
            sub = _normalize_phrase(sub)
            sub = _strip_stopword_tail(sub)
            if not sub:
                continue
            words = [w for w in sub.split() if w not in _STOPWORDS]
            if not words:
                continue
            full_phrase = " ".join(words)
            # Tier 1: full phrase
            _add(full_phrase)
            # Tier 2: trailing bigram (head noun + modifier)
            if len(words) >= 2:
                _add(" ".join(words[-2:]))
            # Tier 3: each individual non-stopword as standalone
            for word in words:
                _add(word)
    return alternatives


_MAX_REQUIRED_GROUPS = 2  # AND-strictness ceiling — hand-authored rules use 1-3


def derive_autodraft_rule_from_pattern_spec(
    pattern_spec: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Derive a `_AUTO_PATTERN_RULES`-shaped rule from a pattern_spec.

    Strategy (matches hand-authored vocabulary granularity):
      - First 2 trigger_conditions → required_groups (asset + mechanism).
        Hand-authored rules in _AUTO_PATTERN_RULES use 1-3 required_groups
        with short keyword alternatives. Deriving 4+ groups from a verbose
        spec creates a too-strict AND that real PDFs rarely satisfy.
      - Remaining triggers + applicable_contexts → optional_terms (boost
        score without gating the match).

    Returns None if no usable trigger_conditions can produce at least one
    non-empty required_group.

    Output shape (matches existing _AUTO_PATTERN_RULES entries):
      {
        "required_groups": [[alt1, alt2, ...], [alt1, alt2, ...], ...],
        "optional_terms": [term1, term2, ...],
      }
    """
    triggers = list(pattern_spec.get("trigger_conditions", []) or [])
    contexts = list(pattern_spec.get("applicable_contexts", []) or [])

    # Derive groups from each trigger
    all_groups: list[list[str]] = []
    for trig in triggers:
        group = _trigger_to_required_group(trig)
        if group:
            all_groups.append(group)

    # Fallback: if no triggers but we have applicable_contexts, use them
    # as required_groups too (better than nothing).
    if not all_groups:
        for ctx in contexts:
            group = _trigger_to_required_group(ctx)
            if group:
                all_groups.append(group)

    if not all_groups:
        return None

    # Cap required_groups; surplus moves to optional_terms.
    required_groups = all_groups[:_MAX_REQUIRED_GROUPS]
    surplus_required = all_groups[_MAX_REQUIRED_GROUPS:]

    required_flat = {term for group in required_groups for term in group}
    optional_terms: list[str] = []
    for term in (t for group in surplus_required for t in group):
        if term not in required_flat and term not in optional_terms:
            optional_terms.append(term)
    for ctx in contexts:
        group = _trigger_to_required_group(ctx)
        for term in group:
            if term in required_flat:
                continue
            if term in optional_terms:
                continue
            optional_terms.append(term)

    return {
        "required_groups": required_groups,
        "optional_terms": optional_terms,
    }


def derive_rules_for_patterns_missing_autodraft(
    pattern_specs_by_id: Mapping[str, Mapping[str, Any]],
    existing_rule_ids: set[str],
) -> dict[str, dict[str, Any]]:
    """Bulk-derive rules for all patterns that don't already have one.

    Args:
      pattern_specs_by_id: {pattern_id: pattern_spec_dict}
      existing_rule_ids: pattern ids that already have a hand-authored rule

    Returns:
      {pattern_id: derived_rule} for patterns where derivation succeeded
    """
    out: dict[str, dict[str, Any]] = {}
    for pid, spec in pattern_specs_by_id.items():
        if pid in existing_rule_ids:
            continue
        derived = derive_autodraft_rule_from_pattern_spec(spec)
        if derived is None:
            continue
        out[pid] = derived
    return out
